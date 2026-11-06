"""Observable, seeded Turkish corruptions; each operation records before/after."""
import random
import re
from .text import lower_tr, swapcase_tr
from .colloquial import colloquialize, rewrite, hard_candidates, ne_candidates
from .spelling import misspell, drop_proper_apostrophe, misspelling_candidates, apostrophe_candidates

ASCII = str.maketrans('çğıöşüÇĞİÖŞÜ', 'cgiosuCGIOSU')
KEYBOARD = ['qwertyuıopğü', 'asdfghjklşi', 'zxcvbnmöç']
NEIGHBORS = {}
for row in KEYBOARD:
    for i, c in enumerate(row):
        NEIGHBORS[c] = row[max(0, i-1):i] + row[i+1:i+2]

class NoiseGenerator:
    names = ['harf_sil', 'harf_tekrar', 'harf_yer_değiştir', 'klavye', 'türkçe_karakter',
             'küçük_harf', 'noktalama_sil', 'noktalama_ekle', 'boşluk_sil', 'boşluk_ekle',
             'fazla_boşluk', 'de_da', 'ki', 'soru_eki', 'kesme', 'gündelik',
             'sert_ünsüz', 'ne_kısalt', 'yazım_yanlışı', 'özel_ad_kesme']
    # Operations that are only applicable to specific words; used to target everyday sentences.
    targeted = {'sert_ünsüz': lambda t: bool(hard_candidates(t)), 'ne_kısalt': lambda t: bool(ne_candidates(t)),
                'yazım_yanlışı': lambda t: bool(misspelling_candidates(t)),
                'özel_ad_kesme': lambda t: bool(apostrophe_candidates(t))}

    def __init__(self, seed=42):
        self.rng = random.Random(seed)

    def apply(self, text, kind):
        r = self.rng
        letters = [i for i, c in enumerate(text) if c.isalpha()]
        if not letters:
            return text
        i = r.choice(letters)
        if kind == 'harf_sil':
            return text[:i] + text[i+1:]
        if kind == 'harf_tekrar':
            return text[:i] + text[i] * r.randint(2, 3) + text[i+1:]
        if kind == 'harf_yer_değiştir' and i + 1 < len(text) and text[i+1].isalpha():
            return text[:i] + text[i+1] + text[i] + text[i+2:]
        if kind == 'klavye' and lower_tr(text[i]) in NEIGHBORS:
            return text[:i] + r.choice(NEIGHBORS[lower_tr(text[i])]) + text[i+1:]
        if kind == 'türkçe_karakter':
            return ''.join(c.translate(ASCII) if r.random() < .7 else c for c in text)
        if kind == 'küçük_harf':
            return lower_tr(text) if r.random() < .8 else swapcase_tr(text)
        if kind == 'noktalama_sil':
            return re.sub(r'[.,!?;:]', '', text)
        if kind == 'noktalama_ekle':
            return text[:i] + r.choice('.,!?') + text[i:]
        if kind == 'boşluk_sil':
            spaces = [m.start() for m in re.finditer(' ', text)]
            if spaces:
                i = r.choice(spaces)
                return text[:i] + text[i+1:]
        if kind == 'boşluk_ekle':
            return text[:i] + ' ' + text[i:]
        if kind == 'fazla_boşluk':
            return text.replace(' ', '  ', 1)
        if kind == 'de_da':
            return re.sub(r'\b(\w+) (de|da)\b', r'\1\2', text, count=1)
        if kind == 'ki':
            if re.search(r'\bki\b', text):
                return re.sub(r' (ki)\b', r'\1', text, count=1)
            return re.sub(r'(\w{3,})(ki)\b', r'\1 \2', text, count=1)
        if kind == 'soru_eki':
            return re.sub(r' (m[ıiuü](?:s[ıiuü]n(?:[ıiuü]z)?|y[ıiuü]m|y[ıiuü]z)?)\b', r'\1', text, count=1)
        if kind == 'kesme':
            return text.replace("'", '').replace('’', '')
        if kind == 'gündelik':
            return colloquialize(text, r)
        if kind == 'sert_ünsüz':
            return rewrite(text, r, hard_candidates)
        if kind == 'ne_kısalt':
            return rewrite(text, r, ne_candidates)
        if kind == 'yazım_yanlışı':
            return misspell(text, r)
        if kind == 'özel_ad_kesme':
            return drop_proper_apostrophe(text, r)
        return text

    def preferred(self, text):
        """Pick the first operation for an everyday sentence: a targeted one when the sentence
        contains a softening verb, a ne-contraction, a common misspelling target or a proper noun
        with a suffix apostrophe; otherwise the generic colloquial rewrite."""
        options = [name for name, applies in self.targeted.items() if applies(text)]
        # Generic colloquial rewrite keeps the vowel-initial forms (gidicem) well represented.
        generic = .15 if {'ne_kısalt', 'yazım_yanlışı'} & set(options) else .35
        return self.rng.choice(options) if options and self.rng.random() > generic else 'gündelik'

    def corrupt(self, text, difficulty, prefer=None):
        """Apply 1/2/4 successful operations. `prefer` forces the first attempted operation
        (used so everyday sentences always carry at least one colloquial rewrite)."""
        if difficulty == 'temiz':
            return text, []
        count = {'kolay': 1, 'orta': 2, 'zor': 4}[difficulty]
        history = []
        current = text
        for n in range(count):
            for attempt in range(16):
                if n == 0 and attempt == 0 and prefer:
                    kind = prefer
                else:
                    # Favor realistic diacritics/case/chat noise over random destruction.
                    kind = self.rng.choice(self.names + ['türkçe_karakter'] * 4 + ['gündelik'] * 3 + ['küçük_harf']
                                         + ['yazım_yanlışı'] * 3 + ['özel_ad_kesme'] * 3 + ['sert_ünsüz'] * 2 + ['ne_kısalt'] * 2)
                changed = self.apply(current, kind)
                if changed != current and changed.strip():
                    history.append({'operation': kind, 'before': current, 'after': changed})
                    current = changed
                    break
        return current, history
