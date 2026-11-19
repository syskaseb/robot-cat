"""19D complete head mask, pitch back, yaw shroud, shoulder and waist in the saved assembly."""
from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part,math,json,runpy
from zipfile import ZipFile
from xml.etree import ElementTree as ET
P=Path(__file__).parent;C=P.parent/"day19-closed-head-neck-and-module-interfaces"
D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"whole-cat19D.FCStd").resolve()
src=(C/"head-and-shoulder.py").read_text()
exec(src[src.index("def box("):src.index("def cheek_seat")])
lay=json.loads((P/"whole-lay.json").read_bytes())
grey=(.20,.205,.22);dark=(.12,.13,.145);amber=(.98,.55,.105);black=(.026,.023,.024)
records={}
def install(n,s,color,role):
    if not s.isValid() or len(s.Solids)!=1:
        raise ValueError((n,s.isValid(),len(s.Solids)))
    o=put(n,s,color,role);o.ViewObject.Visibility=True
    records[n]=dict(role=role,volume=s.Volume,solids=len(s.Solids),extents=[s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength])
    write("form-members.json",records);return s
def outer(rows,d=0):return Part.makeLoft([ring(row,d,.64) for row in rows],True,True)
def split_skin(rows,wall,front=False):
    out=outer(rows);a=list(rows)
    if front:
        x,w,l,h=rows[0];a[0]=(x+wall,w,l,h)
    return out.cut(outer(a,wall)).removeSplitter()
def polyface(pts):
    vs=[V(*p) for p in pts]
    return Part.makePolygon(vs+[vs[0]])
def whole():
    # Keep the B19 eight anchor and bearing load structure. Provide a wide flat
    # shelf and access below the tangent instead of rigid side cheeks at the return.
    floor=sh("B19_FrontFloor")
    base=box(-71.4,21.5,41,6,18.3,4.8);pillar=box(-71.3,34.8,43.5,5.9,5.1,86.4)
    rail=box(-71.3,16,127.5,22,24,3)
    def ramp(x,y,z):
        b=box(x-6,y-6,z-5.7,12,12,2.3);b=b.cut(box(x-2,y-2,z-6,4,4,4))
        b.rotate(V(x,y,z),V(1,0,0),35);return b
    S=lay["head_receiver"];B=lay["fixed_receiver"]
    fore=fused([floor,base,pillar,rail,box(-60,25.5,129.5,7,4,7.6),ramp(*B)])
    install("D19D_FrontFloor",fore,(.20,.34,.34),"four base anchors, yaw bearing bridge, open stationary tie shelf")
    original=sh("D18C_TRUE_PITCH_OPTICAL_RECEIVER").cut(box(-204,1.2,91,17.5,15,24))
    carrier=fused([original,box(-182.9,16.5,156.9,4.9,4.7,7.4),box(-182.9,16.5,162,41.8,5.8,3),box(-149.2,18.9,163.6,6,9.4,2.5),ramp(*S)])
    install("D19D_OpticsCarrier",carrier,(.20,.34,.34),"two optical boards and moving open tie shelf")
    # The eye centres and broad temple roots define the face. The small low
    # muzzle accounts for actual ToF PCB below the camera aperture.
    rows=[(-222,11,111,135),(-218,28,97,155),(-212,51,88,181),(-203,68,84,199),(-189,80,84,210),(-176,82,86,213),(-163,76.5,90,212)]
    raw=outer(rows);mask=split_skin(rows,1.55,True)
    # Two real ledges bear on the optical frame. Source camera carrier remains
    # free to receive both boards before the mask is offered from the front.
    for side in [-1,1]:
        y=side*18
        tab=box(-202,min(y,side*23),151,23,5,3.4)
        post=box(-184,min(y,side*22),151,5,4,6.8)
        cheek=box(-210,min(y,side*49),151,10,31,3.4).common(raw)
        mount=fused([tab,post,cheek]).cut(carrier)
        trial=mask.fuse(mount).removeSplitter()
        if len(trial.Solids)==1 and trial.isValid():mask=trial
    for sign,suf in [(1,"L"),(-1,"R")]:
        axis=V(-.96,.28*sign,.10);axis.normalize();center=V(-210.5,sign*42,158.5);rot=A.Rotation(V(0,0,1),axis)
        def loc(s):s.Placement=A.Placement(center,rot).multiply(s.Placement);return s
        def disc(r,z,h):return cyl((0,0,z),r,h,(0,0,1))
        # Shoulder recess around a shallow inlay. Die backs bridge the varying
        # depth of the cheek and key the eyes without a decorative raised rim.
        sleeve=loc(disc(20.7,-15,15.1).cut(disc(17.8,-16,17))).common(raw)
        trial=mask.fuse(sleeve).removeSplitter()
        if len(trial.Solids)==1 and trial.isValid():mask=trial
        mask=mask.cut(loc(disc(19.55,-1.75,29))).cut(loc(disc(17.8,-24,27)))
        iris=ell((0,0,0),(19.45,19.45,3.7)).common(box(-21,-21,0,42,42,5))
        iris=iris.fuse(disc(19.45,-1.72,1.85)).fuse(disc(17.55,-3.45,2.2)).cut(disc(11.65,-4,11))
        for yy in [-15,15]:iris=iris.cut(box(-2,yy-1.3,-3.8,4,2.6,3))
        pupil=ell((0,0,2.15),(11.55,11.55,3.4)).common(box(-13,-13,2.15,26,26,4)).fuse(disc(11.5,-3.5,5.8))
        install("D19D_Iris_"+suf,loc(iris.removeSplitter()),amber,"39 mm diameter amber inlay with recessed bearing lip")
        install("D19D_Pupil_"+suf,loc(pupil.removeSplitter()),black,"23 mm diameter black through-insert")
    # Inclined triangular pinnae with broad hollow base; root bridges the upper
    # temple rather than a narrow peg. Keep the front recess under a rear wall.
    for sign,suf in [(1,"L"),(-1,"R")]:
        def ear(x,y0,y1,tip,bz,tz):
            return polyface([(x,sign*y0,bz),(x,sign*y1,bz+1),(x,sign*tip,tz)])
        skins=[ear(-193,24,74,74,191,239),ear(-181,23,78,78,190,255),ear(-169,30,72,73,192,250)]
        shell=Part.makeLoft(skins,True,True)
        hollow=Part.makeLoft([ear(-195,29,71,72,195,235),ear(-180,29,72,75,195,247),ear(-171,34,67,70,196,241)],True,True)
        shell=shell.cut(hollow);shell=shell.cut(raw)
        if len(shell.Solids)>1:shell=max(shell.Solids,key=lambda o:o.Volume)
        # Ear heel sits on the exterior of the face; two integral tenons enter
        # their matched holes before the internal retainer is threaded.
        for yy,zz in [(43,203),(62,196)]:
            post=cyl((-184,sign*yy,zz-8),2.1,18,(0,0,1))
            trial=shell.fuse(post).removeSplitter()
            if len(trial.Solids)==1 and trial.isValid():
                shell=trial;mask=mask.cut(cyl((-184,sign*yy,zz-9),2.28,21,(0,0,1)))
        install("D19D_Ear_"+suf,shell,grey,"hollow triangular pinna on matched temple")
    nose=ell((-220,0,124),(4.8,7.2,3.6)).fuse(cyl((-220,0,124),2.2,7,(1,0,0)))
    mask=mask.cut(nose)
    install("D19D_Nose",nose.removeSplitter(),black,"short nose at central muzzle")
    with ZipFile(P.parent/"day18-body-reception-and-closed-fit/body-reception.FCStd") as z:
        xml=ET.fromstring(z.read("Document.xml"))
        for nn in ["D18C_CAM_MODEL_CLOCK_BOUND_FOV","D18C_TOF_MODEL_CLOCK_BOUND_FOV"]:
            ref=xml.find("./ObjectData/Object[@name='%s']/Properties/Property[@name='Shape']/Part"%nn).get("file")
            s=Part.Shape();s.importBrepFromString(z.read(ref).decode("ascii"));mask=mask.cut(s)
    install("D19D_Face",mask.removeSplitter(),grey,"one front mask, both original optical fields removed")
    backrows=[(-162.65,76.5,90,212),(-151,74,87,213),(-141,68,86,209),(-129,59,87,202),(-115,47,92,193)]
    back=split_skin(backrows,1.45)
    # Retain a flange joining both halves on their inside edge. Four paired
    # access slots accept tie feeds with the head open on the bench.
    rim=split_skin([(-166,74.6,92,210),(-161.8,75.6,91,211)],1.5)
    back=back.fuse(rim).removeSplitter()
    if len(back.Solids)!=1:back=split_skin(backrows,1.45)
    install("D19D_PitchBack",back,grey,"pitch moving short cranial back, open at rear")
    # A dedicated yaw cheek passes BEHIND the jaw. The outer back of the head
    # advances into its open mouth. The suspension saddle moves with the cheek.
    yawrows=[(-138,82,72,220),(-126,79,70,220),(-111,74,68,218),(-97,67,67,211)]
    hood=split_skin(yawrows,1.45)
    for sign in [-1,1]:
        plate=box(-130,min(sign*66,sign*82),110.6,9,16,2.8).common(outer(yawrows))
        t=hood.fuse(plate).removeSplitter()
        if len(t.Solids)==1 and t.isValid():hood=t
    install("D19D_YawHood",hood,dark,"intermediate yaw hood behind pitch back; open lower attachment")
    bodyrows=[(-110,91,38,220),(-98,99,27,220),(-77,104,18,211),(-54,101,17,189),(-31,99,21,172),(-5,98,23,164),(20,102,23,167)]
    aftrows=[(20.22,102,23,167),(47,104,20,172),(91,105,12,174),(145,101,8,168),(174,94,15,163),(204,61,37,148),(213,38,55,133)]
    for name,rs,fl in [("D19D_Shoulder",bodyrows,fore),("D19D_RearShell",aftrows,sh("B19_RearFloor"))]:
        out=outer(rs);skin=split_skin(rs,1.45)
        for x in [-75,120]:
            for y in [-120,38]:skin=skin.cut(box(x-34,y,-12,68,82,54))
        for x in [-89,-77,-65,-53]:skin=skin.cut(box(x,-55,140,3.3,20,82)).cut(box(x,33,140,3.3,18,82))
        if name.endswith("RearShell"):
            skin=skin.cut(box(202,-12,72.8,15,25,25)).cut(box(161,-112,91,14,41,14)).cut(box(126,-13,143,50,35,38))
            for x in (25,37,49,61,73,85,97):skin=skin.cut(box(x,-14,148,3,27,36))
        for x in ([-64,-20] if name.endswith("Shoulder") else [42,92]):
            for sign in [-1,1]:
                tab=box(x-4,min(sign*84,sign*110),77.3,8,26,2.3).common(out)
                tab=tab.cut(box(x-1.8,min(sign*90,sign*95),77,3.6,5,3))
                cand=skin.fuse(tab).removeSplitter()
                if len(cand.Solids)==1 and cand.isValid():skin=cand
        skin=skin.cut(fl).removeSplitter()
        install(name,skin,dark,"detachable raised belly with slotted side lands")
    shift=V(*lay["yaw_pair_translation"])
    D.BR_PAIR_HY.Placement.Base # apply full source mated housing translation
    pair=sh("BR_PAIR_HY").copy();pair.translate(shift);o=put("D19D_YawMatedPair",pair,(.66,.40,.15),"both complete mated factory halves");o.ViewObject.Visibility=True
    for name in ["BR_PAIR_HY","C19_ShoulderFloor","C19_MovingOpticsCarrier","C19_FixedShoulderShell","C19_OpenRearHelmet","C19_FaceAndEars","C19_Ear_1","C19_Ear_2","C19_Nose","C19_Iris_L","C19_Iris_R","C19_Pupil_L","C19_Pupil_R","D19_ROUNDED_REAR_COWL"]:D.getObject(name).ViewObject.Visibility=False
    def paths(q):return Part.makeCompound([Part.makePolygon([V(*p) for p in line]) for line in q])
    q=next(m for m in lay["motion"] if m["yaw"]==m["pitch"]==0)
    pitch=json.loads((P.parent/"day18-body-reception-and-closed-fit/yaw-laid-factory.json").read_bytes())["rows"]
    for n,lines,color in [("D19D_ToF",lay["head"]+q["cores"]+[f["centreline"] for f in lay["fixed"]],(.97,.55,.1)),("D19D_HeadServoWires",[lay["yaw_factory"]["centreline"],next(m["centreline"] for m in pitch if m["yaw"]==0)]+[j["centreline"] for j in lay["jr"]]+[f["centreline"] for j in lay["jr"] for f in j["fans"]],(.76,.22,.2))]:
        put(n,paths(lines),color,"installation field").ViewObject.Visibility=False
    D.recompute();D.save();write("build.json",dict(objects=len(D.Objects),members=records))
whole()

