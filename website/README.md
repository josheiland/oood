# outofourdepth.com

The Out of Our Depth website. Plain HTML, CSS and JS with one Vercel function. No build step.

## Files

- `index.html`, `styles.css`, `main.js`: the homepage
- `config.js`: links you will change (Spotify URL, email, socials, an optional pinned episode)
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

## Common edits

- **Spotify is live:** paste the show URL into `spotify` in `config.js`. The button switches from "coming soon" to a real link.
- **Feature a specific episode:** fill in `pinnedEpisode` in `config.js`. It overrides the automatic YouTube lookup.
- **Preview locally:** `npx vercel dev` from this folder runs the page and the function together. Opening `index.html` directly works too, but the episode card stays on "coming soon" without the function.
