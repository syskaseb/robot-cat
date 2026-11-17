"""One source-derived hollow enclosure; no purchased part placement changes."""
import FreeCAD as A, Part, math, json, time
from pathlib import Path
from datetime import datetime, timezone
D=A.ActiveDocument; V=A.Vector; P=Path(__file__).parent
def put(n,x): (P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def box(x,y,z,a,b,c): return Part.makeBox(a,b,c,V(x,y,z))
def fuse(xs):
 q=xs[0]
 for s in xs[1:]: q=q.fuse(s)
 return q
def bb(s):
 b=s.BoundBox; return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def obj(n,s):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.19,.205,.22);o.ViewObject.LineColor=(.08,.08,.08);o.ViewObject.Transparency=0;return o
# Actual high bank/speaker/inline/monitor fields require the broad middle.
# Ends taper only AFTER their occupied source intervals. Crown/belly vary in X.
stations=[(-168,62,54,145),(-145,102,40,161),(-105,121,33,178),(-45,123,35,182),(25,121,36,181),(90,118,33,178),(145,112,34,172),(174,91,42,158),(190,48,57,132),(197,12,76,105)]
def wire(x,ry,lo,hi,inset=0):
 ry-=inset;lo+=inset;hi-=inset;c=(hi+lo)/2;rz=(hi-lo)/2;pts=[]
 for k in range(40):
  t=2*math.pi*k/40;co=math.cos(t);si=math.sin(t)
  pts.append(V(x,ry*math.copysign(abs(co)**(2/2.6),co),c+rz*math.copysign(abs(si)**(2/2.6),si)))
 curve=Part.BSplineCurve();curve.interpolate(pts,PeriodicFlag=True);return Part.Wire([curve.toShape()])
def run():
 t=time.perf_counter();D.save()
 outer=Part.makeLoft([wire(*s) for s in stations],True,False)
 # Radial-coordinate inset 2mm; NOT a claimed constant normal-wall thickness.
 # Close both ends with actual 2mm X webs, except the specified functional apertures.
 ins=[list(s) for s in stations];ins[0][0]+=2;ins[-1][0]-=2
 endinner=Part.makeLoft([wire(*s,inset=2.0) for s in ins],True,False)
 shell=outer.cut(endinner)
 # Real access apertures; fields and moving mechanisms are not erased from the assembly.
 neck=box(-190,-77,79,108,154,106)
 root=D.getObject('TAIL_ROTATING_HOLLOW_REAL_ROOT').Shape
 tr=max(math.hypot(v.Point.x-140,v.Point.z-130) for v in root.Vertexes)+1.25
 tailguard=Part.makeCylinder(tr,root.BoundBox.YLength+2.5,V(140,root.BoundBox.YMin-1.25,130),V(0,1,0))
 cuts=[neck,tailguard,
  Part.makeCylinder(23,100,V(88.5,-145,108),V(0,1,0)),
  box(104.5,-145,104.5,44,62,28),
  Part.makeCylinder(17,100,V(49,-145,119),V(0,1,0))]
 # Speaker pair round acoustic openings, preserving full nominal100x45 module.
 for x in [-76,-24]:cuts.append(Part.makeCylinder(20,55,V(x,82,122.5),V(0,1,0)))
 # Pi cooling perforations in the negative side, not the old large rectangular device hole.
 for x in [-119,-109,-99,-89,-79,-69,-59,-49]:
  for z in [66,78,90]:cuts.append(Part.makeCylinder(2.5,60,V(x,-145,z),V(0,1,0)))
 # Microphone openings above the complete source board; USB and mute remain open during lay.
 for x in [27,45,63,81,94]:cuts.append(Part.makeCylinder(2.0,55,V(x,-10,143),V(0,0,1)))
 # Capacitive touch works through a thin uninterrupted roof; actual sensitivity is FIT3.
 for q in cuts:shell=shell.cut(q)
 shell=shell.removeSplitter()
 put('hollow-body-first-checkpoint.json',{'utc':datetime.now(timezone.utc).isoformat(),'stations':stations,'wall_basis':'2mm radial-coordinate inset, normal wall measured later','outer_valid':outer.isValid(),'shell_valid':shell.isValid(),'shell_solids':len(shell.Solids),'shell_volume':shell.Volume,'tail_continuous_cylindrical_guard_R':tr,'tail_guard_scope':'entire rotating root under Y rotation; source tube continuation/bought neighbours separate','physicalPASS':False})
 # Source-exact six keyed tabs, retained interface to unchanged P02/P03.
 tabs=[]
 for x in [-70,70,145]:
  for sy in [-1,1]:
   old=D.getObject('CLOSED_BODY_'+('front' if x<30 else 'rear')+'_'+('positive' if sy>0 else 'negative')).Shape
   tab=old.common(box(x-6,66 if sy>0 else -86,43.62,12,20,2.4))
   rib=box(x-6,65 if sy>0 else -123,43.62,12,58,2.4).common(outer)
   # Keep original keyed bearing geometry; remove own current deck material only.
   deck=D.getObject('P02_front_deck' if x<30 else 'P03_rear_deck_integrated_load_yoke').Shape
   rib=rib.cut(deck).cut(Part.makeCylinder(1.7,20,V(x,sy*72,35)))
   tabs.append((x,sy,tab.fuse(rib)))
 regions=[('F_NEG',-180,-140,190,140),('F_POS',-180,0,190,140),('R_NEG',10,-140,210,140),('R_POS',10,0,210,140)]
 G=D.addObject('App::DocumentObjectGroup','HOLLOW_BODY_CURRENT_PRINTS')
 rows=[]
 for tag,x,y,dx,dy in regions:
  q=shell.common(box(x,y,20,dx,dy,190))
  own=[s for tx,sy,s in tabs if (tx<10)==tag.startswith('F') and (sy>0)==tag.endswith('POS')]
  q=fuse([q]+own).removeSplitter()
  o=obj('HB_'+tag,q);G.addObject(o)
  rows.append({'name':o.Name,'valid':q.isValid(),'solids':len(q.Solids),'volume':q.Volume,'bounds':bb(q)})
 for n in ['NIGHT_BODY_PROPORTION_ENVELOPE_NOT_PRINT','Ola_body_ENVELOPE']:
  o=D.getObject(n)
  if o:o.ViewObject.Visibility=False
 D.recompute();D.save()
 put('hollow-body-first-checkpoint.json',{'utc':datetime.now(timezone.utc).isoformat(),'stations':stations,'wall_basis':'2mm radial-coordinate inset; not constant normal thickness','tail_continuous_cylindrical_guard_R':tr,'parts':rows,'provisional_solid_body_retired_from_selected_material':True,'bought_placements_changed':[],'actual_operator_mounts':'next common interfaces; apertures not evidence of retention','neck_and_tail_guard_closure':'functional apertures; final retained collar/access still unqualified','wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t})
 print(json.dumps({'parts':rows,'seconds':time.perf_counter()-t}))
run()
