"""Change the saved face locally using two real, swept ear roots and a hollow brow."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from hashlib import sha256
from tempfile import gettempdir
import json
import sys

import FreeCAD as App
import Part

HERE=Path(__file__).resolve().parent
BASIS=HERE.parent/"day21-functional-eye-face"
MODEL=BASIS/"whole-cat21-face.FCStd"
EXPECTED="3026c641fb9aa1d569c62f3d9e11e9c9d8af4a3f9fec287e8f4ebd24217c3a15"
assert sha256(MODEL.read_bytes()).hexdigest()==EXPECTED
sys.path.insert(0,str(BASIS))
from layout import V,Y,articulated,CAM_EYE,TOF_EYE,CAM_WIDE,TOF_WIDE,field,moved,write_json
from face import FACE_SECTIONS, face_loft, bez, radial

KIT=Path(gettempdir())/"robot-cat21-sculpted-head-kit"
KIT.mkdir(exist_ok=True)
BASE_ACTORS=("D21_Face","D21_Ear_R","D21_Ear_L","D21_Ear_Inset_R","D21_Ear_Inset_L",
             "D19D_PitchBack","E19_FrontShroud","H19_FrontFrame","E19_UpperYawCover",
             "D21_Camera_OEM","D21_ToF","D21_Carrier")
# Extra height at the crown and an outward bias of the upper controls.
# Lower cheek and eye geometry retain the original sections.
CROWN=((0,0),(0,0),(0,0),(0,0),(2.2,.45),(9.9,2.9),
       (7.6,2.3),(3.0,1.1),(.40,.15),(0,0),(0,0),(0,0))
# z, x, outward y, fore-aft and lateral semiaxes
ROOT=((179.2,-208.6,77.7,1.35,1.6),
      (182.7,-208.2,77.8,3.45,4.85),
      (187.0,-207.0,77.55,4.15,6.45),
      (191.3,-205.5,77.65,3.95,6.25),
      (195.4,-204.05,78.6,3.15,4.35),
      (197.85,-202.85,78.75,1.65,3.7),
      (200.25,-201.8,79.2,.80,2.45))

def saved(names):
    with ZipFile(MODEL) as z:
        doc=ET.fromstring(z.read("Document.xml"))
        values={}
        for name in names:
            props=doc.find(f"./ObjectData/Object[@name='{name}']/Properties/Property[@name='Shape']/Part")
            assert props is not None,name
            s=Part.Shape()
            s.importBrepFromString(z.read(props.attrib["file"]).decode("ascii"))
            values[name]=s
    return values

def check(s,name):
    assert len(s.Solids)==1 and s.isValid(),(name,len(s.Solids),s.isValid())
    return s

def optbox(s):
    b=s.optimalBoundingBox()
    return [round(v,3) for v in (b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)]

def point_ray(s,y,z,xlim=-162.8):
    ray=Part.makeLine(V(-275,y,z),V(xlim,y,z))
    part=s.common(ray)
    return sorted((min(v.Point.x for v in e.Vertexes),max(v.Point.x for v in e.Vertexes))
                  for e in part.Edges if e.Length>1.e-4)

def hit(a,b):
    if not a.BoundBox.intersect(b.BoundBox):return 0.
    q=a.common(b)
    assert q.isNull() or q.isValid()
    return round(q.Volume,5)

def shaped_section(section, lift, wrap, inset):
    x,w,lo,hi=section
    w=max(.8,w-inset)
    z=(lo+hi)*.5
    h=(hi-lo)*.5-inset
    peak=h+lift
    edges=[]
    for q in [
        [(0,peak),(.62*w+wrap,peak),(w,.59*h+.18*lift),(w,0)],
        [(w,0),(w,-.67*h),(.69*w,-h),(0,-h)],
        [(0,-h),(-.69*w,-h),(-w,-.67*h),(-w,0)],
        [(-w,0),(-w,.59*h+.18*lift),(-.62*w-wrap,peak),(0,peak)]
    ]:
        edges.append(bez([V(x,y,z+dz) for y,dz in q]))
    return Part.Wire(edges)

def crown_layers():
    outer=[]
    inner=[]
    for section,(lift,wrap) in zip(FACE_SECTIONS,CROWN):
        x,w,lo,hi=section
        outer.append(shaped_section(section,lift,wrap,0))
        inner.append(shaped_section((x+2.65,w,lo,hi),lift,wrap,2.65))
    new_out=check(Part.makeLoft(outer,True,False),"convex outer crown")
    new_in=check(Part.makeLoft(inner,True,False),"matching hollow")
    # Lower X/Z interface stays on the original face contour; keep more
    # than one full layer through the upper transition for a strong bond.
    band=Part.makeBox(95,185,73,V(-256,-92.5,163))
    return new_out,new_in,band

def ellipse_wire(z,x,y,rx,ry):
    k=.552284749831
    quadrants=(
        ((rx,0),(rx,k*ry),(k*rx,ry),(0,ry)),
        ((0,ry),(-k*rx,ry),(-rx,k*ry),(-rx,0)),
        ((-rx,0),(-rx,-k*ry),(-k*rx,-ry),(0,-ry)),
        ((0,-ry),(k*rx,-ry),(rx,-k*ry),(rx,0)))
    edges=[]
    for q in quadrants:
        curve=Part.BezierCurve()
        curve.setPoles([V(x+u,y+v,z) for u,v in q])
        edges.append(curve.toShape())
    return Part.Wire(edges)

def root_form():
    return check(Part.makeLoft([ellipse_wire(z,x,-y,rx,ry) for z,x,y,rx,ry in ROOT],
                              True,False),"swept ear front skirt")

def biggest(s,label,allowed):
    parts=sorted(s.Solids,key=lambda q:q.Volume,reverse=True)
    assert parts and sum(q.Volume for q in parts[1:])<=allowed, (label,[q.Volume for q in parts])
    return check(parts[0],label)

def build():
    src=saved(BASE_ACTORS)
    previous=src["D21_Face"]
    cover,cavity,band=crown_layers()
    raw=cover.common(band)
    cap=biggest(raw.cut(cavity),"hollow crown",10)
    print("crown ready",round(cap.Volume,3),flush=True)
    optics={"camera":field(CAM_EYE,(4.25,4.25),CAM_WIDE),
            "ToF":field(TOF_EYE,(4.10,2.40),TOF_WIDE)}
    original=face_loft(FACE_SECTIONS)
    # Preserve all machined sections and the original rear lip. The added
    # hood occupies new exterior volume, and rejoins the existing skin
    # where the two surfaces cross along the tapered transition.
    extension=cap.cut(original)
    # Reuse the exact rolled cups that formed the two existing eye
    # surrounds. The optical frusta alone cannot preserve the visible rims.
    cups=[radial([(-254,34.5),(-240,34),(-233,32.3),(-226,26.2),
                  (-221.0,19.9),(-219.8,19.7)],y,142) for y in (-40.,40.)]
    for cup in cups:
        extension=extension.cut(cup)
    for obstacle in (*optics.values(),src["D19D_PitchBack"],src["D21_Ear_R"],
                     src["D21_Ear_L"],src["D21_Ear_Inset_R"],src["D21_Ear_Inset_L"]):
        if hit(extension,obstacle)>0:
            extension=extension.cut(obstacle)
    # At the first trial's +20/+10 stop the only contact was the
    # front frame against the deep temple return. Test the same contact
    # in the local frame and relieve only newly added material.
    frame=moved(src["H19_FrontFrame"],articulated(20,10).inverse())
    touch=extension.common(frame)
    relief=[]
    for item in touch.Solids:
        if item.Volume<.0001:
            continue
        x0,y0,z0,x1,y1,z1=optbox(item)
        assert x0>-201 and x1<-188 and y1<-68 and 189<z0<z1<203,optbox(item)
        spare=.23
        name=Part.makeBox(x1-x0+2*spare,y1-y0+2*spare,z1-z0+2*spare,
                          V(x0-spare,y0-spare,z0-spare))
        extension=extension.cut(name).cut(name.mirror(V(),Y))
        relief.append({"actual_first_contact_mm3":item.Volume,"tool_bounds_mm":optbox(name)})
    print("external extension",round(extension.Volume,3),"relief",relief,flush=True)
    mask=biggest(previous.fuse(extension,1.e-6),"fused crown skin",35)
    print("crown fuse",round(mask.Volume-previous.Volume,3),flush=True)
    assert mask.Volume>previous.Volume+800
    root=root_form()
    right=src["D21_Ear_R"]
    both={"temple_return_relief":relief,"ear_brim_to_skirt_integral_overlap_mm3":hit(root,right),
          "front_temple_before_seat_mm3":hit(root,mask)}
    print("root gate",both,flush=True)
    assert both["ear_brim_to_skirt_integral_overlap_mm3"]>45
    assert both["front_temple_before_seat_mm3"]>12
    # Cut just the added root to the closed mask and the existing dark
    # insert. Do not cut the old ear through the newly sculpted skin.
    fit_root=root.cut(mask).cut(src["D21_Ear_Inset_R"])
    both["root_before_fuse_overlap_mm3"]=hit(fit_root,right)
    new_right=biggest(right.fuse(fit_root),"unified ear with matched front root",12)
    new_left=check(new_right.mirror(V(),Y),"mirrored ear")
    active={"D21_Face":mask,"D21_Ear_R":new_right,"D21_Ear_L":new_left}
    for n,g in active.items():
        print("member",n,round(g.Volume,3),optbox(g),flush=True)
        (KIT/(n+".brep")).write_bytes(g.exportBrepToString().encode("ascii"))
    write_json(KIT/"shape-ready.json",{"baseline_sha256":EXPECTED,
        "members":{n:{"bounds_mm":optbox(o),"volume_mm3":o.Volume} for n,o in active.items()}})
    return src,active,optics,cap,both

def verify(src,active,optics,cap,roots):
    mask=active["D21_Face"]
    before=src["D21_Face"]
    changes={}
    for n,delta in active.items():
        diff=delta.cut(src[n])
        assert not diff.isNull(),n
        changes[n]=diff
    shape_delta=Part.makeCompound(list(changes.values()))
    field_contacts={n:{key:hit(shape,f) for key,shape in changes.items()} for n,f in optics.items()}
    own_contacts={n:hit(shape_delta,src[n]) for n in ("D19D_PitchBack","D21_Carrier","D21_Camera_OEM","D21_ToF")}
    poses=[]
    for yaw,pitch in ((0,0),(-20,-10),(-20,10),(20,-10),(20,10)):
        turn=moved(shape_delta,articulated(yaw,pitch))
        contacts={n:hit(turn,src[n]) for n in ("E19_FrontShroud","H19_FrontFrame")}
        contacts["E19_UpperYawCover"]=hit(moved(shape_delta,articulated(0,pitch)),
                                        src["E19_UpperYawCover"])
        poses.append({"yaw":yaw,"pitch":pitch,"delta_contact_mm3":contacts})
        print("pose",poses[-1],flush=True)
    profiles={}
    for y,zs in ((0,(165,175,185,193,198,203,209,214,218)),
                 (-48,(165,175,185,193,198,203,207)),(-64,(169,177,185,193,198))):
        rows=[]
        for z in zs:
            q=point_ray(before,y,z)
            p=point_ray(mask,y,z)
            if q and p:rows.append([z,round(q[0][0],4),round(p[0][0],4)])
        profiles[str(y)]=rows
    baseline=Part.makeCompound([before,src["D21_Ear_R"],src["D21_Ear_Inset_R"]])
    updated=Part.makeCompound([mask,active["D21_Ear_R"],src["D21_Ear_Inset_R"]])
    light=[]
    for z in (190.,193.,195.,197.,199.):
        for y in (-77.,-79.):
            q=point_ray(baseline,y,z,-174)
            p=point_ray(updated,y,z,-174)
            light.append({"yz_mm":[y,z],"source_intervals_x":q,"updated_intervals_x":p})
    roots["final_seat_positive_volume_mm3"]=hit(mask,active["D21_Ear_R"])
    roots["seat_contact_with_0p15mm_back_toward_temple_mm3"]=hit(
       mask,moved(active["D21_Ear_R"],App.Placement(V(.15,0,0),App.Rotation())))
    result={"basis_sha256":EXPECTED,"pass_name":"short-root-original-rolled-cups","scoped_geometry":{"crown":[list(q) for q in CROWN],
        "ear_root_right":[list(q) for q in ROOT],"crown_nominal_layer_x_mm":2.65,
        "actual_added_mm3":{n:round(s.Volume,3) for n,s in changes.items()},
        "crown_raw_layer_mm3":round(cap.Volume,3)},
        "section_profiles_mm":profiles,"ear_front_rays":light,"ear_nominal_joint":roots,
        "added_material_vs_optical_fields_mm3":field_contacts,"added_material_vs_moving_neighbors_mm3":own_contacts,
        "five_pose_delta_mm3":poses,"physical_fit":None,"print_release":False,
        "inherited_open":["FFC200 routing","M2 and production ear/mask retention"]}
    write_json(HERE/"scoped-proof.json",result)
    print("PROOF",field_contacts,own_contacts,roots,flush=True)

if __name__=="__main__":
    verify(*build())
