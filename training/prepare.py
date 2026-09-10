"""8,000 clean source sentences -> 32,000 pairs; split BEFORE corruption."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import gzip
import hashlib
import json
import random
import re
from megazeka.storage import ROOT, ensure_budget, configure
from megazeka.text import normalize, canonical
from megazeka.noise import NoiseGenerator

def read_pairs(split):
    with gzip.open(ROOT / f'data/processed/{split}.jsonl.gz', 'rt', encoding='utf-8') as stream:
        return [json.loads(line) for line in stream]

def main():
    configure()
    ensure_budget(30_000_000, '32.000 sıkıştırılmış eğitim çifti')
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
        sources.setdefault(canonical(text), {'target': text, 'source': 'Common Voice / CC0-1.0'})
    original = ROOT / 'data/raw/original.txt'
    if original.exists():
        for text in original.read_text(encoding='utf-8').splitlines():
            if text.strip():
                sources[canonical(text)] = {'target': text, 'source': 'Megazeka özgün örnek / CC0-1.0'}
    values = list(sources.values())
    rng.shuffle(values)
    if len(values) < 8320:
        raise RuntimeError(f'Yeterli süzülmüş cümle yok: {len(values)}')
    selected = {'train': values[:8000], 'validation': values[8000:8160], 'test': values[8160:8320]}
    metadata = {'seed': 42, 'source': json.loads((ROOT / 'data/raw/source.json').read_text(encoding='utf-8')),
                'split_method': 'NFC + Türkçe küçük harf + alfanümerik kanonik tekilleştirme; gürültüden önce ayrım',
                'clean_ratio': .25, 'format': 'gzip-compressed JSONL', 'splits': {}}
    keys = []
    for index, (split, rows) in enumerate(selected.items()):
        generator = NoiseGenerator(42 + index)
        output = []
        for row in rows:
            key = canonical(row['target'])
            group_id = hashlib.sha256(key.encode()).hexdigest()[:16]
            for difficulty in ['temiz', 'kolay', 'orta', 'zor']:
                noisy, operations = generator.corrupt(row['target'], difficulty)
                output.append({**row, 'input': noisy, 'difficulty': difficulty, 'operations': operations, 'group_id': group_id})
        rng.shuffle(output)
        path = ROOT / f'data/processed/{split}.jsonl.gz'
        with path.open('wb') as raw:
            with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as stream:
                for row in output:
                    stream.write((json.dumps(row, ensure_ascii=False) + '\n').encode())
        metadata['splits'][split] = {'pairs': len(output), 'unique_targets': len(rows),
                                    'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        keys.append({canonical(row['target']) for row in rows})
    assert not keys[0] & keys[1] and not keys[0] & keys[2] and not keys[1] & keys[2]
    (ROOT / 'data/metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(metadata, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
