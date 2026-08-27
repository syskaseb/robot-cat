// Czaszka. The top of the head: brow, cheeks, ear sockets, both eye bores,
// and the bulkhead that carries the camera. Cut just below the eye line so
// the whole face opens - the split follows the cheekbone, where a real cat
// has a fur boundary anyway, so the seam reads as marking, not as a crack.
//
// The camera lives HERE and not in the removable jaw, because the eye it
// looks through is at z = +6 and the split is at z = -6: the optics and the
// hole they aim at have to be in the same piece or the aim moves every time
// the head is opened.
//
// Print brow-down. In that orientation the eye bores, the ear sockets and
// the bulkhead's own holes are all vertical, and nothing needs support.
include <shell_lib.scad>

bulkhead_x = 1;         // face plate, one lens length behind the eyes
bulkhead_t = 3;

// Camera Module 3: 25 x 24mm board, four M2 holes on a 21 x 12.5mm
// rectangle, per the Raspberry Pi mechanical drawing. The illuminator is a
// round module and gets a pair of side lugs instead.
cam_hole_x = 21;
cam_hole_y = 12.5;

// Cut through at_ear() - the same transform cat_assembly uses to place the
// printed ear - so the socket and the plug cannot drift apart.
module ear_socket() {
    for (sy = [-1, 1])
        at_ear(sy)
            translate([0, 0, -ear_tang / 2 + 2])
                cube([ear_w * 0.6, ear_t + 0.35, ear_tang + 6], center = true);
}

// A plate spanning the whole skull just behind the eyes. Spanning it fully
// is what makes it stiff and what connects it to both side walls; the
// central window keeps the mass off and lets the wiring through.
module bulkhead() {
    difference() {
        intersection() {
            head_form(0);
            translate([bulkhead_x, -100, head_split_z]) cube([bulkhead_t, 200, 200]);
        }
        // central window
        translate([bulkhead_x - 1, 0, 4])
            cube([bulkhead_t + 2, 20, 26], center = true);
        // sight lines for both eyes
        for (sy = [-1, 1])
            translate([bulkhead_x - 1, sy * eye_spacing / 2, eye_z])
                rotate([0, 90, 0]) cylinder(d = cam_bore_d, h = bulkhead_t + 2);
        // camera board holes behind the cat's left eye
        translate([0, eye_spacing / 2, eye_z])
            for (sy = [-1, 1], sz = [-1, 1])
                translate([bulkhead_x - 1, sy * cam_hole_x / 2, sz * cam_hole_y / 2])
                    rotate([0, 90, 0]) cylinder(d = 1.9, h = bulkhead_t + 2);
        // illuminator lugs behind the right eye
        translate([0, -eye_spacing / 2, eye_z])
            for (sy = [-1, 1])
                translate([bulkhead_x - 1, sy * 13, 0])
                    rotate([0, 90, 0]) cylinder(d = 2.4, h = bulkhead_t + 2);
    }
}

module head_upper() {
    union() {
        difference() {
            intersection() {
                difference() {
                    head_form(0);
                    head_form(skin);
                }
                translate([-100, -100, head_split_z]) cube(200);
            }
            for (sy = [-1, 1])
                at_eye(sy) rotate([0, 90, 0])
                    cylinder(d = eye_d, h = 40, center = true);
            ear_socket();
        }
        bulkhead();
    }
}

head_upper();
