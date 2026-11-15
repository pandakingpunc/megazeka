---
language:
- tr
license: cc0-1.0
task_categories:
- text-generation
task_ids:
- text-simplification
tags:
- turkish
- spelling-correction
- grammatical-error-correction
- synthetic
- text-correction
size_categories:
- 10K<n<100K
source_datasets:
- original
annotations_creators:
- machine-generated
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train.jsonl.gz
  - split: validation
    path: data/validation.jsonl.gz
  - split: test
    path: data/test.jsonl.gz
---

# Megazeka · Turkish Spelling Correction Pairs

75,401 (misspelled → correct) Turkish sentence pairs with **a full record of every corruption that
was applied**, generated from the CC0 Common Voice Turkish Sentence Collector and from project-authored
everyday and targeted sentences.

The distinguishing feature is the `operations` field: each pair carries the exact sequence of noise
transformations that produced it, with before/after text at each step. That makes it possible to
evaluate a corrector per error type, how well does it handle diacritic loss versus merged words versus
chat-style spellings like `gidicem`?, rather than only in aggregate.

Used to train [`pandakingpunc/megazeka-byt5-tr-spellfix`](https://huggingface.co/pandakingpunc/megazeka-byt5-tr-spellfix) v4.
There is no hosted demo; a local Gradio app is in `space/` in the GitHub repo. Author: Mustafa Karatüm.
Generation code: [github.com/pandakingpunc/megazeka](https://github.com/pandakingpunc/megazeka)
(`training/prepare.py`, `training/everyday.py`, `training/targeted.py`, `training/v35.py`, `training/v35_extra.py`, `training/prepare_v35.py`, `src/megazeka/noise.py`, `src/megazeka/colloquial.py`,
`src/megazeka/spelling.py`).

## What's new in v4

The dataset release that goes with the v4 model (`main`). Its internal data version is **v3.5**: the label of the
Hugging Face release is `v4`, the files' internal version is `v3.5` (`metadata.json` → `version`). There was no separate public v3.5
release; a byt5-small model trained on this data was used only for comparison and never published. The previous release stays
available under tag `v3.2`.

v4/v3.5 is the v3.2 data with three changes:

- **Approved audit applied** (`data/audit/v3.5-approved.jsonl` in the GitHub repo): in train 30 targets corrected and
  109 removed; in validation 1 corrected and 3 removed.
- **15,038 new targeted training pairs and 795 validation pairs** with the new source label
  `Megazeka v3.5 hedefli / CC0-1.0`, written by hand from an extra misspelling catalog of 117 words
  (`training/v35_extra.py`) and `training/v35.py`. Kinds (`kind` field, train / validation):
  `yazım` 9,196 / 474, `koruma` 4,798 / 265 (correct sentences left unchanged on purpose), `özel_ad` 515 / 2,
  `açık_yazım` 337 / 23, `bağlaç` 152 / 9, `noktalama` 40 / 22. Each such row has `kind`, `focus` and `family`
  (the group the sentence was written for). The only operation recorded is `v35_explicit` (before/after text).
- **Leak checks.** New rows are rejected if they match the frozen test or any `evaluation/challenge*.jsonl` file
  (now five hand-written challenge sets, two of which are new in this release), or the opposite split
  (train: 2 test, 3 challenge, 8 opposite-split and 41 duplicate rows rejected; validation: 1 challenge, 4 opposite-split).
  The frozen test file is byte-identical to v2 (SHA-256 `43738c61…`).

Train is now 70,831 pairs (31,932 Common Voice, 8,792 everyday, 1,272 two-sentence chunks, 13,906 v3.2 targeted,
15,038 v3.5 targeted); validation 3,442 pairs; test 1,128 pairs. The v3.5 additions are not audited sentence by
sentence and use a closed word list (see *Limitations*).

## What was new in v3.2

(Kept for history.) v3.2 was `main` before v4; it stays available under tag `v3.2`, with `v3.1`, `v3`, `v2` and `v1`.

v3.2 adds a **third, targeted source** next to Common Voice and the everyday sentences:

- **`Megazeka hedefli şablon / CC0-1.0`** (`training/targeted.py`): 3,485 project-authored template
  sentences in three kinds, recorded in two extra fields on those rows, `kind` and `focus`:
  - `yazım` (1,149 sentences): sentences built around words that are commonly misspelled (`laboratuvar`,
    `kılavuz`, `şoför`, `tıraş`, `sarımsak`, …), each word in at least 12 different sentences;
  - `özel_ad` (1,160): proper names starting with I or İ (Isparta, Iğdır, Işık, İzmir, …) in different
    positions, bare and with apostrophe suffixes;
  - `koruma` (1,176): correct words a model tends to damage (`sıcak`, `yabani`, `denecek`, …); 40% of these
    pairs are left unchanged on purpose.
  This gives 13,906 train and 1,210 validation pairs.
- **Two new noise operations**, used only by the targeted source: `yazım_yanlışı_v32` (about 38 more
  misspellings: `traş`, `kirbit`, `sarmısak`, `şarz`, …) and `özel_ad_bozma` (I/İ confusion and lost
  capitals in proper names).
- **The older stream is unchanged.** The targeted source has its own seed and generator, so the Common
  Voice and everyday pairs are the same as in v3.1, except for a few sentences excluded because they are
  targets of the new challenge set.
- **Second challenge set.** 66 hand-written pairs (`evaluation/challenge2.jsonl` in the GitHub repo) were
  written before training; with the first set, 146 targets are excluded from train and validation
  (`metadata.json` → `challenge_targets_excluded`).
- **Test split.** Still byte-identical to v2. `evaluation/test_target_audit.jsonl` in the GitHub repo lists
  13 non-standard test targets; the split itself is not modified.

Train is now 55,902 pairs (31,932 Common Voice, 8,792 everyday, 1,272 two-sentence chunks, 13,906
targeted); validation is 2,650 pairs. The targeted sentence code was written by OpenAI Codex (GPT) coding
agents and reviewed with Claude.

## What was new in v3.1

(Kept for history.)

v3.1 was a **target-cleaning release**:

- **Audit.** All 10,560 distinct train/validation targets were audited in two rounds: 11 Claude Haiku
  subagents, then 11 Claude Sonnet subagents. Rule-based scans were added on top. Claude Opus verified every
  flag by hand.
- **Result.** 136 targets were corrected and 12 broken sentences removed. The corrections cover OCR errors
  in Common Voice (`memurlan → memurları`, `kaşlan → kaşları`, `Haşan → Hasan`), colloquial forms inside
  targets (`burda`, `nerde`, `içerde`), TDK spellings (`hiç bir → hiçbir`, `davavekili → dava vekili`) and
  titles (`Raif efendi → Raif Efendi`). Nonsensical template sentences such as `Sen seni izliyorsun` were
  also removed. The full list (`data/audit/corrections.jsonl`), the per-model flags and the report
  (`data/audit/RAPOR.md`) are in the GitHub repo. `metadata.json` → `target_corrections` records what was
  applied.
- **Noise rules.** Three rules that marked valid words as errors were removed: `ağabey → abi`,
  `bilmiyorum → bilmem`, `tabii → tabi`.
- **Templates.** The generator no longer pairs a subject with an object of the same person; the rest of the
  template stream is identical to v3.
- **Test split.** Still byte-identical to v2 (not cleaned, so results stay comparable). It contains at
  least 3 known non-standard targets: `şurda burda`, `nerdeyse`, `bitpazarı`.

Train is now 42,017 pairs (31,936 Common Voice, 8,808 everyday, 1,273 two-sentence chunks); validation is
1,440 pairs.

## What was new in v3

(Kept for history.)

- **Four new noise operations**: `sert_ünsüz` (hardened consonants such as `gitcez`/`etcem`, where the
  correct form has a softened `d`), `ne_kısalt` (`napcam` → `ne yapacağım…`), `yazım_yanlışı` (~35 common
  Turkish misspellings: `yanlız`, `herkez`, `yalnış`, `şöför`, `orjinal`, `süpriz`, `makina`, `hastahane`,
  `yada`, …) and `özel_ad_kesme` (`Ankaraya` for `Ankara'ya`).
- **Casing bug fixed**: `str.swapcase` turned `İ` into two code points and `I` into `i`; the generator now
  uses Turkish-aware `swapcase_tr` / `upper_tr`.
- **More everyday sentences**: 1,470 → 2,561 generated (2,526 used after de-duplication against Common Voice).
- **Train** is now 42,075 pairs (31,996 Common Voice, 8,804 everyday, 1,275 two-sentence chunks);
  **validation** was regenerated and has 1,440 pairs (640 Common Voice, 800 everyday).
- **Test split frozen from v2**: the 1,128 test pairs are byte-identical to v2
  (SHA-256 `43738c617c498e21753f71f9af928ac518c374e938742901a443e81b827e30a5`), so models from v2 and v3
  can be compared directly. Test targets are excluded from train and validation.
- The 81 targets of a hand-written challenge set (in the GitHub repo, `evaluation/challenge.jsonl`) are also
  excluded from train and validation. That set was written alongside the new noise rules, so it measures
  whether targeted failures got fixed, not general accuracy.

## What was new in v2

(Kept for history.)

v1 (tag `v1`) had 33,280 pairs from Common Voice only. Those sentences are literary and mostly third
person, `gideceğim` appeared 8 times in 32,000 training pairs, so a model trained on them never learned
colloquial first-person forms. v2 adds:

- **Everyday sentences** (CC0-1.0, written for this project): template sentences from a 50-verb table and
  a small conjugator (future, present continuous, negative, question suffix; vowel harmony and the
  `git`/`et`/`ye`/`de` special cases) plus ~250 hand-written short sentences, ~1,470 in total.
- **Suffix-based colloquial noise**, applied to any verb rather than a fixed word list
  (`-eceğim → -icem/-cem`, `-yorum → -yom`, `gideceğim → gitcem`, `burada → burda`, `bir şey → bişey`, …).
  The `gündelik` operation count in train went from 1,001 to 8,178.
- **Two-sentence chunks** in train: two independent pairs of the same difficulty joined with a space,
  at most 170 bytes.
- Larger validation and test splits (1,128 pairs each) with an everyday subset.

The 160 Common Voice test target sentences are the same as in v1, but the noise generator changed, so
most corrupted inputs differ.

## Splits

| Split | Pairs | Distinct targets | Common Voice | Everyday | Two-sentence | Targeted |
|---|---:|---:|---:|---:|---:|---:|
| **train (v4)** | 70,831 | 20,756 | 31,932 | 8,792 | 1,272 | 13,906 + 15,038 (v3.5) |
| **validation (v4)** | 3,442 | 1,261 | 640 | 800 | - | 1,210 + 795 (v3.5) |
| test (frozen from v2) | 1,128 | 282 | 640 | 488 | - |, |

(v3.2, tag `v3.2`: train 55,902 pairs from 13,387 distinct targets; validation 2,650 pairs from 639 targets.)

Splitting happens on canonical target form (NFC + Turkish lowercase + alphanumeric key) **before**
noise is applied, so no variant of the same sentence crosses splits. Of the 2,524 everyday sentences used, about 1/12 go to validation and the rest to train; of the 3,485 targeted sentences, 8% go to validation; the v3.5 validation pairs are capped at 795 with a fixed seed (3500). The test split
is not regenerated but carried over from v2. Seed 42 (targeted source: 3200).

## Schema

```json
{
  "target": "Yarın sabah ben evde kalıyorum.",
  "source": "Megazeka gündelik şablon / CC0-1.0",
  "input": "Yarın sabah benevde kalıyom.",
  "difficulty": "orta",
  "operations": [
    {"operation": "gündelik",  "before": "Yarın sabah ben evde kalıyorum.",
                               "after":  "Yarın sabah ben evde kalıyom."},
    {"operation": "boşluk_sil", "before": "Yarın sabah ben evde kalıyom.",
                               "after":  "Yarın sabah benevde kalıyom."}
  ],
  "group_id": "5864952e584f92f7"
}
```

- `target`: correct sentence
- `input`: corrupted sentence, identical to `target` when `difficulty` is `temiz`
- `difficulty`: `temiz` (clean) / `kolay` (easy) / `orta` (medium) / `zor` (hard), targeting
  0 / 1 / 2 / 4 successfully applied operations
- `source`: `Common Voice / CC0-1.0`, `Megazeka gündelik şablon / CC0-1.0` (everyday),
  `Megazeka hedefli şablon / CC0-1.0` (targeted, since v3.2), `Megazeka v3.5 hedefli / CC0-1.0`
  (hand-written targeted pairs, new in v4) or `Birleşik iki cümle` (two-sentence chunk)
- `kind`, `focus`: only on targeted rows: `yazım` / `özel_ad` / `koruma` (and, on v3.5 rows, `açık_yazım`,
  `bağlaç`, `noktalama`), and the word the sentence was built around
- `family`: only on v3.5 rows: the group of sentences written for one word
- `group_id`: canonical target hash; shared by the four variants of one sentence
- `group_id_second`: only on two-sentence chunks: the `group_id` of the second sentence
- `operations`: ordered list of applied corruptions with before/after text; on two-sentence chunks the
  operations of both halves are listed, each with the text of its own half

Difficulty counts in train: clean 19,591, easy 13,662, medium 23,886 (includes the 10,240 changed v3.5 pairs, which are all labelled medium) and hard 13,692. About **28% of pairs are clean**, so a model
trained on this data learns to leave correct text alone. For easy and medium everyday pairs the first
operation is always `gündelik`. Rare multi-operation corruptions can cancel each other out, when
measuring overcorrection, count every example where `input == target` (19,654 in train, 1,002 in
validation, 282 in test) rather than trusting the `temiz` label.

## Noise operations

Counts over the training split (v4 / v3.5), including two-sentence chunks (a pair may apply several):

| Operation | Count | What it does |
|---|---:|---|
| `v35_explicit` | 10,240 | Hand-written misspelling recorded as one before/after step, since v4 (v3.5 rows) |
| `türkçe_karakter` | 18,734 | Diacritic loss: ı→i, ş→s, ğ→g, ç→c, ö→o, ü→u |
| `küçük_harf` | 10,236 | Capitalization errors (Turkish-aware as of v3) |
| `gündelik` | 10,157 | Colloquial spellings (gidicem, yapcaz, bilmiyom, burda, bişey, …) |
| `harf_sil` | 5,816 | Dropped letter |
| `klavye` | 5,759 | Turkish Q-keyboard neighbour key |
| `fazla_boşluk` | 5,651 | Extra whitespace |
| `noktalama_ekle` | 5,614 | Spurious punctuation |
| `boşluk_sil` | 5,590 | Merged words |
| `boşluk_ekle` | 5,563 | Split word |
| `harf_tekrar` | 5,545 | Repeated letter |
| `noktalama_sil` | 5,283 | Missing punctuation |
| `harf_yer_değiştir` | 4,609 | Transposed adjacent letters |
| `özel_ad_bozma` | 2,979 | I/İ confusion and lost capitals in proper names (ısparta, igdir), since v3.2 |
| `yazım_yanlışı_v32` | 2,114 | More common misspellings (traş, kirbit, sarmısak, espiri, …), since v3.2 |
| `yazım_yanlışı` | 1,261 | Common misspellings (yanlız, herkez, yalnış, şöför, makina, …), since v3 |
| `özel_ad_kesme` | 906 | Dropped apostrophe before a suffix on a proper noun (Ankaraya), since v3 |
| `ne_kısalt` | 498 | `ne yap-` contractions (napcam, napıyosun), since v3 |
| `sert_ünsüz` | 490 | Hardened consonant (gitcez, etcem), since v3 |
| `soru_eki` | 488 | Question suffix wrongly attached |
| `kesme` | 218 | Missing apostrophe before a suffix |
| `de_da` | 196 | `de`/`da` clitic merged with the word |
| `ki` | 159 | `ki` clitic merged with the word |

## Source and filtering

- **Common Voice Turkish Sentence Collector** at pinned commit
  `b12cde653757295103c5948c1cd601b166e1b905` (1,557,129 bytes, 47,781 lines,
  SHA-256 `28e2d095…4058ece`). No audio or dev corpus was downloaded. Sentences were kept if they are
  3–24 words, 18–160 UTF-8 bytes, start with a capital letter and end with punctuation, then deduplicated
  on a canonical key.
- **Everyday sentences**, generated by `training/everyday.py` in the GitHub repository and released here
  under CC0-1.0 (2,560 generated, 2,524 used).
- **Targeted sentences**, generated by `training/targeted.py` in the GitHub repository and released here
  under CC0-1.0 (3,488 generated in v3.2, 3,485 used).

- **v3.5 hand-written pairs**, from `training/v35.py` and `training/v35_extra.py` in the GitHub repository and
  released here under CC0-1.0 (15,833 pairs in train and validation).

Per-file SHA-256 checksums for the generated splits are in `metadata.json`.

## Limitations

- **Synthetic.** These are programmatically corrupted sentences, not errors real people made. A
  model that scores well here may do noticeably worse on genuine user text.
- Operation frequencies reflect the generator's weights, not measured Turkish error frequencies.
- The everyday sentences come from 50 verbs and a limited set of complements; they do not represent real
  chat language in full, and the test everyday subset is from the same template family as train.
- The v3.5 pairs are hand-written around a closed catalog (117 extra words plus earlier lists); a model trained on them memorises the taught words and does not by itself generalise to other misspellings (measured on the v4 challenge sets). They were not audited sentence by sentence.
- The targeted sentences are templates around a fixed word list (about 75 misspelling targets, I/İ names and
  protected words). They make up a quarter of train, so those words are over-represented compared with
  natural text. The targeted sentences were not audited sentence by sentence.
- Common Voice sentences may themselves contain overlooked mistakes. The v3.1 audit fixed 136 of them, but
  it is not exhaustive: Haiku, Sonnet and rule-based scans each found errors the others missed, and how
  many remain is unknown. The frozen test split was not cleaned.
- Sentence-length only (plus two-sentence chunks). No long documents, lists, code, or mixed-language text.
- Split separation is on canonical sentence form. Semantically similar sentences, including template
  sentences that share a verb or complement, may still be split across sets, and overlap with any given
  model's pretraining corpus is unknown.

## Versions

| Version | Revision | Pairs (train / val / test) | Sources |
|---|---|---|---|
| **v4** (internal data v3.5) | `main` | 70,831 / 3,442 / 1,128 (test frozen from v2) | v3.2 data plus approved audit (30 fixed, 109 removed in train) and 15,038 new targeted pairs; v3.5 was not released separately |
| v3.2 | tag `v3.2` | 55,902 / 2,650 / 1,128 (test frozen from v2) | v3.1 plus a targeted source (misspellings, I/İ names, correct-word protection), 2 new noise operations |
| v3.1 | tag `v3.1` | 42,017 / 1,440 / 1,128 (test frozen from v2) | v3 with audited targets (136 fixed, 12 removed), 3 noise rules removed |
| v3 | tag `v3` | 42,075 / 1,440 / 1,128 (test frozen from v2) | Common Voice + more everyday + two-sentence chunks, 4 new noise operations |
| v2 | tag `v2` | 38,057 / 1,128 / 1,128 | Common Voice + everyday + two-sentence chunks |
| v1 | tag `v1` | 32,000 / 640 / 640 | Common Voice only |

The default is v4. Load a specific version with `load_dataset("pandakingpunc/megazeka-tr-spellfix-pairs", revision="v3.2")` (or `"v3.1"`, `"v3"`, `"v2"`, `"v1"`).

## Licensing

Common Voice source sentences are **CC0-1.0**
([Common Voice licensing](https://github.com/common-voice/common-voice#licensing-and-content-source));
the everyday, targeted and v3.5 sentences were written for this project and are also released under CC0-1.0, as are all
derived pairs. No Common Voice program code (MPL-2.0) is included here. The generation code is MIT, in
the GitHub repository.
