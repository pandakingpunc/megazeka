# Megazeka değerlendirmesi

```json
{
  "examples": 1128,
  "cer": 0.09633796074676879,
  "wer": 0.35791610284167796,
  "exact_match": 0.24911347517730498,
  "edit_precision": 0.0,
  "edit_recall": 0.0,
  "edit_f1": 0.0,
  "clean_examples": 282,
  "overcorrection": 0.0035460992907801418
}
```

## Alt küme: common_voice (640 çift)

```json
{
  "filtreli": {
    "examples": 640,
    "cer": 0.10002291475710358,
    "wer": 0.3562231759656652,
    "exact_match": 0.2484375,
    "edit_precision": 0.0,
    "edit_recall": 0.0,
    "edit_f1": 0.0,
    "clean_examples": 160,
    "overcorrection": 0.00625
  },
  "ham": {
    "examples": 640,
    "cer": 3.6314925145126793,
    "wer": 3.8800965665236054,
    "exact_match": 0.0,
    "edit_precision": 0.002136386942403008,
    "edit_recall": 0.02865876958349255,
    "edit_f1": 0.0039763539485194715,
    "clean_examples": 160,
    "overcorrection": 1.0
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
    "cer": 0.09015132085150039,
    "wer": 0.3608058608058608,
    "exact_match": 0.25,
    "edit_precision": 0.0,
    "edit_recall": 0.0,
    "edit_f1": 0.0,
    "clean_examples": 122,
    "overcorrection": 0.0
  },
  "ham": {
    "examples": 488,
    "cer": 4.720441138753526,
    "wer": 4.740842490842491,
    "exact_match": 0.0,
    "edit_precision": 0.002184434831027541,
    "edit_recall": 0.03627311522048364,
    "edit_f1": 0.004120712640892013,
    "clean_examples": 122,
    "overcorrection": 1.0
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

Bu kategoride örnek yok.
## Yanlış düzeltmeler

```text
GİRDİ: Hatta ailesini, bu aile arasındaki vaziyetini yakından görünce hakkındaki merakım büsbütün arttı.
MODEL: Hatta ailesini bu aile arasındaki vaziyetini yakından görünce hakkındaki merakım büsbütün arttı.
HEDEF: Hatta ailesini, bu aile arasındaki vaziyetini yakından görünce hakkındaki merakım büsbütün arttı.
```

## Kaçırılan düzeltmeler

```text
GİRDİ: Nihayet şarrrkıyı bbbitirdi ve sazı eline alarak ayağa kalktı.
MODEL: Nihayet şarrrkıyı bbbitirdi ve sazı eline alarak ayağa kalktı.
HEDEF: Nihayet şarkıyı bitirdi ve sazı eline alarak ayağa kalktı.
```

```text
GİRDİ: kIM OLDUGUMU SOYLEMEYE HACET YOKTU.
MODEL: kIM OLDUGUMU SOYLEMEYE HACET YOKTU.
HEDEF: Kim olduğumu söylemeye hacet yoktu.
```

```text
GİRDİ: Eskiye itibar olsaydi bitpazarina nur yagardi.
MODEL: Eskiye itibar olsaydi bitpazarina nur yagardi.
HEDEF: Eskiye itibar olsaydı bitpazarına nur yağardı.
```

```text
GİRDİ: Herhalde yaşamak istemediği için
MODEL: Herhalde yaşamak istemediği için
HEDEF: Herhalde yaşamak istemediği için.
```

```text
GİRDİ: wşeği  suren osuruguna katşanir.
MODEL: wşeği  suren osuruguna katşanir.
HEDEF: Eşeği süren osuruğuna katlanır.
```

```text
GİRDİ: senş  seviyor muusn?
MODEL: senş  seviyor muusn?
HEDEF: Seni seviyor musun?
```

```text
GİRDİ: Her zamankinden daha iltifatkarsınız sulltanım.
MODEL: Her zamankinden daha iltifatkarsınız sulltanım.
HEDEF: Her zamankinden daha iltifatkarsınız sultanım.
```

```text
GİRDİ: Yarin aksam sama annlatıyoru?z.
MODEL: Yarin aksam sama annlatıyoru?z.
HEDEF: Yarın akşam sana anlatıyoruz.
```

```text
GİRDİ: Ben onu beklerken, evimi ona kabbbule haz irlrken olmustu.
MODEL: Ben onu beklerken, evimi ona kabbbule haz irlrken olmustu.
HEDEF: Ben onu beklerken, evimi ona kabule hazırlarken ölmüştü.
```

```text
GİRDİ: Bir kere çıka yım da, sonrası kolay.
MODEL: Bir kere çıka yım da, sonrası kolay.
HEDEF: Bir kere çıkayım da, sonrası kolay.
```

```text
GİRDİ: ne ldu, iyiisin?
MODEL: ne ldu, iyiisin?
HEDEF: Ne oldu, iyi misin?
```

```text
GİRDİ: Soyle.yecek bir kelime bulamadi.
MODEL: Soyle.yecek bir kelime bulamadi.
HEDEF: Söyleyecek bir kelime bulamadı.
```

## Zor örnekler

```text
GİRDİ: wşeği  suren osuruguna katşanir.
MODEL: wşeği  suren osuruguna katşanir.
HEDEF: Eşeği süren osuruğuna katlanır.
```

```text
GİRDİ: senş  seviyor muusn?
MODEL: senş  seviyor muusn?
HEDEF: Seni seviyor musun?
```

```text
GİRDİ: Yarin aksam sama annlatıyoru?z.
MODEL: Yarin aksam sama annlatıyoru?z.
HEDEF: Yarın akşam sana anlatıyoruz.
```

```text
GİRDİ: Ben onu beklerken, evimi ona kabbbule haz irlrken olmustu.
MODEL: Ben onu beklerken, evimi ona kabbbule haz irlrken olmustu.
HEDEF: Ben onu beklerken, evimi ona kabule hazırlarken ölmüştü.
```

```text
GİRDİ: ne ldu, iyiisin?
MODEL: ne ldu, iyiisin?
HEDEF: Ne oldu, iyi misin?
```

```text
GİRDİ: BBunu neden ypatttigımi bilmiyorum.
MODEL: BBunu neden ypatttigımi bilmiyorum.
HEDEF: Bunu neden yaptığımı bilmiyorum.
```

```text
GİRDİ: Biz  gazeteyi okuyouz ve okuldansonra size uğruyor
MODEL: Biz  gazeteyi okuyouz ve okuldansonra size uğruyor
HEDEF: Biz gazeteyi okuyoruz ve okuldan sonra size uğruyor.
```

```text
GİRDİ: Nihayet şarkiyi bitirdi ve sazi elineaalarak ayaga kalkti
MODEL: Nihayet şarkiyi bitirdi ve sazi elineaalarak ayaga kalkti
HEDEF: Nihayet şarkıyı bitirdi ve sazı eline alarak ayağa kalktı.
```

```text
GİRDİ: Sieihiyacımyok.
MODEL: Sieihiyacımyok.
HEDEF: Size ihtiyacım yok.
```

```text
GİRDİ: Oğleden sonra og retmenmesaji gonderiyo.
MODEL: Oğleden sonra og retmenmesaji gonderiyo.
HEDEF: Öğleden sonra öğretmen mesajı gönderiyor.
```

```text
GİRDİ: C?okuzgünumbaba.
MODEL: C?okuzgünumbaba.
HEDEF: Çok üzgünüm baba.
```

```text
GİRDİ: Pekala,  hxir misiniz?
MODEL: Pekala,  hxir misiniz?
HEDEF: Pekala, hazır mısınız?
```

## Manuel örnekler

```text
GİRDİ: bugün okula gidicem ama hava cok kötü galiba
MODEL: bugün okula gidicem ama hava cok kötü galiba
HEDEF: Bugün okula gideceğim ama hava çok kötü galiba.
```

```text
GİRDİ: yarin arkadaşlarla buluşcaz sonrada sinemaya gidicez
MODEL: yarin arkadaşlarla buluşcaz sonrada sinemaya gidicez
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
MODEL: Ankaraya yarin gidicem.
HEDEF: Ankara'ya yarın gideceğim.
```

```text
GİRDİ: herkez buraya gelsin
MODEL: herkez buraya gelsin
HEDEF: Herkes buraya gelsin.
```

```text
GİRDİ: Beni duyuyormusun?
MODEL: Beni duyuyormusun?
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
MODEL: Cok tesekkur ederim.
HEDEF: Çok teşekkür ederim.
```

```text
GİRDİ: Işık, İstanbul’a yarın gelecek.
MODEL: Işık, İstanbul’a yarın gelecek.
HEDEF: Işık, İstanbul’a yarın gelecek.
```
