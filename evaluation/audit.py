"""Frozen targets stay untouched; apply explicit corrections only while measuring."""
import json
from pathlib import Path
from megazeka.metrics import measure

AUDIT = Path(__file__).with_name('test_target_audit.jsonl')


def load_audit(path=AUDIT):
    entries = {}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row['target'] in entries or row['action'] not in ('fix', 'drop'):
            raise ValueError('Geçersiz veya yinelenen hedef denetimi.')
        if row['action'] == 'fix' and not row.get('fix'):
            raise ValueError('Düzeltilmiş hedef eksik.')
        entries[row['target']] = row
    return entries


def audited_rows(rows, audit=None):
    audit = load_audit() if audit is None else audit
    result = []
    for row in rows:
        entry = audit.get(row['target'])
        if entry and entry['action'] == 'drop':
            continue
        result.append({**row, 'target': entry['fix'] if entry else row['target']})
    return result


def recompute_audited_metrics(report, audit=None):
    """Recompute without inference or mutations; input remains the original noisy text."""
    return measure(audited_rows(report['examples'], audit))
