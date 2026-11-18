"""Form one recessed optical cheek and partition the forehead surface for paint."""
from pathlib import Path
import json,math
import FreeCAD as A,FreeCADGui as G,Part
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
assert Path(D.FileName).resolve()==(P/"body-reception.FCStd").resolve()
def ell(c,r):
    m=A.Matrix();m.A11,m.A22,m.A33=r
    s=Part.makeSphere(1).transformGeometry(m);s.translate(V(*c));return s
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def envelope(d):
    def part(c,rad):return ell(c,tuple(v-d for v in rad))
    return part((-158,0,150),(64,77,64)).fuse(part((-200,0,112),(24,38,25))).removeSplitter()
def window(x,y,z,hy,hz,ah,av):
    wires=[]
    for xx in (x+.01,x-55):
        h=hy+max(0,x-xx)*math.tan(math.radians(ah));v=hz+max(0,x-xx)*math.tan(math.radians(av))
        pts=[V(xx,y-h,z-v),V(xx,y+h,z-v),V(xx,y+h,z+v),V(xx,y-h,z+v)]
        wires.append(Part.makePolygon(pts+[pts[0]]))
    return Part.makeLoft(wires,True,True)
previous=json.loads((P.parent/"day18-front-insert-correction"/"face-apertures.json").read_bytes())
ref=previous["tof_reference"];w,h=previous["ToF_world_seed_HV"]
cam=window(*previous["camera_reference"],4,4,51,33.5);tof=window(*ref,w/2,h/2,22.5,22.5)
# A single concave mask gives both apertures depth from the source optical
# packages. Keep a positive thickness across the area between the apertures.
def well(d):return ell((-254,0,141),(50+d,47+d,68+d))
cap=envelope(0).cut(well(0)).cut(envelope(1.6).cut(well(1.6))).common(box(-245,-90,60,53,180,170))
old=D.INSERT_OPTICAL_FACE
seam=old.Shape.cut(box(-250,-105,60,57.75,210,180))
face=seam.fuse(cap).cut(cam).cut(tof).cut(D.TOF_FULL14x26x26_INSTALLATION_CAPACITY_NOT_PRINT.Shape).removeSplitter()
assert face.isValid() and len(face.Solids)==1,("face",len(face.Solids))
def eye(y,ry,rz):
    s=Part.makeCylinder(1,55,V(0,0,0),V(1,0,0));m=A.Matrix();m.A22=ry;m.A33=rz
    s=s.transformGeometry(m);s.translate(V(-230,y,160));return s
eyes=[eye(side*43,ry,rz) for side in (-1,1) for ry,rz in ((16,19),(13.4,16.4))]
coated=face.Solids[0]
coated.exportBrep(str(P/"cheek-before-paint.brep"))
Part.makeCompound(eyes).exportBrep(str(P/"eye-boundaries.brep"))
colors=[(.16,.17,.19,1.)]*len(coated.Faces);counts={}
o=D.addObject("PartDesign::Feature","BR_COMMON_OPTICAL_MASK");o.Shape=coated;o.ViewObject.DisplayMode="Shaded";o.ViewObject.DiffuseColor=colors
old.ViewObject.Visibility=False
for f in D.Objects:
    if f.Name.startswith("F3_PAINT_"):f.ViewObject.Visibility=False
notes=dict(face_solids=len(coated.Solids),valid=coated.isValid(),paint_faces=counts,source_optical=previous["source_sha256"],full_Camera_reserve_common=coated.common(D.CAMERA_FULL_INSTALLATION_CAPACITY_RELOCATED_NOT_PRINT.Shape).Volume,
    full_ToF_reserve_common=coated.common(D.TOF_FULL14x26x26_INSTALLATION_CAPACITY_NOT_PRINT.Shape).Volume,
    cam_window_common=coated.common(cam).Volume,tof_window_common=coated.common(tof).Volume,
    physical_condition="Delivered ToF TX/RX openings and camera corner rays through a real mask. Keep the complete PCB and both installation volumes.",physical_PASS=False)
(P/"common-cheek-mask.json").write_bytes((json.dumps(notes,indent=1)+"\n").encode())
D.recompute();G.runCommand("Std_Save")
