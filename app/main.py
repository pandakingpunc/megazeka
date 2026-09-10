import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from megazeka.storage import ROOT, configure
configure()
import gc
import json
import queue
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from app.widgets import theme, text_area, set_text, TEXT, MUTED, ACCENT
from app.inspection import Inspection
from app.dashboard import Dashboard, StoragePanel, DatasetPanel

class MegazekaApp:
    def __init__(self, root, engine_factory=None):
        self.root = root
        self.engine_factory = engine_factory
        self.engine = None
        self.engine_revision = None
        self.busy = False
        self.events = queue.Queue()
        self.training_process = None
        self.training_log = None
        root.title('Megazeka · Türkçe Yazım Atölyesi')
        root.geometry('1180x820'); root.minsize(820, 640)
        theme(root)
        container = ttk.Frame(root, padding=24); container.pack(fill='both', expand=True)
        header = ttk.Frame(container); header.pack(fill='x', pady=(0, 18))
        left = ttk.Frame(header); left.pack(side='left')
        ttk.Label(left, text='megazeka', style='Title.TLabel').pack(anchor='w')
        ttk.Label(left, text='TÜRKÇE YAZIM ATÖLYESİ', style='Muted.TLabel').pack(anchor='w')
        self.learning = tk.BooleanVar(value=False)
        self.filter_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(header, text='Öğrenme modu', variable=self.learning, command=self.toggle_learning).pack(side='right', padx=10)
        ttk.Label(header, text='●  YEREL MODEL', foreground=ACCENT).pack(side='right', padx=18)
        self.notebook = ttk.Notebook(container); self.notebook.pack(fill='both', expand=True)
        main = ttk.Frame(self.notebook, padding=16); self.notebook.add(main, text='Metin düzelt')
        ttk.Label(main, text='Düşünceniz aynı kalsın. Yazımınız netleşsin.', style='Heading.TLabel').pack(anchor='w', pady=(0, 6))
        ttk.Label(main, text='Metninizi yazın veya yapıştırın. Eğitilmiş model bu bilgisayarda çalışır.', style='Muted.TLabel').pack(anchor='w', pady=(0, 16))
        panels = ttk.Panedwindow(main, orient='horizontal'); panels.pack(fill='both', expand=True)
        original = ttk.Frame(panels); corrected = ttk.Frame(panels)
        panels.add(original, weight=1); panels.add(corrected, weight=1)
        ttk.Label(original, text='SİZİN METNİNİZ', style='Muted.TLabel').pack(anchor='w', pady=8)
        ttk.Label(original, text='Metninizi buraya yazın...', style='Muted.TLabel').pack(anchor='w', pady=(0, 7))
        frame, self.input = text_area(original, height=6); frame.pack(fill='both', expand=True, padx=(0, 8))
        self.input.bind('<<Modified>>', self.update_counter)
        ttk.Label(corrected, text='DÜZELTİLMİŞ METİN', style='Muted.TLabel').pack(anchor='w', pady=8)
        ttk.Label(corrected, text='Sonuç burada görünecek.', style='Muted.TLabel').pack(anchor='w', pady=(0, 7))
        frame, self.output = text_area(corrected, height=6, readonly=True); frame.pack(fill='both', expand=True, padx=(8, 0))
        counters = ttk.Frame(main); counters.pack(fill='x', pady=8)
        self.counter = ttk.Label(counters, text='0 / 4.000 karakter', style='Muted.TLabel'); self.counter.pack(side='left')
        self.result_count = ttk.Label(counters, text='', style='Muted.TLabel'); self.result_count.pack(side='right')
        actions = ttk.Frame(main); actions.pack(fill='x', pady=(7, 12))
        self.correct_button = ttk.Button(actions, text='Düzelt  →', style='Accent.TButton', command=self.correct)
        self.correct_button.pack(side='left')
        self.clear_button = ttk.Button(actions, text='Temizle', command=self.clear); self.clear_button.pack(side='left', padx=8)
        self.copy_button = ttk.Button(actions, text='Kopyala', command=self.copy, state='disabled'); self.copy_button.pack(side='right')
        self.status = ttk.Label(main, text='Hazır · Ctrl+Enter ile düzeltin.', style='Muted.TLabel', wraplength=1000)
        self.status.pack(anchor='w', pady=5)
        self.spinner = ttk.Progressbar(main, mode='indeterminate'); self.spinner.pack(fill='x', pady=5)
        self.disclaimer = ttk.Label(main, text='Deneysel model: özellikle özel adları ve anlamı etkileyen değişiklikleri gözden geçirin.', style='Muted.TLabel')
        self.disclaimer.pack(anchor='w', pady=(7, 0))
        self.spinner.pack_forget()
        self.inspection = Inspection(self.notebook)
        self.dashboard = Dashboard(self.notebook, self.start_training, self.stop_training)
        self.dataset = DatasetPanel(self.notebook)
        self.storage = StoragePanel(self.notebook)
        self.model_tab = ttk.Frame(self.notebook, padding=16)
        ttk.Label(self.model_tab, text='Model karşılaştırması ve teknik bilgiler', style='Heading.TLabel').pack(anchor='w', pady=8)
        ttk.Checkbutton(self.model_tab, text='Temkinli filtre: büyük değişiklikleri engelle (varsayılan)', variable=self.filter_enabled).pack(anchor='w', pady=6)
        ttk.Label(self.model_tab, text='Filtre bazı doğru düzeltmeleri de reddedebilir. Kapatırsanız sonraki Düzelt işlemi ham model çıktısını kullanır.', style='Muted.TLabel', wraplength=950).pack(anchor='w')
        ttk.Label(self.model_tab, text='Girdi kutusundaki aynı metni temel model, en iyi ve son kayıtla çalıştırır.\nTemel model, düzeltme görevi için henüz eğitilmemiştir. Bu karşılaştırma zaman alabilir.', style='Muted.TLabel').pack(anchor='w', pady=8)
        self.compare_button = ttk.Button(self.model_tab, text='Aynı metni karşılaştır', command=self.compare)
        self.compare_button.pack(anchor='w', pady=8)
        frame, self.model_box = text_area(self.model_tab, readonly=True); frame.pack(fill='both', expand=True)
        set_text(self.model_box, 'Model ilk düzeltmede yüklenir.\n\nDikkat haritaları bu sürümde gösterilmez: bellek maliyeti ekler ve modelin nedenini kanıtlamaz.\nBayt olasılıkları kalibre edilmiş düzeltme güveni değildir.\nBüyük değişiklik filtresi, uzak veya yarım üretilmiş metni reddeder. Ham sonuç her zaman incelemede bulunur.')
        self.educational = [(self.inspection, 'Nasıl düzeltti?'), (self.dashboard, 'Eğitim'), (self.dataset, 'Veri kümesi'),
                            (self.model_tab, 'Model bilgisi'), (self.storage, 'Depolama')]
        root.bind('<Control-Return>', lambda e: self.correct())
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(100, self.poll)
        root.after(1000, self.refresh_dashboard)

    def toggle_learning(self):
        if self.learning.get():
            for pane, name in self.educational:
                self.notebook.add(pane, text=name)
            self.storage.refresh(); self.dashboard.refresh()
        else:
            self.filter_enabled.set(True)
            for pane, name in self.educational:
                if str(pane) in self.notebook.tabs(): self.notebook.hide(pane)
            self.notebook.select(0)

    def update_counter(self, event=None):
        n = len(self.input.get('1.0', 'end-1c'))
        self.counter.configure(text=f'{n:,} / 4.000 karakter', foreground='#ff9aab' if n > 4000 else MUTED)
        self.input.edit_modified(False)

    def set_busy(self, busy, message=''):
        self.busy = busy
        for button in [self.correct_button, self.clear_button, self.compare_button]:
            button.configure(state='disabled' if busy else 'normal')
        self.input.configure(state='disabled' if busy else 'normal')
        if busy:
            self.spinner.pack(fill='x', pady=5, before=self.disclaimer)
            self.spinner.start(12)
        else:
            self.spinner.stop()
            self.spinner.configure(value=0)
            self.spinner.pack_forget()
        if message: self.status.configure(text=message)

    def create_engine(self, checkpoint='best'):
        if self.engine_factory:
            return self.engine_factory(checkpoint)
        from megazeka.inference import CorrectionEngine
        return CorrectionEngine(checkpoint)

    def correct(self):
        if self.busy: return
        text = self.input.get('1.0', 'end-1c')
        if not text.strip():
            self.status.configure(text='Düzeltmek için bir metin yazın.'); self.input.focus_set(); return
        if len(text) > 4000:
            self.status.configure(text='Lütfen metni 4.000 karakterin altına bölün.'); return
        inspect = self.learning.get()
        conservative = self.filter_enabled.get()
        self.set_busy(True, 'Model yükleniyor / metin düzeltiliyor…')
        def work():
            try:
                weights = ROOT / 'models/checkpoints/best/adapter_model.safetensors'
                revision = weights.stat().st_mtime_ns if weights.exists() else None
                if self.engine is not None and revision != self.engine_revision and not self.engine_factory:
                    self.engine = None
                    gc.collect()
                if self.engine is None: self.engine = self.create_engine()
                self.engine_revision = revision
                self.events.put(('result', self.engine.correct(text, inspect=inspect, conservative=conservative)))
            except Exception as error:
                self.events.put(('error', f'Metin düzeltilemedi: {error}'))
        threading.Thread(target=work, daemon=True).start()

    def copy(self):
        text = self.output.get('1.0', 'end-1c')
        if not text: return
        try:
            self.root.clipboard_clear(); self.root.clipboard_append(text); self.root.update_idletasks()
            self.copy_button.configure(text='Kopyalandı!')
            self.root.after(1800, lambda: self.copy_button.configure(text='Kopyala'))
        except tk.TclError:
            self.status.configure(text='Panoya erişilemedi. Sonuç metnini seçip Ctrl+C kullanabilirsiniz.')

    def clear(self):
        if self.busy: return
        set_text(self.input, ''); set_text(self.output, '')
        self.copy_button.configure(state='disabled', text='Kopyala')
        self.status.configure(text='Hazır · Yeni metninizi yazabilirsiniz.')
        self.result_count.configure(text=''); self.input.focus_set(); self.update_counter()

    def compare(self):
        if self.busy: return
        text = self.input.get('1.0', 'end-1c')
        if not text.strip() or len(text) > 4000:
            set_text(self.model_box, 'Önce düzeltme ekranındaki kutuya 1–4.000 karakterlik bir metin girin.'); return
        self.set_busy(True, 'Temel model ve mevcut kontrol noktaları karşılaştırılıyor…')
        def work():
            try:
                self.engine = None; gc.collect()
                import torch
                if torch.cuda.is_available(): torch.cuda.empty_cache()
                values = []
                for name, label in [('base', 'Temel model'), ('best', 'En iyi kayıt'), ('latest', 'Son kayıt')]:
                    if name != 'base' and not (ROOT / f'models/checkpoints/{name}/adapter_config.json').exists(): continue
                    engine = self.create_engine(name)
                    r = engine.correct(text, inspect=False, conservative=False)
                    values.append(f'{label}\n{r["raw_output"]}')
                    del engine; gc.collect()
                    if torch.cuda.is_available(): torch.cuda.empty_cache()
                self.events.put(('comparison', '\n\n'.join(values)))
            except Exception as error:
                self.events.put(('error', str(error)))
        threading.Thread(target=work, daemon=True).start()

    def start_training(self):
        if self.busy or self.training_process and self.training_process.poll() is None: return
        status_file = ROOT / 'reports/training_status.json'
        if status_file.exists():
            s = json.loads(status_file.read_text(encoding='utf-8'))
            import psutil
            if s.get('running') and s.get('pid') and psutil.pid_exists(s['pid']):
                self.status.configure(text='Bir eğitim zaten çalışıyor. Eğitim sekmesinden izleyebilirsiniz.'); return
        self.engine = None; gc.collect()
        state_path = ROOT / 'models/checkpoints/latest/state.json'
        args = [sys.executable, str(ROOT / 'training/train.py'), '--config', 'configs/quick.json']
        if state_path.exists():
            step = json.loads(state_path.read_text(encoding='utf-8'))['step']
            args.extend(['--resume', '--steps', str(step+60)])
        self.training_log = (ROOT / 'reports/training-console.log').open('a', encoding='utf-8')
        self.training_process = subprocess.Popen(args, cwd=ROOT, stdout=self.training_log, stderr=subprocess.STDOUT,
                                                  creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        self.status.configure(text='60 adımlık yerel eğitim başlatıldı. Eğitim sekmesinden izleyebilirsiniz.')

    def stop_training(self):
        (ROOT / 'reports/stop-training').touch()
        self.status.configure(text='Durdurma istendi. Geçerli adım bitince kontrol noktası kaydedilecek.')

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == 'result':
                    set_text(self.output, value['output'])
                    self.copy_button.configure(state='normal')
                    self.result_count.configure(text=f"{len(value['edits'])} karakter işlemi · {value['elapsed_ms']/1000:.2f} sn")
                    self.inspection.show(value)
                    if self.engine:
                        explanation = ('EĞİTİMDE NE OLDU?\nGürültülü metin girdi, doğru metin hedef olarak verildi. Kayıp, modelin hedef baytlara verdiği olasılıklardan hesaplandı. Geri yayılım ve AdamW, LoRA matrislerini güncelledi; temel model ağırlıkları sabit kaldı.\n\nBu işlemde çıkarım yapılıyor; yazdığınız metin modelin ağırlıklarını değiştirmiyor.\n\nTEKNİK BİLGİLER\n')
                        set_text(self.model_box, explanation + json.dumps(self.engine.info, ensure_ascii=False, indent=2))
                    self.set_busy(False, 'Düzeltme tamamlandı.' + (' ' + ' '.join(value['warnings']) if value['warnings'] else ''))
                elif kind == 'comparison':
                    set_text(self.model_box, value); self.set_busy(False, 'Karşılaştırma tamamlandı.')
                else:
                    self.set_busy(False, value)
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def refresh_dashboard(self):
        if self.learning.get(): self.dashboard.refresh()
        if self.training_process and self.training_process.poll() is not None and self.training_log:
            self.training_log.close(); self.training_log = None
            self.status.configure(text='Eğitim tamamlandı.' if self.training_process.returncode == 0 else 'Eğitim durdu. reports/training-console.log dosyasını inceleyin.')
        self.root.after(5000, self.refresh_dashboard)

    def close(self):
        if self.training_process and self.training_process.poll() is None:
            self.stop_training()
        self.root.destroy()

def main():
    root = tk.Tk(); MegazekaApp(root); root.mainloop()

if __name__ == '__main__': main()
