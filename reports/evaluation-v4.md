# Megazeka değerlendirmesi

```json
{
  "examples": 1128,
  "cer": 0.011823839157491623,
  "wer": 0.05666441136671177,
  "exact_match": 0.7934397163120568,
  "edit_precision": 0.9282184655396619,
  "edit_recall": 0.8871488938603033,
  "edit_f1": 0.9072191154041689,
  "clean_examples": 282,
  "overcorrection": 0.02127659574468085
}
```

## Denetlenmiş hedefler

```json
{
  "examples": 1116,
  "cer": 0.012319189971070395,
  "wer": 0.05832196452933151,
  "exact_match": 0.7840501792114696,
  "edit_precision": 0.9324217722850381,
  "edit_recall": 0.8794642857142857,
  "edit_f1": 0.9051691129546904,
  "clean_examples": 269,
  "overcorrection": 0.007434944237918215
}
```

## Alt küme: common_voice (640 çift)

```json
{
  "filtreli": {
    "examples": 640,
    "cer": 0.01531469599755576,
    "wer": 0.07188841201716738,
    "exact_match": 0.715625,
    "edit_precision": 0.9083907580056749,
    "edit_recall": 0.8563240351547573,
    "edit_f1": 0.8815892997639655,
    "clean_examples": 160,
    "overcorrection": 0.0375
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
    "cer": 0.005963067453193126,
    "wer": 0.030677655677655676,
    "exact_match": 0.8954918032786885,
    "edit_precision": 0.9637155297532656,
    "edit_recall": 0.9445234708392604,
    "edit_f1": 0.9540229885057471,
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

```text
GİRDİ: Seninle konusmak istiyor.
MODEL: Seninle konuşmak istiyor.
HEDEF: Seninle konuşmak istiyor.
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
GİRDİ: Eskiye itibar olsaydı bitpazarına nur yağardı.
MODEL: Eskiye itibar olsaydı bir pazarına nur yağardı.
HEDEF: Eskiye itibar olsaydı bitpazarına nur yağardı.
```

```text
GİRDİ: Sonra ortalığı yıldırmış olduğum için, şurda burda saklı karıları bensiz alıp getiremezlerdi.
MODEL: Sonra ortalığı yıldırmış olduğum için, şurda burada saklı karıları bensiz alıp getiremezlerdi.
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

## Kaçırılan düzeltmeler

```text
GİRDİ: en  azindan oy,leydi.
MODEL: en  azindan oy,leydi.
HEDEF: En azından öyleydi.
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
GİRDİ: Bedri'nin dizleri dermansızaşmıştı.
MODEL: Bedri'nin dizleri dermansızaşmıştı.
HEDEF: Bedri'nin dizleri dermansızlaşmıştı.
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

## Zor örnekler

```text
GİRDİ: wşeği  suren osuruguna katşanir.
MODEL: Veşeği süren osuruğuna katılanır.
HEDEF: Eşeği süren osuruğuna katlanır.
```

```text
GİRDİ: Yarin aksam sama annlatıyoru?z.
MODEL: Yarın akşam sama anlatıyoruz.
HEDEF: Yarın akşam sana anlatıyoruz.
```

```text
GİRDİ: Ben onu beklerken, evimi ona kabbbule haz irlrken olmustu.
MODEL: Ben onu beklerken, evimi ona kabule hazırlırken olmuştu.
HEDEF: Ben onu beklerken, evimi ona kabule hazırlarken ölmüştü.
```

```text
GİRDİ: ne ldu, iyiisin?
MODEL: Ne oldu, iyisin?
HEDEF: Ne oldu, iyi misin?
```

```text
GİRDİ: Sieihiyacımyok.
MODEL: Sizi ihiyacım yok.
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
MODEL: Ben yukarda şedire uzanurum!
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
GİRDİ: sIMDI ONUN NIÇIN BENDEN EVVEL SEYAHATE CIKTIGINI DA ANLAR GIBI OLUyodum
MODEL: Şimdi onun niçin benden evvel şeyahate çıktığını da anlar gibi oluyordum.
HEDEF: Şimdi onun niçin benden evvel seyahate çıktığını da anlar gibi oluyordum.
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
