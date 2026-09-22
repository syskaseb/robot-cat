---
name: robot-cat-electronics
description: Review robot-cat purchased electronics placement, wiring, power budgets or future KiCad ECAD/MCAD integration. Use for electrical integration, not generic software work.
---

# Electronics integration

Read `hardware/electronics/README.md`, mechanical status and the relevant
supplier references under `hardware/reference/`. Resolve exact board revision.

- Keep measured, supplier and assumed dimensions separate. A STEP model of a
  board does not guarantee its revision, connector mating space or cable bend.
- Document supply rails, peak and continuous loads, converter derating, wiring,
  fuses, polarity, grounding and thermal limits. Do not parallel converter
  outputs without an explicitly supported design; AUX and main 5 V are separate.
- Never equate servo stall torque with sustainable running torque or current.
  Use measured/guaranteed data; retain unknowns and worst-case assumptions.
- Mount through actual holes with proper support and insulation. Check assembly
  order, tool access, connector insertion/removal, strain relief and ventilation.
- If editable KiCad sources exist, use ERC/DRC and StepUp/STEP exchange for the
  relevant revision. Do not invent a schematic from an imported mechanical STEP.

Summarize verified interfaces and unresolved bench checks. Model work does not
authorize energizing hardware, buying parts or accepting electrical safety.
