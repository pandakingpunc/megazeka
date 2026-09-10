# Megazeka — tamamlanan eğitim ve doğrulama

Türkçe masaüstü uygulaması; gerçek yerel ByT5-small + LoRA eğitimi. Bulut LLM API kullanılmaz.

## Gerçek eğitim

- Temel model: Google ByT5-small (Apache-2.0); tek sürüm ve tek yerel temel ağırlık kopyası.
- Eğitilen LoRA: 6.258.688 parametre; r=16, alpha=32, tüm uygun doğrusal katmanlar.
- Veri: Common Voice Türkçe Sentence Collector (CC0-1.0), 8.000 farklı hedef üzerinden 32.000 eğitim çifti; 640 doğrulama / 640 test.
- Eğitim: 60 adımlık denemeden devamla toplam 2,000 AdamW adımı, 32,000 işlenen örnek. Mikro parti 8, birikim 2.
- Doğrulama kaybına göre seçilen en iyi adım: 1,800. Son kayıt ayrıca 2,000. adımda; final dosyası best kaydına işaret eder.
- Donanım: AMD Ryzen 5 5600, yaklaşık 16 GB RAM, NVIDIA RTX 4060 8 GB; temel bfloat16, LoRA/optimizer float32.
- Kayıtlardaki eğitim akışı süresi: yaklaşık 18.4 dakika (indirme, uygulama geliştirme ve duraklamalar hariç).
- Windows dosya paylaşım çakışması sonrası 1.000. adımdaki kayıt gerçekten yüklenerek devam edildi; durum dosyası yazımı yeniden denemeli hale getirildi.

## Aynı 640 test çifti üzerinde ölçüm

| Çıktı | CER ↓ | WER ↓ | Tam eşleşme ↑ | Düzenleme F1 ↑ | Gereksiz düzeltme ↓ |
|---|---:|---:|---:|---:|---:|
| Girdiyi aynen kopyalama | %9,29 | %34,92 | %25,16 | %0,00 | %0,00 |
| Eğitim öncesi temel model · ham | %366,46 | %389,24 | %0,00 | %0,50 | %100,00 |
| Eğitilmiş model · ham / filtre kapalı | %1,93 | %9,82 | %63,28 | %85,62 | %2,48 |
| Uygulama · temkinli filtre açık | %5,11 | %13,28 | %60,62 | %62,34 | %2,48 |

Filtreli düzenleme precision: %86,91; recall: %48,60. Ham model precision: %89,54; recall: %82,03.

Gerçekten doğru 161 test girdisinin 4 tanesi gereksiz değiştirildi. Etiketi temiz olmayan bir örnekte gürültüler birbirini geri aldığından, sayı 160 yerine 161 oldu.

Temel model bu göreve göre eğitilmediği için ham üretimi uzayabilir; ekleme sayısı yüksek olduğunda CER/WER %100’ü aşabilir. Koruma filtresi temel modelin çıktısını reddedip girdiyi kopyalar. Eğitilmiş modelde filtre, doğru ama büyük düzenlemeleri de reddederek hata oranını artırıyor; bu fark gizlenmedi. Filtre öğrenme modundan isteğe bağlı kapatılabilir.

Bu sentetik test dağılımına ait ölçümlerdir. Model ağırlığı doğrulama kaybıyla seçildi; test örnekleri eğitimde kullanılmadı. Manuel örnekler genel başarı oranı olarak sunulmaz.

## Küçük manuel kontrol

12 manuel örnekte %66,67 tam eşleşme. Altı doğru örneğin biri değişti; bu küçük gruptaki gereksiz düzeltme oranı %16,67.

| Girdi | Gerçek çıktı |
|---|---|
| bugün okula gidicem ama hava cok kötü galiba | Bugün okula gidicem ama hava çok kötü galiba. |
| yarin arkadaşlarla buluşcaz sonrada sinemaya gidicez | Yarın arkadaşlarla buluşcaz sonrada sinemaya gidicez. |
| Bu film baya iyi olmuş. | Bu film baya iyi olmuş. |
| Bugün hava çok güzel. | Bugün hava çok güzel. |
| Ben de seninle geleceğim. | Ben de seninle geleceğim. |
| Ankaraya yarin gidicem. | Ankaraya yarın gidicem. |
| herkez buraya gelsin | Herkes buraya gelsin. |
| Beni duyuyormusun? | Beni duyuyor musun? |
| Bu gerçekten güzel bir haber. | Bu gerçekten güzel bir haber. |
| Merhaba! ↵  ↵ Nasılsın? | Merhaba! ↵  ↵ Nasılsın? |
| Cok tesekkur ederim. | Çok teşekkür ederim. |
| Işık, İstanbul’a yarın gelecek. | İşık, İstanbul’a yarın gelecek. |

Eksikler: “gidicem”, “buluşcaz”, “gidicez” gibi gündelik gelecek zaman biçimleri her zaman düzelmiyor. “Işık” özel adı bir örnekte “İşık” yapıldı. Özel adlar ve gündelik yazım için daha dengeli hata çiftleri ilk iyileştirme alanıdır. Veri boyutu otomatik artırılmadı.

## Doğrulama

- 16 otomatik test geçti: gürültü, Türkçe normalizasyon, kayıpsız parçalara ayırma, edit işlemleri, veri ayrımı, disk sınırı, Windows yazma çakışması, yerel model, Tk giriş/sonuç/pano.
- Gerçek çıkarım testinde socket bağlantıları engellendi; model çalıştı. CPU çıkarımı ayrıca gerçek ağırlıklarla denendi.
- Gerçek Windows arayüzünde metin girme, Düzelt, yüklenme, Kopyalandı geri bildirimi, öğrenme akışı, canlı grafik ve depolama görünümü kontrol edildi.
- Gerçek Tk/model testinde pano metni sonuçla karşılaştırıldı, iki paragraf ve küçük pencere yerleşimi doğrulandı. UI otomasyonu ekranındaki bazı Türkçe dışı teknik isimler model/kütüphane adlarıdır.
- Tamamlanmış eğitime --resume komutu yeniden verildiğinde eğitim tekrarlanmadı; indirme betiği tekrar çağrıldığında temel model yeniden indirilmedi.

## Depolama

- Proje klasörü: **5.568 GB**.
- Paylaşılan eski önbellek için ihtiyat payıyla: **7.117 GB**. Bu payın tamamının projeye ait olduğu iddia edilmez.
- Kalıcı kullanım 8 GB hedefinin altında; 15 GB kesin sınır. Küresel önbellekler silinmedi.

| Alan | MB |
|---|---:|
| Temel model | 599.34 |
| Best + latest + devam durumu | 100.45 |
| Kaynak ve sıkıştırılmış çiftler | 3.84 |
| Proje önbelleği | 0.00 |
| Günlük ve raporlar | 0.61 |
| Python ortamı | 4862.93 |

## Çalıştırma ve dosyalar

```powershell
cd megazeka
.\.venv\Scripts\python.exe app\main.py
```

`Baslat.bat` çift tıklanarak da açılır. Yerel model: `models/base/model.safetensors` + `models/checkpoints/best/adapter_model.safetensors`. Final işaretçisi: `models/final.json`.

Ayrıntılı kullanım/komutlar: `README.md`. Ham ölçümler ve başarılı/yanlış/kaçırılmış/zor örnekler: `reports/evaluation-best.json` ve `reports/evaluation-best.md`. Eğitim geçmişi: `reports/history.jsonl`.

Kaynaklar: [ByT5 resmî model kartı](https://huggingface.co/google/byt5-small), [Common Voice veri lisansı](https://github.com/common-voice/common-voice#licensing-and-content-source).