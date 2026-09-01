// VISUALISATION ONLY - not a part to print.
//
// The whole cat with its skin on, in the standing pose, so the proportions
// can be judged before anything goes to a printer. Joint angles here are the
// neutral stand, not a gait pose; leg_assembly.scad is still the file for
// checking that the segment interfaces line up.
//
// Render a view with, for example:
//
//   openscad -o side.png --imgsize=1400,900 --projection=o \
//            --camera=0,0,0,90,0,90,700 cat_assembly.scad

include <shell_lib.scad>
use <shell_back_front.scad>
use <shell_back_rear.scad>
use <shell_belly_front.scad>
use <shell_belly_rear.scad>
use <head_upper.scad>
use <head_lower.scad>
use <ear.scad>
use <neck_collar.scad>
use <joint_housing.scad>
use <eye_lens.scad>
use <eye_ring.scad>
use <ankle_link.scad>
use <thigh_fairing.scad>
use <calf_fairing.scad>
use <tail_segment.scad>
use <thigh_segment.scad>
use <calf_segment.scad>
use <hip_link.scad>

// The stand pose, from GaitGenerator.stand(): stance_height 0.16 with the
// knee held near 73% of full reach. Angles in degrees, converted from the
// radians the gait code works in.
stand_thigh = 43.0;
stand_knee = -86.0;
stand_hip = 10.3;

// Everything prints in the same black PETG. The tiny differences below are
// only so adjacent parts are distinguishable in a render - painting the
// structure light grey made the legs read as thin sticks with a bright core,
// which is not what the built cat looks like.
body_col   = [0.10, 0.10, 0.11];
trim_col   = [0.13, 0.13, 0.145];
struct_col = [0.16, 0.16, 0.175];
eye_col    = [0.88, 0.66, 0.12];
ring_col   = [0.96, 0.93, 0.72];

module skin() {
    color(body_col) {
        shell_back_front();
        shell_back_rear();
        shell_belly_front();
        shell_belly_rear();
    }
}

// The barrel over a joint. Its axis is the joint axis, so it is centred on
// the joint rather than stuck to one side of it.
module housing_at(sy) {
    color(trim_col)
        translate([0, sy * (housing_len / 2 - 6), 0])
            rotate([sy > 0 ? -90 : 90, 0, 0]) joint_housing();
}

// Inspection toggles, both off/on so the default render still shows the cat
// rather than a box of parts. Override from the command line, for example
//
//   openscad -D show_skin=false -D show_servos=true ... cat_assembly.scad
//
// to check that the structural chain closes and nothing collides.
show_skin = true;
show_servos = false;
servo_col = [0.95, 0.60, 0.10];

// A servo at the current joint. Same frame as servo_pocket() in helpers.scad:
// the origin is the OUTPUT AXIS, not the case centre, and the body hangs back
// along -Z behind the horn plate that bolts to it.
module servo_at() {
    if (show_servos)
        color(servo_col, 0.45)
            translate([-servo_axis_x - servo_l / 2, -servo_w / 2, -servo_h])
                cube([servo_l, servo_w, servo_h]);
}

module one_leg(sx, sy) {
    translate([sx * hip_x, sy * hip_y, 0])
        rotate([sy * stand_hip, 0, 0]) {
            servo_at();
            housing_at(sy);
            // The lateral bridge from the roll servo's horn to the thigh
            // servo's case. Without it the thigh appears to float the
            // hip_offset gap away from the body.
            color(struct_col)
                rotate([sy > 0 ? -90 : 90, 0, 0]) hip_link();
            translate([0, sy * hip_offset, 0])
                rotate([0, stand_thigh, 0]) {
                    servo_at();
                    // Fairings run along +Z in their own file; the segments
                    // hang downward here, so each is flipped and pulled back
                    // from the end plates the joint caps already cover.
                    // the structural segment, and the fairing over it
                    // hand = sy keeps the servo plates outboard on both
                    // sides; the parts are handed, so this is 2+2 prints.
                    color(struct_col)
                        rotate([0, 180, 0]) thigh_segment(sy);
                    color(trim_col)
                        translate([0, 0, -limb_gap - housing_d / 4])
                            rotate([0, 180, 0]) thigh_fairing();
                    translate([0, 0, -thigh_length]) {
                        housing_at(sy);
                        rotate([0, stand_knee, 0]) {
                            servo_at();
                            color(struct_col)
                                rotate([0, 180, 0]) calf_segment(sy);
                            color(trim_col)
                                translate([0, 0, -limb_gap - housing_d / 4])
                                    rotate([0, 180, 0]) calf_fairing();
                            // the fixed cosmetic wrist, over the last
                            // stretch of bare calf spine
                            color(trim_col)
                                translate([0, 0, -ankle_z - ankle_len])
                                    rotate([0, 180, 0]) ankle_form();
                            color([0.06, 0.06, 0.06])
                                translate([0, 0, -calf_length]) sphere(r = foot_radius);
                        }
                    }
                }
        }
}

module head_assembly() {
    color(body_col) { head_upper(); head_lower(); }
    color(trim_col)
        for (sy = [-1, 1]) at_ear(sy) ear();
    color(eye_col) for (sy = [-1, 1]) eye_at(sy);
    // The ring is IMPORTED, not computed. OpenSCAD's preview renderer draws
    // intersection() against an imported mesh wrong - it showed the ring as
    // the whole skull - so the assembly uses the CGAL-baked part instead.
    // Bake it with:  openscad --render -o skin/eye_ring.stl eye_ring.scad
    color(ring_col)
        for (sy = [-1, 1])
            scale([1, sy, 1])
                translate([eye_x, eye_spacing / 2, eye_z])
                    rotate([0, 90, 0]) import("skin/eye_ring.stl");
}

module tail_assembly() {
    // Each segment leans a little further than the last, which is what gives
    // the tail the upward S the reference image has.
    module chain(i) {
        if (i < tail_n) {
            rotate([0, -6 - i * 0.8, 0])
                translate([0, 0, 0]) {
                    color(trim_col) tail_segment(i);
                    translate([0, 0, tail_len / tail_n - 1]) chain(i + 1);
                }
        }
    }
    chain(0);
}

if (show_skin) skin();

// The neck leaves the chest at neck_rise, the collar follows it, and the
// head is levelled again at the far end and then dropped by head_droop.
// Without that second rotation the head points at the ceiling.
translate(neck_pivot) rotate([0, -neck_rise, 0]) {
    color(trim_col) rotate([0, 90, 0]) neck_collar_form();
    translate([neck_reach, 0, 0])
        rotate([0, neck_rise + head_droop, 0]) head_assembly();
}

translate(tail_pivot) rotate([0, -(90 - tail_rise), 0]) tail_assembly();

for (sx = [-1, 1], sy = [-1, 1]) one_leg(sx, sy);
