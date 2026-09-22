"""Template-generated everyday Turkish sentences (first/second person, future and present tense).

Common Voice sentences are literary and mostly third person, so forms like "gideceğim",
"yapacağız", "geliyor musun" are almost absent from the corpus. This module produces
grammatically correct, plain everyday sentences from a small verb table with a minimal
conjugator, so the noise generator can teach the model "gidicem -> gideceğim" style fixes.
All sentences are authored for this project and released under CC0-1.0.
"""
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from megazeka.text import canonical, upper_first

VOWELS = 'aeıioöuü'
SOFT = {'git': 'gid', 'et': 'ed', 'tat': 'tad'}
NARROW = {'a': 'ı', 'ı': 'ı', 'e': 'i', 'i': 'i', 'o': 'u', 'u': 'u', 'ö': 'ü', 'ü': 'ü'}

# stem, aorist form, complements (already inflected), optional third-person subjects allowed
VERBS = [
    ('gel', 'gelir', ['eve', 'yanına', 'size', 'okula', 'işe', 'buraya', 'toplantıya', 'maça', 'düğüne', 'sizinle']),
    ('git', 'gider', ['okula', 'işe', 'markete', 'eve', 'sinemaya', 'doktora', "Ankara'ya", 'kursa', 'tatile', 'parka', 'kütüphaneye', 'alışverişe', 'dersaneye', 'spora']),
    ('yap', 'yapar', ['ödevimi', 'yemek', 'spor', 'alışveriş', 'temizlik', 'kahvaltı', 'bir şeyler', 'projeyi', 'sunumu', 'elimden geleni']),
    ('al', 'alır', ['ekmek', 'bilet', 'yeni bir telefon', 'hediye', 'kitap', 'süt', 'seni okuldan', 'biraz meyve']),
    ('gör', 'görür', ['seni', 'onu', 'filmi', 'arkadaşlarımı', 'doktoru', 'sonucu']),
    ('oku', 'okur', ['kitabı', 'bu yazıyı', 'mesajını', 'gazeteyi', 'ödevini', 'biraz']),
    ('bekle', 'bekler', ['seni', 'otobüsü', 'cevabını', 'burada', 'kapıda', 'biraz daha']),
    ('söyle', 'söyler', ['sana', 'ona', 'her şeyi', 'gerçeği', 'anneme', 'sonra']),
    ('anlat', 'anlatır', ['sana', 'her şeyi', 'olanları', 'akşam', 'sonra']),
    ('çalış', 'çalışır', ['sınava', 'bütün gün', 'akşama kadar', 'yarın', 'daha çok', 'kütüphanede']),
    ('konuş', 'konuşur', ['onunla', 'seninle', 'müdürle', 'sonra', 'öğretmenle', 'bu konuyu']),
    ('ara', 'arar', ['seni', 'onu', 'annemi', 'akşam', 'sonra', 'doktoru']),
    ('yaz', 'yazar', ['sana', 'mesaj', 'ödevi', 'raporu', 'akşam']),
    ('ye', 'yer', ['yemek', 'pizza', 'dışarıda', 'bir şeyler', 'evde', 'kahvaltıyı']),
    ('iç', 'içer', ['çay', 'kahve', 'su', 'bir şey']),
    ('uyu', 'uyur', ['erken', 'biraz', 'geç', 'burada']),
    ('kalk', 'kalkar', ['erken', 'saat yedide', 'geç', 'sabah']),
    ('çık', 'çıkar', ['dışarı', 'evden', 'işten', 'yola', 'biraz']),
    ('dön', 'döner', ['eve', 'geri', 'akşam', 'yarın', 'İstanbul\'a']),
    ('otur', 'oturur', ['evde', 'burada', 'biraz', 'bahçede']),
    ('izle', 'izler', ['film', 'maçı', 'dizi', 'seni', 'haberleri']),
    ('dinle', 'dinler', ['seni', 'müzik', 'dersi', 'onu']),
    ('başla', 'başlar', ['işe', 'derse', 'yarın', 'spora', 'yeni bir kitaba']),
    ('bitir', 'bitirir', ['ödevi', 'işi', 'kitabı', 'projeyi', 'yemeği']),
    ('öğren', 'öğrenir', ['İngilizce', 'yüzme', 'bunu', 'sonucu', 'araba kullanmayı']),
    ('unut', 'unutur', ['seni', 'bunu', 'her şeyi', 'onu']),
    ('sor', 'sorar', ['sana', 'ona', 'hocaya', 'bunu', 'anneme']),
    ('ver', 'verir', ['sana', 'parayı', 'kitabı', 'haber', 'cevap']),
    ('getir', 'getirir', ['sana', 'kitabı', 'yemek', 'hediye', 'çantayı']),
    ('götür', 'götürür', ['seni', 'onu', 'arabayı', 'çocukları okula']),
    ('bul', 'bulur', ['seni', 'bir yol', 'çözüm', 'onu', 'anahtarı']),
    ('dene', 'dener', ['tekrar', 'bunu', 'yarın', 'bir kez daha']),
    ('düşün', 'düşünür', ['bunu', 'seni', 'biraz', 'teklifi']),
    ('öde', 'öder', ['borcumu', 'faturayı', 'hesabı', 'kirayı']),
    ('pişir', 'pişirir', ['yemek', 'kek', 'çorba', 'akşam yemeğini']),
    ('temizle', 'temizler', ['evi', 'odayı', 'masayı', 'mutfağı']),
    ('yürü', 'yürür', ['parkta', 'biraz', 'sahilde', 'eve kadar']),
    ('koş', 'koşar', ['sabah', 'parkta', 'biraz', 'her gün']),
    ('kal', 'kalır', ['evde', 'burada', 'yurtta', "İstanbul'da", 'biraz daha', 'sende']),
    ('buluş', 'buluşur', ['seninle', 'arkadaşlarla', 'kafede', 'saat beşte', 'okulun önünde']),
    ('et', 'eder', ['sana yardım', 'ona yardım', 'sana telefon', 'işe devam', 'sana teşekkür', 'seni davet', 'bunu kabul']),
    ('ol', 'olur', ['orada', 'evde', 'hazır', 'geç', 'mutlu', 'yanında', 'burada']),
    ('hazırla', 'hazırlar', ['kahvaltıyı', 'sunumu', 'çantamı', 'yemeği']),
    ('taşın', 'taşınır', ['yeni eve', "İstanbul'a", 'yakında']),
    ('de', 'der', ['sana bir şey', 'ona', 'sana şunu']),
    ('gönder', 'gönderir', ['sana', 'mesajı', 'fotoğrafları', 'dosyayı']),
    ('bak', 'bakar', ['sana', 'çocuklara', 'buna', 'sonra']),
    ('uğra', 'uğrar', ['size', 'markete', 'sana', 'eve']),
    ('anla', 'anlar', ['seni', 'bunu', 'her şeyi']),
    ('sev', 'sever', ['seni', 'bunu', 'burayı']),
]
PROPER = {'Ali', 'Ayşe', 'Mehmet', 'Zeynep'}
TIME_WORDS = {'yarın', 'akşam', 'sabah', 'sonra', 'erken', 'geç', 'her gün', 'bütün gün', 'akşama kadar', 'yakında', 'saat beşte', 'saat yedide'}
SUBJECTS_3 = ['Annem', 'Babam', 'Ali', 'Ayşe', 'Öğretmen', 'Arkadaşım', 'Kardeşim', 'O', 'Mehmet', 'Zeynep', 'Hocam', 'Komşumuz']
ADVERBS = ['Yarın', 'Bugün', 'Bu akşam', 'Hafta sonu', 'Sabah', 'Akşam', 'Birazdan', 'Şimdi', 'Gelecek hafta', 'Öğleden sonra',
           'Yarın sabah', 'Bu hafta', 'Sonra', 'Cumartesi', 'Pazartesi', 'Saat üçte', 'Okuldan sonra', 'İşten sonra', 'Yarın akşam',
           'Biraz sonra', 'Bir saat sonra', 'Yakında', 'Bu yaz', 'Tatilde', '', '', '', '']
TAILS = [', tamam mı?', ', değil mi?', ', merak etme.', ', söz.', ', inşallah.', ' herhalde.', ' galiba.', ' sanırım.', ' kesinlikle.', ' mutlaka.']
HAND = """Merhaba, nasılsın?
Selam, ne yapıyorsun?
Bir şey değil.
Çok teşekkür ederim.
Teşekkürler, sağ ol.
Tamam, görüşürüz.
Bugün hiçbir şey yapmadım.
Her şey yolunda mı?
Burada ne yapıyorsun?
Orada kimse yok.
Nerede kaldın?
Ne oldu, iyi misin?
Ne olur gel.
Bilmiyorum, sonra bakarız.
Yalnız kalmak istemiyorum.
Yanlış anladın beni.
Herkes buraya gelsin.
Çünkü çok yorgunum.
Şu anda meşgulüm, sonra ararım.
Kesinlikle haklısın.
Maalesef gelemeyeceğim.
Bugün hava çok güzel.
Yarın hava yağmurlu olacak.
Ne yapacağım bilmiyorum.
Ne yapacağız şimdi?
Sen ne yapıyorsun?
Ne yapıyorsunuz orada?
Biraz sonra oradayım.
Bir şeyler yiyelim mi?
Bir şey söyleyeceğim.
Bir şey sorabilir miyim?
Hiçbir şey anlamadım.
Her şey için teşekkürler.
Sürpriz yapacağım sana.
Bu orijinal bir fikir.
Ben de geliyorum.
Sen de gel.
Bence de öyle.
Evde misin?
İyi misin, bir şey mi oldu?
Yemek yedin mi?
Okula gideceğim.
İşe gidiyorum.
Eve dönüyorum.
Seni özledim.
Seni seviyorum.
Geç kalacağım, beni bekleme.
Yolda kaldım, biraz geç geleceğim.
Otobüsü kaçırdım.
Telefonum kapalıydı, kusura bakma.
Sana bir şey anlatacağım.
Sana bir haberim var.
Bugün çok yoruldum.
Hemen geliyorum.
Şimdi çıkıyorum evden.
Beş dakikaya oradayım.
Kapıdayım, aç.
Anahtarı nereye koydun?
Cüzdanımı bulamıyorum.
Benim de canım sıkıldı.
Sen de mi gelmiyorsun?
Yarın sınavım var.
Ders çalışmam lazım.
Ödevimi bitiremedim.
Öğretmen bugün gelmedi.
Hafta sonu ne yapalım?
Sinemaya gidelim mi?
Ne izleyelim?
Pizza mı yiyelim, makarna mı?
Çay ister misin?
Kahve içelim mi?
Bugün market kapalı.
Ekmek almayı unutma.
Süt bitmiş.
Yemek hazır, gel.
Annem seni çağırıyor.
Babam arabayı aldı.
Kardeşim hasta oldu.
Doktora gideceğiz.
İlaçlarını aldın mı?
Geçmiş olsun.
İyi ki varsın.
Doğum günün kutlu olsun.
İyi geceler, yarın görüşürüz.
Günaydın, iyi uyudun mu?
Hayırlı olsun.
Kolay gelsin.
Afiyet olsun.
Haklısın, özür dilerim.
Kusura bakma, unutmuşum.
Sorun değil, olur böyle şeyler.
Bir daha olmaz.
Sana güveniyorum.
Bana güven.
Beni yalnız bırakma.
Gelmeyeceğim, hasta oldum.
Bugün gelemiyorum.
Yarın gelebilirim.
Belki akşam uğrarım.
Sanırım kaybolduk.
Galiba yanlış yoldayız.
Herhalde unutmuştur.
Neredesin, seni bekliyoruz.
Ne zaman geliyorsun?
Saat kaçta buluşuyoruz?
Kaçta çıkacaksın?
Hangi otobüse bineceğiz?
Nasıl gideceğiz oraya?
Kim geliyor?
Kimse yok mu?
Kapıyı kapatır mısın?
Sesi biraz açar mısın?
Bana yardım eder misin?
Şunu tutar mısın?
Bir dakika bekler misin?
Beni arar mısın?
Onu bana verir misin?
Gelir misin buraya?
Bunu yapar mısın?
Yarın gelecek misin?
Bize katılacak mısın?
Yemek yiyecek misin?
Çalışıyor musun?
Beni duyuyor musun?
Anlıyor musun?
Uyuyor musun?
Geliyor musun?
Gidiyor musunuz?
Bakıyorum, birazdan söylerim.
Şimdi yazıyorum sana.
Her gün spor yapıyorum.
Yeni bir işe başlıyorum.
Bu hafta çok çalışıyoruz.
İngilizce öğreniyorum.
Araba kullanmayı öğreniyorum.
Yürüyüşe çıkıyoruz, gelir misin?
Kitap okuyorum, sonra ararım.
Dizi izliyoruz, gel.
Film başlıyor.
Maç kaçta başlıyor?
Bu akşam maç var.
Takımımız kazandı.
Berabere kaldılar.
Ne kadar tuttu?
Çok pahalıymış.
Biraz indirim yapar mısınız?
Hesabı alabilir miyim?
Bir çay daha alabilir miyim?
Buraya oturabilir miyiz?
Bir şey lazım mı?
Sana ne lazım?
Bana hiçbir şey lazım değil.
Bu da mı gol değil?
Yani şimdi ne olacak?
Tabii ki gelirim.
Tabii ki hayır.
Ağabeyim de gelecek.
Ne haber, nasıl gidiyor?
İyiyim, sen nasılsın?
Fena değil, idare eder.
Çok iyi, sağ ol.
Şöyle böyle.
İşler yoğun, biraz yorgunum.
Hafta sonu dinleneceğim.
Tatile çıkıyoruz.
Yarın erkenden yola çıkacağız.
Uçağımız sabah altıda.
Biletleri aldım.
Otel rezervasyonunu yaptın mı?
Çantanı hazırladın mı?
Pasaportunu unutma.
Şarj aletini de al.
Hava soğuk, mont giy.
Şemsiyeni al, yağmur yağacak.
Yağmur yağıyor, ıslanacaksın.
Kar yağmış, yollar kapalı.
Trafik çok yoğun.
Yolda kaza olmuş.
Geç kalacağız galiba.
Beni beklemeyin, sonra gelirim.
Sen git, ben gelirim.
Önden gidin, yetişirim.
Bir saat sonra oradayım.
Tamam, orada görüşürüz.
Peki, öyle olsun.
Olur, sorun değil.
Hayır, istemiyorum.
Evet, geliyorum.
Belki, bilmiyorum.
Yok, gerek yok.
Lütfen acele et.
Hadi gidelim.
Haydi başlayalım.
Durun, bir dakika.
Yavaş ol biraz.
Dikkat et, düşeceksin.
Sakin ol, her şey düzelecek.
Üzülme, hallederiz.
Merak etme, ben buradayım.
Korkma, bir şey olmaz.
Kimseye söyleme.
Bunu aramızda tutalım.
Sana bir sır vereceğim.
Kimse bilmiyor.
Herkes biliyor zaten.
Ben de öyle düşünüyorum.
Bence de haklısın.
Sence ne yapmalıyım?
Ne dersin, gidelim mi?
Bilmem ki, sen karar ver.
Fark etmez, sen seç.
Bana uyar.
Bana göre değil.
Hiç sanmıyorum.
Sanmam, gelmez o.
Eminim gelecek.
Kesin gelir.
Belki gelmez.
Gelmezse ararız.
Gelirse haber ver.
Bir şey olursa beni ara.
Her şey hazır mı?
Hazırım, gidelim.
Hazır değilim daha.
Bitti mi?
Daha bitmedi.
Az kaldı, bekle.
Neredeyse bitti.
Bitince haber vereceğim.
Bugünlük bu kadar.
Yarın devam ederiz.
İyi çalışmalar.
Görüşmek üzere.
Kendine iyi bak.
Hoşça kal.
Güle güle.
Yine bekleriz.
Tekrar görüşürüz.""".splitlines()


def _last_vowel(stem):
    for c in reversed(stem.lower()):
        if c in VOWELS:
            return c
    return 'a'


def _wide(stem):
    return 'a' if _last_vowel(stem) in 'aıou' else 'e'


def _narrow(stem):
    return NARROW[_last_vowel(stem)]


def future(stem, person):
    """stem + (y)AcAk + person: gideceğim, yapacaksın, okuyacağız, yiyecek."""
    if stem in ('ye', 'de'):
        base, buffer = stem[0] + 'i', 'y'
    elif stem[-1] in VOWELS:
        base, buffer = stem, 'y'
    else:
        base, buffer = SOFT.get(stem, stem), ''
    w = _wide(stem)
    n = NARROW[w]
    tail = {'1s': f'{w}c{w}ğ{n}m', '2s': f'{w}c{w}ks{n}n', '3s': f'{w}c{w}k', '1p': f'{w}c{w}ğ{n}z',
            '2p': f'{w}c{w}ks{n}n{n}z', '3p': f'{w}c{w}kl{w}r'}[person]
    return base + buffer + tail


def future_negative(stem, person):
    w = _wide(stem)
    n = NARROW[w]
    tail = {'1s': f'y{w}c{w}ğ{n}m', '2s': f'y{w}c{w}ks{n}n', '3s': f'y{w}c{w}k', '1p': f'y{w}c{w}ğ{n}z'}[person]
    return stem + 'm' + w + tail


def progressive(stem, person):
    """stem + Iyor + person: gidiyorum, bekliyorsun, okuyoruz, söylüyor, yiyor."""
    if stem in ('ye', 'de'):
        base = stem[0] + 'i'
    elif stem[-1] in VOWELS:
        base = stem[:-1]
        base = base + _narrow(base)
    else:
        base = SOFT.get(stem, stem) + _narrow(stem)
    tail = {'1s': 'yorum', '2s': 'yorsun', '3s': 'yor', '1p': 'yoruz', '2p': 'yorsunuz', '3p': 'yorlar'}[person]
    return base + tail


def progressive_negative(stem, person):
    tail = {'1s': 'yorum', '2s': 'yorsun', '3s': 'yor', '1p': 'yoruz'}[person]
    return stem + 'm' + _narrow(stem) + tail


def question(word, person):
    """Question particle with harmony: gelecek misin, yapar mısın, okuyor musun."""
    n = _narrow(word)
    suffix = {'2s': f'm{n}s{n}n', '2p': f'm{n}s{n}n{n}z', '1p': f'm{n}y{n}z', '3s': f'm{n}'}[person]
    return f'{word} {suffix}'


def _clause(rng, stem, aorist, complements, allow_third=True):
    """One clause without final punctuation, plus a flag for question form."""
    complement = rng.choice(complements)
    adverb = '' if complement in TIME_WORDS else rng.choice(ADVERBS)
    kind = rng.choices(['f1s', 'f1p', 'f2s', 'f3s', 'nf1s', 'p1s', 'p2s', 'p3s', 'p1p', 'np1s', 'qf2s', 'qp2s', 'qa2s', 'qf1p'],
                       weights=[6, 3, 2, 3, 2, 4, 2, 2, 2, 2, 2, 2, 2, 1])[0]
    subject = ''
    if kind[0] == 'n' or kind[0] in 'fp':
        person = kind[-2:]
        verb = {'f': future, 'p': progressive, 'n': None}[kind[0]]
        if kind.startswith('nf'):
            word = future_negative(stem, '1s')
        elif kind.startswith('np'):
            word = progressive_negative(stem, '1s')
        else:
            word = verb(stem, person)
        if person == '3s' and allow_third and rng.random() < .8:
            subject = rng.choice(SUBJECTS_3)
        elif person == '1s' and rng.random() < .2:
            subject = 'Ben'
        elif person == '1p' and rng.random() < .25:
            subject = 'Biz'
        elif person == '2s' and rng.random() < .25:
            subject = 'Sen'
        if adverb and subject and subject not in PROPER:
            subject = subject.translate(str.maketrans({'İ': 'i', 'I': 'ı'})).lower()
        words = [adverb, subject, complement, word]
        return ' '.join(w for w in words if w), False
    person = kind[-2:]
    if kind == 'qf2s':
        word = question(future(stem, '3s'), '2s')
    elif kind == 'qp2s':
        word = question(progressive(stem, '3s'), '2s')
    elif kind == 'qa2s':
        word = question(aorist, '2s')
    else:
        word = question(future(stem, '3s'), '1p')
    words = [adverb, complement, word]
    return ' '.join(w for w in words if w), True


def sentences(count=1500, seed=42):
    """Deterministic list of unique everyday sentences (hand-written first, then templates)."""
    rng = random.Random(seed)
    result = []
    seen = set()

    def add(text):
        text = re.sub(r'\s+', ' ', text).strip()
        text = upper_first(text)
        key = canonical(text)
        if key in seen or not 18 <= len(text.encode('utf-8')) <= 160 or len(text.split()) < 3:
            return
        seen.add(key)
        result.append(text)

    for line in HAND:
        add(line)
    attempts = 0
    while len(result) < count and attempts < count * 40:
        attempts += 1
        stem, aorist, complements = rng.choice(VERBS)
        clause, is_question = _clause(rng, stem, aorist, complements)
        roll = rng.random()
        if is_question:
            text = clause + '?'
        elif roll < .18:
            other = rng.choice(VERBS)
            second, second_question = _clause(rng, other[0], other[1], other[2], allow_third=False)
            joiner = rng.choice([' ama ', ', sonra ', ' çünkü ', ', ', ' ve '])
            if second_question:
                continue
            first_char = second[0]
            second = first_char.translate(str.maketrans({'İ': 'i', 'I': 'ı'})).lower() + second[1:]
            text = clause + joiner + second + '.'
        elif roll < .32:
            text = clause + rng.choice(TAILS)
        else:
            text = clause + '.'
        add(text)
    return result


if __name__ == '__main__':
    rows = sentences()
    print(len(rows))
    for row in rows[:20] + rows[-40:]:
        print(row)
