// ==================== source of truth ====================
// Every number below is cross-referenced to either this repo's own simulation
// model (src/robot_cat_description/urdf/cat.urdf.xacro at scale 1.0, and
// robot_cat_gait/leg_ik.py) or to a measurement of a real CAD file - see
// hardware/cad/measure/README.md for the method, the sources and the raw
// numbers.
//
// Nothing here is a guess any more. The two values that used to be flagged
// ADJUSTABLE (the horn bolt circle and a downloaded bracket's flange) were
// replaced by measurements taken off the official STS3215 STEP model, so the
// downloaded bracket is no longer on the critical path at all.

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

// ---- ST3215 / STS3215 servo - MEASURED from the official CAD model
// (TheRobotStudio/SO-ARM100, STEP/SO100/STS3215_03a.step). The shop pages'
// "45.2 x 24.7 x 35" is the CASE only; the model bounding box is 39.6 deep
// because the output boss and the idler boss stand proud of it. Pocket depth
// must use servo_h, clearance above it must allow for servo_boss. ----
servo_l = 45.4;
servo_w = 24.8;
servo_h = 35.4;        // case alone, faces at +/-17.7 from centre
servo_boss_h = 2.3;    // output boss above the case face
servo_boss_d = 22.1;   // raised collar around the output axis, +0.1 clearance
servo_axis_x = 12.5;   // output axis offset from the servo's own centre,
                       // i.e. 10.2mm in from the near end face
servo_fit = 0.4;       // FDM clearance added per side around the pocket

// ---- Raspberry Pi 5 mounting - VERIFIED against the official Raspberry Pi
// Ltd mechanical drawing (RP-008347-DS-1): 58 x 49mm hole spacing, Ø2.7mm
// holes (clearance for M2.5) ----
pi_hole_x = 58;
pi_hole_y = 49;
pi_hole_d = 2.9;       // add a touch over the datasheet 2.7 for FDM tolerance

// ---- servo horn bolt circle - MEASURED, exact
// Four holes, all on ONE circle of radius 7.000mm (diameter 14.00), at 45,
// 135, 225 and 315 degrees - a square of side 9.90mm. Least-squares circle
// fit to the STEP model's analytic CIRCLE entities, residual 0.000mm.
//
// The earlier "three holes at 6.7, one at 5.6" here was wrong. It came from
// misreading OpenRoboticDog's hip_x4.stl, which has no horn circle at all -
// those were the servo's case screws. See measure/README.md.
horn_bolt_r = 7.0;
horn_bolt_d = 2.7;         // M2.5 clearance, model bore is 2.5
horn_hub_d = 9.2;          // Ø9.0 hub on the horn face, +0.2 clearance

// ---- servo case screw positions - MEASURED
// The four screws that hold the servo case together double as mounting
// points: this is how OpenRoboticDog fixes the servo to its frame, and that
// part measures 3.75mm apart against this model's 3.8mm. Positions are given
// relative to the servo centre, on both flanks at y = +/-10.25.
case_screw_y = 10.25;
case_screw_x = [4.2, -16.5, -20.3];
case_screw_d = 2.2;        // M2 clearance; the servo's own bore is 1.5 pilot

// Two of the three are enough to fix a servo, and OpenRoboticDog uses two.
// Which two matters here: taking the pair NEAREST the output axis keeps a
// mounting pad 35mm long instead of 45mm, which is what lets the trunk frame
// stay inside the 300mm body. The outermost screw stays available if a part
// wants all three.
case_screw_x_used = [4.2, -16.5];

// ---- print structure ----
wall = 4;             // load-bearing wall thickness in PETG
insert_d = 4.2;        // M3 brass heat-set insert bore
insert_depth = 6;
$fn = 48;
