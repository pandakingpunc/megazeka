# Megazeka değerlendirmesi

```json
{
  "examples": 640,
  "cer": 0.09288114879315612,
  "wer": 0.3492489270386266,
  "exact_match": 0.2515625,
  "edit_precision": 0.0,
  "edit_recall": 0.0,
  "edit_f1": 0.0,
  "clean_examples": 161,
  "overcorrection": 0.0
}
```

Düzenleme hassasiyeti/duyarlılığı, orijinal karakter konumlarına bağlı Levenshtein işlem kümeleriyle ölçülür.

## Başarılı düzeltmeler

Bu kategoride örnek yok.
## Yanlış düzeltmeler

Bu kategoride örnek yok.
## Kaçırılan düzeltmeler

```text
GİRDİ: NNNe yapıyorsunuz çocuklar?
MODEL: NNNe yapıyorsunuz çocuklar?
HEDEF: Ne yapıyorsunuz çocuklar?
```

```text
GİRDİ: kendisi  de biraz doğruldu.
MODEL: kendisi  de biraz doğruldu.
HEDEF: Kendisi de biraz doğruldu.
```

```text
GİRDİ: Yardımların  için reşekkürler.
MODEL: Yardımların  için reşekkürler.
HEDEF: Yardımların için teşekkürler.
```

```text
GİRDİ: iki yaşlarında kadar bir çocuk salıncakta oturmuş katılırcasına alıyordu.
MODEL: iki yaşlarında kadar bir çocuk salıncakta oturmuş katılırcasına alıyordu.
HEDEF: İki yaşlarında kadar bir çocuk salıncakta oturmuş katılırcasına ağlıyordu.
```

```text
GİRDİ: İki ya şlarında kadar bir çocuk salıncakta oturmuş katılırcasına ağlıyordu.
MODEL: İki ya şlarında kadar bir çocuk salıncakta oturmuş katılırcasına ağlıyordu.
HEDEF: İki yaşlarında kadar bir çocuk salıncakta oturmuş katılırcasına ağlıyordu.
```

```text
GİRDİ: Benimle dalga mı geçiyosun?
MODEL: Benimle dalga mı geçiyosun?
HEDEF: Benimle dalga mı geçiyorsun?
```

```text
GİRDİ: Nereden aklina evvela bu zavallinin ismi glmisti?
MODEL: Nereden aklina evvela bu zavallinin ismi glmisti?
HEDEF: Nereden aklına evvela bu zavallının ismi gelmişti?
```

```text
GİRDİ: gep yazmak istiy orum.
MODEL: gep yazmak istiy orum.
HEDEF: Hep yazmak istiyorum.
```

```text
GİRDİ: B urası da en nihayet bir şehirdi.
MODEL: B urası da en nihayet bir şehirdi.
HEDEF: Burası da en nihayet bir şehirdi.
```

```text
GİRDİ: Omer  bu anda zavalli kıza sahiden a.cidıgini hissetti
MODEL: Omer  bu anda zavalli kıza sahiden a.cidıgini hissetti
HEDEF: Ömer bu anda zavallı kıza sahiden acıdığını hissetti.
```

```text
GİRDİ: küçük satici, o tştrek ve !ince sesiyle bagırıyordu.
MODEL: küçük satici, o tştrek ve !ince sesiyle bagırıyordu.
HEDEF: Küçük satıcı, o titrek ve ince sesiyle bağırıyordu.
```

```text
GİRDİ: Önem.li  değil, gerçekten.
MODEL: Önem.li  değil, gerçekten.
HEDEF: Önemli değil, gerçekten.
```

## Zor örnekler

```text
GİRDİ: Omer  bu anda zavalli kıza sahiden a.cidıgini hissetti
MODEL: Omer  bu anda zavalli kıza sahiden a.cidıgini hissetti
HEDEF: Ömer bu anda zavallı kıza sahiden acıdığını hissetti.
```

```text
GİRDİ: küçük satici, o tştrek ve !ince sesiyle bagırıyordu.
MODEL: küçük satici, o tştrek ve !ince sesiyle bagırıyordu.
HEDEF: Küçük satıcı, o titrek ve ince sesiyle bağırıyordu.
```

```text
GİRDİ: cok  uzgunum baba.
MODEL: cok  uzgunum baba.
HEDEF: Çok üzgünüm baba.
```

```text
GİRDİ: Atın ürleği,yğidin korkağı.
MODEL: Atın ürleği,yğidin korkağı.
HEDEF: Atın ürkeği, yiğidin korkağı.
```

```text
GİRDİ: Bedrinin dizleri dermansizlasmist.i.
MODEL: Bedrinin dizleri dermansizlasmist.i.
HEDEF: Bedri'nin dizleri dermansızlaşmıştı.
```

```text
GİRDİ: Tavuslara, sulunleere bakmaya tenrzzül etmeyen y.abani kus, kanadi kirik bir cullugun, avı oldu.
MODEL: Tavuslara, sulunleere bakmaya tenrzzül etmeyen y.abani kus, kanadi kirik bir cullugun, avı oldu.
HEDEF: Tavuslara, sülünlere bakmaya tenezzül etmeyen yabani kuş, kanadı kırık bir çulluğun, avı oldu.
```

```text
GİRDİ: Ates  etmk icin cobanın görulmesiini bekliyordu.
MODEL: Ates  etmk icin cobanın görulmesiini bekliyordu.
HEDEF: Ateş etmek için çobanın görülmesini bekliyordu.
```

```text
GİRDİ: Diger ressam arkadaslardasizi merak ed iyorlardi.
MODEL: Diger ressam arkadaslardasizi merak ed iyorlardi.
HEDEF: Diğer ressam arkadaşlar da sizi merak ediyorlardı.
```

```text
GİRDİ: dort gün sonra polonya ve romanya uzerinden turkiye'ye dondum
MODEL: dort gün sonra polonya ve romanya uzerinden turkiye'ye dondum
HEDEF: Dört gün sonra, Polonya ve Romanya üzerinden Türkiye'ye döndüm.
```

```text
GİRDİ: Simdi   onun nicin benden evvel seyahate çiktigıni da anlar fibi oluyordum.
MODEL: Simdi   onun nicin benden evvel seyahate çiktigıni da anlar fibi oluyordum.
HEDEF: Şimdi onun niçin benden evvel seyahate çıktığını da anlar gibi oluyordum.
```

```text
GİRDİ: beni rahat bırak? on!
MODEL: beni rahat bırak? on!
HEDEF: Beni rahat bırakın!
```

```text
GİRDİ: ama  biz felsefeyi birakalim da, canin isterse,  yılbaşi gecesi beraber bir yere gidelim.
MODEL: ama  biz felsefeyi birakalim da, canin isterse,  yılbaşi gecesi beraber bir yere gidelim.
HEDEF: Ama biz felsefeyi bırakalım da, canın isterse, yılbaşı gecesi beraber bir yere gidelim.
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
