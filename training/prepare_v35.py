"""Merge audited v3.2 backups and explicit v3.5 pairs deterministically."""
import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
import os
import random
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT))

from megazeka.text import canonical
from training.prepare import _challenge_keys, group_of
from training.v35 import build_splits

SPLITS = ('train', 'validation')
VALIDATION_CAP = 800


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_rows(path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        return [json.loads(line) for line in stream if line.strip()]


def keys(rows):
    return {canonical(row[field]) for row in rows for field in ('input', 'target')}


def challenge_keys(root):
    paths = sorted((root / 'evaluation').glob('challenge*.jsonl'))
    blocked = _challenge_keys(paths)
    for path in paths:
        with path.open(encoding='utf-8') as stream:
            for line in stream:
                if line.strip():
                    row = json.loads(line)
                    if isinstance(row.get('source'), str):
                        blocked.add(canonical(row['source']))
    return blocked


def load_approved(path):
    decisions = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row['action'] not in ('drop', 'fix'):
            raise ValueError('Unknown audit action')
        if row['action'] == 'fix' and not isinstance(row.get('fix'), str):
            raise ValueError('Audit fix must be text')
        if row['target'] in decisions and decisions[row['target']] != row:
            raise ValueError('Conflicting audit decisions')
        decisions[row['target']] = row
    return decisions


def as_pair(row):
    target, source = row['target'], row['input']
    clean = source == target
    return {'target': target, 'kind': row['kind'], 'focus': row['focus'],
            'family': row['family'], 'source': row['source'], 'input': source,
            'difficulty': 'temiz' if clean else 'orta',
            'operations': [] if clean else [
                {'operation': 'v35_explicit', 'before': target, 'after': source}],
            'group_id': group_of(target)}


def validate(rows, changed):
    """Legacy overlap is allowed only between two untouched legacy rows."""
    for split in SPLITS:
        other = 'validation' if split == 'train' else 'train'
        if keys(changed[split]) & keys(rows[other]):
            raise ValueError('Changed rows overlap the opposite split')
    for split_rows in rows.values():
        for row in split_rows:
            if '\ufffd' in json.dumps(row, ensure_ascii=False):
                raise ValueError('Replacement character in output')


def gzip_rows(rows):
    buffer = io.BytesIO()
    # Explicitly omit the filename: temporary paths must not enter gzip headers.
    with gzip.GzipFile(filename='', fileobj=buffer, mode='wb', mtime=0) as stream:
        for row in rows:
            stream.write((json.dumps(row, ensure_ascii=False) + '\n').encode('utf-8'))
    return buffer.getvalue()


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + '.',
                                         suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(root=None, dry_run=False):
    root = Path(ROOT if root is None else root)
    base_paths = {s: root / f'data/v3.2-backup/{s}.jsonl.gz' for s in SPLITS}
    paths = {s: root / f'data/processed/{s}.jsonl.gz' for s in SPLITS}
    test_path = root / 'data/processed/test.jsonl.gz'
    approved_path = root / 'data/audit/v3.5-approved.jsonl'
    metadata_path = root / 'data/metadata.json'
    base_hashes = {s: sha256(p.read_bytes()) for s, p in base_paths.items()}
    test_hash = sha256(test_path.read_bytes())
    decisions = load_approved(approved_path)
    base = {s: read_rows(p) for s, p in base_paths.items()}
    rows, changed = {s: [] for s in SPLITS}, {s: [] for s in SPLITS}
    audit_counts = {s: {'fixed': 0, 'dropped': 0} for s in SPLITS}
    for split in SPLITS:
        for row in base[split]:
            decision = decisions.get(row['target'])
            if decision is None:
                rows[split].append(row)
            elif decision['action'] == 'fix' and row['input'] == row['target']:
                fixed = dict(row)
                fixed['input'] = fixed['target'] = decision['fix']
                fixed['group_id'] = group_of(fixed['target'])
                rows[split].append(fixed)
                changed[split].append(fixed)
                audit_counts[split]['fixed'] += 1
            else:
                audit_counts[split]['dropped'] += 1

    validate(rows, changed)
    base_keys = {s: keys(rows[s]) for s in SPLITS}
    test_keys = keys(read_rows(test_path))
    blocked_challenge = challenge_keys(root)
    existing_pairs = {(r['input'], r['target'])
                      for collection in (base, rows) for rs in collection.values() for r in rs}
    additions = {s: Counter() for s in SPLITS}
    rejected = {s: Counter({reason: 0 for reason in (
        'test', 'challenge', 'opposite_base', 'duplicate', 'opposite_new')}) for s in SPLITS}
    new_keys = {s: set() for s in SPLITS}
    generated = build_splits()
    # Doğrulama süresi ve checkpoint seçimi şablon verisine kaymasın diye yeni
    # doğrulama satırları sabit tohumla sınırlandırılır (sıra korunur).
    if len(generated['validation']) > VALIDATION_CAP:
        keep = set(random.Random(3500).sample(range(len(generated['validation'])), VALIDATION_CAP))
        generated['validation'] = [r for i, r in enumerate(generated['validation']) if i in keep]
    for split in SPLITS:
        other = 'validation' if split == 'train' else 'train'
        for entry in generated[split]:
            entry_keys = keys([entry])
            pair = (entry['input'], entry['target'])
            # First matching reason wins, so rejection counts sum to discarded rows.
            reason = next((label for label, blocked in (
                ('test', test_keys), ('challenge', blocked_challenge),
                ('opposite_base', base_keys[other])) if entry_keys & blocked), None)
            if reason is None and pair in existing_pairs:
                reason = 'duplicate'
            if reason is None and entry_keys & new_keys[other]:
                reason = 'opposite_new'
            if reason is not None:
                rejected[split][reason] += 1
                continue
            row = as_pair(entry)
            rows[split].append(row)
            changed[split].append(row)
            existing_pairs.add(pair)
            new_keys[split].update(entry_keys)
            additions[split][row['kind']] += 1

    validate(rows, changed)
    compressed = {s: gzip_rows(rows[s]) for s in SPLITS}
    report = {
        'base_sha256': base_hashes,
        'approved_sha256': sha256(approved_path.read_bytes()),
        'base_rows': audit_counts,
        'added': {s: {'pairs': sum(additions[s].values()),
                      'by_kind': dict(sorted(additions[s].items()))} for s in SPLITS},
        'rejected': {s: dict(rejected[s]) for s in SPLITS},
        'pairs': {s: len(rows[s]) for s in SPLITS},
        'output_sha256': {s: sha256(compressed[s]) for s in SPLITS},
    }
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    metadata['version'] = 'v3.5'
    for split in SPLITS:
        stats = metadata.setdefault('splits', {}).setdefault(split, {})
        stats['pairs'] = len(rows[split])
        stats['sha256'] = report['output_sha256'][split]
        stats['bytes'] = len(compressed[split])
    metadata['v35'] = report
    if not dry_run:
        for split in SPLITS:
            atomic_write(paths[split], compressed[split])
        written = {s: read_rows(paths[s]) for s in SPLITS}
        validate(written, changed)
        for split in SPLITS:
            if sha256(paths[split].read_bytes()) != report['output_sha256'][split]:
                raise RuntimeError('Output checksum mismatch')
    if sha256(test_path.read_bytes()) != test_hash:
        raise RuntimeError('Frozen test changed')
    if any(sha256(p.read_bytes()) != base_hashes[s] for s, p in base_paths.items()):
        raise RuntimeError('Backup changed')
    if not dry_run:
        atomic_write(metadata_path, (json.dumps(metadata, ensure_ascii=False, indent=2)
                                     + '\n').encode('utf-8'))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def cli(argv=None, root=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    return main(root=root, dry_run=parser.parse_args(argv).dry_run)


if __name__ == '__main__':
    cli()
