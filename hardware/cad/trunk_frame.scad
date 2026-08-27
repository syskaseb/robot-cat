// Rama tułowia. Not a shell - a ladder frame: two side rails holding the
// four hip/roll servo (ID1) mounts at the VERIFIED positions from
// cat.urdf.xacro (hip_x=110, hip_y=55, so 220x110mm), joined by three
// cross braces for rigidity. This is the same construction real STS3215
// quadrupeds use (OpenRoboticDog's body_side/body_plate/body_front_back),
// not a sculpted box - the skin is a later, separate, cosmetic layer.
//
// The four corner pads use the same ADJUSTABLE bracket flange as hip_link
// and thigh_segment (see params.scad) - confirm hole spacing AND which face
// the bracket actually mates on, against the real downloaded bracket,
// before printing the final set. The pad's position (hip_x, hip_y) is
// VERIFIED and does not change.
include <params.scad>
include <helpers.scad>

rail_w = 16;
rail_h = 10;
pad_h = wall;

module corner_pad() {
    // outward-facing mount: bracket screws on from outside the rail
    rotate([90, 0, 0]) bracket_plate(pad_h);
}

module side_rail(y_sign) {
    translate([-hip_x, y_sign * hip_y - rail_w / 2, -rail_h / 2])
        cube([2 * hip_x, rail_w, rail_h]);
    for (sx = [-1, 1])
        translate([sx * hip_x, y_sign * hip_y + y_sign * (pad_h - 0.5), 0])
            corner_pad();
}

module cross_brace(x) {
    translate([x - wall / 2, -hip_y + rail_w / 2, -rail_h / 2])
        cube([wall, 2 * (hip_y - rail_w / 2), rail_h]);
}

module trunk_frame() {
    union() {
        side_rail(1);
        side_rail(-1);
        cross_brace(0);
        cross_brace(-hip_x * 0.6);
        cross_brace(hip_x * 0.6);
    }
}

trunk_frame();
