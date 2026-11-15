# Megazeka · Türkçe Yazım Atölyesi

Bu proje, **gerçekten yerelde eğitilen ByT5 + LoRA modeliyle** (v4: `google/byt5-base`; v3.2 ve öncesi: `google/byt5-small`) Türkçe metinlerin yazımını düzeltir. Türkçe masaüstü arayüzünde metin girişi, sonuç, panoya kopyalama ve isteğe bağlı öğrenme ekranları bulunur. Çıkarımda ağ bağlantısı veya ücretli yapay zekâ API'si kullanılmaz. Eğitim amaçlı küçük bir deneydir; kusursuz bir yazım denetleyicisi değildir.

## Sonuçlar

**Tarayıcı demosu (yerel):** `space/` klasöründeki Gradio uygulaması; `pip install gradio==5.49.1` sonrası `python space/app.py` ile açılır. (Hugging Face artık ücretsiz hesapta Gradio Space barındırmadığı için şimdilik çevrim içi demo yok.)

### v4 (en son sürüm)

v4, taban modeli `google/byt5-small` yerine **`google/byt5-base`** (581.653.248 parametre) yapar; LoRA rank 16 ile
toplam 592.417.536 parametrenin 10.764.288'i eğitilir. Veri, iç adıyla v3.5'tir (aşağıda "Veri ve lisanslar");
v3.5 ayrı bir sürüm olarak **yayınlanmadı**, v4 ile birlikte ilk kez yayınlanıyor. Yanında, model dışında çalışan
**isteğe bağlı bir sözlük katmanı** gelir (`--dictionary`, varsayılan kapalı; bkz. Mimari). Sayılar 1.128 çiftlik
dondurulmuş testten ve elle yazılmış beş zorluk kümesinden gelir; ham ölçümler `reports/` altındadır. Tabloda
sözlük koruması (`lexicon_guard`) kapalıdır.

| Küme | v3.2 | v4 | v4 + sözlük |
|---|---:|---:|---:|
| Donmuş test tam eşleşme (1.128) | %78,1 | %79,3 | **%81,6** |
| Donmuş test düzenleme F1 | 0,909 | 0,907 | **0,913** |
| Temiz cümle bozma (282 temiz girdi, düşük iyi) | 3 | 6 | 8 |
| challenge (81) | 72 | 77 | 77 |
| challenge2 (66) | 60 | 63 | 63 |
| challenge3 (84) | 59 | 73 | **74** |
| challenge4 (90) | 30 | 62 | **75** |
| challenge4 liste dışı (25) | 1 | 4 | **16** |
| challenge5 (70) | ölçülmedi | 44 | **59** |
| challenge5 görülmemiş sözcük (26) | ölçülmedi | 7 | **20** |
| challenge5 koruma (30) | ölçülmedi | 24 | **25** |

**v4'ü dürüst okumak.** Tabanı büyütmek genel doğruluğu biraz artırdı (donmuş testte %78,1 → %79,3), ama bu fark
gürültü sınırındadır (eşleştirilmiş McNemar p=0,18; yalnız v3.2'nin bildiği 40, yalnız v4'ün bildiği 54 çift) ve
temiz cümle bozma 3'ten 6'ya çıktı. Görülmemiş sözcüğe genelleme değişmedi: challenge4'te liste dışı sözcüklerde
v4 4/25, challenge5'te görülmemiş sözcüklerde 7/26 kaldı (aynı veriyle eğitilen byt5-small v3.5 modeli challenge4'te
60/90, v4 62/90; p=0,69). Bu açığı büyük taban değil, **sözlük katmanı** kapattı: donmuş testte
%79,3 → %81,6 (33 çift düzeldi, 8 bozuldu; p=0,0001), challenge5'te 44 → 59 (hiçbir çift bozulmadı; p=6e-5).
Bedeli: temiz cümle bozma 6'dan 8'e çıktı ve çıkarım süresi eklenir (aşağıda).

Eşleştirilmiş karşılaştırmalar ([`evaluation/compare.py`](evaluation/compare.py); çıktılar `reports/compare-*.txt`):
v3.2 → v4 donmuş test p=0,18; v4 → v4 + sözlük donmuş test p=0,0001; v3.2 → v4 + sözlük donmuş test p=0,0004;
v4 → v4 + sözlük challenge4 p=0,0002 (13 kazanç, 0 kayıp); challenge5 p=6e-5 (15 kazanç, 0 kayıp).

**Kümelerin bağımsızlığı:**

- challenge3, önceki sürümlerin geliştirmesi sırasında görüldü; **bağımsız bir ölçüm değildir**.
- challenge4'te sözlük eşiği (11 nat) ayarlandı; "v4 + sözlük" sütunu **iyimserdir**.
- challenge5, ayar sırasında hiç bakılmayan kümedir; **bağımsız ölçüm budur**.

**Maliyet.** v4 çıkarımı v3.5 modeline göre yaklaşık 1,6 kat yavaştır (dondurulmuş testte 221 sn → 358 sn, RTX 4060);
sözlük katmanı üstüne yaklaşık %20 ekler (358 sn → 429 sn). Taban ağırlığı 2,33 GB'dır (byt5-small: 0,60 GB).
v4 eğitimi `configs/v4.json` ile RTX 4060 8 GB'ta 3 saat 4 dakika sürdü (7.000 adım, en iyi kayıt 6.750. adım,
doğrulama kaybı 0,0218).

Ham ölçümler: [`reports/evaluation-v4.md`](reports/evaluation-v4.md), [`reports/evaluation-v4-dict.md`](reports/evaluation-v4-dict.md);
zorluk kümeleri `reports/challenge{,2,3,4,5}-v4*.md`.

### Zorluk kümesi 4 (90 çift, v4 ile açık)

[`evaluation/challenge4.jsonl`](evaluation/challenge4.jsonl): elle yazılmış 90 cümle; dört kategori: `listede` (30;
v3.5'in ek yazım kataloğundaki sözcükler), `liste_dışı` (25; kataloğa girmeyen yazım yanlışları), `koruma` (25;
değişmemesi gereken doğru cümleler) ve `karışık` (10). Küme, "öğretilen sözcüğü ezberliyor, görmediğine genellemiyor"
bulgusunu ölçer. byt5-small v3.2 30/90 (liste dışı 1/25), byt5-small v3.5 60/90 (listede 29/30, liste dışı 4/25),
v4 62/90 (liste dışı 4/25), v4 + sözlük 75/90 (liste dışı 16/25). Sözlük eşiği bu kümede ayarlandığı için son sayı iyimserdir.
Çıktılar: [`reports/challenge4-v4-dict.md`](reports/challenge4-v4-dict.md).

### Zorluk kümesi 5 (70 çift, bağımsız ölçüm, v4 ile açık)

[`evaluation/challenge5.jsonl`](evaluation/challenge5.jsonl): sözlük katmanı ayarlandıktan sonra, ayara hiç bakılmadan
ölçülen küme. Kategoriler: `öğretilmiş` (11), `yeni_sözcük` (26; eğitimde görülmemiş sözcükler), `koruma` (30; doğru cümleler) ve
`karışık` (3). v4 44/70: öğretilmiş 11/11, görülmemiş sözcük 7/26, koruma 24/30. v4 + sözlük 59/70: öğretilmiş 11/11,
görülmemiş sözcük 20/26, koruma 25/30. Koruma kategorisinde hâlâ 5 doğru cümle bozuluyor; bu, sözlük katmanının
en zayıf yanıdır (aşağıda "Bilinen sınırlar"). Çıktılar: [`reports/challenge5-v4-dict.md`](reports/challenge5-v4-dict.md).

```powershell
.\.venv\Scripts\python.exe evaluation\challenge.py --checkpoint v4 --file evaluation\challenge4.jsonl --dictionary --tag challenge4-v4-dict
.\.venv\Scripts\python.exe evaluation\challenge.py --checkpoint v4 --file evaluation\challenge5.jsonl --dictionary --tag challenge5-v4-dict
```

### v3.2 ve öncesi (byt5-small)

Aşağıdaki sayılar v3.2 ve öncesidir (byt5-small); yerinde bırakıldı. 1.128 çiftlik ayrılmış test kümesinde (`evaluation/evaluate.py --checkpoint best`): 640 Common Voice çifti
ve 488 gündelik konuşma çifti. "Girdiyi kopyala", hiçbir şey değiştirmeyen önemsiz başlangıç değeridir;
"temel ByT5" ise eğitilmemiş `google/byt5-small`. Test kümesi v2'den **bayt bayt aynı** dondurulmuştur
(SHA-256 `43738c61…`), bu yüzden v2, v3, v3.1, v3.2 ve v4 doğrudan karşılaştırılabilir.

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

Her iki depoda da ana dal bu depodaki yeni eğitimi (**v4**: byt5-base + LoRA, 7.000 adım, 70.831 eğitim çifti, iç veri sürümü v3.5)
içerir. Önceki sürümler etiketleriyle yüklenebilir kalır: **v3.2** (byt5-small, 6.500 adım, 55.902 çift, hedefli veri),
**v3.1** (5.000 adım, 42.017 çift, denetlenmiş hedefler), **v3** (5.000 adım, 42.075 çift),
**v2** (4.000 adım, 38.057 çift) ve **v1** (1.800 adım, 32.000 çift).

| Sürüm | Taban | Adım | Eğitim çifti | Erişim |
|---|---|---:|---:|---|
| **v4** | `google/byt5-base` | 7.000 | 70.831 | `main` |
| v3.2 | `google/byt5-small` | 6.500 | 55.902 | `revision="v3.2"` |
| v3.1 | `google/byt5-small` | 5.000 | 42.017 | `revision="v3.1"` |
| v3 | `google/byt5-small` | 5.000 | 42.075 | `revision="v3"` |
| v2 | `google/byt5-small` | 4.000 | 38.057 | `revision="v2"` |
| v1 | `google/byt5-small` | 1.800 | 32.000 | `revision="v1"` |

**Dikkat: v3.2 ve öncesi adaptörler `google/byt5-small` tabanını ister; v4 `google/byt5-base` ister.** Adaptör yanlış tabana
yüklenirse boyutlar uyuşmaz. v4 için:
`PeftModel.from_pretrained(AutoModelForSeq2SeqLM.from_pretrained("google/byt5-base"), "pandakingpunc/megazeka-byt5-tr-spellfix")`.
Eskiler için taban `google/byt5-small` olur ve `revision="v3.2"` (veya `"v3.1"`, `"v3"`, `"v2"`, `"v1"`) eklenir. Sözlük katmanı
**Hugging Face model deposunda değil, bu GitHub kodundadır** (`src/megazeka/dictionary.py`). v3.5 modeli yayınlanmadı. Yayın
kartlarının kaynağı: `release/hf-model/README.md` ve `release/hf-dataset/README.md`.

## In English

Megazeka is a Turkish spelling and typo correction model. **The current release, v4, fine-tunes `google/byt5-base`** with LoRA
(r=16, alpha=32, 10.76M trainable of 592.4M parameters) on 70,831 training pairs (internal data version v3.5, see below);
v3.2 and earlier use `google/byt5-small` (6.26M trainable parameters). The v3.2 data: `google/byt5-small` was fine-tuned with LoRA
on 55,902 synthetically corrupted sentence pairs: 31,932
derived from the CC0 Common Voice Turkish Sentence Collector, 8,792 from project-authored everyday
first/second-person sentences (template-generated with a small conjugator, CC0), 1,272 two-sentence
chunks and 13,906 from a targeted source added in v3.2 (common misspellings, I/İ-initial proper names, and
correct words the model must leave alone). Colloquial noise is rule-based on suffixes ("-eceğim → -icem", "-yorum → -yom", "burada → burda"),
so chat-style forms are corrected for any verb; v3 adds hardened consonants ("gitcez"), "ne yapacağım"
contractions ("napcam"), ~35 common misspellings ("yanlız", "herkez", "şöför") and dropped proper-noun
apostrophes ("Ankaraya"). It ships with an offline Tkinter desktop app:
inference makes no network calls and uses no hosted LLM API.

**Browser demo (local):** a Gradio app in `space/` (`python space/app.py`); there is no hosted demo for now.

On a held-out 1,128-pair test set (frozen byte-identical since v2, so all versions are directly comparable)
v3.2 reduces CER from 0.096 to 0.012 and WER from 0.358 to 0.059 against a copy-the-input baseline, raising
exact match from 25.0% to 78.1% (86.9% on the 488 everyday pairs), while changing 1.1% of already correct
inputs. v3.1 scored 0.0129 CER / 0.0609 WER / 78.0% exact; v3 0.0124 / 0.0612 / 77.5%; v2 0.0137 / 0.0678 /
76.2%.

**v4 (current).** v4 swaps the base model for `google/byt5-base` and trains on the v3.5 data (the v3.2 data plus an approved
target audit, 30 fixes and 109 removals in train, and 15,038 new targeted training pairs; the frozen test is unchanged).
v3.5 itself was never released; it ships for the first time inside v4. An optional, off-by-default dictionary layer
(`--dictionary`, `src/megazeka/dictionary.py`, `zeyrek==0.1.3`) checks model output with a Turkish morphological analyser and,
for words it does not recognise, tries single-edit candidates ranked by the model's own forced-decoding log-probability
(threshold 11 nats). It lives in the GitHub code, not in the Hugging Face model repository.

| Set | v3.2 | v4 | v4 + dictionary |
|---|---:|---:|---:|
| Frozen test exact match (1,128) | 78.1% | 79.3% | **81.6%** |
| Frozen test edit F1 | 0.909 | 0.907 | **0.913** |
| Clean sentences damaged (of 282) | 3 | 6 | 8 |
| challenge (81) | 72 | 77 | 77 |
| challenge2 (66) | 60 | 63 | 63 |
| challenge3 (84) | 59 | 73 | **74** |
| challenge4 (90) | 30 | 62 | **75** |
| challenge4 out-of-list (25) | 1 | 4 | **16** |
| challenge5 (70) | not measured | 44 | **59** |
| challenge5 unseen words (26) | not measured | 7 | **20** |
| challenge5 protection (30) | not measured | 24 | **25** |

Honest reading: a larger base raised general accuracy slightly (78.1% to 79.3% on the frozen test; McNemar p=0.18, at the noise
level) but did **not** change generalisation to unseen words; the dictionary layer did (frozen test 79.3% to 81.6%, 33 fixed, 8 broken,
p=0.0001; challenge5 44 to 59 with no regressions, p=6e-5), at the price of more damaged clean sentences (6 to 8) and about 20%
more inference time. v4 inference is about 1.6x slower than the byt5-small v3.5 model; the base weights are 2.33 GB. challenge3 was
seen during the development of earlier versions (not independent), the dictionary threshold was tuned on challenge4 (that column is
optimistic), and challenge5 was never looked at while tuning (it is the independent measurement). challenge4 and challenge5 are
released with v4. Known limits: candidate ranking is weak (`asensörü` to `sensörü`), the analyser rejects some valid forms
(`ürkeği`, `korkağı`) and the layer damages them, errors two edits away are missed (`dikdörgen`, `profitörol`, `sesizce`), and the
model can corrupt brand names (`Netflix` to `Netfliz`).

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

Releases: `main` = v4 (`google/byt5-base`); tags `v3.2`, `v3.1`, `v3`, `v2` and `v1` stay loadable with `revision="v3.2"` etc. and need `google/byt5-small` as the base.
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

- **Google ByT5-base (v4)**: ByT5-small ile aynı mimari ailesi, daha büyük taban (581.653.248 parametre; Apache-2.0; sabit revizyon `92d8c008d55cf7c254915bac165171dfe6c20c44`). LoRA rank 16 ile eğitilebilir parametre 10.764.288, adaptörle toplam 592.417.536. Ayar `configs/v4.json` (batch 4 × birikim 4, 7.000 adım, öğrenme hızı 5e-4, bfloat16); taban yolu ayardaki `base` alanından okunur (`models/base-byt5-base`). Kaynak: [resmî model kartı](https://huggingface.co/google/byt5-base).
- **Sözlük destekli katman (v4, isteğe bağlı, varsayılan kapalı)**: `--dictionary` ile açılır (`src/megazeka/dictionary.py`; bağımlılık `zeyrek==0.1.3`, `requirements.txt` içinde). Model çıktısında zeyrek biçimbilim çözümleyicisinin tanımadığı sözcük için tek düzenleme uzaklığındaki geçerli adaylar üretilir; adaylar modelin zorlanmış çözümleme log-olasılığıyla puanlanır ve eşik 11 nattır. Arayüz bu katmanı sunmaz; `CorrectionEngine.correct(..., dictionary=True)` ve değerlendirme betikleri kullanır.
- **Google ByT5-small (v3.2 ve öncesi)**: çok dilli, encoder–decoder Transformer; UTF-8 baytlarıyla çalışır. Türkçe karakterleri alt kelime sözlüğüne bağımlı olmadan temsil eder. Bozuk yazımlara uygunluğu nedeniyle seçildi. Kaynak: [resmî model kartı](https://huggingface.co/google/byt5-small), [ByT5 araştırması](https://arxiv.org/abs/2105.13626).
- **LoRA, r=16, alpha=32**: doğrusal katmanlara düşük ranklı eğitilebilir matrisler eklenir. Temel ağırlıklar sabittir; byt5-small'da 6.258.688 parametre eğitilir (temel model yaklaşık 299,6 milyon parametre; adaptörle toplam 305.896.448), byt5-base'de 10.764.288. Bu, bir API sarmalayıcısı veya salt kural sistemi değildir.
- RTX 4060'ta temel model **bfloat16** tutulur; LoRA parametreleri ve AdamW durumları gerektiğinde float32'dir. CPU'da model float32'ye yüklenir. Nicemleme, ONNX ve `torch.compile` eklenmedi: bu ölçek için kurulum/depolama karmaşıklığını artırıyorlar.
- Üretim deterministik açgözlü çözümleme kullanır (`num_beams=1`, `do_sample=False`). Uzun metinler **176 UTF-8 baytını** aşmayan parçalara ayrılır, sessizce kesilmez. En fazla 224 yeni token üretilir. Bu bayt sınırı karakter sınırı değildir.
- Önişleme yalnızca NFC Unicode ve satır sonlarını normalleştirir. Modelden sonra iki katmanlı açık bir koruma filtresi vardır. **Parça filtresi**: karakter düzenleme sayısı girdi uzunluğunu aşarsa (oran > 1,0), çıktı girdi uzunluğunun %65'inden kısaysa, çıktı boşsa veya bitiş tokenı gelmemişse o parça özgün haliyle korunur. Eski %45 eşiği 1.128 çiftlik testte doğru ağır düzeltmelerin çoğunu reddediyordu (düzenleme F1 0,71 → 0,89); gereksiz düzeltme oranı eşikten bağımsız kaldı, bu yüzden gevşetildi. **Kelime kilidi**: kelimeler büyük/küçük harf, Türkçe karakter ve noktalamadan bağımsız hizalanır; bir kelime grubu harf benzerliği olmayan başka bir grupla değiştirilmişse (normalize Levenshtein uzaklığı > 0,6), bir kelime silinmişse veya karşılığı olmayan yeni kelime eklenmişse yalnızca o grup özgün haliyle kalır. Böylece "gidicem → gideceğim" veya "napcam → ne yapacağım" gibi harf benzerliği taşıyan düzeltmeler geçer; "okula → eğitim kurumuna" gibi anlam değiştiren kelime değişimleri geçmez. Filtrenin ham üretimi öğrenme ekranında görünür. Bu filtre anlamın korunmasını garanti etmez; yalnızca kelime düzeyinde eş anlamlı değişimi ve uydurma kelimeyi engeller.

## Depolama sözleşmesi

Tercih edilen toplam **8 GB altında**, kesin üst sınır **15 GB**. **v4 notu:** byt5-base ile bu kurulum 8 GB tercih hedefini aşar (bu makinede proje klasörü yaklaşık 8,6 GB, 1,55 GB ihtiyat payıyla yaklaşık 10,1 GB); 15 GB kesin sınırı ise yeter (`megazeka/storage.py` değiştirilmedi). Buradaki GB ondalıktır (1.000.000.000 bayt). `.venv`, indirmeler, geçici dosyalar, önbellek, veriler ve kayıtlar hesaba katılır. 5 / 8 / 12 GB eşiklerinde uyarı gösterilir. İşlem öncesi öngörülen boyut sınıra ulaşıyorsa işlem başlamaz; indirmede ve eğitimde ayrıca çalışma zamanı denetimi yapılır. İşletim sisteminin sayfa dosyası gibi proje dışındaki otomatik yönetilen alanlar bu sayımda değildir.

`configs/storage.json` önceki iptal edilmiş indirmeden kalan paylaşılan uv önbelleği için **1,55 GB ihtiyat payı** içerir. Bu önbelleğin tamamının projeye ait olduğu iddia edilmez; alan bütçesi açısından tamamı hesaba katılmıştır. Ortak önbelleğe dokunulmaz. Gerçek proje klasörü ve bu ek payla hesaplanan bütçe toplamı ayrı gösterilir.

| Alan | Yaklaşık kalıcı boyut / yaklaşım |
|---|---|
| Python + GPU kütüphaneleri | 4,81 GB; en büyük kalem |
| Temel model | byt5-small: bfloat16 safetensors, yaklaşık 0,60 GB; byt5-base (v4): yaklaşık 2,33 GB |
| Son ve en iyi LoRA | Adaptörler toplam yaklaşık 50 MB; son kaydın optimizer/RNG durumu ayrıca yaklaşık 50 MB |
| Sıkıştırılmış eğitim/veri dosyaları | Yaklaşık 2,3 MB; kaynak metin yaklaşık 1,6 MB |
| Final model | `models/final.json` işaretçisi; ağırlık kopyası yok |
| Önbellek | Projedeki `.cache/`; kurulum geçicileri temizlenir |

PyTorch GPU paketi için indirme **2,53 GB**, açılmış paket ve bağımlılıklar için yaklaşık **5 GB**, kurulum tepe artışı için **8,1 GB** bütçe ayrılır. Bu sığmazsa kurulum betiği otomatik olarak daha küçük CPU paketini seçer. ByT5 için yalnızca seçilen tek taban indirilir: byt5-small için başlangıçtaki bin dosyası **1,199 GB**, dönüştürülmüş bfloat16 dosyası yaklaşık **0,60 GB**; byt5-base (`--base base`) için bin dosyası **2,327 GB**, dönüştürülmüş dosya yaklaşık **2,33 GB** (dönüşümde ikisi bir arada bulunduğu için tepe artış yaklaşık 4,7 GB; temiz kurulumda toplam 12 GB uyarı eşiğine yaklaşabilir, 15 GB sınırının altında kalır). Dönüşümde ikisi kısa süre birlikte bulunur; başarılı kayıttan sonra redundant bin dosyası kaldırılır. 1 GB'dan büyük planlanan işlemler mevcut, ek ve beklenen boyutu konsola yazar.

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
- Temel model: **Apache-2.0**; v4 için `google/byt5-base`, `92d8c008d55cf7c254915bac165171dfe6c20c44` sürümü; v3.2 ve öncesi için `google/byt5-small`, `68377bdc18a2ffec8a0533fef03b1c513a4dd49d` sürümü.
- Projede yazılan kod: `LICENSE` dosyasında MIT. Diğer Python paketleri kendi lisanslarını korur; kurulu dağıtımların `.dist-info` dizinlerinde lisans kayıtları vardır.

`data/raw/source.json`, tam kaynak URL'sini, commit'i ve SHA-256'yı içerir. `data/metadata.json`, küme boyutlarını ve üretilen sıkıştırılmış dosyaların SHA-256 değerlerini tutar.

### Veri üretimi

```powershell
.\.venv\Scripts\python.exe scripts\download.py
.\.venv\Scripts\python.exe training\prepare.py
```

v4'ün verisi (iç sürüm v3.5) iki adımda üretilir: `training\prepare.py` v3.2 verisini üretir, `training\prepare_v35.py` onaylı denetimi ve yeni satırları ekler (aşağıda). v4 tabanını `scripts\download.py --base base` indirir.

3–24 kelimelik, 18–160 UTF-8 baytlık, büyük harfle başlayıp noktalama ile biten cümleler süzülür. NFC ve Türkçe küçük harf dönüşümü yapılmış, noktalaması kaldırılmış anahtarlarla tekilleştirilir. **Gürültü eklenmeden önce** 8.000 / 160 / 160 farklı Common Voice cümlesi eğitim / doğrulama / teste ayrılır. Her hedef için temiz / kolay / orta / zor olmak üzere dört çift hazırlanır.

**v3.5 verisi (v4'ün eğitim verisi).** [`training/prepare_v35.py`](training/prepare_v35.py), v3.2 verisini (`data/v3.2-backup`, git'te yok) alır ve deterministik biçimde üç şey yapar:
(1) onaylı denetimi (`data/audit/v3.5-approved.jsonl`) uygular: eğitimde 30 düzeltme ve 109 çıkarma, doğrulamada 1 düzeltme ve 3 çıkarma;
(2) [`training/v35.py`](training/v35.py) ve ek yazım kataloğu [`training/v35_extra.py`](training/v35_extra.py) içindeki, elle yazılmış açık çiftlerden
**15.038 yeni hedefli eğitim satırı** ekler (yazım 9.196, koruma 4.798, özel ad 515, açık yazım 337, bağlaç 152, noktalama 40;
koruma satırları değiştirilmeden bırakılan doğru cümlelerdir) ve doğrulamaya sabit tohumla 795 satır ekler; (3) dondurulmuş testle ya da
herhangi bir `evaluation/challenge*.jsonl` dosyasıyla çakışan satırları reddeder (eğitimde 2 test, 3 zorluk kümesi, 8 karşı küme çakışması, 41 yineleme). Dondurulmuş test
değişmedi (SHA-256 aynı). Yeni satırların kaynak etiketi `Megazeka v3.5 hedefli / CC0-1.0`'dir; işlem kaydı tek bir `v35_explicit` adımıdır.
Sonuç: eğitim 70.831, doğrulama 3.442, test 1.128 çift.

**Gündelik cümleler.** Common Voice cümleleri edebî ve çoğunlukla üçüncü şahıstır; 32.000 çiftte "gideceğim" yalnızca 8, "geleceğim" 4 kez geçiyordu. Bu yüzden ilk sürüm "gidicem", "gitcez", "yapıcam" gibi biçimleri düzeltemiyordu. `training/everyday.py`, 50 fiillik bir tablo ve küçük bir çekim yardımcısıyla (gelecek zaman, şimdiki zaman, olumsuz, soru eki; ünlü uyumu ve git/et/ye/de özel durumları) birinci/ikinci şahıs gündelik cümleler ile elle yazılmış yaklaşık 250 kısa cümle üretir. Bu cümleler projeye aittir ve CC0-1.0 ile yayınlanır. v3'te üretilen gündelik cümle sayısı 1.470'ten 2.561 benzersiz cümleye çıktı (Common Voice ile çakışanlar atıldıktan sonra 2.526'sı kullanılır). Yaklaşık 1/12'si doğrulamaya ayrılır, test v2'den dondurulmuştur, kalanı eğitime gider; kolay ve orta zorlukta ilk işlem gündelik bir dönüşümdür (mümkünse hedefli işlem: `sert_ünsüz`, `ne_kısalt`, `yazım_yanlışı`, `özel_ad_kesme`). Zorluk kümesinin 81 hedefi eğitim ve doğrulamadan dışlanır.

**Birleşik parçalar.** Eğitim kümesine, aynı zorlukta iki bağımsız çiftin boşlukla birleştirilmesiyle oluşan ve 170 baytı aşmayan çok cümleli örnekler eklenir. Kullanıcı paragraf yapıştırdığında model parça içinde birden çok cümle görür; bu örnekler bunun için vardır.

| Küme | Farklı hedef | Toplam çift | Kaynak dağılımı |
|---|---:|---:|---|
| Eğitim | 13.387 | 55.902 | 31.932 Common Voice · 8.792 gündelik · 1.272 birleşik · 13.906 hedefli |
| Doğrulama | 639 | 2.650 | 640 Common Voice · 800 gündelik · 1.210 hedefli |
| **Eğitim (v3.5, v4)** | 20.756 | 70.831 | v3.2 satırları (139'u denetimle çıkarıldı ya da düzeltildi) + 15.038 v3.5 hedefli |
| **Doğrulama (v3.5, v4)** | 1.261 | 3.442 | v3.2 satırları (4'ü denetimle çıkarıldı ya da düzeltildi) + 795 v3.5 hedefli |
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

v4'ü eğitmek ya da çalıştırmak için tabanı da indirin (yaklaşık 2,33 GB; `megazeka/storage.py` bütçe denetimi geçerlidir): `.\.venv\Scripts\python.exe scripts\download.py --base base`. Varsayılan `--base small`, v3.2 ve öncesinin byt5-small tabanını indirir (davranışı değişmedi). `models/base-byt5-base/` doluysa betik yeniden indirmez.

Python'un Tk bileşeni standart Windows Python kurulumuna dahildir. `scripts/setup.py` proje içi önbellek ve geçici dizinleri ayarlar; `uv --no-cache` kullanır. Python 3.14 yerine 3.12 seçimi, sabitlenmiş ML paketlerinin uyumlu Windows tekerlekleri içindir. Ayrıntılı çalışmış paket listesi `requirements-lock.txt` dosyasındadır.

## Eğitim ve devam etme

```powershell
# Önce kısa deneme: 60 adım
.\.venv\Scripts\python.exe training\train.py --config configs/quick.json

# Sıfırdan tam eğitim: 3.000 adım, 48.000 örnek işlenir; best/latest kayıtlarını değiştirir
.\.venv\Scripts\python.exe training\train.py --config configs/medium.json

# v4: byt5-base + LoRA, 7.000 adım (taban yolu configs/v4.json içindeki base alanından okunur)
.\.venv\Scripts\python.exe training\train.py --config configs/v4.json

# Kesinti sonrası son kayıttan aynı şekilde devam
.\.venv\Scripts\python.exe training\train.py --config configs/medium.json --resume

# İsteğe bağlı: aynı küçük veri üzerinde daha çok eğitim; otomatik başlatılmaz
.\.venv\Scripts\python.exe training\train.py --config configs/quality.json --resume
```

Yayınlanan **v4 modeli** `configs/v4.json` ile (byt5-base, LoRA r=16, öğrenme hızı 5e-4, mikro parti 4 × birikim 4 = etkin parti 16, bfloat16, 7.000 adım) RTX 4060 8 GB'ta 3 saat 4 dakikada eğitildi; en iyi kayıt 6.750. adım, doğrulama kaybı 0,0218 (v3.2'nin kaybıyla doğrudan karşılaştırılamaz: doğrulama kümesi farklıdır). Yayınlanan v3.2 modeli `configs/medium.json` ayarlarıyla (öğrenme hızı 5e-4, LoRA r=16) ve `--steps 6500` ile
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
# v4 ve isteğe bağlı sözlük katmanı
.\.venv\Scripts\python.exe evaluation\evaluate.py --checkpoint v4 --dictionary --tag v4-dict
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
src/megazeka/        gürültü, gündelik kurallar, normalizasyon, çıkarım ve kelime kilidi, isteğe bağlı sözlük katmanı (dictionary.py), metrikler, disk denetimi
training/            veri üretimi, gündelik ve hedefli cümle şablonları, devam edilebilir LoRA eğitimi
evaluation/          ayrılmış test, elle yazılmış beş zorluk kümesi, eşleştirilmiş karşılaştırma ve okunabilir değerlendirme
space/               Gradio tarayıcı demosu (yerel)
configs/             quick / medium / quality / v3.5 / v4 ve depolama bütçesi
data/                tek kaynak, metadata ve sıkıştırılmış çiftler
data/audit/          v3.1 hedef cümle denetimi: ajan işaretleri, kararlar, düzeltme listesi ve rapor
models/base/         byt5-small temel model + tokenizer (v3.2 ve öncesi)
models/base-byt5-base/ byt5-base temel model + tokenizer (v4; git'e girmez)
release/             Hugging Face model ve veri kartlarının kaynağı
models/checkpoints/  yalnızca best / latest
models/final.json    best kaydına işaretçi
reports/             gerçek ölçümler ve eğitim geçmişi
tests/               önemli bileşen ve arayüz kontrolleri
scripts/             bütçeli kurulum/indirme, temizlik ve gerçek UI kontrolü
```

## Bilinen sınırlar ve sonraki deneyler

**v4 ve sözlük katmanının sınırları:**

- **Aday sıralaması zayıf**: sözlük katmanı yanlış adayı seçebilir (`asensörü → sensörü`, `tafsiyesine → tasfiyesine`).
- **Çözümleyici bazı geçerli biçimleri tanımıyor**: zeyrek `ürkeği`, `korkağı` gibi doğru biçimleri tanımadığı için katman bunları bozar. challenge5 koruma kümesinde 30 doğru cümleden 5'i hâlâ bozuluyor.
- **İki düzenleme uzaklığındaki hatalar kaçıyor** (`dikdörgen`, `profitörol`, `sesizce`): katman yalnız tek düzenlemelik adaylar dener.
- **Özel ve marka adları**: model `Netflix → Netfliz`, `Whatsapp → Whatsap` gibi bozabilir.
- **Genelleme**: büyük taban görülmemiş sözcüğe genellemeyi değiştirmedi; bu kazanç yalnızca isteğe bağlı sözlük katmanından gelir ve zeyrek'in kapsamına bağlıdır. challenge4 sütunu eşik ayarı nedeniyle iyimserdir.
- **Maliyet**: v4 çıkarımı v3.5 modelinden yaklaşık 1,6 kat, sözlük katmanı ayrıca yaklaşık %20 yavaştır; taban 2,33 GB'dır ve depolama hedefini (8 GB) aşar.
- **İstatistiksel güç**: donmuş testte v3.2 → v4 farkı gürültü sınırındadır (p=0,18); sözlük farkı anlamlıdır (p=0,0001).

Aşağıdaki liste v3.2 ölçümlerindendir (byt5-small); v4'te bazıları değişmiş olabilir (challenge ve challenge2 sonuçları yukarıdadır).

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
