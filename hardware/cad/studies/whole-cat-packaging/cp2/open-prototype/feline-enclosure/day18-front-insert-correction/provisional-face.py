"""Sculpt two sensor wells in the moving face, using the complete native sensors."""
import FreeCAD as A,Part,json,math,hashlib
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
assert Path(D.FileName).resolve()==(P/"front-insert.FCStd").resolve()
assert not D.getObject("INSERT_OPTICAL_FACE")
def ell(x,y,z,rx,ry,rz):
    s=Part.makeSphere(1);m=A.Matrix();m.A11,m.A22,m.A33=rx,ry,rz
    s=s.transformGeometry(m);s.translate(V(x,y,z));return s
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
lobes=[(-158,0,150,64,77,64),(-204,-14,111,20,25,24),(-204,14,111,20,25,24)]
def envelope(d):
    ss=[ell(x,y,z,a-d,b-d,c-d) for x,y,z,a,b,c in lobes]
    return ss[0].multiFuse(ss[1:]).removeSplitter()
def frustum(x,y,z,hy,hz,ah,av):
    wires=[]
    for xx in [x+.01,x-58]:
        dx=max(0,x-xx);w=hy+dx*math.tan(math.radians(ah));h=hz+dx*math.tan(math.radians(av))
        pts=[V(xx,y-w,z-h),V(xx,y+w,z-h),V(xx,y+w,z+h),V(xx,y-w,z+h)]
        wires.append(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges))
    return Part.makeLoft(wires,True,True)
opt=P.parent/"day18-optical-local-apertures"/"optical-local-apertures.json"
guide=json.loads(opt.read_bytes())
tof=D.VL53L5CX
seed=guide["tof"]["mask_guide"]
verts=[tof.Placement.multVec(V(x,y,2.566)) for x in seed["seed_x_limits_mm"] for y in seed["seed_y_limits_mm"]]
cy=sum(v.y for v in verts)/4;cz=sum(v.z for v in verts)/4
ty=(max(v.y for v in verts)-min(v.y for v in verts))/2
tz=(max(v.z for v in verts)-min(v.z for v in verts))/2
tx=verts[0].x
assert abs(tx-tof.Shape.BoundBox.XMin)<.02
camera=frustum(-201,0,145,4,4,51,33.5)
rays=frustum(tx,cy,cz,ty,tz,22.5,22.5)
# Cavity front and back surfaces both flare to the actual optical profiles.
def wells(d):
    return ell(-242,0,145,38+d,42+d,30+d).fuse(ell(-247,cy,cz,33.15+d,34+d,19+d))
outer=envelope(0);inner=envelope(1.6)
frontcap=outer.cut(wells(0)).cut(inner.cut(wells(1.6))).common(box(-250,-90,63,48.0,180,170))
frontcap=frontcap.cut(camera).cut(rays)
original=D.F3_HEAD_FRONT.Shape
remaining=original.cut(box(-260,-100,60,57.75,200,190))
s=remaining.fuse(frontcap).removeSplitter()
assert not s.isNull() and s.isValid()
o=D.addObject("PartDesign::Feature","INSERT_OPTICAL_FACE");o.Shape=s
o.ViewObject.ShapeColor=(.16,.17,.19);o.ViewObject.DisplayMode="Shaded";D.F3_HEAD_FRONT.ViewObject.Visibility=False
reserve=D.TOF_FULL14x26x26_INSTALLATION_CAPACITY_NOT_PRINT
assert abs(reserve.Shape.BoundBox.XMin+187)<.01
reserve.Placement=A.Placement(V(-24,0,0),A.Rotation()).multiply(reserve.Placement)
r=dict(source_sha256=hashlib.sha256(opt.read_bytes()).hexdigest(),camera_reference=[-201,0,145],tof_reference=[tx,cy,cz],
       ToF_world_seed_HV=[2*ty,2*tz],note="STEP placed axes measured in world; both package windows included. Installed 14x26x26 field now moves with true pitch.",
       face_solids=len(s.Solids),valid=s.isValid(),face_vs_camera_full=s.common(D.CAMERA_FULL_INSTALLATION_CAPACITY_RELOCATED_NOT_PRINT.Shape).Volume,
       face_vs_ToF_full=s.common(reserve.Shape).Volume,face_vs_cam_ray=s.common(camera).Volume,face_vs_ToF_ray=s.common(rays).Volume,
       unresolved="real camera pupil/AF/corner rays; both ToF TX/RX origins, corner illumination and crosstalk; verify actual mask on/off on real parts",physical_PASS=False)
(P/"face-apertures.json").write_bytes((json.dumps(r,indent=1)+"\n").encode())
D.recompute();D.save();print("OPTICAL FACE",r)
