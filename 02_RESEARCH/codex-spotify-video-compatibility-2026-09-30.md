# Spotify video compatibility: Episode 002 repeated rejection

Accessed 2026-09-30. Technical production evidence; no upload or processing success claimed.

## Official sources

- **Spotify, Video specs** (undated): https://support.spotify.com/us/creators/article/video-specs/ — MP4 edit lists are unsupported; one video and one audio track; equal audio/video duration; H.264 and Rec.709 SDR recommended; 30 fps accepted; approximately one keyframe per second recommended; first video PTS within 50 ms of zero. Any bitrate is accepted within file-size limits. These are documented requirements/recommendations, not an explanation of Spotify's internal color-error classifier.
- **FFmpeg, Formats documentation** (live/undated): https://ffmpeg.org/ffmpeg-formats.html — MP4/MOV `use_editlist` controls edit-list use. Accessed 2026-09-30. Verified the resulting box structure locally rather than relying only on the option.

## Local findings

Josh reports the first corrected Episode 002 Spotify file still produces the same color-change error. Prior correction normalized all coded color tags and all 59,828 decoded frames passed the color-only gate. Expanded inspection confirms those color tags remain uniform. It also finds three `elst` boxes and two SPS configurations: the intro at 7.133333 s omits the aspect-ratio declaration present elsewhere. PPS is consistent; one video sample entry exists. See `01_EPISODES/E002-make-ai-useful/edit/codex-spotify-continuous-encode-2026-09-30/previous-repair-expanded-audit.json`.

**Confirmed:** unsupported timing edit lists are present; an encoding declaration changes at the intro. **Unconfirmed:** which of those, if either, triggers Spotify's exact color-error message. No new hidden color change was found in the previously corrected file.

## Remedy and prevention

Create a fresh continuous H.264 8-bit 4:2:0 1080p30 encode with explicit limited BT.709, stable square pixels, one-second GOPs, no B-frame delay, no MP4 edit lists, and only video/audio tracks. Copy the existing AAC payload, dropping only the negative-time priming packet; verify all audible packets and timestamps. Keep captions and chapters as matching sidecars, with the same final-cut timeline. Expanded gate checks complete coded parameter sets, MP4 color/sample structure, edit-list absence and every decoded frame. Local acceptance does not prove Spotify processing acceptance.
