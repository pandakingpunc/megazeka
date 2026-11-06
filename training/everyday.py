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
SOFT = {'git': 'gid', 'et': 'ed', 'tat': 'tad', 'güt': 'güd', 'kaybet': 'kaybed', 'affet': 'affed', 'hisset': 'hissed',
        'seyret': 'seyred', 'reddet': 'redded', 'bahset': 'bahsed'}
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


def _clause(rng, stem, aorist, complements, allow_third=True, kinds=None, weights=None):
    """One clause without final punctuation, plus a flag for question form."""
    complement = rng.choice(complements)
    adverb = '' if complement in TIME_WORDS else rng.choice(ADVERBS)
    kind = rng.choices(kinds or ['f1s', 'f1p', 'f2s', 'f3s', 'nf1s', 'p1s', 'p2s', 'p3s', 'p1p', 'np1s', 'qf2s', 'qp2s', 'qa2s', 'qf1p'],
                       weights=weights or [6, 3, 2, 3, 2, 4, 2, 2, 2, 2, 2, 2, 2, 1])[0]
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


# ---------------------------------------------------------------------------------------------
# v3 additions: softening verbs, ne-contractions, commonly misspelled words, proper-name suffixes.
# ---------------------------------------------------------------------------------------------
SOFT_VERBS = [
    ('git', 'gider', ['okula', 'işe', 'markete', 'eve', 'sinemaya', 'doktora', 'kursa', 'tatile', 'parka', 'kütüphaneye',
                      'alışverişe', 'spora', 'sizinle', 'oraya', 'birlikte', 'denize', 'köye', 'pazara', 'maça', 'konsere']),
    ('et', 'eder', ['sana yardım', 'size yardım', 'bana yardım', 'ona yardım', 'bunu kabul', 'teklifi kabul', 'sana teşekkür',
                    'herkese teşekkür', 'dikkat', 'seni ziyaret', 'evi tamir', 'arabayı tamir', 'sana telefon', 'ona telefon',
                    'seni davet', 'toplantıyı iptal', 'işe devam', 'derse devam', 'bunu tercih', 'şikâyet', 'seni takip', 'ona hitap']),
    ('tat', 'tadar', ['yemeği', 'çorbayı', 'bu tatlıyı', 'bir lokma', 'şu peyniri', 'her çeşidi', 'bu reçeli']),
    ('kaybet', 'kaybeder', ['maçı', 'bu fırsatı', 'sabrımı', 'umudu', 'anahtarı', 'işimi', 'bu davayı']),
    ('affet', 'affeder', ['seni', 'onu', 'beni', 'herkesi', 'bunu']),
    ('hisset', 'hisseder', ['bunu', 'farkı', 'seni', 'soğuğu', 'yalnızlığı']),
    ('seyret', 'seyreder', ['filmi', 'maçı', 'diziyi', 'manzarayı', 'bu programı']),
    ('reddet', 'reddeder', ['teklifi', 'bunu', 'daveti', 'önerini']),
    ('bahset', 'bahseder', ['ona', 'sana bundan', 'toplantıda', 'hocaya', 'bundan']),
]
SOFT_KINDS = ['f1s', 'f1p', 'f2s', 'f2p', 'f3s', 'qf2s', 'qf1p']
SOFT_WEIGHTS = [6, 5, 3, 2, 1, 3, 2]

NE_GREETING = ['', '', '', 'Abi, ', 'Selam, ', 'Hey, ', 'Anne, ', 'Baba, ', 'Arkadaşlar, ', 'Hocam, ', 'Kardeşim, ', 'Ayşe, ',
               'Ali, ', 'Işık, ', 'Irmak, ', 'Yahu, ', 'Şimdi, ', 'Peki, ']
NE_NOW = [('ne yapıyorsun', ['', 'sen ']), ('ne yapıyorsunuz', ['', 'siz ']), ('ne yapıyoruz', ['', 'biz ']),
          ('ne yapıyorum', ['', 'ben ']), ('ne yapıyorlar', ['', 'onlar '])]
NE_FUTURE = [('ne yapacağım', ['', 'ben ']), ('ne yapacağız', ['', 'biz ']), ('ne yapacaksın', ['', 'sen ']),
             ('ne yapacaksınız', ['', 'siz '])]
NE_TIME = ['şimdi', 'bugün', 'bu akşam', 'hafta sonu', 'tatilde', 'yarın', 'yarın akşam', 'bu hafta', 'bu yaz', 'sonra']
NE_PLACE = ['orada', 'burada', 'evde', 'okulda', 'dışarıda', 'bu saatte', 'böyle']
NE_OPT = ['ne yapayım', 'ne yapalım', 'ne yapsam', 'ne yapmalıyım', 'ne yapmalıyız']
NE_PAST = [('ne yaptın', 'sen '), ('ne yaptınız', 'siz '), ('ne yaptık', 'biz '), ('ne yaptım', 'ben ')]
NE_PAST_TIME = ['dün', 'dün akşam', 'bugün', 'hafta sonu', 'tatilde', 'okulda', 'sınavdan sonra', 'geçen hafta', 'bu sabah']
NE_THIRD = ['Ali', 'Ayşe', 'Annem', 'Babam', 'Işık', 'Irmak', 'Kardeşim', 'Öğretmen', 'Mehmet']
NE_HAND = """Sana ne oldu böyle?
Orada ne oldu?
Bugün okulda ne oldu?
Dün akşam ne oldu?
Sınavda ne oldu?
Maçta ne oldu?
Toplantıda ne oldu?
Ne oldu, neden üzgünsün?
Ne oldu, bir sorun mu var?
Ne oldu, geç mi kaldın?
Ne oldu, kızdın mı?
Ne oldu, anlatsana bana.
Ne oldu da bu hale geldi?
Ne olur, bir kere daha dene.
Ne olur, bana yardım et.
Ne olur, bugün gitme.
Ne olur, bana söyle.
Ne olur, bu sefer sen gel.
Ne olur kızma bana.
Ne olur, beni bekle.
Ne olur, bir şey söyle.
Burada ne oluyor?
Orada ne oluyor?
Dışarıda ne oluyor?
Evde ne oluyor?
Bu ne oluyor böyle?
Ne oluyor, kim bağırıyor?
Ne oluyor, neden herkes burada?
Ne olacak şimdi?
Yarın ne olacak?
Sonuç ne olacak?
Ya yağmur yağarsa ne olacak?
Ne olursa olsun yanındayım.
Ne olursa olsun gelirim.
Ne olursa olsun vazgeçme.
Ne haber, nasılsın?
Ne haber, iyi misin?
Ne haber, neler yapıyorsun?
Ne haber bakalım, işler nasıl?
Ne haber, hâlâ çalışıyor musun?
Ne haber, bugün nasıl geçti?
Ona ne olmuş böyle?
Sana ne olmuş, çok değişmişsin.
Ne olsun, hiçbir şey olmadı.
Bu işin sonunda ne olmuş?""".splitlines()

MISSPELL_HAND = """Yalnız başıma sinemaya gitmeyi seviyorum.
Bu akşam evde yalnızım.
Yalnız bir şey söyleyeceğim sana.
Yalnızca sen gelirsen ben de giderim.
Yalnızlık bazen insana iyi gelir.
Yalnız kalınca çok sıkılıyorum.
Yalnız gitmesin diye ben de gideceğim.
Yanlış numarayı aramışsın.
Bu cevap yanlış çıktı.
Yanlışlıkla telefonu yere düşürdüm.
Yanlış anlamayın beni lütfen.
Yanlışlıkla başkasının çantasını aldım.
Yanlış yolda olduğumuzu fark ettim.
Herkes sana teşekkür ediyor.
Herkesin kendine göre bir hikâyesi var.
Herkese iyi akşamlar dilerim.
Herkes aynı fikirde değil.
Bu haberi herkes duymuş zaten.
Herkesle konuşmak zorunda değilsin.
Şoför bizi otelin önüne bıraktı.
Şoförler bugün greve gitmiş.
Babam otobüs şoförü olarak çalışıyor.
Şoföre adresi söyledim.
Taksi şoförü çok kibardı.
Yeni bir eşofman takımı aldım.
Eşofmanımı dolaba koydun mu?
Spor için eşofman giydim.
Bu eşofman çok rahat.
Orijinal fatura yanımda.
Bu çanta orijinal mi?
Orijinal belgeleri getirmeyi unutma.
Filmin orijinal adı farklıymış.
Orijinal ses dosyasını sana gönderdim.
Annem için sürpriz bir parti hazırlıyoruz.
Sürpriz yapmayı çok severim.
Bu hediye büyük bir sürpriz oldu.
Sürpriz misafirler geldi.
Laboratuvar sonuçları yarın çıkacak.
Ablam laboratuvarda çalışıyor.
Laboratuvara girerken eldiven giy.
Arabanın egzozu ses yapıyor.
Egzoz dumanı çok kötü kokuyor.
Egzoz borusunu tamirciye gösterdim.
Çok entelektüel bir sohbetti.
Entelektüel insanlarla konuşmayı severim.
Kullanım kılavuzunu okudun mu?
Kılavuz bize şehri gezdirdi.
Kılavuzu çekmeceye koydum.
Her gün meyve yemeye çalışıyorum.
Pazardan meyve ve sebze aldım.
Bu meyve çok tatlı.
Meyve suyu içmek ister misin?
Çamaşır makinesi bozulmuş.
Bulaşık makinesini çalıştırdın mı?
Bu makine çok gürültülü çalışıyor.
Kahve makinesi nerede?
Mütevazı bir ev satın aldık.
Çok mütevazı biri, hiç övünmez.
Mütevazı bir kutlama yaptık.
Hastanede saatlerce bekledik.
Dedemi hastaneye götürdüm.
Hastane çok kalabalıktı.
Yarın hastaneye gitmem lazım.
Bu pantolon bana büyük geldi.
Yeni bir pantolon almak istiyorum.
Pantolonumu ütüler misin?
Sıcak çikolata içelim mi?
Çikolatalı kek yaptım.
Bana biraz çikolata getir.
Çay ya da kahve alabilir miyim?
Bugün ya da yarın gelirim.
Ya da bunu sonra konuşalım.
Her zaman yanındayım.
Seni her zaman severim.
Her zaman bu kadar geç mi kalkarsın?
Her gün yürüyüşe çıkıyorum.
Her gün aynı yoldan gidiyorum.
Her gün biraz İngilizce çalışıyorum.
Hiçbir zaman pes etmem.
Seni hiçbir zaman unutmayacağım.
Bir daha böyle yapma.
Bir daha sana güvenmem.
Bir daha ne zaman görüşürüz?
O kadar çok yoruldum ki.
Hava o kadar soğuk değil.
Bu kadar acele etme.
Bu kadar güzel olacağını düşünmemiştim.
Yorgundum ama yine de gittim.
Yağmur yağıyor, yine de çıkacağız.
Hastayım, bu yüzden gelemedim.
Çok yorgunum, bu yüzden erken yatacağım.
O zaman yarın görüşürüz.
O zaman ben giderim.
Pek çok arkadaşım orada olacak.
Bu konuda pek çok kitap okudum.
Hoş geldin, nasılsın bakalım?
Eve hoş geldin canım.
Hoş geldiniz, buyurun oturun.
Hoşça kal, yine görüşürüz.
Hoşça kalın, iyi günler dilerim.
İyi ki doğdun, çok mutluyuz.
İyi ki geldin, çok özlemiştim.
İyi ki bana söyledin.
Tabii ki yardım ederim.
Tabii ki bunu bilmiyordum.
Birtakım sorunlar yaşadık.
Birtakım insanlar buna inanıyor.""".splitlines()

PLACES = ['Ankara', 'İstanbul', 'İzmir', 'Bursa', 'Antalya', 'Adana', 'Konya', 'Eskişehir', 'Kayseri', 'Trabzon', 'Samsun',
          'Mersin', 'Gaziantep', 'Diyarbakır', 'Erzurum', 'Isparta', 'Iğdır', 'Edirne', 'Malatya', 'Denizli', 'Sakarya',
          'Muğla', 'Çanakkale', 'Van', 'Sivas', 'Rize', 'Hatay', 'Aydın', 'Türkiye', 'Almanya', 'Irak', 'İngiltere']
PEOPLE = ['Ali', 'Ayşe', 'Mehmet', 'Zeynep', 'Fatma', 'Ahmet', 'Mustafa', 'Elif', 'Emre', 'Işık', 'Irmak', 'Ilgaz', 'Ilgın',
          'Işıl', 'Işın', 'İpek', 'İlker', 'İlkay', 'İrem', 'İsmail', 'İbrahim', 'İnci', 'İlhan', 'İdil', 'Selin', 'Can',
          'Deniz', 'Burak', 'Merve', 'Cem', 'Eren', 'Ece', 'Kerem']
I_PEOPLE = ['Işık', 'Irmak', 'Ilgaz', 'Ilgın', 'Işıl', 'Işın', 'İpek', 'İlker', 'İlkay', 'İrem', 'İsmail', 'İbrahim', 'İnci']
I_PLACES = ['Isparta', 'Iğdır', 'Irak', 'İzmir', 'İstanbul', 'İngiltere']
PLACE_T = ["Yarın {dat} gidiyoruz.", "Bu hafta sonu {dat} gideceğiz.", "{abl} yeni döndüm.", "{abl} uçakla geldik.",
           "{loc} hava bugün çok güzel.", "{loc} yağmur yağıyor mu?", "{gen} havası çok güzelmiş.",
           "{gen} yemekleri çok meşhur.", "Tatilde {dat} gitmek istiyorum.", "Sonra {dat} döneceğim.",
           "Ben {abl} geliyorum, sen nerelisin?", "Kardeşim {loc} okuyor.", "Akşam {dat} yetişirim.",
           "Beni {dat} götürür müsün?", "{loc} kaç gün kalacaksınız?", "Bilet {dat} değil, başka şehre aldım.",
           "Annemler {abl} geliyor.", "{loc} bir arkadaşım yaşıyor.", "Eskiden {loc} otururduk.",
           "Haftaya {dat} taşınıyoruz."]
PERSON_T = ["{gen} kitabı masada kalmış.", "{gen} telefonu çalıyor.", "{dat} telefon edeceğim.", "Bunu {dat} sen söyle.",
            "{abl} haber bekliyorum.", "{with} sinemaya gittik.", "{with} yarın buluşacağız.", "{nom} şimdi evde değil.",
            "Bu hediyeyi {dat} alacağım.", "{gen} yanına gidiyorum.", "{gen} doğum günü yarın.",
            "{nom} bana akşam mesaj attı.", "{nom} ile {nom2} aynı takımda.", "{nom} yarın {pdat} gelecek.",
            "{nom} {pdat} taşınmış.", "{abl} bir şey sordum.", "{with} birlikte çalışıyoruz.",
            "{gen} annesi bizi çağırdı.", "{nom} bugün okula gelmedi mi?", "{dat} bir şey söylemem lazım."]
PERSON_FIRST = ["{nom} geldi mi?", "{nom} nerede kaldı?", "{nom} ile konuştun mu?"]
_TR_LOWER = str.maketrans({'I': 'ı', 'İ': 'i'})


def suffix(name, case):
    """Proper-noun case suffix with apostrophe: Ankara'ya, Işık'ın, Ahmet'ten, Ayşe'yle."""
    lowered = name.translate(_TR_LOWER).lower()
    last = next((c for c in reversed(lowered) if c in VOWELS), 'a')
    ends_vowel = lowered[-1] in VOWELS
    voiceless = lowered[-1] in 'çfhkpsşt'
    w = 'a' if last in 'aıou' else 'e'
    n = NARROW[last]
    ending = {'dat': ('y' if ends_vowel else '') + w, 'abl': ('t' if voiceless else 'd') + w + 'n',
              'loc': ('t' if voiceless else 'd') + w, 'gen': ('n' if ends_vowel else '') + n + 'n',
              'with': ('y' if ends_vowel else '') + 'l' + w}[case]
    return f"{name}'{ending}"


def _fill(template, rng, subject_is_person, place=None, person=None):
    place = place or rng.choice(PLACES)
    person = person or rng.choice(PEOPLE)
    owner = person if subject_is_person else place
    forms = {case: suffix(owner, case) for case in ('dat', 'abl', 'loc', 'gen', 'with')}
    forms.update({'nom': person, 'nom2': rng.choice(PEOPLE), 'pdat': suffix(rng.choice(PLACES), 'dat')})
    return template.format(**forms)


def _name_sentences(rng, count):
    result = []
    for _ in range(count):
        roll = rng.random()
        if roll < .4:
            place = rng.choice(I_PLACES) if rng.random() < .3 else None
            result.append(_fill(rng.choice(PLACE_T), rng, False, place=place))
        elif roll < .55:
            result.append(_fill(rng.choice(PERSON_FIRST), rng, True, person=rng.choice(I_PEOPLE)))
        else:
            person = rng.choice(I_PEOPLE) if rng.random() < .5 else None
            result.append(_fill(rng.choice(PERSON_T), rng, True, person=person))
    return result


def _ne_sentences(rng, count):
    result = list(NE_HAND)
    for _ in range(count):
        greeting = rng.choice(NE_GREETING)
        roll = rng.random()
        if roll < .30:
            phrase, subjects = rng.choice(NE_NOW)
            body = rng.choice([f'{rng.choice(subjects)}{phrase} {rng.choice(NE_TIME + NE_PLACE)}',
                               f'{rng.choice(NE_TIME)} {rng.choice(subjects)}{phrase}',
                               f'{rng.choice(subjects)}{phrase}'])
        elif roll < .58:
            phrase, subjects = rng.choice(NE_FUTURE)
            body = rng.choice([f'{rng.choice(subjects)}{phrase} {rng.choice(NE_TIME)}',
                               f'{rng.choice(NE_TIME)} {rng.choice(subjects)}{phrase}',
                               f'{rng.choice(subjects)}{phrase} sence'])
        elif roll < .78:
            verb = rng.choice(NE_OPT)
            body = rng.choice([f'{verb} şimdi', f'şimdi {verb}', f'sence {verb}', f'bu durumda {verb}', f'{verb} böyle'])
        elif roll < .90:
            phrase, subject = rng.choice(NE_PAST)
            body = rng.choice([f'{rng.choice(NE_PAST_TIME)} {subject}{phrase}', f'{subject}{phrase} {rng.choice(NE_PAST_TIME)}'])
        else:
            subject = rng.choice(NE_THIRD)
            greeting = ''
            body = rng.choice([f'{subject} ne yapıyor', f'{subject} bugün ne yapıyor', f'{subject} ne yapacak',
                               f'{subject} yarın ne yapacak', f'{subject} ne yaptı', f'{subject} sana ne dedi'])
        result.append(upper_first(greeting + body) + '?')
    return result


def _soft_sentences(rng, count):
    result = []
    verbs = {v[0]: v for v in SOFT_VERBS}
    names = [v[0] for v in SOFT_VERBS]
    weights = [8, 8, 2, 2, 1, 1, 1, 1, 1]
    for _ in range(count):
        stem, aorist, complements = verbs[rng.choices(names, weights=weights)[0]]
        clause, is_question = _clause(rng, stem, aorist, complements, kinds=SOFT_KINDS, weights=SOFT_WEIGHTS)
        if is_question:
            result.append(clause + '?')
        elif rng.random() < .3:
            result.append(clause + rng.choice(TAILS))
        else:
            result.append(clause + '.')
    return result


TOP_ACTS = ['eve gidiyorum', 'yemek yiyorum', 'sinemaya gittim', 'yürüyüşe çıktım', 'okula gideceğim', 'çalışıyorum',
            'kahve içiyorum', 'tatile çıkıyorum', 'markete gittim', 'kitap okuyorum', 'film izledim', 'eve döndüm']
TOP_WHEN = ['Bugün', 'Bu akşam', 'Dün', 'Hafta sonu', 'Sabah', 'Tatilde', 'Şimdi', 'Bu hafta']
TOP_WRONG = ['otobüse bindim', 'kapıyı çaldım', 'numarayı aradım', 'yöne gittim', 'adrese geldik', 'sınıfa girdim',
             'şifreyi yazdım', 'peçeteyi aldım', 'yolu seçtik', 'cevabı verdim', 'kutuyu açtı', 'telefonu açtım']
TOP_ALL = ['burada', 'hazır', 'evde', 'çok yorgun', 'sana teşekkür ediyor', 'seni bekliyor', 'orada', 'bu akşam gelecek',
           'bizimle gelecek', 'bunu biliyor', 'toplantıda', 'bugün çok mutlu']


def _top_misspelling_sentences(rng):
    """Frames for the most frequent real-world mistakes (yalnız, yanlış, herkes) so they recur often."""
    result = []
    for _ in range(40):
        act = rng.choice(TOP_ACTS)
        result.append(rng.choice([f'Yalnız {act}.', f'{rng.choice(TOP_WHEN)} yalnız {act}.',
                                  f'{rng.choice(TOP_WHEN)} yalnız başıma {act}.']))
    for _ in range(26):
        result.append(rng.choice([f'Yanlış {rng.choice(TOP_WRONG)}.', f'Dün yanlış {rng.choice(TOP_WRONG)}.',
                                  f'Yanlışlıkla {rng.choice(TOP_WRONG)}.']))
    for _ in range(36):
        who = rng.choice(['Herkes', 'Herkes', 'Bugün herkes', 'Şimdi herkes', 'Sanırım herkes'])
        result.append(f'{who} {rng.choice(TOP_ALL)}.')
    return result


def _misspelling_sentences(rng):
    result = list(MISSPELL_HAND) + _top_misspelling_sentences(rng)
    for line in list(result):
        if line.endswith('.') and rng.random() < .7:
            result.append(line[:-1] + rng.choice(TAILS))
    return result


def extra_sentences(seed=2024):
    """Targeted v3 families, drawn with their own seed so the v2 sentence stream is unchanged."""
    rng = random.Random(seed)
    return (_soft_sentences(rng, 250) + _ne_sentences(rng, 230) + _misspelling_sentences(rng)
            + _name_sentences(rng, 320))


def sentences(count=1500, seed=42, extra=True):
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
    if extra:
        for text in extra_sentences():
            add(text)
    return result


if __name__ == '__main__':
    rows = sentences()
    print(len(rows))
    for row in rows[:20] + rows[-40:]:
        print(row)
