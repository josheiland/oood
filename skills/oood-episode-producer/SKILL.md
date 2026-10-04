---
name: oood-episode-producer
description: Turn Out of Our Depth raw recordings into a rendered episode and release-review package, including editorial cuts, dialogue cleanup, branded graphics, captions, chapters, and verification.
---

# OOOD episode producer

Deliver the actual episode when raw media and execution tools are accessible. A cut list alone does not fulfill “make the episode.” This skill orchestrates editing tools; it is not a video-generation model. Read live project context and [editorial direction](references/editorial-direction.md), [brand guide](references/brand-guide.md), then [production workflow](references/production-workflow.md). Use [show context](references/show-context.md) only when live repo context is unavailable. New instructions win over bundled snapshots.

## Inputs and scope

Resolve episode ID and raw path(s), prior cut/notes if relevant, and requested deliverables. Identify existing files before creating a new episode folder. Never infer episode identity from the older `001-make-your-ai-useful` path: that is a historical recording of what became E002. Don't mix old takes into a new-source-only request.

Inventory runtimes, streams, frame rates, source hashes, and space. Preserve originals. Do not overwrite an existing export; version outputs. Read/edit local media with available tools. Check available transcription and font dependencies before large processing. If a capability is missing, complete unaffected deliverables, identify the precise blocker, and never claim a video was rendered or reviewed. Do not buy services or upload private footage to a new external service without authorization.

## Editorial mandate

Optimize for fun, comprehension, and attachment to the hosts together. Preserve real laughter, meaningful interruptions, affectionate disagreement, surprise, and callbacks. Keep the setup that makes a reaction make sense. Tighten repetition and abandoned starts without flattening every pause or converting the conversation into a lecture. Both hosts must retain substantive judgment; do not cast Mary as merely asking Josh questions.

Review the full transcript plus source audio and picture around candidate joins, strong relationship moments, and uncertain claims. Timestamp speakers only when supported. Mark uncertain words instead of inventing them. Distinguish “transcript read,” “frames sampled,” “clips listened to,” and continuous audiovisual review. Verify factual corrections in speech; an overlay is insufficient if it reverses an audible claim.

Create a reversible edit decision list with source ranges, output positions, reasons, and whether each cut affects a joke, claim, or transition. Make substantive first-pass decisions within the request; don't stop to ask permission for every cut. Keep comments on the proposed edit separate from approved host decisions.

## Finish and verify

Follow the production reference for dialogue, timing, graphic, caption, and export requirements. Use the supplied brand for new graphics; don't reuse the old neutral Arial graphics as the current identity. Use the bundled `scripts/media_job.py` for read-only inventory, strict edit-list validation, a basic reproducible render, and technical QC when it fits. Its reference documents its limits. Adapt the render for separate microphones, complex transitions, graphics, and speaker automation when needed; do not silently omit requested finishing because the helper is basic.

Every final H.264 SDR export, including custom card/hook swaps, must pass `python3 scripts/color_qc.py EXPORT --report NEW_REPORT.json` before handoff. Set limited BT.709 range, matrix, primaries and transfer on newly encoded segments and the final container. The gate checks every coded SPS/PPS configuration, MP4 color boxes, sample descriptions, absence of unsupported MP4 edit lists, and every decoded frame's color, dimensions, pixel format, aspect ratio and interlacing. A stream-header or keyframe-only check can hide unspecified tags at a join. `media_job.py` runs the gate automatically and stops on failure. Use one continuous final H.264 encoder session with no B-frame timing delay, one-second keyframes and no MP4 edit lists for Spotify delivery. Preserve audio sync when removing negative-time AAC priming packets. A metadata-only repair is insufficient if configurations change or the platform still rejects it: E002's first such repair passed color-only checks but Josh reported the same rejection. Do not hand it off again based only on those checks. Preserve originals and verify the exact full replacement, duration, audio, captions and chapters. Convert genuinely different color spaces instead of relabeling them. Josh required this prevention after repeat Spotify failures on 2026-09-30; local QC does not establish platform acceptance.

Default package: complete versioned 1080p master, audio master when requested/appropriate, corrected SRT or VTT timed to the final export, chapters, source/claim register, edit log and reproducible EDL, graphics/cue list, and QC/release-status report. Include title/thumbnail/description drafts if “publish-ready package” is requested. Use the release skill if installed; otherwise apply the brand and source checks directly.

## Accurate completion language

- **Rendered / technically checked:** export exists and measured checks are recorded.
- **Ready for host review:** complete package, with any outstanding factual/personal/subjective checks named.
- **Ready to publish:** required checks and actual host approval are recorded for this exact version; no unresolved blocking claims, rights, or export problems.
- **Published:** only after an authorized publication action and visible confirmation.

“Publish-ready” is not automatic authorization to upload, post, or send messages. If host approval is still needed, finish all authorized production first and present the concrete complete cut for approval. Don't leave a half-built export solely because approval will eventually be needed. Do not invent approval or call sampling continuous review.
