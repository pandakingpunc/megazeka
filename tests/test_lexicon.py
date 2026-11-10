import gzip
import json
import pytest
from megazeka import lexicon
from megazeka import inference


def tiny_known(word, min_count=1):
    counts = {'sıcak': 3, 'ankaraya': 3, "ankara'ya": 3, 'bi': 4, 'bir': 50, 'herşey': 4,
              'geldi': 2, 'yabani': 3}
    words = lexicon.tokens(word)
    return len(words) == 1 and counts.get(words[0], 0) >= min_count


@pytest.mark.parametrize('source,candidate,expected,blocked', [
    ('Hava sıcak', 'Hava sıyacak', 'Hava sıcak', 1),
    ('gidicem', 'Gideceğim.', 'Gideceğim.', 0),
    ('Ankaraya', "Ankara'ya", "Ankara'ya", 0),
    ('sıcak', 'Sıyacak.', 'Sıcak.', 1),
    ('sıcak!', 'Sıyacak?', 'Sıcak?', 1),
    ('hava sıcak', 'Hava sıyacak!', 'Hava sıcak!', 1),
    ('bi şey', 'bir şey', 'bir şey', 0),
    ('yabani kuş', 'yabanı kuş', 'yabani kuş', 1),
    ('herşey', 'her şey', 'her şey', 0),
    ('geldi', 'Galdı.', 'Galdı.', 0),
    ('sıcak', 'çok sıcak', 'çok sıcak', 0),
    ('çok sıcak', 'sıcak', 'sıcak', 0),
    ('sıcak bi', 'sıyacak bir', 'sıyacak bir', 0),
])
def test_lexicon_guard(source, candidate, expected, blocked):
    assert inference.guard_lexicon(source, candidate, known=tiny_known) == (expected, blocked)


def test_lexicon_frequency_apostrophes_and_deterministic_bytes():
    counts = lexicon.build_lexicon(["Ankara'ya, ANKARA’YA! Sıcak; İYİ."])
    assert counts == {"ankara'ya": 2, 'ankara': 2, 'sıcak': 1, 'iyi': 1}
    assert lexicon.cache_bytes(counts) == lexicon.cache_bytes(dict(reversed(list(counts.items()))))
    assert json.loads(gzip.decompress(lexicon.cache_bytes(counts))) == counts


def test_lazy_cache_and_missing_raw(tmp_path, monkeypatch):
    monkeypatch.setattr(lexicon, 'CACHE', tmp_path / 'lexicon.json.gz')
    monkeypatch.setattr(lexicon, 'RAW', tmp_path / 'absent.txt')
    lexicon.load_lexicon.cache_clear()
    try:
        with pytest.warns(RuntimeWarning, match='Sözlük koruması kapalı'):
            assert not lexicon.known('sıcak')
        lexicon.CACHE.write_bytes(lexicon.cache_bytes({'sıcak': 3}))
        lexicon.load_lexicon.cache_clear()
        assert lexicon.known('Sıcak!', min_count=3)
        assert not lexicon.known('sıcak', min_count=4)
    finally:
        lexicon.load_lexicon.cache_clear()


def test_guard_default_is_off_and_opt_in_warns(monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError('Varsayılan koruma sözlüğe erişmemeli.')
    monkeypatch.setattr(lexicon, 'known', unexpected)
    assert inference.LEXICON_GUARD_DEFAULT is False
    assert inference.guard('sıcak', 'Sıyacak.', [1]) == ('Sıyacak.', None)
    monkeypatch.setattr(lexicon, 'known', tiny_known)
    text, warning = inference.guard('sıcak', 'Sıyacak.', [1], lexicon_guard=True)
    assert text == 'Sıcak.' and '1 kelime sözlük korumasıyla' in warning


def test_load_builds_raw_and_everyday_lexicon(tmp_path, monkeypatch):
    from training import everyday
    raw = tmp_path / 'common_voice_tr.txt'
    raw.write_text('İlk satır.\nİkinci satır.\nSon satır.\n', encoding='utf-8')
    monkeypatch.setattr(lexicon, 'RAW', raw)
    monkeypatch.setattr(lexicon, 'CACHE', tmp_path / 'lexicon.json.gz')
    monkeypatch.setattr(everyday, 'sentences', lambda: ['Gündelik temiz hedef.'])
    lexicon.load_lexicon.cache_clear()
    try:
        assert lexicon.known('son') and lexicon.known('gündelik')
        assert lexicon.known('satır', min_count=3)
        assert lexicon.CACHE.read_bytes() == lexicon.cache_bytes(lexicon.load_lexicon())
    finally:
        lexicon.load_lexicon.cache_clear()


def test_checkpoint_names_and_directory_validation(tmp_path, monkeypatch):
    monkeypatch.setattr(inference, 'ROOT', tmp_path)
    path = tmp_path / 'models/checkpoints/v3.1b'
    path.mkdir(parents=True)
    assert inference.checkpoint_path('v3.1b') == path
    for name in ['../v3', 'v3/child', 'v3\\child', '..', '.', 'v3..1', '', 'C:foo', 'missing']:
        with pytest.raises(ValueError):
            inference.checkpoint_path(name)
