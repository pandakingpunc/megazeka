import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import json
import time
from megazeka.storage import ROOT, ensure_budget, usage
from megazeka.inference import CorrectionEngine
from megazeka.metrics import measure
from training.prepare import read_pairs

MANUAL = [
 ('bugün okula gidicem ama hava cok kötü galiba', 'Bugün okula gideceğim ama hava çok kötü galiba.'),
 ('yarin arkadaşlarla buluşcaz sonrada sinemaya gidicez', 'Yarın arkadaşlarla buluşacağız, sonra da sinemaya gideceğiz.'),
 ('Bu film baya iyi olmuş.', 'Bu film baya iyi olmuş.'),
 ('Bugün hava çok güzel.', 'Bugün hava çok güzel.'),
 ('Ben de seninle geleceğim.', 'Ben de seninle geleceğim.'),
 ('Ankaraya yarin gidicem.', "Ankara'ya yarın gideceğim."),
 ('herkez buraya gelsin', 'Herkes buraya gelsin.'),
 ('Beni duyuyormusun?', 'Beni duyuyor musun?'),
 ('Bu gerçekten güzel bir haber.', 'Bu gerçekten güzel bir haber.'),
 ('Merhaba!\n\nNasılsın?', 'Merhaba!\n\nNasılsın?'),
 ('Cok tesekkur ederim.', 'Çok teşekkür ederim.'),
 ('Işık, İstanbul’a yarın gelecek.', 'Işık, İstanbul’a yarın gelecek.'),
 ('yarın okula gidicem', 'Yarın okula gideceğim.'),
 ('bugün sinemaya gitcez sonra yemek yiycez', 'Bugün sinemaya gideceğiz sonra yemek yiyeceğiz.'),
 ('Yapıcam dedim ama yapmıcam.', 'Yapacağım dedim ama yapmayacağım.'),
 ('gelicem ama biraz geç olcak', 'Geleceğim ama biraz geç olacak.'),
 ('bilmiyom ki napcam', 'Bilmiyorum ki ne yapacağım.'),
 ('yanlız kaldım burda', 'Yalnız kaldım burada.'),
 ('napıyosun bugun', 'Ne yapıyorsun bugün?'),
 ("İstanbul'a gidicem ve orda kalıcam.", "İstanbul'a gideceğim ve orada kalacağım."),
 ('Okula gideceğim.', 'Okula gideceğim.'),
 ('Ben de seninle geleceğim, sen de gelir misin?', 'Ben de seninle geleceğim, sen de gelir misin?'),
 ('Yarın arkadaşlarımla sinemaya gideceğiz.', 'Yarın arkadaşlarımla sinemaya gideceğiz.'),
]
# Correct sentences that must stay unchanged; guards against paraphrase-like rewrites.
UNCHANGED = [t for _, t in MANUAL if _ == t]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', choices=['base', 'best', 'latest'], default='best')
    parser.add_argument('--limit', type=int, default=640)
    args = parser.parse_args()
    ensure_budget(10_000_000, 'Değerlendirme raporu')
    engine = CorrectionEngine(args.checkpoint)
    source = read_pairs('test')[:args.limit]
    rows = []
    started = time.perf_counter()
    for offset in range(0, len(source), 8):
        batch = source[offset:offset+8]
        results = engine.correct_batch([r['input'] for r in batch])
        for row, result in zip(batch, results):
            rows.append({**{k: row[k] for k in ['input', 'target', 'difficulty', 'source']},
                         'output': result['output'], 'raw_output': result['raw_output'], 'warnings': result['warnings']})
        if (offset + 8) % 40 == 0:
            print(f'Değerlendirme {min(offset+8, len(source))}/{len(source)}', flush=True)
    manual = []
    for text, target in MANUAL:
        result = engine.correct(text, inspect=False)
        manual.append({'input': text, 'target': target, 'output': result['output'], 'raw_output': result['raw_output']})
    subsets = {}
    for name, keep in [('common_voice', lambda r: r['source'].startswith('Common Voice')),
                       ('gündelik', lambda r: r['source'].startswith('Megazeka'))]:
        chosen = [r for r in rows if keep(r)]
        if chosen:
            subsets[name] = {'metrics': measure(chosen), 'raw_metrics': measure([{**r, 'output': r['raw_output']} for r in chosen]),
                             'identity_baseline': measure([{**r, 'output': r['input']} for r in chosen])}
    report = {'checkpoint': args.checkpoint, 'metrics': measure(rows), 'subsets': subsets,
              'raw_metrics': measure([{**r, 'output': r['raw_output']} for r in rows]),
              'identity_baseline': measure([{**r, 'output': r['input']} for r in rows]),
              'manual_metrics': measure(manual), 'manual': manual, 'examples': rows,
              'seconds': time.perf_counter()-started, 'model_info': engine.info, 'storage': usage(),
              'note': 'Sentetik test; karakter düzenleme F1; manuel örnekler eğitim dışında. Modelin ön eğitim verileriyle olası örtüşme bilinmiyor.'}
    path = ROOT / f'reports/evaluation-{args.checkpoint}.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# Megazeka değerlendirmesi', '', '```json', json.dumps(report['metrics'], ensure_ascii=False, indent=2), '```', '']
    for name, values in subsets.items():
        lines.extend([f'## Alt küme: {name} ({values["metrics"]["examples"]} çift)', '', '```json',
                      json.dumps({'filtreli': values['metrics'], 'ham': values['raw_metrics'], 'girdiyi_kopyala': values['identity_baseline']}, ensure_ascii=False, indent=2), '```', ''])
    lines += [
             'Düzenleme hassasiyeti/duyarlılığı, orijinal karakter konumlarına bağlı Levenshtein işlem kümeleriyle ölçülür.', '']
    categories = {'Başarılı düzeltmeler': [r for r in rows if r['input'] != r['target'] and r['output'] == r['target']],
                  'Yanlış düzeltmeler': [r for r in rows if r['input'] == r['target'] and r['output'] != r['target']],
                  'Kaçırılan düzeltmeler': [r for r in rows if r['input'] != r['target'] and r['output'] == r['input']],
                  'Zor örnekler': [r for r in rows if r['difficulty'] == 'zor' and r['output'] != r['target']],
                  'Manuel örnekler': manual}
    for title, examples in categories.items():
        lines.extend(['## ' + title, ''])
        if not examples:
            lines.append('Bu kategoride örnek yok.')
        for row in examples[:12]:
            lines.extend(['```text', 'GİRDİ: ' + row['input'], 'MODEL: ' + row['output'], 'HEDEF: ' + row['target'], '```', ''])
    (ROOT / f'reports/evaluation-{args.checkpoint}.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in ['examples', 'manual']}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
