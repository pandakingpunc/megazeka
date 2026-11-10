# Megazeka değerlendirmesi

```json
{
  "examples": 1128,
  "cer": 0.012254667304930588,
  "wer": 0.058694181326116375,
  "exact_match": 0.7810283687943262,
  "edit_precision": 0.93046875,
  "edit_recall": 0.8881431767337807,
  "edit_f1": 0.908813429988554,
  "clean_examples": 282,
  "overcorrection": 0.010638297872340425
}
```

## Denetlenmiş hedefler

```json
{
  "examples": 1116,
  "cer": 0.012970106075216972,
  "wer": 0.062414733969986355,
  "exact_match": 0.767921146953405,
  "edit_precision": 0.9339473684210526,
  "edit_recall": 0.8802083333333334,
  "edit_f1": 0.9062819203268642,
  "clean_examples": 269,
  "overcorrection": 0.0037174721189591076
}
```

## Alt küme: common_voice (640 çift)

```json
{
  "filtreli": {
    "examples": 640,
    "cer": 0.015543843568591507,
    "wer": 0.07162017167381975,
    "exact_match": 0.7140625,
    "edit_precision": 0.9195449004469728,
    "edit_recall": 0.8647306075659151,
    "edit_f1": 0.8912957857424183,
    "clean_examples": 160,
    "overcorrection": 0.01875
  },
  "ham": {
    "examples": 640,
    "cer": 0.01401619309501986,
    "wer": 0.06893776824034335,
    "exact_match": 0.7203125,
    "edit_precision": 0.9166998804304504,
    "edit_recall": 0.8788689338937715,
    "edit_f1": 0.8973858759266485,
    "clean_examples": 160,
    "overcorrection": 0.01875
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
    "cer": 0.006732495511669659,
    "wer": 0.03663003663003663,
    "exact_match": 0.8688524590163934,
    "edit_precision": 0.9499637418419145,
    "edit_recall": 0.9317211948790897,
    "edit_f1": 0.940754039497307,
    "clean_examples": 122,
    "overcorrection": 0.0
  },
  "ham": {
    "examples": 488,
    "cer": 0.006732495511669659,
    "wer": 0.03663003663003663,
    "exact_match": 0.8688524590163934,
    "edit_precision": 0.9499637418419145,
    "edit_recall": 0.9317211948790897,
    "edit_f1": 0.940754039497307,
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
GİRDİ: Aşk ağlatırr, dert söyletir.
MODEL: Aşk ağlatır, dert söyletir.
HEDEF: Aşk ağlatır, dert söyletir.
```

```text
GİRDİ: İki yaşlarinda kadar bir cocuk salıncakta oturmuş katilırcasına agliyordu.
MODEL: İki yaşlarında kadar bir çocuk salıncakta oturmuş katılırcasına ağlıyordu.
HEDEF: İki yaşlarında kadar bir çocuk salıncakta oturmuş katılırcasına ağlıyordu.
```

```text
GİRDİ: Seninle konusmak istiyor.
MODEL: Seninle konuşmak istiyor.
HEDEF: Seninle konuşmak istiyor.
```

## Yanlış düzeltmeler

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
GİRDİ: Sonra ortalığı yıldırmış olduğum için, şurda burda saklı karıları bensiz alıp getiremezlerdi.
MODEL: Sonra ortalığı yıldırmış olduğum için, şurda burada saklı karıları bensiz alıp getiremezlerdi.
HEDEF: Sonra ortalığı yıldırmış olduğum için, şurda burda saklı karıları bensiz alıp getiremezlerdi.
```

## Kaçırılan düzeltmeler

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
GİRDİ: Tavuslara, sülnlere bakmaya tenezzül etmeyen yabani kuş, kanadı kırık bir çulluğun, avı oldu.
MODEL: Tavuslara, sülnlere bakmaya tenezzül etmeyen yabani kuş, kanadı kırık bir çulluğun, avı oldu.
HEDEF: Tavuslara, sülünlere bakmaya tenezzül etmeyen yabani kuş, kanadı kırık bir çulluğun, avı oldu.
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
GİRDİ: sIZINSUÖUNUZDEĞIL.
MODEL: sIZINSUÖUNUZDEĞIL.
HEDEF: Sizin suçunuz değil.
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

```text
GİRDİ: Ağız büzülür, göz süzülür, ilşe burun, ille burun.
MODEL: Ağız büzülür, göz süzülür, ilşe burun, ille burun.
HEDEF: Ağız büzülür, göz süzülür, ille burun, ille burun.
```

## Zor örnekler

```text
GİRDİ: wşeği  suren osuruguna katşanir.
MODEL: Eşeği süren osuruğuna katşanır.
HEDEF: Eşeği süren osuruğuna katlanır.
```

```text
GİRDİ: Yarin aksam sama annlatıyoru?z.
MODEL: Yarın akşam sama anlatıyoruz.
HEDEF: Yarın akşam sana anlatıyoruz.
```

```text
GİRDİ: Ben onu beklerken, evimi ona kabbbule haz irlrken olmustu.
MODEL: Ben onu beklerken, evimi ona kabule hazırlarken olmuştu.
HEDEF: Ben onu beklerken, evimi ona kabule hazırlarken ölmüştü.
```

```text
GİRDİ: ne ldu, iyiisin?
MODEL: Ne oldu, iyisin?
HEDEF: Ne oldu, iyi misin?
```

```text
GİRDİ: Sieihiyacımyok.
MODEL: Sihi yacım yok.
HEDEF: Size ihtiyacım yok.
```

```text
GİRDİ: Oğleden sonra og retmenmesaji gonderiyo.
MODEL: Öğleden sonra oğretmen mesajı gönderiyor.
HEDEF: Öğleden sonra öğretmen mesajı gönderiyor.
```

```text
GİRDİ: C?okuzgünumbaba.
MODEL: Çokuz günüm baba.
HEDEF: Çok üzgünüm baba.
```

```text
GİRDİ: Pekala,  hxir misiniz?
MODEL: Pek ala, hiç misiniz?
HEDEF: Pekala, hazır mısınız?
```

```text
GİRDİ: Bir kere cikayım fa sonrasş kolay
MODEL: Bir kere çıkayım, fasonrası kolay.
HEDEF: Bir kere çıkayım da, sonrası kolay.
```

```text
GİRDİ: Ben yukarda sedire uzanurım!
MODEL: Ben yukarda sedire uzanırım!
HEDEF: Ben yukarıda sedire uzanırım!
```

```text
GİRDİ: kusura bakma unut musum
MODEL: Kusura bakma unut musun?
HEDEF: Kusura bakma, unutmuşum.
```

```text
GİRDİ: Şidi babam deni bulacak sonra sabah kitabıbitirecek
MODEL: Şidi babam deni bulacak, sonra sabah kitabı bitirecek.
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
MODEL: Yarın arkadaşlarla buluşacağız, sonra da sinemaya gideceğiz.
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
