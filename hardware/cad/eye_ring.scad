// Pierscien oka, x2. The lit ring around each eye.
//
// On the concept render the eyes are the strongest feature on the whole
// robot, and the ring is most of why: it separates the iris from the black
// of the face. Print it in translucent filament and back-light it with a
// small LED, or in a contrasting colour and leave it unlit - either reads
// far better than a bare bore.
//
// It is a CURVED washer, not a flat one: cut as the shell between the skin
// and a copy of it eye_ring_depth in, so it beds onto the face instead of
// rocking on a flat spotface that would break through the cheek.
//
// Print recess-side down. No support.
include <shell_lib.scad>

rotate([0, -90, 0]) translate([-eye_x, -eye_spacing / 2, -eye_z]) eye_ring(1);
