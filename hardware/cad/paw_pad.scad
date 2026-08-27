// Nakładka łapy. A dome that bolts onto the calf's stub with one M3 screw,
// counterbored from below so the screw head never touches the ground.
//
// Geometry only - the MATERIAL is the part that actually matters and is
// each's own choice, already covered in montaz.pdf: goły PETG measures
// mu=0.3-0.4 and both slides and clicks; print this in TPU 95A, or print it
// in PETG and dip it in Plasti Dip, or skip printing it and use a silicone
// furniture foot of about this size instead. foot_mu=1.2 in the simulation
// assumes a soft pad - the measured drift and speed numbers only hold with
// one fitted.
include <params.scad>

cut_z = foot_radius * 0.55;   // flat mating face height above centre

module paw_pad() {
    difference() {
        intersection() {
            sphere(r = foot_radius);
            translate([-foot_radius, -foot_radius, -foot_radius - 1])
                cube([foot_radius * 2, foot_radius * 2, foot_radius + 1 + cut_z]);
        }
        // M3 clearance straight through, screws up into the calf's insert
        translate([0, 0, -foot_radius - 1]) cylinder(d = 3.4, h = foot_radius * 3);
        // countersink so the screw head sits inside, not on the ground
        translate([0, 0, -foot_radius - 0.1]) cylinder(d1 = 7, d2 = 3.4, h = 4);
    }
}

paw_pad();
