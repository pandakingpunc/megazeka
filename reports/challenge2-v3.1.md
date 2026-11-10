# Zorluk kümesi: v3.1b

Tam eşleşme: **46/66 = %69.7**

Gereksiz düzeltme (zaten doğru 16 cümle): **2/16 = %12.5**

| Kategori | Doğru | Toplam | Tam eşleşme |
|---|---:|---:|---:|
| ı_i_isimleri | 5 | 12 | %41.7 |
| yazım_yanlışı | 7 | 14 | %50.0 |
| doğru_kelime_koruma | 13 | 16 | %81.2 |
| noktalama | 5 | 6 | %83.3 |
| sohbet | 8 | 10 | %80.0 |
| doğru_cümle | 8 | 8 | %100.0 |

## Başarısızlıklar (20)

```text
[ı_i_isimleri]
GİRDİ: yarın ispartaya gidiyoruz
MODEL: Yarın İsparta'ya gidiyoruz.
HEDEF: Yarın Isparta'ya gidiyoruz.
```

```text
[ı_i_isimleri]
GİRDİ: izmirden ıspartaya otobüsle gittik
MODEL: İzmir'den İsparta'ya otobüsle gittik.
HEDEF: İzmir'den Isparta'ya otobüsle gittik.
```

```text
[ı_i_isimleri]
GİRDİ: ilgaz bu sabah erken kalktı
MODEL: İlgaz bu sabah erken kalktı.
HEDEF: Ilgaz bu sabah erken kalktı.
```

```text
[ı_i_isimleri]
GİRDİ: Iğdır ve Isparta arasında uçuş yok.
MODEL: Iğdır ve İsparta arasında uçuş yok.
HEDEF: Iğdır ve Isparta arasında uçuş yok.
```

```text
[ı_i_isimleri]
GİRDİ: istanbuldan igdira uçak var mı
MODEL: İstanbul'dan İğdır'a uçak var mı?
HEDEF: İstanbul'dan Iğdır'a uçak var mı?
```

```text
[ı_i_isimleri]
GİRDİ: ısık ile irem sinemaya gitti
MODEL: Isık ile İrem sinemaya gitti.
HEDEF: Işık ile İrem sinemaya gitti.
```

```text
[ı_i_isimleri]
GİRDİ: ilgın bana kitabını verdi
MODEL: İlgin bana kitabını verdi.
HEDEF: Ilgın bana kitabını verdi.
```

```text
[yazım_yanlışı]
GİRDİ: şöförler bugün grevde
MODEL: Şöförler bugün grevde.
HEDEF: Şoförler bugün grevde.
```

```text
[yazım_yanlışı]
GİRDİ: labaratuvar sonuçları yarın çıkacak
MODEL: Labaratuvar sonuçları yarın çıkacak.
HEDEF: Laboratuvar sonuçları yarın çıkacak.
```

```text
[yazım_yanlışı]
GİRDİ: kullanım klavuzunu okudun mu
MODEL: Kullanım kalavuzunu okudun mu?
HEDEF: Kullanım kılavuzunu okudun mu?
```

```text
[yazım_yanlışı]
GİRDİ: sabah traş oldum
MODEL: Sabah taraş oldum.
HEDEF: Sabah tıraş oldum.
```

```text
[yazım_yanlışı]
GİRDİ: telefonun şarzı bitmek üzere
MODEL: Telefonun şarzı bitmek üzere.
HEDEF: Telefonun şarjı bitmek üzere.
```

```text
[yazım_yanlışı]
GİRDİ: yemeğe biraz sarmısak ekle
MODEL: Yemeğe biraz sarmışak ekle.
HEDEF: Yemeğe biraz sarımsak ekle.
```

```text
[yazım_yanlışı]
GİRDİ: kirbit kutusu masanın üstünde
MODEL: Kirbir kutusu masanın üstünde.
HEDEF: Kibrit kutusu masanın üstünde.
```

```text
[doğru_kelime_koruma]
GİRDİ: Ormanda yabani hayvanlar yaşar.
MODEL: Ormanda yabanı hayvanlar yaşar.
HEDEF: Ormanda yabani hayvanlar yaşar.
```

```text
[doğru_kelime_koruma]
GİRDİ: abi yarın bize gelicek mi
MODEL: Babi yarın bize gelecek mi?
HEDEF: Abi yarın bize gelecek mi?
```

```text
[doğru_kelime_koruma]
GİRDİ: hava sicak ama yagmur yagiyor
MODEL: Hava sıçak ama yağmur yağıyor.
HEDEF: Hava sıcak ama yağmur yağıyor.
```

```text
[noktalama]
GİRDİ: kim geldi
MODEL: Kim geldi.
HEDEF: Kim geldi?
```

```text
[sohbet]
GİRDİ: yarın görüşürüz insallah
MODEL: Yarın görüşürüz insallah.
HEDEF: Yarın görüşürüz inşallah.
```

```text
[sohbet]
GİRDİ: kitabı masada unuttumda geri döndüm
MODEL: Kitabı masada unuttumda geri döndüm.
HEDEF: Kitabı masada unuttum da geri döndüm.
```
