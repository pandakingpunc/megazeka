# Megazeka değerlendirmesi

```json
{
  "examples": 1128,
  "cer": 0.013068453805648635,
  "wer": 0.06309201623815967,
  "exact_match": 0.7677304964539007,
  "edit_precision": 0.9135738385673501,
  "edit_recall": 0.8749689286602038,
  "edit_f1": 0.8938547486033519,
  "clean_examples": 282,
  "overcorrection": 0.024822695035460994
}
```

## Denetlenmiş hedefler

```json
{
  "examples": 1116,
  "cer": 0.013789778206364513,
  "wer": 0.06667803547066849,
  "exact_match": 0.753584229390681,
  "edit_precision": 0.9170821306743637,
  "edit_recall": 0.8668154761904762,
  "edit_f1": 0.8912405967104425,
  "clean_examples": 269,
  "overcorrection": 0.01486988847583643
}
```

## Alt küme: common_voice (640 çift)

```json
{
  "filtreli": {
    "examples": 640,
    "cer": 0.015887564925145127,
    "wer": 0.07591201716738197,
    "exact_match": 0.696875,
    "edit_precision": 0.8957915831663327,
    "edit_recall": 0.8540313335880779,
    "edit_f1": 0.8744131455399061,
    "clean_examples": 160,
    "overcorrection": 0.04375
  },
  "ham": {
    "examples": 640,
    "cer": 0.015620226092270088,
    "wer": 0.0740343347639485,
    "exact_match": 0.7015625,
    "edit_precision": 0.8894571203776553,
    "edit_recall": 0.8639663737103553,
    "edit_f1": 0.8765264586160109,
    "clean_examples": 160,
    "overcorrection": 0.04375
  },
  "girdiyi_kopyala": {
    "examples": 640,
    "cer": 0.09998472349526429,
    "wer": 0.35568669527896996,
    "exact_match": 0.25,
    "edit_precision": 0.0,
    "edit_recall": 0.0,
    "edit_f1": 0.0,
    "clean_examples": 160,
    "overcorrection": 0.0
  }
}
```

## Alt küme: gündelik (488 çift)

```json
{
  "filtreli": {
    "examples": 488,
    "cer": 0.008335470633495767,
    "wer": 0.04120879120879121,
    "exact_match": 0.860655737704918,
    "edit_precision": 0.9462444771723122,
    "edit_recall": 0.9139402560455192,
    "edit_f1": 0.9298118668596237,
    "clean_examples": 122,
    "overcorrection": 0.0
  },
  "ham": {
    "examples": 488,
    "cer": 0.008143113618876634,
    "wer": 0.04075091575091575,
    "exact_match": 0.8627049180327869,
    "edit_precision": 0.9422092172640819,
    "edit_recall": 0.9160739687055477,
    "edit_f1": 0.9289578074287774,
    "clean_examples": 122,
    "overcorrection": 0.0
  },
  "girdiyi_kopyala": {
    "examples": 488,
    "cer": 0.09015132085150039,
    "wer": 0.3608058608058608,
    "exact_match": 0.25,
    "edit_precision": 0.0,
    "edit_recall": 0.0,
    "edit_f1": 0.0,
    "clean_examples": 122,
    "overcorrection": 0.0
  }
}
```

Düzenleme hassasiyeti/duyarlılığı, orijinal karakter konumlarına bağlı Levenshtein işlem kümeleriyle ölçülür.

## Başarılı düzeltmeler

```text
GİRDİ: Nihayet şarrrkıyı bbbitirdi ve sazı eline alarak ayağa kalktı.
MODEL: Nihayet şarkıyı bitirdi ve sazı eline alarak ayağa kalktı.
HEDEF: Nihayet şarkıyı bitirdi ve sazı eline alarak ayağa kalktı.
```

```text
GİRDİ: kIM OLDUGUMU SOYLEMEYE HACET YOKTU.
MODEL: Kim olduğumu söylemeye hacet yoktu.
HEDEF: Kim olduğumu söylemeye hacet yoktu.
```

```text
GİRDİ: Eskiye itibar olsaydi bitpazarina nur yagardi.
MODEL: Eskiye itibar olsaydı bitpazarına nur yağardı.
HEDEF: Eskiye itibar olsaydı bitpazarına nur yağardı.
```

```text
GİRDİ: Herhalde yaşamak istemediği için
MODEL: Herhalde yaşamak istemediği için.
HEDEF: Herhalde yaşamak istemediği için.
```

```text
GİRDİ: senş  seviyor muusn?
MODEL: Seni seviyor musun?
HEDEF: Seni seviyor musun?
```

```text
GİRDİ: Her zamankinden daha iltifatkarsınız sulltanım.
MODEL: Her zamankinden daha iltifatkarsınız sultanım.
HEDEF: Her zamankinden daha iltifatkarsınız sultanım.
```

```text
GİRDİ: Bir kere çıka yım da, sonrası kolay.
MODEL: Bir kere çıkayım da, sonrası kolay.
HEDEF: Bir kere çıkayım da, sonrası kolay.
```

```text
GİRDİ: Soyle.yecek bir kelime bulamadi.
MODEL: Söyleyecek bir kelime bulamadı.
HEDEF: Söyleyecek bir kelime bulamadı.
```

```text
GİRDİ: Arkamdan hayretle bakanhizmetçi kıza teşekkür bile etmeden merdivenleri dörder dörder atladım.
MODEL: Arkamdan hayretle bakan hizmetçi kıza teşekkür bile etmeden merdivenleri dörder dörder atladım.
HEDEF: Arkamdan hayretle bakan hizmetçi kıza teşekkür bile etmeden merdivenleri dörder dörder atladım.
```

```text
GİRDİ: BBunu neden ypatttigımi bilmiyorum.
MODEL: Bunu neden yaptığımı bilmiyorum.
HEDEF: Bunu neden yaptığımı bilmiyorum.
```

```text
GİRDİ: Birkac parcadan ibaret camasırlari kapınin arkasina yigdim.
MODEL: Birkaç parçadan ibaret çamaşırları kapının arkasına yığdım.
HEDEF: Birkaç parçadan ibaret çamaşırları kapının arkasına yığdım.
```

```text
GİRDİ: İki yaşlarinda kadar bir cocuk salıncakta oturmuş katilırcasına agliyordu.
MODEL: İki yaşlarında kadar bir çocuk salıncakta oturmuş katılırcasına ağlıyordu.
HEDEF: İki yaşlarında kadar bir çocuk salıncakta oturmuş katılırcasına ağlıyordu.
```

## Yanlış düzeltmeler

```text
GİRDİ: Her akla geleni işleme her ağacı taslama.
MODEL: Her akla geleni işleme her ağacı taşlama.
HEDEF: Her akla geleni işleme her ağacı taslama.
```

```text
GİRDİ: Hani nerdeyse harman yerlerinden duyulacaktı.
MODEL: Hani neredeyse harman yerlerinden duyulacaktı.
HEDEF: Hani nerdeyse harman yerlerinden duyulacaktı.
```

```text
GİRDİ: İyi etmediniz, bizim kaptan asabidir, şakadan hazzetmez.
MODEL: İyi etmediniz, bizim kaptan asabıdır, şakadan hazzetmez.
HEDEF: İyi etmediniz, bizim kaptan asabidir, şakadan hazzetmez.
```

```text
GİRDİ: Tavuslara, sülünlere bakmaya tenezzül etmeyen yabani kuş, kanadı kırık bir çulluğun, avı oldu.
MODEL: Tavuşlara, sülünlere bakmaya tenezzül etmeyen yabani kuş, kanadı kırık bir çulluğun, avı oldu.
HEDEF: Tavuslara, sülünlere bakmaya tenezzül etmeyen yabani kuş, kanadı kırık bir çulluğun, avı oldu.
```

```text
GİRDİ: Sonra ortalığı yıldırmış olduğum için, şurda burda saklı karıları bensiz alıp getiremezlerdi.
MODEL: Sonra ortalığı yıldırmış olduğum için, şurda burada saklı karıları bensiz alıp getiremezlerdi.
HEDEF: Sonra ortalığı yıldırmış olduğum için, şurda burda saklı karıları bensiz alıp getiremezlerdi.
```

```text
GİRDİ: Islak kumlar ayaklarımızın altında gıcırdıyordu.
MODEL: Islak kumlar ayaklarımızın altında gıçırdıyordu.
HEDEF: Islak kumlar ayaklarımızın altında gıcırdıyordu.
```

```text
GİRDİ: Aşk ağlatır, dert söyletir.
MODEL: Akşak ağlatır, dert söyletir.
HEDEF: Aşk ağlatır, dert söyletir.
```

## Kaçırılan düzeltmeler

```text
GİRDİ: Ben yukarda sedire uzanurım!
MODEL: Ben yukarda sedire uzanurım!
HEDEF: Ben yukarıda sedire uzanırım!
```

```text
GİRDİ: Yağmur yağıyor, ıslancaksın.
MODEL: Yağmur yağıyor, ıslancaksın.
HEDEF: Yağmur yağıyor, ıslanacaksın.
```

```text
GİRDİ: Hiçbir ipucu ok.
MODEL: Hiçbir ipucu ok.
HEDEF: Hiçbir ipucu yok.
```

```text
GİRDİ: Bir şeyer ayarlarız.
MODEL: Bir şeyer ayarlarız.
HEDEF: Bir şeyler ayarlarız.
```

```text
GİRDİ: Hadise, umumiyet itibariyle, zannedildiği kadar korkunç bir şey eğildi.
MODEL: Hadise, umumiyet itibariyle, zannedildiği kadar korkunç bir şey eğildi.
HEDEF: Hadise, umumiyet itibariyle, zannedildiği kadar korkunç bir şey değildi.
```

```text
GİRDİ: Yarın aşkamevi temizler misin?
MODEL: Yarın aşkamevi temizler misin?
HEDEF: Yarın akşam evi temizler misin?
```

```text
GİRDİ: bEN SIZEYETISIRIM
MODEL: bEN SIZEYETISIRIM
HEDEF: Ben size yetişirim.
```

```text
GİRDİ: Genç kız onun uyanmış olduğunu görünce gülüm sedi.
MODEL: Genç kız onun uyanmış olduğunu görünce gülüm sedi.
HEDEF: Genç kız onun uyanmış olduğunu görünce gülümsedi.
```

```text
GİRDİ: Başkatürlü olacağını mı zan nediyordunuz?
MODEL: Başkatürlü olacağını mı zan nediyordunuz?
HEDEF: Başka türlü olacağını mı zannediyordunuz?
```

```text
GİRDİ: Bir gardiyan elindeki kağıda bakarak yoklama yatı.
MODEL: Bir gardiyan elindeki kağıda bakarak yoklama yatı.
HEDEF: Bir gardiyan elindeki kağıda bakarak yoklama yaptı.
```

```text
GİRDİ: Ancak kenefe gittiği zamankar peşinden fırlar, apteshane aralığında sıkıştırıp üç beş lira alırım.
MODEL: Ancak kenefe gittiği zamankar peşinden fırlar, apteshane aralığında sıkıştırıp üç beş lira alırım.
HEDEF: Ancak kenefe gittiği zamanlar peşinden fırlar, apteshane aralığında sıkıştırıp üç beş lira alırım.
```

```text
GİRDİ: Birkaç adım daha atınca yanına feldi.
MODEL: Birkaç adım daha atınca yanına feldi.
HEDEF: Birkaç adım daha atınca yanına geldi.
```

## Zor örnekler

```text
GİRDİ: wşeği  suren osuruguna katşanir.
MODEL: Güzeği şüren osuruğuna katşanır.
HEDEF: Eşeği süren osuruğuna katlanır.
```

```text
GİRDİ: Yarin aksam sama annlatıyoru?z.
MODEL: Yarın akşam sama anlatıyoruz.
HEDEF: Yarın akşam sana anlatıyoruz.
```

```text
GİRDİ: Ben onu beklerken, evimi ona kabbbule haz irlrken olmustu.
MODEL: Ben onu beklerken, evimi ona kabule hazırlaken olmuştu.
HEDEF: Ben onu beklerken, evimi ona kabule hazırlarken ölmüştü.
```

```text
GİRDİ: ne ldu, iyiisin?
MODEL: Ne yapdı, iyisin?
HEDEF: Ne oldu, iyi misin?
```

```text
GİRDİ: Sieihiyacımyok.
MODEL: Sihiyacım yok.
HEDEF: Size ihtiyacım yok.
```

```text
GİRDİ: C?okuzgünumbaba.
MODEL: Çokuz günüm baba.
HEDEF: Çok üzgünüm baba.
```

```text
GİRDİ: Pekala,  hxir misiniz?
MODEL: Pekala, hizir misiniz?
HEDEF: Pekala, hazır mısınız?
```

```text
GİRDİ: Bir kere cikayım fa sonrasş kolay
MODEL: Bir kere çıkayım, fas sonrası kolay.
HEDEF: Bir kere çıkayım da, sonrası kolay.
```

```text
GİRDİ: Ben yukarda sedire uzanurım!
MODEL: Ben yukarda sedire uzanurım!
HEDEF: Ben yukarıda sedire uzanırım!
```

```text
GİRDİ: Fakatadresiin blimiyrdum.
MODEL: Fakat dersin bilmiyordum.
HEDEF: Fakat adresini bilmiyordum.
```

```text
GİRDİ: kusura bakma unut musum
MODEL: Kusura bakma unut musun?
HEDEF: Kusura bakma, unutmuşum.
```

```text
GİRDİ: Şidi babam deni bulacak sonra sabah kitabıbitirecek
MODEL: Şidi babam deni bulacak sonra sabah kitabı bitirecek.
HEDEF: Şimdi babam seni bulacak, sonra sabah kitabı bitirecek.
```

## Manuel örnekler

```text
GİRDİ: bugün okula gidicem ama hava cok kötü galiba
MODEL: Bugün okula gideceğim ama hava çok kötü galiba.
HEDEF: Bugün okula gideceğim ama hava çok kötü galiba.
```

```text
GİRDİ: yarin arkadaşlarla buluşcaz sonrada sinemaya gidicez
MODEL: Yarın arkadaşlarla buluşacağız, sonrada sinemaya gideceğiz.
HEDEF: Yarın arkadaşlarla buluşacağız, sonra da sinemaya gideceğiz.
```

```text
GİRDİ: Bu film baya iyi olmuş.
MODEL: Bu film baya iyi olmuş.
HEDEF: Bu film baya iyi olmuş.
```

```text
GİRDİ: Bugün hava çok güzel.
MODEL: Bugün hava çok güzel.
HEDEF: Bugün hava çok güzel.
```

```text
GİRDİ: Ben de seninle geleceğim.
MODEL: Ben de seninle geleceğim.
HEDEF: Ben de seninle geleceğim.
```

```text
GİRDİ: Ankaraya yarin gidicem.
MODEL: Ankara'ya yarın gideceğim.
HEDEF: Ankara'ya yarın gideceğim.
```

```text
GİRDİ: herkez buraya gelsin
MODEL: Herkes buraya gelsin.
HEDEF: Herkes buraya gelsin.
```

```text
GİRDİ: Beni duyuyormusun?
MODEL: Beni duyuyor musun?
HEDEF: Beni duyuyor musun?
```

```text
GİRDİ: Bu gerçekten güzel bir haber.
MODEL: Bu gerçekten güzel bir haber.
HEDEF: Bu gerçekten güzel bir haber.
```

```text
GİRDİ: Merhaba!

Nasılsın?
MODEL: Merhaba!

Nasılsın?
HEDEF: Merhaba!

Nasılsın?
```

```text
GİRDİ: Cok tesekkur ederim.
MODEL: Çok teşekkür ederim.
HEDEF: Çok teşekkür ederim.
```

```text
GİRDİ: Işık, İstanbul’a yarın gelecek.
MODEL: Işık, İstanbul’a yarın gelecek.
HEDEF: Işık, İstanbul’a yarın gelecek.
```
