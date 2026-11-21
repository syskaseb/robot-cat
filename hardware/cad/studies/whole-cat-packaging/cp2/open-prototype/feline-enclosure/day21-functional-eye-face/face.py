"""Editable, source-sized face parts for 20H. Forward is -X."""
import math
from pathlib import Path
import sys

import FreeCAD as A
import Part

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from layout import (CAM_BORES,CAM_EYE,CAM_WIDE,HERE,IRIS_X,TOF_EYE,TOF_WIDE,
                    V,X,Y,Z,articulated,bounds,box,camera_geometry,cylinder,field,
                    load_saved,moved,solid_hit,tof_geometry,write_json)

FACE_SECTIONS = [
    (-236.2,4,141,161),(-235.4,18,130,173),(-233,32,115,185),
    (-230,48,101,196),(-225,62,90,205),(-217,74,83,212),
    (-208,83,77.8,218),(-196,88,77,220),(-182,86,80,218),
    (-173,81.8,84.8,215),(-165,77.4,89.3,212.5),(-162.7,76.5,90,212)
]
MASK_WALL = 2.2
EAR_POINTS = [(32,201),(39,213),(56,231),(69,243),(77,242),(82,232),
              (85,215),(85,194),(82,178),(75,185),(55,193)]
NOSE_POINTS = [(0,9),(6.4,8.6),(10.6,6.8),(12,4),(9.4,.6),(5.8,-1.6),
               (3.4,-5.5),(0,-7.1),(-3.4,-5.5),(-5.8,-1.6),(-9.4,.6),(-12,4),
               (-10.6,6.8),(-6.4,8.6)]

def bez(points):
    curve=Part.BezierCurve()
    curve.setPoles(points)
    return curve.toShape()

def crown(section, inset=0.):
    x,w,lo,hi=section
    w=max(.8,w-inset)
    z=(lo+hi)*.5
    h=(hi-lo)*.5-inset
    top,bottom=.62,.69
    edges=[]
    for q in [
        [(0,h),(top*w,h),(w,.59*h),(w,0)],
        [(w,0),(w,-.67*h),(bottom*w,-h),(0,-h)],
        [(0,-h),(-bottom*w,-h),(-w,-.67*h),(-w,0)],
        [(-w,0),(-w,.59*h),(-top*w,h),(0,h)]
    ]:
        edges.append(bez([V(x,y,z+dz) for y,dz in q]))
    return Part.Wire(edges)

def profile_wire(points, fn, tightness=.15):
    p=[fn(u,v) for u,v in points]
    tangent=[(p[(i+1)%len(p)]-p[i-1])*tightness for i in range(len(p))]
    return Part.Wire([bez([a,a+tangent[i],b-tangent[(i+1)%len(p)],b])
            for i,(a,b) in enumerate(zip(p,p[1:]+p[:1]))])

def face_loft(sections,inset=0.):
    return Part.makeLoft([crown(q,inset) for q in sections],True,False)

def radial(rows,y,z):
    wires=[Part.Wire([Part.makeCircle(r,V(x,y,z),X)]) for x,r in rows]
    return Part.makeLoft(wires,True,False)

def one(name,s):
    if not s.isValid() or len(s.Solids)!=1:
        raise ValueError((name,s.isValid(),len(s.Solids)))
    return s

def fuse(s,others):
    return s.multiFuse(others).removeSplitter()

def ann(x,y,z,r,h,inner):
    return cylinder(x,y,z,r,h).cut(cylinder(x-.02,y,z,inner,h+.04))

def ellipsoid(center,radii):
    # Select a longitudinal seam away from the touching cheek footprints.
    s=Part.makeSphere(1)
    m=A.Matrix()
    m.A11,m.A22,m.A33=radii
    s=s.transformGeometry(m)
    s.translate(center)
    return s

def cushion(sign):
    c=V(-226.5,sign*20.4,105.2)
    s=ellipsoid(c,(21.2,21.8,18.7))
    s.rotate(c,X,-sign*9)
    return s

def ear_loft(sign,rows,ruled):
    wires=[]
    for x,scale in rows:
        def at(y,z):
            a=56+(y-56)*scale
            b=208+(z-208)*scale
            return V(x+.19*(b-208)+.11*(a-56),sign*a,b)
        wires.append(profile_wire(EAR_POINTS,at,.14))
    return Part.makeLoft(wires,True,ruled)

def ear(sign,head):
    outer=ear_loft(sign,[(-210,.91),(-205,1),(-194,.90),(-182,.59)],False)
    bowl=ear_loft(sign,[(-222,.86),(-209,.865),(-202,.78),(-197,.61)],True)
    outer_rim=one("ear wall",outer.cut(bowl).removeSplitter())
    lining=ear_loft(sign,[(-202.4,.682),(-199.1,.696),(-196.65,.607)],True)
    lining=lining.common(outer).cut(outer_rim).cut(head).removeSplitter()
    parts=sorted(lining.Solids,key=lambda s:s.Volume,reverse=True)
    print("ear root / dark inset",round(solid_hit(outer_rim,head),3),
          [round(s.Volume,3) for s in parts],flush=True)
    assert parts and parts[0].Volume>1500
    # The mask hides the lower disconnected pocket. Seat one continuous inlay.
    return outer_rim,one("ear inset",parts[0])

def nose_loft():
    wires=[]
    for x,s in [(-251,.23),(-249.8,.76),(-247.7,1),(-244.6,.93),(-239.1,.58),(-237,.29)]:
        wires.append(profile_wire(NOSE_POINTS,lambda y,z:V(x,y*s,117.4+z*s),.15))
    return Part.makeLoft(wires,True,False)

def make_mask(src,optical):
    raw=one("outer face",face_loft(FACE_SECTIONS))
    inside=[(x+2.65,w,lo,hi) for x,w,lo,hi in FACE_SECTIONS]
    inner=one("inner void",face_loft(inside,2.65))
    skin=raw.cut(inner)
    cups=[]
    seats=[]
    for y in (40.,-40.):
        # Rounded brow falls smoothly into a recess, then onto a thin lip.
        recess=radial([(-254,34.5),(-240,34),(-233,32.3),(-226,26.2),(-221.0,19.9),(-219.8,19.7)],y,142)
        support=radial([(-248,37),(-233,36.4),(-225,30.4),(-220,24),(-215.2,19.7)],y,142)
        cups.append(recess)
        seats.append(raw.common(support))
    skin=fuse(skin,seats).cut(Part.makeCompound(cups))
    for y in (40.,-40.):
        skin=skin.cut(cylinder(-221.30,y,142,19.37,2.72))
        skin=skin.cut(cylinder(-220.11,y,142,17.53,1.95))
        skin=skin.cut(cylinder(-218.18,y,142,16.63,7.4))
    # These broad integral cheeks are the two front volumes. Hollow their
    # interiors after joining to the mask so they contribute little mass.
    cheeks=[cushion(sign) for sign in (-1,1)]
    skin=fuse(skin,cheeks)
    for sign in (-1,1):
        c=V(-226.3,sign*20.4,105.4)
        hollow=ellipsoid(c,(18.5,19.1,15.8))
        hollow.rotate(c,X,-sign*9)
        skin=skin.cut(hollow)
    nose=nose_loft()
    owner=skin
    nose=nose.cut(owner).removeSplitter()
    # Preserve a flat saddle under the nose and a concealed locating stem.
    stem=cylinder(-241,0,118.5,3.05,8.4)
    nose=nose.fuse(stem).removeSplitter()
    skin=skin.cut(stem.copy().fuse(cylinder(-241.2,0,118.5,3.24,9.0)))
    for f in optical.values():skin=skin.cut(f)
    # The inherited pitch rear rim is the authoritative mating section.
    skin=skin.cut(src["D19D_PitchBack"]).removeSplitter()
    print("shell fragments",[(round(s.Volume,3),bounds(s)) for s in skin.Solids],flush=True)
    print("nose fragments",[(round(s.Volume,3),bounds(s)) for s in nose.Solids],flush=True)
    skin=sorted(skin.Solids,key=lambda s:s.Volume,reverse=True)
    assert sum(s.Volume for s in skin[1:])<1400
    return one("shell",skin[0]),clear_nose(nose,optical["Cam"]),raw

def clear_nose(nose,camera_field):
    # The right/left cut is paired so the small rounded triangle stays centred.
    # The full corner field at the projecting nose is wider than at the iris.
    result=nose.cut(camera_field).cut(camera_field.mirror(V(),Y)).removeSplitter()
    return one("nose outside the selected camera field",result)

def eyes(optical):
    solids={}
    for key,y in (("Cam",40.),("ToF",-40.)):
        lip=Part.makeTorus(18.55,.78,V(IRIS_X-.27,y,142),X)
        lip=lip.fuse(ann(IRIS_X+.06,y,142,19.10,1.32,17.35)).removeSplitter()
        # Broad charcoal insert sets into the iris and stops at the axial
        # locating face; the through holes are defined by the two real fields.
        dark=cylinder(IRIS_X+.28,y,142,17.28,1.52)
        if key=="Cam":
            dark=dark.cut(cylinder(IRIS_X-.2,y,142,5.9,3))
        dark=dark.cut(optical[key]).removeSplitter()
        solids["D21_Rim_"+key]=(one(key+" rim",lip),(.76,.372,.057))
        solids["D21_Insert_"+key]=(one(key+" insert",dark),(.035,.037,.040))
    return solids

def arm_plate(items):
    return fuse(items[0],items[1:])

def carrier(src,cp,tp,tof_board):
    base=src["D19D_OpticsCarrier"]
    bits=[base]
    cutters=[]
    cam_rear=-210.225
    for y,z in CAM_BORES:
        bits.append(cylinder(cam_rear,y,z,2.35,6.15))
        cutters.append(cylinder(cam_rear-.25,y,z,1.13,13))
    bits.extend([box(-204.2,25.9,139.0,8.9,28.4,6.25),
                 box(-198,24.5,139,20.6,5.8,6.25),
                 box(-181,19.0,139,5.1,11.1,18.25)])
    targets=[tp.multVec(V(-206.,-3.81,z)) for z in (96.54,109.24)]
    for p in targets:
        bits.append(cylinder(p.x,p.y,p.z,2.4,4.4))
        cutters.append(cylinder(p.x-.2,p.y,p.z,1.13,14))
    bits.extend([box(-211.55,-49.2,136.6,10.8,18.5,5.8),
                 box(-202,-34.4,136.6,23.2,4.5,5.8),
                 box(-182,-33.9,136.6,5.5,16.3,14.6),
                 box(-182,-20.5,137.3,4.8,5.0,13.4)])
    c=arm_plate(bits)
    c=c.cut(Part.makeCompound(cutters)).removeSplitter()
    return c,targets

def metal_poses(src,tof_pose):
    # Preserve the two complete M2 triples for each existing module.
    old_camera_mount=V(-189.72,-10.5,144.9)
    new_camera_mount=V(-210.896,50.5,142.1)
    spin=A.Rotation(X,180)
    cam_pose=A.Placement(new_camera_mount-spin.multVec(old_camera_mount),spin)
    return {n:moved(s,cam_pose if n.startswith("CAM_primary") else tof_pose)
            for n,s in src.items() if n.startswith(("CAM_primary","TOF_primary"))}

def load_actors():
    actors=["D19D_Face","D19D_OpticsCarrier","D19D_PitchBack","VL53L5CX",
            "E19_FrontShroud","E19_UpperYawCover","MG92B_Head_pitch","D19D_YawSaddle",
            "H19_FrontFrame","F19_ForeCap","C19_FFC190","D19D_ToF","PITCH_HORN_ROOF_JOURNAL",
            "PITCH_SHAFT_FRAME_POSITIVE_CROSSPIN_full_screw"]
    for y in ("10_5","_10_5"):
        actors.extend("CAM_primary_upper_"+y+"_"+s for s in
                      ("fullM2x12","fullnut","lowerwasher","upperwasher"))
    for k in ("116_54","129_24"):
        actors.extend("TOF_primary_"+k+"_"+s for s in
                      ("fullM2x10","fullnut","lowerwasher","upperwasher"))
    src=load_saved(actors)
    assert set(src)==set(actors),set(actors)-set(src)
    return src

def mask_retention(shell,raw,carrier_shape,back):
    """Root two short-access ribs at the inherited lateral M2 seats."""
    steel={}
    ribs=[]
    for sign,suf in ((1,"L"),(-1,"R")):
        y0=28.35 if sign>0 else -93
        rail=box(-183.6,y0,152.35,6.3,64.65,5.15).common(raw)
        rail=rail.cut(carrier_shape).cut(back)
        axis=-sign*Y
        at=V(-180.6,sign*35.8,155)
        clearance=Part.makeCylinder(1.16,18,at,axis)
        rail=rail.cut(clearance)
        assert solid_hit(shell,rail)>5
        ribs.append(rail)
        shaft=Part.makeCylinder(1.,12.,V(-180.6,sign*33.55,155),axis)
        head=Part.makeCylinder(1.9,2.,V(-180.6,sign*35.55,155),axis)
        washer=Part.makeCylinder(2.45,.50,V(-180.6,sign*33.55,155),axis).cut(shaft)
        steel["Mask_M2_reference_"+suf]=Part.makeCompound([head,shaft,washer])
    return one("primary mask with retention ribs",fuse(shell,ribs)),steel

def build():
    src=load_actors()
    co,cp,fpc=camera_geometry()
    tp,_=tof_geometry(src["VL53L5CX"])
    tof=moved(src["VL53L5CX"],tp)
    cam=moved(co,cp)
    optical={"Cam":field(CAM_EYE,(4.25,4.25),CAM_WIDE),
             "ToF":field(TOF_EYE,(4.10,2.40),TOF_WIDE)}
    shell,nose,raw=make_mask(src,optical)
    solids={"D21_Face":(shell,(.178,.181,.184)),"D21_Nose":(nose,(.105,.078,.065))}
    solids.update(eyes(optical))
    original_ear,lining=ear(-1,shell)
    mirror=original_ear.mirror(V(),Y)
    mirror_lining=lining.mirror(V(),Y)
    assert solid_hit(original_ear,shell)>100 and solid_hit(mirror,shell)>100
    # Cut a matching seat for each independent solid. A mirrored BRep fused
    # across the freeform brow lost its left crown in the earlier stitch.
    shell=one("face with matched ear seats",shell.cut(original_ear).cut(mirror).removeSplitter())
    solids["D21_Ear_R"]=(original_ear,(.195,.196,.199))
    solids["D21_Ear_L"]=(mirror,(.195,.196,.199))
    solids["D21_Ear_Inset_R"]=(lining,(.077,.080,.084))
    solids["D21_Ear_Inset_L"]=(mirror_lining,(.077,.080,.084))
    solids["D21_Face"]=(shell,(.195,.196,.199))
    c,targets=carrier(src,cp,tp,tof)
    print("carrier solids",[(round(q.Volume,2),bounds(q)) for q in c.Solids],flush=True)
    solids["D21_Carrier"]=(one("carrier",c),(.23,.24,.248))
    shell,retention=mask_retention(shell,raw,c,src["D19D_PitchBack"])
    # Reapply the two physical bores after machining the seat ribs.
    shell=one("final optical mask",shell.cut(optical["Cam"]).cut(optical["ToF"]))
    solids["D21_Face"]=(shell,(.195,.196,.199))
    metals=metal_poses(src,tp)
    metals.update(retention)
    return src,solids,cam,tof,co,cp,tp,fpc,optical,metals

if __name__=="__main__":
    result=build()
    src,solids,cam,tof,*_=result
    from tempfile import gettempdir
    scratch=Path(gettempdir())/"robot-cat21-camera-oem/native-kit"
    scratch.mkdir(exist_ok=True)
    archive={**solids,"D21_Camera_OEM":(cam,(.083,.121,.101)),"D21_ToF":(tof,(.069,.080,.076))}
    for n,s in result[-1].items():archive["D21_"+n]=(s,(.54,.54,.56))
    for name,(s,color) in archive.items():
        (scratch/(name+".brep")).write_bytes(s.exportBrepToString().encode("ascii"))
    write_json(scratch/"objects.json",{k:{"color":list(v[1]),"volume":v[0].Volume,"bounds":bounds(v[0]),"solids":len(v[0].Solids)} for k,v in archive.items()})
    print({k:(round(v[0].Volume,2),bounds(v[0])) for k,v in solids.items()},flush=True)
