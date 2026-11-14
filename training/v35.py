"""Megazeka v3.5 için elle yazılmış, deterministik yazım düzeltme çiftleri.

Aileler genişletilmeden önce eğitim ve doğrulama kümelerine ayrılır. Bütün
çekim biçimleri açıkça yazılmıştır; rastgele kök-ek birleştirme yapılmaz.
"""
from dataclasses import dataclass
import hashlib
from collections import Counter, defaultdict
import itertools
import random
import re
import string

from megazeka.text import canonical, lower_tr

SOURCE = 'Megazeka v3.5 hedefli / CC0-1.0'
PEOPLE = ('Ayşe', 'Mehmet', 'Elif', 'Emre', 'Zeynep', 'Burak',
          'Ece', 'Mert', 'Selin', 'Onur', 'Derya', 'Barış')


@dataclass(frozen=True)
class Pair:
    target: str
    input: str


@dataclass(frozen=True)
class Family:
    name: str
    kind: str
    focus: str
    pairs: tuple[Pair, ...]


def _catalog(name, kind, focus, text):
    pairs = []
    for line in text.strip().splitlines():
        target, wrong = line.strip().split('|')
        pairs.append(Pair(target, wrong))
    return Family(name, kind, focus, tuple(pairs))


def _identity(name, focus, text):
    return Family(name, 'koruma', focus,
                  tuple(Pair(line.strip(), line.strip())
                        for line in text.strip().splitlines()))


def _forms(name, kind, focus, forms, frames):
    """Açıkça çekimlenmiş (doğru, yanlış) biçimleri bağlamlara yerleştir."""
    pairs = []
    for correct, wrong in forms:
        for frame in frames.strip().splitlines():
            pairs.append(Pair(frame.strip().replace('{x}', correct),
                              frame.strip().replace('{x}', wrong)))
    return Family(name, kind, focus, tuple(pairs))


def _protected_forms(name, focus, words, frames):
    return _forms(name, 'koruma', focus,
                  tuple((word, word) for word in words), frames)


def _spelling_families():
    data = (
        ('kilavuz', 'kılavuz', '''
Kılavuzu baştan okudum.|Klavuzu baştan okudum.
Bu kılavuz oldukça açıklayıcı.|Bu klavuz oldukça açıklayıcı.
{p} kılavuzdaki çizimi inceledi.|{p} klavuzdaki çizimi inceledi.
Cihazı kılavuz yardımıyla kuracağız.|Cihazı klavuz yardımıyla kuracağız.
{p} kullanım kılavuzunu rafa kaldırdı.|{p} kullanım klavuzunu rafa kaldırdı.
Aradığım açıklama kılavuzda yok.|Aradığım açıklama klavuzda yok.
'''),
        ('tiras', 'tıraş', '''
Tıraş bıçağını değiştirdim.|Traş bıçağını değiştirdim.
{p} tıraş olmak için berbere gitti.|{p} traş olmak için berbere gitti.
Bu tıraş makinesi çok sessiz.|Bu traş makinesi çok sessiz.
Tıraştan sonra yüzümü yıkadım.|Traştan sonra yüzümü yıkadım.
{p} temiz bir tıraş havlusu getirdi.|{p} temiz bir traş havlusu getirdi.
Kardeşimin tıraşı çok kısa olmuş.|Kardeşimin traşı çok kısa olmuş.
'''),
        ('sarimsak', 'sarımsak', '''
Çorbaya bir diş sarımsak ekledim.|Çorbaya bir diş sarmısak ekledim.
{p} sarımsakları ince ince doğradı.|{p} sarmısakları ince ince doğradı.
Bu sarımsak oldukça taze.|Bu sarmısak oldukça taze.
Sarımsaklı yoğurdu karıştırır mısın?|Sarmısaklı yoğurdu karıştırır mısın?
{p} bahçeye sarımsak ekecek.|{p} bahçeye sarmısak ekecek.
Sarımsak kabuklarını masada bırakma.|Sarmısak kabuklarını masada bırakma.
'''),
        ('kibrit', 'kibrit', '''
Kibrit kutusu çekmecede kalmış.|Kiprit kutusu çekmecede kalmış.
{p} kamp için kibrit aldı.|{p} kamp için kirbit aldı.
Son kibriti de rüzgâr söndürdü.|Son kirbiti de rüzgâr söndürdü.
Kibritle oynamak tehlikelidir.|Kipritle oynamak tehlikelidir.
{p} kibritleri kuru bir yere koydu.|{p} kipritleri kuru bir yere koydu.
Sobayı yakmak için kibritin var mı?|Sobayı yakmak için kirbitin var mı?
'''),
        ('yalniz', 'yalnız', '''
Bugün evde yalnız kaldım.|Bugün evde yanlız kaldım.
{p} yalnız yürümeyi seviyor.|{p} yanlız yürümeyi seviyor.
Bu yolda yalnız değiliz.|Bu yolda yanlız değiliz.
Yalnız bir yolcu bankta oturuyor.|Yanlız bir yolcu bankta oturuyor.
{p} yalnızlığı bazen özlüyor.|{p} yanlızlığı bazen özlüyor.
Köpeği evde yalnız bırakmayalım.|Köpeği evde yanlız bırakmayalım.
'''),
        ('yanlis', 'yanlış', '''
Yanlış numarayı aramışım.|Yalnış numarayı aramışım.
{p} yanlışını hemen kabul etti.|{p} yalnışını hemen kabul etti.
Bu hesap bence yanlış.|Bu hesap bence yalnış.
Yanlış dosyayı silmediğinden emin misin?|Yalnış dosyayı silmediğinden emin misin?
{p} yanlış anlaşılmak istemiyor.|{p} yalnış anlaşılmak istemiyor.
Adres yanlışsa bana haber ver.|Adres yalnışsa bana haber ver.
'''),
        ('herkes', 'herkes', '''
Herkes aynı şeyi düşünmek zorunda değil.|Herkez aynı şeyi düşünmek zorunda değil.
{p} herkesi toplantıya çağırdı.|{p} herkezi toplantıya çağırdı.
Herkese birer bardak verdim.|Herkeze birer bardak verdim.
Bu bahçe herkese açık.|Bu bahçe herkeze açık.
{p} herkesin fikrini dikkatle dinledi.|{p} herkezin fikrini dikkatle dinledi.
Herkesten önce sen gelmişsin.|Herkezden önce sen gelmişsin.
'''),
        ('sofor', 'şoför', '''
Şoför yolu çok iyi biliyor.|Şöför yolu çok iyi biliyor.
{p} şoföre yeni adresi verdi.|{p} şöföre yeni adresi verdi.
Otobüsü şoför garaja çekti.|Otobüsü şöför garaja çekti.
Yeni şoför dikkatle kullanıyor.|Yeni şöför dikkatle kullanıyor.
{p} şoförün yanına oturdu.|{p} şöförün yanına oturdu.
Valizleri şoföre teslim edebilirsin.|Valizleri şöföre teslim edebilirsin.
'''),
        ('esofman', 'eşofman', '''
Bu eşofman bana çok rahat geldi.|Bu eşortman bana çok rahat geldi.
{p} spor için eşofman aldı.|{p} spor için eşortman aldı.
Eşofmanın paçasını kısalttım.|Eşortmanın paçasını kısalttım.
Temiz eşofman bulamadın mı?|Temiz eşortman bulamadın mı?
{p} eşofmanlarını balkona astı.|{p} eşortmanlarını balkona astı.
Pamuklu eşofman giymeyi seviyorum.|Pamuklu eşortman giymeyi seviyorum.
'''),
        ('orijinal', 'orijinal', '''
Bu tablo gerçekten orijinal mi?|Bu tablo gerçekten orjinal mi?
{p} orijinal belgeyi arşive verdi.|{p} orjinal belgeyi arşive verdi.
Orijinal kutusunu atmayın.|Orjinal kutusunu atmayın.
Çizimin orijinali bende kaldı.|Çizimin orjinali bende kaldı.
{p} orijinal bir fikir sundu.|{p} orjinal bir fikir sundu.
Orijinal kaydı henüz dinlemedim.|Orjinal kaydı henüz dinlemedim.
'''),
        ('surpriz', 'sürpriz', '''
Sana küçük bir sürpriz hazırladım.|Sana küçük bir süpriz hazırladım.
{p} sürprizden habersiz geldi.|{p} süprizden habersiz geldi.
Sürpriz konuğa yer açalım.|Süpriz konuğa yer açalım.
Bu kutu kardeşime sürpriz.|Bu kutu kardeşime süpriz.
{p} sürpriz pastayı buzdolabına sakladı.|{p} süpriz pastayı buzdolabına sakladı.
Beklenmedik sürprizler beni sevindirir.|Beklenmedik süprizler beni sevindirir.
'''),
        ('laboratuvar', 'laboratuvar', '''
Laboratuvarın kapısı açık kalmış.|Labaratuvarın kapısı açık kalmış.
{p} numuneyi laboratuvara götürdü.|{p} numuneyi labaratuvara götürdü.
Laboratuvar sonuçlarını bekliyoruz.|Labaratuvar sonuçlarını bekliyoruz.
Deney bitince laboratuvarı havalandırdım.|Deney bitince labaratuvarı havalandırdım.
{p} laboratuvarda yeni bir deney yapıyor.|{p} labaratuvarda yeni bir deney yapıyor.
Laboratuvara izinsiz girmeyin.|Labaratuvara izinsiz girmeyin.
'''),
        ('egzoz', 'egzoz', '''
Egzoz borusunda delik varmış.|Eksoz borusunda delik varmış.
{p} egzozu ustayla kontrol etti.|{p} eksozu ustayla kontrol etti.
Egzozdan tuhaf bir ses geliyor.|Eksozdan tuhaf bir ses geliyor.
Bu egzoz çok gürültülü çalışıyor.|Bu eksoz çok gürültülü çalışıyor.
{p} egzoz muayenesinden geçti.|{p} eksoz muayenesinden geçti.
Egzoz sistemini yarın değiştirecekler.|Eksoz sistemini yarın değiştirecekler.
'''),
        ('pantolon', 'pantolon', '''
Bu pantolon bana biraz bol.|Bu pantalon bana biraz bol.
{p} pantolonunun paçasını kısalttı.|{p} pantalonunun paçasını kısalttı.
Pantolonu ters çevirerek yıka.|Pantalonu ters çevirerek yıka.
Mavi pantolonu nereden aldın?|Mavi pantalonu nereden aldın?
{p} pantolon cebinde anahtar buldu.|{p} pantalon cebinde anahtar buldu.
Pantolonlar dolaba sığmadı.|Pantalonlar dolaba sığmadı.
'''),
        ('cikolata', 'çikolata', '''
Bir parça çikolata yedim.|Bir parça çikolota yedim.
{p} pastaya çikolata rendeledi.|{p} pastaya çikolota rendeledi.
Çikolatayı serin yerde sakla.|Çikolotayı serin yerde sakla.
Sütlü çikolata sever misin?|Sütlü çikolota sever misin?
{p} çikolatalı kurabiyeleri paylaştı.|{p} çikolotalı kurabiyeleri paylaştı.
Hava ısınınca çikolatalar eridi.|Hava ısınınca çikolotalar eridi.
'''),
        ('mutevazi', 'mütevazı', '''
Mütevazı bir evde yaşıyorlar.|Mütevazi bir evde yaşıyorlar.
{p} başarısına rağmen mütevazı kaldı.|{p} başarısına rağmen mütevazi kaldı.
Mütevazı bir kutlama yapacağız.|Mütevazi bir kutlama yapacağız.
Bu oda küçük ve mütevazı.|Bu oda küçük ve mütevazi.
{p} mütevazı önerisini anlattı.|{p} mütevazi önerisini anlattı.
Gösterişsiz ve mütevazı giyinmişti.|Gösterişsiz ve mütevazi giyinmişti.
'''),
        ('sarj', 'şarj', '''
Telefonu şarja taktım.|Telefonu şarza taktım.
{p} şarj aletini çantasına koydu.|{p} şarz aletini çantasına koydu.
Şarj kablosunu zorlamayın.|Şarz kablosunu zorlamayın.
Pil şarj olmuyor.|Pil şarz olmuyor.
{p} şarj yüzdesini kontrol etti.|{p} şarz yüzdesini kontrol etti.
Yedek şarj cihazını almayı unutma.|Yedek şarz cihazını almayı unutma.
'''),
        ('kirpik', 'kirpik', '''
Kirpiklerim çok kısa görünüyor.|Kipriklerim çok kısa görünüyor.
{p} kirpiklerine rimel sürdü.|{p} kipriklerine rimel sürdü.
Yanağında bir kirpik var.|Yanağında bir kiprik var.
Kirpik fırçamı temizledim.|Kiprik fırçamı temizledim.
{p} dökülen kirpiği eliyle aldı.|{p} dökülen kipriği eliyle aldı.
Bebeğin kirpikleri ne kadar uzun!|Bebeğin kiprikleri ne kadar uzun!
'''),
        ('ukala', 'ukala', '''
Ukala görünmek istemiyorum.|Ukalla görünmek istemiyorum.
{p} ukala tavırlardan hoşlanmıyor.|{p} ukalla tavırlardan hoşlanmıyor.
Bana ukala cevaplar verme.|Bana ukalla cevaplar verme.
Bu çocuk ukala değil.|Bu çocuk ukalla değil.
{p} ukalalık yaptığını kabul etti.|{p} ukallalık yaptığını kabul etti.
Haklıydı ama ukala konuştu.|Haklıydı ama ukalla konuştu.
'''),
        ('doviz', 'döviz', '''
Döviz hesabımı kontrol ettim.|Dövız hesabımı kontrol ettim.
{p} döviz kurunu ekranda izledi.|{p} dövız kurunu ekranda izledi.
Döviz alırken makbuzu sakla.|Dövız alırken makbuzu sakla.
Bankada döviz işlemi yaptık.|Bankada dövız işlemi yaptık.
{p} döviz bürosunun önünde bekledi.|{p} dövız bürosunun önünde bekledi.
Dövizdeki dalgalanma beni şaşırttı.|Dövızdeki dalgalanma beni şaşırttı.
'''),
        ('pogaca', 'poğaça', '''
Peynirli poğaça yapıyorum.|Peynirli poğaca yapıyorum.
{p} poğaçaları tepsiye dizdi.|{p} poğacaları tepsiye dizdi.
Poğaçanın üstüne yumurta sürdüm.|Poğacanın üstüne yumurta sürdüm.
Fırından poğaça kokusu geliyor.|Fırından poğaca kokusu geliyor.
{p} zeytinli poğaçayı paylaştı.|{p} zeytinli poğacayı paylaştı.
Poğaça hamuru güzelce kabardı.|Poğaca hamuru güzelce kabardı.
'''),
        ('kravat', 'kravat', '''
Kravatımı bağlamakta zorlandım.|Karavatımı bağlamakta zorlandım.
{p} tören için kravat seçti.|{p} tören için karavat seçti.
Kravatın düğümünü gevşet.|Karavatın düğümünü gevşet.
Bu kravat gömleğe uyuyor.|Bu karavat gömleğe uyuyor.
{p} kravatını askıya astı.|{p} karavatını askıya astı.
Kırmızı kravatı nereye koydun?|Kırmızı karavatı nereye koydun?
'''),
        ('tisort', 'tişört', '''
Tişörtümü değiştirmek istiyorum.|Tişortümü değiştirmek istiyorum.
{p} beyaz tişörtü sepete koydu.|{p} beyaz tişortü sepete koydu.
Tişörtü düşük ısıda ütüle.|Tişortü düşük ısıda ütüle.
Bu tişört bana küçük geldi.|Bu tişort bana küçük geldi.
{p} tişörtüne kahve döktü.|{p} tişortüne kahve döktü.
Pamuklu tişörtler askıda kuruyor.|Pamuklu tişortler askıda kuruyor.
'''),
        ('aferin', 'aferin', '''
Aferin sana çok güzel çizmişsin!|Aferim sana çok güzel çizmişsin!
{p} başaran çocuğa aferin dedi.|{p} başaran çocuğa aferim dedi.
Bir aferin duymak beni sevindirdi.|Bir aferim duymak beni sevindirdi.
Öğretmen herkese aferin dedi.|Öğretmen herkese aferim dedi.
{p} aferin diyerek alkışladı.|{p} aferim diyerek alkışladı.
Aferin arkadaşlar birlikte başardınız!|Aferim arkadaşlar birlikte başardınız!
'''),
        ('maydanoz', 'maydanoz', '''
Maydanozları ince doğradım.|Maydonozları ince doğradım.
{p} salataya maydanoz ekledi.|{p} salataya maydonoz ekledi.
Bu maydanoz çok taze.|Bu maydonoz çok taze.
Bir demet maydanoz yeter.|Bir demet maydonoz yeter.
{p} maydanoz saplarını ayıkladı.|{p} maydonoz saplarını ayıkladı.
Bahçedeki maydanozları sulamayı unutma.|Bahçedeki maydonozları sulamayı unutma.
'''),
        ('karnabahar', 'karnabahar', '''
Karnabahar yemeği pişiriyorum.|Karnıbahar yemeği pişiriyorum.
{p} karnabaharı küçük parçalara ayırdı.|{p} karnıbaharı küçük parçalara ayırdı.
Bu karnabahar oldukça iri.|Bu karnıbahar oldukça iri.
Fırında karnabahar yapar mısın?|Fırında karnıbahar yapar mısın?
{p} karnabahar çorbasını beğendi.|{p} karnıbahar çorbasını beğendi.
Karnabaharın yapraklarını atma.|Karnıbaharın yapraklarını atma.
'''),
        ('muhasebe', 'muhasebe', '''
Muhasebe kaydını düzelttim.|Muhasabe kaydını düzelttim.
{p} faturayı muhasebeye götürdü.|{p} faturayı muhasabeye götürdü.
Şirketin muhasebesi düzenli tutuluyor.|Şirketin muhasabesi düzenli tutuluyor.
Muhasebe programını kullanabiliyor musun?|Muhasabe programını kullanabiliyor musun?
{p} muhasebe bürosunda çalışıyor.|{p} muhasabe bürosunda çalışıyor.
Muhasebe belgelerini teslim etmeyi unutma.|Muhasabe belgelerini teslim etmeyi unutma.
'''),
        ('muteahhit', 'müteahhit', '''
Müteahhitle biraz görüştüm.|Müteahitle biraz görüştüm.
{p} müteahhitten yeni teklif aldı.|{p} müteahitten yeni teklif aldı.
Binayı yapan müteahhit burada mı?|Binayı yapan müteahit burada mı?
Bu müteahhit güvenilir biri.|Bu müteahit güvenilir biri.
{p} müteahhitle sözleşmeyi imzaladı.|{p} müteahitle sözleşmeyi imzaladı.
Müteahhit gelince bana haber ver.|Müteahit gelince bana haber ver.
'''),
        ('musaade', 'müsaade', '''
İçeri girmek için müsaade istedim.|İçeri girmek için müsade istedim.
{p} erken çıkmama müsaade etti.|{p} erken çıkmama müsade etti.
Müsaade almadan çıkmayın.|Müsade almadan çıkmayın.
Bu işe müsaade edemem.|Bu işe müsade edemem.
{p} konuşmamız için müsaade istedi.|{p} konuşmamız için müsade istedi.
Bana müsaade kalkmam gerekiyor.|Bana müsade kalkmam gerekiyor.
'''),
        ('iddia', 'iddia', '''
Bu iddiayı araştırıyorum.|Bu iddayı araştırıyorum.
{p} aynı iddiayı bir kez daha duydu.|{p} aynı iddayı bir kez daha duydu.
Ortada ciddi bir iddia var.|Ortada ciddi bir idda var.
İddianı kanıtlayabilir misin?|İddanı kanıtlayabilir misin?
{p} iddiasından vazgeçmedi.|{p} iddasından vazgeçmedi.
İddiaları belgelerle destekleyin.|İddaları belgelerle destekleyin.
'''),
        ('inisiyatif', 'inisiyatif', '''
İnisiyatif almaktan çekinmedim.|Inisyatif almaktan çekinmedim.
{p} gerektiğinde inisiyatif kullandı.|{p} gerektiğinde inisyatif kullandı.
Bu konuda inisiyatif sende.|Bu konuda inisyatif sende.
İnisiyatif kullanmayı öğrenmelisin.|Inisyatif kullanmayı öğrenmelisin.
{p} inisiyatifi ekibe bıraktı.|{p} inisyatifi ekibe bıraktı.
Yönetici çalışanlara inisiyatif tanıyor.|Yönetici çalışanlara inisyatif tanıyor.
'''),
        ('sandvic', 'sandviç', '''
Peynirli sandviç hazırladım.|Peynirli sandoviç hazırladım.
{p} sandviçini çantasına koydu.|{p} sandoviçini çantasına koydu.
Sandviçin içine domates ekledim.|Sandoviçin içine domates ekledim.
Bu sandviç çok büyük.|Bu sandoviç çok büyük.
{p} sandviçleri kâğıda paketledi.|{p} sandoviçleri kâğıda paketledi.
Yol için iki sandviç yeter.|Yol için iki sandoviç yeter.
'''),
        ('restoran', 'restoran', '''
Restoranda masa ayırttım.|Restorantta masa ayırttım.
{p} restoranın menüsünü inceledi.|{p} restorantın menüsünü inceledi.
Bu restoran akşamları kalabalık.|Bu restorant akşamları kalabalık.
Restoranın adresini bana gönder.|Restorantın adresini bana gönder.
{p} restoranda yeni bir işe başladı.|{p} restorantta yeni bir işe başladı.
Restorana yürüyerek gidebiliriz.|Restoranta yürüyerek gidebiliriz.
'''),
    )
    families = []
    for name, focus, text in data:
        family = _catalog(name, 'yazım', focus, text)
        families.extend((
            Family(name + '_a', 'yazım', focus, family.pairs[::2]),
            Family(name + '_b', 'yazım', focus, family.pairs[1::2]),
        ))
    # v3.5 genişletmesi: ek sözcükler ayrı modülde; her doğru cümle koruma
    # (kimlik) satırı olarak da girer, böylece temiz oran korunur.
    try:
        from training.v35_extra import EXTRA_SPELLING
    except ImportError:
        EXTRA_SPELLING = ()
    for name, focus, text in EXTRA_SPELLING:
        family = _catalog('x_' + name, 'yazım', focus, text)
        families.extend((
            Family(family.name + '_a', 'yazım', focus, family.pairs[::2]),
            Family(family.name + '_b', 'yazım', focus, family.pairs[1::2]),
            Family(family.name + '_k', 'koruma', focus,
                   tuple(Pair(pair.target, pair.target) for pair in family.pairs)),
        ))
    return families


def _name_families():
    """Her ad ve çekim yalnız kendi elle yazılmış bağlamında kullanılır."""
    return [
        _catalog('ozel_ad_i_yer_a', 'özel_ad', 'I/İ yer adları', '''
Isparta haritada işaretli.|isparta haritada işaretli.
Yarın Isparta'ya gideceğiz.|Yarın ispartaya gideceğiz.
{p} Iğdır'dan yeni döndü.|{p} ığdırdan yeni döndü.
Iğdır adını defterime yazdım.|ığdır adını defterime yazdım.
Ilgın'da kısa bir mola verdik.|ilgında kısa bir mola verdik.
{p} Ihlara'nın fotoğraflarını gösterdi.|{p} ıhlaranın fotoğraflarını gösterdi.
'''),
        _catalog('ozel_ad_i_yer_b', 'özel_ad', 'I/İ yer adları', '''
Ilıca yolculuk listemizde.|ılıca yolculuk listemizde.
Işkodra hakkında bir kitap okudum.|ışkodra hakkında bir kitap okudum.
{p} Isparta'nın sokaklarını gezdi.|{p} ispartanın sokaklarını gezdi.
Iğdır'a otobüsle gidilir mi?|ığdıra otobüsle gidilir mi?
Ihlara'da yürüyüş yaptık.|ıhlarada yürüyüş yaptık.
{p} Ilgın'dan kart gönderdi.|{p} ilgından kart gönderdi.
'''),
        _catalog('ozel_ad_noktali_yer_a', 'özel_ad', 'I/İ yer adları', '''
İzmir haritada işaretli.|izmir haritada işaretli.
Yarın İzmir'e uçacağız.|Yarın izmire uçacağız.
{p} İstanbul'dan yeni döndü.|{p} istanbuldan yeni döndü.
İznik adını defterime yazdım.|iznik adını defterime yazdım.
İnegöl'de kısa bir mola verdik.|inegölde kısa bir mola verdik.
{p} İstanbul'un fotoğraflarını gösterdi.|{p} istanbulun fotoğraflarını gösterdi.
'''),
        _catalog('ozel_ad_noktali_yer_b', 'özel_ad', 'I/İ yer adları', '''
İran yolculuk listemizde.|iran yolculuk listemizde.
İtalya hakkında bir kitap okudum.|italya hakkında bir kitap okudum.
{p} İzmir'in sokaklarını gezdi.|{p} izmirin sokaklarını gezdi.
İngiltere'ye otobüsle gidilir mi?|ingiltereye otobüsle gidilir mi?
İskenderun'da yürüyüş yaptık.|iskenderunda yürüyüş yaptık.
{p} İznik'ten kart gönderdi.|{p} iznikten kart gönderdi.
'''),
        _catalog('ozel_ad_i_kisi_a', 'özel_ad', 'I/İ kişi adları', '''
Işık bugün bize katıldı.|ısık bugün bize katıldı.
{p} Işık'ın önerisini kabul etti.|{p} ısıkın önerisini kabul etti.
Işın'a paket gönderdim.|ışına paket gönderdim.
{p} Işın'dan haber aldı.|{p} ışından haber aldı.
Irmak bugün erken geldi.|ırmak bugün erken geldi.
Ilgar'ın defteri burada kalmış.|ılgarın defteri burada kalmış.
'''),
        _catalog('ozel_ad_i_kisi_b', 'özel_ad', 'I/İ kişi adları', '''
Işıl bugün bize katıldı.|ışıl bugün bize katıldı.
{p} Ilkın'ın resmini beğendi.|{p} ılkının resmini beğendi.
Ilgaz'a mesaj yazdım.|ılgaza mesaj yazdım.
{p} Ilgın'dan haber aldı.|{p} ilgından haber aldı.
Işıl'ın çantası burada kalmış.|ışılın çantası burada kalmış.
Ilkın bugün erken geldi.|ılkın bugün erken geldi.
'''),
        _catalog('ozel_ad_noktali_kisi_a', 'özel_ad', 'I/İ kişi adları', '''
İpek bugün bize katıldı.|ipek bugün bize katıldı.
{p} İpek'in önerisini kabul etti.|{p} ipekin önerisini kabul etti.
İrem'e paket gönderdim.|ireme paket gönderdim.
{p} İsmail'den haber aldı.|{p} ismailden haber aldı.
İdil bugün erken geldi.|idil bugün erken geldi.
İlker'in defteri burada kalmış.|ilkerin defteri burada kalmış.
'''),
        _catalog('ozel_ad_noktali_kisi_b', 'özel_ad', 'I/İ kişi adları', '''
İnan bugün bize katıldı.|inan bugün bize katıldı.
{p} İrfan'ın resmini beğendi.|{p} ırfanın resmini beğendi.
İlhan'a mesaj yazdım.|ilhana mesaj yazdım.
{p} İrem'den haber aldı.|{p} iremden haber aldı.
İsmail'in çantası burada kalmış.|ismailin çantası burada kalmış.
İnan bugün erken geldi.|inan bugün erken geldi.
'''),
        _catalog('ozel_ad_kesme_a', 'özel_ad', 'özel ad kesmeleri', '''
Ayşe'nin çantası burada kaldı.|ayşenin çantası burada kaldı.
{p} Mehmet'e haber verdi.|{p} mehmete haber verdi.
Zeynep'ten paket aldım.|zeynepten paket aldım.
Özge'de yedek anahtar var.|özgede yedek anahtar var.
{p} Can'ın kitabını okudu.|{p} canın kitabını okudu.
Derya'yla parkta buluştuk.|deryayla parkta buluştuk.
'''),
        _catalog('ozel_ad_kesme_b', 'özel_ad', 'özel ad kesmeleri', '''
Işık'ın önerisi mantıklı.|ışıkın önerisi mantıklı.
{p} İpek'e hediye aldı.|{p} ipeke hediye aldı.
Ece'den mektup geldi.|eceden mektup geldi.
Burak'ta yedek pil var.|burakta yedek pil var.
{p} Elif'in notlarını okudu.|{p} elifin notlarını okudu.
Emre'yle kütüphanede buluştuk.|emreyle kütüphanede buluştuk.
'''),
    ]


def _colloquial_families():
    return [
        _catalog('ne_yap_acik', 'açık_yazım', 'ne yap', '''
Ne yapıyorsun bugün?|Napıyorsun bugün?
{p} yarın ne yapacak?|{p} yarın napacak?
Birlikte ne yapalım?|Birlikte napalım?
Ne yapacağını bana söyle.|Napacağını bana söyle.
{p} bu durumda ne yapabilir?|{p} bu durumda napabilir?
Ne yaptığını biliyorum.|Naptığını biliyorum.
{p} akşam ne yapmayı planlıyor?|{p} akşam napmayı planlıyor?
{p} ne yapacağımı merak ediyor.|{p} napacağımı merak ediyor.
'''),
        _catalog('ne_olur_acik', 'açık_yazım', 'ne olur', '''
Ne olur beni bekle.|Nolur beni bekle.
{p} ne olur kapıyı açsın.|{p} nolur kapıyı açsın.
Ne olur bunu bir daha düşün.|Nolur bunu bir daha düşün.
Bana ne olur haber ver.|Bana nolur haber ver.
{p} ne olur bu kez gecikmesin.|{p} nolur bu kez gecikmesin.
Ne olur sessiz olur musun?|Nolur sessiz olur musun?
{p} ne olur bana yardım etsin.|{p} nolur bana yardım etsin.
{p} ne olur bu haberi saklasın.|{p} nolur bu haberi saklasın.
'''),
        _catalog('ne_haber_acik', 'açık_yazım', 'ne haber', '''
Senden ne haber?|Senden naber?
{p} arayıp "Ne haber?" diye sordu.|{p} arayıp "Naber?" diye sordu.
Ne haber nasıl gidiyor?|Naber nasıl gidiyor?
Dostundan ne haber var?|Dostundan naber var?
{p} "Ne haber?" diyerek yanıma geldi.|{p} "Naber?" diyerek yanıma geldi.
Ne haber bugün buluşuyor muyuz?|Naber bugün buluşuyor muyuz?
{p} bana "Ne haber?" diye yazdı.|{p} bana "Naber?" diye yazdı.
{p} kardeşine "Ne haber?" diye sordu.|{p} kardeşine "Naber?" diye sordu.
'''),
        _catalog('ne_oldu_acik', 'açık_yazım', 'ne oldu', '''
Sana ne oldu böyle?|Sana noldu böyle?
{p} ne olduğunu anlamadı.|{p} nolduğunu anlamadı.
Ne oldu neden sustun?|Noldu neden sustun?
Toplantıda ne oldu?|Toplantıda noldu?
{p} bana ne olduğunu söyledi.|{p} bana nolduğunu söyledi.
Ne oldu da vazgeçtin?|Noldu da vazgeçtin?
{p} ne olduğunu açıkladı.|{p} nolduğunu açıkladı.
{p} toplantıda ne olduğunu sordu.|{p} toplantıda nolduğunu sordu.
'''),
    ]


def _de_da_families():
    """Kişi, çatı ve bulunma anlamı her satırda ayrı ayrı yazılmıştır."""
    return [
        _catalog('de_da_baglac_a', 'bağlaç', 'de/da bağlacı', '''
Ben de bu akşam geleceğim.|Bende bu akşam geleceğim.
Sen de bu öneriyi kabul ettin.|Sende bu öneriyi kabul ettin.
O da bizimle yürüdü.|Oda bizimle yürüdü.
Biz de yarın yeniden deneyeceğiz.|Bizde yarın yeniden deneyeceğiz.
{p} bu kitabı da okudu.|{p} bu kitabıda okudu.
Onlar da toplantıya katıldı.|Onlarda toplantıya katıldı.
'''),
        _catalog('de_da_baglac_b', 'bağlaç', 'de/da bağlacı', '''
Ben de kararımı açıkladım.|Bende kararımı açıkladım.
Sen de kapıyı kapattın.|Sende kapıyı kapattın.
Elif de bize katıldı.|Elifde bize katıldı.
Biz de paketi teslim aldık.|Bizde paketi teslim aldık.
{p} son soruyu da yanıtladı.|{p} son soruyuda yanıtladı.
Onlar da bahçeye çıktı.|Onlarda bahçeye çıktı.
'''),
        _catalog('de_da_bulunma_a', 'bağlaç', 'de/da bulunma eki', '''
Anahtarlar evde kalmış.|Anahtarlar ev de kalmış.
{p} okulda seni bekliyor.|{p} okul da seni bekliyor.
Çocuklar parkta oynuyor.|Çocuklar park ta oynuyor.
Müdür bugün ofiste çalıştı.|Müdür bugün ofis te çalıştı.
{p} bahçede çiçekleri suladı.|{p} bahçe de çiçekleri suladı.
Öğrenciler sınıfta sessizce okudu.|Öğrenciler sınıf ta sessizce okudu.
'''),
        _catalog('de_da_bulunma_b', 'bağlaç', 'de/da bulunma eki', '''
Tencere mutfakta kaldı.|Tencere mutfak ta kaldı.
Bu konu kitapta ayrıntılı anlatılıyor.|Bu konu kitap ta ayrıntılı anlatılıyor.
{p} atölyede yeni bir sandalye yaptı.|{p} atölye de yeni bir sandalye yaptı.
Kutular depoda duruyor.|Kutular depo da duruyor.
{p} sahilde yürüyüş yaptı.|{p} sahil de yürüyüş yaptı.
Notlarım arabada kalmış.|Notlarım araba da kalmış.
'''),
    ]


def _punctuation_families():
    return [
        _catalog('gereksiz_virgul_ozne', 'noktalama', 'özne sonrası gereksiz virgül', '''
Elif kitabını okudu ve notlarını paylaştı.|Elif, kitabını okudu ve notlarını paylaştı.
Çocuklar bahçeye çıktı ve oyun oynadı.|Çocuklar, bahçeye çıktı ve oyun oynadı.
{p} pencereyi açtı ve odayı havalandırdı.|{p}, pencereyi açtı ve odayı havalandırdı.
Herkes dışarı çıktı ve kapıyı kapattı.|Herkes, dışarı çıktı ve kapıyı kapattı.
Kardeşim ödevini bitirdi ve kitap okudu.|Kardeşim, ödevini bitirdi ve kitap okudu.
{p} çantayı aldı ve kapıyı kapattı.|{p}, çantayı aldı ve kapıyı kapattı.
'''),
        _catalog('gereksiz_virgul_ve', 'noktalama', 've öncesi gereksiz virgül', '''
Kitabı okudum ve özetini yazdım.|Kitabı okudum, ve özetini yazdım.
{p} kapıyı açtı ve içeri girdi.|{p} kapıyı açtı, ve içeri girdi.
Ekmeği böldüm ve arkadaşımla paylaştım.|Ekmeği böldüm, ve arkadaşımla paylaştım.
Müzik başladı ve çocuklar dans etti.|Müzik başladı, ve çocuklar dans etti.
{p} notları topladı ve dosyaya koydu.|{p} notları topladı, ve dosyaya koydu.
Tren durdu ve yolcular indi.|Tren durdu, ve yolcular indi.
'''),
    ]


def _identity_families():
    families = []
    common = (
        ('koruma_islak', 'ıslak', '''
Islak havluyu balkona astım.
{p} ıslak ayakkabılarını çıkardı.
Islak zeminde yavaş yürüyoruz.
{p} ıslak saçlarını kuruttu.
Islak mendil var mı?
{p} ıslak montunu değiştirdi.
'''),
        ('koruma_ilik', 'ılık', '''
Ilık suyla ellerimi yıkadım.
{p} ılık sütü masaya koydu.
Ilık çorbayı içebilirsin.
{p} ılık havada yürümeyi seviyor.
Ilık bir esinti başladı.
{p} ılık ekmeği paylaştı.
'''),
        ('koruma_isik', 'ışık', '''
Işık gözümü alıyor.
{p} ışık sensörünü kapattı.
Işık kırmızıya dönünce durduk.
{p} ışık kaynağını değiştirdi.
Işık olmadan okuyamıyorum.
{p} ışık hızını derste öğrendi.
'''),
        ('koruma_irmak', 'ırmak', '''
Irmak kenarında dinlendik.
{p} ırmak boyunca yürüdü.
Irmak suyu oldukça soğuk.
{p} ırmak kıyısını fotoğrafladı.
Irmak yatağı kurumuş.
{p} ırmak köprüsünü inceledi.
'''),
        ('koruma_izgara', 'ızgara', '''
Izgara sebzeleri çok sevdim.
{p} ızgara telini temizledi.
Izgara balık pişireceğiz.
{p} ızgara ateşini kontrol etti.
Izgara dumanı yükseliyor.
{p} ızgara köfteleri paylaştı.
'''),
        ('koruma_ihlamur', 'ıhlamur', '''
Ihlamur çayı demledim.
{p} ıhlamur ağacını suladı.
Ihlamur kokusu odayı sardı.
{p} ıhlamur çiçeklerini kuruttu.
Biraz ıhlamur ister misin?
{p} ıhlamur almayı unutmadı.
'''),
        ('koruma_isirgan', 'ısırgan', '''
Isırgan otuna dikkatle yaklaştım.
{p} ısırgan yapraklarını tanıdı.
Isırgan çorbası pişireceğiz.
{p} ısırgan toplarken eldiven taktı.
Isırgan elimi yaktı.
{p} ısırgan otlarını ayıkladı.
'''),
        ('koruma_israr', 'ısrar', '''
Israr etmek istemiyorum.
{p} ısrar edince kabul ettim.
Israrla aynı soruyu sorma.
{p} ısrarla yardım istedi.
Bu konuda ısrar etmeyeceğim.
{p} ısrarla kapıyı çalmadı.
'''),
    )
    for name, focus, text in common:
        families.append(_identity(name, focus, text))

    risky = (
        ('koruma_sicak', 'sıcak', '''
Sıcak çorbayı yavaşça içtim.
{p} sıcak ekmeği masaya getirdi.
Hava sıcak olduğu için pencereyi açalım.
{p} sıcakta uzun süre çalışmadı.
Sıcak su hazır mı?
{p} sıcağı hissedince gölgeye geçti.
'''),
        ('koruma_bicak', 'bıçak', '''
Bıçak gerçekten çok keskin.
{p} bıçağı yıkayıp kuruladı.
Sebze bıçağını arıyorum.
{p} bıçakla ekmek kesti.
Bıçağın sapını değiştirdim.
{p} bıçağın ağzını biledi.
'''),
        ('koruma_ocak', 'ocak', '''
Ocak birden söndü.
{p} ocağın altını kapattı.
Çayı ocakta unuttum.
{p} ocakta yemek pişirdi.
Ocağın alevi çok kısık.
{p} elektrikli ocağı temizledi.
'''),
        ('koruma_kucak', 'kucak', '''
Kucak dolusu çiçek getirdim.
{p} bebeği kucağına aldı.
Kedi kucağımda uyuyor.
{p} kardeşini sıkıca kucakladı.
Annem bana kucak açtı.
{p} paketleri kucağında taşıdı.
'''),
        ('koruma_oyuncak', 'oyuncak', '''
Oyuncak arabayı tamir ettim.
{p} oyuncakları kutuya topladı.
Yerde bir oyuncak buldum.
{p} oyuncağın pilini değiştirdi.
Oda oyuncaklarla dolu.
{p} tahta oyuncağı boyadı.
'''),
        ('koruma_salincak', 'salıncak', '''
Salıncak rüzgârda sallanıyor.
{p} salıncağın ipini kontrol etti.
Bahçede salıncak var.
{p} salıncakta kitap okudu.
Salıncağın tahtası çatlamış.
{p} salıncağı yeniden boyadı.
'''),
        ('koruma_bucak', 'bucak', '''
Köşe bucak anahtarımı aradım.
{p} bucak sınırlarını inceledi.
Bu bucakta kaç köy var?
{p} bucak merkezini haritada gösterdi.
Bucağın nüfusu azalmış.
{p} bucak yönetimi hakkında yazı yazdı.
'''),
        ('koruma_sancak', 'sancak', '''
Sancak törenle taşındı.
{p} sancağın tarihini araştırdı.
Müzede eski bir sancak var.
{p} sancağın desenini çizdi.
Sancak kumaşı yıpranmış.
{p} sancağın yanında durdu.
'''),
        ('koruma_denecek', 'denecek', '''
Denecek söz kalmadı.
{p} buna ne denecek diye sordu.
İyi denecek bir sonuç aldık.
{p} güzel denecek bir resim çizdi.
Denecek sözleri not ettim.
{p} buna başarı denecek mi dedi.
'''),
        ('koruma_yenecek', 'yenecek', '''
Yenecek bir şey var mı?
{p} yenecek elmaları yıkadı.
Dolapta yenecek yemek kalmadı.
{p} yenecek porsiyonları ayırdı.
Bu kadar yemek nasıl yenecek?
{p} yenecek otları tanıyor.
'''),
    )
    for name, focus, text in risky:
        families.append(_identity(name, focus, text))

    name_frames = '''
{x} bugün bize katıldı.
{p} {x} ile konuştu.
Aradığım kişi {x} olabilir.
{x} hakkında güzel şeyler duydum.
{p} {x} ile kütüphanede karşılaştı.
Bu paket {x} için hazırlandı.
'''
    families.extend([
        _protected_forms('koruma_nolan', 'Nolan adı', ('Nolan',), name_frames),
        _protected_forms('koruma_norman', 'Norman adı', ('Norman',), name_frames),
        _protected_forms('koruma_nalan', 'Nalan adı', ('Nalan',), name_frames),
        _identity('koruma_plan', 'plan sözcüğü', '''
Bu plan hepimiz için uygun.
{p} planı dikkatle inceledi.
Yeni bir plan yapabiliriz.
{p} plan hakkında konuştu.
Plan değişirse haber ver.
{p} planın ayrıntılarını anlattı.
'''),
        _identity('koruma_ne_kisa_adlar', 'Can, Nuri ve Neşe adları', '''
Can bugün erken geldi.
{p} Nuri ile konuştu.
Neşe bize katıldı.
{p} Can için paket hazırladı.
Nuri kapıda bekliyor.
{p} Neşe ile çalıştı.
'''),
        _identity('koruma_dogal_cumleler', 'doğal çok yan cümleli yazım', '''
Yağmur dinince çocuklar bahçeye çıktı ve oyun oynadı.
{p} ödevini bitirince kitabını aldı ve balkona çıktı.
Tren gecikince beklemeye devam ettik ve çay içtik.
Hava kararınca lambaları yaktım ve pencereleri kapattım.
{p} müziği duyunca gülümsedi ve bize katıldı.
Ders bitince öğrenciler defterlerini topladı ve dışarı çıktı.
'''),
        _identity('koruma_de_da_dogru', 'doğru de/da kullanımı', '''
Ben de bu akşam sizinle geleceğim.
{p} bütün gün evde sessizce çalıştı.
Sen de bu kitabı okudun mu?
{p} okulda tören boyunca bizi bekledi.
Onlar da dün toplantıya katıldı.
{p} akşam parkta yürüyüş yaptı.
'''),
        _identity('koruma_kesme_dogru', 'doğru özel ad kesmeleri', '''
Ayşe'nin çantası dün burada kaldı.
{p} Mehmet'e bugün haber verdi.
İpek'in renkli resmi çok güzel.
{p} Işık'ın son önerisini kabul etti.
Özge'ye küçük paket gönderdik.
{p} Can'ın yeni kitabını okudu.
'''),
        _identity('koruma_abi', 'abi ve çekimli biçimleri', '''
Abi bugün bize geldi.
{p} abi diye seslendi.
Abim kapıda bekliyor.
{p} abime paket verdi.
Bana abi desinler mi?
{p} abisiyle konuştu.
'''),
        _identity('koruma_bilmem', 'bilmem sözcüğü', '''
Nerede olduklarını bilmem mümkün değil.
{p} bilmem diye cevapladı.
Bu yolu bilmem gerekir mi?
{p} bilmem demekle yetinmedi.
Her şeyi bilmem beklenemez.
{p} bilmem diyerek sustu.
'''),
        _identity('koruma_tabi', 'kurala tabi kullanımı', '''
Bu karar kurallara tabi.
{p} bu kurallara tabi oldu.
Öğrenciler okul kurallarına tabi.
Belgeler incelemeye tabi.
{p} tabi kelimesini cümlede kullandı.
Bu başvuru onaya tabi.
'''),
    ])
    return families


def _suffix_protection():
    return [_identity('koruma_ad_ekleri', 'Nolan/Norman/Nalan çekimleri', '''
Nolan'ın yeni projesi merak uyandırdı.
{p} Nolan'ın açıklamasını dikkatle dinledi.
Nolan'a ulaşmak için sekreterini aradık.
{p} Nolan'dan bir yanıt bekliyor.
Nolan'la yapılan söyleşi gazetede çıktı.
{p} Nolan'ın çalışmalarını yakından takip ediyor.
Nolan'ın masasında eski bir defter duruyor.
{p} Nolan'a davetiye gönderdi.
Norman'ın bavulu otelde unutulmuş.
{p} Norman'a yol tarif etti.
Norman'dan gelen mesajı okudum.
{p} Norman'ın adresini not etti.
Norman'la aynı sırada oturduk.
Nalan'ın evi parka çok yakın.
{p} Nalan'a teşekkür etti.
Nalan'dan ödünç aldığım kitabı bitirdim.
{p} Nalan'ın çantasını arabaya koydu.
Nalan'la birlikte kursa yazıldık.
''')]


def _families():
    families = (_spelling_families() + _name_families() + _colloquial_families()
                + _de_da_families() + _punctuation_families() + _identity_families()
                + _suffix_protection())
    names = [family.name for family in families]
    assert len(names) == len(set(names))
    return families


def _expand_pair(pair):
    fields = sorted({field for _, field, _, _ in string.Formatter().parse(pair.target)
                     if field is not None})
    assert set(fields) <= {'p'}
    groups = []
    values = (PEOPLE,) if fields else ()
    for selected in itertools.product(*values):
        slots = dict(zip(fields, selected))
        target = ' '.join(pair.target.format(**slots).split())
        wrong = ' '.join(pair.input.format(**slots).split())
        groups.append((target, wrong))
    return groups


def _choose_family(family, limit, rng):
    groups = []
    for pair in family.pairs:
        expanded = _expand_pair(pair)
        rng.shuffle(expanded)
        groups.append(expanded)
    rng.shuffle(groups)
    selected = []
    while groups and len(selected) < limit:
        remaining = []
        for group in groups:
            if len(selected) < limit and group:
                selected.append(group.pop())
            if group:
                remaining.append(group)
        groups = remaining
    assert len(selected) >= min(limit, len(family.pairs)), family.name
    return selected


# A family is an authored sentence skeleton, not a focus/word bucket.
_NAMES = PEOPLE + ('Isparta', 'Iğdır', 'Ilgın', 'Ihlara', 'Ilıca', 'Işkodra',
    'İzmir', 'İstanbul', 'İznik', 'İnegöl', 'İran', 'İtalya', 'İngiltere',
    'İskenderun', 'Işık', 'Işın', 'Irmak', 'Ilgar', 'Işıl', 'Ilkın', 'Ilgaz',
    'İpek', 'İrem', 'İsmail', 'İdil', 'İlker', 'İnan', 'İrfan', 'İlhan',
    'Özge', 'Can', 'Nolan', 'Norman', 'Nalan', 'Nuri', 'Neşe')
_NAME_PATTERN = re.compile(r"\b(?:" + '|'.join(map(re.escape, sorted(set(_NAMES), key=len, reverse=True)))
                           + r")(?:'[A-Za-zÇĞİÖŞÜçğıöşü]+)?\b")


def skeleton(text):
    return canonical(_NAME_PATTERN.sub('adslot', text.replace('{p}', 'adslot')))


def build_splits(seed=3500):
    """Independent deterministic skeleton holdout, with every focus in train."""
    groups = defaultdict(list)
    for catalog in _families():
        for pair in catalog.pairs:
            groups[skeleton(pair.target)].append((catalog, pair))
    group_keys = sorted(groups)
    rng = random.Random(seed)
    rng.shuffle(group_keys)
    coverage = defaultdict(set)
    for key, entries in groups.items():
        for catalog, _ in entries:
            coverage[(catalog.kind, catalog.focus)].add(key)
    held = set()
    for key in group_keys:
        if len(held) >= round(len(groups) * .15):
            break
        focuses = {(c.kind, c.focus) for c, _ in groups[key]}
        if all(len(coverage[f] - held - {key}) >= 2 for f in focuses):
            held.add(key)
    splits = {'train': [], 'validation': []}
    pair_seen = set()
    for key in sorted(groups):
        split = 'validation' if key in held else 'train'
        family_id = 'v35_' + hashlib.sha256(key.encode()).hexdigest()[:16]
        for catalog, pair in groups[key]:
            for target, wrong in _expand_pair(pair):
                variants = [wrong]
                if wrong != target and lower_tr(wrong) != wrong:
                    variants.append(lower_tr(wrong))
                for source in variants:
                    signature = (source, target)
                    if signature in pair_seen:
                        continue
                    pair_seen.add(signature)
                    splits[split].append({'input': source, 'target': target,
                        'kind': catalog.kind, 'focus': catalog.focus, 'family': family_id,
                        'source': SOURCE})
    rng.shuffle(splits['train'])
    rng.shuffle(splits['validation'])
    _validate(splits)
    return splits


def _validate(splits):
    train, validation = splits['train'], splits['validation']
    assert len(train) >= 1200 and len(validation) >= 100
    labels = {}
    for rows in splits.values():
        for row in rows:
            target, source = row['target'], row['input']
            for text in (target, source):
                assert 2 <= len(text.split()) <= 24, text
                assert len(text.encode('utf-8')) <= 170, text
                assert '\ufffd' not in text, text
            assert target[0].isupper() and target[-1] in '.?!', target
            assert source[-1] == target[-1], row
            key, value = canonical(source), canonical(target)
            assert key not in labels or labels[key] == value, row
            labels[key] = value
    for field in ('target', 'input'):
        assert {canonical(r[field]) for r in train}.isdisjoint(canonical(r[field]) for r in validation)
    assert {r['family'] for r in train}.isdisjoint(r['family'] for r in validation)
    assert {skeleton(r['target']) for r in train}.isdisjoint(skeleton(r['target']) for r in validation)
    assert len({r['family'] for r in train}) >= 60
    assert len({canonical(r['target'].split()[0]) for r in train}) >= 50
    for rows in (train, validation):
        assert sum(r['input'] == r['target'] for r in rows) / len(rows) >= .25
    expected = {(c.kind, c.focus) for c in _families()}
    assert expected <= {(r['kind'], r['focus']) for r in train}
    assert max(Counter(r['family'] for r in train).values()) / len(train) <= .05
