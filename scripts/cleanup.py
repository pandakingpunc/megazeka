"""Only exact project-owned redundant temporary artifacts. Never global caches."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import json
from megazeka.storage import ROOT, remove_owned, usage, configure

def main():
    configure()
    import psutil
    status = ROOT / 'reports/training_status.json'
    if status.exists():
        s = json.loads(status.read_text(encoding='utf-8'))
        if s.get('running') and s.get('pid') and psutil.pid_exists(s['pid']):
            raise RuntimeError('Eğitim çalışırken temizlik yapılmaz.')
    for folder in ['tmp', 'uv', 'pip']:
        parent = ROOT / '.cache' / folder
        if parent.exists():
            for child in parent.iterdir():
                remove_owned(child)
    for child in (ROOT / 'models/checkpoints').glob('temporary-*'):
        remove_owned(child)
    print(json.dumps(usage(), ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
