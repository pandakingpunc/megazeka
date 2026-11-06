"""Megazeka · Türkçe Yazım Düzeltici — Gradio Space demo."""
import os
import re
import threading
from difflib import SequenceMatcher

import gradio as gr

from megazeka_core import correct_text

BASE_ID = "google/byt5-small"
ADAPTER_ID = "pandakingpunc/megazeka-byt5-tr-spellfix"
REVISION = os.environ.get("MEGAZEKA_REVISION", "main")
MAX_CHARS = int(os.environ.get("MEGAZEKA_MAX_CHARS", "1000"))

EXAMPLES = [
    "yarın okula gidicem ama bilmiyom ne zaman dönücem",
    "napıyosun bu akşam burda mısın",
    "herkez bu konuda yanlız değil",
    "kIM OLDUGUMU SOYLEMEYE HACET YOKTU",
    "ankaraya gitcez haftaya",
    "bu gün çok yorgunum bişey yapmıcam",
    "Nihayet şarrrkıyı bbbitirdi ve sazı eline alarak ayağa kalktı",
    "Bugün hava çok güzel, akşam arkadaşlarımla yürüyüşe çıkacağız.",
]

_state = {}
_lock = threading.Lock()


def load_model():
    """Load base ByT5 + LoRA adapter once, merge the adapter, and cache everything."""
    with _lock:
        if _state:
            return _state
        import torch
        from peft import PeftModel
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        device = os.environ.get("MEGAZEKA_DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")
        dtype = torch.bfloat16 if device == "cuda" and torch.cuda.is_bf16_supported() else torch.float32
        if device == "cpu":
            torch.set_num_threads(max(1, os.cpu_count() or 2))
        tokenizer = AutoTokenizer.from_pretrained(BASE_ID)
        base = AutoModelForSeq2SeqLM.from_pretrained(BASE_ID, torch_dtype=dtype)
        model = PeftModel.from_pretrained(base, ADAPTER_ID, revision=REVISION)
        model = model.merge_and_unload().to(device).eval()
        model.config.use_cache = True
        _state.update(model=model, tokenizer=tokenizer, device=device, dtype=str(dtype))
        return _state


def diff_tokens(source, target):
    """Word-level diff as HighlightedText items: (text, 'silindi' | 'eklendi' | None)."""
    a, b = re.findall(r"\S+|\s+", source), re.findall(r"\S+|\s+", target)
    items = []
    for tag, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            items.append(("".join(a[i1:i2]), None))
            continue
        if tag in ("replace", "delete") and "".join(a[i1:i2]).strip():
            items.append(("".join(a[i1:i2]), "silindi"))
        if tag in ("replace", "insert") and "".join(b[j1:j2]).strip():
            items.append(("".join(b[j1:j2]), "eklendi"))
        elif tag in ("replace", "insert"):
            items.append(("".join(b[j1:j2]), None))
    return items


def correct(text, use_guard=True):
    """Returns (corrected, diff_items, raw_output, warnings_text)."""
    if not text or not text.strip():
        raise gr.Error("Düzeltmek için bir metin yazın. / Please enter some text.")
    if len(text) > MAX_CHARS:
        raise gr.Error(f"Bu demoda en fazla {MAX_CHARS} karakter kullanabilirsiniz.")
    s = load_model()
    try:
        result = correct_text(s["model"], s["tokenizer"], s["device"], text, conservative=use_guard,
                              max_chars=MAX_CHARS)
    except ValueError as e:
        raise gr.Error(str(e))
    warnings = "\n".join(result["warnings"]) if result["warnings"] else (
        "Koruma filtresi kapalı." if not use_guard else "Uyarı yok: koruma filtresi hiçbir çıktıyı reddetmedi.")
    return result["output"], diff_tokens(text, result["output"]), result["raw_output"], warnings


CSS = ".footer-note {font-size: 0.9em; opacity: 0.85}"

with gr.Blocks(title="Megazeka · Türkçe Yazım Düzeltici", css=CSS, theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# Megazeka · Türkçe Yazım Düzeltici\n"
        "*Turkish spelling correction with a tiny byte-level model (ByT5-small + LoRA).*\n\n"
        "Hatalı yazılmış Türkçe metni girin; model yazım, aksan ve konuşma dili hatalarını düzeltsin."
    )
    with gr.Row():
        with gr.Column():
            inp = gr.Textbox(label="Metin / Text", lines=6, max_lines=14, max_length=MAX_CHARS,
                             placeholder="Örn: yarın okula gidicem ama bilmiyom ne zaman dönücem")
            use_guard = gr.Checkbox(value=True, label="Koruma filtresi",
                                    info="Modelin kelimeleri silmesini, eklemesini veya anlamca değiştirmesini engeller. / Blocks deleted, inserted or swapped words.")
            btn = gr.Button("Düzelt / Correct", variant="primary")
        with gr.Column():
            out = gr.Textbox(label="Düzeltilmiş metin / Corrected text", lines=6, max_lines=14,
                             show_copy_button=True, interactive=False)
            diff = gr.HighlightedText(label="Değişiklikler / Changes", combine_adjacent=False, show_legend=True,
                                      color_map={"silindi": "#f87171", "eklendi": "#4ade80"})
    with gr.Accordion("Ham model çıktısı / Raw model output", open=False):
        raw = gr.Textbox(label="Koruma filtresinden önce / Before guards", lines=4, interactive=False,
                         show_copy_button=True)
        warn = gr.Textbox(label="Koruma uyarıları / Guard warnings", lines=3, interactive=False)

    gr.Examples(examples=[[e] for e in EXAMPLES], inputs=[inp], label="Örnekler / Examples")

    outputs = [out, diff, raw, warn]
    btn.click(correct, [inp, use_guard], outputs, api_name="correct")
    inp.submit(correct, [inp, use_guard], outputs)

    gr.Markdown(
        "---\n"
        "**Dürüst not:** Bu küçük bir eğitim deneyidir; üretim kullanımı için tasarlanmadı. Test setinde "
        "(1.128 çift) karakter hata oranı (CER) 0,096 → 0,012, birebir eşleşme %77,5. Model hata yapabilir; "
        "önemli metinleri kendiniz kontrol edin.\n\n"
        "*Honest note: a small educational experiment, not production-grade. On the 1,128-pair test set "
        "CER dropped from 0.096 to 0.012 with 77.5% exact match. It can still make mistakes.*\n\n"
        "[Model](https://huggingface.co/pandakingpunc/megazeka-byt5-tr-spellfix) · "
        "[Veri seti / Dataset](https://huggingface.co/datasets/pandakingpunc/megazeka-tr-spellfix-pairs) · "
        "[GitHub](https://github.com/pandakingpunc/megazeka) · Yazar / Author: Mustafa Karatüm",
        elem_classes="footer-note",
    )

# Load the model once at startup (before serving requests).
load_model()
demo.queue(max_size=16)

if __name__ == "__main__":
    demo.launch(server_name=os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0"),
                server_port=int(os.environ.get("GRADIO_SERVER_PORT", "7860")))
