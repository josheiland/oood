# outofourdepth.com

The Out of Our Depth website. Plain HTML, CSS and JS with one Vercel function. No build step.

## Files

- `index.html`, `styles.css`, `main.js`: the homepage
- `config.js`: links you will change (Spotify URL, email, socials, `hiddenVideos`, an optional pinned episode) plus the saved episode list, which the sync job maintains
- `api/latest.js`: returns every public long-form YouTube upload (newest 15, no Shorts). The homepage merges it with the saved list, so a new episode, with its number and HD thumbnail, shows up on its own within about 15 minutes of going public
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

## Newsletter signup, tan buttons, site-only titles (2026-10-11, later)

- **Signup at the bottom of the page**, from Mary's mockup, built as a navy band (option D of five Josh and Mary compared). Heading "We take notes. Want a copy?" in cream Teachers 800, held to one line at every width; subline "No more than one cute little email each month." No handwriting font: Mary didn't like the mockup's, and they chose the site's existing fonts.
  - The form posts to `api/subscribe.js`, which saves the address to Upstash Redis: Vercel Marketplace resource **`oood-newsletter`** (free plan), connected to the `oood-website` project, which sets the `KV_*` env vars. Addresses go in the hash `newsletter:subscribers`, keyed by the lowercased address, with the time and source. A second signup keeps the first record.
  - Bot guard: a hidden `website` field (filled in = pretend success, save nothing) and 30 signups per IP per hour. It works without JS too: a plain form post redirects back to `/?subscribed=1#notes`.
  - **Export the list:** `vercel env pull .env.newsletter --cwd website` once (gitignored), then `node scripts/export-subscribers.js > subscribers.csv`. The export uses the read-only token.
  - Nothing sends email yet. This only collects addresses.
- **Listen buttons** (YouTube, Spotify, Apple Podcasts) are all tan with a navy outline and turn blue on hover or keyboard focus, per Josh.
- **`siteTitles` in `config.js`** shows a different title on the site than on YouTube, by video ID. The sync job keeps YouTube's title in the saved list and uses `siteTitles` on the no-JS cards. First use: 004 shows as "Build With Us: Turn ChatGPT Into Your Coach".

## Apple Podcasts, tagline, full-width latest episode, Mary v3 (2026-10-11)

- **Apple Podcasts button** next to YouTube and Spotify, outlined like Spotify. URL is `applePodcasts` in `config.js`; short link `outofourdepth.com/apple`. On phones YouTube gets its own row and Spotify and Apple Podcasts share the next.
- **Tagline** is centered above the buttons at every width, in sentence case (no more all caps), set in **Poppins 500**, per Josh. Poppins applies to those two lines only; everything else stays Teachers and JetBrains Mono. Phones break it into three lines: "Underprepared newlyweds at / Stanford Business School, / learning AI out loud".
- **Newest episode runs the full content width** on every screen size; older episodes stay three across under it (text rows on phones, as before). `main.js` now sizes the laptop hero so the tagline, buttons and the top ~160px of the newest episode fit on one screen.
- **Mary's cutout is `images/mary-v3.webp`** (610 × 1036, 2× the old size, same framing). v2 still had her far eye, nose tip and cheek keyed out along the left edge. v3 was cut fresh from the full-resolution original photo Mary texted Josh on 10/11 (macOS Vision subject lifting, local), aligned to v2's framing, colour-matched to the banner grade so she still matches `josh.webp`, and defringed. The bottom of the cutout still has rough edges, but the hero fade covers that zone at every width.
- **Share image is `og-v5.png`**, v4's layout rendered with `mary-v3.webp`. LinkedIn caches previews about a week; re-run linkedin.com/post-inspector to refresh.

## Episodes update themselves (2026-10-06)

Nobody needs to edit the episode list. Two pieces keep it current:

1. **Live, within ~15 minutes:** `api/latest.js` reads the channel's long-form uploads feed (playlist `UULF...`, which leaves out Shorts). Backups are the channel feed and then the Videos tab. `main.js` merges that with the saved list: new uploads appear, YouTube's current title wins, and episodes are numbered 000, 001, ... in publish order.
2. **Saved, every 6 hours:** the GitHub Action `.github/workflows/sync-site-episodes.yml` runs `scripts/sync-site-episodes.js`. It writes new uploads and renamed titles into `config.js` and the no-JS cards in `index.html` (between the `episodes:start` / `episodes:end` markers) and commits, which redeploys through Vercel. That keeps old episodes listed after they fall out of the feed's newest 15. It swaps in the HD thumbnail once YouTube has one. Run it by hand from the Actions tab, or locally with `node scripts/sync-site-episodes.js --dry-run`.

Safety rules in the sync: a video is dropped only when YouTube's oEmbed says it doesn't exist (404). It never drops more than one per run; more than that fails the run, which GitHub emails about. If YouTube can't be reached, nothing changes.

- **A long-form upload that isn't an episode** (trailer, clip): add its ID to `hiddenVideos` in `config.js`. It disappears and stops counting toward numbers.
- **Re-uploads:** once the old video is deleted, the next sync drops it and renumbers, as on 10/3.
- **Title tests:** while a YouTube title test runs, sources can disagree on the title. The site shows what the feed reports.
- **Pull before you push:** the job commits to `main`, so run `git pull` before pushing local work.

## Episode 004 (2026-10-06)

- **Episode 004** "We Asked ChatGPT to Coach Our Ultramarathon. Then We Had to Coach It." (`Fby7CJC9i-Q`, public 10/6 7:54 a.m. PT) is the new lead in `config.js` and the no-JS cards. 003 moves into the grid.
- Titles for 000, 001 and 003 now match YouTube's current casing ("with", "from", "is").
- 002 was left alone during its title test. The sync job now handles titles.

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
