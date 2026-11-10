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

# Opt-in only: extending MISSPELLINGS would change the seeded v3.1 stream.
# Unambiguous standard spellings; ambiguous lexical pairs (e.g. direk/direkt,
# mütevazı/mütevazi) are not added here. Existing v3.1 entries stay untouched.
MISSPELLINGS_V32 = [
    ('tıraş', ['traş'], False), ('kibrit', ['kirbit'], False),
    ('sarımsak', ['sarmısak'], False), ('şarj', ['şarz'], False),
    ('kirpik', ['kiprik'], False), ('ukala', ['ukela'], False),
    ('döviz', ['dövüz'], False), ('poğaça', ['poaça'], False),
    ('kravat', ['kıravat'], False), ('tişört', ['tişort'], False),
    ('aferin', ['aferim'], True), ('maydanoz', ['maydonoz'], False),
    ('muhatap', ['muhattap'], False), ('muhasebe', ['muhasepe'], False),
    ('müteahhit', ['mütahit', 'müteahit'], False), ('müsaade', ['müsade'], False),
    ('iddia', ['iddaa'], False), ('inisiyatif', ['insiyatif'], False),
    ('doküman', ['döküman'], False), ('tren', ['tiren'], False),
    ('film', ['filim'], False), ('espri', ['espiri'], False),
    ('astronot', ['astronat'], False),
    ('antrenman', ['antreman'], False), ('antrenör', ['antirenör'], False),
    ('sandviç', ['sandüviç'], False), ('bisküvi', ['büsküvi'], False),
    ('deodorant', ['deodarant'], False), ('restoran', ['restorant'], False),
    ('karnabahar', ['karnıbahar'], False), ('kavanoz', ['kavonoz'], False),
    ('fasulye', ['fasülye'], False), ('ekşi', ['eşki'], False),
    ('maalesef', ['malesef'], True), ('mükemmel', ['mükemel'], False),
    ('teşekkür', ['teşekür'], False), ('sıhhat', ['sıhat'], False),
    ('yanlış', ['yannış'], False),
]

# Separate vocabulary for the opt-in name corruption; never extend PROPER_NAMES.
NAMES_V32 = frozenset((
    'Isparta Iğdır Ilgaz Ilgın Ilıca Işık Işıl Işın Irmak Irak Ihlara Ilgar '
    'İzmir İstanbul İpek İrem İsmail İnegöl İznik İskenderun İran İtalya İngiltere İsveç İspir '
    'Ankara Bursa Antalya Ali Ayşe Zeynep Deniz Ahmet'
).split())

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


def misspelling_candidates(text, *, v32=False):
    """(start, end, [wrong forms]) for every common misspelling target present in `text`."""
    lowered = lower_tr(text)
    found = []
    if len(lowered) != len(text):
        return found
    for correct, wrong, whole in (MISSPELLINGS + MISSPELLINGS_V32 if v32 else MISSPELLINGS):
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


def misspell(text, rng, *, v32=False):
    options = misspelling_candidates(text, v32=v32)
    if not options:
        return text
    start, end, forms = rng.choice(options)
    return text[:start] + rng.choice(forms) + text[end:]


def corrupt_proper_name(text, rng):
    """One known, capitalized name: Turkish lowercase, ASCII, or I/İ confusion.

    The exact-token vocabulary avoids treating any sentence-initial capital as a
    name. The targeted corpus marks actual names; ordinary lowercase nouns such
    as ışık/ırmak are never selected. Apostrophe suffixes may lose their separator.
    """
    options = [m for m in re.finditer(r'\b[A-Za-zÇĞİÖŞÜçğıöşü]+\b', text)
               if m.group() in NAMES_V32]
    if not options:
        return text
    match = rng.choice(options)
    name = match.group()
    ascii_table = str.maketrans('çğıöşüÇĞİÖŞÜ', 'cgiosuCGIOSU')
    # Fold suffix letters as well for the keyboard modes: Işık'ın -> isik'in.
    suffix_match = re.match(r"['’][a-zçğıöşü]+", text[match.end():])
    tail = suffix_match.group() if suffix_match else ''
    variants = [lower_tr(name) + tail, (name + tail).translate(ascii_table),
                lower_tr(name + tail).translate(ascii_table)]
    if name.startswith('I'):
        variants.append('İ' + name[1:] + tail)
    elif name.startswith('İ'):
        variants.append('I' + name[1:] + tail)
    variants = list(dict.fromkeys(v for v in variants if v != name + tail))
    replacement = rng.choice(variants)
    if tail and rng.random() < .35:
        replacement = replacement.replace("'", '').replace('’', '')
    return text[:match.start()] + replacement + text[match.end() + len(tail):]


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
