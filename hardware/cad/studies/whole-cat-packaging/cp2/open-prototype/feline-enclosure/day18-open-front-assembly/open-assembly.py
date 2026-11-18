"""Build one two-foot bearing bridge and a transverse upper audio deck behind the data reserve."""
from pathlib import Path
import json
import FreeCAD as A, FreeCADGui as G, Part
P=Path(__file__).parent
D=A.ActiveDocument
assert Path(D.FileName).resolve()==(P/"open-front.FCStd").resolve()
assert not D.getObject("OPEN_PORTAL_AND_FLOOR")
V=A.Vector
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,V(x,y,z))
def feature(n,shape,col):
    o=D.addObject("PartDesign::Feature",n);o.Shape=shape;o.ViewObject.ShapeColor=col;o.ViewObject.DisplayMode="Shaded";return o
def bounds(s):
    b=s.BoundBox
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
seat=cyl(-130,0,98,15.5,23)
for sign in (-1,1):
    seat=seat.fuse(cyl(-130,sign*14.5,110,3.5,11))
seat=seat.cut(cyl(-130,0,97,9,26)).cut(cyl(-130,0,100,11.1,22))
for sign in (-1,1):
    seat=seat.cut(cyl(-130,sign*14.5,109.5,1.1,13)).cut(box(-132.42,12.1 if sign==1 else -22,111.9,4.84,9.9,1.8))
# The upper header carries the ring into both uprights above the full MG horn.
# Both sides transfer torque into existing continuous rails on the native deck.
members=[seat,box(-120,-7,101,10,14,6),box(-117,-31,100.5,8,62,7)]
for sign in (-1,1):
    members += [box(-140,27 if sign==1 else -35,46.5,67,8,6),
                box(-117,23 if sign==1 else -32,49.5,8,9,57.5),
                box(-117,8.3 if sign==1 else -31,66.5,8,22.7,3)]
    ledge=box(-140,sign*11.5-3.2,66.5,31,6.4,3)
    members.append(ledge.cut(cyl(-134,sign*11.5,63.5,1.15,10)))
portal=members[0].multiFuse(members[1:]).removeSplitter()
assert portal.isValid() and len(portal.Solids)==1
floor=D.D18C_P02_THREE_ROOT_THROUGH_VERSION.Shape
connected=portal.common(floor).Volume
root=floor.fuse(portal).removeSplitter()
assert connected>0 and root.isValid() and len(root.Solids)==1
feature("OPEN_PORTAL_AND_FLOOR",root,(.22,.43,.43))
feature("OPEN_PORTAL_MATERIAL_SUBSET",portal,(.22,.43,.43)).ViewObject.Visibility=False
D.FRONT18_FLOOR_AND_YAW_ROOT.ViewObject.Visibility=False
# Broad free region extending from the case to an open fixed-handlay bay.
# This field is conditional on a low exit on the rear face, with space across
# the complete case width. Actual supplier exit side and strain relief remain open.
band=box(-119.5,-18,48.5,27,36,16.5)
field=feature("OPEN_MG_EXIT_BAND",band,(.87,.58,.15));field.ViewObject.Visibility=False
info=dict(portal_solids=len(portal.Solids),root_solids=len(root.Solids),floor_common_mm3=connected,
          portal_vs_case_adjacent_field=portal.common(band).Volume,floor_vs_case_adjacent_field=floor.common(band).Volume,
          side_uprights_mm=[8,9],rail_foot_mm=[67,8,6],upper_header_mm=[8,62,7],
          exit_field_xyz=bounds(band),mg_source_case=bounds(D.MG92B_Head_yaw.Shape),moves={})
def pose(n,names,target,angle):
    o=D.getObject(n);s=o.Shape.BoundBox.Center;r=A.Rotation(V(0,0,1),angle)
    pl=A.Placement(V(*target)-r.multVec(s),r)
    for name in dict.fromkeys([n]+names):
        obj=D.getObject(name);before=bounds(obj.Shape);obj.Placement=pl.multiply(obj.Placement)
        info["moves"][name]=dict(prior=before,after=bounds(obj.Shape),matrix=pl.toMatrix().A)
mic="ReSpeakerLite_on_REMOVABLE_back"
mic_more=[o.Name for o in D.Objects if o.Name.startswith("HB_MIC_") and o.ViewObject.Visibility]
pose(mic,mic_more+["INSERT_AUDIO_USB_C_FULL_MATE_FIELD","INSERT_MIC_ACOUSTIC_FACE"],(62,0,171),90)
pose("Speaker",["INSERT_SPEAKER_TWO_BTL_TABS_FIELD","INSERT_SPEAKER_ACOUSTIC_FACE"],(105,0,176),90)
amp_more=[o.Name for o in D.Objects if o.Name.startswith("CB_AMP_") and o.ViewObject.Visibility]
pose("MAX98357A_amp",amp_more,(97,40,150),0)
# Existing DATA500 curves and straight tails form a low approach and a flat
# upper return. This shelf supports the latter from below without enclosing it.
# Two transverse beams between existing negative and positive bank flanges;
# only the inboard portions are raised above the installed fuse bodies.
def rail_poly(x):
    rr=[box(x,-73,128,4,5,36),box(x,68,128,4,5,36),box(x,-73,163,4,146,3.6)]
    return rr[0].multiFuse(rr[1:]).removeSplitter()
# Physical tray anchored by integral legs reaching the existing panel surfaces.
rails=[]
for x in (-63,-31):
    p=rail_poly(x)
    for y in (-1,1):
        foot=box(x-1,68 if y==1 else -73,126.9,6,5,2.5)
        p=p.fuse(foot)
    rails.append(p.removeSplitter())
for i,r in enumerate(rails):
    feature("OPEN_DATA_CROSSBEARER_"+str(i),r,(.32,.44,.46))
# Each bearer is a trial support. Retire it as usable if installed hardware
# occupies the path; the separate cross section reports that directly.
info["data_beams"]=[dict(solid=len(r.Solids),bounds=bounds(r)) for r in rails]
(P/"open-assembly.json").write_bytes((json.dumps(info,indent=1)+"\n").encode())
D.Label="OPEN FRONT ASSEMBLY - TWO FOOT PORTAL AND AUDIO DECK";D.recompute();G.runCommand("Std_Save")
