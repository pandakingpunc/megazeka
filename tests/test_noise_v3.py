import gzip
import hashlib
import json
import random
from megazeka.colloquial import hard_candidates, ne_candidates
from megazeka.noise import NoiseGenerator
from megazeka.spelling import misspelling_candidates, apostrophe_candidates, misspell, drop_proper_apostrophe
from megazeka.storage import ROOT
from megazeka.text import lower_tr, upper_first, swapcase_tr, canonical


def forms(candidates):
    return {f for _, _, fs in candidates for f in fs}


def test_softening_verbs_use_the_hard_consonant():
    assert 'gitcez' in forms(hard_candidates('Yarın sinemaya gideceğiz.'))
    assert 'gitcem' in forms(hard_candidates('Okula gideceğim.'))
    assert 'gitcek' in forms(hard_candidates('Sen de gidecek misin?'))
    assert {'gitcen', 'gitceksin'} <= forms(hard_candidates('Sen de gideceksin.'))
    assert 'etcem' in forms(hard_candidates('Sana yardım edeceğim.'))
    assert 'etcek' in forms(hard_candidates('Bunu kabul edecek misin?'))
    assert 'tatcaz' in forms(hard_candidates('Yemeği tadacağız.'))
    assert 'kaybetcem' in forms(hard_candidates('Maçı kaybedeceğim.'))
    assert 'Gitcem' in forms(hard_candidates('Gideceğim.'))
    # No softened stem, nothing to harden.
    assert not hard_candidates('Yarın yapacağım.') and not hard_candidates('Gelecek hafta görüşürüz.')
    assert not hard_candidates('Dün gittim.')


def test_sert_unsuz_operation_changes_text_deterministically():
    out = NoiseGenerator(1).apply('Yarın sinemaya gideceğiz.', 'sert_ünsüz')
    assert out == 'Yarın sinemaya gitcez.'
    assert NoiseGenerator(1).apply('Okula gidiyorum.', 'sert_ünsüz') == 'Okula gidiyorum.'


def test_ne_contractions():
    assert {'napcam', 'napıcam'} <= forms(ne_candidates('Ben ne yapacağım?'))
    assert {'napıyosun', 'napıyon'} <= forms(ne_candidates('Bugün ne yapıyorsun?'))
    assert 'Noldu' in forms(ne_candidates('Ne oldu sana?'))
    assert 'Naber' in forms(ne_candidates('Ne haber, nasılsın?'))
    assert 'Nolur' in forms(ne_candidates('Ne olur gel.'))
    assert not ne_candidates('Napolyon geldi.') and not ne_candidates('Bu ne kadar?')
    assert NoiseGenerator(3).apply('Sen ne yapıyorsun?', 'ne_kısalt') != 'Sen ne yapıyorsun?'


def test_common_misspellings():
    assert 'Yanlız' in forms(misspelling_candidates('Yalnız kaldım.'))
    assert misspell('Bu herkesin işi.', random.Random(0)) == 'Bu herkezin işi.'
    assert 'şöför' in forms(misspelling_candidates('Bu şoför iyi.'))
    assert misspell('Bu yanlışlıkla oldu.', random.Random(0)) == 'Bu yalnışlıkla oldu.'
    assert 'yada' in forms(misspelling_candidates('Çay ya da kahve?'))
    assert 'makina' in forms(misspelling_candidates('Bu makine bozuk.'))
    assert not misspelling_candidates('Makineler bozuk.')  # whole-word rules do not fire on suffixed forms
    assert not misspelling_candidates('Bugün hava güzel.')
    rng = random.Random(0)
    assert misspell('Yalnız başıma kaldım.', rng) == 'Yanlız başıma kaldım.'
    assert misspell('Bugün hava güzel.', rng) == 'Bugün hava güzel.'


def test_proper_noun_apostrophe_drop():
    rng = random.Random(0)
    assert drop_proper_apostrophe("Yarın Ankara'ya gideceğim.", rng) == 'Yarın Ankaraya gideceğim.'
    assert drop_proper_apostrophe('Işık’ın kitabı burada.', rng) == 'Işıkın kitabı burada.'
    assert drop_proper_apostrophe("ankara'dan geldim", rng) == 'ankaradan geldim'
    # a lowercase non-name keeps its apostrophe
    assert drop_proper_apostrophe("bu o'nun kitabı", rng) == "bu o'nun kitabı"
    assert len(apostrophe_candidates("İstanbul'a ve Ayşe'nin evine")) == 2
    for seed in range(20):
        out = drop_proper_apostrophe("İzmir'den Bursa'ya gittik.", random.Random(seed))
        assert out != "İzmir'den Bursa'ya gittik."
    assert NoiseGenerator(5).apply("Türkiye'de hava güzel.", 'özel_ad_kesme') == 'Türkiyede hava güzel.'


def test_turkish_casing_round_trip_for_i_names():
    assert lower_tr('Işık') == 'ışık' and upper_first('ışık') == 'Işık'
    assert lower_tr('İzmir') == 'izmir' and upper_first('izmir') == 'İzmir'
    assert lower_tr('Iğdır') == 'ığdır' and upper_first('ığdır') == 'Iğdır'
    assert swapcase_tr('Işık İzmir') == 'ıŞIK iZMİR'
    text = "Işık, İzmir'e Isparta'dan İpek ile geldi."
    assert swapcase_tr(swapcase_tr(text)) == text
    gen = NoiseGenerator(11)
    seen = set()
    for _ in range(300):
        out = gen.apply(text, 'küçük_harf')
        seen.add(out)
        # str.swapcase / str.lower would turn İ into i + U+0307 and change the length
        assert '̇' not in out and len(out) == len(text)
        if out == lower_tr(text):
            assert out == "ışık, izmir'e ısparta'dan ipek ile geldi."
    assert any(o.startswith('ıŞIK') for o in seen) and any(o.startswith('ışık') for o in seen)


def test_everyday_names_use_correct_suffixes_and_cover_i_names():
    from training.everyday import suffix, sentences
    assert suffix('Işık', 'gen') == "Işık'ın" and suffix('Ahmet', 'abl') == "Ahmet'ten"
    assert suffix('Ayşe', 'with') == "Ayşe'yle" and suffix('Iğdır', 'dat') == "Iğdır'a"
    assert suffix('İzmir', 'loc') == "İzmir'de" and suffix('Ali', 'gen') == "Ali'nin" and suffix('Van', 'abl') == "Van'dan"
    rows = sentences()
    assert len({canonical(r) for r in rows}) == len(rows)
    text = '\n'.join(rows)
    for needle in ["Işık'", 'Irmak', 'Ilgaz', 'İpek', "Isparta'", "Iğdır'", 'gideceğiz', 'edeceğim', 'ne yapacağım', 'Ne oldu']:
        assert needle in text, needle
    assert sum('ne yap' in r.lower() for r in rows) > 150


def test_frozen_test_split_is_the_v2_file_and_challenge_is_held_out():
    meta = json.loads((ROOT / 'data/metadata.json').read_text(encoding='utf-8'))
    path = ROOT / 'data/processed/test.jsonl.gz'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == meta['splits']['test']['sha256']
    assert meta['splits']['test'].get('frozen_from') == 'v2'
    challenge = [json.loads(l) for l in (ROOT / 'evaluation/challenge.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    assert 60 <= len(challenge) <= 100 and all({'source', 'target', 'category'} <= set(c) for c in challenge)
    targets = {canonical(c['target']) for c in challenge}
    for split in ('train', 'validation'):
        with gzip.open(ROOT / f'data/processed/{split}.jsonl.gz', 'rt', encoding='utf-8') as stream:
            for line in stream:
                row = json.loads(line)
                assert canonical(row['target']) not in targets
                assert canonical(row.get('target', '')) not in targets


def test_challenge_summary():
    from evaluation.challenge import summarize
    rows = [{'source': 'a', 'target': 'b', 'output': 'b', 'category': 'x'},
            {'source': 'c', 'target': 'c', 'output': 'd', 'category': 'y'},
            {'source': 'e', 'target': 'e', 'output': 'e', 'category': 'y'}]
    result = summarize(rows)
    assert result['exact'] == 2 and result['categories']['y']['exact'] == 1
    assert result['clean_total'] == 2 and result['clean_changed'] == 1 and result['overcorrection'] == .5
