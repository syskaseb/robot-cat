// Brzuch, przod. The chest pan. This is the panel that comes off for access,
// so it carries no fixed hardware - the speaker grille is in the rear half,
// away from the front legs.
include <shell_lib.scad>

module shell_belly_front() { body_panel(top = false, fore = true); }

shell_belly_front();
