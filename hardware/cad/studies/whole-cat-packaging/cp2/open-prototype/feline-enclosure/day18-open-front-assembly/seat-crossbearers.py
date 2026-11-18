"""Seat the DATA layer on panel edges and clock the removable audio insert for its actual fasteners."""
from pathlib import Path
import json
import FreeCAD as A, FreeCADGui as G, Part
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
assert Path(D.FileName).resolve()==(P/"open-front.FCStd").resolve()
assert not D.getObject("OPEN_FORE_BANK_AND_DATA_FRAME")
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def move(n,names,center,rotation):
    old=D.getObject(n).Shape.BoundBox.Center;transform=A.Placement(V(*center)-rotation.multVec(old),rotation)
    for name in dict.fromkeys([n]+names):
        o=D.getObject(name);o.Placement=transform.multiply(o.Placement)
mic_names=[o.Name for o in D.Objects if o.Name.startswith("HB_MIC_") and o.ViewObject.Visibility]
move("ReSpeakerLite_on_REMOVABLE_back",mic_names+["INSERT_AUDIO_USB_C_FULL_MATE_FIELD","INSERT_MIC_ACOUSTIC_FACE"],(62,0,171),A.Rotation(V(0,0,1),180))
amp_names=[o.Name for o in D.Objects if o.Name.startswith("CB_AMP_") and o.ViewObject.Visibility]
move("MAX98357A_amp",amp_names,(97,-39,150),A.Rotation())
# Put the feet outboard of the bought cases and the upper transverse returns
# above them. The enlarged flanges intersect both actual panel edges.
beams=[]
for i,x in enumerate((-63,-31)):
    parts=[box(x,-85.5,162.5,4,171,4.1)]
    for side in (-1,1):
        y=82.4 if side==1 else -87.4
        parts.extend([box(x,y,127,4,5,38.5),box(x-1,y,126.4,6,5,4)])
    r=parts[0].multiFuse(parts[1:]).removeSplitter()
    o=D.getObject("OPEN_DATA_CROSSBEARER_"+str(i));o.Shape=r;o.ViewObject.Visibility=False;beams.append(r)
fore=[D.getObject("FRONT18_FORE_"+tag+"_PANEL") for tag in ("POS","NEG")]
merged=fore[0].Shape.multiFuse([fore[1].Shape]+beams).removeSplitter()
assert merged.isValid() and len(merged.Solids)==1
o=D.addObject("PartDesign::Feature","OPEN_FORE_BANK_AND_DATA_FRAME");o.Shape=merged;o.ViewObject.DisplayMode="Shaded";o.ViewObject.ShapeColor=(.22,.4,.42)
for prior in fore:prior.ViewObject.Visibility=False
# Fuse the real rail feet of this frame into the existing floor. Its top
# bridge and two bearing feet all remain on one part when the cover lifts off.
root=D.OPEN_PORTAL_AND_FLOOR
common=root.Shape.common(merged).Volume
solid=root.Shape.fuse(merged).removeSplitter()
if common>0 and solid.isValid() and len(solid.Solids)==1:
    full=D.addObject("PartDesign::Feature","OPEN_SINGLE_FRONT_FLOOR");full.Shape=solid;full.ViewObject.ShapeColor=(.24,.40,.42);full.ViewObject.DisplayMode="Shaded"
    o.ViewObject.Visibility=False;root.ViewObject.Visibility=False
# The actual stepped floor carries a ramp-sided free space over its front rim.
# Preserve the entire original broad-band intersection as a negative witness.
def section(x,z):
    v=[V(x,-18,z),V(x,18,z),V(x,18,68),V(x,-18,68)]
    return Part.makePolygon(v+[v[0]])
s=Part.makeLoft([section(-119.5,48.5),section(-112,48.5),section(-105.1,55.8),section(-92.5,55.8)],True,True)
f=D.addObject("PartDesign::Feature","OPEN_HANDLAY_OVER_FLOOR");f.Shape=s;f.ViewObject.Visibility=False
c=s.common(root.Shape).Volume
(P/"seated-frame.json").write_bytes((json.dumps(dict(whole_floor_candidate_solids=len(solid.Solids),valid=solid.isValid(),common_between_floor_and_frame=common,
    front_bank_crossframe_solids=len(merged.Solids),handlay_region_mm3=s.Volume,handlay_vs_complete_root=c,
    lower_step="36 mm wide rear case access rises from 48.5 to 55.8 over the existing floor rim. Source case/exit physical sample remains open.",
    print_bbox=[solid.BoundBox.XLength,solid.BoundBox.YLength,solid.BoundBox.ZLength],physical_PASS=False),indent=1)+"\n").encode())
D.recompute();G.runCommand("Std_Save")
