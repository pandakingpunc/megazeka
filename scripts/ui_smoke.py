"""Real model -> real Tk input/button/result -> OS clipboard integration test."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import time
import tkinter as tk
from app.main import MegazekaApp
from megazeka.storage import ROOT

root = tk.Tk()
app = MegazekaApp(root)
root.update()
app.input.insert('1.0', 'bugun hava cok guzel\n\nYarın görüşürüz.')
app.learning.set(True); app.toggle_learning()
app.correct_button.invoke()
deadline = time.time() + 120
while app.busy and time.time() < deadline:
    root.update(); time.sleep(.03)
assert not app.busy, 'Gerçek model zaman aşımı'
output = app.output.get('1.0', 'end-1c')
assert output.strip(), app.status.cget('text')
assert '\n\n' in output
app.copy_button.invoke(); root.update()
assert root.clipboard_get() == output
assert app.copy_button.cget('text') == 'Kopyalandı!'
assert app.inspection.result['generated']
report = {'input': app.input.get('1.0', 'end-1c'), 'output': output, 'clipboard_matches': True,
          'learning_mode': True, 'tokens_observed': len(app.inspection.result['generated']),
          'window_size': [root.winfo_width(), root.winfo_height()]}
app.storage.refresh()
root.geometry('840x660'); root.update()
assert app.correct_button.winfo_ismapped()
report['small_window_size'] = [root.winfo_width(), root.winfo_height()]
app.compare_button.invoke()
deadline = time.time() + 120
while app.busy and time.time() < deadline:
    root.update(); time.sleep(.03)
comparison = app.model_box.get('1.0', 'end-1c')
assert not app.busy and all(label in comparison for label in ['Temel model', 'En iyi kayıt', 'Son kayıt']), app.status.cget('text')
report['checkpoint_comparison'] = comparison
(ROOT / 'reports/ui-smoke.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
root.destroy()
