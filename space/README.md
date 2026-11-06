---
title: Megazeka · Türkçe Yazım Düzeltici
emoji: ✍️
colorFrom: indigo
colorTo: green
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
license: mit
models:
  - pandakingpunc/megazeka-byt5-tr-spellfix
  - google/byt5-small
datasets:
  - pandakingpunc/megazeka-tr-spellfix-pairs
short_description: Türkçe yazım hatası düzeltici (ByT5 + LoRA)
---

# Megazeka · Türkçe Yazım Düzeltici

**TR:** `google/byt5-small` üzerine LoRA ile ince ayar yapılmış küçük bir Türkçe yazım düzeltme modelinin demosu. Konuşma dili ("gidicem"), aksan eksikleri, büyük/küçük harf ve tekrarlı harf hatalarını düzeltir; iki katmanlı koruma filtresi modelin kelime silmesini, eklemesini veya anlamca değiştirmesini engeller. Küçük bir eğitim deneyidir: 1.128 çiftlik test setinde CER 0,096 → 0,014, birebir eşleşme %76,2.

**EN:** Demo of a small Turkish spelling-correction model: `google/byt5-small` + LoRA. It fixes colloquial spellings, missing diacritics, casing and letter repetitions, with a two-layer guard against deleted, inserted or swapped words. A small educational experiment (CER 0.096 → 0.014, 76.2% exact match on the 1,128-pair test set).

- Model: https://huggingface.co/pandakingpunc/megazeka-byt5-tr-spellfix
- Dataset: https://huggingface.co/datasets/pandakingpunc/megazeka-tr-spellfix-pairs
- GitHub: https://github.com/pandakingpunc/megazeka
- Author: Mustafa Karatüm

Set the `MEGAZEKA_REVISION` environment variable (Space variable) to pin a model tag; default `main`.
