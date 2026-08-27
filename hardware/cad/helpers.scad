// Shared building blocks. Convention: every part's own joint-to-joint axis
// is local Z, so end plates are naturally perpendicular to it and holes bore
// straight along Z. Whole parts get rotated into the world only when placed
// into an assembly view - never inside a single part's own file.
include <params.scad>

// A boss with a heat-set-insert bore, sized to sit inside a wall.
module insert_boss(h) {
    difference() {
        cylinder(d = insert_d + wall, h = h);
        translate([0, 0, h - insert_depth])
            cylinder(d = insert_d, h = insert_depth + 0.1);
    }
}

// Four insert bosses in a rectangle, base sitting on z=0.
module bolt_pattern(x, y, h) {
    for (sx = [-1, 1]) for (sy = [-1, 1])
        translate([sx * x / 2, sy * y / 2, 0]) insert_boss(h);
}

// Clearance holes through a slab of thickness h, for the mating part.
module bolt_holes(x, y, d, h) {
    for (sx = [-1, 1]) for (sy = [-1, 1])
        translate([sx * x / 2, sy * y / 2, -0.1]) cylinder(d = d, h = h + 0.2);
}

// Horn-side bolt circle, holes along Z, through a slab of thickness h - see
// params.scad for why the fourth hole sits at a smaller radius.
module horn_bolt_circle(h) {
    for (a = [0, 90, 180]) rotate([0, 0, a])
        translate([horn_bolt_r_major, 0, -0.1]) cylinder(d = horn_bolt_d, h = h + 0.2);
    rotate([0, 0, 270]) translate([horn_bolt_r_minor, 0, -0.1])
        cylinder(d = horn_bolt_d, h = h + 0.2);
    translate([0, 0, -0.1]) cylinder(d = horn_hub_d, h = h + 0.2);
}

// A round plate carrying the horn bolt circle, face normal along Z, sitting
// at z=[0,h]. This is what a leg segment bolts to a servo's rotating horn.
module horn_plate(h) {
    d = horn_bolt_r_major * 2 + 10;
    difference() {
        cylinder(d = d, h = h);
        horn_bolt_circle(h);
    }
}

// A square plate carrying the bracket's own flange holes - ADJUSTABLE, see
// params.scad. This is what a leg segment bolts to the downloaded bracket.
module bracket_plate(h) {
    side = bracket_hole_x + 12;
    difference() {
        translate([-side / 2, -side / 2, 0]) cube([side, side, h]);
        bolt_holes(bracket_hole_x, bracket_hole_y, bracket_screw_d, h);
    }
}

// The ST3215 body pocket: servo drops in from the open top, its case (not
// the gearbox) bearing on the lip.
module servo_pocket(depth) {
    l = servo_l + 2 * servo_fit;
    w = servo_w + 2 * servo_fit;
    translate([-l / 2, -w / 2, 0]) cube([l, w, depth + 0.1]);
}
