# Zorluk kümesi: v4

Tam eşleşme: **44/70 = %62.9**

Gereksiz düzeltme (zaten doğru 30 cümle): **6/30 = %20.0**

| Kategori | Doğru | Toplam | Tam eşleşme |
|---|---:|---:|---:|
| öğretilmiş | 11 | 11 | %100.0 |
| yeni_sözcük | 7 | 26 | %26.9 |
| koruma | 24 | 30 | %80.0 |
| karışık | 2 | 3 | %66.7 |

## Başarısızlıklar (26)

```text
[yeni_sözcük]
GİRDİ: Salataya biraz maydonos doğradım.
MODEL: Salataya biraz maydanos doğradım.
HEDEF: Salataya biraz maydanoz doğradım.
```

```text
[yeni_sözcük]
GİRDİ: Çocuklar bahçede kelebeg kovalıyor.
MODEL: Çocuklar bahçede kelebeğ kovalıyor.
HEDEF: Çocuklar bahçede kelebek kovalıyor.
```

```text
[yeni_sözcük]
GİRDİ: Doktor iki hafta istirahat verdi ve reçete yazdı, eczaneden ilaçları aldım ama termometire almayı unuttum.
MODEL: Doktor iki hafta istirahat verdi ve reçete yazdı, eczaneden ilaçları aldım ama termometire almayı unuttum.
HEDEF: Doktor iki hafta istirahat verdi ve reçete yazdı, eczaneden ilaçları aldım ama termometre almayı unuttum.
```

```text
[yeni_sözcük]
GİRDİ: Yeni aldığımız buzdolabı çok sessiz çalışıyor ama çamaşır makinesi gürlütülü.
MODEL: Yeni aldığımız buzdolabı çok sessiz çalışıyor ama çamaşır makinesi gürlütülü.
HEDEF: Yeni aldığımız buzdolabı çok sessiz çalışıyor ama çamaşır makinesi gürültülü.
```

```text
[yeni_sözcük]
GİRDİ: Sınavdan önce kütüphanede sesizce çalıştık.
MODEL: Sınavdan önce kütüphanede sesizce çalıştık.
HEDEF: Sınavdan önce kütüphanede sessizce çalıştık.
```

```text
[yeni_sözcük]
GİRDİ: Öğretmen tahtaya bir üçgen ve bir dikdörgen çizdi.
MODEL: Öğretmen tahtaya bir üçgen ve bir dikdörgen çizdi.
HEDEF: Öğretmen tahtaya bir üçgen ve bir dikdörtgen çizdi.
```

```text
[yeni_sözcük]
GİRDİ: Dedem her sabah gazatesini okur.
MODEL: Dedem her sabah gazatesini okur.
HEDEF: Dedem her sabah gazetesini okur.
```

```text
[yeni_sözcük]
GİRDİ: Yolda bir kaplunbağa gördük.
MODEL: Yolda bir kaplunbağa gördük.
HEDEF: Yolda bir kaplumbağa gördük.
```

```text
[yeni_sözcük]
GİRDİ: Bu filmin senoryosu çok zayıf.
MODEL: Bu filmin senoryosu çok zayıf.
HEDEF: Bu filmin senaryosu çok zayıf.
```

```text
[yeni_sözcük]
GİRDİ: Tiyatro oyununun pirovası gece yarısına kadar sürdü.
MODEL: Tiyatro oyununun pirovası gece yarısına kadar sürdü.
HEDEF: Tiyatro oyununun provası gece yarısına kadar sürdü.
```

```text
[yeni_sözcük]
GİRDİ: Konserde orkestıra harika çaldı.
MODEL: Konserde orkestira harika çaldı.
HEDEF: Konserde orkestra harika çaldı.
```

```text
[koruma]
GİRDİ: Dosyayı Whatsapp'tan gönderdim.
MODEL: Dosyayı Whatsap'tan gönderdim.
HEDEF: Dosyayı Whatsapp'tan gönderdim.
```

```text
[koruma]
GİRDİ: Akşam Netflix'te bir dizi izledik.
MODEL: Akşam Netfliz'te bir dizi izledik.
HEDEF: Akşam Netflix'te bir dizi izledik.
```

```text
[koruma]
GİRDİ: Havalimanında pasaportumu kontrol ettiler ve bagajımı teslim aldım, sonra otobüs terminaline gittim.
MODEL: Havalimanında pasaportumu kontrol ettiler ve bağajımı teslim aldım, sonra otobüs terminaline gittim.
HEDEF: Havalimanında pasaportumu kontrol ettiler ve bagajımı teslim aldım, sonra otobüs terminaline gittim.
```

```text
[yeni_sözcük]
GİRDİ: Otelin resepsyonunda uzun süre bekledik.
MODEL: Otelin resepsyonunda uzun süre bekledik.
HEDEF: Otelin resepsiyonunda uzun süre bekledik.
```

```text
[yeni_sözcük]
GİRDİ: Tatlı olarak sütlaç yerine profitörol aldık.
MODEL: Tatlı olarak sütlaç yerine profitörol aldık.
HEDEF: Tatlı olarak sütlaç yerine profiterol aldık.
```

```text
[yeni_sözcük]
GİRDİ: Kahveme iki kaşık şekker attım.
MODEL: Kahveme iki kaşık şekker attım.
HEDEF: Kahveme iki kaşık şeker attım.
```

```text
[yeni_sözcük]
GİRDİ: Dişçi dolguyu yaptıktan sonra anastezi geçti.
MODEL: Dişçi dolguyu yaptıktan sonra anastezi geçti.
HEDEF: Dişçi dolguyu yaptıktan sonra anestezi geçti.
```

```text
[yeni_sözcük]
GİRDİ: Yağmurdan sonra gökkuşagı çıktı.
MODEL: Yağmurdan sonra gökküşağı çıktı.
HEDEF: Yağmurdan sonra gökkuşağı çıktı.
```

```text
[koruma]
GİRDİ: Toplantıya Gökçe Hanım ve Tolga Bey de katılacak.
MODEL: Toplantıya Gökçe Hanım ve Tolga Bey'de katılacak.
HEDEF: Toplantıya Gökçe Hanım ve Tolga Bey de katılacak.
```

```text
[yeni_sözcük]
GİRDİ: Muhasebeci faturaları tek tek kontorol etti.
MODEL: Muhasebeci faturaları tek tek kontorol etti.
HEDEF: Muhasebeci faturaları tek tek kontrol etti.
```

```text
[yeni_sözcük]
GİRDİ: Maaşlar bu ay geçikmeli yatacakmış.
MODEL: Maşlar bu ay geçikmeli yatacakmış.
HEDEF: Maaşlar bu ay gecikmeli yatacakmış.
```

```text
[koruma]
GİRDİ: Abi bu oyun acayip sarıyor ya.
MODEL: Abi bu oyun acayıp sarıyor ya.
HEDEF: Abi bu oyun acayip sarıyor ya.
```

```text
[koruma]
GİRDİ: Kanka akşam halı sahaya geliyon mu?
MODEL: Kanka akşam halı sahaya geliyorsun mu?
HEDEF: Kanka akşam halı sahaya geliyon mu?
```

```text
[yeni_sözcük]
GİRDİ: Trafik yüzünden randevüye geç kaldım.
MODEL: Trafik yüzünden randevüye geç kaldım.
HEDEF: Trafik yüzünden randevuya geç kaldım.
```

```text
[karışık]
GİRDİ: Rezarvasyon için otelin resepsyonunu aradım.
MODEL: Rezervasyon için otelin resepsyonunu aradım.
HEDEF: Rezervasyon için otelin resepsiyonunu aradım.
```
