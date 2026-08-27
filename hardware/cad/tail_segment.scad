// Segment ogona. One of eleven, threaded onto a single 2mm steel wire that
// runs from the tail servo to the tip. The segments are passive: they carry
// no drive, they only give the wire a shape and a taper.
//
// Which segment this is comes from `seg` on the command line, 0 at the root:
//
//     openscad -D seg=0  -o tail_00.stl tail_segment.scad
//
// tail_plate.scad lays out all eleven at once for a single print job. The
// ends are spherical so consecutive segments roll on each other instead of
// hinging on a corner - that is what lets the tail curve smoothly rather
// than kinking at every joint.
include <shell_lib.scad>

seg = 0;

seg_len = tail_len / tail_n;
function seg_d(i) = tail_root_d + (tail_tip_d - tail_root_d) * i / (tail_n - 1);

module tail_segment(i = seg) {
    d0 = seg_d(i);
    d1 = seg_d(i + 1);
    difference() {
        union() {
            cylinder(d1 = d0, d2 = d1, h = seg_len - d1 / 2);
            translate([0, 0, seg_len - d1 / 2]) sphere(d = d1);
        }
        // socket for the next segment's ball
        translate([0, 0, -0.1]) sphere(d = d0 + 0.5);
        translate([0, 0, -0.1]) cylinder(d = tail_bore_d, h = seg_len + 5);
    }
}

tail_segment();
