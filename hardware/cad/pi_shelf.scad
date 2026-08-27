// Półka pod Raspberry Pi 5 + AI HAT+. Hole pattern VERIFIED against the
// official Raspberry Pi Ltd mechanical drawing (RP-008347-DS-1): 58x49mm,
// M2.5, Ø2.7mm holes. Board outline is 85x58mm per the same drawing - the
// shelf is sized with a margin around that.
//
// Plain clearance holes, not printed bosses: montaz.pdf's parts list
// already has M2,5 standoffs to buy for this - use those between the shelf
// and the Pi board rather than threading into printed plastic.
//
// Corner tabs are generic M3 through-holes, not tied to a specific frame
// position: zip-tie or screw the shelf to the trunk_frame's cross braces
// wherever it lands clear of the servo pads and near its own converter -
// per montaz.pdf, that means away from the corners where ID1 sits, close to
// the 5V/5A line, with clearance above for the Active Cooler.
include <params.scad>
include <helpers.scad>

plate_l = 95;
plate_w = 68;

module pi_shelf() {
    difference() {
        translate([-plate_l / 2, -plate_w / 2, 0]) cube([plate_l, plate_w, wall]);
        translate([0, 0, -0.1]) bolt_holes(pi_hole_x, pi_hole_y, pi_hole_d, wall + 0.2);
        for (sx = [-1, 1]) for (sy = [-1, 1])
            translate([sx * (plate_l / 2 - 8), sy * (plate_w / 2 - 8), -0.1])
                cylinder(d = 3.4, h = wall + 0.2);
    }
}

pi_shelf();
