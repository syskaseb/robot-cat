"""Finish the symmetric face surfaces and relieve the measured rear clashes."""
from pathlib import Path
from tempfile import gettempdir
import json
import sys

import FreeCAD as A
import Part

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from layout import CAM_EYE,CAM_WIDE,TOF_EYE,TOF_WIDE,V,Y,bounds,box,field,write_json

KIT=Path(gettempdir())/"robot-cat21-camera-oem/native-kit"
props=json.loads((KIT/"objects.json").read_bytes())
def read(n):
    s=Part.Shape()
    s.importBrepFromString((KIT/(n+".brep")).read_text("ascii"))
    return s
def output(n,s):
    assert s.isValid() and len(s.Solids)==1,(n,s.isValid(),len(s.Solids))
    (KIT/(n+".brep")).write_bytes(s.exportBrepToString().encode("ascii"))
    props[n].update(volume=s.Volume,solids=1,bounds=bounds(s))
    print(n,s.Volume,flush=True)

mask=read("D21_Face")
# Both forehead quarters use the proven negative-Y surface. Keep the parting
# surfaces split through fusion to avoid unifying their trimmed spline faces.
r=mask.common(box(-290,-110,65,130,110.008,186))
assert r.isValid() and len(r.Solids)==1
s=r.fuse(r.mirror(V(),Y))
s=s.cut(field(CAM_EYE,(4.25,4.25),CAM_WIDE))
s=s.cut(field(TOF_EYE,(4.10,2.40),TOF_WIDE))
# Measured rear-jaw contacts in the pitch frame: x=-171.36..-162.70,
# |y|<=26.60 and z=85.85..93.79. Lift only that concealed return.
s=s.cut(box(-172.4,-28.1,82,13.2,56.2,13.0))
output("D21_Face",s)
# Spring clearance is provided only on the concealed heel of each ear;
# the forward rim/web and the mirror relationship stay intact.
right=read("D21_Ear_R")
heel=box(-200.8,-86.5,191.9,18.2,16.5,7.05)
right=right.cut(heel).removeSplitter()
output("D21_Ear_R",right)
output("D21_Ear_L",right.mirror(V(),Y))
# The right eye insert stops 0.20 mm ahead of the supplier package plane.
tof_insert=read("D21_Insert_ToF").cut(box(-218.60,-67,120,3.4,54,44))
output("D21_Insert_ToF",tof_insert)
write_json(KIT/"objects.json",props)
