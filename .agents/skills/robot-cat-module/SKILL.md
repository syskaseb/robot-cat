---
name: robot-cat-module
description: Design or migrate a robot-cat FreeCAD subassembly with shared mounting interfaces, editable masters and linked native assemblies. Use for this repository's mechanical CAD work, not visual-only meshes.
---

# Robot-cat module

Resolve the repository from the current worktree; never hard-code a user's path.
Read `hardware/MODULAR_DESIGN.md`, `hardware/cad/README.md` if present, and
`hardware/skorupa/STATUS.md` before choosing the current source. Check Git status.

- Preserve released/checkpoint files; use a new module or development document.
- Identify the owner of each physical part. A power mount must not own private
  copies of the chassis, shell or tail bridge. Put shared mating dimensions in
  the parameter document; published datums/axes define the module interface.
- Prefer structured FreeCAD MCP tools for interactive features and constraints.
  Use versioned scripts for migration, unsupported cross-document operations,
  repeatable exports and validation. Do not hide editable geometry in one opaque
  scripted solid when useful sketches and features already exist.
- Use one-way dependencies: parameters/references -> modules -> assembly.
  Verify external links, local/global placements, native joint references,
  recompute and close/reopen from a relocated copy. A link's existence alone
  does not prove it updates correctly.
- Test one intentional parameter change, observe every affected mating part,
  restore it and compare geometry with the baseline. Preserve inherited failures
  as failures. Stop bulk migration if the pilot changes geometry unintentionally.

Report which parts are editable, linked, inherited snapshots or temporary.
Do not claim all of the robot migrated when only the AUX pilot did.
