// ==================== source of truth ====================
// Every VERIFIED number below is cross-referenced to either this repo's own
// simulation model (src/robot_cat_description/urdf/cat.urdf.xacro at scale
// 1.0, and robot_cat_gait/leg_ik.py) or an independently checked datasheet -
// see hardware/cad/README.md for exactly what was checked and against what.
//
// ADJUSTABLE numbers are flagged because the one thing they depend on - the
// downloaded servo bracket's own mounting face - could not be fetched from
// Printables/Thingiverse in this session (both block automated access).
// Print ONE part that uses an ADJUSTABLE value, hold it against the real
// bracket, correct the number, then print the rest. Everything else here is
// safe to print in full sets straight away.

// ---- leg geometry - VERIFIED, must match leg_ik.py exactly ----
thigh_length = 110;   // LegGeometry.thigh_length, axis to axis
calf_length  = 110;   // LegGeometry.calf_length, axis to paw centre
hip_offset   = 25;    // hip roll axis -> thigh pitch axis, lateral
foot_radius  = 12;    // paw pad sphere radius

// ---- trunk geometry - VERIFIED ----
hip_x = 110;          // hip mount, x from body centre (so 220mm hip-to-hip)
hip_y = 55;           // hip mount, y from body centre (so 110mm hip-to-hip)
body_length = 300;
body_width  = 111;
body_height = 141;

// ---- ST3215 servo body - VERIFIED: DFRobot product page (2962) and
// servodatabase.com both give 45.2 x 24.7 x 35.0 mm ----
servo_l = 45.2;
servo_w = 24.7;
servo_h = 35.0;
servo_fit = 0.4;      // FDM clearance added per side around the pocket

// ---- Raspberry Pi 5 mounting - VERIFIED against the official Raspberry Pi
// Ltd mechanical drawing (RP-008347-DS-1): 58 x 49mm hole spacing, Ø2.7mm
// holes (clearance for M2.5) ----
pi_hole_x = 58;
pi_hole_y = 49;
pi_hole_d = 2.9;       // add a touch over the datasheet 2.7 for FDM tolerance

// ---- ADJUSTABLE: servo horn bolt circle ----
// Reverse-measured from a real, printed, STS3215-based quadruped
// (github.com/garciamathias/OpenRoboticDog, hip_x4.stl) - NOT the servo
// datasheet, because no datasheet with this number could be reached. Four
// holes: three at 6.7mm radius, one at 5.6mm (verified asymmetric - this is
// what the real mesh measured, not a rounding choice). Treat this as a
// well-informed starting point, not gospel: confirm on the physical horn
// before drilling the rest.
horn_bolt_r_major = 6.7;
horn_bolt_r_minor = 5.6;   // the fourth hole sits closer to centre
horn_bolt_d = 2.6;         // self-tapping screw clearance
horn_hub_d = 6.0;          // splined output shaft boss, servo horn already has this - clearance only

// ---- ADJUSTABLE: bracket-to-frame flange ----
// Printables 653674 is described as exposing "4 standard M3 machine screws"
// on its outward face once mounted to the servo, but the exact spacing could
// not be fetched (site returns 403 to automated tools). Starting guess sized
// to comfortably clear the servo body's 24.7mm width. CONFIRM AND CORRECT
// against the downloaded bracket before printing the rest.
bracket_hole_x = 20;
bracket_hole_y = 16;
bracket_screw_d = 3.4;    // M3 clearance

// ---- print structure ----
wall = 4;             // load-bearing wall thickness in PETG
insert_d = 4.2;        // M3 brass heat-set insert bore
insert_depth = 6;
$fn = 48;
