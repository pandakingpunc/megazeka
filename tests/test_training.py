import json
from pathlib import Path
from training.train import write_json

def test_status_writer_retries_windows_sharing_violation(tmp_path, monkeypatch):
    original = Path.replace
    attempts = []
    def flaky(self, target):
        attempts.append(1)
        if len(attempts) < 3:
            raise PermissionError('simulated Windows reader')
        return original(self, target)
    monkeypatch.setattr(Path, 'replace', flaky)
    path = tmp_path / 'training_status.json'
    write_json(path, {'step': 1000})
    assert json.loads(path.read_text())['step'] == 1000
    assert len(attempts) == 3
