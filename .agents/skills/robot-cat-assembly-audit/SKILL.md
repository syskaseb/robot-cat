---
name: robot-cat-assembly-audit
description: Audit robot-cat physical attachments and native FreeCAD joints, including migration regressions and motion retention. Use before accepting an assembly or reporting that parts stay connected.
---

# Assembly audit

Read the current `hardware/skorupa/STATUS.md` and the target assembly manifest.
Audit physical construction and solver constraints separately.

- Account for every component and joint. Compare with the source: missing,
  duplicated or newly TEMP parts are failures unless an intentional change is
  documented. Fixed joints do not stand in for bolts or an actual load path.
- For each changed mount, check hole axes, fastener stack, thread engagement,
  access for tools, assembly order, wire/connector clearance and moving envelope.
- Check BRep validity and geometry ownership before interpreting Boolean
  intersections. Invalid legacy shells require explicit limited-scope results,
  never a blanket zero-collision/production claim.
- Exercise native solver frames and measure joint-origin gaps, fixed rotations,
  revolute-axis alignment and expected angular excursions. Test linked geometry's
  global placement as well as the wrapper that carries its joint. Restore rest
  pose even if validation fails; save only the intended development document.
- Reopen in a fresh process and relocated directory to expose stale cached
  shapes, absolute paths and missing workbench dependencies.

Distinguish kinematic animation from dynamic Gazebo trials and real hardware
tests. State the ranges actually checked; sampled poses are not swept-volume proof.
