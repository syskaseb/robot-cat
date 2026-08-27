// Segment uda (thigh_link). Runs from the thigh servo's horn (ID2, drives
// this part) to the knee servo's body, bolted on via the downloaded bracket
// at the far end. 110mm axle-to-axle - VERIFIED, must equal thigh_length in
// leg_ik.py or the gait commands feet the leg cannot reach.
include <params.scad>
include <helpers.scad>

spine_w = 14;
spine_h = 10;

module thigh_segment() {
    union() {
        horn_plate(wall);
        translate([0, 0, thigh_length - wall]) bracket_plate(wall);
        translate([-spine_w / 2, -spine_h / 2, wall - 1])
            cube([spine_w, spine_h, thigh_length - 2 * wall + 2]);
    }
}

thigh_segment();
