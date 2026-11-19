"""Transfer the lower yaw skirt to the fixed shield; seat guides and optical wells from inside."""
from pathlib import Path
import json,runpy
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent
code=(P/"close-moving-interface.py").read_text()
exec(code[:code.index("S=lay")])
# Fit both actual four-jacket seats. All force from the open pads goes to the
# carrier below the jackets. The case-side vertical web is on the carrier root.
S=lay["head_receiver"];B=lay["fixed_receiver"]
orig=sh("D18C_TRUE_PITCH_OPTICAL_RECEIVER").cut(box(-204,1.2,91,17.5,15,24))
foot=box(-182.9,-19.8,148.6,5.2,5.1,9.6);leg=box(-182.9,-43,148.6,5.2,28,2.8)
beam=box(-182.9,-43.5,148.6,34,4.1,2.9);rise=box(-153.4,-44.8,149,4.9,4.2,7.2)
seat=pad(*S);seat.translate(V(0,0,-.8))
update("D19D_OpticsCarrier",fused([orig,foot,leg,beam,rise,seat]))
fl=sh("B19_FrontFloor");seat=pad(*B);seat.translate(V(0,0,-.8))
fore=fused([fl,box(-73.2,20,41,6.2,34.2,4.5),box(-73.2,51,42.5,5.6,4.2,90.2),box(-73.2,50.7,130.4,20.9,4.5,2.6),seat])
update("D19D_FrontFloor",fore)
# The fixed shield encloses everything below the division. End the entire
# moving skirt at Z=98.2, above the previous -138..-101, Z=81..96.79 overlap.
yaw=sh("D19D_YawHood").common(box(-170,-105,98.2,115,210,143))
# Put the hood clamp on the opposite leg of the yaw saddle, clear of the
# factory pitch wire and the rotating crosspin body at Z=121.
saddle=sh("BR_FINISHED_YAW_SADDLE");rail=box(-136,67,128.6,10.2,6,4.4).cut(box(-132.8,68.6,128,2.8,3.2,6))
ribs=[box(x,14,128.6,4.2,57.4,3.6) for x in [-136,-130]]
update("D19D_YawSaddle",fused([saddle,rail]+ribs))
tab=box(-136,67.2,133.2,10.2,16.8,3.1).common(outer([(-138,82,72,220),(-126,79,70,220),(-111,74,68,218),(-97,67,67,211)])).cut(box(-132.8,68.6,133,2.8,3.2,4))
update("D19D_YawHood",join_valid(yaw,tab))
# Replace the tapering rear tube by a broad, short back. It terminates at
# the yaw-mounted diaphragm. The longitudinal loop enters the body axially.
backrows=[(-162.65,76.5,90,212),(-153,77,86,213),(-143,76,85,211),(-132.8,72.5,85,205)]
back=split_skin(backrows,1.45)
rim=split_skin([(-166,74.6,92,210),(-161.8,75.6,91,211)],1.5);back=join_valid(back,rim)
update("D19D_PitchBack",back)
# Rebuild a front optical well bounded by the outside of the real mask and
# open at the near end of each source cone. The field stops in front of its
# delivered board; an end cap inside that gap would obstruct the lens.
face=sh("D19D_Face")
rows=[(-222,11,111,135),(-218,28,97,155),(-212,51,88,181),(-203,68,84,199),(-189,80,84,210),(-176,82,86,213),(-163,76.5,90,212)]
blank=outer(rows)
# Remove material projecting forward of the designed muzzle/forehead. Retain
# the two rounded muzzle lobes and the bearing plane of each inlay.
allowed=blank
for sg in [-1,1]:allowed=allowed.fuse(ell((-217,sg*11.8,121.7),(8.8,13.3,8.7)))
centre=box(-228,-30,89,40,60,97)
face=face.cut(centre.cut(allowed))
with ZipFile(P.parent/"day18-body-reception-and-closed-fit/body-reception.FCStd") as z:
    xml=ET.fromstring(z.read("Document.xml"))
    for n in ["D18C_CAM_MODEL_CLOCK_BOUND_FOV","D18C_TOF_MODEL_CLOCK_BOUND_FOV"]:
        ref=xml.find("./ObjectData/Object[@name='%s']/Properties/Property[@name='Shape']/Part"%n).get("file")
        field=Part.Shape();field.importBrepFromString(z.read(ref).decode("ascii"));outside=field.copy();outside.translate(V(1.6,0,0))
        # Punch the full section of the translated cone at the lens-side end.
        x=field.BoundBox.XMax-.45;patch=outside.common(box(x,-50,87,4,100,106))
        face=face.cut(patch)
for sign,suf in [(1,"L"),(-1,"R")]:
    iris=sh("D19D_Iris_"+suf);axis=V(-.96,.28*sign,.10);axis.normalize();c=V(-210.5,sign*42,158.5);rot=A.Rotation(V(0,0,1),axis)
    def loc(s):s.Placement=A.Placement(c,rot).multiply(s.Placement);return s
    p=sh("D19D_Pupil_"+suf)
    lip=Part.makeCone(11.45,11.94,.9,V(0,0,-4.4),V(0,0,1))
    p=p.fuse(loc(lip)).cut(loc(cyl((0,0,-5),9.9,7.35,(0,0,1)))).cut(loc(box(-.45,-12,-4.5,.9,24,4.6)))
    update("D19D_Pupil_"+suf,p)
    # Retain a curved brow above the eye rather than a ring around it.
    brow=ell((-204.5,sign*43,177.5),(7.6,21,5.4)).cut(ell((-203.9,sign*43,177.4),(6.4,19.7,4.1)))
    face=join_valid(face,brow);face=face.cut(iris).cut(p)
face=face.cut(back);update("D19D_Face",face)
D.recompute();D.save();write("interface-final.json",dict(fixed_to_yaw_division_z=98.2,pitchback_ends_x=-132.8,actual_seat_top_relative_z=-2.9,saddle_rail_side="+Y",optical_wells="inside-mask open at both source near planes"))
runpy.run_path(str(P/"views.py"))

