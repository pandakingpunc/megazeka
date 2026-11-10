# Zorluk kümesi: best

Tam eşleşme: **67/81 = %82.7**

Gereksiz düzeltme (zaten doğru 17 cümle): **0/17 = %0.0**

| Kategori | Doğru | Toplam | Tam eşleşme |
|---|---:|---:|---:|
| yumuşama | 10 | 10 | %100.0 |
| ne_yap | 10 | 12 | %83.3 |
| sohbet | 6 | 8 | %75.0 |
| yazım_yanlışı | 13 | 17 | %76.5 |
| kesme_işareti | 7 | 8 | %87.5 |
| ı_i_isimleri | 4 | 9 | %44.4 |
| doğru_cümle | 17 | 17 | %100.0 |

## Başarısızlıklar (14)

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
[sohbet]
GİRDİ: bilmiyom valla
MODEL: Bilmiyorum vallah.
HEDEF: Bilmiyorum valla.
```

```text
[yazım_yanlışı]
GİRDİ: şöför beni evin önünde bıraktı
MODEL: Şöför beni evin önünde bıraktı.
HEDEF: Şoför beni evin önünde bıraktı.
```

```text
[yazım_yanlışı]
GİRDİ: labaratuvarda çalışıyorum
MODEL: Labaratuvarda çalışıyorum.
HEDEF: Laboratuvarda çalışıyorum.
```

```text
[yazım_yanlışı]
GİRDİ: klavuz kitabı masada
MODEL: Kalavuz kitabı masada.
HEDEF: Kılavuz kitabı masada.
```

```text
[yazım_yanlışı]
GİRDİ: herzaman böyle yapıyorsun
MODEL: Her zaman böyle yapıyorsun?
HEDEF: Her zaman böyle yapıyorsun.
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
[ı_i_isimleri]
GİRDİ: Irmak ile Ilgaz parka gitti
MODEL: Irmak ile İlgaz parka gitti.
HEDEF: Irmak ile Ilgaz parka gitti.
```

```text
[ı_i_isimleri]
GİRDİ: isparta gülleriyle ünlüdür
MODEL: İsparta gülleriyle ünlüdür.
HEDEF: Isparta gülleriyle ünlüdür.
```

```text
[ı_i_isimleri]
GİRDİ: ılgaz ve işık yarın gelcek
MODEL: Ilgaz ve işık yarın gelecek.
HEDEF: Ilgaz ve Işık yarın gelecek.
```

```text
[ı_i_isimleri]
GİRDİ: Isparta'dan Igdir'a yolculuk uzun
MODEL: Isparta'dan İğdır'a yolculuk uzun.
HEDEF: Isparta'dan Iğdır'a yolculuk uzun.
```
