"""Elle yazılmış zorluk kümesi (evaluation/challenge.jsonl): şablonla üretilmemiş, gerçekçi kullanıcı hataları.

Tam eşleşme genel ve kategori bazında raporlanır; kaynağı zaten doğru olan cümlelerde
gereksiz düzeltme ayrıca sayılır. Her başarısızlık raporda listelenir.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import json
import time
from megazeka.storage import ROOT

CHALLENGE = ROOT / 'evaluation/challenge.jsonl'

def load():
    return [json.loads(line) for line in CHALLENGE.read_text(encoding='utf-8').splitlines() if line.strip()]

def summarize(rows):
    """rows: dicts with source/target/output/category. Pure function so it can be unit-tested."""
    categories = {}
    for row in rows:
        entry = categories.setdefault(row['category'], {'total': 0, 'exact': 0})
        entry['total'] += 1
        entry['exact'] += row['output'] == row['target']
    for entry in categories.values():
        entry['exact_match'] = entry['exact'] / entry['total']
    clean = [r for r in rows if r['source'] == r['target']]
    changed = [r for r in clean if r['output'] != r['source']]
    return {'total': len(rows), 'exact': sum(r['output'] == r['target'] for r in rows),
            'exact_match': sum(r['output'] == r['target'] for r in rows) / max(1, len(rows)),
            'categories': categories,
            'clean_total': len(clean), 'clean_changed': len(changed),
            'overcorrection': len(changed) / len(clean) if clean else None}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', choices=['base', 'best', 'latest'], default='best')
    args = parser.parse_args()
    from megazeka.inference import CorrectionEngine
    engine = CorrectionEngine(args.checkpoint)
    started = time.perf_counter()
    rows = []
    for item in load():
        result = engine.correct(item['source'], inspect=False, conservative=True)
        rows.append({**item, 'output': result['output'], 'raw_output': result['raw_output']})
    summary = summarize(rows)
    failures = [r for r in rows if r['output'] != r['target']]
    report = {'checkpoint': args.checkpoint, **summary, 'seconds': time.perf_counter() - started,
              'failures': failures, 'rows': rows, 'model_info': engine.info}
    stem = ROOT / f'reports/challenge-{args.checkpoint}'
    stem.with_suffix('.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = [f'# Zorluk kümesi: {args.checkpoint}', '',
             f'Tam eşleşme: **{summary["exact"]}/{summary["total"]} = %{summary["exact_match"]*100:.1f}**', '']
    if summary['overcorrection'] is not None:
        lines += [f'Gereksiz düzeltme (zaten doğru {summary["clean_total"]} cümle): '
                  f'**{summary["clean_changed"]}/{summary["clean_total"]} = %{summary["overcorrection"]*100:.1f}**', '']
    lines += ['| Kategori | Doğru | Toplam | Tam eşleşme |', '|---|---:|---:|---:|']
    for name, e in summary['categories'].items():
        lines.append(f'| {name} | {e["exact"]} | {e["total"]} | %{e["exact_match"]*100:.1f} |')
    lines += ['', f'## Başarısızlıklar ({len(failures)})', '']
    for r in failures:
        lines += ['```text', f'[{r["category"]}]', 'GİRDİ: ' + r['source'], 'MODEL: ' + r['output'], 'HEDEF: ' + r['target'], '```', '']
    stem.with_suffix('.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in ('rows', 'failures', 'model_info')}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
