import random
import pytest
from megazeka.text import normalize, chunks, lower_tr, canonical
from megazeka.noise import NoiseGenerator
from megazeka.metrics import edits, measure
from megazeka.storage import ensure_budget, remove_owned
from training.prepare import read_pairs

def test_turkish_normalization():
    assert lower_tr('IŞIK İSTANBUL') == 'ışık istanbul'
    assert normalize('o\u0308rnek\r\n\r\n  ikinci') == 'örnek\n\n  ikinci'
    assert canonical('İyi, güzel!') == canonical('iyi güzel')

@pytest.mark.parametrize('text', ['\n\n', '  uzun yazı\n\n\tikinci satır  ', 'ü'*450, 'a '*500, '🙂'*300, 'a\t  b'])
def test_chunking_is_lossless(text):
    result = chunks(text)
    assert ''.join(t for t, layout in result) == text
    assert all(len(t.encode()) <= 176 for t, layout in result if not layout)

def test_noise_reproducible_and_observable():
    a, b = NoiseGenerator(9), NoiseGenerator(9)
    text = "Bugün Ankara'ya gideceğim, sen de gelir misin?"
    assert a.corrupt(text, 'temiz') == (text, [])
    for difficulty in ['kolay', 'orta', 'zor'] * 20:
        result = a.corrupt(text, difficulty)
        assert result == b.corrupt(text, difficulty)
        changed, operations = result
        previous = text
        for op in operations:
            assert op['before'] == previous and op['after'] != previous
            previous = op['after']
        assert previous == changed and changed.strip()

def test_every_noise_operation_can_change():
    gen = NoiseGenerator(42)
    text = "Bugün Ankara'ya gideceğim, sen de evdeki kitabı getirir misin?"
    for name in gen.names:
        assert any(gen.apply(text, name) != text for _ in range(100)), name

def test_exact_edits_reconstruct():
    for old, new in [('yarin', 'Yarın.'), ('kel ime', 'kelime'), ('a', 'aaa'), ('', 'ş'), ('ü', '')]:
        ops = edits(old, new)
        result = list(old)
        # Reverse original coordinates; tied inserts are reversed for correct order.
        for op in reversed(ops):
            i = op['source_index']
            if op['operation'] == 'insert': result.insert(i, op['new'])
            elif op['operation'] == 'delete': del result[i]
            else: result[i] = op['new']
        assert ''.join(result) == new

def test_metrics_identity_and_perfect():
    data = [{'input': 'bugun', 'target': 'bugün', 'output': 'bugün'}, {'input': 'İyi.', 'target': 'İyi.', 'output': 'İyi.'}]
    result = measure(data)
    assert result['cer'] == result['wer'] == result['overcorrection'] == 0
    assert result['exact_match'] == result['edit_f1'] == 1
    result = measure([{**r, 'output': r['input']} for r in data])
    assert result['edit_recall'] == 0 and result['cer'] > 0

def test_data_has_no_group_leakage():
    rows = [read_pairs(s) for s in ['train', 'validation', 'test']]
    groups = [{r['group_id'] for r in split} for split in rows]
    assert not groups[0] & groups[1] and not groups[0] & groups[2] and not groups[1] & groups[2]
    combined = [r for r in rows[0] if r.get('group_id_second')]
    second = {r['group_id_second'] for r in combined}
    assert not second & groups[1] and not second & groups[2]
    assert len(rows[0]) > 32000 and combined
    assert sum(r['difficulty'] == 'temiz' for r in rows[0]) >= 8000
    assert any(r['source'].startswith('Megazeka') for r in rows[2])

def test_storage_blocks_before_write(tmp_path):
    with pytest.raises(RuntimeError): ensure_budget(15_000_000_000, 'test', tmp_path)
    assert not list(tmp_path.iterdir())
    with pytest.raises(ValueError): remove_owned(tmp_path)


def test_colloquial_rules_generalize_to_any_verb():
    from megazeka.colloquial import candidates
    def forms(text):
        return {f for _, _, fs in candidates(text) for f in fs}
    assert {'gidicem', 'gitcem'} <= forms('Yarın okula gideceğim.')
    assert {'yapıcaz', 'yapcaz'} <= forms('Bunu yapacağız.')
    assert 'bekliyom' in forms('Seni bekliyorum.')
    assert 'geliyo' in forms('Ali geliyor.')
    assert 'Söylicem' in forms('Söyleyeceğim.') and 'okucam' in forms('Kitabı okuyacağım.')
    assert 'Yapmıcam' in forms('Yapmayacağım.')
    assert {'Burda', 'napıyosun'} & forms('Burada ne yapıyorsun?')
    assert not candidates('Görüşürüz.')

def test_word_guard_blocks_paraphrase_but_keeps_spelling_fixes():
    from megazeka.inference import guard_words
    assert guard_words('yarın okula gidicem', 'Yarın okula gideceğim.') == ('Yarın okula gideceğim.', 0)
    assert guard_words('bilmiyom ki napcam', 'Bilmiyorum ki ne yapacağım.')[1] == 0
    text, blocked = guard_words('okula gideceğim', 'eğitim kurumuna gideceğim')
    assert blocked == 1 and text.startswith('okula')
    text, blocked = guard_words('kedi geldi', 'Köpek geldi.')
    assert blocked == 1 and text.startswith('kedi')
    assert guard_words('evi gördüm', 'evi dün gördüm')[1] == 1
