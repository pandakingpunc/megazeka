import json
from pathlib import Path
import subprocess
import sys

import pytest

from training import prepare_v35 as prepare


def legacy(target, source=None, **extra):
    return {'target': target, 'input': target if source is None else source,
            'source': 'legacy', 'difficulty': 'temiz', 'operations': [],
            'group_id': prepare.group_of(target), **extra}


def explicit(target, source=None, kind='yazım'):
    return {'input': target if source is None else source, 'target': target,
            'kind': kind, 'focus': 'odak', 'family': 'aile', 'source': 'v35'}


def write_gzip(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(prepare.gzip_rows(rows))


@pytest.fixture
def dataset(tmp_path, monkeypatch):
    untouched = legacy('Özgün eğitim.', 'özgün egitim', custom={'nested': [1, 'ışık']})
    train = [legacy('Eski hedef.'), legacy('Eski hedef.', 'eski hedf'),
             legacy('Silinecek hedef.'), legacy('Silinecek hedef.', 'silinecek hedf'),
             untouched, legacy('Ortak eski.')]
    validation = [legacy('Doğrulama hedefi.', 'doğrulama girdisi'), legacy('Ortak eski.')]
    for split, rows in [('train', train), ('validation', validation)]:
        write_gzip(tmp_path / f'data/v3.2-backup/{split}.jsonl.gz', rows)
        write_gzip(tmp_path / f'data/processed/{split}.jsonl.gz', [legacy('Önceki çıktı.')])
    write_gzip(tmp_path / 'data/processed/test.jsonl.gz',
               [legacy('Dondurulmuş hedef.', 'Dondurulmuş girdi.')])
    audit = tmp_path / 'data/audit/v3.5-approved.jsonl'
    audit.parent.mkdir(parents=True)
    audit.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in [
        {'target': 'Eski hedef.', 'action': 'fix', 'fix': 'Düzeltilmiş hedef.'},
        {'target': 'Silinecek hedef.', 'action': 'drop'}]), encoding='utf-8')
    evaluation = tmp_path / 'evaluation'
    evaluation.mkdir()
    (evaluation / 'challenge.jsonl').write_text(json.dumps({
        'source': 'Zorluk girdisi.', 'target': 'Zorluk hedefi.'}), encoding='utf-8')
    (evaluation / 'challenge-extra.jsonl').write_text(json.dumps({
        'source': 'Ek zorluk girdisi.', 'target': 'Ek zorluk hedefi.'}), encoding='utf-8')
    (tmp_path / 'data/metadata.json').write_text(json.dumps({
        'version': 'v3.2', 'custom': {'keep': True},
        'splits': {'train': {'pairs': 1, 'custom': 42},
                   'validation': {'pairs': 1}, 'test': {'pairs': 1, 'frozen': True}}}),
        encoding='utf-8')
    monkeypatch.setattr(prepare, 'ROOT', tmp_path)
    monkeypatch.setattr(prepare, 'build_splits', lambda: {
        'train': [explicit('Yeni hedef.', 'yeni hedf'), explicit('Temiz yeni.', kind='koruma')],
        'validation': [explicit('Yeni doğrulama.', 'yeni dogrulama')]})
    return tmp_path, train, validation


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob('*') if p.is_file()}


def test_audit_schema_preservation_and_metadata(dataset, capsys):
    root, original, validation = dataset
    before = snapshot(root)
    report = prepare.main()
    assert json.loads(capsys.readouterr().out) == report
    rows = prepare.read_rows(root / 'data/processed/train.jsonl.gz')
    fixed = dict(original[0], input='Düzeltilmiş hedef.', target='Düzeltilmiş hedef.',
                 group_id=prepare.group_of('Düzeltilmiş hedef.'))
    assert rows[:3] == [fixed, original[4], original[5]]
    assert list(rows[1].items()) == list(original[4].items())
    assert prepare.read_rows(root / 'data/processed/validation.jsonl.gz')[:2] == validation
    assert rows[3] == {
        'target': 'Yeni hedef.', 'kind': 'yazım', 'focus': 'odak', 'family': 'aile',
        'source': 'v35', 'input': 'yeni hedf', 'difficulty': 'orta',
        'operations': [{'operation': 'v35_explicit', 'before': 'Yeni hedef.', 'after': 'yeni hedf'}],
        'group_id': prepare.group_of('Yeni hedef.')}
    assert rows[4]['difficulty'] == 'temiz'
    assert rows[4]['operations'] == []
    assert report['base_rows'] == {'train': {'fixed': 1, 'dropped': 3},
                                   'validation': {'fixed': 0, 'dropped': 0}}
    assert report['added']['train'] == {'pairs': 2, 'by_kind': {'koruma': 1, 'yazım': 1}}
    metadata = json.loads((root / 'data/metadata.json').read_text(encoding='utf-8'))
    assert metadata['version'] == 'v3.5'
    assert metadata['v35'] == report
    assert metadata['custom'] == {'keep': True}
    assert metadata['splits']['train']['custom'] == 42
    assert metadata['splits']['train']['pairs'] == len(rows)
    assert metadata['splits']['test'] == {'pairs': 1, 'frozen': True}
    after = snapshot(root)
    writable = {'data/processed/train.jsonl.gz', 'data/processed/validation.jsonl.gz',
                'data/metadata.json'}
    assert set(before) == set(after)
    for path in before.keys() - writable:
        assert after[path] == before[path]
    for split in prepare.SPLITS:
        data = after[f'data/processed/{split}.jsonl.gz']
        assert data[4:8] == b'\0\0\0\0'
        assert not data[3] & 8  # No filename in the gzip header.
        assert report['output_sha256'][split] == prepare.sha256(data)
        assert report['base_sha256'][split] == prepare.sha256(
            before[f'data/v3.2-backup/{split}.jsonl.gz'])
    assert report['approved_sha256'] == prepare.sha256(before['data/audit/v3.5-approved.jsonl'])


@pytest.mark.parametrize('field', ['input', 'target'])
@pytest.mark.parametrize('blocked,reason', [
    ('DONDURULMUŞ GİRDİ!!!', 'test'), ('DONDURULMUŞ HEDEF!!!', 'test'),
    ('ZORLUK GİRDİSİ!!!', 'challenge'), ('ZORLUK HEDEFİ!!!', 'challenge'),
    ('EK ZORLUK GİRDİSİ!!!', 'challenge'), ('EK ZORLUK HEDEFİ!!!', 'challenge'),
    ('DOĞRULAMA GİRDİSİ!!!', 'opposite_base'),
    ('DOĞRULAMA HEDEFİ!!!', 'opposite_base'),
])
def test_canonical_leaks(dataset, monkeypatch, field, blocked, reason):
    root, _, _ = dataset
    row = explicit('Yeni bağımsız hedef.', 'yeni bağımsız girdi')
    row[field] = blocked
    monkeypatch.setattr(prepare, 'build_splits', lambda: {'train': [row], 'validation': []})
    report = prepare.main(root=root, dry_run=True)
    assert report['rejected']['train'][reason] == 1
    assert report['added']['train']['pairs'] == 0


def test_duplicates_and_new_cross_split_overlap(dataset, monkeypatch):
    _, original, _ = dataset
    duplicate = explicit(original[4]['target'], original[4]['input'])
    monkeypatch.setattr(prepare, 'build_splits', lambda: {
        'train': [duplicate, explicit('Yeni ortak.', 'Yeni girdi.')],
        'validation': [explicit('Farklı hedef.', 'YENİ ORTAK!'),
                       explicit('ÖZGÜN EĞİTİM!', 'başka girdi')]})
    report = prepare.main(dry_run=True)
    assert report['rejected']['train']['duplicate'] == 1
    assert report['rejected']['validation']['opposite_new'] == 1
    assert report['rejected']['validation']['opposite_base'] == 1


def test_idempotence_and_dry_run(dataset):
    root, _, _ = dataset
    before = snapshot(root)
    dry_report = prepare.main(dry_run=True)
    assert snapshot(root) == before
    assert prepare.main() == dry_report
    once = snapshot(root)
    assert prepare.main() == dry_report
    assert snapshot(root) == once
    assert prepare.main(dry_run=True) == dry_report
    assert snapshot(root) == once


def test_cli_dry_run_writes_nothing(dataset):
    root, _, _ = dataset
    before = snapshot(root)
    script = Path(prepare.__file__).resolve()
    # Exercise the actual CLI parser against the fixture, with no copy of the script.
    code = ("import runpy; from pathlib import Path; "
            f"ns = runpy.run_path({str(script)!r}, run_name='fixture_prepare'); "
            "ns['main'].__globals__['build_splits'] = lambda: {'train': [], 'validation': []}; "
            f"ns['cli'](['--dry-run'], root=Path({str(root)!r}))")
    result = subprocess.run([sys.executable, '-B', '-c', code], capture_output=True,
                            text=True, encoding='utf-8', check=True)
    assert json.loads(result.stdout)['added']['train']['pairs'] == 0
    assert snapshot(root) == before


def test_fix_cannot_introduce_cross_split_overlap(dataset):
    root, _, _ = dataset
    path = root / 'data/audit/v3.5-approved.jsonl'
    path.write_text(json.dumps({'target': 'Eski hedef.', 'action': 'fix',
                                'fix': 'DOĞRULAMA GİRDİSİ!'}), encoding='utf-8')
    before = snapshot(root)
    with pytest.raises(ValueError, match='overlap'):
        prepare.main()
    assert snapshot(root) == before


def test_replacement_character_rejected_before_writing(dataset, monkeypatch):
    root, _, _ = dataset
    monkeypatch.setattr(prepare, 'build_splits', lambda: {
        'train': [explicit('Bozuk \ufffd metin.')], 'validation': []})
    before = snapshot(root)
    with pytest.raises(ValueError, match='Replacement character'):
        prepare.main()
    assert snapshot(root) == before


def test_config_only_steps_changed():
    root = Path(prepare.__file__).resolve().parents[1]
    medium = json.loads((root / 'configs/medium.json').read_text(encoding='utf-8'))
    expected = dict(medium, steps=7000)
    assert json.loads((root / 'configs/v3.5.json').read_text(encoding='utf-8')) == expected
