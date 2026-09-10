"""Install under a measured storage ceiling. No global caches are modified."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from megazeka.storage import ROOT, configure, ensure_budget, size, LIMIT, remove_owned, usage, external_reserve
import subprocess
import time
import json

configure()
python = ROOT / '.venv/Scripts/python.exe'

def install(args, estimate):
    ensure_budget(estimate, 'Bağımlılık kurulumu')
    p = subprocess.Popen(['uv', 'pip', 'install', '--python', str(python), '--no-cache', *args], cwd=ROOT)
    while p.poll() is None:
        # Reserve headroom for download writes between samples.
        if size(ROOT) + external_reserve() > LIMIT - 500_000_000:
            p.kill()
            p.wait()
            raise RuntimeError('15 GB sınırına yaklaşınca kurulum durduruldu.')
        time.sleep(2)
    if p.returncode:
        raise RuntimeError(f'Kurulum başarısız: {p.returncode}')

installed = subprocess.run([str(python), '-c', 'import torch; assert torch.__version__.startswith("2.6.0")'], capture_output=True).returncode == 0
if not installed:
    try:
        ensure_budget(8_100_000_000, 'GPU ortamı planı')
        torch_args = ['torch @ https://download.pytorch.org/whl/cu124/torch-2.6.0%2Bcu124-cp312-cp312-win_amd64.whl']
        estimate = 8_100_000_000
    except RuntimeError:
        print('GPU paketi bütçeye sığmıyor; daha küçük CPU paketi otomatik seçildi.', flush=True)
        torch_args = ['torch==2.6.0', '--index-url', 'https://download.pytorch.org/whl/cpu']
        estimate = 900_000_000
    install(torch_args, estimate)
install(['-r', str(ROOT / 'requirements.txt')], 450_000_000)
for child in (ROOT / '.cache/tmp').iterdir():
    remove_owned(child)
print(json.dumps(usage(), indent=2))
