You are auditing TARGET sentences of a Turkish spelling-correction training set (ByT5 model). Targets must be perfectly written standard Turkish (TDK). Any error in a target teaches the model a wrong spelling, so recall matters, but every flag will be human-verified, so do not invent errors either.

Each input line is `<id><TAB><sentence>`. Read each file completely with the Read tool and go through EVERY line one by one. Do not skim.

Flag types:
- `yazim`: misspelled word. Pay special attention to OCR errors from scanned books: "rı"/"ri" read as "n" (memurlan→memurları, kaşlan→kaşları, kenannda→kenarında, yaşma→yaşına), "rn" read as "m", "ı/i" confusion, missing ş/ğ/ç/ö/ü (sey→şey), doubled or dropped letters (yüksellti, alttğı, uykusuından).
- `konusma_dili`: colloquial/spoken spellings that are not standard written Turkish, EVEN INSIDE DIALOGUE: burda, orda, şurda, nerde, nerden, burdan, içerde, dışarda, bi (for bir), napıyorsun, bişey, diil, gelcem/gidicem-type forms, cıgara, onla (onunla), sora (=sonra). Fix to the standard form. (Reason: the training noise turns standard forms into these, so they must never appear in targets.)
- `ayri_bitisik`: "hiç bir"→"hiçbir", "her şey"/"bir şey" joined, "herzaman", conjunction de/da and ki joined or locative/-ki split, question particle mi joined, "her zaman ki"→"her zamanki".
- `kesme`: missing/wrong apostrophe on proper-noun inflection (Allaha→Allah'a, Aydının→Aydın'ın when the region is meant). Derivational suffixes -lı/-li, -lık, -cı do NOT take an apostrophe (Praglı, İstanbullu are correct).
- `buyuk_harf`: wrong capitals mid-sentence (Ben Bu akşam), lowercase sentence start.
- `noktalama`: double final marks (.., !., ;.), yes/no question with "mi" ending in a period, clearly missing comma in a list.
- `dilbilgisi`: broken suffix, wrong case (cevabım beklemeden→cevabını), vowel harmony, mi/mı harmony (yolunda mi→yolunda mı).
- `anlamsiz`: nonsense or unnatural sentence. For conversational template sentences especially: subject and object are the same person (2nd singular verb with seni/sana/seninle: "Yakında seni unutur musun?", "Sen seni izliyorsun"; 1st singular verb with beni/bana/benimle: "Bana yardım edeceğim"), or absurd verb-object pairs. fix = null.

Do NOT flag (these are correct): archaic/literary vocabulary and proverbs; "kati" (=kesin), "tabi olmak" (=bağlı olmak), "bilmem", "abi", "can" as a name; "Samsun da ..." where da is the conjunction "too"; "Bu akşam akşam yemeği"; spoken constructions like "Ne yap biliyor musun?", "Sorunun ne biliyor musun?"; tense forms like "olduydu"; optional circumflex; foreign names; word order or style.

Output: write ONE file with the Write tool (path given below). One JSON object per line, UTF-8, real Turkish characters:
{"id": 123, "target": "<original sentence exactly as in the file>", "fix": "<fully corrected sentence with ALL errors fixed, or null>", "type": "yazim", "note": "<short Turkish reason, e.g. 'memurlan -> memurları'>"}
Copy `target` exactly. If nothing is flagged write an empty file. Do not create or modify any other files.

Final reply: number of lines checked, number flagged, and at most 5 example flags. Keep it short.
