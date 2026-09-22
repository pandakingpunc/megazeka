"""Rule-based Turkish colloquial (chat-style) corruptions applied to correct text.

Every rule maps a *correct* written form to one or more informal spellings that
real users type: "gideceğim" -> "gidicem", "geliyorum" -> "geliyom",
"burada" -> "burda", "ne yapıyorsun" -> "napıyosun". Suffix rules generalize to
any verb, so the model is not limited to a fixed word list.
"""
import re
from .text import lower_tr, upper_first

VOWELS = 'aeıioöuü'

# Future tense: (suffix on the correct form, vowel-initial informal form, consonant-initial informal form)
FUTURE = [
    ('eceğim', 'icem', 'cem'), ('acağım', 'ıcam', 'cam'),
    ('eceğiz', 'icez', 'cez'), ('acağız', 'ıcaz', 'caz'),
    ('eceksiniz', 'iceksiniz', 'ceksiniz'), ('acaksınız', 'ıcaksınız', 'caksınız'),
    ('eceksin', 'iceksin', 'ceksin'), ('acaksın', 'ıcaksın', 'caksın'),
    ('ecekler', 'icekler', 'cekler'), ('acaklar', 'ıcaklar', 'caklar'),
    ('ecek', 'icek', 'cek'), ('acak', 'ıcak', 'cak'),
]
# Plain suffix substitutions (negative future, present progressive). Longest first.
SUFFIX = [
    ('meyeceğim', ['micem']), ('mayacağım', ['mıcam']), ('meyeceğiz', ['micez']), ('mayacağız', ['mıcaz']),
    ('meyeceksin', ['miceksin']), ('mayacaksın', ['mıcaksın']), ('meyecekler', ['micekler']), ('mayacaklar', ['mıcaklar']),
    ('meyecek', ['micek']), ('mayacak', ['mıcak']),
    ('yorsunuz', ['yosunuz']), ('yorlar', ['yolar']), ('yorum', ['yom']), ('yorsun', ['yosun']), ('yoruz', ['yoz']),
    ('yordum', ['yodum']), ('yordun', ['yodun']), ('yorduk', ['yoduk']), ('yordu', ['yodu']), ('yormuş', ['yomuş']),
    ('yor', ['yo']),
]
# Whole words and phrases; matched case-insensitively on word boundaries.
WORDS = {
    'burada': ['burda'], 'orada': ['orda'], 'şurada': ['şurda'], 'nerede': ['nerde'],
    'buradan': ['burdan'], 'oradan': ['ordan'], 'nereden': ['nerden'],
    'içeride': ['içerde'], 'dışarıda': ['dışarda'], 'yukarıda': ['yukarda'], 'aşağıda': ['aşağda'],
    'ne yapıyorsun': ['napıyorsun', 'napıyosun', 'napıyon'], 'ne yapıyorsunuz': ['napıyorsunuz', 'napıyosunuz'],
    'ne yapıyorum': ['napıyorum', 'napıyom'], 'ne yapıyor': ['napıyor', 'napıyo'],
    'ne yapacağım': ['napcam', 'napıcam', 'ne yapıcam'], 'ne yapacağız': ['napcaz', 'napıcaz'],
    'ne yapacaksın': ['napcaksın', 'napıcaksın'], 'ne yapacak': ['napcak', 'napıcak'],
    'ne yapayım': ['napayım', 'napiyim'], 'ne yapalım': ['napalım'], 'ne yapsam': ['napsam'],
    'ne oldu': ['noldu'], 'ne olur': ['nolur'], 'ne oluyor': ['noluyor', 'noluyo'], 'ne olacak': ['nolacak', 'nolcak'],
    'bir şey': ['bişey', 'birşey', 'bişi'], 'bir şeyler': ['bişeyler', 'birşeyler'],
    'her şey': ['herşey'], 'hiçbir şey': ['hiçbişey', 'hiçbirşey', 'hiç bir şey'], 'hiçbir': ['hiç bir'],
    'herhangi bir': ['herhangibir'], 'birçok': ['bir çok'], 'birkaç': ['bir kaç'],
    'değil mi': ['dimi', 'değilmi', 'deilmi'], 'değil': ['diil', 'deil', 'değl'],
    'tamam': ['tmm', 'tamm'], 'teşekkürler': ['tşk', 'teşekürler', 'tesekkurler'],
    'teşekkür ederim': ['teşekür ederim', 'tşk ederim'], 'teşekkür': ['teşekür'],
    'merhaba': ['mrb', 'merhba'], 'selam': ['slm'], 'nasılsın': ['nasılsn', 'nslsn'],
    'çünkü': ['çünki'], 'herkes': ['herkez'], 'yalnız': ['yanlız'], 'yanlış': ['yalnış'],
    'bugün': ['bu gün'], 'inşallah': ['inşalah', 'inş'], 'maalesef': ['malesef'],
    'sürpriz': ['süpriz'], 'orijinal': ['orjinal'], 'herhalde': ['heralde'], 'şu anda': ['şuanda', 'şuan'],
    'şu an': ['şuan'], 'kesinlikle': ['kesinlkle'], 'sonra': ['sora'], 'birazdan': ['bi azdan'],
    'bilmiyorum': ['bilmiyom', 'bilmem', 'blmiyorum'], 'istiyorum': ['istiyom', 'istiom'],
    'gideceğim': ['gitcem'], 'gideceğiz': ['gitcez'], 'gidecek': ['gitcek'], 'edeceğim': ['etcem'],
    'biraz': ['bi raz', 'bir az'], 'bir': ['bi'], 'ne kadar': ['nekadar'],
    'yani': ['yni'], 'tabii': ['tabi'], 'ağabey': ['abi'], 'ne haber': ['naber'],
}


def _harmony(stem):
    """Narrow vowel that follows the last vowel of `stem` (four-way vowel harmony)."""
    for c in reversed(lower_tr(stem)):
        if c in VOWELS:
            return {'a': 'ı', 'ı': 'ı', 'e': 'i', 'i': 'i', 'o': 'u', 'u': 'u', 'ö': 'ü', 'ü': 'ü'}[c]
    return 'ı'


def _preserve_case(original, replacement):
    return upper_first(replacement) if original[:1].isupper() else replacement


def candidates(text):
    """All informal rewrites applicable to `text` as (start, end, [replacements])."""
    lowered = lower_tr(text)
    if len(lowered) != len(text):
        return []
    found = []
    for word in re.finditer(r'\w+', lowered):
        start, end, w = word.start(), word.end(), word.group()
        original = text[start:end]
        matched = False
        for suffix, forms in SUFFIX:
            # Negative future and present progressive are plain substitutions; checked first
            # so "yapmayacağım" prefers "yapmıcam" over the generic future rule.
            cut = len(w) - len(suffix)
            if not w.endswith(suffix) or cut < 2:
                continue
            if suffix.startswith('m') or lower_tr(w[cut - 1]) in 'ıiuü':
                stem = original[:cut]
                found.append((start, end, [_preserve_case(original, stem + f) for f in forms]))
                matched = True
                break
        if matched:
            continue
        for suffix, vowel_form, consonant_form in FUTURE:
            if not w.endswith(suffix) or len(w) - len(suffix) < 2:
                continue
            stem = original[:len(w) - len(suffix)]
            vowel_form = _harmony(stem) + vowel_form[1:]
            if stem.endswith('y') and len(stem) > 2 and lower_tr(stem[-2]) in VOWELS:
                # söyle-y-eceğim -> söylecem, söyleycem, söylicem ; oku-y-acağım -> okucam, okuycam
                base = stem[:-1]
                forms = [base + consonant_form, stem + consonant_form]
                dropped = lower_tr(base[-1])
                if dropped in 'eai':
                    forms.append(base[:-1] + {'e': 'i', 'a': 'ı', 'i': 'i'}[dropped] + vowel_form[1:])
            elif lower_tr(stem[-1:]) in VOWELS:
                forms = [stem + consonant_form, stem + 'y' + consonant_form]
            else:
                hard = stem[:-1] + 't' if lower_tr(stem[-1]) == 'd' else stem
                forms = [stem + vowel_form, hard + consonant_form]
            found.append((start, end, [_preserve_case(original, f) for f in forms]))
            break
    for phrase, forms in WORDS.items():
        for m in re.finditer(r'(?<!\w)' + re.escape(phrase) + r'(?!\w)', lowered):
            original = text[m.start():m.end()]
            found.append((m.start(), m.end(), [_preserve_case(original, f) for f in forms]))
    return found


def colloquialize(text, rng):
    """Apply one randomly chosen informal rewrite; returns text unchanged if none applies."""
    options = candidates(text)
    if not options:
        return text
    # Common single words like "bir" should not dominate: weight suffix rules and phrases higher.
    weights = [1 if lower_tr(text[s:e]) == 'bir' else 4 for s, e, _ in options]
    start, end, forms = rng.choices(options, weights=weights)[0]
    return text[:start] + rng.choice(forms) + text[end:]
