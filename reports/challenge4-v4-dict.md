# Zorluk kümesi: v4

Tam eşleşme: **75/90 = %83.3**

Gereksiz düzeltme (zaten doğru 25 cümle): **2/25 = %8.0**

| Kategori | Doğru | Toplam | Tam eşleşme |
|---|---:|---:|---:|
| listede | 29 | 30 | %96.7 |
| liste_dışı | 16 | 25 | %64.0 |
| koruma | 23 | 25 | %92.0 |
| karışık | 7 | 10 | %70.0 |

## Başarısızlıklar (15)

```text
[listede]
GİRDİ: Pazar günleri geç kavaltı ederiz.
MODEL: Pazar günleri geç kavaltı ederiz.
HEDEF: Pazar günleri geç kahvaltı ederiz.
```

```text
[liste_dışı]
GİRDİ: Kışlıkları gardroba yerleştirdim.
MODEL: Kışlıkları gardroba yerleştirdim.
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
GİRDİ: Binanın asensörü yine arızalanmış.
MODEL: Binanın sensörü yine arızalanmış.
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
GİRDİ: Ustanın tafsiyesine uyup parçayı değiştirdik.
MODEL: Ustanın tasfiyesine uyup parçayı değiştirdik.
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
GİRDİ: Tarife iki yüz giram un ekleyin.
MODEL: Tarife iki yüz giram un ekleyin.
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
GİRDİ: Yazarın anlatım sitili çok akıcı.
MODEL: Yazarın anlatım sitili çok akıcı.
HEDEF: Yazarın anlatım stili çok akıcı.
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
[karışık]
GİRDİ: Müsafirler için bir kaç şişe meyve suyu aldım.
MODEL: Müsafirler için birkaç şişe meyve suyu aldım.
HEDEF: Misafirler için birkaç şişe meyve suyu aldım.
```

```text
[karışık]
GİRDİ: Apartımanın asensörü hakında yöneticiyle konuştum.
MODEL: Apartmanın sensörü hakkında yöneticiyle konuştum.
HEDEF: Apartmanın asansörü hakkında yöneticiyle konuştum.
```

```text
[karışık]
GİRDİ: Seyehat öncesi herşeyi iki kez kontrol ettim.
MODEL: Seyehat öncesi her şeyi iki kez kontrol ettim.
HEDEF: Seyahat öncesi her şeyi iki kez kontrol ettim.
```
