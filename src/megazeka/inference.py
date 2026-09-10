"""Offline inference, measurable byte probabilities and lossless paragraph layout."""
from .storage import ROOT, configure, size
configure()
import json
import math
import time
from contextlib import nullcontext
from .text import normalize, chunks
from .metrics import edits, change_type

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
            from rapidfuzz.distance import Levenshtein
            ratio = Levenshtein.distance(part, raw) / max(1, len(part))
            if conservative and (not raw.strip() or ratio > .45 or len(raw) < .65 * len(part) or 1 not in ids):
                final = part
                warnings.append(f'{part_index+1}. parça: kapsamlı/eksik üretim korunma filtresiyle reddedildi. Ham çıktı inceleme ekranında.')
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

    def correct_batch(self, texts):
        """Evaluation path for short independent sentences; never truncate long input."""
        if not texts:
            return []
        if any(len(chunks(normalize(t))) != 1 or len(t.encode('utf-8')) > 176 or not t.strip() for t in texts):
            return [self.correct(t, inspect=False) for t in texts]
        from rapidfuzz.distance import Levenshtein
        prepared = [normalize(t) for t in texts]
        x = self.tokenizer(prepared, padding=True, return_tensors='pt').to(self.device)
        with self.torch.inference_mode():
            sequences = self.model.generate(**x, max_new_tokens=224, num_beams=1, do_sample=False)
        outputs = self.tokenizer.batch_decode(sequences, skip_special_tokens=True)
        results = []
        for text, raw, ids in zip(prepared, outputs, sequences.tolist()):
            rejected = not raw.strip() or Levenshtein.distance(text, raw) / max(1, len(text)) > .45 or len(raw) < .65*len(text) or 1 not in ids
            results.append({'output': text if rejected else raw, 'raw_output': raw,
                            'warnings': ['Kapsamlı/eksik üretim reddedildi.'] if rejected else []})
        return results
