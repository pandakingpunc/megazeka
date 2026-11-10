"""Lazy corpus-frequency lexicon; no model or network needed."""
from collections import Counter
from functools import lru_cache
import gzip
import io
import json
import re
import warnings
from .storage import ROOT
from .text import lower_tr

RAW = ROOT / 'data/raw/common_voice_tr.txt'
CACHE = ROOT / 'data/lexicon.json.gz'
_TOKEN = re.compile(r"[^\W_]+(?:'[^\W_]+)*", re.UNICODE)


def tokens(text):
    return _TOKEN.findall(lower_tr(text).replace('’', "'").replace('‘', "'"))


def build_lexicon(sentences):
    counts = Counter()
    for sentence in sentences:
        for word in tokens(sentence):
            counts[word] += 1
            if "'" in word:
                counts[word.split("'", 1)[0]] += 1
    return dict(counts)


def cache_bytes(counts):
    payload = json.dumps(counts, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    buffer = io.BytesIO()
    with gzip.GzipFile(filename='', mode='wb', fileobj=buffer, mtime=0) as stream:
        stream.write(payload)
    return buffer.getvalue()


@lru_cache(maxsize=1)
def load_lexicon():
    if CACHE.exists():
        try:
            return json.loads(gzip.decompress(CACHE.read_bytes()))
        except (OSError, EOFError, ValueError) as exc:
            warnings.warn(f'Sözlük önbelleği okunamadı, yeniden kuruluyor: {exc}', RuntimeWarning)
    if not RAW.exists():
        warnings.warn('Sözlük koruması kapalı: data/raw/common_voice_tr.txt bulunamadı.', RuntimeWarning)
        return None
    # training is a repo-local package, outside the installed src package.
    import sys
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from training.everyday import sentences
    with RAW.open(encoding='utf-8') as stream:
        counts = build_lexicon(stream)
    counts = dict(Counter(counts) + Counter(build_lexicon(sentences())))
    try:
        CACHE.write_bytes(cache_bytes(counts))
    except OSError as exc:
        warnings.warn(f'Sözlük önbelleği yazılamadı: {exc}', RuntimeWarning)
    return counts


def known(word, min_count=1):
    words = tokens(word)
    lexicon = load_lexicon()
    return bool(lexicon is not None and len(words) == 1 and lexicon.get(words[0], 0) >= min_count)
