"""Clean source sentences -> noisy/clean pairs; split BEFORE corruption.

Sources: 8,000 Common Voice sentences plus template/hand-written everyday sentences
(training/everyday.py). Everyday sentences always receive at least one colloquial
rewrite in the 'kolay' and 'orta' difficulties. A slice of the training set joins two
sentences so the model also sees multi-sentence chunks like real pasted paragraphs.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gzip
import hashlib
import json
import random
import re
from megazeka.storage import ROOT, ensure_budget, configure
from megazeka.text import normalize, canonical
from megazeka.noise import NoiseGenerator
from training.everyday import sentences as everyday_sentences

EVERYDAY_SOURCE = 'Megazeka gündelik şablon / CC0-1.0'
COMMON_VOICE_SOURCE = 'Common Voice / CC0-1.0'
COMBINED_SOURCE = 'Birleşik iki cümle'
DIFFICULTIES = ['temiz', 'kolay', 'orta', 'zor']
COMBINED_MAX_BYTES = 170

def read_pairs(split):
    with gzip.open(ROOT / f'data/processed/{split}.jsonl.gz', 'rt', encoding='utf-8') as stream:
        return [json.loads(line) for line in stream]

def group_of(text):
    return hashlib.sha256(canonical(text).encode()).hexdigest()[:16]

def main():
    configure()
    ensure_budget(30_000_000, 'Sıkıştırılmış eğitim çiftleri')
    rng = random.Random(42)
    sources = {}
    for row in (ROOT / 'data/raw/common_voice_tr.txt').read_text(encoding='utf-8').splitlines():
        text = normalize(row).strip()
        if not 3 <= len(text.split()) <= 24 or not 18 <= len(text.encode('utf-8')) <= 160:
            continue
        if not re.match(r'^[A-ZÇĞİÖŞÜ]', text) or text[-1:] not in '.?!':
            continue
        if any(x in text for x in ['http', '�', '"', '<', '>']):
            continue
        sources.setdefault(canonical(text), {'target': text, 'source': COMMON_VOICE_SOURCE})
    everyday = []
    for text in everyday_sentences():
        key = canonical(text)
        if key not in sources:
            everyday.append({'target': text, 'source': EVERYDAY_SOURCE})
            sources[key] = everyday[-1]
    values = [v for v in sources.values() if v['source'] == COMMON_VOICE_SOURCE]
    rng.shuffle(values)
    if len(values) < 8320:
        raise RuntimeError(f'Yeterli süzülmüş cümle yok: {len(values)}')
    rng.shuffle(everyday)
    held = max(40, len(everyday) // 12)
    selected = {'train': values[:8000] + everyday[2 * held:],
                'validation': values[8000:8160] + everyday[:held],
                'test': values[8160:8320] + everyday[held:2 * held]}
    metadata = {'seed': 42, 'source': json.loads((ROOT / 'data/raw/source.json').read_text(encoding='utf-8')),
                'everyday_source': {'name': 'Megazeka gündelik şablon ve elle yazılmış cümleler', 'module': 'training/everyday.py',
                                    'license': 'CC0-1.0', 'sentences': len(everyday)},
                'split_method': 'NFC + Türkçe küçük harf + alfanümerik kanonik tekilleştirme; gürültüden önce ayrım',
                'clean_ratio': .25, 'format': 'gzip-compressed JSONL', 'splits': {}}
    keys = []
    for index, (split, rows) in enumerate(selected.items()):
        generator = NoiseGenerator(42 + index)
        output = []
        for row in rows:
            everyday_row = row['source'] == EVERYDAY_SOURCE
            for difficulty in DIFFICULTIES:
                prefer = 'gündelik' if everyday_row and difficulty in ('kolay', 'orta') else None
                noisy, operations = generator.corrupt(row['target'], difficulty, prefer=prefer)
                output.append({**row, 'input': noisy, 'difficulty': difficulty, 'operations': operations,
                               'group_id': group_of(row['target'])})
        if split == 'train':
            # Multi-sentence chunks: join two independent training pairs of the same difficulty.
            by_difficulty = {d: [r for r in output if r['difficulty'] == d] for d in DIFFICULTIES}
            combined = []
            target_count = len(rows) // 8
            attempts = 0
            while len(combined) < target_count and attempts < target_count * 20:
                attempts += 1
                difficulty = rng.choice(DIFFICULTIES)
                a, b = rng.sample(by_difficulty[difficulty], 2)
                target = a['target'] + ' ' + b['target']
                if len(target.encode('utf-8')) > COMBINED_MAX_BYTES:
                    continue
                combined.append({'target': target, 'source': COMBINED_SOURCE, 'input': a['input'] + ' ' + b['input'],
                                 'difficulty': difficulty, 'operations': a['operations'] + b['operations'],
                                 'group_id': a['group_id'], 'group_id_second': b['group_id']})
            output.extend(combined)
        rng.shuffle(output)
        path = ROOT / f'data/processed/{split}.jsonl.gz'
        with path.open('wb') as raw:
            with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as stream:
                for row in output:
                    stream.write((json.dumps(row, ensure_ascii=False) + '\n').encode())
        counts = {}
        for row in output:
            counts[row['source']] = counts.get(row['source'], 0) + 1
        metadata['splits'][split] = {'pairs': len(output), 'unique_targets': len(rows), 'by_source': counts,
                                    'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        keys.append({row['group_id'] for row in output} | {row.get('group_id_second') for row in output if row.get('group_id_second')})
    assert not keys[0] & keys[1] and not keys[0] & keys[2] and not keys[1] & keys[2]
    (ROOT / 'data/metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(metadata, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
