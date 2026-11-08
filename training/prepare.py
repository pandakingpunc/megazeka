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

CHALLENGE = ROOT / 'evaluation/challenge.jsonl'
TEST_PATH = ROOT / 'data/processed/test.jsonl.gz'

def challenge_keys():
    """Canonical keys of the hand-written challenge targets: they must never enter train/validation."""
    if not CHALLENGE.exists():
        return set()
    return {canonical(json.loads(line)['target']) for line in CHALLENGE.read_text(encoding='utf-8').splitlines() if line.strip()}

CORRECTIONS = ROOT / 'data/audit/corrections.jsonl'

def load_corrections(path=CORRECTIONS):
    """Audit corrections: (fixes {original target: fixed target}, drops {original target}). Missing file -> empty."""
    fixes, drops = {}, set()
    path = Path(path)
    if not path.exists():
        return fixes, drops
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row['action'] == 'drop':
            drops.add(row['target'])
        elif row['action'] == 'fix' and row.get('fix') and row['fix'] != row['target']:
            fixes[row['target']] = row['fix']
    overlap = set(fixes) & drops
    if overlap:
        raise RuntimeError(f'Hem düzeltilen hem silinen hedef: {sorted(overlap)[:3]}')
    return fixes, drops

def main():
    configure()
    ensure_budget(30_000_000, 'Sıkıştırılmış eğitim çiftleri')
    rng = random.Random(42)
    fixes, drops = load_corrections()
    fixed_applied = 0
    dropped_ids = set()      # id() of Common Voice / everyday entries whose original target is dropped
    original_key = {}        # id(entry) -> canonical key of the ORIGINAL text (frozen-test check uses it)
    everyday_dropped = 0
    sources = {}
    for row in (ROOT / 'data/raw/common_voice_tr.txt').read_text(encoding='utf-8').splitlines():
        text = normalize(row).strip()
        if not 3 <= len(text.split()) <= 24 or not 18 <= len(text.encode('utf-8')) <= 160:
            continue
        if not re.match(r'^[A-ZÇĞİÖŞÜ]', text) or text[-1:] not in '.?!':
            continue
        if any(x in text for x in ['http', '�', '"', '<', '>']):
            continue
        key = canonical(text)
        if key in sources:
            continue
        # The dict key stays the ORIGINAL text so insertion order (seeded shuffle, frozen test slice) is unchanged.
        entry = sources[key] = {'target': fixes.get(text, text), 'source': COMMON_VOICE_SOURCE}
        original_key[id(entry)] = key
        fixed_applied += text in fixes
        if text in drops:
            dropped_ids.add(id(entry))
    everyday = []
    for text in everyday_sentences():
        key = canonical(text)
        if key not in sources:
            if text in drops:
                everyday_dropped += 1
                continue
            everyday.append({'target': fixes.get(text, text), 'source': EVERYDAY_SOURCE})
            fixed_applied += text in fixes
            sources[key] = everyday[-1]
    values = [v for v in sources.values() if v['source'] == COMMON_VOICE_SOURCE]
    rng.shuffle(values)
    if len(values) < 8320:
        raise RuntimeError(f'Yeterli süzülmüş cümle yok: {len(values)}')
    rng.shuffle(everyday)
    everyday_total = len(everyday)
    held = max(40, len(everyday) // 12)
    frozen = TEST_PATH.exists()
    blocked = challenge_keys()
    if frozen:
        # The v2 test split is frozen so v2 and v3 stay comparable: never regenerated, and every
        # sentence it contains is excluded from train/validation before any noise is added.
        frozen_rows = read_pairs('test')
        frozen_keys = {canonical(r['target']) for r in frozen_rows}
        cv_test = {original_key[id(v)] for v in values[8160:8320]}
        if cv_test != {canonical(r['target']) for r in frozen_rows if r['source'] == COMMON_VOICE_SOURCE}:
            raise RuntimeError('Dondurulmuş test, Common Voice ayrımıyla uyuşmuyor; data/v2-backup kullanın.')
        blocked |= frozen_keys
        everyday = [e for e in everyday if canonical(e['target']) not in blocked]
        held = max(40, len(everyday) // 12)
        selected = {'train': [v for v in values[:8000] if canonical(v['target']) not in blocked and id(v) not in dropped_ids] + everyday[held:],
                    'validation': [v for v in values[8000:8160] if canonical(v['target']) not in blocked and id(v) not in dropped_ids] + everyday[:held]}
    else:
        selected = {'train': values[:8000] + everyday[2 * held:],
                    'validation': values[8000:8160] + everyday[:held],
                    'test': values[8160:8320] + everyday[held:2 * held]}
        selected = {k: [r for r in v if k == 'test' or (canonical(r['target']) not in blocked and id(r) not in dropped_ids)]
                    for k, v in selected.items()}
    # A fix can land on a sentence that already exists elsewhere: keep one copy (test > validation > train).
    seen_targets, collisions = set(), 0
    for split in sorted(selected, key=lambda k: ['test', 'validation', 'train'].index(k)):
        kept = []
        for row in selected[split]:
            key = canonical(row['target'])
            if key in seen_targets:
                collisions += 1
                continue
            seen_targets.add(key)
            kept.append(row)
        selected[split] = kept
    dropped_applied = sum(1 for v in values[:8160] if id(v) in dropped_ids) + everyday_dropped  # test slice is never trimmed
    corrections_file = CORRECTIONS if CORRECTIONS.exists() else None
    metadata = {'seed': 42, 'source': json.loads((ROOT / 'data/raw/source.json').read_text(encoding='utf-8')),
                'everyday_source': {'name': 'Megazeka gündelik şablon ve elle yazılmış cümleler', 'module': 'training/everyday.py',
                                    'license': 'CC0-1.0', 'sentences': everyday_total},
                'split_method': 'NFC + Türkçe küçük harf + alfanümerik kanonik tekilleştirme; gürültüden önce ayrım',
                'clean_ratio': .25, 'format': 'gzip-compressed JSONL', 'version': 'v3.1',
                'target_corrections': {'file': 'data/audit/corrections.jsonl',
                                           'sha256': hashlib.sha256(corrections_file.read_bytes()).hexdigest() if corrections_file else None,
                                           'fixed_applied': fixed_applied, 'dropped_applied': dropped_applied},
                'test_frozen_from': 'v2' if frozen else None, 'challenge_targets_excluded': len(challenge_keys()), 'splits': {}}
    print(f'Hedef düzeltmeleri: {fixed_applied} düzeltme, {dropped_applied} silme uygulandı; {collisions} çakışan kopya elendi.')
    keys = []
    for index, (split, rows) in enumerate(selected.items()):
        generator = NoiseGenerator(42 + index)
        output = []
        for row in rows:
            everyday_row = row['source'] == EVERYDAY_SOURCE
            for difficulty in DIFFICULTIES:
                prefer = generator.preferred(row['target']) if everyday_row and difficulty in ('kolay', 'orta') else None
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
    if frozen:
        # Test is not rewritten: record its statistics as read from the untouched v2 file.
        counts = {}
        for row in frozen_rows:
            counts[row['source']] = counts.get(row['source'], 0) + 1
        metadata['splits']['test'] = {'pairs': len(frozen_rows), 'unique_targets': len({row['group_id'] for row in frozen_rows}),
                                      'by_source': counts, 'bytes': TEST_PATH.stat().st_size,
                                      'sha256': hashlib.sha256(TEST_PATH.read_bytes()).hexdigest(), 'frozen_from': 'v2'}
        keys.append({row['group_id'] for row in frozen_rows})
    assert not keys[0] & keys[1] and not keys[0] & keys[2] and not keys[1] & keys[2]
    for split in ('train', 'validation'):
        leaked = [r['target'] for r in read_pairs(split) if canonical(r['target']) in challenge_keys()]
        assert not leaked, f'Zorluk kümesi hedefi {split} içinde: {leaked[:3]}'
    (ROOT / 'data/metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(metadata, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
