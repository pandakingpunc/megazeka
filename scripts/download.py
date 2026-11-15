"""One selected model, pinned revision. Guard before network and each write."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import hashlib
import json
import urllib.request
from megazeka.storage import ROOT, configure, ensure_budget, size, LIMIT, external_reserve

REV = '68377bdc18a2ffec8a0533fef03b1c513a4dd49d'
# v4 base: google/byt5-base, Apache-2.0. File names, sizes and SHA-256 were read from the
# Hugging Face repository at this exact revision (flax/tf copies are not needed).
BASE_REPO = 'google/byt5-base'
BASE_REV = '92d8c008d55cf7c254915bac165171dfe6c20c44'
BASE_FILES = [('config.json', 721), ('generation_config.json', 147), ('special_tokens_map.json', 2503),
              ('tokenizer_config.json', 2593), ('pytorch_model.bin', 2_326_727_132)]
BASE_BIN_SHA256 = '268bdbac27c1fdb14abc20774c765f3a6fc15e6c3e67f6811f0dc8183a23bbd6'

def download(url, path, estimate):
    if path.exists():
        return
    part = path.with_name(path.name + '.part')
    offset = part.stat().st_size if part.exists() else 0
    ensure_budget(max(0, estimate - offset), f'İndirme: {path.name}; açılmış boyut = indirme boyutu')
    req = urllib.request.Request(url, headers={'Range': f'bytes={offset}-'} if offset else {})
    with urllib.request.urlopen(req, timeout=90) as response:
        append = offset > 0 and response.status == 206
        if not append:
            offset = 0
        content_length = response.headers.get('Content-Length')
        expected_size = int(content_length) + offset if content_length else None
        with part.open('ab' if append else 'wb') as out:
            available = LIMIT - size(ROOT) - external_reserve() - 100_000_000
            while block := response.read(4 * 1024 * 1024):
                if available < len(block):
                    raise RuntimeError('Depolama sınırı: indirme durduruldu.')
                out.write(block)
                available -= len(block)
    if expected_size is not None and part.stat().st_size != expected_size:
        raise RuntimeError('Eksik indirme: geçici dosya korunuyor, yeniden deneyebilirsiniz.')
    part.replace(path)

def download_base():
    folder = ROOT / 'models/base-byt5-base'
    if (folder / 'model.safetensors').exists():
        print('byt5-base zaten yerel safetensors biçiminde; yeniden indirilmedi.')
        return
    folder.mkdir(parents=True, exist_ok=True)
    for name, estimate in BASE_FILES:
        download(f'https://huggingface.co/{BASE_REPO}/resolve/{BASE_REV}/{name}', folder / name, estimate)
    with (folder / 'pytorch_model.bin').open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != BASE_BIN_SHA256:
        raise RuntimeError('byt5-base SHA-256 doğrulaması başarısız; dosya korunuyor, elle inceleyin.')
    (folder / 'source.json').write_text(json.dumps({'repo': BASE_REPO, 'revision': BASE_REV,
          'license': 'Apache-2.0', 'sha256': digest}, indent=2), encoding='utf-8')
    print('byt5-base indirildi; eğitim sırasında safetensors biçimine dönüştürülecek.')

def main(argv=None):
    parser = argparse.ArgumentParser(description='Veriyi ve seçilen temel modeli indirir.')
    parser.add_argument('--base', choices=['small', 'base'], default='small',
                        help='small: google/byt5-small (v3.5 ve öncesi, varsayılan); base: google/byt5-base (v4)')
    args = parser.parse_args(argv)
    configure()
    source = json.loads((ROOT / 'data/raw/source.json').read_text(encoding='utf-8'))
    data_path = ROOT / 'data/raw/common_voice_tr.txt'
    download(source['url'], data_path, source['bytes'])
    with data_path.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != source['sha256']:
            raise RuntimeError('Veri kaynağı SHA-256 doğrulaması başarısız.')
    if args.base == 'base':
        download_base()
        return
    folder = ROOT / 'models/base'
    folder.mkdir(parents=True, exist_ok=True)
    if (folder / 'model.safetensors').exists():
        print('Seçilen temel model zaten yerel safetensors biçiminde; yeniden indirilmedi.')
        return
    for name, estimate in [('config.json', 5000), ('tokenizer_config.json', 10000),
                           ('special_tokens_map.json', 10000), ('pytorch_model.bin', 1_198_627_927)]:
        download(f'https://huggingface.co/google/byt5-small/resolve/{REV}/{name}', folder / name, estimate)
    model_path = folder / 'pytorch_model.bin'
    with model_path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    (folder / 'source.json').write_text(json.dumps({'model': 'google/byt5-small', 'revision': REV,
          'license': 'Apache-2.0', 'sha256': digest}, indent=2), encoding='utf-8')
    print('Tek temel model indirildi; eğitim sırasında safetensors biçimine dönüştürülecek.')

if __name__ == '__main__':
    main()
