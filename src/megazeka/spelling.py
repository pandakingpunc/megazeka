"""Realistic orthographic mistakes: commonly misspelled words and dropped proper-noun apostrophes.

Unlike the chat rewrites in colloquial.py these are *spelling errors* (TDK "sık yapılan yanlışlar"):
"yalnız" -> "yanlız", "şoför" -> "şöför", "Ankara'ya" -> "Ankaraya". Both operations only propose
a rewrite when the correct form is actually present, so the target is always the original text.
"""
import re
from .text import lower_tr, upper_first

# (correct, [common misspellings], whole_word_only). Without whole_word_only the rule also fires
# on suffixed forms (herkes -> herkesin -> herkezin, şoför -> şoförler -> şöförler).
MISSPELLINGS = [
    ('yalnız', ['yanlız'], False), ('yanlış', ['yalnış'], False), ('herkes', ['herkez'], False),
    ('şoför', ['şöför'], False), ('eşofman', ['eşortman'], False), ('orijinal', ['orjinal'], False),
    ('sürpriz', ['süpriz'], False), ('laboratuvar', ['laboratuar', 'labaratuvar'], False),
    ('egzoz', ['egzos'], False), ('entelektüel', ['entellektüel'], False), ('kılavuz', ['klavuz'], False),
    ('hastane', ['hastahane'], False), ('pantolon', ['pantalon'], False), ('çikolata', ['çukulata'], False),
    ('makine', ['makina'], True), ('meyve', ['meyva'], True), ('mütevazı', ['mütevazi'], True),
    ('ya da', ['yada'], True), ('her zaman', ['herzaman'], True), ('her gün', ['hergün'], True),
    ('hiçbir zaman', ['hiçbirzaman'], True), ('bir daha', ['birdaha'], True), ('o kadar', ['okadar'], True),
    ('bu kadar', ['bukadar'], True), ('yine de', ['yinede'], True), ('bu yüzden', ['buyüzden'], True),
    ('o yüzden', ['oyüzden'], True), ('o zaman', ['ozaman'], True), ('pek çok', ['pekçok'], True),
    ('hoş geldin', ['hoşgeldin'], True), ('hoş geldiniz', ['hoşgeldiniz'], True), ('hoşça kal', ['hoşçakal'], True),
    ('iyi ki', ['iyiki'], True), ('tabii ki', ['tabiki', 'tabi ki'], True), ('birtakım', ['bir takım'], True),
]

# Names that take a case suffix after an apostrophe. Also matches lowercase chat text
# ("ankara'ya"); capitalized words are treated as proper nouns whether listed or not.
PROPER_NAMES = {lower_tr(n) for n in (
    'Ankara İstanbul İzmir Bursa Antalya Adana Konya Eskişehir Kayseri Trabzon Samsun Mersin Gaziantep '
    'Diyarbakır Erzurum Isparta Iğdır Edirne Malatya Denizli Sakarya Muğla Çanakkale Van Sivas Rize '
    'Hatay Tokat Ordu Aydın Türkiye Almanya Fransa İngiltere Avrupa Amerika Irak İran Japonya '
    'Ali Ayşe Mehmet Zeynep Fatma Ahmet Mustafa Elif Emre Işık Irmak Ilgaz Ilgın Işıl Işın İpek İlker '
    'İlkay İrem İsmail İbrahim İnci İlhan İdil Selin Can Deniz Burak Merve Cem Eren Ece Kerem'
).split()}

_SUFFIXED = re.compile(r"(?<![\w'’])([A-Za-zÇĞİIıÖŞÜçğöşü]+)['’]([a-zçğıöşü]+)")


def _fix_case(original, replacement):
    return upper_first(replacement) if original[:1].isupper() else replacement


def misspelling_candidates(text):
    """(start, end, [wrong forms]) for every common misspelling target present in `text`."""
    lowered = lower_tr(text)
    found = []
    if len(lowered) != len(text):
        return found
    for correct, wrong, whole in MISSPELLINGS:
        pattern = r'(?<!\w)' + re.escape(correct) + (r'(?!\w)' if whole else '')
        for m in re.finditer(pattern, lowered):
            original = text[m.start():m.start() + len(correct)]
            found.append((m.start(), m.start() + len(correct), [_fix_case(original, w) for w in wrong]))
    return found


def apostrophe_candidates(text):
    """(start, end) of the apostrophe in proper-noun + suffix pairs: Ankara'ya, ayşe'nin, Işık'ın."""
    found = []
    for m in _SUFFIXED.finditer(text):
        name = m.group(1)
        if name[:1].isupper() or lower_tr(name) in PROPER_NAMES:
            found.append((m.start() + len(name), m.start() + len(name) + 1))
    return found


def misspell(text, rng):
    options = misspelling_candidates(text)
    if not options:
        return text
    start, end, forms = rng.choice(options)
    return text[:start] + rng.choice(forms) + text[end:]


def drop_proper_apostrophe(text, rng):
    """Remove the apostrophe from one proper noun + suffix (sometimes from every one)."""
    options = apostrophe_candidates(text)
    if not options:
        return text
    if len(options) > 1 and rng.random() < .4:
        chosen = options
    else:
        chosen = [rng.choice(options)]
    for start, end in sorted(chosen, reverse=True):
        text = text[:start] + text[end:]
    return text
