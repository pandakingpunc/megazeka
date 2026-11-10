# Zorluk kümesi: best

Tam eşleşme: **72/81 = %88.9**

Gereksiz düzeltme (zaten doğru 17 cümle): **1/17 = %5.9**

| Kategori | Doğru | Toplam | Tam eşleşme |
|---|---:|---:|---:|
| yumuşama | 9 | 10 | %90.0 |
| ne_yap | 10 | 12 | %83.3 |
| sohbet | 7 | 8 | %87.5 |
| yazım_yanlışı | 15 | 17 | %88.2 |
| kesme_işareti | 7 | 8 | %87.5 |
| ı_i_isimleri | 8 | 9 | %88.9 |
| doğru_cümle | 16 | 17 | %94.1 |

## Başarısızlıklar (9)

```text
[yumuşama]
GİRDİ: yemeği tadcaz bakalım
MODEL: Yemeği tadacağız, bakalım.
HEDEF: Yemeği tadacağız bakalım.
```

```text
[ne_yap]
GİRDİ: nolur gel
MODEL: Ne olur, gel.
HEDEF: Ne olur gel.
```

```text
[ne_yap]
GİRDİ: naber nasılsın
MODEL: Ne yaber nasılsın?
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
GİRDİ: makina bozuldu galiba
MODEL: Makine bozuldu, galiba.
HEDEF: Makine bozuldu galiba.
```

```text
[yazım_yanlışı]
GİRDİ: klavuz kitabı masada
MODEL: Kalavuz kitabı masada.
HEDEF: Kılavuz kitabı masada.
```

```text
[kesme_işareti]
GİRDİ: Ayşenin kitabı masada.
MODEL: Ayşenin kitabı masada.
HEDEF: Ayşe'nin kitabı masada.
```

```text
[ı_i_isimleri]
GİRDİ: ısık bugün okula gelmedi
MODEL: Isık bugün okula gelmedi.
HEDEF: Işık bugün okula gelmedi.
```

```text
[doğru_cümle]
GİRDİ: Nolan'ın yeni filmini izledim.
MODEL: Ne olan'ın yeni filmini izledim.
HEDEF: Nolan'ın yeni filmini izledim.
```
