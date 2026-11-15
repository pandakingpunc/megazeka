# Zorluk kümesi: v4

Tam eşleşme: **74/84 = %88.1**

Gereksiz düzeltme (zaten doğru 39 cümle): **3/39 = %7.7**

| Kategori | Doğru | Toplam | Tam eşleşme |
|---|---:|---:|---:|
| yazım | 16 | 16 | %100.0 |
| özel_ad | 12 | 14 | %85.7 |
| koruma | 19 | 20 | %95.0 |
| sohbet | 8 | 10 | %80.0 |
| bağlaç | 9 | 12 | %75.0 |
| karışık | 10 | 12 | %83.3 |

## Başarısızlıklar (10)

```text
[özel_ad]
GİRDİ: Ipeğin eldivenleri burada kalmış.
MODEL: İpeğin eldivenleri burada kalmış.
HEDEF: İpek'in eldivenleri burada kalmış.
```

```text
[özel_ad]
GİRDİ: Selimin çizdiği resmi duvara astık.
MODEL: Selimin çizdiği resmi duvara astık.
HEDEF: Selim'in çizdiği resmi duvara astık.
```

```text
[koruma]
GİRDİ: Takım ligdeki mevkiini korudu.
MODEL: Takım liğdeki mevkini korudu.
HEDEF: Takım ligdeki mevkiini korudu.
```

```text
[sohbet]
GİRDİ: Yağmur yağarsa naparsın?
MODEL: Yağmur yağarsan ne yaparsın?
HEDEF: Yağmur yağarsa ne yaparsın?
```

```text
[sohbet]
GİRDİ: Seni arıycam ama önce işim bitsin.
MODEL: Seni karıyacağım ama önce işim bitsin.
HEDEF: Seni arayacağım ama önce işim bitsin.
```

```text
[bağlaç]
GİRDİ: Komşumuzda bizimle sinemaya geldi.
MODEL: Komşumuzda bizimle sinemaya geldi.
HEDEF: Komşumuz da bizimle sinemaya geldi.
```

```text
[bağlaç]
GİRDİ: Bilet aldık ama kardeşimde gelmek istiyor.
MODEL: Bilet aldık ama kardeşimde gelmek istiyor.
HEDEF: Bilet aldık ama kardeşim de gelmek istiyor.
```

```text
[bağlaç]
GİRDİ: Bu akşam bizde yemek yiyelim.
MODEL: Bu akşam biz de yemek yiyelim.
HEDEF: Bu akşam bizde yemek yiyelim.
```

```text
[karışık]
GİRDİ: Nalanın sipariş ettiği kitap gelmiş.
MODEL: Nalanın sipariş ettiği kitap gelmiş.
HEDEF: Nalan'ın sipariş ettiği kitap gelmiş.
```

```text
[karışık]
GİRDİ: Nolan bu filmi hangi yıl çekti?
MODEL: Ne olan bu filmi hangi yıl çekti?
HEDEF: Nolan bu filmi hangi yıl çekti?
```
