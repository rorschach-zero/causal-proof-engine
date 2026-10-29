# Import note: original research package

| Field | Value |
|---|---|
| Source file | `CPE_Forschungspaket_2026-10-16.zip` (uploaded 2026-10-16, upload id prefix `c3ead589`) |
| ZIP SHA-256 | `dc69e2a7bf903547806f1dca38a2bbdbe04595894ae27d79844632341d986415` |
| ZIP size | 249752 bytes |
| Extracted entries | 72 files in `CPE_Forschungspaket_2026-10-16/` (71 listed in `MANIFEST.sha256` plus the manifest itself) |
| Manifest check | `sha256sum -c MANIFEST.sha256`: 71/71 OK, no missing or extra files |
| Safety checks | no symlinks, no absolute paths, no path traversal, no credential-like literals found |
| Imported by | Claude Code session on 2026-10-16, branch `research/claude-handoff` |

## Rules for this directory

- **Verbatim and read-only.** Nothing under `CPE_Forschungspaket_2026-10-16/` was edited, reformatted,
  translated or reordered. It is the source of record for the original research. Corrections, critiques and
  revisions live in `research/*.md`, never here.
- The sub-tree `08_Anhang/Referenz_Code_Vorschlaege_NICHT_IMPLEMENTIEREN/` is **reference evidence, not
  project code**. It is excluded from project tooling (lint, tests, packaging). Do not import from it.
- Re-verify integrity at any time with `cd CPE_Forschungspaket_2026-10-16 && sha256sum -c MANIFEST.sha256`.
