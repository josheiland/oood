# Mary's paired-host thumbnail format

Mary supplied the Episode 000 reference on 2026-09-28. It places Josh and Mary close together on the recording set, a blue square `OUT OF OUR / DEPTH` lockup at upper left, and a navy single-line episode strip at lower left. This direct host reference is the current recurring thumbnail format. The 1280 × 720 Episode 000 JPEG is in `01_EPISODES/E000-why-were-here/release/`.

`mary-clean-photo-2026-09-28.jpg` is the current Episode 000 photo. It is 692 × 461 pixels, but has no baked-in lettering and produces a clean 1280 × 720 thumbnail. `render_thumbnail.py` shapes the logo and title as complete strings in the installed Teachers font. `episode-000.json` holds the editable number, title and photo choice; `episode-000-thumbnail.svg` is a self-contained editable vector with live text and the licensed font embedded. The upload JPEG is `../../01_EPISODES/E000-why-were-here/release/episode-000-thumbnail.jpg`. The older composite and comparison exports were removed at Josh's request on 2026-09-29.

For a later episode, copy the JSON into a new folder with a real host photo, set `episode_number` to `001`, `002`, etc., and change the title. Render to new, unused paths:

```sh
python3 03_ASSETS/thumbnail-template/render_thumbnail.py \
  --config /path/to/episode-001.json \
  --jpg /path/to/episode-001-thumbnail.jpg \
  --svg /path/to/episode-001-thumbnail.svg
```

The renderer refuses to overwrite existing files and shrinks a longer title to fit the strip. Use this paired-host photo layout when a real frame/photo supports it; do not invent reactions or replace the people with generated imagery. The font and OFL license are in `../brand-fonts/`. The current 1280 × 720 JPEG was inspected at full size and at 210 pixels wide; its SHA-256 is `10b0e3bff415b283cc7808812551ff77efa26064dd2ceb7601ad364a4489b5c4`.
