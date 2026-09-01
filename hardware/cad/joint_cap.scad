// Kapturek stawu, x8. The round disc over every hip and knee.
//
// This is the strongest visual signature in the reference image and it is
// nearly free: it hides the horn screws and the gap between two segments,
// and it costs four grams. It bolts to the servo's IDLE face - the one
// opposite the horn - using the same measured 4 x M2.5 on a 14.00mm circle,
// which is why the servo being dual-shafted is worth knowing about.
//
// Print flat, dome up. No support.
include <shell_lib.scad>

module joint_cap() {
    difference() {
        union() {
            // dome
            intersection() {
                scale([1, 1, 0.42]) sphere(d = cap_d);
                cylinder(d = cap_d, h = cap_h + 1);
            }
            // rim, so the cap sits proud of the segment like a hubcap
            cylinder(d = cap_d, h = 1.6);
        }
        // hollow it out down to the wall thickness
        translate([0, 0, -0.1])
            intersection() {
                scale([1, 1, 0.42]) sphere(d = cap_d - 2 * skin);
                cylinder(d = cap_d - 2 * skin, h = cap_h);
            }
        // the measured bolt circle
        for (a = [45, 135, 225, 315]) rotate([0, 0, a])
            translate([horn_bolt_r, 0, -1]) cylinder(d = horn_bolt_d, h = 10);
        translate([0, 0, -1]) cylinder(d = horn_hub_d, h = 10);
    }
}

joint_cap();
