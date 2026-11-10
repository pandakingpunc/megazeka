# Megazeka · Türkçe Yazım Atölyesi

Bu proje, **gerçekten yerelde eğitilen ByT5-small + LoRA modeliyle** Türkçe metinlerin yazımını düzeltir. Türkçe masaüstü arayüzünde metin girişi, sonuç, panoya kopyalama ve isteğe bağlı öğrenme ekranları bulunur. Çıkarımda ağ bağlantısı veya ücretli yapay zekâ API'si kullanılmaz. Eğitim amaçlı küçük bir deneydir; kusursuz bir yazım denetleyicisi değildir.

## Sonuçlar

**Tarayıcı demosu (yerel):** `space/` klasöründeki Gradio uygulaması; `pip install gradio==5.49.1` sonrası `python space/app.py` ile açılır. (Hugging Face artık ücretsiz hesapta Gradio Space barındırmadığı için şimdilik çevrim içi demo yok.)

1.128 çiftlik ayrılmış test kümesinde (`evaluation/evaluate.py --checkpoint best`): 640 Common Voice çifti
ve 488 gündelik konuşma çifti. "Girdiyi kopyala", hiçbir şey değiştirmeyen önemsiz başlangıç değeridir;
"temel ByT5" ise eğitilmemiş `google/byt5-small`. Test kümesi v2'den **bayt bayt aynı** dondurulmuştur
(SHA-256 `43738c61…`), bu yüzden v2, v3, v3.1 ve v3.2 doğrudan karşılaştırılabilir.

| Ölçüt | Girdiyi kopyala | Temel ByT5 | v2 | v3 | v3.1 | **Megazeka v3.2 (best)** | v3.2, filtresiz |
|---|---:|---:|---:|---:|---:|---:|---:|
| CER ↓ | 0,0963 | 0,0963 | 0,0137 | 0,0124 | 0,0129 | **0,0123** | 0,0113 |
| WER ↓ | 0,3576 | 0,3579 | 0,0678 | 0,0612 | 0,0609 | **0,0587** | 0,0570 |
| Tam eşleşme ↑ | %25,0 | %24,9 | %76,2 | %77,5 | %78,0 | **%78,1** | %78,5 |
| Düzenleme F1 ↑ | 0,000 | 0,000 | 0,898 | 0,907 | 0,905 | **0,909** | 0,913 |
| Gereksiz düzeltme ↓ | %0,0 | %0,4 (ham %100) | %1,8 | %1,8 | %2,1 | **%1,1** | %1,1 |

Alt kümeler (filtre açık), v2 → v3 → v3.1 → v3.2:

| Alt küme | Çift | Tam eşleşme | Gereksiz düzeltme |
|---|---:|---:|---:|
| Common Voice | 640 | %70,3 → %70,2 → %70,3 → **%71,4** | %3,1 → %3,1 → %3,8 → %1,9 |
| Gündelik | 488 | %84,0 → %87,1 → %88,1 → **%86,9** | %0,0 → %0,0 → %0,0 → %0,0 |
| Elle seçilmiş 23 örnek | 23 | %73,9 → %91,3 → %87,0 → **%87,0** | %11,1 → %0,0 → %0,0 → %0,0 |

**v3.2'yi dürüst okumak.** v3.2 hedefli bir sürümdür: v3.1'in bilinen üç zayıflığına (yaygın yazım
yanlışları, I/İ ile başlayan özel adlar, doğru kelimeyi uydurma kelimeye çevirme) yönelik eğitim verisi
eklendi. **Dondurulmuş testte v3.1 ile aynı düzeydedir:** örnek bazında yalnız v3.1'in bildiği 30, yalnız
v3.2'nin bildiği 31 çift vardır (McNemar p=1,0; tam eşleşme farkının %95 güven aralığı −1,6 ile +1,9 puan).
Bu beklenen bir sonuçtur, çünkü dondurulmuş testte bu üç hata türü neredeyse hiç yoktur. Kazanç, elle
yazılmış iki kümede görülür (aşağıda): eğitimden önce yazılan ve veri üreten ajanlara gösterilmeyen 66
cümlelik ikinci zorluk kümesinde 46 → 60 doğru (McNemar p=0,0005), ilk zorluk kümesinde 67 → 72 (p=0,23;
tek başına gürültü sınırında). Gereksiz düzeltme 6 örnekten 3'e indi; kalan üçün ikisi standart dışı test
hedefinin doğru düzeltilmesidir (`nerdeyse → neredeyse`, `şurda burda → şurda burada`), biri gerçek hatadır
(`asabidir → asabıdır`). v3.1'deki `denecek → deneyecek`, `yabani → yabanı`, `mevkiini → mevkini` hataları
görülmüyor. Karşılaştırma [`evaluation/compare.py`](evaluation/compare.py) ile yapılır (eşleştirilmiş McNemar
ve hedef cümle bazında bootstrap); çıktılar `reports/compare-v3.1-v3.2-*.txt`.

**v3.1'i dürüst okumak.** v3.1 bir veri temizliği sürümüdür; v3'ün düzeyindedir, belirgin biçimde daha iyi
değildir. Örnek bazında v3'ün bilip v3.1'in kaçırdığı 35, v3.1'in bilip v3'ün kaçırdığı 41 test çifti
vardır (net +6; tek eğitim koşusunda bu kadarı rastlantı olabilir). Gereksiz düzeltme 5'ten 6 örneğe çıktı,
ama örnekler tek tek incelendiğinde her iki modelde de üçü aslında doğru düzeltmedir, çünkü dondurulmuş test
hedefinin kendisi standart dışıdır (`nerdeyse → neredeyse`, `şurda burda → burada`, `bitpazarı → bit
pazarı`). Gerçekten yanlış olan gereksiz düzeltme her iki modelde de 3'tür (v3: `asabidir`,
`iltifatkarsınız`, `bitpazarı → bir pazarı`; v3.1: `denecek → deneyecek`, `yabani → yabanı`,
`mevkiini → mevkini`). Dondurulmuş test eski gürültü kurallarıyla ve temizlenmemiş hedeflerle üretildiği
için temizliğin faydasını tam ölçemez.

Girdiyi kopyalama her iki alt kümede %25'tir. 23 örnek yalnızca bir nitelik kontrolüdür, başarı oranı değildir.

Eğitilmemiş temel model bu görevde kullanılamaz (ham CER 4,04; her çıktıyı değiştirir), bu yüzden
korumalı sonucu girdiyle aynıdır. v3.2 eğitimi 6.500 adım sürdü; en iyi kayıt 6.000. adımdır. Ham ölçümler ve
başarılı / yanlış / kaçırılmış örnekler: [`reports/evaluation-best.md`](reports/evaluation-best.md);
v3.1 ölçümleri: [`reports/evaluation-v3.1.md`](reports/evaluation-v3.1.md); v3 ölçümleri:
[`reports/evaluation-v3.md`](reports/evaluation-v3.md); v2 ölçümleri:
[`reports/evaluation-v2.md`](reports/evaluation-v2.md).

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
`challenge_targets_excluded`), ama kategoriler v3 kurallarıyla örtüşür; bu yüzden %88,9 bir genel
başarı oranı olarak okunmamalıdır.

```powershell
.\.venv\Scripts\python.exe evaluation\challenge.py --checkpoint best
```

| Kategori | Cümle | v2 | v3 | v3.1 | **v3.2** |
|---|---:|---:|---:|---:|---:|
| yumuşama (gitcez → gideceğiz) | 10 | 7 | 9 | 10 | **9** |
| ne_yap (napcam → ne yapacağım) | 12 | 1 | 9 | 10 | **10** |
| sohbet | 8 | 7 | 7 | 6 | **7** |
| yazım_yanlışı (yanlız, herkez, …) | 17 | 2 | 12 | 13 | **15** |
| kesme_işareti (Ankaraya → Ankara'ya) | 8 | 0 | 7 | 7 | **7** |
| ı_i_isimleri (Isparta, Işık, Iğdır) | 9 | 0 | 5 | 4 | **8** |
| doğru_cümle (değişmemeli) | 17 | 16 | 17 | 17 | **16** |
| **Toplam tam eşleşme** | 81 | 33 (%40,7) | 66 (%81,5) | 67 (%82,7) | **72 (%88,9)** |
| Gereksiz düzeltme (17 doğru cümlede) | 17 | 1 (%5,9) | 0 (%0,0) | 0 (%0,0) | **1 (%5,9)** |

v3.1'den v3.2'ye 8 cümle düzeldi ("isparta → Isparta", "Igdir'a → Iğdır'a", "Ilgaz", "şöför → şoför",
"labaratuvar → laboratuvar", "bilmiyom valla") ve 3 cümle bozuldu: doğru yazılmış "Nolan'ın" artık
"Ne olan'ın" oluyor (yeni bir gerileme), "yemeği tadcaz bakalım" ve "makina bozuldu galiba" cümlelerine
gereksiz virgül ekleniyor. Başarısız 9 cümle ve gerçek çıktılar: [`reports/challenge-best.md`](reports/challenge-best.md)
(v3.1: [`reports/challenge-v3.1.md`](reports/challenge-v3.1.md); v3: [`reports/challenge-v3.md`](reports/challenge-v3.md);
v2: [`reports/challenge-v2.md`](reports/challenge-v2.md); bu dosyaların başlığı "best" yazar, içerikleri o
sürümün ölçümüdür).

### İkinci zorluk kümesi (66 çift, v3.2)

[`evaluation/challenge2.jsonl`](evaluation/challenge2.jsonl), v3.2 eğitiminden **önce** elle yazılmış 66 yeni
cümle çiftidir. Veriyi üreten ajanlara gösterilmedi ve hedefleri eğitimden dışlandı; ilk kümenin "kurallarla
birlikte yazıldı" zayıflığını azaltmak için eklendi. Yine de kategoriler v3.2'nin hedeflediği hata
türleridir; genel doğruluk ölçüsü değildir.

```powershell
.\.venv\Scripts\python.exe evaluation\challenge.py --checkpoint best --file evaluation\challenge2.jsonl
```

| Kategori | Cümle | v3.1 | **v3.2** |
|---|---:|---:|---:|
| ı_i_isimleri | 12 | 5 | **11** |
| yazım_yanlışı | 14 | 7 | **11** |
| doğru_kelime_koruma (değişmemeli) | 16 | 13 | **16** |
| noktalama | 6 | 5 | **5** |
| sohbet | 10 | 8 | **9** |
| doğru_cümle (değişmemeli) | 8 | 8 | **8** |
| **Toplam tam eşleşme** | 66 | 46 (%69,7) | **60 (%90,9)** |

Yalnız v3.2'nin bildiği 15, yalnız v3.1'in bildiği 1 cümle vardır (McNemar p=0,0005). Kalan 6 hata:
"traş → taraş", "sarmısak → sarmışak", "kirbit" düzelmiyor, "ısık → Isık", "nolur bana yardım et"
cümlesine gereksiz virgül, "unuttumda" ayrılmıyor. Çıktılar: [`reports/challenge2-best.md`](reports/challenge2-best.md)
(v3.1: [`reports/challenge2-v3.1.md`](reports/challenge2-v3.1.md)).

**v3.2 ve v3.1 farkı.** Yapılandırma aynıdır (`configs/medium.json`); adım sayısı veri büyüdüğü için
5.000'den 6.500'e çıkarıldı. Farklar:

- **Hedefli veri kaynağı** ([`training/targeted.py`](training/targeted.py)). v3.1 verisinde yazım yanlışı
  kuralları vardı ama kapsam yoktu: "laboratuvar" ve "kılavuz" birer, "mütevazı" sıfır hedef cümlede
  geçiyordu; I ile başlayan özel adlar toplam 130 kelime kadardı. Yeni kaynak üç türde 3.485 şablon cümle
  üretir: `yazım` (1.149; her yanlış yazım için anlamına uygun en az 12 farklı cümle), `özel_ad` (1.160;
  Isparta, Iğdır, Işık, İzmir… cümle başında, ortasında, ekli ve eksiz) ve `koruma` (1.176; "sıcak",
  "yabani", "denecek" gibi modelin bozduğu doğru kelimeler, %40'ı değiştirilmeden). Bunlardan 13.906 eğitim
  ve 1.210 doğrulama çifti çıkar. Yazım yanlışı sözlüğüne yaklaşık 38 girdi eklendi (tıraş, kibrit,
  sarımsak, şarj, döviz, poğaça, müteahhit…).
- **Eski akış korunur.** v3.1 dersinden dolayı hedefli kaynak ayrı tohum ve ayrı üreteçle çalışır; eski
  Common Voice ve gündelik çiftler v3.1 ile aynıdır (yeni zorluk kümesinin dışladığı birkaç cümle hariç)
  ve bunu bir test denetler (`tests/test_v32.py`).
- **Ölçüm araçları.** [`evaluation/compare.py`](evaluation/compare.py) iki raporu aynı örnekler üzerinde
  eşleştirir (McNemar, hedef cümle bazında bootstrap güven aralığı). `evaluate.py` ve `challenge.py`
  arşivlenmiş kayıtları `--checkpoint <ad>` ile ölçer. [`evaluation/test_target_audit.jsonl`](evaluation/test_target_audit.jsonl)
  dondurulmuş testin standart dışı 13 hedefini listeler; raporlardaki `audited_metrics` bloğu bunlar
  düzeltilip çıkarıldığında elde edilen sayıdır (ana `metrics` bloğu değişmez).
- **Sözlük koruması (isteğe bağlı, varsayılan kapalı).** `--lexicon-guard`, bilinen bir kelime sözlükte
  olmayan bir kelimeye çevrildiğinde değişikliği geri alır (`src/megazeka/lexicon.py`; sözlük Common Voice ve
  şablon cümlelerinden kurulur). v3.1 modelinde işe yarıyordu (ikinci zorluk kümesi 46 → 49), v3.2'de hiçbir
  çıktıyı değiştirmedi; bu yüzden kapalı bırakıldı.
- Veri üretimi ve ölçüm araçlarının kodunu OpenAI Codex alt ajanları (GPT) yazdı; tasarım, denetim, ikinci
  zorluk kümesi ve değerlendirme Claude ile yapıldı.

**v3.1 ve v3 farkı.** Yapılandırma ve adım sayısı aynıdır (`configs/medium.json`, 5.000
adım); fark yalnızca veridedir:

- **Hedef cümle denetimi** ([`data/audit/RAPOR.md`](data/audit/RAPOR.md)). Eğitim ve doğrulamadaki 10.560
  benzersiz hedef cümle iki turda denetlendi: önce 11 Claude Haiku alt ajanı, sonra 11 Claude Sonnet alt ajanı.
  Buna kural tabanlı taramalar eklendi. Her işaret Claude Opus tarafından tek tek okunup kabul ya da
  reddedildi; kararlar [`data/audit/build_corrections.py`](data/audit/build_corrections.py) içinde koddur.
  Sonuç 223 kayıttır ([`data/audit/corrections.jsonl`](data/audit/corrections.jsonl)). Common Voice
  cümlelerinin bir kısmında taranmış kitaplardan kalan OCR hataları vardı (`memurlan`, `kaşlan`, `Haşan`).
  Ayrıca konuşma dili biçimleri (`burda`, `nerde`), TDK yazımları (`hiç bir`, `davavekili`) ve unvanlar
  (`Raif efendi` → `Raif Efendi`) düzeltildi. Toplam 136 hedef düzeltildi, 12 bozuk cümle çıkarıldı.
- **Şablon düzeltmesi.** `training/everyday.py` özne ile nesnenin aynı kişi olduğu cümleler
  üretiyordu ("Yakında seni unutur musun?", "Sen seni izliyorsun"); bunlar artık başka bir tümleçle
  değiştiriliyor. "Ali'den bir şey sordum" şablonu "Ali'ye" yapıldı.
- **Çelişen gürültü kuralları kaldırıldı.** `ağabey → abi`, `bilmiyorum → bilmem` ve `tabii → tabi`
  kuralları geçerli Türkçe sözcükleri "yanlış" sayıyordu ("abi", "bilmem" ve "tabi olmak" doğrudur).

Bir uyarı: şablon değişikliği ilk denemede (v3.1a) rastgele sayı üretecinin tüketim sırasını değiştirdi ve
bütün şablon akışı kaydı. Örneğin "yiyecek" içeren hedefler 109'dan 74'e indi, model "yicek → yeyecek"
yanlışını yapmaya başladı ve tam eşleşme %76,9'a düştü. Yayınlanan v3.1'de ana üreteç v3'teki gibi
tüketilir; çakışan tümleç ayrı bir üreteçle değiştirilir. Böylece 2.561 şablon cümlenin 2.472'si v3 ile
aynıdır ve ölçülen fark temizlikten gelir.

**v3 ve v2 farkı.** v3, v2 ile aynı yapılandırmayı kullanır (`configs/medium.json`, öğrenme
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

Her iki depoda da ana dal bu depodaki yeni eğitimi (**v3.2**: 6.500 adım, 55.902 çift, hedefli veri)
içerir. Önceki sürümler etiketleriyle yüklenebilir kalır: **v3.1** (5.000 adım, 42.017 çift, denetlenmiş
hedefler), **v3** (5.000 adım, 42.075 çift),
**v2** (4.000 adım, 38.057 çift) ve **v1** (1.800 adım, 32.000 çift), örneğin
`PeftModel.from_pretrained(base, "pandakingpunc/megazeka-byt5-tr-spellfix", revision="v3.1")` veya
`revision="v2"` / `revision="v1"`.

## In English

Megazeka is a Turkish spelling and typo correction model: `google/byt5-small` fine-tuned with LoRA
(r=16, alpha=32, 6.26M trainable parameters) on 55,902 synthetically corrupted sentence pairs (v3.2): 31,932
derived from the CC0 Common Voice Turkish Sentence Collector, 8,792 from project-authored everyday
first/second-person sentences (template-generated with a small conjugator, CC0), 1,272 two-sentence
chunks and 13,906 from a targeted source added in v3.2 (common misspellings, I/İ-initial proper names, and
correct words the model must leave alone). Colloquial noise is rule-based on suffixes ("-eceğim → -icem", "-yorum → -yom", "burada → burda"),
so chat-style forms are corrected for any verb; v3 adds hardened consonants ("gitcez"), "ne yapacağım"
contractions ("napcam"), ~35 common misspellings ("yanlız", "herkez", "şöför") and dropped proper-noun
apostrophes ("Ankaraya"). It ships with an offline Tkinter desktop app —
inference makes no network calls and uses no hosted LLM API.

**Browser demo (local):** a Gradio app in `space/` (`python space/app.py`); there is no hosted demo for now.

On a held-out 1,128-pair test set (frozen byte-identical since v2, so all versions are directly comparable)
v3.2 reduces CER from 0.096 to 0.012 and WER from 0.358 to 0.059 against a copy-the-input baseline, raising
exact match from 25.0% to 78.1% (86.9% on the 488 everyday pairs), while changing 1.1% of already correct
inputs. v3.1 scored 0.0129 CER / 0.0609 WER / 78.0% exact; v3 0.0124 / 0.0612 / 77.5%; v2 0.0137 / 0.0678 /
76.2%.

**v3.2 is a targeted release. On the frozen test it is on par with v3.1** (paired: 31 pairs fixed only by
v3.2, 30 only by v3.1, McNemar p=1.0; 95% CI of the exact-match difference −1.6 to +1.9 points), which is
expected because that test barely contains the targeted error types. The gain shows on hand-written sets: a
second 66-pair challenge set, written before training and never shown to the agents that generated the
data, went from 46 to 60 correct (15 fixed, 1 broken, McNemar p=0.0005), with I/İ names 5 → 11 of 12,
misspellings 7 → 11 of 14 and correct-word protection 13 → 16 of 16. The first challenge set went from 67 to
72 of 81 (p=0.23, not significant on its own). The second set's categories are still the error types v3.2
targeted, so it is not a general accuracy figure. One regression: the correctly written `Nolan'ın` now
becomes `Ne olan'ın`. An optional lexicon guard (`--lexicon-guard`, off by default) reverts a known word
replaced by an unknown one; it helped v3.1 but changed nothing for v3.2. `evaluation/compare.py` does the
paired comparison.

**v3.1 was a data-cleaning release and performed on par with v3, not clearly better:** per example, 41 test
pairs are fixed only by v3.1 and 35 only by v3 (net +6, within single-run noise). v3.1 audited all 10,560
training/validation target sentences. Two rounds of Claude subagents (11 Haiku, then 11 Sonnet) flagged
candidates, and rule-based scans added more. Claude Opus then verified every flag by hand. The result was 223
corrections: OCR errors in Common Voice sentences such as `memurlan`/`kaşlan`, colloquial forms in targets
such as `burda`/`nerde`, TDK spellings, and nonsensical template sentences such as "Sen seni izliyorsun".
Three noise rules that marked valid words as errors (`abi`, `bilmem`, `tabi`) were removed. Of the 6 clean test
inputs that v3.1 changes, 3 are genuine fixes of non-standard frozen-test targets (`nerdeyse`, `şurda burda`,
`bitpazarı`), so the real harmful overcorrection count is 3 for both v3 and v3.1. The audit report is
`data/audit/RAPOR.md`. A word-level guard keeps any word substitution that has no letter
overlap with the original (e.g. a synonym swap) from reaching the output. Byte-level modelling was chosen so
Turkish diacritics (ı/İ, ş, ğ, ç, ö, ü) survive corruption without depending on a subword vocabulary.

A separate 81-pair hand-written challenge set (7 categories) went from 40.7% (v2) to 81.5% (v3) and 82.7%
(v3.1) exact match, with no overcorrection on its 17 already-correct sentences. **Caveat:** that set was
written alongside the v3 noise rules and aimed at known v2 failures (its targets are excluded from
training), so it measures whether those targeted failures were fixed, not general real-world accuracy.
v3.2 reaches 88.9% (72/81) and fixes `isparta`, `Igdir'a`, `Ilgaz`, `şöför` and `labaratuvar`. Still
failing: `klavuz` → `Kalavuz`, `traş` → `taraş`, `ısık` → `Isık`, `naber nasılsın` → `Ne yaber nasılsın?`,
`Ayşenin` keeps its missing apostrophe, and a few stray commas (`Ne olur, gel.`).

Releases: `main` = v3.2; tags `v3.1`, `v3`, `v2` and `v1` stay loadable with `revision="v3.1"` etc.
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
| Eğitim | 13.387 | 55.902 | 31.932 Common Voice · 8.792 gündelik · 1.272 birleşik · 13.906 hedefli |
| Doğrulama | 639 | 2.650 | 640 Common Voice · 800 gündelik · 1.210 hedefli |
| Test (v2'den dondurulmuş) | 282 | 1.128 | 640 Common Voice · 488 gündelik |

Test kümesi v2'den bayt bayt aynıdır (SHA-256 `43738c617c498e21753f71f9af928ac518c374e938742901a443e81b827e30a5`);
`training/prepare.py` mevcut test dosyasını yeniden üretmez ve hedeflerini eğitim ve doğrulamadan
dışlar. Doğrulama kümesi v3'te yenilendi (daha çok gündelik cümle), v3.2'de hedefli cümleler eklendi. İki zorluk kümesinin 146 hedefi eğitim ve doğrulamadan dışlanır. Önceki veri ve modeller `v3.1`, `v3`, `v2` etiketlerinde durur.

**Hedef düzeltmeleri (v3.1).** `training/prepare.py`, `data/audit/corrections.jsonl` dosyasını okur. Düzeltilecek
Common Voice hedeflerini yerinde değiştirir ve çıkarılacakları gürültüden önce eğitim ve doğrulamadan atar
(136 düzeltme, 12 çıkarma; `data/metadata.json` → `target_corrections`). Common Voice ayrımı özgün cümle
sırasına göre yapıldığı için dondurulmuş test ayrımı değişmez. Denetimin yöntemi, Haiku ile Sonnet ajanlarının
karşılaştırması ve sınırları [`data/audit/RAPOR.md`](data/audit/RAPOR.md) içindedir. Dondurulmuş testte
bilinen 3 standart dışı hedef değiştirilmemiştir.

Temiz örnek payı %25'tir. Gürültü; harf silme/tekrarlama/komşu harfleri yer değiştirme, Türkçe Q klavye komşuları, Türkçe karakter kaybı, büyük/küçük harf, noktalama, birleşmiş/ayrılmış kelimeler, fazla boşluk, de/da ve ki birleşmeleri, soru eki ve kesme işareti kaybı ve gündelik biçimleri içerir. v3'te dört işlem eklendi: **`sert_ünsüz`** ("gideceğim → gitcem", "edeceğim → etcem": yumuşak ünsüzün sertleşmesi), **`ne_kısalt`** ("ne yapacağım → napcam" gibi "ne yap-" kısaltmaları), **`yazım_yanlışı`** (yaklaşık 35 yaygın yanlış yazım: yanlız, herkez, yalnış, şöför, orjinal, süpriz, makina, hastahane, yada…) ve **`özel_ad_kesme`** ("Ankara'ya → Ankaraya"). Büyük/küçük harf hatası da düzeltildi: `str.swapcase` "İ" harfini iki kod noktasına ayırıp "I" harfini "i" yapıyordu; artık Türkçe duyarlı `swapcase_tr` / `upper_tr` kullanılır (`src/megazeka/text.py`). Yazım yanlışı sözlüğü `src/megazeka/spelling.py` içindedir. Her uygulanmış işlem **önce/sonra metniyle kaydedilir**. Bazı cümlelerde bir işlem uygulanabilir değilse başka bir işlem denenir. Zorluk seviyeleri 1 / 2 / 4 başarılı işlem hedefler.

**Gündelik dönüşüm kuralları** (`src/megazeka/colloquial.py`) sabit bir kelime listesi değil, ek tabanlı kurallardır ve her fiile uygulanır: "-eceğim → -icem/-cem", "-acağız → -ıcaz/-caz", "-ecek → -icek/-cek", "-mayacağım → -mıcam", "-yorum → -yom", "-yorsun → -yosun", "-yor → -yo"; "gideceğim → gitcem" gibi ünsüz sertleşmesi ve "okuyacağım → okucam", "söyleyeceğim → söylicem" gibi kaynaştırma düşmeleri; ayrıca "burada → burda", "ne yapıyorsun → napıyosun", "ne yapacağım → napcam", "bir şey → bişey", "değil → diil", "herkes → herkez", "yalnız → yanlız", "teşekkürler → tşk", "bir → bi" gibi kelime ve öbek kuralları. v3.1'de geçerli sözcükleri bozan üç kural kaldırıldı: "ağabey → abi", "bilmiyorum → bilmem", "tabii → tabi". Eğitim kümesinde gündelik işlem sayısı v1'de 1.001, v2'de 8.178, v3'te 8.853'tür; ayrıca v3'te 991 `yazım_yanlışı`, 729 `özel_ad_kesme`, 478 `ne_kısalt` ve 449 `sert_ünsüz` işlemi vardır.

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

Yayınlanan v3.2 modeli `configs/medium.json` ayarlarıyla (öğrenme hızı 5e-4, LoRA r=16) ve `--steps 6500` ile
sıfırdan tek koşuda 6.500 adım eğitildi (toplam 104.000 örnek, RTX 4060'ta yaklaşık 74 dakika; en iyi kayıt
6.000. adım, bkz. `reports/training-console.log`). v3.1 ve v3 aynı ayarlarla 5.000 adım eğitilmişti (yaklaşık 50 dakika); v2, 4.000 adımla (64.000 örnek, yaklaşık 33 dakika) eğitilmişti.

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
training/            veri üretimi, gündelik ve hedefli cümle şablonları, devam edilebilir LoRA eğitimi
evaluation/          ayrılmış test, elle yazılmış iki zorluk kümesi, eşleştirilmiş karşılaştırma ve okunabilir değerlendirme
space/               Gradio tarayıcı demosu (yerel)
configs/             quick / medium / quality ve depolama bütçesi
data/                tek kaynak, metadata ve sıkıştırılmış çiftler
data/audit/          v3.1 hedef cümle denetimi: ajan işaretleri, kararlar, düzeltme listesi ve rapor
models/base/         tek yerel temel model + tokenizer
models/checkpoints/  yalnızca best / latest
models/final.json    best kaydına işaretçi
reports/             gerçek ölçümler ve eğitim geçmişi
tests/               önemli bileşen ve arayüz kontrolleri
scripts/             bütçeli kurulum/indirme, temizlik ve gerçek UI kontrolü
```

## Bilinen sınırlar ve sonraki deneyler

Sentetik gürültü gerçek kullanıcı hatalarının bütün çeşitliliğini karşılamaz. Model özellikle nadir/özel ad, karma dil, bağlama bağlı de/da/ki ve noktalama tercihlerinde yanılabilir. İki zorluk kümesindeki (`reports/challenge-best.md`, `reports/challenge2-best.md`) kalan 15 hata v3.2'nin sınırlarını gösterir:

- **Bazı yazım yanlışları uydurma kelimeye dönüyor**: "klavuz" → "Kalavuz" (kılavuz), "traş" → "taraş" (tıraş), "sarmısak" → "sarmışak" (sarımsak); "kirbit" olduğu gibi kalır.
- **Işık adı**: "ısık" → "Isık" olur (ş geri gelmez). Diğer I/İ adlar (Isparta, Iğdır, Ilgaz, Ilgın) v3.2'de düzeldi.
- **Yeni gerileme**: doğru yazılmış "Nolan'ın" → "Ne olan'ın" olur; "nolur → ne olur" örüntüsü özel ada taşıyor.
- **Konuşma kısaltmaları ve noktalama**: "naber nasılsın" → "Ne yaber nasılsın?", "nolur gel" → "Ne olur, gel.", "Ayşenin" kesmesiz kalır, "unuttumda" ayrılmaz; birkaç cümlede virgül tercihi hedeften ayrılır.
- **Uydurma kelimeler**: v3.1'in "denecek → deneyecek", "yabani → yabanı" hataları görülmüyor; testte bir tane kaldı ("asabidir → asabıdır"). Kelime kilidi yalnızca harf benzerliği olmayan değişimleri engeller; isteğe bağlı sözlük koruması, kaynağı sözlükte olmayan kelimelerde (klavuz, traş) işe yaramaz.
- "tşk", "inş" gibi aşırı kısaltmalar kelime kilidine takılıp değişmeden kalabilir.
- Zorluk kümeleri hedeflenen hata türleriyle yazıldı; %88,9 ve %90,9 genel doğruluk değildir. Dondurulmuş testte v3.2, v3.1 ile aynı düzeydedir; Common Voice alt kümesi v2'den beri %70-71 bandındadır.
- Hedef denetimi kusursuz değildir: ajanların kaçırdığı hatalar kalmış olabilir ve Haiku, Sonnet ve kural taramaları birbirinin kaçırdıklarını buldu. Kaç hatanın hiç bulunmadığı ölçülmedi.
- Şablon cümleler 50 fiil ve sınırlı tümleçle üretildiği için gündelik alt küme gerçek sohbet dilinin tamamını temsil etmez. 176 baytlık bağımsız parçalar arasında bağlam taşınmaz. Veriye belirli bir üslup dönüştürme hedefi verilmedi; buna rağmen küçük eğitimle anlamı etkileyen yanlış düzenlemeler görülebilir. Doğru metni koruma eğitimi ve büyük değişiklik filtresi bu riski tamamen ortadan kaldırmaz.

İlk iyileştirmeler: gerçek kullanıcı mesajlarından derlenmiş küçük bir hata kümesi, özel adlarda "nolur/naber" açılımını engelleme, yanlış yazımı sözlükte olmayan kelimeler için hedef tarafında sözlük kontrolü, virgül tercihlerini dengeleme, daha fazla fiil ve tümleçle gündelik şablonlar, sentetik bozma ağırlıklarını doğrulama kümesiyle ayarlama. Veri boyutu kullanıcı açıkça istemeden artırılmaz. Kayıt veya model varyantı biriktirilmez.
