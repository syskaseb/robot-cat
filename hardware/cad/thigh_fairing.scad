// Oslona uda, x4. A C-section that snaps over the thigh segment's spine and
// turns a 14 x 10mm bar into the rounded limb the reference image shows.
//
// It clips rather than bolts, and it is deliberately short of the end plates
// at both ends: the joint caps cover those, and leaving a gap means the
// fairing never fouls a horn screw.
include <shell_lib.scad>

spine_w = thigh_spine[0];   // params.scad, shared with the segment
spine_h = thigh_spine[1];
fair_len = (thigh_length) - 2 * limb_gap - housing_d / 2;

module thigh_fairing() { limb_fairing(spine_w, spine_h, fair_len, limb_d_thigh[0], limb_d_thigh[1]); }

thigh_fairing();
