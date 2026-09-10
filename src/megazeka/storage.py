"""Decimal GB limits; project-only accounting, reservations and safe cleanup."""
from pathlib import Path
import json
import os
import shutil
import time
import sys

ROOT = Path(__file__).resolve().parents[2]
GB = 1_000_000_000
LIMIT = 15 * GB

def external_reserve(root=ROOT):
    path = root / 'configs/storage.json'
    return json.loads(path.read_text(encoding='utf-8')).get('external_reserve_bytes', 0) if path.exists() else 0

def size(path):
    path = Path(path)
    if path.is_file():
        return path.stat().st_size
    total = 0
    for folder, dirs, files in os.walk(path, followlinks=False):
        dirs[:] = [d for d in dirs if not Path(folder, d).is_symlink()]
        for name in files:
            try:
                total += Path(folder, name).stat().st_size
            except FileNotFoundError:
                pass
    return total

def usage(root=ROOT):
    groups = {'model': 'models/base', 'dataset': 'data', 'checkpoints': 'models/checkpoints',
              'cache': '.cache', 'logs': 'reports', 'environment': '.venv'}
    result = {key: size(root / folder) for key, folder in groups.items()}
    result['total'] = size(root)
    result['other'] = max(0, result['total'] - sum(result[k] for k in groups))
    result['external_reserve'] = external_reserve(root)
    result['budget_total'] = result['total'] + result['external_reserve']
    result['warnings'] = [f'{n} GB eşiği aşıldı' for n in (5, 8, 12) if result['budget_total'] >= n * GB]
    return result

def configure():
    os.environ['PYTHONUTF8'] = '1'
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    for name, rel in {'HF_HOME': 'huggingface', 'UV_CACHE_DIR': 'uv', 'PIP_CACHE_DIR': 'pip',
                      'TMP': 'tmp', 'TEMP': 'tmp', 'TORCH_HOME': 'torch'}.items():
        folder = ROOT / '.cache' / rel
        folder.mkdir(parents=True, exist_ok=True)
        os.environ[name] = str(folder)
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'

def ensure_budget(additional, operation, root=ROOT):
    project_size = size(root)
    reserve = external_reserve(root)
    current = project_size + reserve
    expected = current + additional
    message = {'operation': operation, 'current_project_gb': round(project_size / GB, 3),
               'external_reserve_gb': round(reserve / GB, 3), 'additional_gb': round(additional / GB, 3),
               'expected_project_gb': round((project_size + additional) / GB, 3), 'expected_budget_gb': round(expected / GB, 3)}
    if additional >= GB:
        print('DEPOLAMA: ' + json.dumps(message, ensure_ascii=False), flush=True)
    for threshold in (5, 8, 12):
        if current < threshold * GB <= expected:
            print(f'DEPOLAMA UYARISI: bu işlem {threshold} GB eşiğini aşabilir.', flush=True)
    if expected >= LIMIT or shutil.disk_usage(root).free < additional + 500_000_000:
        raise RuntimeError('Depolama sınırı: işlem başlatılmadı. Daha küçük yapılandırma kullanın.')
    return message

def remove_owned(path):
    path = Path(path).resolve()
    allowed = [ROOT / '.cache', ROOT / 'models/checkpoints', ROOT / 'data/temporary']
    if not any(path.is_relative_to(p.resolve()) and path != p.resolve() for p in allowed):
        raise ValueError('Silme yolu projeye ait izinli geçici alanın dışında.')
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()

if __name__ == '__main__':
    configure()
    print(json.dumps(usage(), ensure_ascii=False, indent=2))
