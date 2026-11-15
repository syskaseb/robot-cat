import FreeCAD as A,FreeCADGui as G,Part,math,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;S=A.getDocument('DAY15_DIRECT_CARRIER');P=Path(S.FileName).parent.parent/'day15-carrier-rear-contour-fit';P.mkdir(exist_ok=True)
cyl=next(f.Surface for f in S.getObject('S0_body').Shape.Faces if isinstance(f.Surface,Part.Cylinder));cx,cy=cyl.Center.x,cyl.Center.y;rs=cyl.Radius
# Rearoutercorner remains X108/Y-21. Clearance gives a lowerR; fullcellfit +2mmweb gives upperR.
dx=cx-108;dy=-21-cy;clear=1.25;b=2*(dx+dy-rs-clear);c=dx*dx+dy*dy-(rs+clear)**2;Rmin=(-b+math.sqrt(b*b-4*c))/2;Rmax=(3*math.sqrt(2)-2)/(math.sqrt(2)-1);R=5.0
assert Rmin<R<Rmax
gap_analytic=math.hypot(dx+R,dy+R)-R-rs;minimum_web=R-math.sqrt(2)*(R-3)
premise=dict(utc=datetime.now(timezone.utc).isoformat(),status='ONE_FUNCTIONAL_CONTOUR_FROM_ACTUAL_SOURCE_INTERVAL_BEFORE_MATERIAL',source_commit='89e3c97380b0a1cd314c50e40ff4a1fbee5613f6',S0_cylinder=dict(center=[cx,cy],radius=rs,axis=list(cyl.Axis)),battery_box=[-2,-17.5,65,104.5,17.5,86.5],cell_fit_allowance0p5_notpaddingcredit=True,chosen_inner_rear_X=105,chosen_inner_corner_Y=18,minimum_useful_wall_project2=True,source_outer_rear_X108_Y21_preserved=True,Rinterval=[Rmin,Rmax],chosen_R=R,method='SolveonequadraticfromactualS0cylinder+1.25; intersectRwallbound. ChooseonewholemmR5 insideinterval, noradiusgrid.',analytic_fullcircle_gap=gap_analytic,minimum_corner_wall=minimum_web,straight_rear_wall=3,remaining_floor=2,old_floor_and_workingstop_function_explicit_replacement=True,physical_cellmeasure_padding_strength='FIT, notactualpartproof',no_new_root_steel_strap_or_bought_pose=True)
(P/'rear-contour-premise.json').write_bytes((json.dumps(premise,indent=2)+'\n').encode())
D=A.newDocument('DAY15_CARRIER_CONTOUR');groups={}
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape.copy();q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
old=D.getObject('P19_shared_lower_carrier').Shape.copy()
# Keepmask onlyreplaces workingrearoutline; everyfunctionX<=103, inclfourfeet/crossarm/newroot, remains.
keep=box(-120,-60,40,223,120,80).fuse(box(103,-16,40,5,32,80))
for y in [-16,16]:keep=keep.fuse(Part.makeCylinder(5,80,V(103,y,40)))
# Halfmillimetre rear/lateralfit reservation cutONLYabovefloor/cell datum65, neverborrowingpadding.
fit=box(104.5,-18,65,.5,36,22)
new=old.common(keep).cut(fit);assert new.isValid()
D.getObject('P19_shared_lower_carrier').Shape=new;D.recompute();D.Label='DAY15 CARRIER REARCONTOUR / BEFOREWHOLEGATE';D.saveAs(str(P/'carrier-contour.FCStd'))
r=dict(status='SAVED_ONE_FUNCTIONAL_REAR_CONTOUR_BEFORE_GATE',valid=new.isValid(),solids=len(new.Solids),old_volume=old.Volume,new_volume=new.Volume,planned_rear_replacement_loss=old.cut(new).Volume,protected=[],intended_rear=[])
protected=[('fourfoot'+str(x)+'_'+str(y),box(x,y,48.52,5,4,14.48)) for x in [5,95] for y in [-45,41]]
protected += [('rearcrossarm',box(95,-45,62,5,90,3)),('MTAfloor',box(-98,-48.5,64,177,10.1,3))]
for n in ['DIRECT_P19_loadbeam','DIRECT_P19_upriser','DIRECT_P19_flange']:protected.append((n,D.getObject(n).Shape))
for n,s in protected:
 actual=old.common(s);q=actual.cut(new);r['protected'].append(dict(member=n,source_actual_volume=actual.Volume,missing=q.Volume,valid=q.isValid()));assert q.isValid() and q.Volume<1e-5,n
for n,s in [('newrear_floor',box(103,-21,60.8,5,42,4.2)),('newworking_endstop',box(104.5,-21,65,3.5,42,3))]:
 intended=old.common(s).common(keep).cut(fit);q=intended.cut(new);r['intended_rear'].append(dict(member=n,intended_volume=intended.Volume,missing=q.Volume,valid=q.isValid(),bounds=str(intended.BoundBox)));assert q.isValid() and q.Volume<1e-5
s0=D.getObject('S0_body').Shape;c=new.common(s0);r['actual_S0_gate']=dict(gap=new.distToShape(s0)[0],common=c.Volume,valid=c.isValid(),required=1.25)
r['status']='REAR_CONTOUR_ACTUAL_S0_CLEAR_SCOPED' if c.isValid() and c.Volume<1e-5 and r['actual_S0_gate']['gap']>=1.25 else 'FIRST_REAL_CONTOUR_HOLD_STOP'
(P/'rear-contour-material-and-first-gate.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(dict(status=r['status'],actual=r['actual_S0_gate'],protected=len(r['protected']),loss=r['planned_rear_replacement_loss'],premise=premise)))
