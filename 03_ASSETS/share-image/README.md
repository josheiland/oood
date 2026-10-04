# Share image (`website/images/og-v2.png`)

The 1200 × 630 image LinkedIn, X, Slack and iMessage show when someone links outofourdepth.com. Rebuilt 2026-10-04 after Mary asked for a closer crop with no visible cutout edge.

- Hosts are the site cutouts (`website/images/mary.webp`, `josh.webp`) scaled about 1.33×. The frame's bottom edge sits above the diagonal slash in each cutout: Mary's starts about 455px down her 518px image, and Josh's about 460px down his 653px one.
- DEPTH crosses their shoulders at the waterline, like the phone hero. Checked legible at LinkedIn's roughly 256px preview.

Re-render (copy `mary.webp` and `josh.webp` beside `og.html` first):

```
python3 og.py '{"mw":"406px","mx":"48px","my":"30px","jw":"587px","jx":"584px","jy":"28px","kf":"34px","ky":"332px","wf":"262px","wy":"364px","wl":"476px"}' out.png "$PWD/og.html"
```

Give a new version a new filename (`og-v3.png`) and update `og:image` in `website/index.html`, since platforms cache previews by URL.
