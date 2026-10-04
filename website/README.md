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

The top bar shows only Instagram, X and email, per Josh. TikTok, LinkedIn and Facebook are live but commented out in `config.js`.

## Renumbering and the Episode 002 re-upload (2026-10-03)

Episodes are numbered in public order. Josh re-uploaded the AI-basics episode without pop-ups on October 3 (12:37 p.m. PT, new ID `cp4P_2t5rRQ`), so it is now **002** and the featured latest episode. Projects/connectors/skills is **001**. The old ID `-YWPmoWKbrM` returns 404. The section below is the 9/30 record under the old numbering.

On phones, More episodes shows no thumbnails, the tagline runs two lines, and Josh's cutout is scaled so the hero's bottom edge cuts above the diagonal edge in `josh.webp`.

## Current episodes (verified 2026-09-30, old numbering)

All three launch episodes are public on the official channel. The homepage features Episode 002 and shows Episodes 001 and 000 beneath it, with exact YouTube titles, summaries, thumbnails and direct YouTube links. Episode 000 now points to its September 30 upload, not the September 29 URL.

- 002: https://www.youtube.com/watch?v=d-ykZl4WHjo
- 001: https://www.youtube.com/watch?v=-YWPmoWKbrM
- 000: https://www.youtube.com/watch?v=y0NH_zvAdEo

`config.js` stores the verified launch metadata. The HTML also contains these links, so the episodes remain accessible before scripts load or when the feed is unavailable. The automatic latest-upload lookup stays enabled; a response with an older publication date cannot replace the verified latest upload. Future featured uploads leave the launch episodes in More episodes. Website titles match YouTube verbatim, including capitalization and punctuation, per Josh's September 30 instruction; this supersedes the shorter episode-index title guideline on this surface. When adding future episode summaries, update `episodes` in `config.js` and the matching HTML fallback.

Publication evidence: the official channel Atom feed (`https://www.youtube.com/feeds/videos.xml?channel_id=UCr2sdn2AwHyhjm5SUtWUNGQ`), publisher YouTube / Out of Our Depth, accessed September 30, 2026. Public timestamps: 000 at 21:31:01 UTC, 001 at 22:38:35 UTC, 002 at 23:00:52 UTC, all September 30. These correspond to 2:31, 3:38 and 4:00 p.m. Pacific. This confirms public URLs/titles, not byte identity with local exports or Spotify publication.

## Common edits

- **Spotify is live:** paste the show URL into `spotify` in `config.js`. The button switches from "coming soon" to a real link.
- **Feature a specific episode:** fill in `pinnedEpisode` in `config.js`. It overrides the automatic YouTube lookup.
- **Preview locally:** `npx vercel dev` from this folder runs the page and the function together. Opening `index.html` directly works too, but the episode card stays on "coming soon" without the function.
