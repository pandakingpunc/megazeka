# Megazeka değerlendirmesi

```json
{
  "examples": 640,
  "cer": 0.0510617170791323,
  "wer": 0.13277896995708155,
  "exact_match": 0.60625,
  "edit_precision": 0.8691176470588236,
  "edit_recall": 0.48601973684210525,
  "edit_f1": 0.6234177215189873,
  "clean_examples": 161,
  "overcorrection": 0.024844720496894408
}
```

Düzenleme hassasiyeti/duyarlılığı, orijinal karakter konumlarına bağlı Levenshtein işlem kümeleriyle ölçülür.

## Başarılı düzeltmeler

```text
GİRDİ: NNNe yapıyorsunuz çocuklar?
MODEL: Ne yapıyorsunuz çocuklar?
HEDEF: Ne yapıyorsunuz çocuklar?
```

```text
GİRDİ: kendisi  de biraz doğruldu.
MODEL: Kendisi de biraz doğruldu.
HEDEF: Kendisi de biraz doğruldu.
```

```text
GİRDİ: İki ya şlarında kadar bir çocuk salıncakta oturmuş katılırcasına ağlıyordu.
MODEL: İki yaşlarında kadar bir çocuk salıncakta oturmuş katılırcasına ağlıyordu.
HEDEF: İki yaşlarında kadar bir çocuk salıncakta oturmuş katılırcasına ağlıyordu.
```

```text
GİRDİ: Benimle dalga mı geçiyosun?
MODEL: Benimle dalga mı geçiyorsun?
HEDEF: Benimle dalga mı geçiyorsun?
```

```text
GİRDİ: Nereden aklina evvela bu zavallinin ismi glmisti?
MODEL: Nereden aklına evvela bu zavallının ismi gelmişti?
HEDEF: Nereden aklına evvela bu zavallının ismi gelmişti?
```

```text
GİRDİ: Omer  bu anda zavalli kıza sahiden a.cidıgini hissetti
MODEL: Ömer bu anda zavallı kıza sahiden acıdığını hissetti.
HEDEF: Ömer bu anda zavallı kıza sahiden acıdığını hissetti.
```

```text
GİRDİ: Önem.li  değil, gerçekten.
MODEL: Önemli değil, gerçekten.
HEDEF: Önemli değil, gerçekten.
```

```text
GİRDİ: Ateş etmek için çobanın görülmesini bekliyordu
MODEL: Ateş etmek için çobanın görülmesini bekliyordu.
HEDEF: Ateş etmek için çobanın görülmesini bekliyordu.
```

```text
GİRDİ: bir kere çıkayım da, sonrası k!olay.
MODEL: Bir kere çıkayım da, sonrası kolay.
HEDEF: Bir kere çıkayım da, sonrası kolay.
```

```text
GİRDİ: ondan  sonra bekir'e döndüm, ellerimi uzattım.
MODEL: Ondan sonra Bekir'e döndüm, ellerimi uzattım.
HEDEF: Ondan sonra Bekir'e döndüm, ellerimi uzattım.
```

```text
GİRDİ: Seniyarın ararim.
MODEL: Seni yarın ararım.
HEDEF: Seni yarın ararım.
```

```text
GİRDİ: Hiçbir yere gitmeyecegim.
MODEL: Hiçbir yere gitmeyeceğim.
HEDEF: Hiçbir yere gitmeyeceğim.
```

## Yanlış düzeltmeler

```text
GİRDİ: Eskiye itibar olsaydı bitpazarına nur yağardı.
MODEL: Eskiye itibar olsaydı bit pazarına nur yağardı.
HEDEF: Eskiye itibar olsaydı bitpazarına nur yağardı.
```

```text
GİRDİ: İyi etmediniz, bizim kaptan asabidir, şakadan hazzetmez.
MODEL: İyi etmediniz, bizim kaptan asabıdır, şakadan hazzetmez.
HEDEF: İyi etmediniz, bizim kaptan asabidir, şakadan hazzetmez.
```

```text
GİRDİ: Tavuslara, sülünlere bakmaya tenezzül etmeyen yabani kuş, kanadı kırık bir çulluğun, avı oldu.
MODEL: Tavuslara, sülünlere bakmaya tenezzül etmeyen yabanı kuş, kanadı kırık bir çulluğun, avı oldu.
HEDEF: Tavuslara, sülünlere bakmaya tenezzül etmeyen yabani kuş, kanadı kırık bir çulluğun, avı oldu.
```

```text
GİRDİ: Islak kumlar ayaklarımızın altında gıcırdıyordu.
MODEL: İslak kumlar ayaklarımızın altında gıcırdıyordu.
HEDEF: Islak kumlar ayaklarımızın altında gıcırdıyordu.
```

## Kaçırılan düzeltmeler

```text
GİRDİ: Onu, her şeye rağmen, bu çeşit bir mahluk addede mezdim.
MODEL: Onu, her şeye rağmen, bu çeşit bir mahluk addede mezdim.
HEDEF: Onu, her şeye rağmen, bu çeşit bir mahluk addedemezdim.
```

```text
GİRDİ: oNE MLI DEGIL GERÇEKTEN
MODEL: oNE MLI DEGIL GERÇEKTEN
HEDEF: Önemli değil, gerçekten.
```

```text
GİRDİ: bIR KERE HEYBETLI DELIKANLIYDI
MODEL: bIR KERE HEYBETLI DELIKANLIYDI
HEDEF: Bir kere heybetli delikanlıydı!
```

```text
GİRDİ: Bütün akraba gelmişe benziyorsu.
MODEL: Bütün akraba gelmişe benziyorsu.
HEDEF: Bütün akraba gelmişe benziyordu.
```

```text
GİRDİ: bENEDN ISTEDIGIN HER SE?YI YAPTIM.
MODEL: bENEDN ISTEDIGIN HER SE?YI YAPTIM.
HEDEF: Benden istediğin her şeyi yaptım.
```

```text
GİRDİ: Pantolon cebinde bir hayli arandıktan sonra parayı verdi, polislerin kolun da, çıkıp gitti.
MODEL: Pantolon cebinde bir hayli arandıktan sonra parayı verdi, polislerin kolun da, çıkıp gitti.
HEDEF: Pantolon cebinde bir hayli arandıktan sonra parayı verdi, polislerin kolunda, çıkıp gitti.
```

```text
GİRDİ: RcET, BUTARAFTAN.
MODEL: RcET, BUTARAFTAN.
HEDEF: Evet, bu taraftan.
```

```text
GİRDİ: bIR HAYLI YÜRÜDÜKTEN SONRA ?YOL BIRDENBIRE DENIZ KENARINI TAKIBE BAŞLADI.
MODEL: bIR HAYLI YÜRÜDÜKTEN SONRA ?YOL BIRDENBIRE DENIZ KENARINI TAKIBE BAŞLADI.
HEDEF: Bir hayli yürüdükten sonra yol birdenbire deniz kenarını takibe başladı.
```

```text
GİRDİ: Konuşmak nietiyle çıktıkları halde ikisi de kendi âlemlerine dalmışlardı.
MODEL: Konuşmak nietiyle çıktıkları halde ikisi de kendi âlemlerine dalmışlardı.
HEDEF: Konuşmak niyetiyle çıktıkları halde ikisi de kendi âlemlerine dalmışlardı.
```

```text
GİRDİ: hICBIR YERE GITMEYECEĞI M
MODEL: hICBIR YERE GITMEYECEĞI M
HEDEF: Hiçbir yere gitmeyeceğim.
```

```text
GİRDİ: Bir şey er ayarlarız.
MODEL: Bir şey er ayarlarız.
HEDEF: Bir şeyler ayarlarız.
```

```text
GİRDİ: Ben onu bekleren, evimi ona kabule hazırlarken ölmüştü.
MODEL: Ben onu bekleren, evimi ona kabule hazırlarken ölmüştü.
HEDEF: Ben onu beklerken, evimi ona kabule hazırlarken ölmüştü.
```

## Zor örnekler

```text
GİRDİ: küçük satici, o tştrek ve !ince sesiyle bagırıyordu.
MODEL: Küçük satici, o terek ve ince sesiyle bağırıyordu.
HEDEF: Küçük satıcı, o titrek ve ince sesiyle bağırıyordu.
```

```text
GİRDİ: cok  uzgunum baba.
MODEL: Çok uzgunum baba.
HEDEF: Çok üzgünüm baba.
```

```text
GİRDİ: Atın ürleği,yğidin korkağı.
MODEL: Atın ürleğiyi yıdın korkağı.
HEDEF: Atın ürkeği, yiğidin korkağı.
```

```text
GİRDİ: Bedrinin dizleri dermansizlasmist.i.
MODEL: Bedrinin dizleri dermansızlaşmıştı.
HEDEF: Bedri'nin dizleri dermansızlaşmıştı.
```

```text
GİRDİ: Tavuslara, sulunleere bakmaya tenrzzül etmeyen y.abani kus, kanadi kirik bir cullugun, avı oldu.
MODEL: Tavuşlara, sulunlere bakmaya tenrül etmeyen yabanı kuş, kanadı kırık bir çulluğun, avı oldu.
HEDEF: Tavuslara, sülünlere bakmaya tenezzül etmeyen yabani kuş, kanadı kırık bir çulluğun, avı oldu.
```

```text
GİRDİ: Diger ressam arkadaslardasizi merak ed iyorlardi.
MODEL: Diğer ressam arkadaşlarda sizi merak ediyorlardı.
HEDEF: Diğer ressam arkadaşlar da sizi merak ediyorlardı.
```

```text
GİRDİ: dort gün sonra polonya ve romanya uzerinden turkiye'ye dondum
MODEL: Dort gün sonra polonya ve romanya üzerinden Türkiye'ye döndüm.
HEDEF: Dört gün sonra, Polonya ve Romanya üzerinden Türkiye'ye döndüm.
```

```text
GİRDİ: Simdi   onun nicin benden evvel seyahate çiktigıni da anlar fibi oluyordum.
MODEL: Simdi onun niçin benden evvel seyahate çıktığını da anlar fibi oluyordum.
HEDEF: Şimdi onun niçin benden evvel seyahate çıktığını da anlar gibi oluyordum.
```

```text
GİRDİ: beni rahat bırak? on!
MODEL: Beni rahat bırak? On!
HEDEF: Beni rahat bırakın!
```

```text
GİRDİ: Ben de .szi bekllitordum.
MODEL: Ben de sizi beklitordum.
HEDEF: Ben de sizi bekliyordum.
```

```text
GİRDİ: oNE MLI DEGIL GERÇEKTEN
MODEL: oNE MLI DEGIL GERÇEKTEN
HEDEF: Önemli değil, gerçekten.
```

```text
GİRDİ: Her iey incelikten iinsan kablıktan kırılır
MODEL: Her iyi incelikten insan kablıktan kırılır.
HEDEF: Her şey incelikten insan kabalıktan kırılır.
```

## Manuel örnekler

```text
GİRDİ: bugün okula gidicem ama hava cok kötü galiba
MODEL: Bugün okula gidicem ama hava çok kötü galiba.
HEDEF: Bugün okula gideceğim ama hava çok kötü galiba.
```

```text
GİRDİ: yarin arkadaşlarla buluşcaz sonrada sinemaya gidicez
MODEL: Yarın arkadaşlarla buluşcaz sonrada sinemaya gidicez.
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
MODEL: Ankaraya yarın gidicem.
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
MODEL: İşık, İstanbul’a yarın gelecek.
HEDEF: Işık, İstanbul’a yarın gelecek.
```
