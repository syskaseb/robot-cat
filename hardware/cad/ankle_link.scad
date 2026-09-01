// Kostka, x4. The fixed cosmetic wrist between calf and paw.
//
// The concept draws a joint here. We have three servos in a leg and none of
// them is at the ankle, so this DOES NOT MOVE - it is a shaped cover that
// clips onto the bare calf spine below the calf fairing and makes the limb
// read as jointed. Calling it a joint in the CAD would be a lie the builder
// discovers at assembly.
//
// It also does real work: it covers the last stretch of bare spine, which
// was the one place the leg still looked like a rod.
//
// Print upright, mouth to the side. No support.
include <shell_lib.scad>

ankle_form();
