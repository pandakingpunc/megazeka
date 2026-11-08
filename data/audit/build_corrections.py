"""Megazeka v3.1 hedef cümle denetimi: Haiku işaretleri + deterministik tarama, Opus tarafından tek tek doğrulandı.
Çıktı: corrections.jsonl  {"target": eski, "action": "fix"|"drop", "fix": yeni|null, "reason": ..., "found_by": ...}
"""
import json, glob, re
from pathlib import Path
HERE = Path(__file__).parent
targets = [json.loads(l) for l in open(HERE/'targets.jsonl', encoding='utf-8')]
by_text = {r['target']: r for r in targets}

# Haiku işaretlerinden REDDEDİLENLER (yanlış alarm; cümle doğru)
REJECT = {
    'Derhal yumuşak fakat kati bir hareketle kolunu çekti.': 'kati = kesin; doğru',
    'Ben asıl Praglıyım, Çek Almanlarından.': '-lı yapım eki kesme almaz',
    'Dalan gözlerini dikilmiş olduğu bir noktadan ayırdı.': 'dalan sıfat-fiil; geçerli',
    'Fakat bütün emekler beyhude yere gidiyor, efe kımıldayabilecek derecede bir takat gösteremiyordu.': 'efe = karakter; geçerli',
    'Nasılsınız efendim? yollu bir hatır sormadan başka bir şey gördüğü yoktu.': 'alıntı + yollu; geçerli',
    'Ne yap biliyor musun?': 'konuşma dili yapısı; geçerli',
    'Samsun da hapishane, burası da hapishaneydi.': 'da bağlaç; doğru',
    'Sesi çıkmaz olduydu.': 'hikâye bileşik zamanı; geçerli',
    'Sonra kürk mantosunu sırtına geçiriyor, merdivenlerden ağır ağır indiriyordum!': 'indirmek (onu); geçerli',
    'Sorunun ne biliyor musun?': 'konuşma dili; geçerli',
    'Bu akşam akşam yemeğini pişirecek.': 'bu akşam + akşam yemeği; doğru',
}
# Haiku düzeltmesi yanlış/eksik olanlar: düzeltilmiş hali
OVERRIDE_FIX = {
    'Her sey yolunda mi?': 'Her şey yolunda mı?',
    'Hulasa bir başka türlü olmuşsun.': 'Hülasa bir başka türlü olmuşsun.',
    'Hulasa, uzatmayalım, bu hastaneye ambar katibi olarak girdik.': 'Hülasa, uzatmayalım, bu hastaneye ambar katibi olarak girdik.',
}
# Düzeltmesi belirsiz: cümleyi çıkar
DROP_UNSURE = {
    'Birkaç ay beraber yaşadıktan sonra kış vakası geldi.',
    'Fakat Esma, yirmi dört yaşın derin uykusundan kolay kolay uyarlamıyordu.',
    'Fakat bu evette benim anlayamadığım bir şeyler de gizli gibiydi.',
    'Macide’ye uzun uzun batıktan sonra yerinden kalktı.',
}
# Deterministik tarama + Opus: Haiku'nun kaçırdığı konuşma dili biçimleri (gürültü kurallarıyla çelişir)
EXTRA_FIX = {
    'Ben nerden bileyim?': 'Ben nereden bileyim?',
    'Bu panayırın en büyük hünerleri içerde.': 'Bu panayırın en büyük hünerleri içeride.',
    'Burda bir makale var, belki sizi alakadar eder.': 'Burada bir makale var, belki sizi alakadar eder.',
    'Böyle deme, burda kal.': 'Böyle deme, burada kal.',
    'Bırak efendi, Allahını seversen, sulfata nerde?': "Bırak efendi, Allah'ını seversen, sulfata nerede?",
    'Neler oluyor burda?': 'Neler oluyor burada?',
    'Nerde birlik, orda dirlik.': 'Nerede birlik, orada dirlik.',
    'Nerde hareket, orda bereket.': 'Nerede hareket, orada bereket.',
    'Neren ağrırsa canın orda.': 'Neren ağrırsa canın orada.',
    'Süt veriyor, biz burda her akşam sarhoşuz.': 'Süt veriyor, biz burada her akşam sarhoşuz.',
    'İyi ama doktor, bin liranın yolu nerde?': 'İyi ama doktor, bin liranın yolu nerede?',
    'İçerde ama, bugün görüşme günü değil.': 'İçeride ama, bugün görüşme günü değil.',
    'İçerde bir kıpırdama oldu.': 'İçeride bir kıpırdama oldu.',
    'İçerde, kulübesinde; bak, sesi geliyor!': 'İçeride, kulübesinde; bak, sesi geliyor!',
    'Şurdan burdan topladığı kemikleri oyuncak gibi bir araya getirdi ve seyretti.': 'Şuradan buradan topladığı kemikleri oyuncak gibi bir araya getirdi ve seyretti.',
    'Sora yüzünü Recep\'in yüzüne yaklaştırdı.': 'Sonra yüzünü Recep\'in yüzüne yaklaştırdı.',
}
out = {}
def add(t, action, fix, reason, by):
    if t not in by_text:
        print('YOK:', t); return
    out[t] = {'id': by_text[t]['id'], 'split': by_text[t]['split'], 'source': by_text[t]['source'],
              'target': t, 'action': action, 'fix': fix, 'reason': reason, 'found_by': by}

for f in sorted(glob.glob(str(HERE/'flags'/'*.jsonl'))):
    for line in open(f, encoding='utf-8'):
        if not line.strip(): continue
        r = json.loads(line); t = r['target']
        if t in REJECT: continue
        if t in DROP_UNSURE or r['type'] == 'anlamsiz' or not r.get('fix'):
            add(t, 'drop', None, r.get('note', ''), 'haiku+opus')
        else:
            add(t, 'fix', OVERRIDE_FIX.get(t, r['fix']), r.get('note', ''), 'haiku+opus')
for t, fx in EXTRA_FIX.items():
    if t not in out: add(t, 'fix', fx, 'konuşma dili biçimi; gürültü kuralıyla çelişir', 'deterministik+opus')

# Şablon özne-nesne çakışması (sen ... seni/sana; ben ... bana)
CLASH = [(r'\b(seni|sana|seninle)\b', r'(sın|sin|sun|sün)[?.!]?$|(acaksın|eceksin|[ıiuü]yorsun|mısın|misin|musun|müsün)\b'),
         (r'\b(beni|bana|benimle)\b', r'(acağım|eceğim|[ıiuü]yorum)\b')]
for r in targets:
    if not r['source'].startswith('Megazeka'): continue
    c = r['target'].split(',')[-1].strip()
    for o, v in CLASH:
        if re.search(o, c) and re.search(v, c.lower()) and r['target'] not in out:
            add(r['target'], 'drop', None, 'şablon: özne ve nesne aynı kişi', 'deterministik+opus')
for t in ['Bu pantolon bana büyük geldi sanırım.']:
    out.pop(t, None)  # yanlış eşleşme; cümle doğru


# ---- Tur 2: Sonnet 5.5 denetimi (flags_sonnet/), Opus doğrulaması ----
SONNET_REJECT = {
    'Bu taraklarda hiç bezi olmayan arkadaşımın birdenbire hovardalığa kalkmış olmasına ihtimal verilemezdi.': '"bu tarakta bezi olmamak" deyimi; doğru',
}
SONNET_DROP = {  # bozuk cümle; önerilen düzeltme tahmin
    'Bütün ihtiyatına rağmen onun yüzüne çarpan bir kılıcı siyah örtüsünü düşürdü.',
    'Efe, karşısında kordonla ile titreyen Abdülhamit\'in yâverine güzel bir ders vermişti.',
    'Macide’nin gözleri aynadaki hayali üzerinde süratle dolaştırdıktan sonra saçlarına takılıp kaldı.',
    'Mısırların altı günlerden beri sulanmamış, yapraklar sararmaya yüz tutmuştu.',
    'Ne gezer? Hiçbir şeyler dimedi!',
    'Ne geçmişi, ne geleceği düşünmüyor, ancak yaşamakta olduğum anları biliyordum.',
}
SONNET_OVERRIDE = {
    'Ben Bu akşam sizinle dans etmeyeceğim Nurullah bey.': 'Ben bu akşam sizinle dans etmeyeceğim, Nurullah Bey.',
    'Sevgililer günün kutlu olsun.': 'Sevgililer Günün kutlu olsun.',
}
for f in sorted(glob.glob(str(HERE/'flags_sonnet'/'*.jsonl'))):
    for line in open(f, encoding='utf-8'):
        if not line.strip(): continue
        r = json.loads(line); t = r['target']
        if t in SONNET_REJECT or t in REJECT: continue
        if t in out:
            if t in SONNET_OVERRIDE: out[t]['fix'] = SONNET_OVERRIDE[t]
            out[t]['found_by'] += '+sonnet'
            continue
        if t in SONNET_DROP or r['type'] == 'anlamsiz' or not r.get('fix'):
            add(t, 'drop', None, r.get('note', ''), 'sonnet+opus')
        else:
            add(t, 'fix', SONNET_OVERRIDE.get(t, r['fix']), r.get('note', ''), 'sonnet+opus')

# Unvan: Ad + bey/efendi/hanım küçük harfle -> TDK (Raif Efendi, Nurettin Bey'le)
NAMES = 'Raif|Nurullah|Hanife|Emine|Nurettin|Hüsamettin|Hüseyin|Mihriye|Hafız'  # elle doğrulanmış kişi adları
TITLE = re.compile(r"\b(" + NAMES + r") (bey|efendi|hanım)(nin|in|ın|den|dan|le|la|e|a|i|ı|yi|ye)?(?![\wçğıöşü])")
def fix_titles(t):
    def rep(m):
        name, title, suf = m.groups()
        T = {'bey': 'Bey', 'efendi': 'Efendi', 'hanım': 'Hanım'}[title]
        return f"{name} {T}" + (f"'{suf}" if suf else '')
    return TITLE.sub(rep, t)
for r in targets:
    base = out[r['target']]['fix'] if r['target'] in out and out[r['target']]['action'] == 'fix' else r['target']
    if r['target'] in out and out[r['target']]['action'] == 'drop': continue
    new = fix_titles(base)
    if new != base:
        if r['target'] in out: out[r['target']]['fix'] = new
        else: add(r['target'], 'fix', new, 'unvan büyük harf (TDK)', 'deterministik+opus')

rows = sorted(out.values(), key=lambda r: r['id'])
with open(HERE/'corrections.jsonl', 'w', encoding='utf-8') as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
from collections import Counter
print(len(rows), Counter((r['action'], r['source'][:12]) for r in rows), Counter(r['split'] for r in rows))
