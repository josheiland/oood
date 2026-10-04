# Share image (`website/images/og-v3.png`)

The 1200 × 630 image LinkedIn, X, Slack and iMessage show when someone links outofourdepth.com. Rebuilt 2026-10-04 after Mary asked for a closer crop with no visible cutout edge.

- **v3 (current):** hosts scaled about 1.56× so the frame's bottom edge sits around 385–390px down each cutout. That's well above the diagonal slash (Mary's starts about 455px down her 518px image, Josh's about 460px down his 653px one) and above the rough dress, hair and arm edges v2 still showed. The background is solid tan, with no foam band.
- v2 (1.33×) still showed some cut edges at the bottom.
- DEPTH crosses their shoulders, like the phone hero. Checked legible at LinkedIn's roughly 256px preview.

Re-render (copy `mary.webp` and `josh.webp` beside `og.html` first):

```
python3 og.py '{"mw":"476px","mx":"24px","my":"30px","jw":"688px","jx":"500px","jy":"20px","kf":"34px","ky":"352px","wf":"262px","wy":"384px"}' out.png "$PWD/og.html"
```

Give a new version a new filename (`og-v4.png`) and update `og:image` in `website/index.html`, since platforms cache previews by URL.
