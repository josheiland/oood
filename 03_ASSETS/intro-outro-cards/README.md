# Mono, Mirrored recurring card template

This is the reusable intro/outro format. On 2026-09-30 Josh removed the episode-number label from the intro and the small show-name label from the outro. `show_episode_number: false` and an empty `outro_kicker` control those omissions. Three-digit numbering remains in episode metadata and thumbnails. The folder was renamed from `codex-mono-mirrored-3digit` on 2026-10-03; old edit records still cite that path.

Josh approved `FIGURING OUT AI TOGETHER` as the recurring tagline on 2026-09-30. Keep this same copy for every episode. The legacy JSON key `episode_title` now stores the tagline; it is not the individual episode title.

The editable SVGs embed the licensed Teachers and JetBrains Mono fonts. The 1920 × 1080 PNGs are matching native-font stills. The actual exports were inspected with native Teachers typography. The three outro lines now sit 48 pixels higher, at y=748, 815 and 882; their spacing stays the same. The outro's empty upper area is available for Josh's intended subscribe and recommended-video elements, whose final placement is still to be checked.

For another episode, copy the JSON into a new empty folder, change its metadata number and any approved outro copy, keep the recurring tagline and hidden labels, then run:

```sh
python3 03_ASSETS/intro-outro-cards/render_cards.py --config /path/to/episode-001.json --output-dir /path/to/new/empty/folder
```

The renderer refuses to overwrite existing exports. Music and timing are added in the episode edit, not in these stills. Earlier two-digit card comparisons were removed at Josh's request on 2026-09-29.
