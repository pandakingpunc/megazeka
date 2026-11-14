# Zorluk kümesi: v3.5

Tam eşleşme: **60/90 = %66.7**

Gereksiz düzeltme (zaten doğru 25 cümle): **3/25 = %12.0**

| Kategori | Doğru | Toplam | Tam eşleşme |
|---|---:|---:|---:|
| listede | 29 | 30 | %96.7 |
| liste_dışı | 4 | 25 | %16.0 |
| koruma | 22 | 25 | %88.0 |
| karışık | 5 | 10 | %50.0 |

## Başarısızlıklar (30)

```text
[listede]
GİRDİ: Yarınki matamatik sınavına çalışıyorum.
MODEL: Yarınki maatematik sınavına çalışıyorum.
HEDEF: Yarınki matematik sınavına çalışıyorum.
```

```text
[liste_dışı]
GİRDİ: Babam geçen ay küçük bir ameliyet geçirdi.
MODEL: Babam geçen ay küçük bir ameliyet geçirdi.
HEDEF: Babam geçen ay küçük bir ameliyat geçirdi.
```

```text
[liste_dışı]
GİRDİ: Uzun bir seyehatten yeni döndük.
MODEL: Uzun bir şeyehatten yeni döndük.
HEDEF: Uzun bir seyahatten yeni döndük.
```

```text
[liste_dışı]
GİRDİ: Akşam yemeğine müsafir gelecek.
MODEL: Akşam yemeğine müsaafir gelecek.
HEDEF: Akşam yemeğine misafir gelecek.
```

```text
[liste_dışı]
GİRDİ: Vidayı sıkmak için tornovida lazım.
MODEL: Vidayı sıkmak için tornovida lazım.
HEDEF: Vidayı sıkmak için tornavida lazım.
```

```text
[liste_dışı]
GİRDİ: Kışlıkları gardroba yerleştirdim.
MODEL: Kışlıkları garderoba yerleştirdim.
HEDEF: Kışlıkları gardıroba yerleştirdim.
```

```text
[liste_dışı]
GİRDİ: Çamaşır deterjeni bitmek üzere.
MODEL: Çamaşır deterjeni bitmek üzere.
HEDEF: Çamaşır deterjanı bitmek üzere.
```

```text
[liste_dışı]
GİRDİ: Fırtına yüzünden elektirikler kesildi.
MODEL: Fırtına yüzünden elektirikler kesildi.
HEDEF: Fırtına yüzünden elektrikler kesildi.
```

```text
[liste_dışı]
GİRDİ: Mağaza yeni bir indirim kanpanyası başlattı.
MODEL: Mağaza yeni bir indirim kanpanyası başlattı.
HEDEF: Mağaza yeni bir indirim kampanyası başlattı.
```

```text
[liste_dışı]
GİRDİ: Bizim apartımanın kapısı boyanıyor.
MODEL: Bizim apartımanın kapısı boyanıyor.
HEDEF: Bizim apartmanın kapısı boyanıyor.
```

```text
[liste_dışı]
GİRDİ: Binanın asensörü yine arızalanmış.
MODEL: Binanın asensörü yine arızalanmış.
HEDEF: Binanın asansörü yine arızalanmış.
```

```text
[liste_dışı]
GİRDİ: Kurye motorsikletini kapının önüne bıraktı.
MODEL: Kurye motorsikletini kapının önüne bıraktı.
HEDEF: Kurye motosikletini kapının önüne bıraktı.
```

```text
[liste_dışı]
GİRDİ: Hafta sonu sahilde bisklet sürdük.
MODEL: Hafta sonu sahilde biskelet sürdük.
HEDEF: Hafta sonu sahilde bisiklet sürdük.
```

```text
[liste_dışı]
GİRDİ: Bu işte on yıllık tecürbesi var.
MODEL: Bu işte on yıllık tecürbesi var.
HEDEF: Bu işte on yıllık tecrübesi var.
```

```text
[liste_dışı]
GİRDİ: Ustanın tafsiyesine uyup parçayı değiştirdik.
MODEL: Ustanın tafsiyesine uyup parçayı değiştirdik.
HEDEF: Ustanın tavsiyesine uyup parçayı değiştirdik.
```

```text
[liste_dışı]
GİRDİ: Mesala bu örnek konuyu iyi açıklıyor.
MODEL: Mesala bu örnek konuyu iyi açıklıyor.
HEDEF: Mesela bu örnek konuyu iyi açıklıyor.
```

```text
[liste_dışı]
GİRDİ: Dün çok enterasan bir belgesel izledim.
MODEL: Dün çok interasan bir belgesel izledim.
HEDEF: Dün çok enteresan bir belgesel izledim.
```

```text
[liste_dışı]
GİRDİ: Kardeşim inşaat mühendizi olmak istiyor.
MODEL: Kardeşim inşaat mühendizi olmak istiyor.
HEDEF: Kardeşim inşaat mühendisi olmak istiyor.
```

```text
[liste_dışı]
GİRDİ: Tarife iki yüz giram un ekleyin.
MODEL: Tarife iki yüz giramun ekleyin.
HEDEF: Tarife iki yüz gram un ekleyin.
```

```text
[liste_dışı]
GİRDİ: Güneşe çıkmadan önce kirem sürdüm.
MODEL: Güneşe çıkmadan önce kirem sürdüm.
HEDEF: Güneşe çıkmadan önce krem sürdüm.
```

```text
[liste_dışı]
GİRDİ: Yağmur başlayınca şemşiyemi açtım.
MODEL: Yağmur başlayınca şemşiyemi açtım.
HEDEF: Yağmur başlayınca şemsiyemi açtım.
```

```text
[liste_dışı]
GİRDİ: Bayramda bütün akarabalar bir araya geldi.
MODEL: Bayramda bütün akarabalar bir araya geldi.
HEDEF: Bayramda bütün akrabalar bir araya geldi.
```

```text
[koruma]
GİRDİ: Bu günlerde hava çok değişken.
MODEL: Bugünlerde hava çok değişken.
HEDEF: Bu günlerde hava çok değişken.
```

```text
[koruma]
GİRDİ: Bir kaç, bir yakalan, oyunun kuralı bu.
MODEL: Birkaç, bir yakalan, oyunun kuralı bu.
HEDEF: Bir kaç, bir yakalan, oyunun kuralı bu.
```

```text
[koruma]
GİRDİ: Hiç bu kadar kalabalık bir konser görmemiştim.
MODEL: Hiçbu kadar kalabalık bir konser görmemiştim.
HEDEF: Hiç bu kadar kalabalık bir konser görmemiştim.
```

```text
[karışık]
GİRDİ: Müsafirler için bir kaç şişe meyve suyu aldım.
MODEL: Müsafirler için birkaç şişe meyve suyu aldım.
HEDEF: Misafirler için birkaç şişe meyve suyu aldım.
```

```text
[karışık]
GİRDİ: Apartımanın asensörü hakında yöneticiyle konuştum.
MODEL: Apartımanın asensörü hakkında yöneticiyle konuştum.
HEDEF: Apartmanın asansörü hakkında yöneticiyle konuştum.
```

```text
[karışık]
GİRDİ: Seyehat öncesi herşeyi iki kez kontrol ettim.
MODEL: Seyehat öncesi her şeyi iki kez kontrol ettim.
HEDEF: Seyahat öncesi her şeyi iki kez kontrol ettim.
```

```text
[karışık]
GİRDİ: Kavaltıdan sonra bisklet turuna çıkalım.
MODEL: Kahvaltıdan sonra bisket turuna çıkalım.
HEDEF: Kahvaltıdan sonra bisiklet turuna çıkalım.
```

```text
[karışık]
GİRDİ: Elektirik faturası hakında hiç bir bilgi verilmedi.
MODEL: Elektirik faturası hakkında hiçbir bilgi verilmedi.
HEDEF: Elektrik faturası hakkında hiçbir bilgi verilmedi.
```
