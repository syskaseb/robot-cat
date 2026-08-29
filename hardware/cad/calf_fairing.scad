// Oslona goleni, x4. Same idea as the thigh fairing over the smaller calf
// spine. Shorter, because the paw pad takes the last stretch.
include <shell_lib.scad>

spine_w = calf_spine[0];   // params.scad, shared with the segment
spine_h = calf_spine[1];
fair_len = (calf_length) - 2 * limb_gap - housing_d / 2;

module calf_fairing() { limb_fairing(spine_w, spine_h, fair_len, limb_d_calf[0], limb_d_calf[1]); }

calf_fairing();
