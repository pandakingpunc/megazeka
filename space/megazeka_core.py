"""Megazeka core: text chunking, guards and the chunked correction loop.

Vendored from the project's local engine (src/megazeka/{text,inference}.py) so this Space
is self-contained. Behaviour is intentionally identical to the local engine.
"""
import re
import unicodedata
from difflib import SequenceMatcher

MAX_CHUNK_EDIT_RATIO = 1.0
MIN_LENGTH_RATIO = .65
MAX_WORD_DISTANCE = .6
MAX_NEW_TOKENS = 224
_FOLD = str.maketrans('çğıöşüâîû', 'cgiosuaiu')


def lower_tr(text):
    return text.translate(str.maketrans({'I': 'ı', 'İ': 'i'})).lower()


def normalize(text):
    # Preserve newlines, tabs, repeated spaces and all user-visible characters.
    return unicodedata.normalize('NFC', text.replace('\r\n', '\n').replace('\r', '\n'))


def chunks(text, max_bytes=176):
    """Lossless partition: (part, is_layout). No truncation, even for long words."""
    result = []
    for line in re.split(r'(\n+)', text):
        if not line:
            continue
        if line.startswith('\n') or not line.strip():
            result.append((line, True))
            continue
        leading = line[:len(line) - len(line.lstrip())]
        if leading:
            result.append((leading, True))
            line = line[len(leading):]
        while line:
            n = 0
            used = 0
            for c in line:
                if used + len(c.encode('utf-8')) > max_bytes:
                    break
                used += len(c.encode('utf-8'))
                n += 1
            if n < len(line):
                boundary = line.rfind(' ', 0, n + 1)
                if boundary > n // 2:
                    n = boundary
            part, line = line[:n], line[n:]
            trailing = len(part) - len(part.rstrip())
            if trailing:
                result.extend([(part[:-trailing], False), (part[-trailing:], True)])
            else:
                result.append((part, False))
            whitespace = len(line) - len(line.lstrip(' \t'))
            if whitespace:
                result.append((line[:whitespace], True))
                line = line[whitespace:]
    return result


def fold(word):
    """Case/diacritic/punctuation-insensitive key for aligning words."""
    return ''.join(c for c in lower_tr(word).translate(_FOLD) if c.isalnum())


def guard_words(source, candidate):
    """Keep spelling fixes but refuse word substitutions with no letter overlap,
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


def correct_text(model, tokenizer, device, text, conservative=True, max_chars=4000):
    """Chunked correction identical to CorrectionEngine.correct (without diagnostics).

    Returns {'output', 'raw_output', 'warnings'}.
    """
    import torch
    if not isinstance(text, str):
        raise TypeError('Metin bir yazı dizisi olmalı.')
    if not text.strip():
        raise ValueError('Düzeltmek için bir metin yazın.')
    if len(text) > max_chars:
        raise ValueError(f'Bir seferde en fazla {max_chars} karakter kullanabilirsiniz.')
    output_parts, raw_parts, warnings = [], [], []
    for part_index, (part, layout) in enumerate(chunks(normalize(text))):
        if layout:
            output_parts.append(part); raw_parts.append(part)
            continue
        x = tokenizer(part, return_tensors='pt').to(device)
        with torch.inference_mode():
            result = model.generate(**x, max_new_tokens=MAX_NEW_TOKENS, do_sample=False, num_beams=1,
                                    return_dict_in_generate=True)
        ids = result.sequences[0, 1:].tolist()
        raw = tokenizer.decode(result.sequences[0], skip_special_tokens=True)
        final = raw
        if conservative:
            final, warning = guard(part, raw, ids)
            if warning:
                warnings.append(f'{part_index + 1}. parça: {warning}.')
        raw_parts.append(raw); output_parts.append(final)
    return {'output': ''.join(output_parts), 'raw_output': ''.join(raw_parts), 'warnings': warnings}
