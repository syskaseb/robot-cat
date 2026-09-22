# Superseded experiment — do not use for motor approval

These preliminary results used incorrect rigid-body ownership inherited from
v25: the first hip servo housings were grounded and their horns moved with the
yokes. Matching M2 mounting axes show the opposite mounting in this WAVEGO.
v27 corrects the native FreeCAD joints, link meshes and moving inertia.

`superseded.zip` retains JSON telemetry, configuration, logs and reports for
traceability. No earlier experimental file was deleted. The earliest trials
also received zero `JointState.force` from Gazebo 8.11; later trials use actual
commanded motor effort from a dedicated plugin, NOT measured reaction torque.
Even those later v25 results are superseded by the ownership correction.

Current work: [v27 / simulation runbook](../README.md).
