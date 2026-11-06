# Megazeka · Türkçe Yazım Atölyesi

Bu proje, **gerçekten yerelde eğitilen ByT5-small + LoRA modeliyle** Türkçe metinlerin yazımını düzeltir. Türkçe masaüstü arayüzünde metin girişi, sonuç, panoya kopyalama ve isteğe bağlı öğrenme ekranları bulunur. Çıkarımda ağ bağlantısı veya ücretli yapay zekâ API'si kullanılmaz. Eğitim amaçlı küçük bir deneydir; kusursuz bir yazım denetleyicisi değildir.

## Sonuçlar

**Canlı demo:** [huggingface.co/spaces/pandakingpunc/megazeka](https://huggingface.co/spaces/pandakingpunc/megazeka)
(Space kaynağı bu depoda `space/` klasöründedir).

1.128 çiftlik ayrılmış test kümesinde (`evaluation/evaluate.py --checkpoint best`): 640 Common Voice çifti
ve 488 gündelik konuşma çifti. "Girdiyi kopyala", hiçbir şey değiştirmeyen önemsiz başlangıç değeridir;
"temel ByT5" ise eğitilmemiş `google/byt5-small`. Test kümesi v2'den **bayt bayt aynı** dondurulmuştur
(SHA-256 `43738c61…`), bu yüzden v2 ve v3 doğrudan karşılaştırılabilir.

| Ölçüt | Girdiyi kopyala | Temel ByT5 | v2 | **Megazeka v3 (best)** | v3, filtresiz |
|---|---:|---:|---:|---:|---:|
| CER ↓ | 0,0963 | 0,0963 | 0,0137 | **0,0124** | 0,0115 |
| WER ↓ | 0,3576 | 0,3579 | 0,0678 | **0,0612** | 0,0594 |
| Tam eşleşme ↑ | %25,0 | %24,9 | %76,2 | **%77,5** | %77,8 |
| Düzenleme F1 ↑ | 0,000 | 0,000 | 0,898 | **0,907** | 0,911 |
| Gereksiz düzeltme ↓ | %0,0 | %0,4 (ham %100) | %1,8 | **%1,8** | %1,8 |

Alt kümeler (filtre açık), v2 → v3:

| Alt küme | Çift | Tam eşleşme | Gereksiz düzeltme |
|---|---:|---:|---:|
| Common Voice | 640 | %70,3 → **%70,2** | %3,1 → %3,1 |
| Gündelik | 488 | %84,0 → **%87,1** | %0,0 → %0,0 |
| Elle seçilmiş 23 örnek | 23 | %73,9 → **%91,3** | %11,1 → %0,0 (9 doğru örnekten 1 → 0) |

Girdiyi kopyalama her iki alt kümede %25'tir. Common Voice tarafı pratikte değişmedi (%70,3 → %70,2 bir
fark değil); kazanım gündelik alt kümede ve elle seçilmiş küçük örnek kümesinde. 23 örnek yalnızca bir
nitelik kontrolüdür, başarı oranı değildir.

Eğitilmemiş temel model bu görevde kullanılamaz (ham CER 4,04; her çıktıyı değiştirir), bu yüzden
korumalı sonucu girdiyle aynıdır. v3 eğitimi 5.000 adım sürdü; en iyi kayıt 5.000. adımdır. Ham ölçümler ve
başarılı / yanlış / kaçırılmış örnekler: [`reports/evaluation-best.md`](reports/evaluation-best.md);
v2 ölçümleri: [`reports/evaluation-v2.md`](reports/evaluation-v2.md).

"Filtresiz" sütunu, koruma filtresi kapalıyken ölçülendir. Filtre iki katmanlıdır (parça filtresi + kelime
kilidi, bkz. Mimari) ve tam eşleşmeyi yalnızca 0,4 puan düşürür; karşılığında harf benzerliği olmayan kelime
değişimlerini ve uydurma kelimeleri engeller.

**Ölçüm notu.** `evaluation/evaluate.py` içindeki `--limit` varsayılanı eskiden 640'tı ve 1.128 çiftlik test
kümesinin yalnızca bir kısmını sessizce değerlendiriyordu. Varsayılan artık tüm kümedir (`--limit` yalnızca
hızlı deneme içindir). v2'nin 1.128 çift sonuçları `--limit 1128` ile ölçülmüştü; bu belgedeki v2 ve v3
sayıları aynı 1.128 çiftin tamamı üzerindedir.

### Zorluk kümesi (81 çift)

[`evaluation/challenge.jsonl`](evaluation/challenge.jsonl), elle yazılmış 81 cümle çiftidir (7 kategori;
17'si zaten doğru cümledir). Şablonla üretilmediği için test kümesinden farklı bir bakış sağlar, ancak
**dürüst bir uyarı gerekir: bu küme yeni gürültü kurallarıyla birlikte, v2'nin bilinen hataları hedeflenerek
yazıldı.** Yani genel gerçek dünya doğruluğunu değil, hedeflenen hataların giderilip giderilmediğini ölçer.
Hedef cümleleri eğitim ve doğrulama verisinden çıkarılmıştır (`data/metadata.json` →
`challenge_targets_excluded: 81`), ama kategoriler v3 kurallarıyla örtüşür; bu yüzden %81,5 bir genel
başarı oranı olarak okunmamalıdır.

```powershell
.\.venv\Scripts\python.exe evaluation\challenge.py --checkpoint best
```

| Kategori | Cümle | v2 | **v3** |
|---|---:|---:|---:|
| yumuşama (gitcez → gideceğiz) | 10 | 7 (%70,0) | **9 (%90,0)** |
| ne_yap (napcam → ne yapacağım) | 12 | 1 (%8,3) | **9 (%75,0)** |
| sohbet | 8 | 7 (%87,5) | **7 (%87,5)** |
| yazım_yanlışı (yanlız, herkez, …) | 17 | 2 (%11,8) | **12 (%70,6)** |
| kesme_işareti (Ankaraya → Ankara'ya) | 8 | 0 (%0,0) | **7 (%87,5)** |
| ı_i_isimleri (Isparta, Işık, Iğdır) | 9 | 0 (%0,0) | **5 (%55,6)** |
| doğru_cümle (değişmemeli) | 17 | 16 (%94,1) | **17 (%100,0)** |
| **Toplam tam eşleşme** | 81 | 33 (%40,7) | **66 (%81,5)** |
| Gereksiz düzeltme (17 doğru cümlede) | 17 | 1 (%5,9) | **0 (%0,0)** |

Başarısız 15 cümle ve gerçek çıktılar: [`reports/challenge-best.md`](reports/challenge-best.md)
(v2: [`reports/challenge-v2.md`](reports/challenge-v2.md); o dosyanın başlığı "best" yazar, içerik v2 ölçümüdür).

**Önceki sürümle fark (v3 ve v2).** v3, v2 ile aynı yapılandırmayı kullanır (`configs/medium.json`, öğrenme
hızı 5e-4, LoRA r=16); farklar veri üretiminde ve adım sayısındadır (5.000, v2'de 4.000). Veri üreticisine
dört yeni gürültü işlemi eklendi: `sert_ünsüz` ("gitcez / etcem" gibi sertleşmiş biçimler), `ne_kısalt`
("napcam" → "ne yapacağım…"), `yazım_yanlışı` (yaklaşık 35 yaygın yazım yanlışı: yanlız, herkez, yalnış,
şöför, orjinal, süpriz, makina, hastahane, yada…) ve `özel_ad_kesme` ("Ankaraya" → "Ankara'ya"). Ayrıca bir
büyük/küçük harf hatası düzeltildi: `str.swapcase` "İ" harfini iki kod noktasına çeviriyor, "I" harfini "i"
yapıyordu; yerine `swapcase_tr` / `upper_tr` kullanılıyor. Gündelik cümleler 1.470'ten 2.561 benzersiz
cümleye çıktı. Sonuç: dondurulmuş testte tam eşleşme %76,2 → %77,5, WER 0,0678 → 0,0612; gündelik alt
küme %84,0 → %87,1; ama Common Voice alt kümesi değişmedi ve gereksiz düzeltme oranı aynı kaldı (%1,8).
Büyük sıçrama, v3 kurallarının hedeflediği zorluk kümesindedir (%40,7 → %81,5) ve yukarıdaki uyarıyla
okunmalıdır.

İlk sürüm (v1: 1.800 adım, yalnızca Common Voice verisi) eski 640 çiftlik testte %60,6 tam eşleşme veriyordu
ve "gidicem", "gitcez", "yapıcam" gibi gündelik biçimleri hiç düzeltmiyordu; çünkü eğitim verisinde bu
biçimler neredeyse yoktu. v2 bunları düzeltmeye başladı; v3 "gitcez → gideceğiz", "napcam → ne yapacağım",
"Ankaraya → Ankara'ya" gibi v2'nin yanlış bıraktığı biçimlerin çoğunu da düzeltir.

## Yayınlanan sürümler

- LoRA adaptörü: [`pandakingpunc/megazeka-byt5-tr-spellfix`](https://huggingface.co/pandakingpunc/megazeka-byt5-tr-spellfix)
- Eğitim verisi: [`pandakingpunc/megazeka-tr-spellfix-pairs`](https://huggingface.co/datasets/pandakingpunc/megazeka-tr-spellfix-pairs)
- Canlı demo: [`pandakingpunc/megazeka`](https://huggingface.co/spaces/pandakingpunc/megazeka) (Space; kaynağı `space/`)

Her iki depoda da ana dal bu depodaki yeni eğitimi (**v3**: 5.000 adım, 42.075 çift) içerir. Önceki
sürümler etiketleriyle yüklenebilir kalır: **v2** (4.000 adım, 38.057 çift) ve **v1** (1.800 adım, 32.000
çift), örneğin
`PeftModel.from_pretrained(base, "pandakingpunc/megazeka-byt5-tr-spellfix", revision="v2")` veya
`revision="v1"`.

## In English

Megazeka is a Turkish spelling and typo correction model: `google/byt5-small` fine-tuned with LoRA
(r=16, alpha=32, 6.26M trainable parameters) on 42,075 synthetically corrupted sentence pairs (v3): 31,996
derived from the CC0 Common Voice Turkish Sentence Collector, 8,804 from project-authored everyday
first/second-person sentences (template-generated with a small conjugator, CC0) and 1,275 two-sentence
chunks. Colloquial noise is rule-based on suffixes ("-eceğim → -icem", "-yorum → -yom", "burada → burda"),
so chat-style forms are corrected for any verb; v3 adds hardened consonants ("gitcez"), "ne yapacağım"
contractions ("napcam"), ~35 common misspellings ("yanlız", "herkez", "şöför") and dropped proper-noun
apostrophes ("Ankaraya"). It ships with an offline Tkinter desktop app —
inference makes no network calls and uses no hosted LLM API.

**Live demo:** https://huggingface.co/spaces/pandakingpunc/megazeka (source in `space/`).

On a held-out 1,128-pair test set (frozen byte-identical since v2, so v2 and v3 are directly comparable) v3
reduces CER from 0.096 to 0.012 and WER from 0.358 to 0.061 against a copy-the-input baseline, raising exact
match from 25.0% to 77.5% (87.1% on the 488 everyday pairs), while changing only 1.8% of already correct
inputs. v2 scored 0.0137 CER / 0.0678 WER / 76.2% exact. The Common Voice subset did not improve (70.3% →
70.2%); the gain is in everyday text. A word-level guard keeps any word substitution that has no letter
overlap with the original (e.g. a synonym swap) from reaching the output. Byte-level modelling was chosen so
Turkish diacritics (ı/İ, ş, ğ, ç, ö, ü) survive corruption without depending on a subword vocabulary.

A separate 81-pair hand-written challenge set (7 categories) went from 40.7% (v2) to 81.5% (v3) exact match,
with overcorrection on its 17 already-correct sentences dropping from 5.9% to 0%. **Caveat:** that set was
written alongside the v3 noise rules and aimed at known v2 failures (its targets are excluded from
training), so it measures whether those targeted failures were fixed, not general real-world accuracy.
Still failing: I/İ in names (`isparta` → `İsparta`, `Iğdır` → `İğdır`, `ısık` → `Isık`); `şöför`,
`labaratuvar` and `mütevazi` are not fixed; `klavuz` → `Kalavuz`; `naber` → `Ne yapar`; and one new
regression: `Türkiyede hava çok sıcak.` came out right in v2 but v3 produces `Türkiyede hava çok sıyacak.`,
a hallucinated, letter-similar word that passes the word guard.

Releases: `main` = v3; tags `v2` and `v1` stay loadable with `revision="v2"` / `revision="v1"`.
(`evaluation/evaluate.py` used to default to `--limit 640`, silently scoring only part of the test set; the
default is now the full 1,128 pairs and the v2 numbers above were measured with `--limit 1128`.)

The app includes a "learning mode" that exposes the actual bytes fed to the model, raw generation before
the change-limiting filter, per-token softmax probabilities, character-level edit operations, and the
training history. Observed, derived and unknown quantities are labelled separately; no confidence score
is invented where none exists.

Limitations are documented in the "Bilinen sınırlar" section below: synthetic noise does not cover the
full range of real user errors, no context is carried across 176-byte chunks, and the change-limiting
filter does not guarantee meaning preservation.


## Başlatma

Bu bilgisayardaki kurulum için `Baslat.bat` dosyasına çift tıklayın. PowerShell karşılığı:

```powershell
cd megazeka
.\.venv\Scripts\python.exe app\main.py
```

Metninizi girin, **Düzelt** düğmesine veya **Ctrl+Enter** tuşlarına basın. **Kopyala**, sonucu Windows panosuna aktarır ve “Kopyalandı!” geri bildirimi verir. Bir işlemde 4.000 karakter desteklenir. Satır sonları, boş paragraflar ve parça sınırlarındaki boşluklar korunur. Modelin parça içindeki boşlukları düzeltmesi mümkündür. Çalışırken arayüz yanıt vermeye devam eder. İlk işlem model yüklemesi nedeniyle daha uzun sürer.

## Mimari ve tercihler

- **Google ByT5-small**: çok dilli, encoder–decoder Transformer; UTF-8 baytlarıyla çalışır. Türkçe karakterleri alt kelime sözlüğüne bağımlı olmadan temsil eder. Bozuk yazımlara uygunluğu nedeniyle seçildi. Kaynak: [resmî model kartı](https://huggingface.co/google/byt5-small), [ByT5 araştırması](https://arxiv.org/abs/2105.13626).
- **LoRA, r=16, alpha=32**: doğrusal katmanlara düşük ranklı eğitilebilir matrisler eklenir. Temel ağırlıklar sabittir; 6.258.688 parametre eğitilir. Temel model yaklaşık 299,6 milyon parametredir; adaptörle toplam 305.896.448 olur. Bu, bir API sarmalayıcısı veya salt kural sistemi değildir.
- RTX 4060'ta temel model **bfloat16** tutulur; LoRA parametreleri ve AdamW durumları gerektiğinde float32'dir. CPU'da model float32'ye yüklenir. Nicemleme, ONNX ve `torch.compile` eklenmedi: bu ölçek için kurulum/depolama karmaşıklığını artırıyorlar.
- Üretim deterministik açgözlü çözümleme kullanır (`num_beams=1`, `do_sample=False`). Uzun metinler **176 UTF-8 baytını** aşmayan parçalara ayrılır, sessizce kesilmez. En fazla 224 yeni token üretilir. Bu bayt sınırı karakter sınırı değildir.
- Önişleme yalnızca NFC Unicode ve satır sonlarını normalleştirir. Modelden sonra iki katmanlı açık bir koruma filtresi vardır. **Parça filtresi**: karakter düzenleme sayısı girdi uzunluğunu aşarsa (oran > 1,0), çıktı girdi uzunluğunun %65'inden kısaysa, çıktı boşsa veya bitiş tokenı gelmemişse o parça özgün haliyle korunur. Eski %45 eşiği 1.128 çiftlik testte doğru ağır düzeltmelerin çoğunu reddediyordu (düzenleme F1 0,71 → 0,89); gereksiz düzeltme oranı eşikten bağımsız kaldı, bu yüzden gevşetildi. **Kelime kilidi**: kelimeler büyük/küçük harf, Türkçe karakter ve noktalamadan bağımsız hizalanır; bir kelime grubu harf benzerliği olmayan başka bir grupla değiştirilmişse (normalize Levenshtein uzaklığı > 0,6), bir kelime silinmişse veya karşılığı olmayan yeni kelime eklenmişse yalnızca o grup özgün haliyle kalır. Böylece "gidicem → gideceğim" veya "napcam → ne yapacağım" gibi harf benzerliği taşıyan düzeltmeler geçer; "okula → eğitim kurumuna" gibi anlam değiştiren kelime değişimleri geçmez. Filtrenin ham üretimi öğrenme ekranında görünür. Bu filtre anlamın korunmasını garanti etmez; yalnızca kelime düzeyinde eş anlamlı değişimi ve uydurma kelimeyi engeller.

## Depolama sözleşmesi

Tercih edilen toplam **8 GB altında**, kesin üst sınır **15 GB**. Buradaki GB ondalıktır (1.000.000.000 bayt). `.venv`, indirmeler, geçici dosyalar, önbellek, veriler ve kayıtlar hesaba katılır. 5 / 8 / 12 GB eşiklerinde uyarı gösterilir. İşlem öncesi öngörülen boyut sınıra ulaşıyorsa işlem başlamaz; indirmede ve eğitimde ayrıca çalışma zamanı denetimi yapılır. İşletim sisteminin sayfa dosyası gibi proje dışındaki otomatik yönetilen alanlar bu sayımda değildir.

`configs/storage.json` önceki iptal edilmiş indirmeden kalan paylaşılan uv önbelleği için **1,55 GB ihtiyat payı** içerir. Bu önbelleğin tamamının projeye ait olduğu iddia edilmez; alan bütçesi açısından tamamı hesaba katılmıştır. Ortak önbelleğe dokunulmaz. Gerçek proje klasörü ve bu ek payla hesaplanan bütçe toplamı ayrı gösterilir.

| Alan | Yaklaşık kalıcı boyut / yaklaşım |
|---|---|
| Python + GPU kütüphaneleri | 4,81 GB; en büyük kalem |
| Temel model | bfloat16 safetensors, yaklaşık 0,60 GB |
| Son ve en iyi LoRA | Adaptörler toplam yaklaşık 50 MB; son kaydın optimizer/RNG durumu ayrıca yaklaşık 50 MB |
| Sıkıştırılmış eğitim/veri dosyaları | Yaklaşık 2,3 MB; kaynak metin yaklaşık 1,6 MB |
| Final model | `models/final.json` işaretçisi; ağırlık kopyası yok |
| Önbellek | Projedeki `.cache/`; kurulum geçicileri temizlenir |

PyTorch GPU paketi için indirme **2,53 GB**, açılmış paket ve bağımlılıklar için yaklaşık **5 GB**, kurulum tepe artışı için **8,1 GB** bütçe ayrılır. Bu sığmazsa kurulum betiği otomatik olarak daha küçük CPU paketini seçer. ByT5 için yalnızca seçilen tek sürüm indirilir: başlangıçtaki bin dosyası **1,199 GB**, dönüştürülmüş bfloat16 dosyası yaklaşık **0,60 GB**. Dönüşümde ikisi kısa süre birlikte bulunur; başarılı kayıttan sonra redundant bin dosyası kaldırılır. 1 GB'dan büyük planlanan işlemler mevcut, ek ve beklenen boyutu konsola yazar.

```powershell
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe -m megazeka.storage
.\.venv\Scripts\python.exe scripts\cleanup.py
```

Temizlik betiği yalnızca projeye ait geçici kurulum önbelleklerini ve yarım kalan `temporary-*` kontrol noktalarını kaldırır. Temel model, veri gezgini için kaynak/veri dosyaları, `best`, `latest` ve devam etme durumu korunur. Global pip/uv/Hugging Face önbellekleri silinmez. Kalıcı kontrol noktaları yalnızca **best** ve **latest**'tir; yeni kayıt aynı adı değiştirir. Birikimli epoch ağırlıkları oluşturulmaz. Kayıt yazılırken küçük bir geçici klasör kullanılır.

## Veri ve lisanslar

Tek dış metin kaynağı, **Common Voice Türkçe Sentence Collector** dosyasıdır. Bunun yanında projede yazılmış, `training/everyday.py` içinde üretilen gündelik cümleler vardır (aşağıda). Yaklaşık 47.781 kısa satır içeren 1,56 MB'lık bu dosyanın belirli commit'i kullanılır; dev külliyat veya ses dosyaları indirilmez. Boyutu çok küçük olduğu için bu kaynakta streaming kütüphanesi ve Parquet motoru yerine doğrudan tek dosya ve **gzip JSONL** seçildi. Böylece PyArrow gibi ek bağımlılıklar gerekmez.

- [Kaynağın sabit sürümü](https://raw.githubusercontent.com/common-voice/common-voice/b12cde653757295103c5948c1cd601b166e1b905/server/data/tr/sentence-collector.txt)
- [Common Voice lisans açıklaması](https://github.com/common-voice/common-voice#licensing-and-content-source): bu cümleler **CC0-1.0**. Depodaki program kodunun MPL-2.0 lisansı ile cümlelerin lisansı farklıdır. Buraya Common Voice program kodu alınmadı.
- [Sentence Collector süreci](https://github.com/common-voice/sentence-collector): kamu malı cümle toplama ve gözden geçirme.
- Temel model: **Apache-2.0**, `68377bdc18a2ffec8a0533fef03b1c513a4dd49d` sürümü.
- Projede yazılan kod: `LICENSE` dosyasında MIT. Diğer Python paketleri kendi lisanslarını korur; kurulu dağıtımların `.dist-info` dizinlerinde lisans kayıtları vardır.

`data/raw/source.json`, tam kaynak URL'sini, commit'i ve SHA-256'yı içerir. `data/metadata.json`, küme boyutlarını ve üretilen sıkıştırılmış dosyaların SHA-256 değerlerini tutar.

### Veri üretimi

```powershell
.\.venv\Scripts\python.exe scripts\download.py
.\.venv\Scripts\python.exe training\prepare.py
```

3–24 kelimelik, 18–160 UTF-8 baytlık, büyük harfle başlayıp noktalama ile biten cümleler süzülür. NFC ve Türkçe küçük harf dönüşümü yapılmış, noktalaması kaldırılmış anahtarlarla tekilleştirilir. **Gürültü eklenmeden önce** 8.000 / 160 / 160 farklı Common Voice cümlesi eğitim / doğrulama / teste ayrılır. Her hedef için temiz / kolay / orta / zor olmak üzere dört çift hazırlanır.

**Gündelik cümleler.** Common Voice cümleleri edebî ve çoğunlukla üçüncü şahıstır; 32.000 çiftte "gideceğim" yalnızca 8, "geleceğim" 4 kez geçiyordu. Bu yüzden ilk sürüm "gidicem", "gitcez", "yapıcam" gibi biçimleri düzeltemiyordu. `training/everyday.py`, 50 fiillik bir tablo ve küçük bir çekim yardımcısıyla (gelecek zaman, şimdiki zaman, olumsuz, soru eki; ünlü uyumu ve git/et/ye/de özel durumları) birinci/ikinci şahıs gündelik cümleler ile elle yazılmış yaklaşık 250 kısa cümle üretir. Bu cümleler projeye aittir ve CC0-1.0 ile yayınlanır. v3'te üretilen gündelik cümle sayısı 1.470'ten 2.561 benzersiz cümleye çıktı (Common Voice ile çakışanlar atıldıktan sonra 2.526'sı kullanılır). Yaklaşık 1/12'si doğrulamaya ayrılır, test v2'den dondurulmuştur, kalanı eğitime gider; kolay ve orta zorlukta ilk işlem gündelik bir dönüşümdür (mümkünse hedefli işlem: `sert_ünsüz`, `ne_kısalt`, `yazım_yanlışı`, `özel_ad_kesme`). Zorluk kümesinin 81 hedefi eğitim ve doğrulamadan dışlanır.

**Birleşik parçalar.** Eğitim kümesine, aynı zorlukta iki bağımsız çiftin boşlukla birleştirilmesiyle oluşan ve 170 baytı aşmayan çok cümleli örnekler eklenir. Kullanıcı paragraf yapıştırdığında model parça içinde birden çok cümle görür; bu örnekler bunun için vardır.

| Küme | Farklı hedef | Toplam çift | Kaynak dağılımı |
|---|---:|---:|---|
| Eğitim | 10.200 | 42.075 | 31.996 Common Voice · 8.804 gündelik · 1.275 birleşik |
| Doğrulama | 360 | 1.440 | 640 Common Voice · 800 gündelik |
| Test (v2'den dondurulmuş) | 282 | 1.128 | 640 Common Voice · 488 gündelik |

Test kümesi v2'den bayt bayt aynıdır (SHA-256 `43738c617c498e21753f71f9af928ac518c374e938742901a443e81b827e30a5`);
`training/prepare.py` mevcut test dosyasını yeniden üretmez ve hedeflerini eğitim ve doğrulamadan
dışlar. Doğrulama kümesi v3'te yenilendi (daha çok gündelik cümle). v2 verisi ve modeli `v2` etiketinde durur.

Temiz örnek payı %25'tir. Gürültü; harf silme/tekrarlama/komşu harfleri yer değiştirme, Türkçe Q klavye komşuları, Türkçe karakter kaybı, büyük/küçük harf, noktalama, birleşmiş/ayrılmış kelimeler, fazla boşluk, de/da ve ki birleşmeleri, soru eki ve kesme işareti kaybı ve gündelik biçimleri içerir. v3'te dört işlem eklendi: **`sert_ünsüz`** ("gideceğim → gitcem", "edeceğim → etcem": yumuşak ünsüzün sertleşmesi), **`ne_kısalt`** ("ne yapacağım → napcam" gibi "ne yap-" kısaltmaları), **`yazım_yanlışı`** (yaklaşık 35 yaygın yanlış yazım: yanlız, herkez, yalnış, şöför, orjinal, süpriz, makina, hastahane, yada…) ve **`özel_ad_kesme`** ("Ankara'ya → Ankaraya"). Büyük/küçük harf hatası da düzeltildi: `str.swapcase` "İ" harfini iki kod noktasına ayırıp "I" harfini "i" yapıyordu; artık Türkçe duyarlı `swapcase_tr` / `upper_tr` kullanılır (`src/megazeka/text.py`). Yazım yanlışı sözlüğü `src/megazeka/spelling.py` içindedir. Her uygulanmış işlem **önce/sonra metniyle kaydedilir**. Bazı cümlelerde bir işlem uygulanabilir değilse başka bir işlem denenir. Zorluk seviyeleri 1 / 2 / 4 başarılı işlem hedefler.

**Gündelik dönüşüm kuralları** (`src/megazeka/colloquial.py`) sabit bir kelime listesi değil, ek tabanlı kurallardır ve her fiile uygulanır: "-eceğim → -icem/-cem", "-acağız → -ıcaz/-caz", "-ecek → -icek/-cek", "-mayacağım → -mıcam", "-yorum → -yom", "-yorsun → -yosun", "-yor → -yo"; "gideceğim → gitcem" gibi ünsüz sertleşmesi ve "okuyacağım → okucam", "söyleyeceğim → söylicem" gibi kaynaştırma düşmeleri; ayrıca "burada → burda", "ne yapıyorsun → napıyosun", "ne yapacağım → napcam", "bir şey → bişey", "değil → diil", "herkes → herkez", "yalnız → yanlız", "teşekkürler → tşk", "bir → bi" gibi kelime ve öbek kuralları. Eğitim kümesinde gündelik işlem sayısı v1'de 1.001, v2'de 8.178, v3'te 8.853'tür; ayrıca v3'te 991 `yazım_yanlışı`, 729 `özel_ad_kesme`, 478 `ne_kısalt` ve 449 `sert_ünsüz` işlemi vardır.

Bu %25, özellikle temiz bırakılan örneklerin payıdır. Nadir çoklu gürültüler birbirini geri alabilir; gereksiz düzeltme metriği etiket yerine gerçekten `girdi == hedef` olan bütün örnekleri sayar.

Kanonik aynı hedefin varyantları kümeler arasında bulunmaz; test bunu denetler. Bu, anlamsal olarak benzer bütün cümlelerin veya modelin bilinmeyen ön eğitim verilerinin tamamen ayrıldığı iddiası değildir. Common Voice cümlelerinde gözden kaçmış yazım hataları olabilir; veri filtresi dilbilgisel doğruluğun kanıtı değildir.

## Sıfırdan kurulum

Windows, Python **3.12**, `uv` ve internet gerekir. Bu makinede NVIDIA sürücüsü zaten kuruludur; ayrıca CUDA Toolkit indirilmesine gerek yoktur. Mevcut `.venv` kurulumunda bu bölümü yeniden çalıştırmanız gerekmez.

```powershell
cd megazeka
uv venv --python 3.12 .venv
.\.venv\Scripts\python.exe scripts\setup.py
.\.venv\Scripts\python.exe scripts\download.py
.\.venv\Scripts\python.exe training\prepare.py
```

Python'un Tk bileşeni standart Windows Python kurulumuna dahildir. `scripts/setup.py` proje içi önbellek ve geçici dizinleri ayarlar; `uv --no-cache` kullanır. Python 3.14 yerine 3.12 seçimi, sabitlenmiş ML paketlerinin uyumlu Windows tekerlekleri içindir. Ayrıntılı çalışmış paket listesi `requirements-lock.txt` dosyasındadır.

## Eğitim ve devam etme

```powershell
# Önce kısa deneme: 60 adım
.\.venv\Scripts\python.exe training\train.py --config configs/quick.json

# Sıfırdan tam eğitim: 3.000 adım, 48.000 örnek işlenir; best/latest kayıtlarını değiştirir
.\.venv\Scripts\python.exe training\train.py --config configs/medium.json

# Kesinti sonrası son kayıttan aynı şekilde devam
.\.venv\Scripts\python.exe training\train.py --config configs/medium.json --resume

# İsteğe bağlı: aynı küçük veri üzerinde daha çok eğitim; otomatik başlatılmaz
.\.venv\Scripts\python.exe training\train.py --config configs/quality.json --resume
```

Yayınlanan v3 modeli `configs/medium.json` ayarlarıyla (öğrenme hızı 5e-4, LoRA r=16) ve `--steps 5000` ile
sıfırdan tek koşuda 5.000 adım eğitildi (toplam 80.000 örnek, RTX 4060'ta yaklaşık 52 dakika; en iyi kayıt
5.000. adım, bkz. `reports/training-console.log`). v2, 4.000 adımla (64.000 örnek, yaklaşık 33 dakika) eğitilmişti.

Yeni eğitim (`--resume` olmadan) mevcut best/latest deneyini değiştirir ve `reports/history.jsonl` grafik geçmişini sıfırlar; bunu bilinçli yeni deneylerde kullanın. Uygulamadaki **60 adım eğit** düğmesi varsa son kayıttan devam eder. **Kaydet ve durdur**, güncel adım sonrasında doğrulama/kayıt yapılarak durulmasını ister. Doğrulama üretimi devam ediyorsa bunun tamamlanması beklenir.

AdamW, 30 adımlık öğrenme hızı ısınması, norm 1.0 gradient clipping, mikro parti 8 ve gradient accumulation 2 kullanılır. Her tur için tohuma bağlı deterministik karıştırma vardır. Python/NumPy/PyTorch rastgelelik durumları, optimizer, örnek sayacı ve adım kaydedilir. CUDA'nın bazı işlemleri donanım/sürüm farklılıklarında bit düzeyinde tekrarlanabilir olmayabilir. En iyi model, 640 doğrulama çifti üzerinde hedef token sayısıyla ağırlıklandırılmış kayıpla seçilir. Sekiz ardışık doğrulamada iyileşme olmazsa erken durdurma vardır.

CPU otomatik tanınır ve mikro parti 2'ye düşer; eğitim çok daha yavaştır. Bu bilgisayarda test edilen donanım: **Ryzen 5 5600, yaklaşık 16 GB RAM, RTX 4060 8 GB**. Model ağırlıkları küçüktür ama çalışma belleği dosya boyutundan büyüktür. Bir CPU/GPU çalışma zamanı hatası olduğunda veri veya kontrol noktaları başka servise gönderilmez.

## Öğrenme modu

- **Nasıl düzeltti?**: özgün metin, normalizasyon, gerçek giriş baytları/kimlikleri, ham model çıktısı, koruma filtresinden sonraki sonuç ve ölçülen aşama süreleri.
- **Görsel fark**: silinenler pembe/üstü çizili, eklenenler yeşil; değişen boşluklar `␠` ile görünür. Görsel eşleme `SequenceMatcher`, kesin karakter işlemleri Levenshtein ile hesaplanır.
- **Düzenlemeler**: sıfır tabanlı özgün karakter konumu, ekle/sil/değiştir, önce/sonra, değişim türü ve mesafe. Her satır tek karakter işlemi olduğundan mesafe 1'dir. Taşıma ayrı bir Levenshtein işlemi değildir; silme/ekleme ile temsil edilir.
- **Token gezgini**: seçilmiş tokenın softmax olasılığı ve aynı adımın ilk 5 alternatifi, ortalama ve en düşük bayt olasılığı, log olasılık toplamı. `ü` gibi harfler iki UTF-8 baytıdır. Bunlar **kalibre edilmiş doğruluk olasılığı veya düzeltme başına güven değildir**; olmayan güven puanları uydurulmaz.
- **Eğitim**: adım, tur, kayıp, öğrenme hızı, işlenen örnekler, geçen süre, kalan adımlar ve en iyi kayıt. Kayıp/CER/WER/gereksiz düzeltme grafikleri.
- **Veri kümesi**: tüm sıkıştırılmış eğitim/doğrulama/test örneklerinde gezinme ve gerçek gürültü işlem geçmişi.
- **Model bilgisi**: mimari, parametre sayısı, sözlük, aygıt, hassasiyet, boyut, parça ve üretim ayarları. Aynı girdiyle temel/en iyi/son kayıt karşılaştırması; ham çıktılar gösterilir. Eski epoch ağırlıkları depolama amacıyla saklanmaz.
- **Temkinli filtre deneyi**: Model bilgisi sekmesindeki işaret varsayılan olarak açıktır. Kapatıp yeniden Düzelt'e basarak ham model çıktısını sonuç kutusunda inceleyebilir/kopyalayabilirsiniz. Filtre doğru düzeltmeleri de engelleyebilir; bu nedenle ham ve filtreli ölçümler ayrı verilir. Öğrenme modundan çıkıldığında filtre yeniden açılır.
- **Depolama**: model, veri, kayıtlar, önbellek, günlükler, çalışma ortamı, toplam ve eşik uyarıları.

**Gözlenen / türetilen / bilinmeyen** ayrımı arayüzde açıkça belirtilir. Fark türünün Türkçe açıklaması gözlenen metin farkından türetilir; modelin özel düşüncesi değildir. Attention haritaları bu sürümde yoktur: ek bellek maliyeti getirir ve içsel nedenselliği kanıtlamaz.

## Değerlendirme ve testler

```powershell
.\.venv\Scripts\python.exe evaluation\evaluate.py --checkpoint best
.\.venv\Scripts\python.exe evaluation\challenge.py --checkpoint best
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\ui_smoke.py
```

`reports/evaluation-best.json` ve `.md` içinde sentetik test, ham üretim, korumalı sonuç, girdi-kopyalama başlangıç değeri ve eğitim dışında elle seçilmiş örnekler bulunur. Metrikler:

- Korpus **CER** ve **WER**: toplam Levenshtein hatası / toplam hedef karakter veya kelime sayısı; düşük olması iyidir.
- **Tam eşleşme**: çıktı hedefle harfiyen aynı mı?
- **Karakter düzenleme precision/recall/F1**: orijinal konum + işlem + eklenen/değiştirilen karakter kümelerinin örtüşmesi. Bu proje metriğidir; standart GEC M2/ERRANT F0.5 ile aynı değildir. Eşit maliyetli hizalamalar ve tekrar eden eklemeler puanı etkileyebilir.
- **Gereksiz düzeltme**: doğru girdi örneklerinden kaçında çıktı değişti? Ön/son işleme dahil uygulama oranı ve ham model oranı ayrı verilir.

Eğitim grafikleri hızlı olmak için sabit **16 doğrulama örneği** kullanır; 1.128 çiftlik test sonucu ile karıştırılmamalıdır. `evaluate.py` varsayılan olarak testin tamamını değerlendirir (`--limit N` ilk N çifti). Başarılı, yanlış, kaçırılmış ve zor düzeltmelerden okunabilir örnekler raporda ayrıdır. Manuel örnekler küçük bir nitelik kontrolüdür; genel başarı garantisi değildir. `tests/test_ui.py` hızlı widget testi için test motoru kullanır; `tests/test_inference.py` ve `scripts/ui_smoke.py` **gerçek yerel model** kullanır. Gerçek UI kontrolünde metin girilir, düğme çalıştırılır, sonuç ve işletim sistemi panosu karşılaştırılır.

## Dosyalar

```text
app/                 Türkçe masaüstü, öğrenme ve depolama ekranları
src/megazeka/        gürültü, gündelik kurallar, normalizasyon, çıkarım ve kelime kilidi, metrikler, disk denetimi
training/            veri üretimi, gündelik cümle şablonları ve devam edilebilir LoRA eğitimi
evaluation/          ayrılmış test, elle yazılmış zorluk kümesi ve okunabilir değerlendirme
space/               Hugging Face Space (canlı demo) kaynağı
configs/             quick / medium / quality ve depolama bütçesi
data/                tek kaynak, metadata ve sıkıştırılmış çiftler
models/base/         tek yerel temel model + tokenizer
models/checkpoints/  yalnızca best / latest
models/final.json    best kaydına işaretçi
reports/             gerçek ölçümler ve eğitim geçmişi
tests/               önemli bileşen ve arayüz kontrolleri
scripts/             bütçeli kurulum/indirme, temizlik ve gerçek UI kontrolü
```

## Bilinen sınırlar ve sonraki deneyler

Sentetik gürültü gerçek kullanıcı hatalarının bütün çeşitliliğini karşılamaz. Model özellikle nadir/özel ad, karma dil, bağlama bağlı de/da/ki ve noktalama tercihlerinde yanılabilir. Zorluk kümesindeki (`reports/challenge-best.md`) kalan 15 hata v3'ün sınırlarını gösterir:

- **I/İ içeren özel adlar hâlâ güvenilmez**: "isparta" → "İsparta" (doğrusu Isparta), "Igdir'a" → "İğdır'a" (Iğdır'a), "ısık" → "Isık" (Işık), "ılgaz ve işık" → "Ilgaz ve işık" (Işık).
- **Bazı yazım yanlışları düzelmiyor**: "şöför", "labaratuvar", "mütevazi" (→ mütevazı) olduğu gibi kalır; "klavuz" ise "Kalavuz" olur (doğrusu kılavuz). "yalnış anladın beni" doğru kelimeye düzelir ama sonuna gereksiz soru işareti eklenir.
- **Konuşma kısaltmaları**: "naber" → "Ne yapar" (doğrusu "Ne haber"); "nolur gel" → "Ne olur gel?" ve birkaç cümlede virgül/soru işareti tercihleri hedeften ayrılır.
- **Yeni gerileme**: "Türkiyede hava çok sıcak." cümlesini v2 doğru işliyordu; v3 "Türkiyede hava çok **sıyacak**." üretir. Uydurma ama harf olarak benzer bir kelime olduğu için kelime kilidinden geçer; kilit yalnızca harf benzerliği olmayan değişimleri engeller.
- "tşk", "inş" gibi aşırı kısaltmalar kelime kilidine takılıp değişmeden kalabilir.
- Zorluk kümesi v3 kurallarıyla birlikte, v2 hataları hedeflenerek yazıldı; %81,5 genel doğruluk değildir. Common Voice alt kümesi v2'ye göre iyileşmedi (%70,3 → %70,2).
- Şablon cümleler 50 fiil ve sınırlı tümleçle üretildiği için gündelik alt küme gerçek sohbet dilinin tamamını temsil etmez. 176 baytlık bağımsız parçalar arasında bağlam taşınmaz. Veriye belirli bir üslup dönüştürme hedefi verilmedi; buna rağmen küçük eğitimle anlamı etkileyen yanlış düzenlemeler görülebilir. Doğru metni koruma eğitimi ve büyük değişiklik filtresi bu riski tamamen ortadan kaldırmaz.

İlk iyileştirmeler: gerçek kullanıcı mesajlarından derlenmiş küçük bir hata kümesi, özel adları (özellikle I/İ) koruma için ayrılmış test, uydurma ama harf olarak benzer kelimeleri yakalayacak bir sözlük kontrolü, daha fazla fiil ve tümleçle gündelik şablonlar, sentetik bozma ağırlıklarını doğrulama kümesiyle ayarlama. Veri boyutu kullanıcı açıkça istemeden artırılmaz. Kayıt veya model varyantı biriktirilmez.
