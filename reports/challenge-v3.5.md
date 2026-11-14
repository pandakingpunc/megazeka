# Zorluk kümesi: v3.5

Tam eşleşme: **76/81 = %93.8**

Gereksiz düzeltme (zaten doğru 17 cümle): **0/17 = %0.0**

| Kategori | Doğru | Toplam | Tam eşleşme |
|---|---:|---:|---:|
| yumuşama | 10 | 10 | %100.0 |
| ne_yap | 10 | 12 | %83.3 |
| sohbet | 7 | 8 | %87.5 |
| yazım_yanlışı | 15 | 17 | %88.2 |
| kesme_işareti | 8 | 8 | %100.0 |
| ı_i_isimleri | 9 | 9 | %100.0 |
| doğru_cümle | 17 | 17 | %100.0 |

## Başarısızlıklar (5)

```text
[ne_yap]
GİRDİ: nolur gel
MODEL: Ne olur gel?
HEDEF: Ne olur gel.
```

```text
[ne_yap]
GİRDİ: naber nasılsın
MODEL: Ne haber nasılsın?
HEDEF: Ne haber, nasılsın?
```

```text
[sohbet]
GİRDİ: bi dakika bekle geliyom
MODEL: Bir dakika bekle geliyorum.
HEDEF: Bir dakika bekle, geliyorum.
```

```text
[yazım_yanlışı]
GİRDİ: yalnış anladın beni
MODEL: Yanlış anladın beni?
HEDEF: Yanlış anladın beni.
```

```text
[yazım_yanlışı]
GİRDİ: herzaman böyle yapıyorsun
MODEL: Her zaman böyle yapıyorsun?
HEDEF: Her zaman böyle yapıyorsun.
```
