import gzip
import json
import tkinter as tk
from tkinter import ttk
from megazeka.storage import ROOT, usage
from .widgets import BG, CARD, TEXT, MUTED, ACCENT, table, text_area, set_text, plot

class Dashboard(ttk.Frame):
    def __init__(self, parent, train_callback, stop_callback):
        super().__init__(parent, padding=14)
        top = ttk.Frame(self); top.pack(fill='x', pady=(0, 8))
        self.status = ttk.Label(top, text='Eğitim durumu okunuyor...', wraplength=800)
        self.status.pack(side='left', fill='x', expand=True)
        ttk.Button(top, text='60 adım eğit', command=train_callback).pack(side='right', padx=4)
        ttk.Button(top, text='Kaydet ve durdur', command=stop_callback).pack(side='right', padx=4)
        self.progress = ttk.Progressbar(self); self.progress.pack(fill='x', pady=8)
        grid = ttk.Frame(self); grid.pack(fill='both', expand=True)
        self.plots = []
        for index, (key, title) in enumerate([('loss', 'Eğitim kaybı'), ('validation_loss', 'Doğrulama kaybı'),
                        ('cer', 'Karakter hata oranı · CER'), ('wer', 'Kelime hata oranı · WER'),
                        ('overcorrection', 'Gereksiz düzeltme oranı')]):
            canvas = tk.Canvas(grid, bg=CARD, height=155, highlightthickness=0)
            canvas.grid(row=index//3, column=index%3, sticky='nsew', padx=4, pady=4)
            self.plots.append((canvas, key, title))
        for col in range(3): grid.columnconfigure(col, weight=1)
        for row in range(2): grid.rowconfigure(row, weight=1)
        ttk.Label(self, text='Grafiklerdeki üretim ölçümleri sabit 16 doğrulama örneğidir; küçük örneklem dalgalanabilir.\nTam değerlendirme raporu ayrı test kümesini kullanır. Girdi metinleriniz kaydedilmez.', style='Muted.TLabel').pack(anchor='w', pady=8)

    def refresh(self):
        path = ROOT / 'reports/training_status.json'
        if path.exists():
            try:
                s = json.loads(path.read_text(encoding='utf-8'))
                state = 'Çalışıyor' if s.get('running') else 'Tamamlandı / durduruldu'
                self.status.configure(text=f"{state}  ·  Adım {s['step']}/{s.get('total_steps', '?')}  ·  Tur {s.get('epoch', 0):.2f}\nKayıp {s.get('loss', 0):.4f}  ·  Öğrenme hızı {s.get('learning_rate', 0):.6f}  ·  {s.get('examples_processed', 0):,} örnek  ·  {s.get('elapsed_seconds', 0)/60:.1f} dakika\nEn iyi adım: {s.get('best_step', 'Henüz yok')}  ·  Kalan adım: {s.get('remaining_steps', '?')}")
                self.progress.configure(maximum=s.get('total_steps', 1), value=s['step'])
            except (ValueError, KeyError):
                pass
        path = ROOT / 'reports/history.jsonl'
        history = []
        if path.exists():
            for line in path.read_text(encoding='utf-8').splitlines():
                try: history.append(json.loads(line))
                except ValueError: pass
        for canvas, key, title in self.plots:
            plot(canvas, history, key, title)

class StoragePanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        ttk.Label(self, text='Disk alanı da bir model kaynağıdır.', style='Heading.TLabel').pack(anchor='w')
        ttk.Label(self, text='Hedef < 8 GB  ·  Kesin üst sınır 15 GB  ·  GB = 1.000.000.000 bayt\nOrtam, önbellek ve geçici dosyalar toplamın içindedir.', style='Muted.TLabel').pack(anchor='w', pady=10)
        self.total = ttk.Label(self, text='', style='Heading.TLabel'); self.total.pack(anchor='w', pady=8)
        self.bar = ttk.Progressbar(self, maximum=15); self.bar.pack(fill='x', pady=8)
        frame, self.table = table(self, ['Kategori', 'Boyut (GB)', 'Boyut (MB)'], [300, 160, 160], height=8)
        frame.pack(fill='both', expand=True, pady=10)
        self.warning = ttk.Label(self, text='', foreground='#f4bc77', wraplength=950); self.warning.pack(anchor='w')
        ttk.Button(self, text='Disk kullanımını yenile', command=self.refresh).pack(anchor='w', pady=10)
        ttk.Label(self, text='Yalnızca bu projenin alanı temizlenir. Başka projelerin küresel önbelleklerine dokunulmaz.\nFinal model, en iyi LoRA kaydını kullanır; üçüncü bir ağırlık kopyası oluşturulmaz.', style='Muted.TLabel').pack(anchor='w')

    def refresh(self):
        u = usage()
        self.total.configure(text=f"Proje {u['total']/1e9:.3f} GB · dış önbellek payıyla {u['budget_total']/1e9:.3f} GB / 15 GB")
        self.bar.configure(value=u['budget_total']/1e9)
        self.table.delete(*self.table.get_children())
        names = {'model': 'Temel model', 'dataset': 'Veri kümesi', 'checkpoints': 'Kontrol noktaları / final',
                 'cache': 'Projeye ait önbellek ve geçici dosyalar', 'logs': 'Günlükler ve raporlar',
                 'environment': 'Python ortamı / kütüphaneler', 'other': 'Kod ve diğer dosyalar',
                 'external_reserve': 'Paylaşılan eski önbellek için ihtiyatlı pay'}
        for key, label in names.items():
            self.table.insert('', 'end', values=(label, f'{u[key]/1e9:.4f}', f'{u[key]/1e6:.2f}'))
        self.warning.configure(text=' · '.join(u['warnings']) or 'Depolama sınırları içinde.')

class DatasetPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=14)
        top = ttk.Frame(self); top.pack(fill='x')
        ttk.Label(top, text='Veri kümesini incele', style='Heading.TLabel').pack(side='left')
        self.split = tk.StringVar(value='Eğitim')
        combo = ttk.Combobox(top, values=['Eğitim', 'Doğrulama', 'Test'], textvariable=self.split, state='readonly', width=15)
        combo.pack(side='right'); combo.bind('<<ComboboxSelected>>', self.load)
        ttk.Label(self, text='Her örnekte temiz hedef, üretilen gürültü ve uygulanan gerçek işlemler bulunur.', style='Muted.TLabel').pack(anchor='w', pady=10)
        frame, self.box = text_area(self, height=12, readonly=True); frame.pack(fill='both', expand=True)
        bottom = ttk.Frame(self); bottom.pack(fill='x', pady=10)
        ttk.Button(bottom, text='Önceki', command=lambda: self.move(-1)).pack(side='left')
        ttk.Button(bottom, text='Sonraki', command=lambda: self.move(1)).pack(side='left', padx=7)
        self.counter = ttk.Label(bottom, text=''); self.counter.pack(side='right')
        self.rows = []; self.index = 0
        self.load()

    def load(self, event=None):
        split = {'Eğitim': 'train', 'Doğrulama': 'validation', 'Test': 'test'}[self.split.get()]
        path = ROOT / f'data/processed/{split}.jsonl.gz'
        if path.exists():
            with gzip.open(path, 'rt', encoding='utf-8') as stream:
                self.rows = [json.loads(line) for line in stream]
        self.index = 0; self.move(0)

    def move(self, delta):
        if not self.rows:
            set_text(self.box, 'Veri kümesi henüz hazırlanmadı.'); return
        self.index = (self.index + delta) % len(self.rows)
        row = self.rows[self.index]
        content = f"TEMİZ HEDEF\n{row['target']}\n\nGÜRÜLTÜLÜ GİRDİ\n{row['input']}\n\nZorluk: {row['difficulty']}\nKaynak: {row['source']}\nGrup kimliği: {row['group_id']}\n\nGERÇEK BOZMA İŞLEMLERİ\n"
        for op in row['operations']:
            content += f"\n• {op['operation']}\n  Önce: {op['before']}\n  Sonra: {op['after']}\n"
        if not row['operations']: content += '\nDeğişiklik yok: model doğru metni korumayı öğrenir.'
        set_text(self.box, content); self.counter.configure(text=f'{self.index+1:,} / {len(self.rows):,}')
