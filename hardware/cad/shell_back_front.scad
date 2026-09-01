// Grzbiet, przod. Top skin from the midpoint forward, including the withers
// and the base of the neck. Print standing on the x=0 cut face: the section
// changes slowly along the body, so in that orientation nothing overhangs.
include <shell_lib.scad>

module shell_back_front() { body_panel(top = true, fore = true); }

shell_back_front();
