"""Source placements and first-fit geometry in 20H coordinates (millimetres)."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import hashlib
import json
import math
import os

import FreeCAD as A
import Part

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
SOURCE = STUDY / "day20-whole-battery-and-adaptable-protection/20H/whole-cat20H.FCStd"
REFERENCE = next(p / "reference/appearance/functional-eyes-approved-concept.png"
                 for p in HERE.parents if (p / "reference/appearance/functional-eyes-approved-concept.png").exists())
CAMERA_STEP = Path(os.environ.get("ROBOT_CAT21_CAMERA_STEP", str(
    Path(os.environ["TEMP"]) / "robot-cat21-camera-oem/wide.step")))
CAMERA_URL = "https://pip-assets.raspberrypi.com/categories/1207-design-files/documents/RP-008154-DS-1-camera-module-3-step.zip"
SOURCE_SHA = "40f9ee0753ebc8819f03559ac037af08d82c868e6ecab7a06ed68da312a84c41"
CAMERA_SHA = "b13715ed4fac37ef8357ffddf824cfafe923e55aa849941c5508986cc625c994"
V = A.Vector
X = V(1, 0, 0)
Y = V(0, 1, 0)
Z = V(0, 0, 1)
CAM_EYE = V(-219.0, 40, 142)
TOF_EYE = V(-218.4, -40, 142)
IRIS_X = -220.
CAM_BORES = ((29.5,142.1),(50.5,142.1))
CAM_OTHER_BORES = ((29.5,129.6),(50.5,129.6))
CAM_WIDE = (51.,33.5)
TOF_WIDE = (22.5,22.5)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def bounds(s):
    b = s.BoundBox
    return [round(q,4) for q in (b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)]

def box(x,y,z,dx,dy,dz):
    return Part.makeBox(dx,dy,dz,V(x,y,z))

def cylinder(x,y,z,r,depth):
    return Part.makeCylinder(r,depth,V(x,y,z),X)

def solid_hit(a,b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.
    c = a.common(b)
    if not c.isNull():
        assert c.isValid()
    return round(c.Volume,5)

def moved(s,placement):
    s = s.copy()
    s.Placement = placement.multiply(s.Placement)
    return s

def articulated(yaw,pitch):
    return A.Placement(V(),A.Rotation(Z,yaw),V(-130,0,127)).multiply(
        A.Placement(V(),A.Rotation(Y,pitch),V(-159,0,121)))

def load_saved(names):
    assert sha(SOURCE)==SOURCE_SHA
    result={}
    with ZipFile(SOURCE) as archive:
        xml=ET.fromstring(archive.read("Document.xml"))
        for n in names:
            entry=xml.find(f'./ObjectData/Object[@name="{n}"]/Properties/Property[@name="Shape"]/Part')
            if entry is not None:
                shape=Part.Shape()
                shape.importBrepFromString(archive.read(entry.get("file")).decode("ascii"))
                result[n]=shape
    return result

def camera_geometry():
    assert sha(CAMERA_STEP)==CAMERA_SHA
    source=Part.read(str(CAMERA_STEP))
    rotation=A.Rotation(Z,-Y,X,"ZXY")
    lens=V(14.4,12.5,-8.805)
    pose=A.Placement(CAM_EYE-rotation.multVec(lens),rotation)
    assert (pose.multVec(lens)-CAM_EYE).Length<1e-7
    # Original OEM FPC receptacle occupies x_local 16.95–23.49, at rear.
    # The outside lip is at the high-Z board edge in this clocking.
    fpc=pose.multVec(V(23.492,12.5,1.30))
    return source,pose,fpc

def tof_geometry(s):
    # Pololu STEP +z points forward. Rotate the long package axis into Y
    # and the through-hole pad side into +Z to match the reference eye.
    optical=s.Placement.multVec(V(7.65,8.84,2.566))
    rotation=A.Rotation(X,90)
    pose=A.Placement(TOF_EYE-rotation.multVec(optical),rotation)
    return pose,optical

def rect_wire(x,y,z,hy,hz):
    q=[V(x,y-hy,z-hz),V(x,y+hy,z-hz),V(x,y+hy,z+hz),V(x,y-hy,z+hz)]
    return Part.Wire(Part.makePolygon(q+[q[0]]).Edges)

def field(centre,half,angles,limit=-262.,start=.16):
    seeds=[]
    for x in (centre.x+start,limit):
        dep=max(0.,centre.x-x)
        hy,hz=[h+dep*math.tan(math.radians(a)) for h,a in zip(half,angles)]
        seeds.append(rect_wire(x,centre.y,centre.z,hy,hz))
    return Part.makeLoft(seeds,True,True)

def write_json(path,value):
    temporary=path.with_suffix(".tmp")
    with temporary.open("w",encoding="utf-8",newline="\n") as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2)
        stream.write("\n")
    os.replace(temporary,path)

def cheap():
    names=["VL53L5CX","D19D_OpticsCarrier","D19D_PitchBack","PITCH_HORN_ROOF_JOURNAL",
        "PITCH_SHAFT_FRAME_POSITIVE_CROSSPIN_full_screw","E19_FrontShroud","E19_UpperYawCover",
        "MG92B_Head_pitch","PBAY_F_HY","D19D_YawSaddle","C19_FFC190","D19D_Face"]
    src=load_saved(names)
    camera,cp,fpc=camera_geometry()
    tp,old_center=tof_geometry(src["VL53L5CX"])
    cam=moved(camera,cp)
    tof=moved(src["VL53L5CX"],tp)
    checks={}
    for k,s in (("camera",cam),("ToF",tof)):
        checks[k]={"bounds":bounds(s),"rigid_intersections_before_new_carrier":
            {n:solid_hit(s,src[n]) for n in names[2:9]}}
    # C/S/C bound in the vertical plane of the two cable ends. These values
    # screen the original two-bend topology. They do not credit flex or roll.
    fixed=V(-62.5,-16.5,105.1)
    lengths=[]
    for yaw,pitch in [(0,0),(-20,-10),(-20,10),(20,-10),(20,10)]:
        start=articulated(yaw,pitch).multVec(fpc)
        run=math.hypot(fixed.x-start.x,fixed.y-start.y)
        rise=fixed.z-start.z
        arch=math.hypot(run-44,rise)+math.pi*22
        lengths.append({"yaw":yaw,"pitch":pitch,"straight_lower":round((fixed-start).Length,4),
                        "vertical_end_same_turn_R22_fan":round(arch,4)})
    report={"source":SOURCE_SHA,"reference_sha256":sha(REFERENCE),"camera_source":CAMERA_SHA,
            "camera_source_oem_pcb_and_full_solid_assembly_count":len(cam.Solids),"camera_oem_url":CAMERA_URL,
            "camera_optical_plane_xyz":list(CAM_EYE),"camera_connector_lip_xyz":list(fpc),
            "tof_optical_plane_xyz":list(TOF_EYE),"tof_old_window_centre_xyz":list(old_center),
            "fixed_pi_decision_point_xyz":list(fixed),"rigid":checks,"ffc_length_screen":lengths}
    print(json.dumps(report,ensure_ascii=False),flush=True)
    return report

if __name__=="__main__":
    write_json(HERE/"layout-gate.json",cheap())
