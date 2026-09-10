"""Observable, seeded Turkish corruptions; each operation records before/after."""
import random
import re
from .text import lower_tr

ASCII = str.maketrans('çğıöşüÇĞİÖŞÜ', 'cgiosuCGIOSU')
INFORMAL = {
    'gideceğim': ['gidicem', 'gidiceğim'], 'gideceğiz': ['gidicez', 'gitcez'],
    'geleceğim': ['gelicem', 'gelcem'], 'geleceğiz': ['gelicez'],
    'yapacağım': ['yapıcam', 'yapcam'], 'yapacağız': ['yapıcaz'],
    'buluşacağız': ['buluşcaz', 'buluscaz'], 'söyleyeceğim': ['söylicem'],
    'bilmiyorum': ['bilmiyom', 'bilmiom'], 'istiyorum': ['istiyom'],
    'olacak': ['olcak'], 'bir şey': ['bişey', 'birşey'], 'her şey': ['herşey'],
    'hiçbir': ['hiç bir'], 'biraz': ['bir az'], 'yalnız': ['yanlız'],
    'yanlış': ['yalnış'], 'değil': ['diil', 'deil'], 'tamam': ['tmm'],
    'merhaba': ['mrb'], 'teşekkür': ['teşekür'], 'çünkü': ['çünki'],
    'herkes': ['herkez'], 'bugün': ['bu gün'], 'şimdi': ['şimdi', 'simdi'],
}
KEYBOARD = ['qwertyuıopğü', 'asdfghjklşi', 'zxcvbnmöç']
NEIGHBORS = {}
for row in KEYBOARD:
    for i, c in enumerate(row):
        NEIGHBORS[c] = row[max(0, i-1):i] + row[i+1:i+2]

class NoiseGenerator:
    names = ['harf_sil', 'harf_tekrar', 'harf_yer_değiştir', 'klavye', 'türkçe_karakter',
             'küçük_harf', 'noktalama_sil', 'noktalama_ekle', 'boşluk_sil', 'boşluk_ekle',
             'fazla_boşluk', 'de_da', 'ki', 'soru_eki', 'kesme', 'gündelik']

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
            return lower_tr(text) if r.random() < .8 else text.swapcase()
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
            keys = [k for k in INFORMAL if re.search(r'\b' + k + r'\b', lower_tr(text))]
            if keys:
                k = r.choice(keys)
                return re.sub(r'\b' + k + r'\b', r.choice(INFORMAL[k]), text, count=1, flags=re.I)
        return text

    def corrupt(self, text, difficulty):
        if difficulty == 'temiz':
            return text, []
        count = {'kolay': 1, 'orta': 2, 'zor': 4}[difficulty]
        history = []
        current = text
        for _ in range(count):
            for attempt in range(16):
                # Favor realistic diacritics/case/chat noise over random destruction.
                kind = self.rng.choice(self.names + ['türkçe_karakter'] * 4 + ['gündelik'] * 3 + ['küçük_harf'])
                changed = self.apply(current, kind)
                if changed != current and changed.strip():
                    history.append({'operation': kind, 'before': current, 'after': changed})
                    current = changed
                    break
        return current, history
