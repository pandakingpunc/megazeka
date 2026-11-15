import pytest
from megazeka import dictionary
from megazeka.dictionary import assist

WORDS = {'misafir', 'geldi', 'sensörü', 'asansörü', 'bugün', 'hava', 'güzel'}
TABLE = {'müsafir': ['misafir'], 'asensörü': ['sensörü', 'asansörü'], 'kirem': ['krem', 'karem']}


def valid(word):
    return word.lower() in WORDS


def candidates(word):
    return list(TABLE.get(word, []))


def never(word, min_count=1):
    return False


def scorer(table, default=-10.0):
    calls = []
    def score(source, sentences):
        calls.append(sentences)
        return [table.get(s, default) for s in sentences]
    score.calls = calls
    return score


def run(source, candidate, score, **kw):
    kw.setdefault('known', never)
    return assist(source, candidate, score, valid=valid, candidates=candidates, **kw)


def test_valid_word_untouched():
    score = scorer({})
    assert run('bugün hava güzel', 'bugün hava güzel', score) == ('bugün hava güzel', [])
    assert not score.calls


def test_invalid_single_candidate_applied():
    text, changes = run('müsafir geldi', 'müsafir geldi', scorer({'müsafir geldi': -20.0, 'misafir geldi': -5.0}))
    assert text == 'misafir geldi'
    assert changes == [{'old': 'müsafir', 'new': 'misafir', 'candidates': 1, 'gain': 15.0}]


def test_below_margin_unchanged():
    score = scorer({'müsafir geldi': -5.0, 'misafir geldi': -20.0})
    assert run('müsafir geldi', 'müsafir geldi', score, margin=8.0)[0] == 'müsafir geldi'
    assert run('müsafir geldi', 'müsafir geldi', score, margin=20.0)[0] == 'misafir geldi'


def test_best_of_several_candidates():
    score = scorer({'bugün asensörü': -9.0, 'bugün sensörü': -12.0, 'bugün asansörü': -7.0})
    assert run('bugün asensörü', 'bugün asensörü', score)[0] == 'bugün asansörü'


def test_mid_sentence_capitalised_word_skipped():
    score = scorer({})
    assert run('bugün Müsafir geldi', 'bugün Müsafir geldi', score)[0] == 'bugün Müsafir geldi'
    assert not score.calls


def test_sentence_start_capital_kept():
    text, _ = run('Müsafir geldi.', 'Müsafir geldi.', scorer({'Misafir geldi.': -1.0}))
    assert text == 'Misafir geldi.'
    text, _ = run('Hava güzel. Müsafir geldi.', 'Hava güzel. Müsafir geldi.', scorer({'Hava güzel. Misafir geldi.': -1.0}))
    assert text == 'Hava güzel. Misafir geldi.'


def test_trailing_punctuation_and_quotes_kept():
    text, _ = run('geldi müsafir,', 'geldi müsafir,', scorer({'geldi misafir,': -1.0}))
    assert text == 'geldi misafir,'
    text, _ = run('geldi "müsafir"!', 'geldi "müsafir"!', scorer({'geldi "misafir"!': -1.0}))
    assert text == 'geldi "misafir"!'


def test_whitespace_layout_preserved():
    text, _ = run('geldi  müsafir', 'geldi  müsafir\n', scorer({'geldi  misafir\n': -1.0}))
    assert text == 'geldi  misafir\n'


@pytest.mark.parametrize('word', ['müs1fir', "müsafir'e", 'müs-afir', 'MÜSAFİR', 'mü'])
def test_skipped_words(word):
    score = scorer({})
    assert run('geldi ' + word, 'geldi ' + word, score)[0] == 'geldi ' + word
    assert not score.calls


def test_known_word_skipped():
    score = scorer({})
    known = lambda word, min_count=1: word == 'müsafir' and min_count == dictionary.MIN_KNOWN_COUNT
    assert run('müsafir geldi', 'müsafir geldi', score, known=known)[0] == 'müsafir geldi'
    assert not score.calls


def test_candidate_limit():
    many = {'kirem': [f'k{i}' for i in range(dictionary.MAX_CANDIDATES + 1)]}
    score = scorer({})
    out = assist('kirem', 'kirem', score, valid=valid, candidates=lambda w: many.get(w, []), known=never)
    assert out == ('kirem', []) and not score.calls
    many['kirem'] = many['kirem'][:dictionary.MAX_CANDIDATES]
    assist('kirem', 'kirem', score, valid=valid, candidates=lambda w: many.get(w, []), known=never)
    assert len(score.calls[0]) == dictionary.MAX_CANDIDATES + 1


def test_no_candidates_untouched():
    score = scorer({})
    assert run('zzzzzz', 'zzzzzz', score)[0] == 'zzzzzz'
    assert not score.calls


def test_source_word_candidates_added():
    table = {'kirem': ['krem']}
    cands = lambda w: table.get(w, [])
    sentences = []
    def spy(source, options):
        sentences.append(options)
        return [-9.0, -9.0, -1.0][:len(options)]
    text, changes = assist('kirim', 'kirem', spy, valid=lambda w: w == 'kirim', candidates=cands, known=never)
    assert sentences[0] == ['kirem', 'krem', 'kirim']
    assert text == 'kirim' and changes[0]['candidates'] == 2


def test_source_candidates_skipped_when_word_counts_differ():
    seen = []
    def spy(source, options):
        seen.append(options)
        return [0.0] * len(options)
    assist('kirim yok', 'kirem', spy, valid=lambda w: w == 'kirim', candidates=lambda w: {'kirem': ['krem']}.get(w, []), known=never)
    assert seen[0] == ['kirem', 'krem']


def test_changes_flow_into_later_words():
    seen = []
    def spy(source, options):
        seen.append(options)
        return [-10.0] + [-1.0] * (len(options) - 1)
    text, changes = run('müsafir kirem', 'müsafir kirem', spy)
    assert text == 'misafir krem'
    assert seen[1][0] == 'misafir kirem' and len(changes) == 2


def test_real_zeyrek():
    pytest.importorskip('zeyrek')
    assert dictionary.valid('misafir')
    assert not dictionary.valid('müsafir')
    assert 'misafir' in dictionary.candidates('müsafir')
    assert dictionary.available()
