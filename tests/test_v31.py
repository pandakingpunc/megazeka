from megazeka import colloquial
from training import everyday
from training.prepare import load_corrections


def _all_variants():
    tables = [colloquial.WORDS, colloquial.NE]
    for table in tables:
        for key, values in table.items():
            yield key, values


def test_valid_standard_forms_are_not_noise_targets():
    variants = {v for _, values in _all_variants() for v in values}
    assert not {'abi', 'tabi', 'bilmem'} & variants
    assert 'tabii' not in colloquial.WORDS and 'ağabey' not in colloquial.WORDS
    assert all(values for _, values in _all_variants())
    assert {'bilmiyom', 'blmiyorum'} <= set(colloquial.WORDS['bilmiyorum'])


def test_person_clash_positive():
    for text in ['Yakında seni unutur musun?', 'Sen seni izliyorsun sanırım.',
                 'Yarın akşam bana yardım edeceğim, değil mi?', 'Yakında seni ziyaret edeceksiniz kesinlikle.']:
        assert everyday.person_clash(text), text


def test_person_clash_negative():
    for text in ['Bu pantolon bana büyük geldi sanırım.', 'Annem seni çağırıyor.', 'Neredesin, seni bekliyoruz.',
                 'Yalnız bir şey söyleyeceğim sana.', 'Herkes sana teşekkür ediyor.']:
        assert not everyday.person_clash(text), text


def test_everyday_sentences_are_clean():
    rows = everyday.sentences()
    assert rows
    assert not [r for r in rows if everyday.person_clash(r)]
    assert not [r for r in rows if any(p in r for p in ("'den bir şey sordum", "'dan bir şey sordum",
                                                         "'ten bir şey sordum", "'tan bir şey sordum"))]


def test_load_corrections_reads_audit_file():
    fixes, drops = load_corrections()
    assert fixes and drops
    assert not set(fixes) & drops
    assert load_corrections('does/not/exist.jsonl') == ({}, set())
