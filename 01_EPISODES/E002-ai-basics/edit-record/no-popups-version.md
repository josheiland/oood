# Episode 001 — pop-up-free replacement

This package implements Josh's October 3 request to remove definition/correction overlays from the published cut. Current export: `episode-001-no-popups.mp4`. Status: rendered and technically checked; local replacement ready for host review and re-upload. Not uploaded or published.

## Changes and coverage

- Remove the model-access pop-up at 02:16.100–02:21.600.
- Remove the OpenAI nonprofit/for-profit pop-up at 43:11.667–43:17.167.
- Restore the original full camera image for each 165-frame interval, rather than cropping or masking it.
- Keep all conversation, cuts, mastered audio, the selected `ep1hook`, the covered-lens beginning, recurring intro/music and exact Episode 000 outro.
- Preserve runtime, embedded chapter timing, caption bytes and saved description/chapters. No new conversation cuts.

## Provenance and reproduction

`inputs/episode-001-published.mp4` is the SHA-256-verified Drive release (file ID `1fycZY0Em45E8XyCIYdAwifX-cq6P0wEj`, SHA-256 `181624da06b3255f393fb3dbbe36bfe9f154e9c83fef32fcb5a9ebb6aeb3e87d`). `inputs/episode-001-original-raw.mp4` is the verified raw source (Drive file ID `1z1Zdo2TLCzsOCx2oRYdi83cI9YeGGhE_`, SHA-256 `9f58d3a39c91ce4499fd3215355ddc9873051e6e32a5b26a6c73ce05caf93107`). Both cloud originals remain unchanged.

`popup-removal-plan.json` records exact source/output frames. The restored historical edit decisions establish the two remaining overlays; earlier GPU pop-ups were within the already removed NVIDIA detour. Before/raw picture samples verify the source mapping. `build-no-popups.py` and `render-command.json` record one continuous, explicit limited-BT.709 H.264 encode. Audio is stream-copied, removing only negative-time AAC priming packets for container compatibility.

`verify-no-popups.py` checks frame count, runtime, all embedded chapters, retained AAC payload identity, complete audio decoding, every repaired frame against raw picture and the complete coded-header/container/full-frame export gate. Screenshot checks cover both repair boundaries and the selected hook, intro, covered lens and outro. Technical verification does not establish host approval or platform acceptance.

The matching SRT is `episode-001-no-popups.srt`; `description-and-chapters.txt` retains the saved description unchanged. Episode 002's original release requires no re-render: see the adjacent episode's `edit/codex-no-popups-audit-2026-10-03/README.md` for renderer provenance and sampled picture verification.

## Exact-file results

The output is 52:25.733, 94,372 frames, 1920 × 1080 at 30 fps, 2,058,534,021 bytes. SHA-256: `e5ee8b93c9a621f6700e6df1d311fe5289321eaf58c95002087a98a5f6656bea`. Both video and audio start at 0 and last 3,145.733333 seconds. All 22 embedded chapters match exactly. Caption and saved description bytes match the previous sidecars. All retained nonnegative-time AAC packet payloads match; full audio decoding passed.

All 165 frames in each repair match the original camera at SSIM ≥ 0.9945. First, middle, last and following frames were visually checked. The current hook, intro, covered-lens beginning and three-prompt outro were also checked. The full coded-header/container gate passed: one stable H.264 configuration, explicit limited BT.709, no edit lists, and all 94,372 decoded frames with consistent picture/color properties and increasing timestamps. Detailed evidence is in `integrity-checks.json`, `picture-review.json` and `color-qc.json`. This is sampled visual inspection and numerical verification, not continuous human viewing/listening. Previous caption auditory review limitations remain. No source or published/cloud file was changed or deleted.
