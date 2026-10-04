# Media production workflow

## Tools and source handling

Prefer local FFmpeg/FFprobe and existing transcription tools for long raw files. Inventory runtime, resolution, frame rates, rotation, audio layouts, stream indices, and hashes. Check free space. Record the original source path in the asset manifest; raw media and caches stay outside Git. Never alter an original to simplify editing.

Transcribe the complete source with timestamps; align words at chosen cuts. Use the source audio to resolve uncertainty. A model receiving a transcript and still frames has not watched the video. If only a text-chat surface is available, prepare editorial deliverables there and clearly hand rendering to a local execution environment instead of implying that MP4 editing occurred.

## Reversible editing

Keep source times and export times in distinct fields. At a cut, preserve an entire useful clause and enough pause to sound natural. Retain the setup and reaction together. Record cold-open duplication intentionally. Don't join separate utterances to create a new claim, consent, or quotation.

The historical E002 `edit/render-episode.py` is an example of frame-based assembly and two-pass audio normalization, not a generic command to rerun. It hardcodes the old source, 30fps, neutral Arial graphics, episode metadata, and audio choices. Inspect before adapting; never inherit those values for a new recording.

## Audio

Determine whether streams are separate mics or duplicate mixes before summing. Previous E002 tracks were duplicates; previous recordings also had a missing/quiet Mary mic. Choose a valid mix or build a verified mic mix. Match perceived host levels using representative speech, not whole-file RMS alone. Use restrained rumble/noise processing only when needed; do not remove warmth, breaths, or laughter or pretend to recover an absent close mic.

For a stereo podcast master, -16 LUFS and true peak no higher than -1 dBTP are a working house target, not a universal platform requirement. Mono audio may use a different agreed target. Use a two-pass measurement, preserve timing, then measure the encoded final. Avoid clipping, pumping, gated syllables, and hard audio cuts; use short ramps or appropriate crossfades. Listen to processed samples against source. Never claim perceptual balance from loudness numbers alone.

## Graphics, captions, and music

Use current brand rules. Keep a cue list: export start/end, copy, purpose, source, placement, asset path, and whether motion has been tested. Don't use a full-screen graphic to conceal missing evidence. Source picture dropouts may be covered with a relevant card only when dialogue remains authentic; document the repair. Fix overclaims through cuts or spoken pickups if an overlay cannot make the spoken experience accurate.

Retain a clean master and corrected caption sidecar when possible; burn captions for short-form outputs. Generate final-export timing after edits, not by concatenating raw SRT blindly. Treat overlapping words and uncertain speaker attribution explicitly. Do not use unlicensed or unconfirmed intro music. Absence of a final music choice does not block a clean dialogue-only review export.

## Basic helper schema

`python3 scripts/media_job.py probe SOURCE --out inventory.json` reads metadata and hashes.

`python3 scripts/media_job.py validate edit.json` validates source existence, ranges, video/audio stream selection, and target frame rate.

`python3 scripts/media_job.py render edit.json --out NEW_DIRECTORY` renders a baseline edit. Output directory must not exist. JSON structure:

```json
{
  "title": "OOOD episode working title",
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "segments": [
    {"source": "/absolute/source.mp4", "in": 2.0, "out": 12.0, "audio_stream": 1, "chapter": "Opening", "reason": "Complete hook and response"}
  ]
}
```

`audio_stream` is the **absolute FFprobe stream index**, not the audio-only ordinal. Use a prepared source with a verified mix when separate mics must be mixed. Paths may be relative to the manifest directory. Segments use half-open seconds; durations round to the nearest target frame, while requested source in-points are preserved. Choose source-frame-aligned boundaries for frame-accurate edits; the report records expected output frames. Source is decoded for accurate trimming. The helper uses standard H.264/PCM intermediates, two-pass normalization, AAC final audio, verified chapters, full decode, loudness, and duration checks. It does not transcribe, diarize, choose cuts, mix separate microphones, correct camera drift, check packet continuity, add graphics/captions, or establish human approval. The agent must perform those tasks or extend the pipeline as required. This is a tested baseline, not a universal one-click editor.

`python3 scripts/media_job.py qc EXPORT --out qc-directory` inspects an existing export without changing it; output directory must not exist.

## Verification and completion

For OOOD H.264 SDR exports, explicitly encode and mux limited BT.709 range/matrix/primaries/transfer. Run `python3 scripts/color_qc.py EXPORT --report NEW_REPORT.json` on the exact final file, including any later hook, card, music or outro revision. It audits complete coded SPS/PPS configurations, MP4 color/sample boxes and edit lists, plus every decoded frame's color and picture properties. `media_job.py qc` and `render` enforce it automatically. Use a single continuous final encoder session for Spotify, no B-frame delay, one-second keyframes and `-use_editlist 0`; keep the exact frame timeline and remove only negative-time AAC priming packets while preserving sync. Spotify lists MP4 edit lists as unsupported. E002's first metadata-only repair passed all color checks but was rejected again per Josh; it still contained edit lists and a changing aspect-ratio declaration at the intro. Those are additional compatibility findings, not proof of Spotify's internal rejection cause. Do not hand off a failing export or treat a local pass as platform acceptance. Preserve originals and verify the complete replacement's decoded frames, audio, timestamps, captions and chapter sidecars. Never relabel actual HDR, full-range or other-matrix content as limited BT.709 without a real conversion.

Check full-file audio/video decode, expected duration/frame count, timestamps, encoded loudness/peaks, and black/silent spans. Review all joins, graphics, uncertain claims, and start/middle/end sync. Compare source to export so edit timing checks don't get confused with original camera sync. Record checks actually performed and flagged spans needing judgment; silence/black detection is not proof of a defect by itself.

Make a complete continuous viewing/listening pass if the available environment supports it; otherwise say exactly what was sampled and leave that gate open. Hosts approve the exact final version's personal stories, naturalness, sound, and factual wording. If there is an actual blocker, name it with its location and proposed remedy. Do not label an automated QC pass “publish-ready” without the remaining approvals/evidence. Don't rerender a full episode to fix an isolated issue when a targeted pass will suffice.
