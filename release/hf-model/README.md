---
language:
- tr
license: apache-2.0
base_model: google/byt5-base
library_name: peft
pipeline_tag: text-generation
tags:
- turkish
- spelling-correction
- grammatical-error-correction
- byt5
- lora
- text-correction
datasets:
- pandakingpunc/megazeka-tr-spellfix-pairs
metrics:
- cer
- wer
model-index:
- name: megazeka-byt5-tr-spellfix
  results:
  - task:
      type: text-generation
      name: Turkish Spelling Correction
    dataset:
      name: megazeka-tr-spellfix-pairs (test)
      type: pandakingpunc/megazeka-tr-spellfix-pairs
      split: test
    metrics:
    - type: cer
      value: 0.0118
      name: CER (protected output)
    - type: wer
      value: 0.0567
      name: WER (protected output)
    - type: exact_match
      value: 0.7934
      name: Exact match
---

# Megazeka · Turkish Spelling Correction (ByT5-base + LoRA)

A LoRA adapter for `google/byt5-base` (v4) that corrects Turkish spelling, typos, punctuation,
capitalization, spacing, common keyboard errors and chat-style colloquial spellings
(`gidicem` → `gideceğim`, `bilmiyom` → `bilmiyorum`, `burda` → `burada`). Trained locally on a single
RTX 4060. **v3.2 and earlier adapters use `google/byt5-small` as the base and must be loaded with that base
(see *Usage*); v4 needs `google/byt5-base`.**

**This is a small educational experiment, not a production-grade spell checker.** Read the
limitations before using it for anything that matters.

- Code, offline desktop app and full technical report: **[github.com/pandakingpunc/megazeka](https://github.com/pandakingpunc/megazeka)**
- Training data: **[pandakingpunc/megazeka-tr-spellfix-pairs](https://huggingface.co/datasets/pandakingpunc/megazeka-tr-spellfix-pairs)**
- Local browser demo (Gradio): `space/` in the GitHub repo

## What's new in v4

v4 changes two things: the **base model** and the **training data**, and it ships with an **optional dictionary layer**
that lives in the GitHub code (not in this model repository).

- **Base model:** `google/byt5-base` (581,653,248 parameters, Apache-2.0, revision
  `92d8c008d55cf7c254915bac165171dfe6c20c44`) instead of `google/byt5-small`. LoRA rank 16 as before:
  10,764,288 trainable of 592,417,536 parameters (1.82%).
- **Data (internal version v3.5, first released with v4):** the v3.2 data plus an approved target audit
  (30 corrected and 109 removed in train) and 15,038 new targeted training pairs from an extra catalog of
  hand-written misspellings (`training/v35_extra.py`). Train is 70,831 pairs; validation 3,442; the frozen test
  (1,128 pairs) is unchanged. A byt5-small model trained on this same data (v3.5) was **never released**; it was
  only used for comparison.
- **Training:** `configs/v4.json`, micro-batch 4 × accumulation 4, 7,000 steps, lr 5e-4, bfloat16, one RTX 4060
  (8 GB), 3 h 4 min. Best checkpoint: step 6,750, validation loss 0.0218.
- **Optional dictionary layer (GitHub code, off by default, `--dictionary`):** for words in the model output
  that the `zeyrek` morphological analyser (`zeyrek==0.1.3`) does not recognise, single-edit candidates that
  the analyser accepts are generated and ranked by the model's own forced-decoding log-probability
  (threshold 11 nats). It is **not** part of the weights in this repository; it is `src/megazeka/dictionary.py`
  in the GitHub repo.
- **Two new hand-written challenge sets** are released with v4: `challenge4` (90 pairs: taught words, words
  outside the taught list, protected correct sentences) and `challenge5` (70 pairs, measured after tuning
  without ever being looked at during tuning).

Results (lexicon guard off; the "+ dictionary" column uses the GitHub code with `--dictionary`):

| Set | v3.2 | **v4** | v4 + dictionary |
|---|---:|---:|---:|
| Frozen test exact match (1,128) | 78.1% | **79.3%** | 81.6% |
| Frozen test edit F1 | 0.909 | 0.907 | 0.913 |
| Clean sentences damaged (of 282) | 3 | 6 | 8 |
| challenge (81) | 72 | 77 | 77 |
| challenge2 (66) | 60 | 63 | 63 |
| challenge3 (84) | 59 | 73 | 74 |
| challenge4 (90) | 30 | 62 | 75 |
| challenge4 out-of-list words (25) | 1 | 4 | 16 |
| challenge5 (70) | not measured | 44 | 59 |
| challenge5 unseen words (26) | not measured | 7 | 20 |
| challenge5 protection (30) | not measured | 24 | 25 |

Paired comparisons (exact McNemar test): v3.2 → v4 on the frozen test p=0.18 (40 pairs only v3.2 gets right,
54 only v4); v4 → v4 + dictionary on the frozen test p=0.0001 (33 fixed, 8 broken); v3.2 → v4 + dictionary
p=0.0004; challenge5, v4 → v4 + dictionary p=6e-5 (15 fixed, 0 broken).

**Honest reading.** Growing the base model improved general accuracy a little (78.1% → 79.3%), which is at the
noise level on the frozen test, and it did **not** change how the model handles words it was never taught: out of
list words stay at 4 of 25 (challenge4) and unseen words at 7 of 26 (challenge5). The dictionary layer is what
closed that gap, at the price of more damaged clean sentences (6 → 8) and about 20% more inference time. v4
inference is also about 1.6× slower than the byt5-small v3.5 model, and the base weights are 2.33 GB.
challenge3 was seen during the development of earlier versions, so it is not independent; the dictionary
threshold was tuned on challenge4, so that column is optimistic; challenge5 is the independent measurement.

Known limits of v4 and the dictionary layer: candidate ranking is weak (`asensörü` → `sensörü`,
`tafsiyesine` → `tasfiyesine`); `zeyrek` does not recognise some valid forms (`ürkeği`, `korkağı`) and the layer
damages them; errors two edits away are missed (`dikdörgen`, `profitörol`, `sesizce`); the model can corrupt
brand names (`Netflix` → `Netfliz`, `Whatsapp` → `Whatsap`).

## What was new in v3.2

(Kept for history; v3.2 used `google/byt5-small`.)

v3.2 is a **targeted release**. v3.1 had three known weaknesses: common misspellings it left alone
(`şöför`, `labaratuvar`), proper names starting with I/İ (`isparta` → `İsparta`), and correct words turned
into invented ones (`sıcak → sıyacak`, `yabani → yabanı`). The rules for the first two existed, but the
training data barely covered them: `laboratuvar` and `kılavuz` appeared in one target sentence each,
`mütevazı` in none, and I-initial proper names in about 130 words in total.

- **Targeted data source** (`training/targeted.py`): 3,485 template sentences in three kinds, giving
  13,906 training and 1,210 validation pairs:
  - `yazım` (1,149): each misspelling target in at least 12 different sentences that fit its meaning;
    about 38 misspellings were added to the dictionary (`traş`, `kirbit`, `sarmısak`, `şarz`, …).
  - `özel_ad` (1,160): I/İ-initial place and person names (Isparta, Iğdır, Işık, İzmir, …) sentence-initial,
    medial and final, bare and with apostrophe suffixes.
  - `koruma` (1,176): correct words the model used to damage (`sıcak`, `yabani`, `denecek`, …); 40% of these
    pairs are left unchanged.
- **The old data stream is kept.** The targeted source uses its own seed and generator, so the Common Voice
  and everyday pairs are the same as in v3.1 (a test in the repo checks this). The test split is still frozen.
- **Training:** same recipe (`configs/medium.json`), 6,500 steps instead of 5,000 because the data grew.
- **Measurement:** `evaluation/compare.py` compares two versions on the same examples (exact McNemar test,
  bootstrap confidence interval resampled by target sentence). A second hand-written challenge set
  (`evaluation/challenge2.jsonl`, 66 pairs) was written **before** training and was never shown to the
  coding agents that generated the data; its targets are excluded from training.
- **Optional lexicon guard** in the repo's inference code (`--lexicon-guard`, off by default): reverts a
  known word that was replaced by an unknown one. It helped v3.1 (second challenge set 46 → 49) but changed
  no output of v3.2, so it stays off.

v3.1 → v3.2 (guard on):

| | v3.1 | **v3.2** | Paired comparison |
|---|---:|---:|---|
| Frozen test, exact match (1,128) | 78.0% | **78.1%** | 30 only v3.1, 31 only v3.2; McNemar p=1.0; 95% CI −1.6 to +1.9 points |
| Frozen test, CER ↓ | 0.0129 | **0.0123** | |
| Frozen test, WER ↓ | 0.0609 | **0.0587** | |
| Frozen test, overcorrection ↓ | 2.1% (6) | **1.1% (3)** | |
| Common Voice subset, exact match | 70.3% | **71.4%** | |
| Everyday subset, exact match | **88.1%** | 86.9% | |
| Challenge set (81) | 67 | **72** | 3 only v3.1, 8 only v3.2; p=0.23 |
| Second challenge set (66) | 46 | **60** | 1 only v3.1, 15 only v3.2; p=0.0005 |

Second challenge set by category, v3.1 → v3.2: I/İ names 5 → 11 of 12, misspellings 7 → 11 of 14,
correct-word protection 13 → 16 of 16, punctuation 5 → 5 of 6, chat 8 → 9 of 10, correct sentences 8 → 8 of 8.

**Honest reading.** On the frozen test v3.2 is on par with v3.1; that test barely contains the targeted
error types, so no gain was expected there. The gain is on the hand-written sets, and only the second
set's difference is statistically clear. Both sets consist of the error types v3.2 targeted, so neither
score is a general accuracy figure. Of the 3 remaining changes to already-correct test inputs, 2 are
correct fixes of non-standard test targets (`nerdeyse`, `şurda burda`) and 1 is a real error
(`asabidir → asabıdır`).

Still failing in v3.2: `klavuz` → `Kalavuz`, `traş` → `taraş`, `sarmısak` → `sarmışak`, `kirbit` unchanged,
`ısık` → `Isık` (should be `Işık`), `naber nasılsın` → `Ne yaber nasılsın?`, `Ayşenin` keeps its missing
apostrophe, a few stray commas (`Ne olur, gel.`), and **one new regression**: the correctly written
`Nolan'ın` becomes `Ne olan'ın`.

The data-generation and measurement code was written by OpenAI Codex (GPT) coding agents; design, review,
the second challenge set and the evaluation were done with Claude.

## What was new in v3.1

v3.1 was a **data-cleaning release**. The recipe and step count are identical to v3 (`configs/medium.json`,
5,000 steps); only the training data changed:

- **Target-sentence audit.** All 10,560 distinct training/validation target sentences were audited in two
  rounds: 11 Claude Haiku subagents, then 11 Claude Sonnet subagents. Rule-based scans were added on top, and
  Claude Opus verified every flag by hand. This produced 223 records: 136 targets fixed and 12 removed in
  training. The fixes cover:
  - OCR errors in Common Voice sentences (`memurlan → memurları`, `kaşlan → kaşları`, `Haşan → Hasan`),
  - colloquial forms inside targets (`burda`, `nerde`, `içerde`), which contradicted the noise rules,
  - TDK spellings (`hiç bir → hiçbir`, `davavekili → dava vekili`) and titles (`Raif efendi → Raif Efendi`),
  - nonsensical template sentences such as `Sen seni izliyorsun` or `Yakında seni unutur musun?`.
  The audit report and the full correction list are in `data/audit/` on GitHub.
- **Removed noise rules** that marked valid Turkish words as errors: `ağabey → abi`, `bilmiyorum → bilmem`,
  `tabii → tabi` (`abi`, `bilmem` and `tabi olmak` are correct).
- The template generator no longer pairs a subject with an object of the same person. The template stream
  was otherwise kept identical to v3 (2,472 of 2,561 sentences unchanged), so the measured difference comes
  from the cleaning. A first attempt that changed the stream (v3.1a) regressed to 76.9% because, among other
  things, `yiyecek` targets dropped from 109 to 74.

On the frozen test set (guard on), v3 → v3.1:

| Metric | v3 | **v3.1** |
|---|---:|---:|
| CER ↓ | **0.0124** | 0.0129 |
| WER ↓ | 0.0612 | **0.0609** |
| Exact match ↑ | 77.5% | **78.0%** |
| Edit F1 ↑ | **0.907** | 0.905 |
| Overcorrection ↓ | **1.8%** (5) | 2.1% (6) |
| Common Voice subset, exact match | 70.2% | **70.3%** |
| Everyday subset, exact match | 87.1% | **88.1%** |
| Challenge set (81) | 66 | **67** |

**Honest reading: v3.1 is on par with v3, not clearly better.** Per example, 41 test pairs are fixed only by
v3.1 and 35 only by v3 (net +6, within single-run noise). The overcorrection rise needs a closer look:
- 3 of v3.1's 6 changes to "already correct" test inputs are genuine fixes, because those frozen-test targets are
  themselves non-standard (`nerdeyse → neredeyse`, `şurda burda → burada`, `bitpazarı → bit pazarı`).
- Genuinely harmful overcorrections are 3 for both versions:
  - v3: `asabidir`, `iltifatkarsınız`, `bitpazarı → bir pazarı`;
  - v3.1: `denecek → deneyecek`, `yabani → yabanı`, `mevkiini → mevkini`.
- The frozen test was generated with the old noise rules and uncleaned targets, so it cannot fully show the
  benefit of the cleaning.

In the challenge set, v3.1 fixes v3's `Türkiyede hava çok sıcak. → sıyacak` hallucination, `mütevazi` and
`yalnış anladın beni`. It newly misses `bilmiyom valla` (→ `Bilmiyorum vallah.`), `Ayşenin` (apostrophe not
added) and `Ilgaz` (→ `İlgaz`).

## What's new in v3

v3 keeps the v2 recipe (`configs/medium.json`, lr 5e-4, LoRA r=16) and changes the data generator and the
step count (5,000 instead of 4,000):

- **Four new noise operations**: `sert_ünsüz` (hardened consonants: `gitcez`, `etcem` → softened `d`),
  `ne_kısalt` (`napcam` → `ne yapacağım…`), `yazım_yanlışı` (~35 common Turkish misspellings: `yanlız`,
  `herkez`, `yalnış`, `şöför`, `orjinal`, `süpriz`, `makina`, `hastahane`, `yada`, …) and `özel_ad_kesme`
  (`Ankaraya` → `Ankara'ya`).
- **Casing bug fixed**: `str.swapcase` turned `İ` into two code points and `I` into `i`; the generator now uses
  Turkish-aware `swapcase_tr` / `upper_tr`.
- **More everyday sentences**: 1,470 → 2,561 unique generated sentences. Training set: 42,075 pairs
  (31,996 Common Voice, 8,804 everyday, 1,275 two-sentence chunks); validation 1,440 pairs.
- **Test split frozen from v2**: the 1,128 test pairs are byte-identical to v2 (SHA-256 `43738c61…`), so v2 and
  v3 are directly comparable.
- Training: 5,000 steps in one run from scratch (~52 minutes on an RTX 4060); best checkpoint = step 5,000.

On the frozen test set (guard on), v2 → v3:

| Metric | v2 | **v3** |
|---|---:|---:|
| CER ↓ | 0.0137 | **0.0124** |
| WER ↓ | 0.0678 | **0.0612** |
| Exact match ↑ | 76.2% | **77.5%** |
| Edit F1 ↑ | 0.898 | **0.907** |
| Overcorrection ↓ | 1.8% | **1.8%** |
| Common Voice subset, exact match | 70.3% | **70.2%** |
| Everyday subset, exact match | 84.0% | **87.1%** |
| 23 hand-picked examples, exact match | 73.9% | **91.3%** |

The Common Voice subset did not improve; the gain is in everyday text and the small hand-picked set (23
examples is a sanity check, not a success rate).

### Challenge set

`evaluation/challenge.jsonl` in the GitHub repo: 81 hand-written pairs in 7 categories (17 are already
correct sentences that must stay unchanged).

| Category | Pairs | v2 | **v3** |
|---|---:|---:|---:|
| yumuşama (`gitcez`) | 10 | 7 (70.0%) | **9 (90.0%)** |
| ne_yap (`napcam`) | 12 | 1 (8.3%) | **9 (75.0%)** |
| sohbet (chat style) | 8 | 7 (87.5%) | **7 (87.5%)** |
| yazım_yanlışı (misspellings) | 17 | 2 (11.8%) | **12 (70.6%)** |
| kesme_işareti (apostrophes) | 8 | 0 (0.0%) | **7 (87.5%)** |
| ı_i_isimleri (I/İ in names) | 9 | 0 (0.0%) | **5 (55.6%)** |
| doğru_cümle (must not change) | 17 | 16 (94.1%) | **17 (100.0%)** |
| **Total exact match** | 81 | 33 (40.7%) | **66 (81.5%)** |

Overcorrection on the 17 correct sentences: 5.9% → 0%.

**Caveat:** the challenge set was written alongside the v3 noise rules, aimed at known v2 failures (its
targets are excluded from training). It measures whether those targeted failures got fixed, **not** general
real-world accuracy. Do not read 81.5% as a success rate on arbitrary Turkish text.

Still failing in v3: I/İ in names (`isparta` → `İsparta`, `Iğdır` → `İğdır`, `ısık` → `Isık`), `şöför`,
`labaratuvar` and `mütevazi` unchanged, `klavuz` → `Kalavuz`, `naber` → `Ne yapar`, and one new regression:
`Türkiyede hava çok sıcak.` was handled correctly by v2 but v3 outputs `Türkiyede hava çok sıyacak.`, a
hallucinated, letter-similar word that passes the word guard.

## What's new in v2

v2 (tag `v2`) addressed the first release (v1), which did not correct colloquial forms at all, `gidicem`, `buluşcaz`, `gidicez` came
out unchanged, because its training data was almost entirely literary third-person sentences
(`gideceğim` appeared 8 times in 32,000 pairs). v2 changes the data, not the architecture:

- **4,904 everyday first/second-person pairs** generated from project-authored templates (50 verbs and a
  small conjugator) plus ~250 hand-written short sentences, all CC0-1.0.
- **Rule-based colloquial noise on suffixes**, so it applies to any verb: `-eceğim → -icem/-cem`,
  `-acağız → -ıcaz/-caz`, `-yorum → -yom`, `-yor → -yo`, consonant hardening (`gideceğim → gitcem`),
  plus word rules (`burada → burda`, `bir şey → bişey`, `herkes → herkez`, `yalnız → yanlız`, …).
  Colloquial operations in the training split went from 1,001 to 8,178.
- **1,153 two-sentence training chunks**, so the model sees more than one sentence per input like it does
  when a user pastes a paragraph.
- **Longer training**: 4,000 steps instead of 1,800.
- **Two-layer output guard** in the reference inference code (see *Usage*): a looser chunk filter plus a
  new word-level lock that blocks synonym swaps and invented words.

On the same 160 held-out Common Voice target sentences (noised differently in each version, so the pairs
are not identical), exact match went from 60.6% (v1) to 70.3% (v2). The v1 adapter is still available
with `revision="v1"`.

## Why byte-level

Turkish spelling errors are overwhelmingly *diacritic* errors: `ı/i`, `İ/I`, `ş/s`, `ğ/g`, `ç/c`,
`ö/o`, `ü/u`. Subword tokenizers fragment unpredictably when those characters are corrupted, so a
misspelled word and its correction can land in completely unrelated token space. ByT5 operates on
raw UTF-8 bytes and has no vocabulary to fall out of, which makes it a natural fit for this task.
The cost is sequence length, a Turkish character is often two bytes.

## Results

The v4 results are in *What's new in v4* above (frozen test 79.3% exact match, CER 0.0118, WER 0.0567, edit F1 0.907,
6 of 282 clean inputs changed). The tables below are the earlier releases (`google/byt5-small`) on the same frozen test.

Held-out test set: 1,128 pairs derived from 282 target sentences that appear in no other split,
640 pairs from 160 Common Voice sentences and 488 pairs from 122 everyday sentences. The set is frozen
byte-identical since v2. *Copy input* is the trivial do-nothing baseline. *Base ByT5* is untrained
`google/byt5-small`. *v2*, *v3* and *v3.1* are the previous releases (`revision="v2"` / `"v3"` / `"v3.1"`) on the same
pairs.

| Metric | Copy input | Base ByT5 | v2 | v3 | v3.1 | **v3.2** | Unfiltered (v3.2) |
|---|---:|---:|---:|---:|---:|---:|---:|
| CER ↓ | 0.0963 | 0.0963 | 0.0137 | 0.0124 | 0.0129 | **0.0123** | 0.0113 |
| WER ↓ | 0.3576 | 0.3579 | 0.0678 | 0.0612 | 0.0609 | **0.0587** | 0.0570 |
| Exact match ↑ | 25.0% | 24.9% | 76.2% | 77.5% | 78.0% | **78.1%** | 78.5% |
| Edit F1 ↑ | 0.000 | 0.000 | 0.898 | 0.907 | 0.905 | **0.909** | 0.913 |
| Overcorrection ↓ | 0.0% | 0.4% (raw 100%) | 1.8% | 1.8% | 2.1% | **1.1%** | 1.1% |

By subset (guard on, v3.2, `google/byt5-small`):

| Subset | Pairs | CER ↓ | WER ↓ | Exact match ↑ | Copy-input exact match | Overcorrection ↓ |
|---|---:|---:|---:|---:|---:|---:|
| Common Voice | 640 | 0.0155 | 0.0716 | 71.4% | 25.0% | 1.9% |
| Everyday | 488 | 0.0067 | 0.0366 | 86.9% | 25.0% | 0.0% |

Untrained ByT5 is unusable here, its raw CER is 4.04 and it rewrites every input, so the output guard
falls back to the input almost everywhere. That is why its protected column is close to copy-input.

*Unfiltered* is the raw generation with the output guard (see below) disabled. The guard costs 0.4
points of exact match and buys protection against word substitutions and large rewrites; both are
reported because which one you want depends on your use case.

*Overcorrection* is measured on the 282 test examples where input already equals target (3 of them
were changed; 2 of those are correct fixes of non-standard test targets, see *What's new in v3.2*).

Edit precision/recall/F1 compares sets of `(original position, operation, character)` Levenshtein
edits; with the guard on, precision is 0.930 and recall 0.888. **This is a project-defined metric and
is not comparable to standard GEC M2/ERRANT F0.5.**

## Usage

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

tok = AutoTokenizer.from_pretrained("google/byt5-base")
base = AutoModelForSeq2SeqLM.from_pretrained("google/byt5-base")
model = PeftModel.from_pretrained(base, "pandakingpunc/megazeka-byt5-tr-spellfix").eval()

text = "bugün okula gidicem ama hava cok kötü galiba"
ids = tok(text, return_tensors="pt")
out = model.generate(**ids, max_new_tokens=224, num_beams=1, do_sample=False)
print(tok.decode(out[0], skip_special_tokens=True))
# Bugün okula gideceğim ama hava çok kötü galiba.
```

The default (`main`) is **v4 and needs `google/byt5-base`** (about 2.3 GB). Loading it on `google/byt5-small`
fails with shape mismatches. **v3.2 and every earlier release need `google/byt5-small`** as the base:

```python
base = AutoModelForSeq2SeqLM.from_pretrained("google/byt5-small")
model = PeftModel.from_pretrained(base, "pandakingpunc/megazeka-byt5-tr-spellfix", revision="v3.2")  # or "v3.1", "v3", "v2", "v1"
```

The optional dictionary layer is **not** in this repository. It lives in the GitHub code
(`src/megazeka/dictionary.py`, `pip install zeyrek==0.1.3`) and is switched on with `--dictionary` in the
evaluation scripts or `CorrectionEngine.correct(..., dictionary=True)`.

Things the repo's own inference code (`src/megazeka/inference.py`) does that the snippet above does not:

1. **Normalization.** NFC Unicode and line-ending normalization only.
2. **Chunking.** Input is split into pieces of at most **176 UTF-8 bytes** on whitespace
   boundaries; line breaks and blank paragraphs are preserved. No context crosses chunk borders.
3. **Chunk filter.** A chunk's generation is discarded and the original kept if the character edit
   count exceeds the input length (ratio > 1.0), the output is shorter than 65% of the input, the output
   is empty, or no EOS token was produced. (v1 used a 45% edit-ratio threshold, which rejected most
   correct heavy fixes: edit F1 0.71 → 0.89 when relaxed, with overcorrection unchanged.)
4. **Word lock.** Words are aligned ignoring case, Turkish diacritics and punctuation. If a word group
   was replaced by one with no letter similarity (normalized Levenshtein distance > 0.6), a word was
   deleted, or a new word appeared with no counterpart, only that group is restored to the original.
   So `gidicem → gideceğim` passes, `okula → eğitim kurumuna` does not.
5. **Lexicon guard (optional, off by default, since v3.2).** With `lexicon_guard=True`, a one-to-one word
   replacement is reverted when the source word is in a word list built from the clean training sentences
   and the output word is not.
6. **Dictionary layer (optional, off by default, new in v4, GitHub code only).** See *What's new in v4*.

The guard does **not** guarantee meaning preservation, and it also blocks some correct fixes.
Generation is deterministic greedy decoding (`num_beams=1`, `do_sample=False`).

## What it actually does (and doesn't)

Real outputs of the **v2** adapter on hand-picked sentences outside the training data (raw generation and
guarded output were identical for all of these). v3 fixes several of the failures marked ✗, e.g. 21 of the
23 hand-picked examples (91.3%) are now exactly right in v3, but the table below was not regenerated for v3,
so treat it as v2 history; see the challenge-set section above for v3's remaining failures.

| Input | Output |
|---|---|
| `bugün okula gidicem ama hava cok kötü galiba` | `Bugün okula gideceğim ama hava çok kötü galiba.` |
| `yarin arkadaşlarla buluşcaz sonrada sinemaya gidicez` | `Yarın arkadaşlarla buluşacağız, sonra da sinemaya gideceğiz.` |
| `Yapıcam dedim ama yapmıcam.` | `Yapacağım dedim ama yapmayacağım.` |
| `İstanbul'a gidicem ve orda kalıcam.` | `İstanbul'a gideceğim ve orada kalacağım.` |
| `herkez buraya gelsin` | `Herkes buraya gelsin.` |
| `Beni duyuyormusun?` | `Beni duyuyor musun?` |
| `Cok tesekkur ederim.` | `Çok teşekkür ederim.` |
| `Ben de seninle geleceğim, sen de gelir misin?` | unchanged |
| `bugün sinemaya gitcez sonra yemek yiycez` | `Bugün sinemaya giteceğiz sonra yemek yiyeceğiz.` ✗ (should be `gideceğiz`) |
| `bilmiyom ki napcam` | `Bilmiyorum ki napacağım.` ✗ (should be `ne yapacağım`) |
| `napıyosun bugun` | `Napıyorsun bugün?` ✗ (should be `Ne yapıyorsun`) |
| `yanlız kaldım burda` | `Yanlız kaldım burada.` ✗ (`yanlız` not fixed) |
| `Ankaraya yarin gidicem.` | `Ankaraya yarın gideceğim.` ✗ (missing apostrophe: `Ankara'ya`) |
| `Işık, İstanbul’a yarın gelecek.` | `İşık, İstanbul’a yarın gelecek.` ✗ (proper noun damaged) |

With v2, 17 of these 23 hand-picked examples came out exactly right (73.9%) and 1 of the 9 already-correct ones
was changed (the `Işık` proper noun). With v3: 21 of 23 (91.3%); with v3.1 and v3.2: 20 of 23 (87.0%); 0 of 9
changed in all three. This is a sanity check, not a success rate.

## Training

| | |
|---|---|
| Base | `google/byt5-base`, revision `92d8c008d55cf7c254915bac165171dfe6c20c44` (v3.2 and earlier: `google/byt5-small`, revision `68377bdc18a2ffec8a0533fef03b1c513a4dd49d`) |
| Method | LoRA, r=16, alpha=32, dropout 0.05 |
| Target modules | all linear layers (`q`, `k`, `v`, `o`, `wi_0`, `wi_1`, `wo`) |
| Trainable params | 10,764,288 of 592,417,536 (1.82%); v3.2: 6,258,688 of 305,896,448 (2.05%) |
| Optimizer | AdamW, lr 5e-4, 30-step warmup, grad clip 1.0 |
| Batch | micro-batch 4 × grad accumulation 4 (effective 16); v3.2: 8 × 2 |
| Steps | 7,000 (`configs/v4.json`, one run from scratch); 112,000 examples processed. v3.2: 6,500; v3.1 and v3: 5,000; v2: 4,000 |
| Validation | every 250 steps; early stopping patience 8 |
| Precision | bfloat16 base, float32 LoRA + optimizer state |
| Hardware | Ryzen 5 5600, 16 GB RAM, RTX 4060 8 GB |
| Wall clock | 3 h 4 min (v3.2: ~74 minutes; v3.1: ~50, v3: ~52, v2: ~33) |
| Seed | 42 |

Best checkpoint selected by target-token-weighted validation loss: step 6,750, loss 0.0218
(v3.2: step 6,000, 0.0337; v3.1: step 5,000, 0.0371; v3: step 5,000, 0.0343; v2: step 4,000, 0.0376; v1: 0.0554). The validation sets
differ between versions (v3.2 and v4 add targeted sentences), so the losses are not directly comparable.

## Data

70,831 training pairs from 20,756 distinct targets (internal data version v3.5, used for v4):

- 31,932 from Common Voice Turkish Sentence Collector sentences (CC0-1.0, pinned commit); 136 targets
  corrected and 12 removed by the v3.1 audit,
- 8,792 from project-authored everyday sentences (`training/everyday.py`, CC0-1.0),
- 1,272 two-sentence chunks built by joining two pairs of the same difficulty (≤ 170 bytes),
- 13,906 from project-authored targeted sentences (`training/targeted.py`, CC0-1.0; v3.2),
- 15,038 hand-written targeted pairs added in v3.5 (`training/v35.py`, `training/v35_extra.py`, CC0-1.0): spelling 9,196,
  protection of correct words 4,798, proper names 515, explicit spelling 337, conjunctions 152, punctuation 40.
  The v3.2 rows were also audited again: 30 corrected and 109 removed in train (`training/prepare_v35.py`).

Validation has 3,442 pairs (640 Common Voice, 800 everyday, 1,210 targeted, 795 v3.5 targeted); test has 1,128 (frozen from
v2, unchanged). The 146 targets of the first two challenge sets are excluded from train and validation, and the v3.5
additions are also checked against every `evaluation/challenge*.jsonl` file. (v3.2 had 55,902 training pairs from 13,387 distinct targets.)

Each target yields four variants, clean, easy, medium, hard, targeting 0 / 1 / 2 / 4 applied noise
operations; about 28% of examples are deliberately left clean (input equal to target) so the model learns not to touch correct text.
For easy and medium everyday pairs the first operation is always a colloquial transformation.

Noise operations include letter deletion/repetition/transposition, Turkish Q-keyboard neighbours,
diacritic loss, case errors, punctuation, merged/split words, extra whitespace, `de`/`da` and `ki`
clitic merging, question-suffix and apostrophe loss, suffix-based colloquial spellings and, new in v3,
consonant hardening, `ne yap-` contractions, common misspellings and dropped proper-noun apostrophes; v3.2
adds more misspellings and I/İ proper-name corruption, used only by the targeted source.
Every applied operation is recorded with its before/after text in the dataset.

Splitting happens on canonical target form **before** noise is applied, so no variant of the same
sentence crosses splits. This is not a claim that semantically similar sentences are separated, nor
that these sentences are absent from ByT5's pretraining corpus, **that overlap is unknown.**

## Limitations

- **v4:** the dictionary layer is optional, lives only in the GitHub code and depends on `zeyrek` coverage; see *What's new in v4* for its limits (weak candidate ranking, valid forms such as `ürkeği` / `korkağı` damaged, two-edit errors missed, brand names such as `Netflix` corrupted). Without it, v4 generalises to never-taught words about as poorly as byt5-small did (4 of 25, 7 of 26).
- v4 is about 1.6× slower than the byt5-small model and the base weights are 2.33 GB.
- The notes below are v3.2 measurements unless stated otherwise.
- Synthetic noise does not cover the full variety of real user errors. Expect weaker performance on
  genuine user text than these numbers suggest.
- The everyday subset comes from 50 verbs and a limited set of complements; it does not represent real
  chat language in full, and the 87% everyday score is on sentences of the same template family.
- Some misspellings turn into invented words: `klavuz` → `Kalavuz`, `traş` → `taraş`, `sarmısak` →
  `sarmışak`; `kirbit` is left unchanged.
- `ısık` → `Isık` (the name Işık is not restored). Other I/İ names (Isparta, Iğdır, Ilgaz, Ilgın) work in v3.2.
- Regression in v3.2: the correctly written `Nolan'ın` becomes `Ne olan'ın`.
- The word lock only blocks replacements with no letter similarity, so hallucinated, letter-similar words can
  pass (`asabidir → asabıdır` in the test set). The optional lexicon guard cannot help when the misspelled
  source word is itself unknown (`klavuz`, `traş`).
- The challenge-set scores (88.9% and 90.9%) come from sets made of the error types the releases targeted;
  they are not a measure of general accuracy. On the frozen test v3.2 is on par with v3.1, and the Common
  Voice subset has stayed at 70–71% since v2.
- The v3.1 target audit is not exhaustive: Haiku, Sonnet and rule-based scans each found errors the others
  missed, and how many errors remain unfound was not measured.
- Heavy abbreviations (`tşk`, `inş`) can be held back by the word lock and left unchanged.
- Weak on rare and proper nouns, code-switched text, context-dependent `de`/`da`/`ki`, and stylistic
  punctuation choices (e.g. stray `?` or missing commas).
- No context is carried across 176-byte chunks.
- Meaning-altering edits can still occur despite clean-text training and the output guard.
- Token probabilities exposed by the desktop app are **not calibrated confidence scores** and
  should not be read as per-correction certainty.
- Trained and evaluated on sentence-length text (18–160 UTF-8 bytes, 3–24 words, plus two-sentence
  chunks). Behaviour on long documents, lists, code or mixed-language text is untested.

## Versions

| Version | Revision | Steps | Training pairs | Notes (v3.2 and earlier use `google/byt5-small`) |
|---|---|---:|---:|---|
| **v4** | `main` | 7,000 | 70,831 | `google/byt5-base` + LoRA r=16, v3.5 data (audit plus 15,038 new targeted pairs), optional dictionary layer in the GitHub code; frozen test 79.3% (81.6% with the dictionary layer) |
| v3.2 | tag `v3.2` | 6,500 | 55,902 | targeted data (misspellings, I/İ names, correct-word protection), second challenge set, paired comparison; on par with v3.1 on the frozen test, 46 → 60 of 66 on the second challenge set |
| v3.1 | tag `v3.1` | 5,000 | 42,017 | audited targets (136 fixed, 12 removed), 3 contradictory noise rules removed, no same-person subject/object templates; on par with v3 |
| v3 | tag `v3` | 5,000 | 42,075 | new noise ops (hardening, `ne yap-`, misspellings, apostrophes), casing fix, 2,561 everyday sentences, frozen test |
| v2 | tag `v2` | 4,000 | 38,057 | everyday data, colloquial rules, two-layer guard |
| v1 | tag `v1` | 1,800 | 32,000 | Common Voice only; colloquial forms not corrected |

## Licensing

- This adapter: **Apache-2.0**, matching the `google/byt5-base` (v4) and `google/byt5-small` (v3.2 and earlier) base models.
- Project source code: MIT (see the GitHub repository).
- Training sentences: CC0-1.0, from Common Voice and project-authored everyday sentences. No Common Voice
  program code is included here.

## Author

Mustafa Karatüm (ORCID: [0009-0006-7053-2872](https://orcid.org/0009-0006-7053-2872)).

## Citation

```bibtex
@software{megazeka2026,
  title   = {Megazeka: Turkish Spelling Correction with ByT5 and LoRA},
  author  = {Karatüm, Mustafa},
  year    = {2026},
  version = {4},
  url     = {https://github.com/pandakingpunc/megazeka}
}
```
