# Zorluk kümesi: v3.5

Tam eşleşme: **70/84 = %83.3**

Gereksiz düzeltme (zaten doğru 39 cümle): **2/39 = %5.1**

| Kategori | Doğru | Toplam | Tam eşleşme |
|---|---:|---:|---:|
| yazım | 15 | 16 | %93.8 |
| özel_ad | 10 | 14 | %71.4 |
| koruma | 19 | 20 | %95.0 |
| sohbet | 8 | 10 | %80.0 |
| bağlaç | 9 | 12 | %75.0 |
| karışık | 9 | 12 | %75.0 |

## Başarısızlıklar (14)

```text
[yazım]
GİRDİ: Yeni cihazın kullanma klavuzunu kaybettik.
MODEL: Yeni cihazın kullanmaklavuzunu kaybettik.
HEDEF: Yeni cihazın kullanma kılavuzunu kaybettik.
```

```text
[özel_ad]
GİRDİ: ısık yarın provaya katılacak.
MODEL: Isık yarın provaya katılacak.
HEDEF: Işık yarın provaya katılacak.
```

```text
[özel_ad]
GİRDİ: Teyzem ıspartada öğretmenlik yapıyor.
MODEL: Teyzem ısparta'da öğretmenlik yapıyor.
HEDEF: Teyzem Isparta'da öğretmenlik yapıyor.
```

```text
[özel_ad]
GİRDİ: Ipeğin eldivenleri burada kalmış.
MODEL: İpeğin eldivenleri burada kalmış.
HEDEF: İpek'in eldivenleri burada kalmış.
```

```text
[özel_ad]
GİRDİ: Ayşeye anahtarı teslim ettim.
MODEL: Ayşeye anahtarı teslim ettim.
HEDEF: Ayşe'ye anahtarı teslim ettim.
```

```text
[koruma]
GİRDİ: Takım ligdeki mevkiini korudu.
MODEL: Takım liğdeki mevkiini korudu.
HEDEF: Takım ligdeki mevkiini korudu.
```

```text
[sohbet]
GİRDİ: Seni arıycam ama önce işim bitsin.
MODEL: Seni arıyacağım ama önce işim bitsin.
HEDEF: Seni arayacağım ama önce işim bitsin.
```

```text
[sohbet]
GİRDİ: Akşam beraber yemek yicez.
MODEL: Akşam beraber yemek yeyeceğiz.
HEDEF: Akşam beraber yemek yiyeceğiz.
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
GİRDİ: Sende bizimle yürüyüşe katıl.
MODEL: Sende bizimle yürüyüşe katıl.
HEDEF: Sen de bizimle yürüyüşe katıl.
```

```text
[karışık]
GİRDİ: ısık bu akşam gelmiycekmiş.
MODEL: Isık bu akşam gelmiyecekmiş.
HEDEF: Işık bu akşam gelmeyecekmiş.
```

```text
[karışık]
GİRDİ: Nalanın sipariş ettiği kitap gelmiş.
MODEL: Nala'nın sipariş ettiği kitap gelmiş.
HEDEF: Nalan'ın sipariş ettiği kitap gelmiş.
```

```text
[karışık]
GİRDİ: Nolan bu filmi hangi yıl çekti?
MODEL: Ne olan bu filmi hangi yıl çekti?
HEDEF: Nolan bu filmi hangi yıl çekti?
```
