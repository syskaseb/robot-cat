---
name: robot-cat-petg
description: Review or design robot-cat PETG printed parts for fit, assembly, load direction and a 256 mm cubic printer. Use for printable mechanical changes and print readiness.
---

# PETG manufacturing review

Read the current mechanical status and `hardware/manufacturing/PETG.md`.
All new printed robot parts use PETG; purchased components retain their materials.

- Check each separate print in its proposed orientation against 256 x 256 x
  256 mm, including brim/support allowance. A bounding-box fit alone is not a
  slicer or toolpath validation.
- Evaluate wall continuity, layer-direction tension, screw bearing area, bolt
  clamp loads, stress concentrations and long-term creep. Do not claim strength
  from an isotropic material preset or material colour.
- Use the exact insert/screw/bearing supplier dimensions. Clearance, press fit
  and heat-set holes need calibration coupons on the actual printer and filament;
  nominal CAD clearance is not a measured production fit.
- Record orientation, support contact, nozzle/layer assumptions and postprocessing.
  Keep unset printer/profile information explicit instead of inventing it.
- Check tool access and assembly sequence as well as static intersections.
  A watertight STL does not prove printable walls or functional mounting.

Return measured geometry checks, physical tests still required and an explicit
readiness status. Do not promote a prototype to print-approved with open gates.
