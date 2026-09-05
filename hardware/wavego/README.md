# WAVEGO FreeCAD model

`WAVEGO_PRO_BETA_v3.FCStd` is the coloured, non-animated source model.
`WAVEGO_PRO_BETA_v3_motion.FCStd` is its 12-DOF kinematic working copy.

## Run the motion preview in FreeCAD

1. Open `WAVEGO_PRO_BETA_v3_motion.FCStd`.
2. Run `tools/freecad/WAVEGO_Motion.FCMacro` from **Macro > Macros**.
3. Use the **WAVEGO Motion** dock:
   - **Play trot / Pause** starts or stops the diagonal gait preview;
   - **Stand** restores the imported neutral pose;
   - **Gait phase** scrubs the animation;
   - the 12 numeric fields adjust each servo joint manually;
   - **Show servo axes** displays hip, knee and ankle axes in red, green and blue.

The preview checks hierarchy, ranges and clearances visually. It does not
simulate mass, torque, collisions, ground contact or servo dynamics; those
belong in the ROS 2 / Gazebo model after the CAD motion is accepted.

## Leg/servo mapping

| Leg | Hip | Knee | Ankle |
|---|---:|---:|---:|
| Front right (FR) | 4 | 6 | 10 |
| Front left (FL) | 3 | 8 | 12 |
| Rear right (RR) | 1 | 5 | 9 |
| Rear left (RL) | 2 | 7 | 11 |

The macro is idempotent: running it again reuses the existing kinematic
groups and reopens the controller panel.
