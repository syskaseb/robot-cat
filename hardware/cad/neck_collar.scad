// Kolnierz szyi. Bridges the gap between the body skin and the head, over
// the two neck microservos, and hides them without restricting the pan and
// tilt range the urdf allows (+/-0.6 rad pan, -0.3..+0.5 tilt).
//
// Stacked rings rather than a smooth tube: a smooth tube has to be either
// loose enough to look wrong or tight enough to bind, whereas rings can
// overlap and slide past each other as the head turns.
//
// Sized to stand proud of BOTH the body opening and the skull. An earlier
// version at 34mm disappeared under the head, which on the concept render is
// one of the clearest features of the whole robot.
include <shell_lib.scad>

neck_collar_form();
