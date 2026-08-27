// VISUALISATION ONLY - not a part to print. Stacks hip_link, thigh_segment
// and calf_segment in a straight line with placeholder servo boxes, to
// sanity-check that the plate interfaces actually line up end to end.
// Real joint angles depend on the gait; this is a fully extended pose.
include <params.scad>
include <helpers.scad>
use <hip_link.scad>
use <thigh_segment.scad>
use <calf_segment.scad>
use <paw_pad.scad>

module servo_block() {
    color("orange", 0.55)
        translate([-servo_l / 2, -servo_w / 2, -1])
            cube([servo_l, servo_w, servo_h]);
}

// ID1 servo (roll) - body on the trunk, horn drives hip_link
translate([0, 0, 0]) rotate([0, -90, 0]) servo_block();

color("SteelBlue") hip_link();

// ID2 servo (thigh pitch) - body bolted at the top of hip_link via bracket
translate([0, 0, hip_offset]) rotate([0, -90, 0]) servo_block();

translate([0, 0, hip_offset]) color("SteelBlue") thigh_segment();

// ID3 servo (knee) - body bolted at the far end of thigh_segment
translate([0, 0, hip_offset + thigh_length]) rotate([0, -90, 0]) servo_block();

translate([0, 0, hip_offset + thigh_length]) color("SteelBlue") calf_segment();

translate([0, 0, hip_offset + thigh_length + calf_length])
    color("DimGray") paw_pad();
