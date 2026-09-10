import tkinter as tk
import time
from app.main import MegazekaApp
from megazeka.metrics import edits

class FakeEngine:
    info = {'Mimari': 'Test doubles: model-free widget integration'}
    def correct(self, text, inspect=True, conservative=True):
        return {'original': text, 'model_input': text, 'raw_output': 'Bugün güzel.', 'output': 'Bugün güzel.',
                'edits': [], 'elapsed_ms': 10, 'warnings': [], 'tokens': [], 'generated': [],
                'timings_ms': {}, 'preprocessing_changed': False}

def test_widget_entry_copy_clear_and_learning():
    root = tk.Tk(); root.withdraw()
    app = MegazekaApp(root, engine_factory=lambda checkpoint: FakeEngine())
    app.input.insert('1.0', 'bugun guzel')
    app.correct_button.invoke()
    end = time.time() + 5
    while app.busy and time.time() < end:
        root.update(); time.sleep(.02)
    assert app.output.get('1.0', 'end-1c') == 'Bugün güzel.'
    app.copy_button.invoke(); root.update()
    assert root.clipboard_get() == 'Bugün güzel.'
    assert app.copy_button.cget('text') == 'Kopyalandı!'
    app.learning.set(True); app.toggle_learning(); root.update()
    assert len(app.notebook.tabs()) == 6
    app.filter_enabled.set(False)
    app.learning.set(False); app.toggle_learning()
    assert app.filter_enabled.get()
    app.clear_button.invoke()
    assert app.input.get('1.0', 'end-1c') == app.output.get('1.0', 'end-1c') == ''
    root.destroy()
