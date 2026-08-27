// Zuchwa i pysk. The underside of the head, below the cheekbone seam. Plain
// shell: everything that has to be aimed lives in head_upper, so this half
// can come off without disturbing the camera.
//
// The only feature is the cable slot at the back, where the camera ribbon
// and the two servo leads leave for the neck.
include <shell_lib.scad>


module head_lower() {
    difference() {
        intersection() {
            difference() {
                head_form(0);
                head_form(skin);
            }
            translate([-100, -100, head_split_z - 200 + seam_gap / 2])
                cube(200);
        }
        translate([-34, 0, -14]) cube([14, 20, 10], center = true);
    }
}

head_lower();
