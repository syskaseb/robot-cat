// Ucho, x2. A dished triangle on a tang that plugs into the skull.
//
// The dish is the whole point. A flat triangle reads as a fin; it is the
// concave inner surface catching a different shade that makes the shape read
// as an ear. So the blade is a solid lens with a second, smaller lens
// subtracted from its front face - not a hollow frame.
//
// Print flat on the back face, dish up. No support, and the tang prints as a
// simple rib off the bottom edge.
include <shell_lib.scad>

module ear_lens(inset = 0) {
    scale([1, ear_t / 12, 1])
        hull() {
            translate([-ear_w / 2 + 6, 0, 6]) sphere(r = 6 - inset);
            translate([ ear_w / 2 - 6, 0, 6]) sphere(r = 6 - inset);
            translate([0, 0, ear_h - 5]) sphere(r = 5 - inset);
        }
}

module ear() {
    union() {
        difference() {
            ear_lens(0);
            // the dish, shifted forward so it opens on one face only and
            // leaves a back wall rather than punching through
            translate([0, ear_t * 0.62, 1.5]) ear_lens(2.4);
        }
        // tang - deliberately a touch under the socket so it can be pushed
        // home by hand and pulled out again
        translate([0, 0, -ear_tang / 2 + 2])
            cube([ear_w * 0.58, ear_t, ear_tang + 4], center = true);
    }
}

ear();
