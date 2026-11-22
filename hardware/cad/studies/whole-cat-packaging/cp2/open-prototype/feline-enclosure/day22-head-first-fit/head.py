"""Head-local additions for the 22 November first-fit kit."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from tempfile import gettempdir
from math import cos, sin, pi, sqrt
import sys
import json
import FreeCAD as App
import Part

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/"day21-sculpted-head-ear-roots/whole-cat21-sculpted-head.FCStd"
ORIGINAL=HERE.parent/"day21-functional-eye-face"
sys.path.insert(0,str(ORIGINAL))
from layout import V,X,Y,Z,box,sha,bounds,moved,articulated,field,CAM_EYE,TOF_EYE,CAM_WIDE,TOF_WIDE,write_json
from face import FACE_SECTIONS,face_loft

SHA="18c690a253ac8c0270ca4f9e4a49a492b85cccd51176696f4292b3ae9c53dd98"
KIT=Path(gettempdir())/"robot-cat22-head-kit"
KIT.mkdir(exist_ok=True)
MASK="D21_Face"
BACK="D19D_PitchBack"
CARRY="D21_Carrier"
POSES=((0,0),(-20,-10),(-20,10),(20,-10),(20,10))
ASSORTMENT={"D21_Ear_L","D21_Ear_R","D21_Ear_Inset_L","D21_Ear_Inset_R",
            "D21_Nose","D21_Rim_Cam","D21_Rim_ToF","D21_Insert_Cam","D21_Insert_ToF"}

def saved(names):
    assert sha(PRIOR)==SHA
    with ZipFile(PRIOR) as f:
        doc=ET.fromstring(f.read("Document.xml"))
        refs={}
        for n in names:
            p=doc.find(f'./ObjectData/Object[@name="{n}"]/Properties/Property[@name="Shape"]/Part')
            assert p is not None,n
            s=Part.Shape()
            s.importBrepFromString(f.read(p.get("file")).decode("ascii"))
            refs[n]=s
        return refs

def hit(a,b):
    if not a.Solids or not b.Solids or not a.optimalBoundingBox().intersect(b.optimalBoundingBox()):
        return 0.
    c=a.common(b)
    assert c.isNull() or c.isValid()
    return round(c.Volume,5)

def bound(s):
    b=s.optimalBoundingBox()
    return [round(v,4) for v in (b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)]

def solid(s,label):
    assert len(s.Solids)==1 and s.isValid(),(label,len(s.Solids),round(s.Volume,3))
    return s

def cyl(p,r,l,d):
    return Part.makeCylinder(r,l,p,d)

def hw_washer(p,d):
    return cyl(p,2.5,.5,d).cut(cyl(p,1.12,.5,d))

def hexagon(p,d,r,l):
    transverse=Z.cross(d)
    vertices=[p+r*cos(i*pi/3)*transverse+r*sin(i*pi/3)*Z for i in range(6)]
    return Part.Face(Part.Wire(Part.makePolygon(vertices+[vertices[0]]).Edges)).extrude(d*l)

def hw_nut(p,d):
    return hexagon(p,d,4/sqrt(3),1.6).cut(cyl(p,1.,1.6,d))

def screw(under,d,length):
    return cyl(under,1.,length,d).fuse(cyl(under,1.9,2,-d))

def mirror_if(s,sign):
    return s if sign>0 else s.mirror(V(),Y)

def push(s,items,label):
    return solid(s.multiFuse(items),label)

def stock_witness(a,b):
    return {"overlap_mm3":hit(a,b),"added_bounds_mm":bound(b)}

def build():
    src=saved({MASK,BACK,CARRY,*ASSORTMENT,"D21_Camera_OEM","D21_ToF"})
    skin=src[MASK]
    cranial=src[BACK]
    carrier=src[CARRY]
    outer=face_loft(FACE_SECTIONS)
    new_mask=[]
    new_back=[]
    new_carrier=[]
    references={}
    stack=[]
    for sign,suffix in ((1,"L"),(-1,"R")):
        # Receiver pair: source-supported optical frame carries the face.
        # The two inward screw heads are accessible before the rear rim is
        # fitted. Captive nuts and washers slide in from the rear of the mask.
        v=lambda x,y,z:V(x,sign*y,z)
        axis=sign*Y
        # A curved, broad contour-following rib pushes the contact into
        # the thick shell in shear. Stop its inward end at the carrier.
        raw=box(-186.,28.4,150.5,10.,61.6,9.).common(outer)
        raw=mirror_if(raw,sign)
        seat=cyl(v(-180.6,28.4,155),4.3,7.5,axis)
        rib=raw.fuse(seat)
        cbit=cyl(v(-180.6,19.,155),4.15,9.20,axis)
        clearance=cyl(v(-180.6,18.3,155),1.16,17.1,axis)
        # Rear-opening nut and washer pockets. Side wall remains on
        # both Z faces, so the stack cannot pull through the carrier.
        nutslot=mirror_if(box(-182.99,31.55,152.88,7.4,1.80,4.24),sign)
        washerslot=mirror_if(box(-183.22,31.05,152.38,7.8,.55,5.24),sign)
        tipslot=mirror_if(box(-181.92,33.10,153.68,6.8,2.5,2.64),sign)
        rib=rib.cut(carrier).cut(clearance).cut(nutslot).cut(washerslot).cut(tipslot)
        cbit=cbit.cut(clearance)
        new_mask.append(rib)
        new_carrier.append(cbit)
        receiver_metal=[screw(v(-180.6,18.50,155),axis,16.),
            hw_washer(v(-180.6,18.50,155),axis),
            hw_washer(v(-180.6,31.05,155),axis),hw_nut(v(-180.6,31.55,155),axis)]
        for key,p in zip(("Screw","HeadWasher","NutWasher","Nut"),receiver_metal):
            references[f"D22_Root_{suffix}_{key}"]=p
        driver=cyl(v(-180.6,16.49,155),2.0,14.0,-axis)
        references[f"D22_Root_{suffix}_Driver"]=driver
        row={"stage":"mask onto optical carrier","side":suffix,"axis":list(axis),
             "rib":stock_witness(skin,rib),"carrier_boss":stock_witness(carrier,cbit),
             "head_and_nut_underfaces_at_abs_Y_mm":[18.5,31.55],"tip_past_nut_mm":1.35,
             "hardware":"M2×16, DIN-style hex nut AF4, two OD5 × 0.5 washers",
             "side_before_cable_lay_and_pitchback":True}
        assert row["rib"]["overlap_mm3"]>18 and row["carrier_boss"]["overlap_mm3"]>20,row
        stack.append(row)

        # Rear shell uses the two real source M2×16 head-back datums.
        # Integral block and key under each existing lobe; flat bearings
        # are set at x=-169/-157.25 to preserve the source steel stack.
        # The negative lower cheek of the rear shell is the retained
        # pitch-MG lead opening (x -178..-135, y -96..-53, z 109..157).
        # Stand the opposite retaining lug on the intact rim above it.
        yy,zz=(73.,145.) if sign>0 else (70.,170.)
        v=lambda x,y,z:V(x,sign*(y+yy-73),z+zz-145)
        def shift(p):
            p.translate(V(0,yy-73,zz-145))
            return mirror_if(p,sign)
        aft_raw=shift(box(-169.,68.7,137.4,8.1,8.65,15.2)).common(outer)
        key=shift(box(-164.65,69.4,140.7,2.92,6.80,8.60))
        face_lug=aft_raw.fuse(key)
        back_base=shift(box(-161.73,69.8,139.9,4.48,6.60,10.2))
        back_web=shift(box(-162.90,73.65,138.4,5.65,2.35,13.20))
        back_lug=back_base.fuse(back_web)
        bore=cyl(v(-173.2,73,145),1.16,22.,X)
        pocket=shift(box(-164.9,69.15,140.45,3.17,7.3,9.10))
        new_mask.append(face_lug.cut(bore))
        new_back.append(back_lug.cut(bore).cut(pocket))
        headward=-X
        screw_base=v(-156.75,73,145)
        rear_metal=[screw(screw_base,headward,16),
            hw_washer(v(-156.75,73,145),headward),
            hw_washer(v(-169.,73,145),headward),hw_nut(v(-169.5,73,145),headward)]
        for tag,p in zip(("Screw","HeadWasher","NutWasher","Nut"),rear_metal):
            references[f"D22_Back_{suffix}_{tag}"]=p
        references[f"D22_Back_{suffix}_Driver"]=cyl(v(-154.74,73,145),2.70,31.,X)
        row={"stage":"rear rim onto mask","side":suffix,"axis":[-1,0,0],
             "front_lobe":stock_witness(skin,face_lug),"back_lobe":stock_witness(cranial,back_lug),
             "hardware":"M2×16, DIN-style nut AF4, two OD5 × 0.5 washers",
             "tip_past_nut_mm":1.65}
        assert row["front_lobe"]["overlap_mm3"]>18 and row["back_lobe"]["overlap_mm3"]>18,row
        stack.append(row)
        print("joint bearing stock",suffix,stack[-2:],flush=True)
    shell=push(skin,new_mask,"reversible retained mask")
    rear=push(cranial,new_back,"rear skull with actual rooted support")
    frame=push(carrier,new_carrier,"optics carrier with M2 bearings")
    for sign,suffix in ((1,"L"),(-1,"R")):
        v=lambda x,y,z:V(x,sign*y,z)
        d=sign*Y
        motion_sleeve=cyl(v(-180.6,18.3,155),1.16,17.6,d)
        # The earlier mask retained a partial lug at this exact
        # cross-section. Finish-pocket the complete hardware and the
        # actual carrier rail in the bounded inward fit region.
        m_clip=box(-186,sign*29.6-2.15,151.0,10,4.3,8.0)
        shell=solid(shell.cut(motion_sleeve).cut(carrier.common(m_clip)),"mask clear root bores")
        wash=cyl(v(-180.6,31.05,155),2.625,.57,d)
        nut=hexagon(v(-180.6,31.55,155),d,2.49,1.86)
        tip=cyl(v(-180.6,33.1,155),1.25,2.55,d)
        shell=solid(shell.cut(wash).cut(nut).cut(tip),"full captive root hardware pockets")
        shell=solid(shell.cut(box(-186,28.35,152.35,10,2.02,4.9).common(carrier)),"old positive rib relieved")

        access=cyl(v(-180.6,1.95,155),2.62,17.05,d)
        frame=solid(frame.cut(motion_sleeve).cut(access),"carrier clear bores and washer seats")
        yy,zz=(73.,145.) if sign>0 else (70.,170.)
        ar=cyl(v(-173.3,yy,zz),1.16,22.,X)
        shell=solid(shell.cut(ar),"mask clear back bores")
        rear=solid(rear.cut(ar).cut(cyl(v(-157.24,yy,zz),2.75,35.,X)),"back full head/tool access")
    # The two keys are borne by flat x=-161.73 end faces. Relieve only
    # the seated overlap and the old incidental rim contact, inside the
    # new side pockets, without touching the approved visible mask.
    for r in (box(-166.1,67,130.,5.0,10.5,28.),
              box(-166.1,-75,161.5,5.0,11.,17.5)):
        rear=solid(rear.cut(shell.common(r)),"matched keyed rear shell")
    actors={MASK:shell,BACK:rear,CARRY:frame}
    inject(actors,references)
    write_json(KIT/"mechanical-ready.json",{"sha":SHA,"actors":{n:{"volume_mm3":s.Volume,
              "walls":bound(s)} for n,s in actors.items()},"references":list(references),"joints":stack})
    return src,actors,references,stack

def inject(actors,refs):
    for n,s in (actors|refs).items():
        assert s.isValid(),n
        (KIT/(n+".brep")).write_bytes(s.exportBrepToString().encode("ascii"))

if __name__=="__main__":
    build()
