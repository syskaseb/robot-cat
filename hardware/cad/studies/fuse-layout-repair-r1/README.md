# Working fuse mount replacement, T251

One diagnostic Deck replacement, quantity1, NOT an additional print or selected
R5 part. Preserves its native parent and adds eight fully constrained4x2mm
slots for four2.5mm T18R ties. Old unused F_PWM holes remain deliberately.
F_HP now plans to hang beneath Deck using existing four slots, avoiding the
current top P_REAR reservation. F_PWM gets a whole50x6x6mm insulated-pigtail
design allocation beneath Deck, closer to P_REAR. Neither box is measured hardware.

PETG, same flat orientation as parent, nominal230x190mm plate with5mm brim
per side. No nozzle/layer profile invented. Check slot bridges/edges and
old-hole ligaments in phase2 slicing and print samples. Native geometry and
mesh checks do not qualify creep, loads or actual cable clamps.

Bench assembly with all supplies removed: make and insulate the pigtail using
the selected RNF100 sleeves. Two ties at X44/56 support its body, two at X28/72
restrain insulated conductors independently; all four use Y-28/-18 slot pairs.
Keep locks above Deck in the allocated region, not inside slots. Use no glue
as sole wire restraint. F_HP holder uses its original four slots under Deck.
The exact lock height, fuse leads and slots need delivered-part fit.

Circuit remains P_REAR.4 -> XP01(0.5mm2, entire unfused path<=50mm) ->
F_PWM2420.1A -> XP02 -> L78L05ACZ pin3. No motor power on PWM5.
Actual P_REAR cavity/entry direction, route/bends, underside chassis/battery,
F_HP insulated leads, cover and assembled populated wiring remain OPEN.
Do not select this part in R5 or claim Phase1 finished before these are resolved.
No power, purchases or physical PASS. Old top F_HP(55,70) proposal discarded
because two new slot locations lacked Deck material; do not resurrect it.
