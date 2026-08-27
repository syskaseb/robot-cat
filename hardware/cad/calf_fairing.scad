// Oslona goleni, x4. Same idea as the thigh fairing over the smaller calf
// spine. Shorter, because the paw pad takes the last stretch.
include <shell_lib.scad>

spine_w = calf_spine[0];   // params.scad, shared with the segment
spine_h = calf_spine[1];
fair_len = 78;

module calf_fairing() { limb_fairing(spine_w, spine_h, fair_len); }

calf_fairing();
