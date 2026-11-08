# v3.1 hedef cümle denetimi (2026-11-08)

Amaç: eğitim ve doğrulama verisindeki **hedef** (doğru kabul edilen) cümlelerin gerçekten doğru olup olmadığını denetlemek. Hatalı bir hedef, modele yanlış yazımı "doğru" diye öğretir.

## Yöntem

1. `targets.jsonl`: train ve validation içindeki 10.560 benzersiz hedef (8.159 Common Voice, 2.401 gündelik şablon). "Birleşik iki cümle" kayıtları atlandı, çünkü bunlar zaten denetlenen cümlelerden oluşuyor. Test kümesi v2'den dondurulduğu için denetlenmedi ve değiştirilmedi.
2. `chunks/`: cümleler 500'erlik 22 parçaya bölündü.
3. **Tur 1:** 11 Haiku 5.5 alt ajanı parçaları denetledi, sonuçlar `flags/` klasöründe (88 işaret).
4. **Tur 2:** 11 Sonnet 5.5 alt ajanı aynı parçaları güçlendirilmiş bir talimatla (`sonnet_prompt.md`) yeniden denetledi, sonuçlar `flags_sonnet/` klasöründe (206 işaret).
5. Deterministik taramalar:
   - gürültü kurallarının "yanlış" saydığı biçimlerin hedeflerde geçmesi
   - şablon cümlelerde özne ile nesnenin aynı kişi olması
   - kişi adından sonra küçük harfle yazılmış unvan (bey/efendi/hanım)
6. Opus her işareti tek tek okudu. Kararlar kod olarak `build_corrections.py` içinde tutuluyor, çıktısı `corrections.jsonl`.

## Sonuç: 223 kayıt

| Tür | Sayı | Örnek |
|---|---:|---|
| Common Voice düzeltme | 136 | `alttğı → attığı`, `Haşan → Hasan`, `Hiç bir → Hiçbir`, `burda → burada`, `Raif efendinin → Raif Efendi'nin`, `davavekili → dava vekili` |
| Common Voice çıkarma (bozuk, düzeltmesi belirsiz) | 11 | `Mısırların altı günlerden beri sulanmamış` |
| Şablon düzeltme | 3 | `İdil'den bir şey sordum → İdil'e bir şey sordum` |
| Şablon çıkarma (anlamsız) | 73 | `Yakında seni unutur musun?`, `Yarın akşam bana yardım edeceğim, değil mi?` |

Kayıtların 215'i train'de, 8'i validation'da.

Kaynak dağılımı (`found_by` alanı):
- Sonnet tek başına 75 kayıt buldu.
- Haiku ve Sonnet 71 kaydı birlikte buldu.
- Deterministik tarama ve Sonnet 59 kaydı birlikte buldu.
- Yalnız deterministik taramanın bulduğu 12 kayıt var (çoğu unvan düzeltmesi).
- Yalnız Haiku'nun bulduğu 6 kayıt var.

## Bulgular

- **OCR izleri:** Common Voice cümlelerinin bir kısmı taranmış kitaplardan geliyor. "rı" harfleri "n", "rn" harfleri "m", "s" harfi "ş" olarak okunmuş: `memurlan`, `kaşlan`, `başlarmdayım`, `yaşma`, `Haşan`.
- **Kural çelişkisi:** Gürültü üreteci `burada → burda`, `hiçbir → hiç bir` gibi bozmalar yapıyor. Aynı biçimler bazı hedeflerde de geçiyor. Ayrıca `ağabey → abi`, `bilmiyorum → bilmem` ve `tabii → tabi` kuralları geçerli kelimeleri "yanlış" ilan ediyor: "abi", "bilmem" ve "tabi olmak" doğru Türkçe. Bu çelişkiler gereksiz düzeltmenin bir kaynağı olabilir.
- **Şablon hatası:** `training/everyday.py`, nesneleri (`seni/sana/bana`) öznenin kişisine bakmadan seçiyor. Ayrıca "X'den bir şey sordum" gibi yanlış hâl eki üretiyor.

## Haiku ve Sonnet karşılaştırması

| | Haiku 5.5 | Sonnet 5.5 |
|---|---:|---:|
| İşaret sayısı | 88 | 206 |
| Opus'un reddettiği yanlış alarm | ~13 | 1 (+6 tahmine dayalı düzeltme, cümleler çıkarıldı) |
| Şablondaki özne-nesne çakışması | 20 / 67 | ~70 |
| Konuşma dili biçimleri (burda, nerde) | çoğunu atladı | hepsini yakaladı |

- Sonnet'in talimatı Haiku turundan çıkan derslerle güçlendirildi. Bu yüzden karşılaştırma tamamen eşit koşullarda değil.
- Sonnet de 9 kaydı kaçırdı. Bunları Haiku ya da deterministik tarama buldu.

## Test kümesi

282 hedeften 3'ünde aynı sorun var: `şurda burda`, `Şimdi sana soracak mısın?`, `Pazartesi sen sana bir şey diyorsun.` Test kümesi dondurulmuş olduğu için değiştirilmedi.

## Eğitim sonuçları (2026-11-08)

Değişiklikler:
- `prepare.py` düzeltmeleri uyguluyor: 136 düzeltme, 12 çıkarma. Test kümesi bayt bayt aynı kaldı.
- `everyday.py` kişi çakışmasını ve "X'den sordum" hatasını önlüyor.
- `colloquial.py`'den abi, bilmem ve tabi kuralları kaldırıldı.
- `tests/test_v31.py` eklendi, 33 test geçiyor.

Tüm eğitimlerde ayarlar aynı: `configs/medium.json`, 5.000 adım.

**v3.1a:** Çakışmayı önlemek için şablonların rastgele seçim sırası değiştirildi, bu da bütün şablon cümle akışını değiştirdi. Örneğin "yiyecek" geçen hedefler 109'dan 74'e düştü. Model v3'ün gerisinde kaldı: tam eşleşme %76,9, zorluk kümesi 61/81. Kayıtları `models/checkpoints/v3.1a` ve `reports/v3.1a` klasörlerinde.

**v3.1b:** Şablonların rastgele seçim sırası v3'teki gibi bırakıldı. Çakışan nesne ayrı bir üreteçle değiştiriliyor, böylece 2561 şablon cümlenin 2472'si v3'le birebir aynı kaldı. Kayıtları `models/checkpoints/v3.1b` ve `reports/v3.1b` klasörlerinde.

| Dondurulmuş test (1.128 çift) | v3 | v3.1a | v3.1b |
|---|---:|---:|---:|
| Tam eşleşme | %77,5 | %76,9 | **%78,0** |
| WER | 0,0612 | 0,0650 | **0,0609** |
| CER | **0,0124** | 0,0135 | 0,0129 |
| Düzenleme F1 | **0,907** | 0,897 | 0,905 |
| Gereksiz düzeltme | %1,8 (5) | %2,1 | %2,1 (6) |
| Common Voice, tam eşleşme | %70,2 | %69,4 | %70,3 |
| Gündelik, tam eşleşme | %87,1 | %86,7 | **%88,1** |
| Zorluk kümesi (81) | 66 | 61 | **67** |

Yorum:
- v3.1b ile v3 neredeyse aynı düzeyde. Örnek bazında v3'ün bilip v3.1b'nin kaçırdığı 35, tersi 41 örnek var. Net fark +6 örnek; tek bir eğitim koşusunda bu kadarı şansa da çıkabilir.
- Gereksiz düzeltme sayısı 5'e karşı 6 görünüyor, ama örnekler tek tek incelendi. İki modelin de 3 düzeltmesi aslında doğru, çünkü test hedefinin kendisi hatalı: `nerdeyse → neredeyse`, `şurda burda → burada`, `bitpazarı → bit pazarı` (TDK "bit pazarı" diye ayrı yazar). Gerçekten zararlı gereksiz düzeltme ikisinde de 3 tane:
  - v3: `asabidir`, `iltifatkarsınız`, `bitpazarı → bir pazarı`
  - v3.1b: `denecek → deneyecek`, `yabani → yabanı`, `mevkiini → mevkini`
- Dondurulmuş test kümesi eski gürültü kurallarıyla üretildi ve hatalı hedefler içeriyor. Bu yüzden temizliğin faydasını tam ölçemiyor.

Kalan sorun: I/İ ile başlayan özel adlar (Ilgaz, Işık) hâlâ zayıf. Bu kategoride zorluk kümesi sonucu 4/9.
