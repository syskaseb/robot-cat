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

// Horn-side bolt circle, holes along Z, through a slab of thickness h.
// MEASURED: four holes on one circle of radius 7.0, at 45/135/225/315 - see
// measure/README.md. The central bore clears the horn's own hub.
module horn_bolt_circle(h) {
    for (a = [45, 135, 225, 315]) rotate([0, 0, a])
        translate([horn_bolt_r, 0, -0.1]) cylinder(d = horn_bolt_d, h = h + 0.2);
    translate([0, 0, -0.1]) cylinder(d = horn_hub_d, h = h + 0.2);
}

// A round plate carrying the horn bolt circle, face normal along Z, sitting
// at z=[0,h]. This is what a leg segment bolts to a servo's rotating horn.
// Diameter clears the servo's own raised collar so the plate seats on the
// horn, not on the case.
module horn_plate(h) {
    difference() {
        cylinder(d = servo_boss_d + 2 * wall, h = h);
        horn_bolt_circle(h);
    }
}

// A plate that bolts to the servo's CASE, using the four case screws. The
// servo's own axis sits at x=0 here, so this plate lines up with horn_plate
// on the other side of the joint. Screws go in along Z.
// MEASURED positions - see measure/README.md.
module case_plate(h) {
    xs = [for (x = case_screw_x_used) x - servo_axis_x];
    difference() {
        translate([min(xs) - 6, -case_screw_y - 5, 0])
            cube([max(xs) - min(xs) + 12, 2 * case_screw_y + 10, h]);
        for (x = xs) for (sy = [-1, 1])
            translate([x, sy * case_screw_y, -0.1])
                cylinder(d = case_screw_d, h = h + 0.2);
    }
}

// The ST3215 body pocket: servo drops in from the open top, its case (not
// the gearbox) bearing on the lip. Origin is the servo's OUTPUT AXIS, not
// the case centre, so a pocket lines up with the joint it drives.
module servo_pocket(depth) {
    l = servo_l + 2 * servo_fit;
    w = servo_w + 2 * servo_fit;
    translate([-servo_axis_x - l / 2, -w / 2, 0]) cube([l, w, depth + 0.1]);
}
