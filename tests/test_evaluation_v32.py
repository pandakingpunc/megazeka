import copy
import gzip
import json
from pathlib import Path
import pytest
from evaluation.audit import audited_rows, load_audit, recompute_audited_metrics
from evaluation.compare import mcnemar_exact, paired_bootstrap, compare_reports, character_distance, verdict
from evaluation.challenge import CHALLENGE, output_stem
from evaluation import evaluate, challenge
from megazeka.metrics import measure
from megazeka.storage import ROOT


@pytest.mark.parametrize('a,b,p', [(0, 0, 1), (1, 0, 1), (0, 4, .125), (1, 5, .21875),
                                   (2, 8, .109375), (3, 3, 1)])
def test_mcnemar_hand_computed(a, b, p):
    assert mcnemar_exact(a, b) == p
    assert mcnemar_exact(b, a) == p


def test_bootstrap_deterministic_and_clustered():
    result = paired_bootstrap([1, 1, 1, 1, -1, -1, -1, -1], ['a']*4 + ['b']*4)
    assert result == paired_bootstrap([1, 1, 1, 1, -1, -1, -1, -1], ['a']*4 + ['b']*4)
    assert result == {'difference': 0., 'ci95': [-1., 1.]}
    assert paired_bootstrap([1, -1], ['one', 'one']) == {'difference': 0., 'ci95': [0., 0.]}
    assert paired_bootstrap([1, 1], ['a', 'b']) == {'difference': 1., 'ci95': [1., 1.]}
    # Unequal clusters still estimate a row mean, not an unweighted group mean.
    assert paired_bootstrap([1, 1, -1], ['a', 'a', 'b'])['difference'] == pytest.approx(1/3)


def test_compare_evaluation_and_challenge():
    a = {'examples': [{'input': 'ab', 'target': 'abc', 'output': 'ab', 'source': 'Common Voice', 'difficulty': 'zor'},
                      {'input': 'xy', 'target': 'xy', 'output': 'xy', 'source': 'Megazeka', 'difficulty': 'temiz'}]}
    b = copy.deepcopy(a)
    b['examples'][0]['output'] = 'abc'
    result = compare_reports(a, b)
    assert result['overall']['a_only_correct'] == 0
    assert result['overall']['b_only_correct'] == 1
    assert result['overall']['exact_match']['difference'] == .5
    assert result['overall']['mean_cer']['difference'] == pytest.approx(-1/6)
    assert result['subsets']['common_voice']['exact_match']['difference'] == 1
    assert set(result['difficulty']) == {'zor', 'temiz'}
    assert verdict(result['overall']) == 'fark gürültü sınırında'
    left = {'rows': [{'source': 'girdi', 'target': 'hedef', 'output': 'hedef', 'category': 'test'}]}
    assert compare_reports(left, left)['categories']['test']['mcnemar_p'] == 1
    b['examples'].reverse()
    with pytest.raises(AssertionError, match='satır 0'):
        compare_reports(a, b)


def test_character_distance():
    assert character_distance('sıcak', 'sıyacak') == 2
    assert character_distance('', 'abc') == character_distance('abc', '') == 3


def test_audit_preserves_inputs_and_raw_metrics():
    audit = {'yanlış': {'action': 'fix', 'fix': 'doğru'}, 'bozuk': {'action': 'drop'}}
    rows = [{'input': 'eski gürültü', 'target': target, 'output': 'doğru'} for target in ['yanlış', 'bozuk', 'temiz'] for _ in range(4)]
    report = {'examples': rows, 'metrics': measure(rows)}
    before = copy.deepcopy(report)
    result = recompute_audited_metrics(report, audit)
    assert report == before
    assert result['examples'] == 8 and result['exact_match'] == .5
    assert audited_rows(rows, audit)[0]['input'] == 'eski gürültü'


def test_audit_targets_are_in_frozen_test():
    with gzip.open(ROOT / 'data/processed/test.jsonl.gz', 'rt', encoding='utf-8') as stream:
        rows = [json.loads(line) for line in stream]
    targets = {row['target'] for row in rows}
    audit = load_audit()
    assert len(targets) == 282 and len(rows) == 1128
    assert set(audit) <= targets
    dropped = {t for t, e in audit.items() if e['action'] == 'drop'}
    assert len(audited_rows(rows)) == len(rows) - 4 * len(dropped)
    assert all(e['reason'] and (e['action'] == 'drop' or e['fix'] != t) for t, e in audit.items())


def test_challenge_output_names_keep_dots():
    assert output_stem(CHALLENGE, 'best').name == 'challenge-best'
    assert output_stem(Path('evaluation/challenge2.jsonl'), 'v3.1b').name == 'challenge2-v3.1b'


@pytest.mark.parametrize('tag,enabled', [(None, False), ('v3.2-lexicon', True)])
def test_evaluate_cli_report_without_model(tmp_path, monkeypatch, tag, enabled):
    class Engine:
        info = {}
        def __init__(self, checkpoint):
            assert checkpoint == 'v3.1b'
        def correct_batch(self, texts, lexicon_guard):
            assert lexicon_guard == enabled
            return [{'output': t, 'raw_output': t, 'warnings': []} for t in texts]
        def correct(self, text, inspect, lexicon_guard):
            assert lexicon_guard == enabled
            return {'output': text, 'raw_output': text}
    monkeypatch.setattr(evaluate, 'ROOT', tmp_path)
    monkeypatch.setattr(evaluate, 'CorrectionEngine', Engine)
    monkeypatch.setattr(evaluate, 'MANUAL', [('Temiz.', 'Temiz.')])
    monkeypatch.setattr(evaluate, 'read_pairs', lambda split: [
        {'input': 'Temiz.', 'target': 'Temiz.', 'difficulty': 'temiz', 'source': 'Common Voice'}])
    monkeypatch.setattr(evaluate, 'ensure_budget', lambda *args: None)
    monkeypatch.setattr(evaluate, 'usage', lambda: {})
    argv = ['evaluate', '--checkpoint', 'v3.1b'] + (['--tag', tag, '--lexicon-guard'] if tag else [])
    monkeypatch.setattr('sys.argv', argv)
    evaluate.main()
    path = tmp_path / f'reports/evaluation-{tag or "v3.1b"}.json'
    report = json.loads(path.read_text(encoding='utf-8'))
    assert report['lexicon_guard'] == enabled and report['tag'] == (tag or 'v3.1b')
    assert report['metrics'] == report['audited_metrics']
    assert path.with_suffix('.md').exists()


def test_challenge_cli_custom_file_and_tag(tmp_path, monkeypatch):
    from megazeka import inference
    class Engine:
        info = {}
        def __init__(self, checkpoint):
            assert checkpoint == 'v3.1b'
        def correct(self, text, inspect, conservative, lexicon_guard):
            assert lexicon_guard and conservative
            return {'output': text, 'raw_output': text}
    path = tmp_path / 'challenge2.jsonl'
    path.write_text(json.dumps({'source': 'Temiz.', 'target': 'Temiz.', 'category': 'koruma'}), encoding='utf-8')
    monkeypatch.setattr(challenge, 'ROOT', tmp_path)
    monkeypatch.setattr(inference, 'CorrectionEngine', Engine)
    monkeypatch.setattr('sys.argv', ['challenge', '--checkpoint', 'v3.1b', '--file', str(path),
                                   '--tag', 'v3.2.lex', '--lexicon-guard'])
    challenge.main()
    report_path = tmp_path / 'reports/challenge2-v3.2.lex.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    assert report['lexicon_guard'] and report['exact_match'] == 1
    assert (tmp_path / 'reports/challenge2-v3.2.lex.md').exists()
