// VISUALISATION / PRINT PLATE - not a single part. All eleven tail segments
// laid out in a row, ready to send to the slicer in one job.
include <shell_lib.scad>
use <tail_segment.scad>

for (i = [0 : tail_n - 1])
    translate([i * (tail_root_d + 4), 0, 0])
        tail_segment(i);
