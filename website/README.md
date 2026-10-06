# outofourdepth.com

The Out of Our Depth website. Plain HTML, CSS and JS with one Vercel function. No build step.

## Files

- `index.html`, `styles.css`, `main.js`: the homepage
- `config.js`: links you will change (Spotify URL, email, socials, verified episode fallbacks and an optional pinned episode)
- `api/latest.js`: returns the newest long-form YouTube upload. The homepage card uses it, so a new episode shows up on the site on its own, within about 15 minutes of going public
- `images/`: host cutouts keyed from the kit's `banner-youtube.png`, icons and the share image (`og.png`, a crop of the same banner)

Colors, type and layout follow `03_ASSETS/brand-guidelines.md`. Fonts load from Google Fonts (Teachers and JetBrains Mono, both OFL), so no font binaries live in Git.

## Deploy on Vercel

1. Vercel, then Add New, then Project, then import `josheiland/oood`.
2. Set **Root Directory** to `website`. Framework preset: Other. Leave the build and output settings empty.
3. Deploy.

## Connect outofourdepth.com

The domain's DNS is on Cloudflare. Zoho mail runs through the same zone.

1. In the Vercel project, open Settings, then Domains, and add `outofourdepth.com` and `www.outofourdepth.com`. Pick the apex as primary, and let www redirect to it.
2. In Cloudflare DNS, add the records Vercel shows. Usually that means:
   - `A` record: `@` to `76.76.21.21`
   - `CNAME`: `www` to `cname.vercel-dns.com`
3. Set both records to **DNS only** (grey cloud), not proxied.
4. Do not touch the MX, SPF or DKIM records. Those carry `hi@outofourdepth.com`.

## Short links

`vercel.json` redirects `outofourdepth.com/spotify`, `/youtube`, `/instagram`, `/x`, `/linkedin` and `/facebook` to each platform. Use these anywhere a link gets spoken, printed or put in a bio. They are temporary (307) redirects, so changing a destination takes effect right away.

## Social icons (2026-10-03)

The top bar shows Instagram, X, LinkedIn and email. Josh trimmed it to Instagram, X and email on 10/3 and added LinkedIn back on 10/4, with an outline icon to match Instagram. TikTok and Facebook are live but commented out in `config.js`.

**Homepage copy (2026-10-04, later):** “Stanford Business School” replaces “Stanford GSB” on the homepage and description metadata, per Josh. The explanatory subline is removed entirely, with no replacement, to simplify the page. Only the main tagline remains above the watch/listen buttons.

**Hero fade (2026-10-04):** host photos fade into the page tan on desktop and tablet too, per Josh. The wider-layout fade runs from 16cqw to solid tan at 22cqw, with the title above it. The phone fade remains at 46–62cqw.

**Background (2026-10-04):** the page is tan (`--cream`) throughout, per Josh. The foam lower band under the hero is gone, and so is the cream/foam split in the share image (`images/og-v4.png`, built from `03_ASSETS/share-image/`).

## Episode 004 (2026-10-06)

- **Episode 004** "We Asked ChatGPT to Coach Our Ultramarathon. Then We Had to Coach It." (`Fby7CJC9i-Q`, public 10/6 7:54 a.m. PT) is the new lead in `config.js` and the no-JS cards. 003 moves into the grid.
- Titles for 000, 001 and 003 now match YouTube's current casing ("with", "from", "is").
- **002 is unchanged on purpose.** Its YouTube title is in a Test & Compare run, so update it here once the test picks a winner.

## Episode 003, all episodes, phone hero (2026-10-04, later)

- **Episode 003** "What the Heck Is an AI Agent?" (`rxethT04zMY`, public 10/4 12:13 p.m. PT) is the new lead in `config.js` and the no-JS cards.
- **All episodes show**, three per row, per Josh. Older ones wrap onto new rows. `main.js` sizes the laptop hero so everything through the *first* row fits on one screen, and later rows scroll. Tablets: newest full width, the rest three across. Phones: unchanged, newest with thumbnail and the rest as text rows.
- **Mary's cutout is `images/mary-v2.webp`.** `mary.webp` had a notch keyed out of the left of her forehead, because her skin is nearly the tan. v2 restores it from `banner-youtube.png` (her cutout sits at 575,687 in the banner). `mary.webp` stays only as the original.
- **Phone hero:** the hosts are scaled so their heads match (same eyes-to-chin, eyes on one line). The title sits below both chins, and the photos fade into tan, solid by 62cqw, leaving plain tan below as buffer, and clipped at the stage so no hairline of photo shows under it.
- **Share image v4** is v3 rebuilt with `mary-v2.webp`, the only change.

## Renumbering and the Episode 002 re-upload (2026-10-03)

Episodes are numbered in public order. Josh re-uploaded the AI-basics episode without pop-ups on October 3 (12:37 p.m. PT, new ID `cp4P_2t5rRQ`), so it is now **002** and the featured latest episode. Projects/connectors/skills is **001**. The old ID `-YWPmoWKbrM` returns 404. The section below is the 9/30 record under the old numbering.

On phones the tagline runs two lines, and Josh's cutout is scaled so the hero's bottom edge cuts above the diagonal edge in `josh.webp`.

## Redesign (2026-10-04)

Josh asked for a cleaner, less boxy page with fewer words.

- **Top left** is now a navy stacked text wordmark ("OUT OF OUR" over "DEPTH", left-aligned to the D), matching the navy social icons. The blue tile is gone from the header but stays as the favicon.
- **Copy:** the "Hi, we're Josh and Mary" section is cut. The buttons read just "YouTube" and "Spotify". The explanatory subline initially added beneath the tagline was subsequently removed per Josh to simplify the page.
- **Episodes:** the latest-episode popup and the boxed "More episodes" cards are replaced by one borderless grid of the newest three episodes (HD `maxresdefault` thumbnails, mono label, verbatim title). The newest gets a waveform and "New". `/api/latest` still slots a newer upload in first. On tablets the newest leads full width; on phones only the newest keeps its thumbnail and the rest are text rows.
- **Alignment:** everything, including the top bar, sits on one content column (`--container` 1120px plus `--gutter`), so the wordmark, tagline and grid share a left edge, and the last social glyph, buttons and grid share a right edge.
- **Wordmark hover** is Deep-End Blue `#38B6FF`, at Josh's request. The kit limits that blue to type 40px and up, and the wordmark is about 31px. Mary approved this exception on 2026-10-04.
- Laptops 1024×640 and up fit on one screen with no scrolling. A short-screen rule tightens spacing below 720px tall.

## Current episodes (verified 2026-09-30, old numbering)

All three launch episodes are public on the official channel. The homepage shows the newest three, with exact YouTube titles, thumbnails and direct YouTube links. The `blurb` fields in `config.js` are kept but no longer displayed. Episode 000 now points to its September 30 upload, not the September 29 URL.

- 002: https://www.youtube.com/watch?v=d-ykZl4WHjo
- 001: https://www.youtube.com/watch?v=-YWPmoWKbrM
- 000: https://www.youtube.com/watch?v=y0NH_zvAdEo

`config.js` stores the verified launch metadata. The HTML also contains these links, so the episodes remain accessible before scripts load or when the feed is unavailable. The automatic latest-upload lookup stays enabled; a response with an older publication date cannot replace the verified latest upload. The grid shows the newest three; older episodes are one click away through "See all". Website titles match YouTube verbatim, including capitalization and punctuation, per Josh's September 30 instruction; this supersedes the shorter episode-index title guideline on this surface. When adding future episode summaries, update `episodes` in `config.js` and the matching HTML fallback.

Publication evidence: the official channel Atom feed (`https://www.youtube.com/feeds/videos.xml?channel_id=UCr2sdn2AwHyhjm5SUtWUNGQ`), publisher YouTube / Out of Our Depth, accessed September 30, 2026. Public timestamps: 000 at 21:31:01 UTC, 001 at 22:38:35 UTC, 002 at 23:00:52 UTC, all September 30. These correspond to 2:31, 3:38 and 4:00 p.m. Pacific. This confirms public URLs/titles, not byte identity with local exports or Spotify publication.

## Common edits

- **Spotify is live:** paste the show URL into `spotify` in `config.js`. The button switches from "Spotify soon" to a real link.
- **Feature a specific episode:** fill in `pinnedEpisode` in `config.js`. It overrides the automatic YouTube lookup.
- **Preview locally:** `npx vercel dev` from this folder runs the page and the function together. Opening `index.html` directly works too; the grid shows the episodes in `config.js` without the function.
