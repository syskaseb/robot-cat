// VISUALISATION ONLY - not a part to print. Trunk frame plus all four legs,
// straight and extended, positioned at the real hip corners (hip_x, hip_y)
// from params.scad. Servo placeholders as before - orientation is cosmetic,
// not verified clearance. This is the actual CAD, not illustration.
include <params.scad>
include <helpers.scad>
use <trunk_frame.scad>
use <hip_link.scad>
use <thigh_segment.scad>
use <calf_segment.scad>
use <paw_pad.scad>

module servo_block() {
    color("orange", 0.55)
        translate([-servo_l / 2, -servo_w / 2, -1])
            cube([servo_l, servo_w, servo_h]);
}

module leg(x_sign, y_sign) {
    translate([x_sign * hip_x, y_sign * hip_y, 0])
        rotate([180, 0, 0])           // hang the chain downward from the corner
        rotate([0, 0, y_sign > 0 ? 90 : -90]) {
        rotate([0, -90, 0]) servo_block();
        color("SteelBlue") hip_link();
        translate([0, 0, hip_offset]) rotate([0, -90, 0]) servo_block();
        translate([0, 0, hip_offset]) color("SteelBlue") thigh_segment();
        translate([0, 0, hip_offset + thigh_length])
            rotate([0, -90, 0]) servo_block();
        translate([0, 0, hip_offset + thigh_length])
            color("SteelBlue") calf_segment();
        translate([0, 0, hip_offset + thigh_length + calf_length])
            color("DimGray") paw_pad();
    }
}

color("SteelBlue") trunk_frame();
leg(1, 1); leg(1, -1); leg(-1, 1); leg(-1, -1);
