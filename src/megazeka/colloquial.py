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
    'yani': ['yni'], 'tabii': ['tabi'], 'ağabey': ['abi'],
}

# "ne yap-/ol-/haber" chat contractions: napcam, napıyosun, noldu, nolur, naber. Each key is the
# correct two-word phrase; values are informal spellings users type.
NE = {
    'ne yapıyorsun': ['napıyosun'] * 3 + ['napıyon'] * 2 + ['nabıyon', 'nabıyosun', 'napıyorsun'],
    'ne yapıyorsunuz': ['napıyosunuz', 'napıyorsunuz', 'napıyonuz', 'nabıyosunuz'],
    'ne yapıyorum': ['napıyom', 'napıyorum'], 'ne yapıyoruz': ['napıyoz', 'napıyoruz'],
    'ne yapıyor': ['napıyo', 'napıyor', 'nabıyo'], 'ne yapıyorlar': ['napıyolar', 'napıyorlar'],
    'ne yapacağım': ['napcam'] * 3 + ['napıcam', 'ne yapıcam', 'napacam'],
    'ne yapacağız': ['napcaz'] * 3 + ['napıcaz', 'ne yapıcaz'],
    'ne yapacaksın': ['napcaksın', 'napıcaksın', 'napcan', 'napıcan', 'ne yapıcan'],
    'ne yapacaksınız': ['napcaksınız', 'napıcaksınız'], 'ne yapacak': ['napcak', 'napıcak'],
    'ne yapayım': ['napayım', 'napiyim', 'napim'], 'ne yapalım': ['napalım'],
    'ne yapsam': ['napsam'], 'ne yapsın': ['napsın'], 'ne yapmalıyım': ['napmalıyım'], 'ne yapmalıyız': ['napmalıyız'],
    'ne yaptın': ['naptın'], 'ne yaptım': ['naptım'], 'ne yaptık': ['naptık'], 'ne yaptınız': ['naptınız'],
    'ne yaparsın': ['naparsın'], 'ne yapar': ['napar'],
    'ne oldu': ['noldu'], 'ne olur': ['nolur'], 'ne oluyor': ['noluyor', 'noluyo'],
    'ne olacak': ['nolacak', 'nolcak'], 'ne olmuş': ['nolmuş'], 'ne olsun': ['nolsun'],
    'ne olursa': ['nolursa'], 'ne olmadı': ['nolmadı'],
    'ne haber': ['naber', 'nbr'],
}
WORDS.update(NE)

# Softening verbs (git-, et-, tat-, kaybet-): the written future is "gideceğim" but users type
# the hard consonant, "gitcem", "etcek", and the second person as "gitcen".
FUTURE_ALT = {'eceksin': ('icen', 'cen'), 'acaksın': ('ıcan', 'can')}
SOFT_STEMS = ('gid', 'ed', 'tad', 'güd')


def _harmony(stem):
    """Narrow vowel that follows the last vowel of `stem` (four-way vowel harmony)."""
    for c in reversed(lower_tr(stem)):
        if c in VOWELS:
            return {'a': 'ı', 'ı': 'ı', 'e': 'i', 'i': 'i', 'o': 'u', 'u': 'u', 'ö': 'ü', 'ü': 'ü'}[c]
    return 'ı'


def _preserve_case(original, replacement):
    return upper_first(replacement) if original[:1].isupper() else replacement


def _harden(stem):
    """gid -> git, ed -> et, tad -> tat: restore the t that softened to d before a vowel."""
    return stem[:-1] + ('T' if stem[-1] == 'D' else 't') if lower_tr(stem[-1]) == 'd' else stem


def _future_forms(stem, vowel_form, consonant_form):
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
        forms = [stem + vowel_form, _harden(stem) + consonant_form]
    return forms


def hard_candidates(text):
    """Softening verbs typed with the hard consonant: gideceğiz -> gitcez, yardım edeceğim ->
    yardım etcem, gideceksin -> gitcen. Only these hard forms (no vowel-initial ones)."""
    found = []
    lowered = lower_tr(text)
    if len(lowered) != len(text):
        return found
    for word in re.finditer(r'\w+', lowered):
        start, end, w = word.start(), word.end(), word.group()
        original = text[start:end]
        for suffix, vowel_form, consonant_form in FUTURE:
            if not w.endswith(suffix) or len(w) - len(suffix) < 2:
                continue
            stem = original[:len(w) - len(suffix)]
            if lower_tr(stem).endswith(SOFT_STEMS):
                options = [consonant_form] + ([FUTURE_ALT[suffix][1]] if suffix in FUTURE_ALT else [])
                found.append((start, end, [_preserve_case(original, _harden(stem) + f) for f in options]))
            break
    return found


def ne_candidates(text):
    """"ne yapıyorsun / ne yapacağım / ne oldu / ne haber" -> napıyosun, napcam, noldu, naber."""
    lowered = lower_tr(text)
    found = []
    if len(lowered) != len(text):
        return found
    for phrase, forms in NE.items():
        for m in re.finditer(r'(?<!\w)' + re.escape(phrase) + r'(?!\w)', lowered):
            original = text[m.start():m.end()]
            found.append((m.start(), m.end(), [_preserve_case(original, f) for f in forms]))
    return found


def rewrite(text, rng, finder):
    """Apply one random rewrite proposed by `finder` (hard_candidates / ne_candidates)."""
    options = finder(text)
    if not options:
        return text
    start, end, forms = rng.choice(options)
    return text[:start] + rng.choice(forms) + text[end:]


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
            forms = _future_forms(stem, vowel_form, consonant_form)
            if suffix in FUTURE_ALT:
                forms += _future_forms(stem, *FUTURE_ALT[suffix])
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
