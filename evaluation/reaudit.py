"""Recalculate audited metrics from saved predictions, without loading a model."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import json
from evaluation.audit import AUDIT, recompute_audited_metrics


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding='utf-8'))
    result = {**report, 'target_audit': str(AUDIT), 'audited_metrics': recompute_audited_metrics(report)}
    path = args.report.with_name(args.report.stem + '-audited.json')
    if path.exists():
        parser.error(f'Çıktı zaten var: {path}')
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report': str(path), 'metrics': result['metrics'],
                      'audited_metrics': result['audited_metrics']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
