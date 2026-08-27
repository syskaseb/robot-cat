// Rama tułowia. Not a shell - a ladder frame: two side rails holding the
// four hip/roll servo (ID1) mounts at the VERIFIED positions from
// cat.urdf.xacro (hip_x=110, hip_y=55, so 220x110mm), joined by three
// cross braces for rigidity. This is the same construction real STS3215
// quadrupeds use (OpenRoboticDog's body_side/body_plate/body_front_back),
// not a sculpted box - the skin is a later, separate, cosmetic layer.
//
// The four corner pads bolt to the ID1 servo's own case screws, whose
// positions are MEASURED (see measure/README.md) - no downloaded bracket is
// involved any more. The pad's position (hip_x, hip_y) comes from the
// simulation model and does not change.
include <params.scad>
include <helpers.scad>

rail_w = 16;
rail_h = 10;
pad_h = wall;

// The pad's origin is the ID1 servo's OUTPUT AXIS, so it lands exactly on
// (hip_x, hip_y). The servo's case screws all sit to ONE side of that axis -
// the axis is 10.2mm in from its near end - so the pad is a flag reaching
// 35mm to one side, not a plate centred on the joint.
//
// The flag is NOT mirrored front to rear. Mirroring it would shorten the
// frame, but it would also mean the rear ID1 servos are installed spun 180
// degrees, and their commanded direction would then have to be negated in
// software. All four legs being identical is a rule this project already
// made deliberately (see CLAUDE.md), so the frame grows instead.
module corner_pad() {
    rotate([90, 0, 0]) case_plate(pad_h);
}

// How far the pad reaches back from the hip axis. The rail has to run at
// least this far past the axis to meet it - which is what sets the frame's
// overall length, and why case_screw_x_used drops the outermost screw.
pad_reach = servo_axis_x - min(case_screw_x_used) + 6;

module side_rail(y_sign) {
    translate([-hip_x - pad_reach, y_sign * hip_y - rail_w / 2, -rail_h / 2])
        cube([2 * hip_x + pad_reach, rail_w, rail_h]);
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
