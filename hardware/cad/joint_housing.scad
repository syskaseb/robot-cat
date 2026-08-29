// Obudowa stawu, x8. The barrel over every hip and knee.
//
// This replaces joint_cap, and the change is not cosmetic bookkeeping: the
// housing bolts to the servo's IDLE face using the measured 4 x M2.5 on the
// Ø14 circle, closing a yoke around the servo so the joint is carried on
// both sides instead of hanging off the horn alone. That is why it has a 4mm
// wall where the old cap had 1.8.
//
// It is also the strongest thing in the silhouette. On the reference render
// the shoulder and knee housings are as visually important as the body, and
// they are what makes each limb segment read as separate.
//
// Print open side down. No support.
include <shell_lib.scad>

joint_housing();
