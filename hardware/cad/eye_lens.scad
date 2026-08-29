// Soczewka oka, x2. A ball on a flange, pushed through the eye bore from
// INSIDE the skull and seating on the counterbore behind it.
//
// Inside-out is not a quirk: it is the only arrangement where the visible
// ball can be larger than the hole it shows through, which is what makes an
// eye look set into a socket rather than glued onto a face. It goes in
// before head_lower closes the head.
//
// The front is trimmed by the skull surface offset outwards by eye_bulge, so
// it stands exactly that far proud wherever the surface happens to be.
//
// Print flange down, no support. This is the one part worth a different
// material - clear or amber PETG. In the same black as the skull it reads as
// a hole, not an eye.
include <shell_lib.scad>

// brought back to the origin and laid flat for printing
rotate([0, -90, 0]) translate([-eye_x, -eye_spacing / 2, -eye_z]) eye_at(1);
