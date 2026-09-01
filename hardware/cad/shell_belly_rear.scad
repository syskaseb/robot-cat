// Brzuch, tyl. Carries the speaker grille: the 100 x 45mm driver from
// plan-zakupowy.pdf fires downward from here, behind the front legs and
// clear of the battery bay.
include <shell_lib.scad>

speaker_x = -60;

module shell_belly_rear() {
    difference() {
        body_panel(top = false, fore = false);
        translate([speaker_x, 0, -body_hh - 5])
            grille(n = 9, len = 86, pitch = 5.0, w = 2.6, depth = 40);
    }
}

shell_belly_rear();
