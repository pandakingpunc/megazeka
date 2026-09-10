"""Corpus CER/WER and exact character edit precision/recall (not calibrated)."""
from rapidfuzz.distance import Levenshtein

def edits(source, target):
    return [{'operation': op.tag, 'source_index': op.src_pos, 'target_index': op.dest_pos,
             'old': source[op.src_pos] if op.tag != 'insert' else '',
             'new': target[op.dest_pos] if op.tag != 'delete' else ''}
            for op in Levenshtein.editops(source, target)]

def edit_set(source, target):
    return {(e['operation'], e['source_index'], e['new']) for e in edits(source, target)}

def measure(rows):
    chars = words = ce = we = exact = tp = proposed = expected = clean = changed = 0
    for row in rows:
        source, prediction, target = row['input'], row['output'], row['target']
        chars += len(target)
        words += len(target.split())
        ce += Levenshtein.distance(prediction, target)
        we += Levenshtein.distance(prediction.split(), target.split())
        exact += prediction == target
        found, truth = edit_set(source, prediction), edit_set(source, target)
        tp += len(found & truth)
        proposed += len(found)
        expected += len(truth)
        if source == target:
            clean += 1
            changed += prediction != source
    precision = tp / proposed if proposed else 0.0
    recall = tp / expected if expected else 0.0
    return {'examples': len(rows), 'cer': ce / max(1, chars), 'wer': we / max(1, words),
            'exact_match': exact / max(1, len(rows)), 'edit_precision': precision, 'edit_recall': recall,
            'edit_f1': 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
            'clean_examples': clean, 'overcorrection': changed / clean if clean else None}

def change_type(old, new):
    from .text import lower_tr
    from .noise import ASCII
    if old.isspace() or new.isspace():
        return 'Boşluk değişikliği'
    if lower_tr(old) == lower_tr(new):
        return 'Büyük/küçük harf'
    if old.translate(ASCII) == new.translate(ASCII):
        return 'Türkçe karakter'
    if (old and not old.isalnum()) or (new and not new.isalnum()):
        return 'Noktalama / simge'
    return 'Harf / yazım değişikliği'
