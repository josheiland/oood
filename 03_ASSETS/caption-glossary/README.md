# Caption glossary (jtan)

YouTube can't learn custom words, so we fix captions before they're uploaded. `glossary.json` lists the names and terms the show uses, and `fix_captions.py` corrects any SRT or VTT against it.

- **`fix`** rules are applied automatically. Example: "Anthropik", "Anthopic" and "entropic" all become "Anthropic".
- **`review`** rules only flag a line for a human listen, because the right answer depends on context. Example: "Chad" is usually Mary's "Chat", and "cloud" is sometimes Claude.

## Use it

```bash
# Report only, change nothing
python3 03_ASSETS/caption-glossary/fix_captions.py check path/to/captions.srt

# Write a corrected copy plus a report. It never overwrites; pick a new file name.
python3 03_ASSETS/caption-glossary/fix_captions.py fix path/to/captions.srt \
  --out path/to/captions-glossary.srt --report path/to/captions-glossary-report.md

# Vocabulary prompt for Whisper-style transcription (e.g. Whisper's initial_prompt),
# so the transcriber gets the spellings right in the first place
python3 03_ASSETS/caption-glossary/fix_captions.py prompt
```

Timing and cue numbers are never changed. The report lists every fix and every flag, so each one can be checked. If a fix lengthens a caption line past 42 characters, it is flagged for rewrapping.

## Add a word

When a caption gets a name wrong, add it to `glossary.json` once, and it's fixed for every later episode. Keep patterns anchored with `\b` so they don't catch parts of other words. Use a `review` rule instead of a `fix` rule when a wrong guess would introduce a new error.

For other agents: run `fix` on your final caption file before a release and keep the report beside it. Please add terms here rather than keeping private name lists inside episode build scripts.
