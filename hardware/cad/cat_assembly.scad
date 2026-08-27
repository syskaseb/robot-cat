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
use <joint_cap.scad>
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

body_col = [0.10, 0.10, 0.11];
trim_col = [0.17, 0.17, 0.19];
struct_col = [0.30, 0.30, 0.33];
eye_col = [0.85, 0.64, 0.13];

module skin() {
    color(body_col) {
        shell_back_front();
        shell_back_rear();
        shell_belly_front();
        shell_belly_rear();
    }
}

// A joint cap on the outer face of a joint, facing away from the body.
module cap_at(sy, out) {
    color(trim_col)
        translate([0, sy * out, 0])
            rotate([sy > 0 ? -90 : 90, 0, 0]) joint_cap();
}

module one_leg(sx, sy) {
    translate([sx * hip_x, sy * hip_y, 0])
        rotate([sy * stand_hip, 0, 0]) {
            cap_at(sy, 4);
            translate([0, sy * hip_offset, 0])
                rotate([0, stand_thigh, 0]) {
                    // Fairings run along +Z in their own file; the segments
                    // hang downward here, so each is flipped and pulled back
                    // from the end plates the joint caps already cover.
                    // the structural segment, and the fairing over it
                    color(struct_col)
                        rotate([0, 180, 0]) thigh_segment();
                    color(trim_col)
                        translate([0, 0, -13]) rotate([0, 180, 0]) thigh_fairing();
                    translate([0, 0, -thigh_length]) {
                        cap_at(sy, 14);
                        rotate([0, stand_knee, 0]) {
                            color(struct_col)
                                rotate([0, 180, 0]) calf_segment();
                            color(trim_col)
                                translate([0, 0, -16]) rotate([0, 180, 0]) calf_fairing();
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
    color(eye_col)
        for (sy = [-1, 1])
            translate([eye_x + 2, sy * eye_spacing / 2, eye_z])
                rotate([0, 90, 0]) cylinder(d = eye_d - 2, h = 3);
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

skin();

// The neck leaves the chest at neck_rise, the collar follows it, and the
// head is levelled again at the far end and then dropped by head_droop.
// Without that second rotation the head points at the ceiling.
translate(neck_pivot) rotate([0, -neck_rise, 0]) {
    color(trim_col) rotate([0, 90, 0]) neck_collar();
    translate([neck_reach, 0, 0])
        rotate([0, neck_rise + head_droop, 0]) head_assembly();
}

translate(tail_pivot) rotate([0, -(90 - tail_rise), 0]) tail_assembly();

for (sx = [-1, 1], sy = [-1, 1]) one_leg(sx, sy);
