// hip_link. The short lateral offset from the hip/roll servo's horn (ID1)
// to the thigh/pitch servo's body (ID2, bolted on through its own case screws). 25mm - VERIFIED, equals hip_offset in leg_ik.py.
include <params.scad>
include <helpers.scad>

spine_w = 12;
spine_h = 9;

// This link is the one place where the two joint axes are PERPENDICULAR, so
// only one of its plates moves:
//
//   case_plate - the thigh servo's body. That joint turns about the lateral
//     axis, which is the same direction this link spans, so its normal is
//     already right along +Z. Unchanged.
//   horn_plate - the roll servo's horn. Roll turns about the fore-aft axis,
//     perpendicular to the span, so this plate faces along local X. It used
//     to face along +Z like the other one, which would have needed the roll
//     servo mounted at ninety degrees to where it actually sits.
module hip_link() {
    union() {
        // seated on the spine's fore face, overlapping 1mm - see thigh_segment
        translate([spine_w / 2 - 1, 0, 0]) rotate([0, 90, 0]) horn_plate(wall);
        translate([0, 0, hip_offset - wall]) case_plate(wall);
        translate([-spine_w / 2, -spine_h / 2, 0])
            cube([spine_w, spine_h, hip_offset - wall + 1]);
    }
}

hip_link();
