import FreeCAD as A,FreeCADGui as G,Part,json,pathlib,math
from PySide import QtCore
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def obj(n,s,c):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=c;o.ViewObject.DisplayMode='Shaded';return o
def ell(c,r):
 s=Part.makeSphere(1);m=A.Matrix();m.A11,m.A22,m.A33=r;s=s.transformGeometry(m);s.translate(V(*c));return s
changes=[]
def move(n,T):
 o=D.getObject(n);v=o.Shape.Volume;o.Placement=T.multiply(o.Placement);changes.append(dict(name=n,volume_before=v,volume_after=o.Shape.Volume,matrix=T.toMatrix().A))
for o in D.Objects:
 if not o.Name.startswith('WAGO415_data') or not o.ViewObject.Visibility:continue
 b=o.Shape.BoundBox
 if b.XMin<70:continue
 cy=(b.YMin+b.YMax)/2;cx=(b.XMin+b.XMax)/2;cz=(b.ZMin+b.ZMax)/2
 R=A.Rotation(V(1,0,0),90);new=V(cx-20,(-40.5 if cy<-35 else -29.5) if cy<0 else (29.5 if cy<46 else 40.5),159.5)
 move(o.Name,A.Placement(new-R.multVec(V(cx,cy,cz)),R))
for o in D.Objects:
 if o.Name.startswith('D18B_INLINE_RL') and o.ViewObject.Visibility:
  b=o.Shape.BoundBox;move(o.Name,A.Placement(V(0,0,126-b.ZMin),A.Rotation()))
# One rounded skull, two SMALL lower pads. Existing optics and 2-axis hardware are not moved.
lobes=[((-134,0,150),(64,77,64)),((-180,-14,111),(20,25,24)),((-180,14,111),(20,25,24))]
ho=ell(*lobes[0]);hi=ell(lobes[0][0],tuple(a-1.6 for a in lobes[0][1]))
for c,r in lobes[1:]:ho=ho.fuse(ell(c,r));hi=hi.fuse(ell(c,tuple(a-1.6 for a in r)))
# The retained visible ear outlines become integral above the skull; obsolete buried lower feet are explicitly replaced.
for n in ['Ola_ear__1','Ola_ear_1']:ho=ho.fuse(D.getObject(n).Shape);D.getObject(n).ViewObject.Visibility=False
hs=ho.cut(hi)
for n in ['D18C_CAM_MODEL_CLOCK_BOUND_FOV','D18C_TOF_MODEL_CLOCK_BOUND_FOV']:hs=hs.cut(D.getObject(n).Shape)
hs=hs.cut(Part.makeBox(88,84,62,V(-162,-42,70)))
for side in [-1,1]:hs=hs.fuse(Part.makeBox(6,3,64,V(-159.6,22 if side>0 else -25,152.5)).common(ho))
for n,x0,x1 in [('FRONT',-205,-140),('BACK',-140,-45)]:obj('F3_HEAD_'+n,hs.common(Part.makeBox(x1-x0,220,240,V(x0,-110,0))).removeSplitter(),(.16,.17,.19))
# Paint regions lie ON the real rounded forehead; no loose floating eye parts or raised collars.
skullface=ell(*lobes[0]).Faces[0]
for side in [-1,1]:
 def ec(ry,rz):
  s=Part.makeCylinder(1,110,V(0,0,0),V(1,0,0));m=A.Matrix();m.A22=ry;m.A33=rz;s=s.transformGeometry(m);s.translate(V(-230,side*43,160));return s
 out=skullface.common(ec(16,19));inside=skullface.common(ec(13.4,16.4))
 band=out.cut(inside);band.translate(V(-.06,0,0));inside.translate(V(-.07,0,0))
 obj('F3_PAINT_GOLD_'+str(side).replace('-','m'),band,(.64,.44,.14));obj('F3_PAINT_DARK_'+str(side).replace('-','m'),inside,(.008,.01,.014))
# Parts-backed shoulder / waist / rump sections. The negative upper shoulder has a fuller curve for actual R30 DATA storage.
stations=[(-149,26,68,106,.5,.5),(-135,44,52.52,154,.5,.5),(-108,74,52.52,176,.7,.5),(-92,92,52.52,185,.95,.55),(-40,92,52.52,185,.95,.55),(20,90,52.52,179,.85,.65),(85,91,52.52,177,.75,.75),(128,88,52.52,179,.75,.75),(156,67,65,165,.7,.7),(180,23,97,143,.5,.5)]
def profile(a,w=0):
 x,ry,floor,top,neg,pos=a;ry-=w;top-=w;f=floor-w*.7;yb=ry*.51;mid=f+(top-f)*.47
 def curve(q):
  c=Part.BezierCurve();c.setPoles([V(x,y,z) for y,z in q]);return c.toShape()
 rows=[[(-yb,f),(-ry*.89,f),(-ry,f+(mid-f)*.31),(-ry,mid)],[(-ry,mid),(-ry,top-(top-mid)*.35),(-ry*neg,top),(0,top)],[(0,top),(ry*pos,top),(ry,top-(top-mid)*.35),(ry,mid)],[(ry,mid),(ry,f+(mid-f)*.31),(ry*.89,f),(yb,f)]]
 return Part.Wire([curve(q) for q in rows]+[Part.makeLine(V(x,yb,f),V(x,-yb,f))])
outer=Part.makeLoft([profile(a) for a in stations],True,True);inner=Part.makeLoft([profile(a,1.6) for a in stations],True,True);wall=outer.cut(inner)
wall=wall.cut(Part.makeCylinder(27,180,V(115.5,-70,92),V(0,1,0))).cut(Part.makeCylinder(8,60,V(-8,-100,84),V(0,1,0))).cut(Part.makeBox(20,41,25,V(-155,-20.5,72)))
for x in [-75,-57,-39,-21,-3]:wall=wall.cut(Part.makeBox(5,80,25,V(x,25,86)))
for x in [-82,-53,-24]:wall=wall.cut(Part.makeBox(12,80,3,V(x,-95,123)))
wall=wall.cut(Part.makeBox(95,104,150,V(-161,-52,112)))
for name,x0,x1 in [('FORE',-150,20),('REAR',20,181)]:
 for side,y0,y1 in [('NEG',-120,0),('POS',0,120)]:obj('F3_BODY_'+name+'_'+side,wall.common(Part.makeBox(x1-x0,y1-y0,260,V(x0,y0,0))).removeSplitter(),(.13,.14,.16))
for o in D.Objects:
 if o.Name.startswith(('F2_BODY_','F2_HEAD_','F2_GOLD_','F2_DARK_','D18C_DATA500_CONNECTED_STATIC_BAY')):o.ViewObject.Visibility=False
data=json.loads((P/'DATA500-horizontal-stock-plan.json').read_text());a=V(*data['source_pi']);b=V(*data['source_bus']);R=30;z=data['landing_z'];rt=2**-.5
def arc(p,m,q):return Part.Arc(V(*p),V(*m),V(*q)).toShape()
ed=[arc(tuple(a),(a.x+R*rt,a.y,a.z+R-R*rt),(a.x+R,a.y,a.z+R)),Part.makeLine(V(a.x+R,a.y,a.z+R),V(a.x+R,a.y,z-R)),arc((a.x+R,a.y,z-R),(a.x+R*rt,a.y,z-R+R*rt),(a.x,a.y,z))]
for seg in data['storage_segments']:
 h=seg['heading_start']+seg['side']*seg['turn']/2;cx,cy,_=seg['center'];r=seg['radius'];m=(cx+seg['side']*r*math.sin(h),cy-seg['side']*r*math.cos(h),z);ed.append(arc(seg['start'],m,seg['end']))
be=[arc(tuple(b),(b.x,b.y-R*rt,b.z+R-R*rt),(b.x,b.y-R,b.z+R)),Part.makeLine(V(b.x,b.y-R,b.z+R),V(b.x,b.y-R,z-R)),arc((b.x,b.y-R,z-R),(b.x-R+R*rt,b.y-R,z-R+R*rt),(b.x-R,b.y-R,z))]
for e in reversed(be):q=e.copy();q.reverse();ed.append(q)
wire=Part.Wire(ed);o=obj('F3_DATA500_HORIZONTAL_COMPLETE_UNIT',wire,(.8,.32,.12));o.ViewObject.LineWidth=3
wr('whole-working-form-effectivity.json',dict(stations=stations,head='ONE rounded skull / two lower small pads / surface paint eyes; existing camera/ToF/full source parts retained',retired_OWN=['F2 four body walls','F2 two dominant cheek lobes','F2 floating gold/dark inserts','buried old ear feet replaced by integral skull-ear wall'],whole_closed_accepted=False,full_DATA500_wire_length=wire.Length+52,whole_module_rigid_moves=changes,still_open=['actual skin joins','neck/stock hazard gate','S0 operator recess closure','full group source-to-source budgets','other common receivers'],physical_PASS=False))
D.recompute();D.save();print('WHOLE_WORKING_FORM_SAVED',wire.Length+52)
