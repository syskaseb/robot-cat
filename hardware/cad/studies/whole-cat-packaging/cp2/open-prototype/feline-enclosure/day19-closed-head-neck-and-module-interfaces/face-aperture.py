"""Use the native moving ToF and camera optical fields in the co-moving face."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
import FreeCAD as A,FreeCADGui as G,Part,json,runpy
P=Path(__file__).parent
src=(P/"head-and-shoulder.py").read_text()
exec(src[:src.index("# Both reception seats")])
source=P.parent/"day18-body-reception-and-closed-fit/body-reception.FCStd"
with ZipFile(source) as z:
    doc=E.fromstring(z.read("Document.xml"))
    face=sh("C19_FaceAndEars");before=face.Volume
    for n in ["D18C_TOF_MODEL_CLOCK_BOUND_FOV","D18C_CAM_MODEL_CLOCK_BOUND_FOV"]:
        ref=doc.find("./ObjectData/Object[@name='%s']/Properties/Property[@name='Shape']/Part"%n).get("file")
        field=Part.Shape();field.importBrepFromString(z.read(ref).decode("ascii"));face=face.cut(field).removeSplitter()
    assert face.isValid() and len(face.Solids)==1,(face.isValid(),len(face.Solids))
    # Assign the entire rear rim to the removable back. Preserve one face and
    # mounting ears; decline fragmentation at their joint.
    split=face.cut(sh("C19_OpenRearHelmet")).removeSplitter()
    seated=split.isValid() and len(split.Solids)==1
    if seated:face=split
D.C19_FaceAndEars.Shape=face
D.recompute();G.runCommand("Std_Save")
write("aperture-seat.json",dict(before=before,after=face.Volume,seat_installed=seated,rear_cut_solids=len(split.Solids),face_solids=len(face.Solids),valid=face.isValid()))
data=json.loads((P/"final-members.json").read_bytes());n="C19_FaceAndEars";s=sh(n)
data[n]=dict(valid=s.isValid(),solids=len(s.Solids),volume=s.Volume,extents=[s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength]);write("final-members.json",data)
runpy.run_path(str(P/"views.py"))

