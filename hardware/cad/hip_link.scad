// hip_link. The short lateral offset from the hip/roll servo's horn (ID1)
// to the thigh/pitch servo's body (ID2, bolted on through its own case screws). 25mm - VERIFIED, equals hip_offset in leg_ik.py.
include <params.scad>
include <helpers.scad>

spine_w = 12;
spine_h = 9;

module hip_link() {
    union() {
        horn_plate(wall);
        translate([0, 0, hip_offset - wall]) case_plate(wall);
        translate([-spine_w / 2, -spine_h / 2, wall - 1])
            cube([spine_w, spine_h, hip_offset - 2 * wall + 2]);
    }
}

hip_link();
