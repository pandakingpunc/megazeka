# Orijinal proje brief'i

Bu dosya, projenin başlangıcında bir dil modeline verilen özgün İngilizce görev tanımıdır. Değiştirilmeden saklanmıştır; nihai uygulamanın hangi gereksinimlerden doğduğunu göstermek içindir. Gerçekleşen tasarım kararları ve ölçümler için [README.md](../README.md) ve [reports/](../reports/) dizinine bakın.

---

I want you to build a complete end-to-end AI project from scratch: a small, genuinely trained Turkish spelling and typo correction model with its own local application.
The goal is simple from the user's perspective:
The application contains a large text input box.
The user types or pastes Turkish text containing spelling mistakes, typos, missing/extra letters, incorrect spacing, capitalization mistakes, common keyboard mistakes, and similar errors.
The trained model processes the text and returns a corrected version.
Under or beside the corrected text output, there must be a clear "Copy" button that copies the corrected text to the clipboard.
However, I do NOT want this to simply be a wrapper around ChatGPT, Gemini, Claude, or another hosted LLM API.
I want you to actually build and train or fine-tune a model for this task.
You have freedom to choose the best technical architecture, libraries, model family, training method, dataset strategy, and UI framework.
You may substantially improve the project beyond what I explicitly describe whenever you believe it improves accuracy, usability, maintainability, or training quality.
────────────────────────────
CORE PROJECT GOAL
────────────────────────────
Build a Turkish text correction system that learns to transform noisy / incorrectly written Turkish text into correctly written Turkish.
Example:
Input:
"bugün okula gidicem ama hava cok kötü galiba"
Possible corrected output:
"Bugün okula gideceğim ama hava çok kötü galiba."
Another example:
Input:
"yarin arkadaşlarla buluşcaz sonrada sinemaya gidicez"
Output:
"Yarın arkadaşlarla buluşacağız, sonra da sinemaya gideceğiz."
The model should focus mainly on spelling, typography, punctuation, capitalization, keyboard mistakes, spacing, and common informal written mistakes.
Avoid unnecessarily rewriting the author's meaning or style.
The correction system should behave like a proofreading model, not a creative rewriting assistant.
────────────────────────────
DATA COLLECTION AND DATASET CREATION
────────────────────────────
Build the dataset pipeline yourself.
Research and use legally accessible/open Turkish text datasets where appropriate.
Prefer reputable sources and datasets with licenses compatible with this project.
Document every dataset source and its license.
Do not blindly scrape private, copyrighted, or prohibited sources.
Use clean Turkish text as the TARGET side of the training dataset.
Then automatically generate realistic corrupted/noisy versions of those sentences as the INPUT side.
Create a sophisticated Turkish typo/noise generation pipeline.
Include realistic errors such as:
* missing letters
* duplicated letters
* swapped adjacent letters
* wrong keyboard-neighbor letters
* missing Turkish characters
   * ş -> s
   * ç -> c
   * ğ -> g
   * ü -> u
   * ö -> o
   * ı -> i
* incorrect capitalization
* missing punctuation
* extra punctuation
* missing spaces
* extra spaces
* words accidentally joined together
* words accidentally separated
* common Turkish suffix spacing mistakes
* "de/da" mistakes where reasonably modelable
* "ki" mistakes
* question particle "mi/mı/mu/mü" spacing mistakes
* apostrophe errors involving proper nouns
* casual/chat-style mistakes
* keyboard typos
* character repetitions
* phonetic/informal variants where suitable
* combinations of multiple mistakes in one sentence
Do NOT corrupt every sentence too aggressively.
Create several difficulty levels:
easy
medium
hard
Also preserve a percentage of already-correct sentences so the model learns NOT to modify correct text unnecessarily.
Prevent train/test leakage.
Create train, validation, and test sets.
Save the generated dataset in a reusable format such as JSONL, Parquet, or Hugging Face Dataset format.
────────────────────────────
MODEL
────────────────────────────
Choose an architecture appropriate for sequence-to-sequence Turkish text correction.
You may consider suitable pretrained multilingual/Turkish transformer models and fine-tune them rather than training a language model entirely from random initialization.
Pick the architecture based on actual suitability, compute efficiency, Turkish support, and expected correction quality.
Explain the reasoning in the project documentation.
The trained model must be stored locally after training.
The application must run inference using the resulting trained model/checkpoint.
Do not secretly rely on a cloud LLM API at inference time.
Optimize inference so it is usable on a normal consumer PC where reasonably possible.
If useful, implement:
* batching
* quantization
* ONNX
* Torch compile
* GPU acceleration
* CPU fallback
but choose these intelligently rather than adding complexity for no reason.
────────────────────────────
TRAINING PIPELINE
────────────────────────────
Create a proper reproducible training pipeline.
Include:
* deterministic seeds where possible
* train/validation split
* tokenizer setup
* model training
* checkpoint saving
* best-checkpoint selection
* evaluation metrics
* early stopping if useful
* mixed precision on supported GPUs
* gradient accumulation if useful
* resume-from-checkpoint support
* progress reporting
* training logs
Save:
* final model
* tokenizer
* training configuration
* evaluation results
* dataset metadata
The training system should detect the available hardware and choose reasonable defaults.
Do not assume the machine has a huge datacenter GPU.
If the full target configuration is too expensive, provide a scalable configuration:
small / quick experiment
medium
high-quality
Prefer starting with a small sanity-check training run before launching the expensive full training.
────────────────────────────
EVALUATION
────────────────────────────
Do not judge the model only from training loss.
Create an actual evaluation suite.
Measure relevant metrics such as:
* Character Error Rate
* Word Error Rate
* exact match
* correction precision
* correction recall
* F-score if appropriate
Also build a manually readable evaluation report containing examples:
NOISY INPUT
MODEL OUTPUT
GROUND TRUTH
Include:
* successful corrections
* false corrections
* missed corrections
* difficult examples
Very important:
Measure overcorrection.
A proofreading model that destroys already-correct sentences is bad.
Include an evaluation set containing clean Turkish sentences and calculate how often the model unnecessarily edits them.
────────────────────────────
APPLICATION
────────────────────────────
Build a polished local desktop or local web application.
You may choose the framework you think is best.
The UI should be simple and modern.
Main screen:
1. Title / app name
2. Large text box:
"Metninizi buraya yazın..."
3. "Düzelt" button
4. Corrected text result area
5. "Kopyala" button
6. Clear/reset button
The Copy button must use the clipboard properly.
When copied, briefly show feedback such as:
"Kopyalandı!"
Add:
   * loading state while inference runs
   * useful error messages
   * character counter
   * responsive layout
   * support for multiline paragraphs
   * preservation of paragraph structure
The interface itself should be in Turkish.
Optionally support automatic correction after a short debounce, but only if it does not harm usability/performance.
────────────────────────────
IMPORTANT BEHAVIOR
────────────────────────────
The model should NOT aggressively rewrite sentences.
It should preserve:
   * meaning
   * vocabulary where possible
   * tone
   * sentence structure
unless a change is necessary to correct an error.
For example, do not transform:
"Bu film baya iyi olmuş."
into an entirely different formal sentence just because another phrasing is possible.
This is a spelling/proofreading system, not a style transfer model.
────────────────────────────
PROJECT STRUCTURE
────────────────────────────
Use a professional repository structure.
For example:
project/
app/
data/
models/
src/
training/
evaluation/
scripts/
tests/
configs/
README.md
requirements.txt or pyproject.toml
You may change this structure if you design a better one.
Avoid putting everything into one giant file.
────────────────────────────
TESTING
────────────────────────────
Write tests for important components.
At minimum test:
   * noise generator
   * preprocessing
   * model inference interface
   * text normalization
   * API/backend if one exists
   * clipboard/UI logic where practical
Also run a set of real Turkish examples manually or automatically before considering the project complete.
────────────────────────────
DOCUMENTATION
────────────────────────────
Create a detailed README explaining:
   * what the project does
   * architecture
   * dataset sources
   * dataset generation
   * training process
   * how to install
   * how to train
   * how to resume training
   * how to evaluate
   * how to launch the application
   * hardware requirements
   * model limitations
   * licenses
Include exact commands.
A new developer should be able to clone the repository, install dependencies, train or download the generated checkpoint if available, and run the application.
────────────────────────────
EXECUTION STYLE
────────────────────────────
You are responsible for actually implementing the system, not merely writing an architectural proposal.
Inspect your work continuously.
Run scripts.
Run tests.
Fix errors.
Perform a small training/inference smoke test.
Verify that the application launches.
Verify that text can be entered.
Verify that the model produces output.
Verify that the Copy button works.
Do not stop after scaffolding files.
Do not leave major core functionality as TODO placeholders.
If something fails, investigate it and continue.
You have broad freedom to improve the design.
When choosing between blindly following one of my implementation suggestions and a technically better solution, prefer the technically better solution while preserving the core goal.
At the end, provide a concise technical report containing:
   * model selected
   * dataset sources
   * number of training examples
   * training method
   * evaluation results
   * overcorrection rate
   * hardware used
   * final model location
   * exact command to start the app
   * known limitations
   * potential next improvements
The final product should feel like a real small machine-learning project, not a demo that secretly sends text to another AI service.
────────────────────────────
LEARNING / MODEL INSPECTION PANEL
────────────────────────────
This project is also meant to teach me how machine-learning text correction systems work.
Therefore, add an optional educational "Model İzleme" / "Nasıl Düzeltti?" panel to the application.
The panel must NOT pretend to expose hidden reasoning or internal chain-of-thought.
Instead, expose real, measurable, technically meaningful information about the correction process.
For every inference, show a clear step-by-step inspection view.
Include, where technically possible:
   1. ORIGINAL TEXT
Show the exact original user input.
   2. TOKENIZATION VIEW
Show how the tokenizer split the original text.
For example:
Original:
"bugun okula gidicem"
Tokens:
["▁bug", "un", "▁okula", "▁gidi", "cem"]
Also show token IDs optionally behind an expandable "Advanced" section.
      3. MODEL INPUT
Show the normalized/model-ready input actually passed to the model.
If preprocessing changed anything before inference, explicitly show those preprocessing changes.
         4. MODEL OUTPUT
Show the raw decoded model output before post-processing.
         5. FINAL OUTPUT
Show the final corrected sentence after any deterministic post-processing.
         6. VISUAL DIFF
Create a visual diff between input and output.
Clearly mark:
            * deleted characters/words
            * inserted characters/words
            * replaced characters/words
            * spacing changes
            * punctuation changes
            * capitalization changes
Example:
bugun -> bugün
gidicem -> gideceğim
Make the diff easy for a beginner to understand.
            7. CORRECTION TABLE
Generate a table for every detected change.
Columns could include:
Original
Corrected
Change type
Character edit distance
Confidence / score
Possible explanation
Example:
bugun | bugün | Turkish character restoration | 1 | 0.96
gidicem | gideceğim | spelling/form correction | 4 | 0.89
Important:
"Possible explanation" must be clearly labeled as a human-readable interpretation derived from observable changes or explicit rules.
Do not claim that this explanation is the model's private reasoning.
               8. EDIT OPERATIONS
Compute the exact edit operations necessary to transform the original text into the corrected text.
Show operations such as:
INSERT
DELETE
REPLACE
MOVE if applicable
For example:
REPLACE "u" -> "ü" at character 2
INSERT "e" after ...
DELETE ...
Use a robust diff/edit-distance algorithm.
                  9. CONFIDENCE / MODEL SCORES
If the chosen architecture allows meaningful token probabilities or sequence scores, expose them.
Show:
                     * average token probability
                     * lowest-confidence generated token
                     * sequence score
                     * per-token confidence
Do not invent confidence values.
If the model architecture does not provide a meaningful calibrated confidence score, explain this clearly in the UI.
                     10. TOKEN PROBABILITY EXPLORER
For educational purposes, optionally allow me to click a generated token and inspect the model's most likely alternatives at that generation step.
Example:
Chosen token:
"bugün"
Possible alternatives:
"bugun"
"bugün"
"bugün,"
...
Only implement this where the model/API architecture actually exposes generation logits.
                        11. ATTENTION / INTERNAL VISUALIZATION
If technically meaningful for the selected transformer architecture, add an optional advanced visualization of attention maps or token-to-token relationships.
Clearly explain in the UI that:
attention is NOT equivalent to model reasoning.
Use this feature for learning and inspection, not as proof of why the model made a decision.
If attention visualization would be misleading or technically unsuitable for the selected architecture, skip it and document why.
                           12. PIPELINE TIMELINE
Show the processing pipeline visually:
User text
↓
Normalization
↓
Tokenization
↓
Neural model
↓
Decoding
↓
Post-processing
↓
Final corrected text
Show the time spent at each stage in milliseconds.
Example:
Preprocessing: 1.8 ms
Tokenization: 2.1 ms
Model inference: 84 ms
Decoding: 4.3 ms
Post-processing: 0.7 ms
                              13. MODEL INFORMATION PANEL
Add an educational model-information tab.
Show:
                                 * architecture name
                                 * parameter count
                                 * tokenizer vocabulary size
                                 * model checkpoint
                                 * model size on disk
                                 * max sequence length
                                 * device currently used
                                 * CPU/GPU
                                 * precision
                                 * quantization status
                                 * inference settings
                                 14. LIVE TRAINING DASHBOARD
If training is launched through the project, create a lightweight training dashboard or generated report showing:
                                    * current epoch
                                    * current step
                                    * training loss
                                    * validation loss
                                    * learning rate
                                    * examples processed
                                    * elapsed training time
                                    * estimated remaining training steps
                                    * best checkpoint
                                    * validation metrics
Generate graphs for:
training loss vs steps
validation loss vs steps
CER vs epochs
WER vs epochs
overcorrection rate vs epochs
                                    15. DATASET EXPLORER
Create a simple educational dataset browser.
Allow me to inspect examples such as:
CLEAN TARGET:
"Bugün arkadaşlarımla sinemaya gideceğim."
GENERATED NOISY INPUT:
"bugun arkadaslarimla sinemaya gidicem"
Show which corruption operations generated that noisy example.
Example:
Turkish character removed:
ü -> u
Turkish character removed:
ş -> s
Informal form injected:
gideceğim -> gidicem
Capitalization removed.
This is important because I want to understand exactly what the model is learning from.
                                       16. BEFORE / AFTER TRAINING COMPARISON
Create a small evaluation tool where the same test sentences can be passed through:
                                          * the original pretrained/base model
                                          * the fine-tuned correction model
Display the results side by side.
This should let me directly observe what the fine-tuning process taught the model.
Example:
Input:
"yarin okula gidicem"
BASE MODEL:
...
FINE-TUNED MODEL:
"Yarın okula gideceğim."
                                          17. CHECKPOINT COMPARISON
If multiple checkpoints exist, allow evaluation of the same sentence across different checkpoints.
For example:
Epoch 1
Epoch 2
Epoch 3
Best model
This should help demonstrate how the model improves or potentially overfits during training.
                                             18. EDUCATIONAL MODE
Add an optional "Öğrenme Modu" toggle.
When disabled:
Keep the interface extremely simple:
Text box -> Düzelt -> Result -> Kopyala.
When enabled:
Reveal all educational/model-inspection tools.
The application should therefore work both as a clean proofreading app and as an interactive ML learning environment.
────────────────────────────
IMPORTANT INTERPRETABILITY RULE
────────────────────────────
Never fabricate an explanation of the model's hidden reasoning.
Distinguish clearly between:
OBSERVED:
actual input/output tokens, probabilities, logits, edit operations, timings, attention values, model configuration.
DERIVED:
human-readable descriptions calculated from the observed input/output difference.
UNKNOWN:
the exact internal causal reason the neural network selected a particular correction.
Teach this distinction explicitly in the UI.
The goal is not to make the model appear magical.
The goal is to let me inspect as much of the real machine-learning pipeline as possible and understand what is actually happening.