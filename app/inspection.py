import difflib
import json
import tkinter as tk
from tkinter import ttk
from .widgets import text_area, set_text, table, ACCENT, MUTED

class Inspection(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=12)
        ttk.Label(self, text='Gözlenen: tokenlar, olasılıklar, süreler.  Türetilen: metin farkı açıklamaları.\nBilinmeyen: modelin belirli bir düzeltmeyi seçmesinin kesin içsel nedeni.',
                  style='Muted.TLabel', wraplength=1000).pack(anchor='w', pady=(0, 10))
        self.tabs = ttk.Notebook(self); self.tabs.pack(fill='both', expand=True)
        self.boxes = {}
        for name in ['Akış ve metinler', 'Görsel fark', 'Tokenlar', 'Düzenlemeler']:
            pane = ttk.Frame(self.tabs, padding=8); self.tabs.add(pane, text=name)
            if name in ['Akış ve metinler', 'Görsel fark']:
                frame, box = text_area(pane, readonly=True, height=12)
                frame.pack(fill='both', expand=True); self.boxes[name] = box
            elif name == 'Düzenlemeler':
                ttk.Label(pane, text='Konumlar sıfırdan başlar; her satır bir Levenshtein karakter işlemidir.\nTür, gözlenen farktan türetilir. Düzeltme başına kalibre edilmiş güven yoktur.', style='Muted.TLabel').pack(anchor='w', pady=8)
                frame, self.edits = table(pane, ['Konum', 'İşlem', 'Önce', 'Sonra', 'Tür', 'Mesafe'], [70, 90, 80, 80, 220, 70])
                frame.pack(fill='both', expand=True)
            else:
                ttk.Label(pane, text='ByT5 UTF-8 baytları kullanır: “ü” iki bayttır (C3 BC). Bayt olasılığı doğruluk güvencesi değildir.\nBir çıktı tokenını seçerek o üretim adımındaki gerçek ilk 5 alternatifi inceleyin.', style='Muted.TLabel').pack(anchor='w', pady=6)
                self.scores = ttk.Label(pane, text='Henüz üretim yok.'); self.scores.pack(anchor='w')
                frame, self.tokens = table(pane, ['Parça', 'Adım', 'Token', 'Kimlik', 'Olasılık'], [60, 60, 120, 80, 100], height=5)
                frame.pack(fill='both', expand=True, pady=7)
                self.alternatives = ttk.Label(pane, text='', wraplength=950); self.alternatives.pack(anchor='w', pady=8)
                self.tokens.bind('<<TreeviewSelect>>', self.choose_token)
        self.result = None

    def choose_token(self, event=None):
        selected = self.tokens.selection()
        if selected and self.result:
            token = self.result['generated'][int(selected[0])]
            self.alternatives.configure(text='Alternatifler: ' + '  •  '.join(f"{v['token']} ({v['probability']:.4f})" for v in token['alternatives']))

    def show(self, result):
        self.result = result
        stages = '\n'.join(f'{name}: {value:.1f} ms' for name, value in result['timings_ms'].items())
        values = [('1 · ÖZGÜN METİN', result['original']), ('2 · MODEL GİRDİSİ', result['model_input']),
                  ('3 · GİRDİ TOKENLARI / KİMLİKLER', ' '.join(f"{t['token']}:{t['id']}" for t in result['tokens'])),
                  ('4 · HAM MODEL ÇIKTISI', result['raw_output']), ('5 · SON ÇIKTI', result['output']),
                  ('6 · ÖLÇÜLEN SÜRELER', stages), ('KORUMA FİLTRESİ', '\n'.join(result['warnings']) or 'Devreye girmedi.')]
        summary = '\n\n'.join(f'{label}\n{text}' for label, text in values)
        summary += '\n\nÖn işleme değişikliği: ' + ('NFC Unicode / satır sonları normalleştirildi.' if result['preprocessing_changed'] else 'Yok.')
        summary += '\nParçalar modele ayrı geçirilir; satır ve paragraf ayırıcıları aynen korunur.'
        set_text(self.boxes['Akış ve metinler'], summary)
        box = self.boxes['Görsel fark']; box.configure(state='normal'); box.delete('1.0', 'end')
        box.tag_configure('delete', foreground='#ff9aab', background='#522b3b', overstrike=True)
        box.tag_configure('insert', foreground='#78ebc9', background='#17493f')
        box.insert('end', 'Pembe / üstü çizili: silinen   ·   Yeşil: eklenen   ·   ␠: değişen boşluk\n\n')
        old, new = result['original'], result['output']
        for tag, i, j, k, l in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
            if tag == 'equal':
                box.insert('end', old[i:j])
            else:
                if i != j:
                    box.insert('end', old[i:j].replace(' ', '␠'), 'delete')
                if k != l:
                    box.insert('end', new[k:l].replace(' ', '␠'), 'insert')
        box.configure(state='disabled')
        self.edits.delete(*self.edits.get_children()); self.tokens.delete(*self.tokens.get_children())
        translations = {'replace': 'Değiştir', 'insert': 'Ekle', 'delete': 'Sil'}
        for op in result['edits']:
            self.edits.insert('', 'end', values=(op['source_index'], translations[op['operation']], repr(op['old']), repr(op['new']), op['type'], 1))
        for i, token in enumerate(result['generated']):
            self.tokens.insert('', 'end', iid=str(i), values=(token['part'], token['step'], token['token'], token['id'], f"{token['probability']:.4f}"))
        if result['generated']:
            minimum = min(result['generated'], key=lambda token: token['probability'])
            self.scores.configure(text=f"Ortalama bayt olasılığı: {result['average_token_probability']:.4f}  ·  En düşük: {minimum['token']} ({minimum['probability']:.4f}, adım {minimum['step']})  ·  Dizi log olasılığı: {result['sequence_log_probability']:.2f}")
        else:
            self.scores.configure(text='Bu işlem için olasılıklar kaydedilmedi; öğrenme modunda tekrar düzeltin.')
