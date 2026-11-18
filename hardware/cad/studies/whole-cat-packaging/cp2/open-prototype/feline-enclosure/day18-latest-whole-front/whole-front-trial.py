"""One forward gimbal on the lower frame, upright side banks and exposed handlay bays."""
import datetime
import json
from pathlib import Path
import FreeCAD as App
import Part

doc = App.ActiveDocument
folder = Path(__file__).parent
V = App.Vector
assert Path(doc.FileName).resolve() == (folder / "whole-front.FCStd").resolve()
assert not doc.getObject("FRONT18_LOWER_BEARING_FRAME"), "trial already present"
moves = {}

def translate(obj, shift):
    before = list(obj.Placement.toMatrix().A)
    obj.Placement = App.Placement(V(*shift), App.Rotation()).multiply(obj.Placement)
    moves[obj.Name] = dict(before=before, after=list(obj.Placement.toMatrix().A))

def orient(obj, center, axis, angle):
    old = obj.Shape.BoundBox.Center
    rot = App.Rotation(V(*axis), angle)
    before = list(obj.Placement.toMatrix().A)
    obj.Placement = App.Placement(V(*center) - rot.multVec(old), rot).multiply(obj.Placement)
    moves[obj.Name] = dict(before=before, after=list(obj.Placement.toMatrix().A))

def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, V(x, y, z))

def cylinder(x, y, z, radius, length):
    return Part.makeCylinder(radius, length, V(x, y, z))

def feature(name, shape, color):
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Shape = shape
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.DisplayMode = "Shaded"
    return obj

# Select actual members, including the matching optical fields and mating hardware.
head_tags = ("MG92B_Head", "Yaw608_", "Pitch688", "YAW_", "PITCH_", "HN_FIXED_SADDLE",
             "HEAD_YAW_FORK_", "CAM_standoff_", "CAM_primary_", "TOF_standoff_", "TOF_primary_",
             "D18C_TRUE_PITCH_", "F3_HEAD_", "F3_PAINT_", "Camera3_NoIR", "VL53L5CX",
             "D18C_CAM_MODEL_", "D18C_TOF_MODEL_", "CAMERA_FULL_INSTALLATION_", "CAMERA_SOURCE_OPTICAL_")
for obj in list(doc.Objects):
    if obj.Name.startswith(head_tags) and hasattr(obj, "Shape") and (
        obj.ViewObject.Visibility or obj.Name.startswith(("D18C_CAM_MODEL", "D18C_TOF_MODEL", "CAMERA_FULL_INSTALLATION"))
    ) and "Group" not in obj.PropertiesList:
        translate(obj, (-24, 0, 0))

# Six upright complete MTA/TE/ATO assemblies on each side. Existing lower and
# upper units alternate, so both sets are available while the back is open.
for index in range(6):
    side = 1 if index < 3 else -1
    for layer, prefix in enumerate(("Motor_ATO4A_1_", "Motor_ATO4A__1_")):
        obj = doc.getObject(prefix + str(index))
        slot = 2 * (index % 3) + layer
        orient(obj, (-53 + 32.5 * slot, side * 70, 113), (0, 1, 0), 90)
for n, x in [("WAGO415_data__1_0", 14), ("WAGO415_data__1_4", 26)]:
    orient(doc.getObject(n), (x, -18, 142), (0, 0, 1), 90)
for obj in doc.Objects:
    if obj.Name.startswith("OP_S1_") and obj.ViewObject.Visibility and hasattr(obj, "Shape"):
        translate(obj, (-75, 0, 0))
translate(doc.getObject("Monitor_MOD05015"), (-30, 0, 0))

# Lower frame rises outside the horn. The ring stops at the lower face of
# the original removable cap. Leave the entire pin level open during assembly.
cx = -130
seat = cylinder(cx, 0, 98, 15.5, 23)
seat = seat.cut(cylinder(cx, 0, 97, 9, 26)).cut(cylinder(cx, 0, 100, 11.1, 22))
frame = seat
for side in (-1, 1):
    y = side * 14.5
    boss = cylinder(cx, y, 110, 3.5, 11)
    frame = frame.fuse(boss)
    # Raise the bearing from the floor using outer posts under the bearing,
    # with a clear, open front for inserting the journal from below.
    y0 = 28 if side == 1 else -34
    rail = box(-143, y0, 46.5, 70, 6, 6)
    post = box(-138, y0, 50, 6, 6, 55)
    arm = box(-138, 10 if side == 1 else -34, 101, 8, 24, 4)
    frame = frame.fuse(rail).fuse(post).fuse(arm)
    frame = frame.cut(cylinder(cx, y, 109.5, 1.1, 13))
    frame = frame.cut(box(cx-2.42, 12.1 if side == 1 else -22, 111.9, 4.84, 9.9, 1.8))
frame = frame.cut(cylinder(cx, 0, 100, 11.1, 22)).removeSplitter()
feature("FRONT18_LOWER_BEARING_FRAME", frame, (0.24, 0.46, 0.47))
# Source CAD housing, screw stack and floor are retained as evidence. The new
# frame must actually join the floor and carry the motor saddle before selection.
# Side stock retainers: shared rail on the floor, receiving both existing rows.
for side, tag in [(-1, "NEG"), (1, "POS")]:
    y = side*70
    columns = [box(x, y-3, 47, 6, 6, 28.5) for x in (-53, 12, 77, 107)]
    rail = box(-68, y-6, 74, 194, 12, 3)
    for column in columns:
        rail = rail.fuse(column)
    feature("FRONT18_BANK_BED_"+tag, rail.removeSplitter(), (0.29, 0.45, 0.46))
# The two factory-connected P_REAR/F_AUX cases stay together on the lower
# deck. Their physical exits remain known constraints on the new frame.
facts = dict(basis="98e254116c1128f13a94742449beddf451461fd5",
             input_sha256="cb6cae78d89b1aee9bb05ba18c1a8ed129aadec572b3417a9c7677f7b61984c1",
             transforms=moves, yaw_center=[-130,0,127],pitch_center=[-159,0,121],
             short_factory_pair=["PBAY_P_REAR","PBAY_F_AUX"],
             assembly=["open floor and lower frame", "lower journal, horn and full crosspin before banks", "place complete side units, soldered PCA/E1 together", "lay occupied groups from above, then skins"],
             old_FFC_ToF_JR_routes="invalidated at changed end; supersede before acceptance",
             actual_fit=None, actual_cut=None, actual_installed_slack=None,
             whole_closed_accepted=False,physical_PASS=False)
(folder/"whole-trial-placements.json").write_bytes((json.dumps(facts,indent=1)+"\n").encode())
doc.Label="WHOLE FRONT TRIAL - LOWER FRAME AND UPRIGHT BANKS"
doc.recompute()
doc.save()
print("TRIAL SAVED",len(moves),len(frame.Solids),frame.isValid())
