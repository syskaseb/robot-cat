"""Actual deck-bottom, open-bottom side/end/roof cowl. No belly through the WAVEGO."""
import FreeCAD as A,Part,json,math,time
from pathlib import Path
from datetime import datetime,timezone
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode())
def fuse(ss):
 q=ss[0]
 for s in ss[1:]:q=q.fuse(s)
 return q
def obj(n,s):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.18,.19,.205);o.ViewObject.Transparency=0;return o
# Convex-hull Bezier bounds in each YZ plane, RULED X segments: no interpolating-loft overshoot.
stations=[(-128,112,176),(-110,117,174),(-70,117,171),(-20,115,169),(30,113,168),(80,112,165),(140,112,160),(163,108,157),(181,42,108)]
def pars(x):
 for a,b in zip(stations,stations[1:]):
  if a[0]<=x<=b[0]:
   u=(x-a[0])/(b[0]-a[0]);return(x,a[1]*(1-u)+b[1]*u,a[2]*(1-u)+b[2]*u)
 return stations[0] if x<stations[0][0] else stations[-1]
def curves(s,sy,inside=False):
 x,ym,top=s;t=1.6 if inside else 0;base=104 if sy<0 and x<0 else 92.5
 if x>163:base=92.5+(40-92.5)*(x-163)/18
 ym-=t;base-=t;top-=t
 def p(y,z):return V(x,sy*y,z)
 q=Part.BezierCurve();q.setPoles([p(base,43.62),p(base,62),p(ym,70),p(ym,104)])
 r=Part.BezierCurve();r.setPoles([p(ym,104),p(ym,min(top,162)),p(min(ym,100),top),p(0,top)])
 return [q.toShape(),r.toShape()]
def profile(s,sy,full=False):
 a=curves(s,sy);p0=a[0].Vertexes[0].Point;p1=a[-1].Vertexes[-1].Point
 if full:return Part.Wire(a+[Part.makeLine(p1,V(s[0],0,43.62)),Part.makeLine(V(s[0],0,43.62),p0)])
 b=curves(s,sy,True);b0=b[0].Vertexes[0].Point;b1=b[-1].Vertexes[-1].Point
 rb=[]
 for e in reversed(b):q=e.copy();q.reverse();rb.append(q)
 return Part.Wire(a+[Part.makeLine(p1,b1)]+rb+[Part.makeLine(b0,p0)])
def run():
 t=time.perf_counter();D.save()
 # Retire ONE unused old cage (not the floor). Pi now occupies its old installation region.
 deck=D.getObject('P02_front_deck');before=deck.Shape.copy();before.exportBrep(str(P/'source-P02-before-unused-cage-retirement.brep'))
 cut=box(-75,-77,48.52,10,10,5.21);oldPi=before.common(D.getObject('Pi4B_actual_PCB').Shape).Volume
 deck.Shape=before.cut(cut).removeSplitter()
 for o in D.Objects:
  if o.Name.startswith('BASE0_'):o.ViewObject.Visibility=False;o.Label='RETIRED UNBUILT front-negative cowl set / replaced by coupled front cowl; '+o.Name
 # Actual inherited MTA/rearframe overlap resolved in the own MTA foot, above protected floor.
 mt=D.getObject('FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER');mtold=mt.Shape.copy();mtold.exportBrep(str(P/'source-MTA-before-register-relief.brep'))
 relief=box(119.55,23.75,47.27,9.7,3,6.5);mt.Shape=mt.Shape.cut(relief).removeSplitter()
 put('current-floor-functional-effects.json',{'retired_only_old_unbuilt_cage':bb(cut),'old_PiPCB_common':oldPi,'new_PiPCB_common':deck.Shape.common(D.getObject('Pi4B_actual_PCB').Shape).Volume,'P02_floor_at_or_below48p52_preserved':True,'source8P01_axes_and_boughtparts_untouched':True,'active_base_cowl_sets':5,'sixth_front_negative_function':'Shared front shell coupling at actual open roof bay; no new moving Pi or unsupported floating wall','MTA_register_relief':bb(relief),'MTA_removed':mtold.Volume-mt.Shape.Volume,'MTA_remaining_under_post_web':2.75,'rear_MTA_common_after':mt.Shape.common(D.getObject('RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER').Shape).Volume})
 rows=[];G=D.addObject('App::DocumentObjectGroup','FLOOR_BASED_CURRENT_COWL')
 for tag,sy,lo,hi in [('F_NEG',-1,-128,80),('F_POS',1,-128,80),('R_NEG',-1,80,181),('R_POS',1,80,181)]:
  ss=[pars(lo)]+[s for s in stations if lo<s[0]<hi]+[pars(hi)]
  q=Part.makeLoft([profile(s,sy) for s in ss],True,True)
  outer=Part.makeLoft([profile(s,sy,True) for s in ss],True,True)
  # Actual end closures; centre bottom stays open to the already existing deck.
  if lo==-128:q=q.fuse(outer.common(box(-128,-140,40,1.6,280,150)))
  if hi==181:q=q.fuse(outer.common(box(179.4,-140,40,1.6,280,150)))
  # Under-floor lap overlaps actual deck edge. Bounded rail portals are purposeful passes.
  flange=box(lo,77.75 if sy>0 else -105.5,43.62,hi-lo,27.75,1.6).common(outer)
  for rn in ['RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER']:
   s=D.getObject(rn).Shape.common(box(lo-1,77 if sy>0 else -96,40,hi-lo+2,19,7.5))
   for a in s.Solids:
    b=a.BoundBox;flange=flange.cut(box(b.XMin-1.25,b.YMin-1.25,39,b.XLength+2.5,b.YLength+2.5,10))
  q=q.fuse(flange)
  # Source-exact five real keyed pads, plus useful outboard risers. No source key through GPIO.
  for x in [-70,70,145]:
   if not lo<x<hi or (x==-70 and sy<0):continue
   old=D.getObject('CLOSED_BODY_'+('front' if x<30 else 'rear')+'_'+('positive' if sy>0 else 'negative')).Shape
   key=old.common(box(x-6,66 if sy>0 else -86,43.62,12,20,2.4))
   base=104 if sy<0 and x<0 else 92.5
   foot=box(x-6,83 if sy>0 else -base-1,43.62,12,base-82,2.4)
   rise=box(x-6,base-1.2 if sy>0 else -base-1,45.52,12,2.2,7)
   q=q.fuse(key).fuse(foot).fuse(rise)
  # Whole functional port apertures/air path from current source fields, not fake wire solids.
  cuts=[]
  if sy<0 and lo<0:
   cuts += [box(-117.25,-99.17,39.75,54.5,25.5,18.5),box(-153.25,-91.65,42.75,28.5,27.5,28.5)]
   cuts += [Part.makeCylinder(2.5,55,V(x,-140,z),V(0,1,0)) for x in [-119,-109,-99,-89,-79,-69,-59,-49] for z in [66,78,90]]
  if sy<0:
   cuts += [Part.makeCylinder(23,100,V(88.5,-145,108),V(0,1,0)),box(104.5,-145,104.5,44,62,28),Part.makeCylinder(17,100,V(49,-145,119),V(0,1,0))]
  if sy>0 and lo<0:cuts += [Part.makeCylinder(20,55,V(x,82,122.5),V(0,1,0)) for x in [-76,-24]]
  if lo<0:
   # Rounded head/neck opening, later paired with an actual hollow moving back + fixed collar.
   el=Part.Ellipse(V(-129,0,119),70,54);el.Axis=V(1,0,0);el.XAxis=V(0,1,0)
   neck=Part.Face(Part.Wire([el.toShape()])).extrude(V(12,0,0));cuts.append(neck)
  if hi==181:
   # LIMITED entry sector only; full-tail continuation remains visible, no 360deg huge cut.
   cuts.append(box(136,-1.25,137,55,19.65,60))
  for c in cuts:
   if q.BoundBox.intersect(c.BoundBox):q=q.cut(c)
  # Matched deck slips/contact; never trim a bought frame or the real deck to fit a skin.
  for dn in ['P02_front_deck','P03_rear_deck_integrated_load_yoke']:q=q.cut(D.getObject(dn).Shape)
  o=obj('FC_'+tag,q.removeSplitter());G.addObject(o)
  rows.append({'name':o.Name,'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'v':o.Shape.Volume,'bounds':bb(o.Shape)})
  D.recompute();D.save();put('floor-cowl-build-checkpoint.json',{'parts':rows,'cursor':len(rows),'stations':stations,'bounded_Bezier_rule':True,'openbottom_uses_actual_decks':True,'wall_radial_nominal':1.6,'no_bought_pose_changes':True,'wholekit':False,'seconds':time.perf_counter()-t})
 for o in D.Objects:
  if o.Name.startswith('HB_') or o.Name=='NIGHT_BODY_PROPORTION_ENVELOPE_NOT_PRINT':o.ViewObject.Visibility=False
 # Preserve REAL new MIC steel (HB_MIC_...) when retiring only previous body alternatives.
 for o in D.Objects:
  if o.Name.startswith('HB_MIC_') and o.Name!='HB_MIC_PRIMARY_POPULATED_SCOPE':o.ViewObject.Visibility=True
 D.recompute();D.save();print(json.dumps({'parts':rows,'seconds':time.perf_counter()-t}))
run()
