import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

BG = '#0b1220'
CARD = '#131f31'
TEXT = '#edf3fa'
MUTED = '#97aac1'
ACCENT = '#57dec0'

def theme(root):
    root.configure(bg=BG)
    tkfont.nametofont('TkDefaultFont', root=root).configure(family='Segoe UI', size=10)
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background=BG, foreground=TEXT, borderwidth=0)
    style.configure('TFrame', background=BG)
    style.configure('Card.TFrame', background=CARD)
    style.configure('TLabel', background=BG, foreground=TEXT)
    style.configure('Muted.TLabel', foreground=MUTED)
    style.configure('Title.TLabel', font=('Segoe UI', 26, 'bold'))
    style.configure('Heading.TLabel', font=('Segoe UI', 12, 'bold'))
    style.configure('TButton', background='#24354c', foreground=TEXT, padding=(15, 10))
    style.map('TButton', background=[('active', '#344b69'), ('disabled', '#192439')])
    style.configure('Accent.TButton', background=ACCENT, foreground=BG, font=('Segoe UI', 11, 'bold'))
    style.map('Accent.TButton', background=[('active', '#8befd7'), ('disabled', '#315e59')])
    style.configure('TCheckbutton', background=BG, foreground=TEXT)
    style.map('TCheckbutton', background=[('active', CARD)])
    style.configure('TNotebook', background=BG)
    style.configure('TNotebook.Tab', background=CARD, foreground=MUTED, padding=(15, 10))
    style.map('TNotebook.Tab', background=[('selected', '#253c50')], foreground=[('selected', ACCENT)])
    style.configure('Treeview', background=CARD, fieldbackground=CARD, foreground=TEXT, rowheight=29)
    style.configure('Treeview.Heading', background='#26364c', foreground=TEXT, padding=7)
    style.map('Treeview', background=[('selected', '#2b5360')])
    style.configure('TCombobox', fieldbackground=CARD, background=CARD, foreground=TEXT)
    style.configure('TProgressbar', background=ACCENT, troughcolor=CARD)

def text_area(parent, height=8, readonly=False):
    frame = ttk.Frame(parent)
    box = tk.Text(frame, bg=CARD, fg=TEXT, insertbackground=ACCENT, selectbackground='#31635e',
                  relief='flat', wrap='word', font=('Segoe UI', 12), padx=18, pady=16,
                  height=height, undo=not readonly, borderwidth=0)
    scroll = ttk.Scrollbar(frame, orient='vertical', command=box.yview)
    box.configure(yscrollcommand=scroll.set)
    box.pack(side='left', fill='both', expand=True); scroll.pack(side='right', fill='y')
    if readonly:
        box.configure(state='disabled')
    return frame, box

def set_text(box, text):
    old = box.cget('state')
    box.configure(state='normal')
    box.delete('1.0', 'end'); box.insert('1.0', text)
    box.configure(state=old)

def table(parent, columns, widths=None, height=7):
    frame = ttk.Frame(parent)
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=height)
    for i, column in enumerate(columns):
        tree.heading(column, text=column)
        tree.column(column, width=(widths or [140]*len(columns))[i], minwidth=60)
    scroll = ttk.Scrollbar(frame, command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side='left', fill='both', expand=True); scroll.pack(side='right', fill='y')
    return frame, tree

def plot(canvas, history, key, title, color=ACCENT):
    canvas.delete('all')
    w = max(250, canvas.winfo_width()); h = max(140, canvas.winfo_height())
    canvas.create_text(15, 17, text=title, anchor='w', fill=TEXT, font=('Segoe UI', 10, 'bold'))
    horizontal = 'epoch' if key in ('cer', 'wer', 'overcorrection') else 'step'
    unit = 'tur' if horizontal == 'epoch' else 'adım'
    values = [(r.get(horizontal, 0), r.get(key) if key in r else r.get('metrics', {}).get(key)) for r in history]
    values = [(x, y) for x, y in values if isinstance(y, (int, float))]
    if not values:
        canvas.create_text(w/2, h/2, text='Henüz ölçüm yok', fill=MUTED)
        return
    xmin, xmax = 0, max(.01, max(x for x, y in values))
    ymin, ymax = 0, max(.01, max(y for x, y in values)) * 1.1
    canvas.create_line(42, 40, 42, h-30, w-15, h-30, fill='#384961')
    canvas.create_text(6, 45, text=f'{ymax:.2f}', fill=MUTED, anchor='w')
    points = []
    for x, y in values:
        px = 42 + x / xmax * (w-60); py = h-30 - y/ymax * (h-75)
        points.extend([px, py]); canvas.create_oval(px-3, py-3, px+3, py+3, fill=color, outline='')
    if len(points) >= 4:
        canvas.create_line(*points, fill=color, width=2)
    label = f'{xmax:.2f}' if horizontal == 'epoch' else str(int(xmax))
    canvas.create_text(w-20, h-12, text=f'{label} {unit}', fill=MUTED, anchor='e')
