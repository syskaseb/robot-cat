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
// The body's own shape lives in skin/loft.py, as a table of sections along
// the spine. It is NOT here and not in shell_lib: a convex hull could not
// produce the concavities a cat needs, so the skin is a lofted mesh and the
// section table is the thing to edit.
//
//     python3 skin/loft.py        # regenerate after editing it
//
// Only the numbers the rest of the cosmetic layer needs are kept here.
body_hw = body_width / 2;              // 55.5
body_hh = body_height / 2;             // 70.5

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
neck_pivot = [132, 0, 34];
neck_rise = 30;       // degrees the neck leaves the chest at
neck_reach = 32;      // pivot to head centre, along that neck axis
head_droop = 2;       // nose-down at rest, which is how a cat holds it

// The head is close-coupled to the chest, the way the concept render has it,
// so its rear half overlaps where the body's front cone used to be. The
// shell gets a round opening along the neck axis instead of a nose cone -
// the head nestles into it and the collar hides the edge. How much yaw the
// opening really allows is a FIT-TEST item, not something this file proves.
neck_relief_d = 70;
tail_pivot = [-148, 0, 34];
tail_rise = 51.6;     // degrees above horizontal, matches the urdf's rpy

// ---- head ----
// The head's SHAPE lives in skin/loft.py, as two section tables - SKULL and
// MUZZLE - united into one watertight mesh. It is not built here any more:
// the hull-of-spheres head could not make the step where the muzzle leaves
// the cheeks, and that step is most of what makes a face read as a cat.
// What stays here is everything the functional cuts need to know: where the
// eyes, ears, camera and split plane sit ON that mesh.
//
//     python3 skin/loft.py        // regenerate after editing the tables

eye_d = 19;           // bore the eye ball shows through
eye_spacing = 44;     // centre to centre - half the head's 88mm width
eye_x = 22;           // forward of the head centre, on the flat face
eye_z = 8;            // above the head centre
eye_toe_in = 8;       // degrees each eye is splayed outward
eye_bulge = 5.0;      // how far the lens stands proud of the skull. A cat's
                      // eye is a sphere pushing out of the socket, not a
                      // window set into it - flush eyes read as a mask.

// Camera Module 3 board, from the Raspberry Pi mechanical drawing: 25 x 24mm
// board, 12.5mm lens barrel. It sits behind ONE eye - the other socket takes
// the IR illuminator, per plan-zakupowy.pdf.
cam_board = [25, 24, 11.5];
cam_bore_d = 16;

ear_h = 34;
ear_w = 33;
ear_t = 3.8;
ear_splay = 22;       // degrees outward from vertical
ear_x = -14;          // behind the head centre
ear_spacing = 48;
// Where the ear's own origin sits on the skull. head_upper cuts its socket
// with the same transform, so the socket and the plug cannot drift apart.
ear_seat_z = 30;

// Where the head splits. head_upper and head_lower both cut on this plane
// from opposite sides, so it has to be one number, not two that agree.
head_split_z = -8;
ear_tang = 13;

// ---- legs ----
// The round disc over every joint is the strongest visual signature in the
// reference image, and it is nearly free: it hides the horn screws and the
// gap between segments. Diameter follows the servo's own collar so it always
// looks deliberate.
// A barrel over the whole servo, not a disc stuck on the side. Sized to
// swallow the servo's 24.8 x 35.4 cross-section (43.2 diagonal), which is
// why it lands near 46 - and at that size it reads the way the reference
// render's shoulder and knee housings do, as a major part of the silhouette
// rather than a cosmetic cap.
//
// It is also structural now: this is the outer arm of the yoke that bolts to
// the servo's idle face, so the joint is supported on both sides instead of
// hanging off the horn. Hence 4mm of wall, not 1.8.
housing_d = 50;
housing_len = 42;
housing_wall = 4;

// Limb segments are capsules with domed ends, deliberately SHORTER than the
// gap between joints. The bare spine showing at each end is what separates
// one segment from the next; a fairing that runs joint to joint welds the
// whole leg into one blob, which is exactly how the first attempt went wrong.
limb_d_thigh = [40, 32];   // diameter at the hip end, and at the knee end
limb_d_calf  = [32, 25];
limb_gap = 6;              // bare spine left showing at each end of a segment
fairing_wall = 2.4;        // the fairing is a SHELL with grip collars at the
                           // ends, not a solid - at 40mm a solid one costs
                           // 25g per thigh, and leg grams are the expensive
                           // grams (see measure/mass_check.py)

fairing_gap = 1.2;    // clearance between a fairing and the segment inside it

// ---- tail ----
// Segments thread onto a single 2mm steel wire or a spring, tapering from
// root to tip. Eleven of them over 190mm reads as a cat tail; fewer looks
// like an antenna. The tail is driven by one microservo at the root, so the
// segments themselves are passive and only need to be light.
tail_n = 11;
tail_len = 190;
tail_root_d = 24;      // the concept's tail is thick at the root - 17 read
tail_tip_d = 10;       // as a whip antenna next to a 46mm joint housing
tail_bore_d = 2.6;    // 2mm wire plus fit

// ---- neck ----
neck_d = 44;
neck_len = 30;
