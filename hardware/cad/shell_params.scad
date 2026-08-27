// ==================== cosmetic layer ====================
// The skin. Everything here is APPEARANCE, deliberately kept in its own file
// and its own namespace so that nothing structural can be changed by tuning
// how the cat looks. params.scad carries the numbers the gait and the torque
// budget depend on; this file must read them and never contradict them.
//
// The one hard constraint the skin has to respect was measured, not guessed:
// sweeping every pose the robot actually commands (walk at 0.10 m/s, full
// turn, stand, stretch, lie down), the nearest any leg part comes to the
// centreline is |y| = 84.6mm, against a body half-width of 55.5mm. That is
// 29mm of clearance, so a full-width skin never touches a leg. Only the four
// hip joints pierce it. Re-run measure/envelope.py after any gait change.

include <params.scad>

// ---- skin ----
skin = 1.8;           // cosmetic wall. Not load bearing - the ladder frame
                      // carries everything. 1.8 is three 0.6 extrusions.
seam_gap = 0.25;      // clearance on a shell-to-shell mating face
clip_d = 3.2;         // magnet / M3 boss for holding panels on

// ---- body ----
// Half-width comes straight from body_width so the skin can never quietly
// outgrow the box the torque was computed on. The vertical scale turns the
// circular stations below into the cat's egg-shaped cross-section: taller
// than wide, which montaz.pdf calls out as the thing to preserve.
body_hw = body_width / 2;              // 55.5
body_hh = body_height / 2;             // 70.5
body_z_scale = body_hh / body_hw;      // 1.27

// Stations along the spine: [x, radius, z-lift]. Radius is in circular
// space, BEFORE the vertical scale; lift is in real mm, after it. The shape
// comes mostly from the radius profile - the lifts only tilt the ends up.
//
// These are sphere CENTRES, not points on the surface: a station puts skin
// at x +/- r, not at x. Sizing them as if they were surface points is what
// makes a 300mm body come out 356mm long, so every station is checked
// against the box by measure/fit_check.py. Run it after touching this list.
// The box is 300 x 111 x 141 because that is what the torque budget and the
// gait were computed on, and the skin has to stay inside it.
body_stations = [
    [-124,  26,  12],   // tail root, lifted so the tail leaves upward
    [-106,  44,   6],   // rump, just behind the rear hips
    [ -70,  52,   1],   // waist - the shallowest part of the back
    [   0,  54.5,  0],  // midpoint
    [  70,  54.5, -1],  // ribcage, the deepest part of a cat
    [ 102,  47,   2],   // shoulder
    [ 120,  30,  12],   // base of the neck
];

// Where the skin is cut into printable pieces. The seam runs along the flank
// exactly at the hip axis (z=0 in the urdf's base_link). That is the widest
// line on the body, which makes it the one place a panel line can run
// straight without wandering across a curve - and it means each hip opening
// is a clean half-circle shared between the top and bottom panel, so either
// can be lifted off without threading it over a leg.
flank_seam_z = 0;
body_split_x = 0;     // fore/aft print split, keeps each panel under 155mm

// The urdf hangs neck_pan_joint and tail_joint off the CORNERS of the
// collision box, at z = +70.5. A rounded skin cannot reach a box corner, and
// nothing in the mass or torque budget depends on where those two decorative
// links attach - neck_mass is deliberately near-zero and the tail is trim.
// So the real pivots go where the skin actually is, and the numbers are
// stated here rather than left to be discovered with a printed part in hand.
neck_pivot = [138, 0, 30];
neck_rise = 34;       // degrees the neck leaves the chest at
neck_reach = 34;      // pivot to head centre, along that neck axis
head_droop = 8;       // nose-down at rest, which is how a cat holds it
tail_pivot = [-148, 0, 34];
tail_rise = 51.6;     // degrees above horizontal, matches the urdf's rpy

// ---- head ----
// Sized off the body, not invented: a domestic cat's skull is about 60% of
// the chest width across the cheeks. The muzzle is short and the eyes sit
// forward, which is most of what makes a face read as feline rather than
// canine.
// 72mm across a 109mm body is 66% - the proportion the reference render
// has. At 60% the head reads as a bird's; much over 70% and it reads as a
// kitten's.
head_w = 72;
head_h = 66;
head_l = 84;

eye_d = 15;           // outer lens/bezel diameter
eye_spacing = 34;     // centre to centre - 52% of head width, which is the
                      // proportion that reads as a cat rather than a fox
eye_x = 16;           // forward of the head centre
eye_z = 6;            // above the head centre
eye_toe_in = 12;      // degrees each eye is splayed outward

// Camera Module 3 board, from the Raspberry Pi mechanical drawing: 25 x 24mm
// board, 12.5mm lens barrel. It sits behind ONE eye - the other socket takes
// the IR illuminator, per plan-zakupowy.pdf.
cam_board = [25, 24, 11.5];
cam_bore_d = 16;

ear_h = 32;
ear_w = 29;
ear_t = 3.6;
ear_splay = 20;       // degrees outward from vertical
ear_x = -6;           // behind the head centre
ear_spacing = 40;
// Where the ear's own origin sits on the skull. head_upper cuts its socket
// with the same transform, so the socket and the plug cannot drift apart.
ear_seat_z = 26;

// Where the head splits. head_upper and head_lower both cut on this plane
// from opposite sides, so it has to be one number, not two that agree.
head_split_z = -6;
ear_tang = 13;

// ---- legs ----
// The round disc over every joint is the strongest visual signature in the
// reference image, and it is nearly free: it hides the horn screws and the
// gap between segments. Diameter follows the servo's own collar so it always
// looks deliberate.
cap_d = servo_boss_d + 12;      // 34.1
cap_h = 4.5;

fairing_gap = 1.2;    // clearance between a fairing and the segment inside it

// ---- tail ----
// Segments thread onto a single 2mm steel wire or a spring, tapering from
// root to tip. Eleven of them over 190mm reads as a cat tail; fewer looks
// like an antenna. The tail is driven by one microservo at the root, so the
// segments themselves are passive and only need to be light.
tail_n = 11;
tail_len = 190;
tail_root_d = 17;
tail_tip_d = 8;
tail_bore_d = 2.6;    // 2mm wire plus fit

// ---- neck ----
neck_d = 34;
neck_len = 26;
