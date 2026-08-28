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

// Only one plate here: the knee. Like the thigh, that joint bends about a
// lateral axis, so the plate faces sideways rather than along the leg - see
// the note in thigh_segment.scad. The paw stub at the far end is a plain
// insert boss and keeps its original axis, since nothing rotates there.
module calf_segment(hand = 1) {
    ry = hand > 0 ? -90 : 90;
    off = hand * (spine_h / 2 - 1);   // see the note in thigh_segment.scad
    union() {
        translate([0, off, 0]) rotate([ry, 0, 0]) horn_plate(wall);
        translate([0, 0, calf_length - stub_h]) insert_boss(stub_h);
        translate([-spine_w / 2, -spine_h / 2, 0])
            cube([spine_w, spine_h, calf_length - stub_h + 1]);
    }
}

calf_segment();
