import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector;t=time.perf_counter()
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def add(n,s,color=(.16,.18,.21)):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=color;o.ViewObject.Visibility=True;return o
# Smooth continuously convex superelliptic profiles; both axial ends have real 2mm material.
# n=3.2 keeps actualsidebankcorners inside without flattening full sides into long parallel walls.
stations=[(-165,75,98,53),(-146,112,94,61),(-90,117,92,62),(0,119,92,62),(90,118,93,62),(165,117,94,63),(201,112,94,63),(229,53,111,39)]
def wire(q,inset=0):
 x,w,c,h=q;w-=inset;h-=inset;k=.8
 # Four identically parametrized convex Bezierquadrants. Fixed knotstructure prevents interiorloft crossing outerloft.
 quadrants=[[(0,h),(k*w,h),(w,k*h),(w,0)],[(w,0),(w,-k*h),(k*w,-h),(0,-h)],[(0,-h),(-k*w,-h),(-w,-k*h),(-w,0)],[(-w,0),(-w,k*h),(-k*w,h),(0,h)]]
 edges=[]
 for poles in quadrants:
  q=Part.BezierCurve();q.setPoles([V(x,y,c+z) for y,z in poles]);edges.append(q.toShape())
 return Part.Wire(edges)
outer=Part.makeLoft([wire(q) for q in stations],True,False)
ins=[(x+2 if i==0 else x-2 if i==len(stations)-1 else x,w,c,h) for i,(x,w,c,h) in enumerate(stations)]
inner=Part.makeLoft([wire(q,2) for q in ins],True,False);skin=outer.cut(inner)
# Fore closure is a rounded shoulder, not openend/flatplug. Actualneck opening around retained movinghead.
neck=Part.makeCylinder(52,58,V(-175,0,125),V(1,0,0));skin=skin.cut(neck)
# TailtransverseY root stays real and visible through an arcuate, separable passage, no bolt-oncube.
# Analytic sector retains only chosenpitch +/-15 plus radialguard; actualnewskin motion still receives localgate.
cy=V(185,-4,112);a0=math.radians(33);a1=math.radians(77);R=94
p0=cy+V(R*math.cos(a0),0,R*math.sin(a0));p1=cy+V(R*math.cos(a1),0,R*math.sin(a1));pm=cy+V(R*math.cos((a0+a1)/2),0,R*math.sin((a0+a1)/2))
sector=Part.Face(Part.Wire([Part.makeLine(cy,p0),Part.Arc(p0,pm,p1).toShape(),Part.makeLine(p1,cy)])).extrude(V(0,32,0))
skin=skin.cut(sector)
# Actual function apertures; no actual boughtpart hidden to disguiseprotrusions.
# Speaker now faces +Y, multiple acoustic slots through real wall; basket support separate.
for z in [99,112,125]:skin=skin.cut(box(-104,80,z,96,70,4))
# Cooling intake/exhaust passages open to actualPi topair region and opposite side, not opaque coveroverheat.
for x in [-126,-112,-98,-84,-70,-56]:skin=skin.cut(box(x,-55,120,4,35,55))
# S0 sidekey operation, S1 rearoperator andmonitor readability; operatorhand fitting remains physicalprototype check.
skin=skin.cut(box(23,-150,96,35,95,23)).cut(box(137,-150,97,25,130,38))
skin=skin.cut(box(135,20,106,46,130,17))
# Six retainedassemblyroots on ownloadgrids, hollow shell tabs are actualbearing not empty envelope.
tabs=[]
for x in [-120,0,150]:
 for y in [-92,92]:
  # tabs attach via radialside at z56; actual finalintersection/foreigngate recordedseparately.
  tab=box(x-5,y-8,46.52,10,16,5).cut(Part.makeCylinder(1.7,6,V(x,y,46)))
  # Sideweb grows toward smoothskin, connected overlaps to shell body lower side at actualz.
  web=box(x-5, y-15 if y<0 else y, 48.52,10,15,14)
  tabs.append((x,y,tab.fuse(web)))
# Splitfour real prospectiveparts; nominal no fusedseparateprint. Bodyroot tabs only if connected to corresponding shell.
parts=[]
(P/'skin-before-parting-debug.json').write_bytes((json.dumps({'skinvolume':skin.Volume,'bounds':[skin.BoundBox.XMin,skin.BoundBox.XMax], 'outer_volume':outer.Volume,'inner_volume':inner.Volume},indent=2)+'\n').encode())
for xa,xb,side,y0,y1 in [(-166,30,'F_NEG',-160,0),(-166,30,'F_POS',0,160),(30,231,'R_NEG',-160,0),(30,231,'R_POS',0,160)]:
 s=skin.common(box(xa,y0,0,xb-xa,y1-y0,220))
 for x,y,tab in tabs:
  if xa<x<xb and y0<y<y1:
   candidate=s.fuse(tab)
   # Do not call detached tabs integral; retainonly if actual positive useful join.
   if len(candidate.Solids)==1:s=candidate
 o=add('LC_CURVED_BODY_'+side,s);parts.append({'name':o.Name,'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume})
for o in D.Objects:
 if o.Name.startswith('LOW_THIN_BODY_'):o.ViewObject.Visibility=False
r={'technical_repair':'fixed four-Bezier matched parameter profiles; prior rearcoverage loss retained as raw technicalfailure not design/mass credit','profiles':stations,'profile_kind':'smooth loft of four convex cubic Bezierquarters k0.8; no long straight sidepanels','wall':'inner w/h reduced2mm, nominal radial not manufacturedconstantwall','real_closed_axialends_mm':2,'head_neck_aperture_R':52,'tailopening':'actual transverseYpitch sector33..77 radial94 y-4..28; no fixedcube','apertures':['speaker slots atpositiveY','Pi intake/exhaustaboveactualPi','S0 key sidewindow','S1 switch rear side','monitor readoutpositiveY'],'parts':parts,'remaining':['actualhead/bodyrelativecontinuousmotion and overlapguard','tailsweepcover/nearby skinverification','complete sixshell tab contact/steel/lateclosure set ifnotconnected','skin seamkeys and allsourceprotrusions actual'], 'elapsed_seconds':time.perf_counter()-t}
(P/'curved-whole-closure-realization.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());D.recompute();D.save();v=G.activeDocument().activeView();v.viewAxonometric();v.fitAll();v.redraw();print(json.dumps({'parts':parts,'seconds':time.perf_counter()-t,'saved':True}))
