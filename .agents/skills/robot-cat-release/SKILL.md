---
name: robot-cat-release
description: Package or verify robot-cat hardware checkpoints and releases with source hashes, BOM revisions and readiness gates. Use for hardware versioning, release preparation or print handoff.
---

# Hardware release

Read `hardware/MODULAR_DESIGN.md`, `hardware/releases/README.md` and current
mechanical status. Check the branch and remote: mechanical work belongs to
`syskaseb/robot-cat`, not the other owner's origin.

- Use stable master names and Git history; preserve prior checkpoints. Track
  part identity/revision separately from whole-robot version and readiness.
- Manifest all required source documents, external dependencies, evidence and
  exports with relative paths and SHA-256. Include tool/addon versions and
  compatibility notes. Never resolve a release dependency as unspecified latest.
- Run `python tools/cad/release_check.py MANIFEST` from the repo. Use
  `--require-print-ready` for a print handoff; that must fail on unknown/open
  required gates. Hash validity alone proves no mechanical safety.
- Inspect changed geometry and rerun affected tests. Do not reuse a green report
  from different file hashes or turn a failed strict audit into a passed release
  by renaming its scope. State exactly what limited prototype checks passed.
- A checkpoint may retain explicit failures. A production/print release may not
  waive required fit, material, load, wiring, assembly and geometry checks.

Create/push immutable release tags only when requested. Do not silently publish
files, order parts or rewrite history as a side effect of preparing a manifest.
