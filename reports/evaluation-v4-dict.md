# Megazeka değerlendirmesi

```json
{
  "examples": 1128,
  "cer": 0.010986117759693633,
  "wer": 0.05158998646820027,
  "exact_match": 0.8156028368794326,
  "edit_precision": 0.928608115048793,
  "edit_recall": 0.898831717623664,
  "edit_f1": 0.9134773272704307,
  "clean_examples": 282,
  "overcorrection": 0.028368794326241134
}
```

## Denetlenmiş hedefler

```json
{
  "examples": 1116,
  "cer": 0.011523625843780135,
  "wer": 0.05320600272851296,
  "exact_match": 0.807347670250896,
  "edit_precision": 0.9325025960539979,
  "edit_recall": 0.8908730158730159,
  "edit_f1": 0.9112125824454591,
  "clean_examples": 269,
  "overcorrection": 0.01486988847583643
}
```

## Alt küme: common_voice (640 çift)

```json
{
  "filtreli": {
    "examples": 640,
    "cer": 0.014245340666055607,
    "wer": 0.06625536480686696,
    "exact_match": 0.7453125,
    "edit_precision": 0.9082202713487629,
    "edit_recall": 0.8696981276270539,
    "edit_f1": 0.888541869998048,
    "clean_examples": 160,
    "overcorrection": 0.05
  },
  "ham": {
    "examples": 640,
    "cer": 0.013825236785823404,
    "wer": 0.06840128755364806,
    "exact_match": 0.725,
    "edit_precision": 0.9048183254344392,
    "edit_recall": 0.8754298815437523,
    "edit_f1": 0.8898815303942513,
    "clean_examples": 160,
    "overcorrection": 0.0375
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
    "cer": 0.005514234419081816,
    "wer": 0.026556776556776556,
    "exact_match": 0.9077868852459017,
    "edit_precision": 0.9654178674351584,
    "edit_recall": 0.9530583214793741,
    "edit_f1": 0.9591982820329277,
    "clean_examples": 122,
    "overcorrection": 0.0
  },
  "ham": {
    "examples": 488,
    "cer": 0.00602718645806617,
    "wer": 0.030677655677655676,
    "exact_match": 0.8954918032786885,
    "edit_precision": 0.9623188405797102,
    "edit_recall": 0.9445234708392604,
    "edit_f1": 0.953338119167265,
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
GİRDİ: Aşk ağlatırr, dert söyletir.
MODEL: Aşk ağlatır, dert söyletir.
HEDEF: Aşk ağlatır, dert söyletir.
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
GİRDİ: Atın ürkeği, yiğidin korkağı.
MODEL: Atın ürkeki, yiğidin korkakı.
HEDEF: Atın ürkeği, yiğidin korkağı.
```

```text
GİRDİ: Hani nerdeyse harman yerlerinden duyulacaktı.
MODEL: Hani neredeyse harman yerlerinden duyulacaktı.
HEDEF: Hani nerdeyse harman yerlerinden duyulacaktı.
```

```text
GİRDİ: Eskiye itibar olsaydı bitpazarına nur yağardı.
MODEL: Eskiye itibar olsaydı bir pazarına nur yağardı.
HEDEF: Eskiye itibar olsaydı bitpazarına nur yağardı.
```

```text
GİRDİ: Sonra ortalığı yıldırmış olduğum için, şurda burda saklı karıları bensiz alıp getiremezlerdi.
MODEL: Sonra ortalığı yıldırmış olduğum için, şurda burada saklı karıları bensiz alıp getirmezlerdi.
HEDEF: Sonra ortalığı yıldırmış olduğum için, şurda burda saklı karıları bensiz alıp getiremezlerdi.
```

```text
GİRDİ: Yeni bir vaka, Çakıcı'nın halk arasındaki mevkiini daha ziyade sağlamlaştırmıştı.
MODEL: Yeni bir vaka, Çakıcı'nın halk arasındaki mevkisini daha ziyade sağlamlaştırmıştı.
HEDEF: Yeni bir vaka, Çakıcı'nın halk arasındaki mevkiini daha ziyade sağlamlaştırmıştı.
```

```text
GİRDİ: Ben yukarıda sedire uzanırım!
MODEL: Ben yukarıda şedire uzanırım!
HEDEF: Ben yukarıda sedire uzanırım!
```

```text
GİRDİ: Siyah eteklikli, topukları yırtık siyah çoraplı, şipidik terlikli şişman bir kadın yerleri siliyordu.
MODEL: Siyah eteklikli, topukları yırtık siyah çoraplı, şipindik terlikli şişman bir kadın yerleri siliyordu.
HEDEF: Siyah eteklikli, topukları yırtık siyah çoraplı, şipidik terlikli şişman bir kadın yerleri siliyordu.
```

## Kaçırılan düzeltmeler

```text
GİRDİ: Hadise, umumiyet itibariyle, zannedildiği kadar korkunç bir şey eğildi.
MODEL: Hadise, umumiyet itibariyle, zannedildiği kadar korkunç bir şey eğildi.
HEDEF: Hadise, umumiyet itibariyle, zannedildiği kadar korkunç bir şey değildi.
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
GİRDİ: Birkaç adım daha atınca yanına feldi.
MODEL: Birkaç adım daha atınca yanına feldi.
HEDEF: Birkaç adım daha atınca yanına geldi.
```

```text
GİRDİ: Ağız büzülür, göz süzülür, ilşe burun, ille burun.
MODEL: Ağız büzülür, göz süzülür, ilşe burun, ille burun.
HEDEF: Ağız büzülür, göz süzülür, ille burun, ille burun.
```

```text
GİRDİ: Ekim bin dokuz yüz otuz bes.
MODEL: Ekim bin dokuz yüz otuz bes.
HEDEF: Ekim bin dokuz yüz otuz beş.
```

```text
GİRDİ: Dört gün sonra, Polonya ve Romanya üzerinden Türkye'ye döndüm.
MODEL: Dört gün sonra, Polonya ve Romanya üzerinden Türkye'ye döndüm.
HEDEF: Dört gün sonra, Polonya ve Romanya üzerinden Türkiye'ye döndüm.
```

## Zor örnekler

```text
GİRDİ: wşeği  suren osuruguna katşanir.
MODEL: Eşeği süren osuruğuna katılanır.
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
MODEL: Sizi ihtiyacım yok.
HEDEF: Size ihtiyacım yok.
```

```text
GİRDİ: C?okuzgünumbaba.
MODEL: Çokuz günüm baba.
HEDEF: Çok üzgünüm baba.
```

```text
GİRDİ: Pekala,  hxir misiniz?
MODEL: Pekala, hiç misiniz?
HEDEF: Pekala, hazır mısınız?
```

```text
GİRDİ: Bir kere cikayım fa sonrasş kolay
MODEL: Bir kere çıkayım, fakat sonrası kolay.
HEDEF: Bir kere çıkayım da, sonrası kolay.
```

```text
GİRDİ: Ben yukarda sedire uzanurım!
MODEL: Ben yukarda şedire uzanırım!
HEDEF: Ben yukarıda sedire uzanırım!
```

```text
GİRDİ: kusura bakma unut musum
MODEL: Kusura bakma unut musun?
HEDEF: Kusura bakma, unutmuşum.
```

```text
GİRDİ: Şidi babam deni bulacak sonra sabah kitabıbitirecek
MODEL: Şimdi babam deni bulacak sonra sabah kitabı bitirecek.
HEDEF: Şimdi babam seni bulacak, sonra sabah kitabı bitirecek.
```

```text
GİRDİ: evet, hakkibiz var, fakat artık benim tavsiyelerimi dinlemiyo.
MODEL: Evet, hakkı biz var, fakat artık benim tavsiyelerimi dinlemiyor.
HEDEF: Evet, hakkınız var, fakat artık benim tavsiyelerimi dinlemiyor.
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
