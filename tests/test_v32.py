"""v3.2 coverage and the v3.1 stream contract (including joined sentences)."""
from collections import Counter
import gzip
import json
import random
import re

import pytest

from megazeka.noise import NoiseGenerator
from megazeka.spelling import (MISSPELLINGS, MISSPELLINGS_V32, NAMES_V32, PROPER_NAMES,
                               misspelling_candidates)
from megazeka.storage import ROOT
from megazeka.text import canonical, lower_tr
from training import prepare, targeted, v35


@pytest.fixture(scope='module')
def sentences():
    return targeted.sentences()


def test_spelling_tables_and_opt_in_round_trip():
    entries = MISSPELLINGS + MISSPELLINGS_V32
    assert 60 <= len(entries) <= 90
    correct_forms = {correct for correct, _, _ in entries}
    for correct, wrong_forms, whole in entries:
        assert wrong_forms
        for wrong in wrong_forms:
            assert wrong != correct and wrong not in correct_forms
            candidates = misspelling_candidates(correct, v32=True)
            assert (0, len(correct), wrong_forms) in candidates
        text = f'Örnek: {correct}.'
        outputs = {NoiseGenerator(seed).apply(text, 'yazım_yanlışı_v32') for seed in range(60)}
        allowed = {f'Örnek: {wrong}.' for c, ws, _ in entries if c == correct for wrong in ws}
        assert outputs == allowed
        # Noise must preserve everything outside the chosen spelling span.
        for output in outputs:
            assert output.startswith('Örnek: ') and output.endswith('.')
            assert output[7:-1] in {w for c, ws, _ in entries if c == correct for w in ws}
    assert not misspelling_candidates('Tıraş oldum.')
    assert 'Traş' in {w for _, _, ws in misspelling_candidates('Tıraş oldum.', v32=True) for w in ws}
    assert misspelling_candidates('Tıraşlar', v32=True)
    assert not misspelling_candidates('Aferinlik', v32=True)
    assert 'yazım_yanlışı_v32' not in NoiseGenerator.names
    assert 'özel_ad_bozma' not in NoiseGenerator.names
    assert 'yazım_yanlışı_v32' not in NoiseGenerator.targeted
    assert 'ılıca' not in PROPER_NAMES
    assert NoiseGenerator(4).apply('Tıraş oldum.', 'yazım_yanlışı_v32') == 'Traş oldum.'


@pytest.mark.parametrize('name,expected', [
    ('Isparta', {'ısparta', 'isparta', 'İsparta'}),
    ('Iğdır', {'ığdır', 'Igdir', 'igdir', 'İğdır'}),
    ('Işık', {'ışık', 'Isik', 'isik', 'İşık'}),
    ('İzmir', {'izmir', 'Izmir'}),
])
def test_proper_name_keyboard_variants(name, expected):
    text = f'{name} güzel bir yer.'
    outputs = {NoiseGenerator(seed).apply(text, 'özel_ad_bozma').split()[0] for seed in range(200)}
    assert outputs == expected
    assert NoiseGenerator(8).apply(text, 'özel_ad_bozma') == NoiseGenerator(8).apply(text, 'özel_ad_bozma')
    suffixed = f"Bugün {targeted.suffix(name, 'dat')} gittik."
    outputs = {NoiseGenerator(seed).apply(suffixed, 'özel_ad_bozma') for seed in range(200)}
    assert any("'" not in text for text in outputs)
    assert any("'" in text for text in outputs)
    assert all('̇' not in text for text in outputs)
    assert NoiseGenerator(1).apply('Islak havluyu dışarı astım.', 'özel_ad_bozma') == 'Islak havluyu dışarı astım.'


@pytest.mark.parametrize('name,case,expected', [
    ('Isparta', 'dat', "Isparta'ya"), ('Isparta', 'gen', "Isparta'nın"),
    ('Iğdır', 'dat', "Iğdır'a"), ('Iğdır', 'abl', "Iğdır'dan"),
    ('Işık', 'gen', "Işık'ın"), ('Işık', 'abl', "Işık'tan"),
    ('İzmir', 'dat', "İzmir'e"), ('Irak', 'loc', "Irak'ta"),
    ('İpek', 'gen', "İpek'in"), ('İpek', 'abl', "İpek'ten"),
    ('Ilıca', 'with', "Ilıca'yla"), ('İnegöl', 'gen', "İnegöl'ün"),
    ('İspir', 'loc', "İspir'de"), ('İsveç', 'abl', "İsveç'ten"),
    ('Ilgın', 'loc', "Ilgın'da"), ('İstanbul', 'gen', "İstanbul'un"),
    ('Ilgaz', 'dat', "Ilgaz'a"), ('İsmail', 'gen', "İsmail'in"),
])
def test_suffix_harmony(name, case, expected):
    assert targeted.suffix(name, case) == expected


def test_targeted_determinism_bounds_and_uniqueness(sentences):
    state = random.getstate()
    assert sentences == targeted.sentences()
    assert sentences != targeted.sentences(seed=3201)
    assert state == random.getstate()
    counts = Counter(row['kind'] for row in sentences)
    assert set(counts) == {'yazım', 'özel_ad', 'koruma'}
    assert all(1000 <= count <= 1300 for count in counts.values())
    assert 3000 <= len(sentences) <= 3600
    assert len({canonical(row['target']) for row in sentences}) == len(sentences)
    for row in sentences:
        text = row['target']
        assert text[0].isupper() and text[-1] in '.?!'
        assert 3 <= len(text.split()) <= 14
        assert 18 <= len(text.encode('utf-8')) <= 160
        assert not re.search(r'\btabi\b', lower_tr(text))


def test_every_spelling_is_covered_in_twelve_distinct_targets(sentences):
    for correct, _, whole in MISSPELLINGS + MISSPELLINGS_V32:
        pattern = r'(?<!\w)' + re.escape(correct) + (r'(?!\w)' if whole else '')
        targets = {row['target'] for row in sentences if row['kind'] == 'yazım'
                   and re.search(pattern, lower_tr(row['target']))}
        assert len(targets) >= 12, (correct, len(targets))


# Include lexical time expressions too, even when they are the focus itself.
# This independent list catches reintroduction of forced adverbs outside slots.
TIME_EXPRESSIONS = tuple(dict.fromkeys(targeted.TIME_EXPRESSIONS + (
    'az önce', 'geçen hafta', 'dün', 'bu sabah', 'yarın', 'bugün', 'akşam',
    'sabah', 'sabahleyin', 'hafta sonu', 'geçen yıl', 'şimdi', 'birazdan',
    'her gün', 'her zaman', 'bazen', 'hâlâ', 'artık', 'sonunda', 'o zaman',
    'daima', 'henüz', 'erken', 'yeni',
)))


def _time_matches(text):
    text = lower_tr(text)
    return {expression for expression in TIME_EXPRESSIONS
            if re.search(r'(?<!\w)' + re.escape(expression) + r'(?!\w)', text)}


def _skeleton(row):
    text = lower_tr(row['target'])
    focus = lower_tr(row['focus'])
    text = re.sub(r'(?<!\w)' + re.escape(focus) + r"[\w'’]*", '<focus>', text)
    for expression in sorted(TIME_EXPRESSIONS, key=len, reverse=True):
        text = re.sub(r'(?<!\w)' + re.escape(expression) + r'(?!\w)', '', text)
    for name in targeted.PEOPLE:
        text = re.sub(r'(?<!\w)' + re.escape(lower_tr(name)) + r"[\w'’]*", '<person>', text)
    return ' '.join(text.split())


def test_time_first_word_and_template_diversity(sentences):
    used = set()
    for kind in ('yazım', 'özel_ad', 'koruma'):
        rows = [r for r in sentences if r['kind'] == kind]
        matches = [_time_matches(r['target']) for r in rows]
        times = Counter(t for found in matches for t in found)
        used.update(times)
        assert sum(bool(found) for found in matches) <= len(rows) * .35
        assert max(times.values(), default=0) <= len(rows) * .06
        first_words = {lower_tr(r['target'].split()[0]).strip(',.?!') for r in rows}
        assert len(first_words) >= 150, (kind, len(first_words))
        # Stronger than focus masking alone: ignore people and time slots too.
        skeletons = Counter(_skeleton(r) for r in rows)
        assert max(skeletons.values()) <= len(rows) * .01, (kind, skeletons.most_common(3))
    assert len(used) >= 25
    assert len(targeted.PEOPLE) >= 30
    assert len(set(targeted.TIME_EXPRESSIONS)) >= 25


def test_authored_contexts_and_suffixed_spelling_coverage(sentences):
    for row in sentences:
        if row['kind'] == 'yazım':
            assert any(lower_tr(row['target'][start:end]) == row['focus']
                       for start, end, _ in misspelling_candidates(row['target'], v32=True)), row
    for focus, frames in targeted.SPELLING_FRAMES.items():
        # A date/person/lexical substitution cannot count as an authored context.
        def shape(frame):
            frame = re.sub(r'\{[^}]+\}', '<slot>', frame)
            return re.sub(r'\[[^]]+\]', '<choice>', frame)
        assert len({shape(frame) for frame in frames}) >= 12, focus
    for correct, _, whole in MISSPELLINGS + MISSPELLINGS_V32:
        if not whole:
            assert any(r['kind'] == 'yazım' and r['focus'] == correct
                       and re.search(r'(?<!\w)' + re.escape(correct) + r'\w+', lower_tr(r['target']))
                       for r in sentences), correct
    for focus, frames in targeted.PROTECTION.items():
        rows = [r for r in sentences if r['kind'] == 'koruma' and r['focus'] == focus]
        assert len(frames) >= 12, focus
        assert len({_skeleton(r) for r in rows}) >= 10, focus
    assert all('resmî' not in lower_tr(r['target']) for r in sentences)
    for form in ('sıcakta', 'sıcağı', 'bıçağı', 'oyuncakları', 'kucağına',
                 'ocakta', 'yabani otlar', 'ciddiye', 'resmi'):
        assert any(form in lower_tr(r['target']) for r in sentences if r['kind'] == 'koruma'), form


def test_all_i_names_have_positions_cases_and_cross_boundary_contexts(sentences):
    rows = [r for r in sentences if r['kind'] == 'özel_ad']
    for name in sorted(n for n in NAMES_V32 if n.startswith(('I', 'İ'))):
        targets = [r['target'] for r in rows if name in r.get('names', [])]
        assert len(set(targets)) >= 25, (name, len(targets))
        pattern = re.escape(name) + r"(?:['’]\w+)?"
        assert any(re.match(pattern + r'\b', text) for text in targets), name
        assert any(re.search(r'\s' + pattern + r'\s', text) for text in targets), name
        assert any(re.search(r'\s' + re.escape(name) + r'[.?!]$', text) for text in targets), name
        for case in ('dat', 'gen', 'abl'):
            assert any(targeted.suffix(name, case) in text for text in targets), (name, case)
    for name in targeted.I_PEOPLE + targeted.DOTTED_PEOPLE:
        assert any(name in r.get('names', [])
                   and any(n.startswith('I') for n in r['names'])
                   and any(n.startswith('İ') for n in r['names']) for r in rows), name
    for word in ('Ilık', 'Islak', 'Isı', 'Işık', 'Irmak', 'Izgara', 'Israr', 'Ihlamur', 'Isırgan'):
        assert any(not r.get('names') and r['target'].startswith(word + ' ') for r in rows), word


def test_all_authored_alternatives_fit_without_optional_time():
    # Bounds must hold even when every time slot is omitted, for both choices.
    rng = random.Random(3200)
    catalogs = (targeted.SPELLING_FRAMES, targeted.PROTECTION, targeted.INITIAL_COMMON)
    for catalog in catalogs:
        for frames in catalog.values():
            for frame in frames:
                for category in targeted.TIME_POOLS:
                    frame = frame.replace('{' + category + '}', '')
                for variant in (0, 1):
                    text = targeted._render(frame, rng, variant)
                    assert 3 <= len(text.split()) <= 14, text
                    assert 18 <= len(text.encode('utf-8')) <= 160, text
    for names, frames in ((targeted.I_PLACES + targeted.DOTTED_PLACES, targeted.PLACE_FRAMES),
                          (targeted.I_PEOPLE + targeted.DOTTED_PEOPLE, targeted.PERSON_FRAMES)):
        for name in names:
            forms = {case: targeted.suffix(name, case) for case in ('dat', 'abl', 'loc', 'gen', 'with')}
            for frame in frames:
                for category in targeted.TIME_POOLS:
                    frame = frame.replace('{' + category + '}', '')
                for variant in (0, 1):
                    text = targeted._render(frame, rng, variant, name=name, other='İpek', **forms)
                    assert 3 <= len(text.split()) <= 14, text
                    assert 18 <= len(text.encode('utf-8')) <= 160, text


def test_holdout_preserves_spelling_coverage_and_blocks_sources(sentences):
    blocked = {canonical(sentences[0]['target'])}
    splits, counts, dropped = prepare.targeted_splits(blocked)
    assert dropped == 1 and sum(counts.values()) == len(sentences) - 1
    assert all(canonical(r['target']) not in blocked for rows in splits.values() for r in rows)
    for correct in {c for c, _, _ in MISSPELLINGS + MISSPELLINGS_V32}:
        assert sum(r.get('focus') == correct for r in splits['train']) >= 12
    for kind, total in counts.items():
        assert sum(r['kind'] == kind for r in splits['validation']) == round(total * .08)


def test_targeted_pair_policy(sentences):
    rows = prepare.targeted_pairs(sentences, 4200)
    clean = Counter(r['kind'] for r in rows if r['difficulty'] == 'temiz')
    counts = Counter(r['kind'] for r in sentences)
    assert clean == Counter({k: n * (2 if k == 'koruma' else 1) for k, n in counts.items()})
    for row in rows:
        if row['kind'] == 'yazım' and row['difficulty'] in ('kolay', 'orta'):
            assert row['operations'][0]['operation'] == 'yazım_yanlışı_v32', row
        if row['kind'] == 'özel_ad' and row['names'] and row['difficulty'] != 'temiz':
            assert row['operations'][0]['operation'] == 'özel_ad_bozma', row


def test_challenge_keys_reads_all_matching_files(tmp_path, monkeypatch):
    directory = tmp_path / 'evaluation'
    directory.mkdir()
    for filename, text in [('challenge.jsonl', 'Birinci hedef burada.'),
                           ('challenge2.jsonl', 'İkinci hedef burada.'),
                           ('challenge_extra.jsonl', 'Üçüncü hedef burada.')]:
        (directory / filename).write_text(json.dumps({'target': text}), encoding='utf-8')
    monkeypatch.setattr(prepare, 'ROOT', tmp_path)
    assert prepare.challenge_keys() == {canonical(t) for t in
                                          ('Birinci hedef burada.', 'İkinci hedef burada.', 'Üçüncü hedef burada.')}


def _read(path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        return [json.loads(line) for line in stream]


def test_legacy_stream_identity_and_frozen_test():
    """v3.1 -> v3.2: the v3.2 stream is checked on its archive, not on the live data.

    `data/processed` is now the v3.5 dataset, so the v3.2 contract is verified on
    `data/v3.2-backup` (gitignored; skipped when the local archives are absent).
    """
    backup = ROOT / 'data/v3.1-backup'
    archive = ROOT / 'data/v3.2-backup'
    for folder in (backup, archive):
        if not (folder / 'train.jsonl.gz').exists():
            pytest.skip(f'{folder.name} is not installed')
    # Only removals required by NEW challenge files are permitted. For joined
    # examples, neither constituent may leak into training either.
    new_keys = prepare.challenge_keys() - prepare._challenge_keys([prepare.CHALLENGE])
    new_groups = {prepare.group_of(k) for k in new_keys}
    fields = ('input', 'target', 'difficulty', 'source')
    for split in ('train', 'validation'):
        expected = [r for r in _read(backup / f'{split}.jsonl.gz')
                    if r['group_id'] not in new_groups and r.get('group_id_second') not in new_groups
                    and canonical(r['target']) not in new_keys]
        actual = [r for r in _read(archive / f'{split}.jsonl.gz') if r['source'] != prepare.TARGETED_SOURCE]
        assert Counter(tuple(r[k] for k in fields) for r in actual) == Counter(tuple(r[k] for k in fields) for r in expected)
        # Also retain operation history and all legacy metadata verbatim.
        assert Counter(json.dumps(r, sort_keys=True) for r in actual) == Counter(json.dumps(r, sort_keys=True) for r in expected)
    assert prepare.TEST_PATH.read_bytes() == (backup / 'test.jsonl.gz').read_bytes()
    assert json.loads((archive / 'metadata.json').read_text(encoding='utf-8'))['version'] == 'v3.2'


def test_processed_targeted_splits_are_disjoint_and_blocked():
    split_rows = {split: prepare.read_pairs(split) for split in ('train', 'validation', 'test')}
    keys = {split: {canonical(r['target']) for r in rows} for split, rows in split_rows.items()}
    assert not keys['train'] & keys['validation']
    assert not keys['train'] & keys['test']
    assert not keys['validation'] & keys['test']
    for split, rows in split_rows.items():
        if split != 'test':
            assert not keys[split] & prepare.challenge_keys()
        extra = [r for r in rows if r['source'] == prepare.TARGETED_SOURCE]
        assert bool(extra) == (split != 'test')
    metadata = json.loads((ROOT / 'data/metadata.json').read_text(encoding='utf-8'))
    # Live data is the v3.5 dataset (v3.2 data + audit + explicit additions); v3.2 stays in its archive.
    assert metadata['version'] == 'v3.5'
    assert metadata['splits']['train']['pairs'] == len(split_rows['train'])
    assert metadata['splits']['validation']['pairs'] == len(split_rows['validation'])
    assert metadata['splits']['test']['pairs'] == len(split_rows['test'])
    added = Counter(r['source'] for split in ('train', 'validation') for r in split_rows[split])
    assert added[v35.SOURCE] == sum(metadata['v35']['added'][s]['pairs'] for s in ('train', 'validation'))
    assert not any(r['source'] == v35.SOURCE for r in split_rows['test'])
    assert metadata['targeted_source']['sentences'] == sum(metadata['targeted_source']['by_kind'].values())
