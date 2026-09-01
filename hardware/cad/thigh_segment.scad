// Segment uda (thigh_link). Runs from the thigh servo's horn (ID2, drives
// this part) to the knee servo's body, bolted on through its own case screws at the far end. 110mm axle-to-axle - VERIFIED, must equal thigh_length in
// leg_ik.py or the gait commands feet the leg cannot reach.
include <params.scad>
include <helpers.scad>

spine_w = thigh_spine[0];
spine_h = thigh_spine[1];

// Both joints this segment touches - thigh pitch at z=0, knee pitch at
// z=thigh_length - turn about a LATERAL axis, perpendicular to the segment.
// A plate bolts flat to a servo, so its normal is that servo's output axis:
// both plates therefore face sideways, not along the leg. They used to face
// along +Z, which would have made both joints twist about the leg instead of
// bending it.
//
// hand: +1 puts the servos on the +Y side, -1 on -Y. The plates only sit on
// one side, so the part is handed - print two of each, not four of one. A
// clevis straddling the servo would restore a single part (the ST3215 is
// dual-shafted, and joint_cap already bolts to the idle face) but that is a
// redesign, not this fix.
module thigh_segment(hand = 1) {
    ry = hand > 0 ? -90 : 90;   // maps a plate's own +Z normal onto hand * Y
    // Seat each plate on the spine's outer face, overlapping it by 1mm to
    // keep the union manifold. Sunk flush the plate would be buried inside
    // the spine and the servo would have nothing to bolt against.
    off = hand * (spine_h / 2 - 1);
    union() {
        translate([0, off, 0]) rotate([ry, 0, 0]) horn_plate(wall);
        translate([0, off, thigh_length]) rotate([ry, 0, 0]) case_plate(wall);
        translate([-spine_w / 2, -spine_h / 2, 0])
            cube([spine_w, spine_h, thigh_length]);
    }
}

thigh_segment();
