# Disk cleanup — October 3, 2026

Josh requested freeing space, especially outdated podcast temporary files. Free space on the Data volume increased from about 3.7 GiB to 9.6 GiB while podcast rendering continued. No measured application-speed improvement is claimed.

## Removed temporary files

- 151 old hash-named El Cruce render-cache MOVs: 2.163 GiB logical, from `edit/codex-review-2026-10-02/intermediate/`.
- 11 assembled Agents audio-cache WAVs: 1.239 GiB, from `edit/codex-proposed-cut-2026-10-03/work/`.
- Unused Spotify playback-cache entries, Dia HTTP/code-cache entries, and the August Dia installer-cache files: 2.395 GiB inventoried bytes now absent after cleanup.

The total is approximately 5.797 GiB of logical temporary-file bytes. Actual free-space change differs because APFS allocation and ongoing render output change concurrently. Recent files, files open by processes, changed candidates and OS-protected entries were skipped. Six cache entries remained protected or in use.

## Preserved and verified

All versioned episode exports and comparison previews, originals, current deliverables, transcripts, edit manifests, captions, source/research/context records, reusable assets and other-agent folders remain. Both active production folders were excluded. All 190 media entries inventoried outside the cleanup roots remain present; the sole metadata change was the actively growing El Cruce v8 render.

Retained `.done` segment descriptions, render recipes and original recordings permit rebuilding the removed podcast caches. Removed intermediates are not themselves backed up. The existing completed-work recovery ZIP remains unchanged.

## Receipts

- `cleanup-plan.json`: exact candidate inventory, original size/inode/mtime, protected-media inventory and disk baseline.
- `podcast-receipt.json`: 162 successful podcast temporary-file deletions.
- `caches-receipt.json`: cache deletions, skipped entries and reconciliation of the first cache pass, which stopped on one OS permission error. Its missing candidates are labeled separately from successful deletions in the second pass.
- `protected-media-verification.json`: media-preservation check using inode/size/mtime, not a new full-file hash pass.

No original source, cloud file, published upload, application preference, browser history, login or active job was deleted or changed by this cleanup. The currently pending Dia update cache was retained; only the August installer-cache subtree was eligible.
