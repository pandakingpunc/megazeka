# Megazeka — tamamlanan eğitim ve doğrulama

Türkçe masaüstü uygulaması; gerçek yerel ByT5-small + LoRA eğitimi. Bulut LLM API kullanılmaz.

## Gerçek eğitim

- Temel model: Google ByT5-small (Apache-2.0); tek sürüm ve tek yerel temel ağırlık kopyası.
- Eğitilen LoRA: 6.258.688 parametre; r=16, alpha=32, tüm uygun doğrusal katmanlar.
- Veri: Common Voice Türkçe Sentence Collector (CC0-1.0) + projede üretilen gündelik cümleler (CC0-1.0). Eğitim 42,075 çift (31,996 common voice, 1,275 birleşik iki cümle, 8,804 megazeka gündelik şablon); doğrulama 1,440 çift (800 megazeka gündelik şablon, 640 common voice); test 1,128 çift (640 common voice, 488 megazeka gündelik şablon).
- Eğitim: sıfırdan toplam 5,000 AdamW adımı, 80,000 işlenen örnek. Mikro parti 8, birikim 2.
- Doğrulama kaybına göre seçilen en iyi adım: 5,000. Son kayıt ayrıca 5,000. adımda; final dosyası best kaydına işaret eder.
- Donanım: AMD Ryzen 5 5600, yaklaşık 16 GB RAM, NVIDIA RTX 4060 8 GB; temel bfloat16, LoRA/optimizer float32.
- Kayıtlardaki eğitim akışı süresi: yaklaşık 51.7 dakika (indirme, uygulama geliştirme ve duraklamalar hariç).
- Gündelik yazım (“gidicem”, “yapıcam”, “bilmiyom”) için ek tabanlı gürültü kuralları ve şablon cümleler eklendi; çıkarımda anlam değiştiren kelime değişimini engelleyen kelime kilidi var.

## Aynı 1,128 test çifti üzerinde ölçüm

| Çıktı | CER ↓ | WER ↓ | Tam eşleşme ↑ | Düzenleme F1 ↑ | Gereksiz düzeltme ↓ |
|---|---:|---:|---:|---:|---:|
| Girdiyi aynen kopyalama | %9,63 | %35,76 | %25,00 | %0,00 | %0,00 |
| Eğitim öncesi temel model · ham | %403,80 | %419,81 | %0,00 | %0,40 | %100,00 |
| Eğitilmiş model · ham / filtre kapalı | %1,15 | %5,94 | %77,84 | %91,11 | %1,77 |
| Uygulama · temkinli filtre açık | %1,24 | %6,12 | %77,48 | %90,72 | %1,77 |

### Alt kümeler (filtre açık)

| Alt küme | Çift | CER ↓ | WER ↓ | Tam eşleşme ↑ | Girdiyi kopyala tam eşleşme | Gereksiz düzeltme ↓ |
|---|---:|---:|---:|---:|---:|---:|
| common_voice | 640 | %1,59 | %7,67 | %70,16 | %25,00 | %3,12 |
| gündelik | 488 | %0,65 | %3,48 | %87,09 | %25,00 | %0,00 |

Filtreli düzenleme precision: %92,62; recall: %88,89. Ham model precision: %92,58; recall: %89,68.

Gerçekten doğru 282 test girdisinin 5 tanesi gereksiz değiştirildi. Etiketi temiz olmayan bazı örneklerde gürültüler birbirini geri aldığından sayı temiz etiket sayısından büyük olabilir.

Temel model bu göreve göre eğitilmediği için ham üretimi uzayabilir; ekleme sayısı yüksek olduğunda CER/WER %100’ü aşabilir. Koruma filtresi temel modelin çıktısını reddedip girdiyi kopyalar. Eğitilmiş modelde iki katmanlı filtre tam eşleşmeyi yalnızca 0,4 puan düşürür; bu fark gizlenmedi. Filtre öğrenme modundan isteğe bağlı kapatılabilir.

Bu sentetik test dağılımına ait ölçümlerdir. Model ağırlığı doğrulama kaybıyla seçildi; test örnekleri eğitimde kullanılmadı. Manuel örnekler genel başarı oranı olarak sunulmaz.

## Küçük manuel kontrol

23 manuel örnekte %91,30 tam eşleşme. 9 doğru örnekteki gereksiz düzeltme oranı %0,00.

| Girdi | Gerçek çıktı |
|---|---|
| bugün okula gidicem ama hava cok kötü galiba | Bugün okula gideceğim ama hava çok kötü galiba. |
| yarin arkadaşlarla buluşcaz sonrada sinemaya gidicez | Yarın arkadaşlarla buluşacağız, sonra da sinemaya gideceğiz. |
| Bu film baya iyi olmuş. | Bu film baya iyi olmuş. |
| Bugün hava çok güzel. | Bugün hava çok güzel. |
| Ben de seninle geleceğim. | Ben de seninle geleceğim. |
| Ankaraya yarin gidicem. | Ankara'ya yarın gideceğim. |
| herkez buraya gelsin | Herkes buraya gelsin. |
| Beni duyuyormusun? | Beni duyuyor musun? |
| Bu gerçekten güzel bir haber. | Bu gerçekten güzel bir haber. |
| Merhaba! ↵  ↵ Nasılsın? | Merhaba! ↵  ↵ Nasılsın? |
| Cok tesekkur ederim. | Çok teşekkür ederim. |
| Işık, İstanbul’a yarın gelecek. | Işık, İstanbul’a yarın gelecek. |
| yarın okula gidicem | Yarın okula gideceğim. |
| bugün sinemaya gitcez sonra yemek yiycez | Bugün sinemaya gideceğiz, sonra yemek yiyeceğiz. |
| Yapıcam dedim ama yapmıcam. | Yapacağım dedim ama yapmayacağım. |
| gelicem ama biraz geç olcak | Geleceğim ama biraz geç olacak. |
| bilmiyom ki napcam | Bilmiyorum ki ne yapacağım? |
| yanlız kaldım burda | Yalnız kaldım burada. |
| napıyosun bugun | Ne yapıyorsun bugün? |
| İstanbul'a gidicem ve orda kalıcam. | İstanbul'a gideceğim ve orada kalacağım. |
| Okula gideceğim. | Okula gideceğim. |
| Ben de seninle geleceğim, sen de gelir misin? | Ben de seninle geleceğim, sen de gelir misin? |
| Yarın arkadaşlarımla sinemaya gideceğiz. | Yarın arkadaşlarımla sinemaya gideceğiz. |

Eksikler: manuel tablodaki farklar gerçek çıktıdır; özel adlar ve nadir kısaltmalar (“tşk” gibi) kelime kilidi nedeniyle korunabilir. Veri boyutu otomatik artırılmadı.

## Doğrulama

- 19 otomatik test geçti: gürültü, gündelik yazım kuralları, kelime kilidi, Türkçe normalizasyon, kayıpsız parçalara ayırma, edit işlemleri, veri ayrımı, disk sınırı, Windows yazma çakışması, yerel model (gündelik düzeltme dahil), Tk giriş/sonuç/pano.
- Gerçek çıkarım testinde socket bağlantıları engellendi; model çalıştı. CPU çıkarımı ayrıca gerçek ağırlıklarla denendi.
- Gerçek Windows arayüzünde metin girme, Düzelt, yüklenme, Kopyalandı geri bildirimi, öğrenme akışı, canlı grafik ve depolama görünümü kontrol edildi.
- Gerçek Tk/model testinde pano metni sonuçla karşılaştırıldı, iki paragraf ve küçük pencere yerleşimi doğrulandı. UI otomasyonu ekranındaki bazı Türkçe dışı teknik isimler model/kütüphane adlarıdır.
- Tamamlanmış eğitime --resume komutu yeniden verildiğinde eğitim tekrarlanmadı; indirme betiği tekrar çağrıldığında temel model yeniden indirilmedi.

## Depolama

- Proje klasörü: **5.938 GB**.
- Paylaşılan eski önbellek için ihtiyat payıyla: **7.487 GB**. Bu payın tamamının projeye ait olduğu iddia edilmez.
- Kalıcı kullanım 8 GB hedefinin altında; 15 GB kesin sınır. Küresel önbellekler silinmedi.

| Alan | MB |
|---|---:|
| Temel model | 599.34 |
| Best + latest + devam durumu | 125.54 |
| Kaynak ve sıkıştırılmış çiftler | 7.43 |
| Proje önbelleği | 0.00 |
| Günlük ve raporlar | 1.65 |
| Python ortamı | 5198.29 |

## Çalıştırma ve dosyalar

```powershell
cd megazeka
.\.venv\Scripts\python.exe app\main.py
```

`Baslat.bat` çift tıklanarak da açılır. Yerel model: `models/base/model.safetensors` + `models/checkpoints/best/adapter_model.safetensors`. Final işaretçisi: `models/final.json`.

Ayrıntılı kullanım/komutlar: `README.md`. Ham ölçümler ve başarılı/yanlış/kaçırılmış/zor örnekler: `reports/evaluation-best.json` ve `reports/evaluation-best.md`. Eğitim geçmişi: `reports/history.jsonl`.

Kaynaklar: [ByT5 resmî model kartı](https://huggingface.co/google/byt5-small), [Common Voice veri lisansı](https://github.com/common-voice/common-voice#licensing-and-content-source).