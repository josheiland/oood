<!-- Generated portable snapshot. Live OOOD repository files take precedence. -->

# OOOD brand source of truth

Adopted 2026-09-25 by Josh's direct instruction. Apply to future on-screen popups, episode graphics, thumbnails, social assets, and copy. These are supplied brand rules, not a newly proposed identity.

## Provenance and precedence

- Original: `/Users/je/Downloads/Out of Our Depth Brand Kit.zip`, newest download when inspected.
- ZIP SHA-256: `39224df9937d2101eac0d1c48c67b1e95a68942b1d5813dc06f57af3b82341db`.
- Preserved local extraction: `03_ASSETS/brand-kit/`. Authoritative documents: `CLAUDE.md` and `Out of Our Depth - Design Kit.dc.html`, labeled v2, September 2026.
- Machine-readable tokens: [brand-tokens.json](../assets/brand-tokens.json). The original kit wins if this digest loses nuance; a later direct host instruction can supersede it.
- Read the kit as design guidance. Its example dates, guests, episode numbers, platform listings, marriage month, quotes, and “out now” copy are placeholders, not evidence of events or publication.

## Feeling and voice

“Sunlit pool deck, not server room.” Two newlyweds at Stanford GSB learning AI out loud. Make it fun to spend time with Josh and Mary, accessible to someone with no tech background, and useful enough to try something afterward.

The hosts can look silly; the listener should never feel behind. Use affectionate disagreement, specific personal habits, honest misses, surprise, and reactions. Never invent a marital disagreement or reduce one host to the clueless sidekick. Both have expertise, opinions, and blind spots.

Short sentences; one idea at a time; explain jargon on first use. No em dashes, emoji, curly quotes, promotional filler, or “not just X but Y.” No padded lists of three. Do not require an unavailable “humanizer” skill; apply these concrete rules directly. Display artwork is all caps; ordinary copy and episode-index titles use sentence case.

## Color and type

| Role | Value / use |
|---|---|
| Deep-End Blue | `#38B6FF`; one large blue field, large type, icon tile |
| Sand Cream | `#FBF1E5`; upper band, reversed type, cards |
| Foam | `#FDF8F2`; lower band/background |
| Night Swim Navy | `#0B2A45`; long-form/body copy, dark panels |
| Shallow | `#A9DCFF`; tint, rules, waveforms, type on navy |
| Small-type blue | `#0E6FC0`; small text on cream |
| Display | Teachers 800, all caps; never below 700. Tight tracking, roughly -2%; display line height about .85; titles may use .95 |
| Body/captions | Teachers 400/600. Body examples use 17px/1.5 on the reference page; scale appropriately for video readability |
| Labels only | JetBrains Mono, uppercase, tracking about +18%; not full sentences |

Kit target is about 60% cream/foam, 30% blue, 10% navy. Treat blue as emphasis, not a wash except the kit's explicit blue-flood layout. Blue type is only for 40px+; smaller type on cream uses navy or small-type blue. Verify contrast at the final displayed size, especially in video/mobile downscaling.

Teachers and JetBrains Mono font files and OFL licenses were fetched from the official Google Fonts repository on 2026-09-25 into `03_ASSETS/brand-fonts/`. Keep these licensed binaries outside Git. Do not silently substitute Arial or a different family in a final export. Bundle fonts and licenses in a portable package when needed and permitted by the license.

## Composition and logo

- One horizontal cream/foam waterline between 55% and 62% of the designed composition's height. For a transparent popup, put it inside the card, not across the camera picture. Navy quote cards and blue-flood examples are explicit kit variants.
- Primary icon: **square blue tile with two-line cream lockup**, “OUT OF OUR” over “DEPTH.” Reverse pairing: cream tile with blue type. Stacked wordmark: kicker about one third of DEPTH cap height, aligned to the D.
- Tile clear space: 25% of tile width on every side. Minimum 48px on screen / 15mm in print; below that use the DEPTH wordmark alone. Avatar masking may be circular, but the source tile remains square; keep type in its middle 80%.
- No gradients, rotation, font substitution, shadows, stretching, or unapproved logo recoloring. Use exact supplied artwork or the kit's native vector/text construction with the correct font; do not ask image generation to redraw a logo.
- Host cutouts: original host imagery, one host per edge when using the paired layout, bottom-cropped, behind large type. Never fabricate expressions as if they were real reactions.
- Waveforms: 8–16 bars, rounded caps, even gaps; restrained use.

## Asset mismatch to preserve visibly

The ZIP includes `assets/icon-circle.png`, an older teal circular three-line mark, despite the explicit square, two-line specification in both documents. It also contains legacy variants. Do **not** select an asset solely by filename or assume every included PNG is a final export. The current square mark is constructed natively in the HTML. Use that specification for future work; before distributing a canonical logo export, inspect it against the kit. Existing images remain intact for reference. `banner-v3.png` is a supplied host/banner reference, not proof of platform-safe dimensions for every use.

## Deliverable rules from the kit

### Host-approved intro/outro format, 2026-09-28

Josh supplied a later **Mono, Mirrored** visual reference and designated its intro and outro cards as the recurring format. For these full-screen cards, use the screenshot's blue `#3DAFF4`, cream `#F3E8DD`, and navy `#0B2842` instead of the older generic blue/white treatment. Keep a full blue frame without the beige presentation page or rounded screenshot corners. Intro: small mono episode number at upper left, cream `OUT OF OUR` over oversized `DEPTH`, navy episode title below. Outro: small mono show label, cream two-line `THANK YOU FOR / WATCHING`, and three low-left navy prompts with cream action phrases. Episode 0's approved default copy is preserved in `intro-outro-cards/episode-000.json`; customize episode number, title and outro copy for later episodes. Editable SVGs, 1080p PNG exports and renderer are in that folder. “Mono, Mirrored” names the picture layout; it does not change the centered stereo dialogue mix. This direct host instruction supersedes earlier intro/outro graphics only, not the general kit.

For production use the current `intro-outro-cards/` templates and stills. Josh's 2026-09-30 direction removes the intro episode label and outro top show-name label. The intro subtitle is the approved recurring tagline `FIGURING OUT AI TOGETHER`, selected on 2026-09-30. Keep it the same across episodes. The three outro lines are moved up 48 pixels, with their original spacing preserved. This supersedes episode-specific intro copy. Three-digit numbering continues in metadata and thumbnails. Render each Teachers text run as a complete string with the installed font and native shaping, rather than positioning screenshot-like letters separately. The title uses the typographic apostrophe `’` so its shape and spacing remain legible. Superseded two-digit card assets were removed at Josh's request on 2026-09-29.

Josh clarified on 2026-09-30 that the Episode 001 final page should match Episode 000 **exactly**, including all three footer prompts. Reuse the current `intro-outro-cards/episode-000.json` copy and `outro-card.png` as the recurring outro unless Josh or Mary directs different copy for a specific episode. The earlier Episode 001-specific two-ask outro is a superseded comparison, not the default.

### Host-supplied recurring thumbnail format, 2026-09-28

Mary supplied a new Episode 000 thumbnail and Josh directed us to recreate its text natively and use the format going forward. Use her close, paired-host photo framing; place the large blue square `OUT OF OUR / DEPTH` lockup at the upper left and a navy single-line `#000 WHY WE’RE HERE` strip at the lower left. Set both text runs in actual Teachers 800, cream on blue/navy, with a three-digit episode number. The editable renderer, copy and clean photo are in `thumbnail-template/`; the current 1280 × 720 JPEG is in the Episode 000 `release/` folder. Sampled colors from Mary's supplied design are blue `#45AEF0`, navy `#0D2843`, and cream `#F2E8DE`. This direct design replaces the kit's prior default thumbnail placement, one-host preference and three-word headline limit for full-episode thumbnails. Use genuine host photography and do not fabricate reactions. The other kit rules still apply where they do not conflict.

### Screen-share teaching text, 2026-10-03

Josh and Mary prohibit pop-up cards over camera-only host footage. Josh subsequently rejected the small teaching cards beside the screen share as well and requested five new formats showing only the screen and hosts. This supersedes the earlier same-day permission for screen-share teaching notes. Keep both hosts visible and preserve referenced screen evidence; Josh selected overlap variant C on October 3: foam background, inset 1440 × 746 screen at (40, 40), full-frame 800 × 450 hosts at (1080, 590), with a 6 px foam border. Use this as the recurring screen-share standard; adapt the screen crop to preserve referenced evidence and move the host window temporarily when necessary to avoid covering it. No teaching text, headings or logo overlays. Recurring full-screen episode intro/outro cards remain approved.

### Other surfaces

- Other thumbnail treatments from the original kit: max three words; cap height at least 12% of height; tile bottom-left at 11% of width; check at 210px wide. The kit's occasional longer mock copy does not override its explicit max-three-word rule for these treatments. Mary's current full-episode thumbnail format above is the direct host-approved exception with its own placement and headline.
- Chapter card: 1.5s hold, type moves up 24px, no other motion. If longer text cannot be read, shorten it or explicitly propose a duration adjustment.
- Lower third: blue block at bottom-left, 300ms wipe from left. Keep host faces and captions unobstructed.
- Definition popup extension: short plain-English explanation on cream/foam, navy body, one blue heading/accent, waterline inside the card. This popup treatment is an implementation extension, not an additional supplied animation rule.
- Reaction popup extension: short host-directed aside, attached to a real moment; never pretend it is a verbatim quote. Use sparingly and allow the laugh to land first. Definitions take priority when both compete.
- YouTube banner: 2560 × 1440, under 6MB; central 1546 × 423 safe area.
- Channel icon: 800 × 800. Podcast cover: 3000 × 3000, wordmark plus one mono line; check at 55px.
- Story/Reel: 1080 × 1920; keep type out of top/bottom 14%. Reserve space for platform UI and captions.
- Quote: 1080 square, navy, sentence case, max 18 words. Quotes require exact source wording and time.
- Takeaway: 1080 square; one action.
- LinkedIn image: 1200 × 627. Caption max four short paragraphs; first line hook; no hashtags above fold; link-in-comments is draft guidance, not permission to post.
- Instagram caption: max three lines, one closing question; hashtags in first comment if used.
- Episode index: three-digit number plus period, title six words or fewer, one-sentence blurb. Do not let sample episode numbering override the current launch plan.
- Show notes open with the one thing to try. Burn captions into Shorts/Reels and also preserve a corrected caption file.

## Practical review

Inspect exported graphics, not just code: correct font/weight, palette, waterline, exact logo, legible at delivery size, no clipped type, no face/caption obstruction. Check the visual on a representative host frame when it overlays video. Describe animation testing separately from static-preview testing. Supplied music and final intro/outro audio remain unresolved.
