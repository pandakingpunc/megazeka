"""Optional dictionary-assisted correction on top of the model output (zeyrek morphology)."""
import contextlib
import importlib.util
import io
import logging
import re
import warnings
from functools import lru_cache
from .text import lower_tr, upper_first

DICTIONARY_MARGIN = 11.0
MIN_KNOWN_COUNT = 3
MAX_CANDIDATES = 12
MIN_WORD_LENGTH = 4
ALPHABET = 'abcçdefgğhıijklmnoöprsştuüvyz'
_SPACE = re.compile(r'(\s+)')
_CLOSERS = '"\'”’»)]'


def available():
    if importlib.util.find_spec('zeyrek') is None:
        warnings.warn('Sözlük desteği kapalı: zeyrek kurulu değil.', RuntimeWarning)
        return False
    return True


@lru_cache(maxsize=1)
def _analyzer():
    logging.getLogger('zeyrek').setLevel(logging.CRITICAL)
    with contextlib.redirect_stdout(io.StringIO()):
        import zeyrek
        return zeyrek.MorphAnalyzer()


@lru_cache(maxsize=None)
def valid(word):
    """True when zeyrek can analyse the (lower-cased) word."""
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return bool(_analyzer()._parse(lower_tr(word)))
    except Exception:
        return False


def _edits(word):
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    found = {a + b[1:] for a, b in splits if b}
    found |= {a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1}
    found |= {a + c + b[1:] for a, b in splits if b for c in ALPHABET}
    found |= {a + c + b for a, b in splits for c in ALPHABET}
    found.discard(word)
    return found


@lru_cache(maxsize=None)
def _candidates(word):
    return tuple(sorted(w for w in _edits(word) if valid(w)))


def candidates(word):
    """Valid words one edit (insert/delete/replace/transpose) away from the lower-cased word."""
    return list(_candidates(lower_tr(word)))


def _split(token):
    start = 0
    while start < len(token) and not token[start].isalnum():
        start += 1
    end = len(token)
    while end > start and not token[end - 1].isalnum():
        end -= 1
    return token[:start], token[start:end], token[end:]


def assist(source, candidate, score, valid=valid, candidates=candidates, known=None, margin=None):
    """Replace invalid words in candidate with the best-scoring one-edit valid word.
    score(source, sentences) -> log-probabilities. margin defaults to the
    module-level DICTIONARY_MARGIN (read at call time). Returns (text, changes)."""
    if known is None:
        from .lexicon import known
    if margin is None:
        margin = DICTIONARY_MARGIN
    parts = _SPACE.split(candidate)
    indices = [i for i in range(0, len(parts), 2) if parts[i]]
    source_words = source.split()
    aligned = len(source_words) == len(indices)
    changes = []
    for position, i in enumerate(indices):
        lead, core, trail = _split(parts[i])
        if len(core) < MIN_WORD_LENGTH or not core.isalpha() or core.isupper():
            continue
        if core[0].isupper():
            previous = parts[indices[position - 1]].rstrip(_CLOSERS) if position else ''
            if position and not previous.endswith(('.', '!', '?')):
                continue
        low = lower_tr(core)
        if valid(low) or known(low, min_count=MIN_KNOWN_COUNT):
            continue
        options = list(candidates(low))
        if aligned:
            _, origin, _ = _split(source_words[position])
            origin = lower_tr(origin)
            if origin != low and origin.isalpha():
                options += list(candidates(origin)) + ([origin] if valid(origin) else [])
        options = [o for n, o in enumerate(options) if o != low and o not in options[:n]]
        if not options or len(options) > MAX_CANDIDATES:
            continue
        capital = core[0].isupper()
        sentences = []
        for option in options:
            word = upper_first(option) if capital else option
            sentences.append(''.join(parts[:i]) + lead + word + trail + ''.join(parts[i + 1:]))
        current = ''.join(parts)
        scores = score(source, [current, *sentences])
        best = max(range(len(options)), key=lambda n: scores[n + 1])
        if scores[best + 1] > scores[0] - margin:
            parts[i] = lead + (upper_first(options[best]) if capital else options[best]) + trail
            changes.append({'old': core, 'new': parts[i][len(lead):len(parts[i]) - len(trail)],
                            'candidates': len(options), 'gain': scores[best + 1] - scores[0]})
    return ''.join(parts), changes
