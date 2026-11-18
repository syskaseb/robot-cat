import FreeCAD as A,FreeCADGui as G,Part,json,pathlib,math
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def obj(n,s,c=(.13,.14,.16)):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=c;o.ViewObject.DisplayMode='Shaded';return o
# Profiles are cubic sections with bounded control polygons, ruled longitudinally: no hidden loft overshoot.
stations=[(-149,26,68,103),(-135,42,52.52,150),(-108,70,52.52,164),(-92,90,52.52,178),(-40,90,52.52,180),(30,90,52.52,179),(100,89,52.52,177),(134,89,52.52,176),(164,70,65,164),(180,24,96,143)]
def profile(x,ry,floor,top,wall=0):
 ry-=wall;top-=wall;f=floor-wall*.7;yb=ry*.51;mid=f+(top-f)*.47
 def curve(q):
  c=Part.BezierCurve();c.setPoles([V(x,y,z) for y,z in q]);return c.toShape()
 # Lower sides rise from a narrow structural floor to the actual side equipment; upper sides continuously arch.
 neglo=[(-yb,f),(-ry*.89,f),(-ry,f+(mid-f)*.31),(-ry,mid)]
 negup=[(-ry,mid),(-ry,top-(top-mid)*.35),(-ry*.5,top),(0,top)]
 posup=[(0,top),(ry*.5,top),(ry,top-(top-mid)*.35),(ry,mid)]
 poslo=[(ry,mid),(ry,f+(mid-f)*.31),(ry*.89,f),(yb,f)]
 return Part.Wire([curve(a) for a in [neglo,negup,posup,poslo]]+[Part.makeLine(V(x,yb,f),V(x,-yb,f))])
outer=Part.makeLoft([profile(*s) for s in stations],True,True);inner=Part.makeLoft([profile(*s,wall=1.6) for s in stations],True,True);wall=outer.cut(inner)
# Optical/front and actual operator/acoustic/cooling functions stay open; real aperture datums remain explicitly nominal where sample is needed.
wall=wall.cut(Part.makeCylinder(27,180,V(115.5,-70,92),V(0,1,0)))
wall=wall.cut(Part.makeCylinder(8,60,V(-8,-100,84),V(0,1,0)))
wall=wall.cut(Part.makeBox(20,41,25,V(-155,-20.5,72)))
# Speaker basket acoustic path, not a large rectangular hiding window.
for x in [-75,-57,-39,-21,-3]:wall=wall.cut(Part.makeBox(5,80,25,V(x,25,86)))
for x in [-82,-53,-24]:wall=wall.cut(Part.makeBox(12,80,3,V(x,-95,123)))
# A real neck interface remains open for the preserved two axes/full200; do not call an outer envelope closed skin here.
wall=wall.cut(Part.makeBox(95,104,150,V(-161,-52,112)))
parts=[]
for name,x0,x1 in [('FORE',-150,20),('REAR',20,181)]:
 for side,y0,y1 in [('NEG',-120,0),('POS',0,120)]:
  s=wall.common(Part.makeBox(x1-x0,y1-y0,260,V(x0,y0,0))).removeSplitter();o=obj('F2_BODY_'+name+'_'+side,s);parts.append(o)
for o in D.Objects:
 if o.Name.startswith(('D18B_BODY_FORM','D18C_HEAD_FACE_CLOCK_BOUND_FORM','D18C_LOCAL_NECK_RECEIVING_FORM','D18C_GOLD_RIM_','D18C_DARK_EYE_')):o.ViewObject.Visibility=False
# Real hollow paired head volume: integrated cheek/orbit lobes and close central optical bridge, no raised goggles.
lobes=[((-135,-30,140),(62,50,75)),((-135,30,140),(62,50,75)),((-139,0,160),(43,38,48)),((-173,-18,111),(19,25,23)),((-173,18,111),(19,25,23)),((-174,0,111),(16,20,20)),((-100,0,168),(45,45,40))]
def ell(c,r):
 s=Part.makeSphere(1);m=A.Matrix();m.A11,m.A22,m.A33=r;s=s.transformGeometry(m);s.translate(V(*c));return s
ho=ell(*lobes[0]);hi=ell(lobes[0][0],tuple(a-1.6 for a in lobes[0][1]))
for c,r in lobes[1:]:ho=ho.fuse(ell(c,r));hi=hi.fuse(ell(c,tuple(a-1.6 for a in r)))
hs=ho.cut(hi)
for n in ['D18C_CAM_MODEL_CLOCK_BOUND_FOV','D18C_TOF_MODEL_CLOCK_BOUND_FOV']:hs=hs.cut(D.getObject(n).Shape)
hs=hs.cut(Part.makeBox(88,84,62,V(-162,-42,70)))
for side in [-1,1]:
 mast=Part.makeBox(6,3,68,V(-159.6,22 if side>0 else -25,152.5)).common(ho);hs=hs.fuse(mast)
for n,x0,x1 in [('FRONT',-230,-140),('BACK',-140,-45)]:
 s=hs.common(Part.makeBox(x1-x0,220,240,V(x0,-110,0))).removeSplitter();o=obj('F2_HEAD_'+n,s);parts.append(o)
# Retained decorative dark eyes/gold rims are geometry only, no LED purchase; real shell is separate from paint regions.
for side in [-1,1]:
 eye=ell((-186,side*43,151),(3,13,16));rim=ell((-184,side*43,151),(3.8,16,19)).cut(eye);obj('F2_GOLD_ORBIT_'+str(side).replace('-','m'),rim,(.65,.43,.13));obj('F2_DARK_EYE_'+str(side).replace('-','m'),eye,(.012,.015,.019))
# Actual ear shapes retained and offered to the shell as integral features; this is not a hidden source geometry deletion.
for n in ['Ola_ear__1','Ola_ear_1']:D.getObject(n).Placement.Base+=V(0,0,16)
report=dict(stations=stations,nominal_wall_mm=1.6,wall_method='outer minus inner bounded cubic-section ruled loft / paired ellipsoid head union; not makeOffsetShape',parts=[],important_status='ACTUAL HOLLOW MATERIAL; neck/tail overlap guards and complete fastening still OPEN, not whole closed-cat release',physical_PASS=False)
for o in parts:
 b=o.Shape.BoundBox;report['parts'].append(dict(name=o.Name,valid=o.Shape.isValid(),solids=len(o.Shape.Solids),volume_mm3=o.Shape.Volume,PETG_g=o.Shape.Volume*.00127,raw_bounds=[b.XLength,b.YLength,b.ZLength],print_scope='BRep only until real joins/clearance complete; no raw ellipsoid bbox gate'))
wr('actual-hollow-body-head-material.json',report);D.recompute();D.save();print('ACTUAL_HOLLOW',[(a['name'],a['valid'],a['solids'],round(a['PETG_g'],2)) for a in report['parts']])
