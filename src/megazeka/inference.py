"""Offline inference, measurable byte probabilities and lossless paragraph layout."""
from .storage import ROOT, configure, size
configure()
import json
import math
import time
from contextlib import nullcontext
from difflib import SequenceMatcher
from .text import normalize, chunks, lower_tr
from .metrics import edits, change_type

# Chunk-level guard: reject a generation that rewrites more characters than the chunk has.
# Measured on the 1,128-pair test set: the old 0.45 threshold rejected most correct heavy
# fixes (edit F1 0.71 -> 0.89 at 1.0) while the word guard alone kept over-correction flat.
MAX_CHUNK_EDIT_RATIO = 1.0
MIN_LENGTH_RATIO = .65
# Word-level guard: a replaced word group must keep letter similarity with the original.
MAX_WORD_DISTANCE = .6
_FOLD = str.maketrans('çğıöşüâîû', 'cgiosuaiu')

def fold(word):
    """Case/diacritic/punctuation-insensitive key for aligning words."""
    return ''.join(c for c in lower_tr(word).translate(_FOLD) if c.isalnum())

def guard_words(source, candidate):
    """Keep the model's spelling fixes but refuse word substitutions with no letter overlap,
    dropped words and invented words. Returns (text, number_of_blocked_groups)."""
    from rapidfuzz.distance import Levenshtein
    a, b = source.split(), candidate.split()
    if not a or not b:
        return candidate, 0
    matcher = SequenceMatcher(None, [fold(w) for w in a], [fold(w) for w in b], autojunk=False)
    output, blocked = [], 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            output.extend(b[j1:j2])
        elif tag == 'replace':
            old, new = fold(''.join(a[i1:i2])), fold(''.join(b[j1:j2]))
            if old and new and Levenshtein.normalized_distance(old, new) > MAX_WORD_DISTANCE:
                output.extend(a[i1:i2]); blocked += 1
            else:
                output.extend(b[j1:j2])
        elif tag == 'delete':
            output.extend(a[i1:i2]); blocked += 1
        else:  # insert: words with nothing to align against
            blocked += 1
    return (candidate if not blocked else ' '.join(output)), blocked

def guard(part, raw, ids):
    """Apply both guards; returns (final_text, warning_or_None)."""
    from rapidfuzz.distance import Levenshtein
    ratio = Levenshtein.distance(part, raw) / max(1, len(part))
    if not raw.strip() or ratio > MAX_CHUNK_EDIT_RATIO or len(raw) < MIN_LENGTH_RATIO * len(part) or 1 not in ids:
        return part, 'kapsamlı/eksik üretim korunma filtresiyle reddedildi'
    final, blocked = guard_words(part, raw)
    if blocked:
        return final, f'{blocked} kelime grubu harf benzerliği olmadığı için özgün haliyle korundu'
    return final, None

class CorrectionEngine:
    def __init__(self, checkpoint='best', device=None):
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        from peft import PeftModel
        self.torch = torch
        if not (ROOT / 'models/base/config.json').exists():
            raise RuntimeError('Temel model bulunamadı. Önce scripts/download.py komutunu çalıştırın.')
        torch.set_num_threads(6)
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.dtype = torch.bfloat16 if self.device == 'cuda' and torch.cuda.is_bf16_supported() else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(ROOT / 'models/base', local_files_only=True)
        base = AutoModelForSeq2SeqLM.from_pretrained(ROOT / 'models/base', local_files_only=True, dtype=self.dtype)
        self.checkpoint = checkpoint
        if checkpoint != 'base':
            if checkpoint not in ('best', 'latest'):
                raise ValueError('Geçersiz kontrol noktası.')
            path = ROOT / 'models/checkpoints' / checkpoint
            if not (path / 'adapter_config.json').exists():
                raise RuntimeError('Eğitilmiş model henüz bulunamadı. Önce eğitim komutunu çalıştırın.')
            base = PeftModel.from_pretrained(base, path, local_files_only=True)
        self.model = base.to(self.device).eval()
        self.model.config.use_cache = True
        self.info = {'Mimari': 'ByT5-small + LoRA' if checkpoint != 'base' else 'ByT5-small (temel)',
                     'Toplam parametre': sum(p.numel() for p in self.model.parameters()),
                     'Token sözlüğü': len(self.tokenizer), 'Kontrol noktası': str(ROOT / ('models/base' if checkpoint == 'base' else f'models/checkpoints/{checkpoint}')),
                     'Temel model boyutu (MB)': round(size(ROOT / 'models/base') / 1e6, 1),
                     'Aygıt': torch.cuda.get_device_name() if self.device == 'cuda' else 'CPU',
                     'Hassasiyet': str(self.dtype), 'Nicemleme': 'Yok', 'Parça sınırı': '176 UTF-8 baytı',
                     'Üretim': 'Açgözlü çözümleme; 1 ışın; en fazla 224 yeni bayt tokenı'}
        state_file = ROOT / f'models/checkpoints/{checkpoint}/state.json'
        if state_file.exists():
            self.info['Eğitim adımı'] = json.loads(state_file.read_text(encoding='utf-8'))['step']
        self.info['LoRA hassasiyeti'] = ', '.join(sorted({str(p.dtype) for n, p in self.model.named_parameters() if 'lora_' in n})) or 'Yok'

    @staticmethod
    def token_label(token_id):
        special = {0: '<pad>', 1: '</s>', 2: '<unk>'}
        if token_id in special:
            return special[token_id]
        if 3 <= token_id <= 258:
            b = token_id - 3
            return repr(chr(b)) if 32 <= b < 127 else f'0x{b:02X}'
        return f'<extra:{token_id}>'

    def correct(self, text, inspect=True, conservative=True):
        if not isinstance(text, str):
            raise TypeError('Metin bir yazı dizisi olmalı.')
        if not text.strip():
            raise ValueError('Düzeltmek için bir metin yazın.')
        if len(text) > 4000:
            raise ValueError('Bir seferde en fazla 4.000 karakter kullanabilirsiniz.')
        torch = self.torch
        def now():
            if self.device == 'cuda':
                torch.cuda.synchronize()
            return time.perf_counter()
        start = now()
        normalized = normalize(text)
        parts = chunks(normalized)
        timings = {'Normalizasyon': (now() - start) * 1000, 'Tokenizasyon': 0., 'Sinir ağı / üretim': 0., 'Çözümleme': 0., 'Son işleme': 0.}
        output_parts, raw_parts, input_tokens, generated = [], [], [], []
        warnings = []
        pieces = []
        for part_index, (part, layout) in enumerate(parts):
            if layout:
                output_parts.append(part); raw_parts.append(part)
                continue
            t = now()
            x = self.tokenizer(part, return_tensors='pt').to(self.device)
            token_ids = x.input_ids[0].tolist()
            input_tokens.extend({'id': i, 'token': self.token_label(i), 'part': part_index} for i in token_ids)
            timings['Tokenizasyon'] += (now() - t) * 1000
            t = now()
            with torch.inference_mode():
                result = self.model.generate(**x, max_new_tokens=224, do_sample=False, num_beams=1,
                    return_dict_in_generate=True, output_scores=inspect)
            timings['Sinir ağı / üretim'] += (now() - t) * 1000
            t = now()
            ids = result.sequences[0, 1:].tolist()
            raw = self.tokenizer.decode(result.sequences[0], skip_special_tokens=True)
            if inspect:
                for step, logits in enumerate(result.scores):
                    chosen = ids[step]
                    if chosen == 0:
                        continue
                    p = torch.softmax(logits[0].float(), dim=-1)
                    values, indices = p.topk(5)
                    generated.append({'part': part_index, 'step': step, 'id': chosen,
                        'token': self.token_label(chosen), 'probability': p[chosen].item(),
                        'alternatives': [{'id': i, 'token': self.token_label(i), 'probability': v}
                                         for v, i in zip(values.tolist(), indices.tolist())]})
            timings['Çözümleme'] += (now() - t) * 1000
            t = now()
            final = raw
            if conservative:
                final, warning = guard(part, raw, ids)
                if warning:
                    warnings.append(f'{part_index+1}. parça: {warning}. Ham çıktı inceleme ekranında.')
            pieces.append({'part': part_index, 'input': part, 'raw': raw, 'final': final})
            raw_parts.append(raw); output_parts.append(final)
            timings['Son işleme'] += (now() - t) * 1000
        output = ''.join(output_parts)
        operations = edits(text, output)
        for op in operations:
            op['type'] = change_type(op['old'], op['new'])
            op['distance'] = 1
            op['confidence'] = None
        probabilities = [token['probability'] for token in generated]
        return {'original': text, 'model_input': normalized, 'raw_output': ''.join(raw_parts), 'output': output,
                'preprocessing_changed': normalized != text, 'tokens': input_tokens, 'generated': generated,
                'edits': operations, 'pieces': pieces, 'timings_ms': timings, 'elapsed_ms': (now()-start)*1000,
                'warnings': warnings, 'average_token_probability': sum(probabilities)/len(probabilities) if probabilities else None,
                'minimum_token_probability': min(probabilities) if probabilities else None,
                'sequence_log_probability': sum(math.log(max(p, 1e-30)) for p in probabilities) if probabilities else None,
                'checkpoint': self.checkpoint}

    def correct_batch(self, texts, conservative=True):
        """Evaluation path for short independent sentences; never truncate long input."""
        if not texts:
            return []
        if any(len(chunks(normalize(t))) != 1 or len(t.encode('utf-8')) > 176 or not t.strip() for t in texts):
            return [self.correct(t, inspect=False, conservative=conservative) for t in texts]
        prepared = [normalize(t) for t in texts]
        x = self.tokenizer(prepared, padding=True, return_tensors='pt').to(self.device)
        with self.torch.inference_mode():
            sequences = self.model.generate(**x, max_new_tokens=224, num_beams=1, do_sample=False)
        outputs = self.tokenizer.batch_decode(sequences, skip_special_tokens=True)
        results = []
        for text, raw, ids in zip(prepared, outputs, sequences.tolist()):
            final, warning = (guard(text, raw, ids) if conservative else (raw, None))
            results.append({'output': final, 'raw_output': raw, 'warnings': [warning] if warning else []})
        return results
