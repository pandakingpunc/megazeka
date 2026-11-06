"""Model-free tests for the vendored core. Run: pytest test_core.py"""
from megazeka_core import chunks, normalize, guard, guard_words, lower_tr, fold


def test_chunking_preserves_layout():
    text = "  ilk satır   burada\n\n\nikinci satır\t sonu  \n" + ("kelime " * 60).strip()
    parts = chunks(normalize(text))
    assert ''.join(p for p, _ in parts) == text
    assert all(len(p.encode('utf-8')) <= 176 for p, layout in parts if not layout)
    assert all(p.strip() == '' for p, layout in parts if layout)


def test_chunking_crlf_normalized_and_long_word_lossless():
    text = "a\r\nb" + "ş" * 200
    out = ''.join(p for p, _ in chunks(normalize(text)))
    assert out == "a\nb" + "ş" * 200


def test_word_guard_blocks_synonym_swap():
    text, blocked = guard_words("yarın okula gidicem", "yarın eğitim kurumuna gidicem")
    assert blocked == 1
    assert text == "yarın okula gidicem"


def test_word_guard_allows_spelling_fix():
    text, blocked = guard_words("yarın okula gidicem", "yarın okula gideceğim")
    assert blocked == 0
    assert text == "yarın okula gideceğim"


def test_word_guard_blocks_deleted_and_inserted_words():
    assert guard_words("bu çok güzel bir gün", "bu güzel bir gün")[1] == 1
    assert guard_words("bu güzel gün", "bu çok güzel gün")[1] == 1


def test_chunk_guard_rejects_empty_output():
    final, warning = guard("herkez geldi", "   ", [1])
    assert final == "herkez geldi" and warning


def test_chunk_guard_rejects_missing_eos_and_too_short():
    assert guard("herkez geldi", "herkes geldi", [5, 6])[1]  # no EOS id 1
    assert guard("herkez burada toplandı", "herkes", [5, 1])[1]  # < 65% length
    assert guard("herkez geldi", "herkes geldi", [5, 1]) == ("herkes geldi", None)


def test_turkish_case_folding():
    assert lower_tr("IŞIK İLE") == "ışık ile"
    assert fold("Çağrı!") == "cagri"
