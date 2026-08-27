// Segment goleni (calf_link). From the knee servo's horn (ID3, drives this
// part) to the paw. Unpowered - no servo at the far end, which is why this
// segment is light: 37g in the mass budget against the thigh's 109g.
// 110mm axle-to-paw-centre - VERIFIED, must equal calf_length in leg_ik.py.
//
// The far end is a stub with a single insert, not a bracket: the paw pad
// bolts on with one M3 screw so it stays "wymienna, nie klejona" per
// montaz.pdf - a wearing part, replaced without reprinting the leg.
include <params.scad>
include <helpers.scad>

spine_w = calf_spine[0];
spine_h = calf_spine[1];
stub_h = wall * 2;

module calf_segment() {
    union() {
        horn_plate(wall);
        translate([0, 0, calf_length - stub_h]) insert_boss(stub_h);
        translate([-spine_w / 2, -spine_h / 2, wall - 1])
            cube([spine_w, spine_h, calf_length - stub_h - wall + 2]);
    }
}

calf_segment();
