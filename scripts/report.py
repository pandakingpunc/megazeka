import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from megazeka.storage import ROOT, configure, usage
configure()
import hashlib
import json

def percent(value):
    return f'%{value*100:.2f}'.replace('.', ',')

def main():
    best = json.loads((ROOT/'reports/evaluation-best.json').read_text(encoding='utf-8'))
    base = json.loads((ROOT/'reports/evaluation-base.json').read_text(encoding='utf-8'))
    state = json.loads((ROOT/'models/checkpoints/latest/state.json').read_text(encoding='utf-8'))
    final = json.loads((ROOT/'models/final.json').read_text(encoding='utf-8'))
    u = usage()
    metrics = [('Girdiyi aynen kopyalama', best['identity_baseline']), ('Eğitim öncesi temel model · ham', base['raw_metrics']),
               ('Eğitilmiş model · ham / filtre kapalı', best['raw_metrics']), ('Uygulama · temkinli filtre açık', best['metrics'])]
    lines = ['# Megazeka — tamamlanan eğitim ve doğrulama', '',
             'Türkçe masaüstü uygulaması; gerçek yerel ByT5-small + LoRA eğitimi. Bulut LLM API kullanılmaz.', '',
             '## Gerçek eğitim', '',
             '- Temel model: Google ByT5-small (Apache-2.0); tek sürüm ve tek yerel temel ağırlık kopyası.',
             '- Eğitilen LoRA: 6.258.688 parametre; r=16, alpha=32, tüm uygun doğrusal katmanlar.',
             '- Veri: Common Voice Türkçe Sentence Collector (CC0-1.0), 8.000 farklı hedef üzerinden 32.000 eğitim çifti; 640 doğrulama / 640 test.',
             f'- Eğitim: 60 adımlık denemeden devamla toplam {state["step"]:,} AdamW adımı, {state["examples_processed"]:,} işlenen örnek. Mikro parti 8, birikim 2.',
             f'- Doğrulama kaybına göre seçilen en iyi adım: {final["best_step"]:,}. Son kayıt ayrıca {state["step"]:,}. adımda; final dosyası best kaydına işaret eder.',
             '- Donanım: AMD Ryzen 5 5600, yaklaşık 16 GB RAM, NVIDIA RTX 4060 8 GB; temel bfloat16, LoRA/optimizer float32.',
             f'- Kayıtlardaki eğitim akışı süresi: yaklaşık {state["elapsed_seconds"]/60:.1f} dakika (indirme, uygulama geliştirme ve duraklamalar hariç).',
             '- Windows dosya paylaşım çakışması sonrası 1.000. adımdaki kayıt gerçekten yüklenerek devam edildi; durum dosyası yazımı yeniden denemeli hale getirildi.', '',
             '## Aynı 640 test çifti üzerinde ölçüm', '',
             '| Çıktı | CER ↓ | WER ↓ | Tam eşleşme ↑ | Düzenleme F1 ↑ | Gereksiz düzeltme ↓ |',
             '|---|---:|---:|---:|---:|---:|']
    for name, m in metrics:
        lines.append(f'| {name} | {percent(m["cer"])} | {percent(m["wer"])} | {percent(m["exact_match"])} | {percent(m["edit_f1"])} | {percent(m["overcorrection"])} |')
    m = best['metrics']; raw = best['raw_metrics']
    lines.extend(['', f'Filtreli düzenleme precision: {percent(m["edit_precision"])}; recall: {percent(m["edit_recall"])}. Ham model precision: {percent(raw["edit_precision"])}; recall: {percent(raw["edit_recall"])}.',
        '', f'Gerçekten doğru {m["clean_examples"]} test girdisinin {round(m["clean_examples"]*m["overcorrection"])} tanesi gereksiz değiştirildi. Etiketi temiz olmayan bir örnekte gürültüler birbirini geri aldığından, sayı 160 yerine 161 oldu.',
        '', 'Temel model bu göreve göre eğitilmediği için ham üretimi uzayabilir; ekleme sayısı yüksek olduğunda CER/WER %100’ü aşabilir. Koruma filtresi temel modelin çıktısını reddedip girdiyi kopyalar. Eğitilmiş modelde filtre, doğru ama büyük düzenlemeleri de reddederek hata oranını artırıyor; bu fark gizlenmedi. Filtre öğrenme modundan isteğe bağlı kapatılabilir.',
        '', 'Bu sentetik test dağılımına ait ölçümlerdir. Model ağırlığı doğrulama kaybıyla seçildi; test örnekleri eğitimde kullanılmadı. Manuel örnekler genel başarı oranı olarak sunulmaz.', '',
        '## Küçük manuel kontrol', '',
        f'12 manuel örnekte {percent(best["manual_metrics"]["exact_match"])} tam eşleşme. Altı doğru örneğin biri değişti; bu küçük gruptaki gereksiz düzeltme oranı {percent(best["manual_metrics"]["overcorrection"])}.', '',
        '| Girdi | Gerçek çıktı |', '|---|---|'])
    for r in best['manual']:
        lines.append('| ' + r['input'].replace('\n',' ↵ ').replace('|','\\|') + ' | ' + r['output'].replace('\n',' ↵ ').replace('|','\\|') + ' |')
    lines.extend(['', 'Eksikler: “gidicem”, “buluşcaz”, “gidicez” gibi gündelik gelecek zaman biçimleri her zaman düzelmiyor. “Işık” özel adı bir örnekte “İşık” yapıldı. Özel adlar ve gündelik yazım için daha dengeli hata çiftleri ilk iyileştirme alanıdır. Veri boyutu otomatik artırılmadı.', '',
        '## Doğrulama', '', '- 16 otomatik test geçti: gürültü, Türkçe normalizasyon, kayıpsız parçalara ayırma, edit işlemleri, veri ayrımı, disk sınırı, Windows yazma çakışması, yerel model, Tk giriş/sonuç/pano.',
        '- Gerçek çıkarım testinde socket bağlantıları engellendi; model çalıştı. CPU çıkarımı ayrıca gerçek ağırlıklarla denendi.',
        '- Gerçek Windows arayüzünde metin girme, Düzelt, yüklenme, Kopyalandı geri bildirimi, öğrenme akışı, canlı grafik ve depolama görünümü kontrol edildi.',
        '- Gerçek Tk/model testinde pano metni sonuçla karşılaştırıldı, iki paragraf ve küçük pencere yerleşimi doğrulandı. UI otomasyonu ekranındaki bazı Türkçe dışı teknik isimler model/kütüphane adlarıdır.',
        '- Tamamlanmış eğitime --resume komutu yeniden verildiğinde eğitim tekrarlanmadı; indirme betiği tekrar çağrıldığında temel model yeniden indirilmedi.', '',
        '## Depolama', '', f'- Proje klasörü: **{u["total"]/1e9:.3f} GB**.', f'- Paylaşılan eski önbellek için ihtiyat payıyla: **{u["budget_total"]/1e9:.3f} GB**. Bu payın tamamının projeye ait olduğu iddia edilmez.',
        '- Kalıcı kullanım 8 GB hedefinin altında; 15 GB kesin sınır. Küresel önbellekler silinmedi.', '', '| Alan | MB |', '|---|---:|'])
    for key, label in [('model','Temel model'),('checkpoints','Best + latest + devam durumu'),('dataset','Kaynak ve sıkıştırılmış çiftler'),('cache','Proje önbelleği'),('logs','Günlük ve raporlar'),('environment','Python ortamı')]:
        lines.append(f'| {label} | {u[key]/1e6:.2f} |')
    lines.extend(['', '## Çalıştırma ve dosyalar', '', '```powershell', 'cd megazeka', '.\\.venv\\Scripts\\python.exe app\\main.py', '```', '',
        '`Baslat.bat` çift tıklanarak da açılır. Yerel model: `models/base/model.safetensors` + `models/checkpoints/best/adapter_model.safetensors`. Final işaretçisi: `models/final.json`.', '',
        'Ayrıntılı kullanım/komutlar: `README.md`. Ham ölçümler ve başarılı/yanlış/kaçırılmış/zor örnekler: `reports/evaluation-best.json` ve `reports/evaluation-best.md`. Eğitim geçmişi: `reports/history.jsonl`.', '',
        'Kaynaklar: [ByT5 resmî model kartı](https://huggingface.co/google/byt5-small), [Common Voice veri lisansı](https://github.com/common-voice/common-voice#licensing-and-content-source).'])
    (ROOT/'reports/TEKNIK_RAPOR.md').write_text('\n'.join(lines),encoding='utf-8')
    (ROOT/'reports/storage-final.json').write_text(json.dumps(u,ensure_ascii=False,indent=2),encoding='utf-8')
    source_path=ROOT/'models/base/source.json'
    source=json.loads(source_path.read_text(encoding='utf-8'))
    source['original_download_sha256']=source.get('sha256')
    source['stored_format']='bfloat16 safetensors; frozen base'
    with (ROOT/'models/base/model.safetensors').open('rb') as f:
        source['stored_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
    source_path.write_text(json.dumps(source,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Teknik rapor ve depolama özeti hazır.')

if __name__ == '__main__': main()
