// Kolnierz szyi. Bridges the gap between the body skin and the head, over
// the two neck microservos, and hides them without restricting the pan and
// tilt range the urdf allows (+/-0.6 rad pan, -0.3..+0.5 tilt).
//
// Stacked rings rather than a smooth tube: a smooth tube has to be either
// loose enough to look wrong or tight enough to bind, whereas rings can
// overlap and slide past each other as the head turns.
include <shell_lib.scad>

rings = 4;
ring_h = neck_len / rings;

module neck_collar() {
    for (i = [0 : rings - 1]) {
        d = neck_d * (1 - 0.06 * i);
        translate([0, 0, i * ring_h * 0.86])
            difference() {
                cylinder(d1 = d, d2 = d - 1.5, h = ring_h);
                translate([0, 0, -0.1])
                    cylinder(d1 = d - 2 * skin, d2 = d - 1.5 - 2 * skin,
                             h = ring_h + 0.2);
            }
    }
}

neck_collar();
