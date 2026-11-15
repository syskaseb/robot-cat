import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;S=A.getDocument('DAY15_MODULE_RETENTION');P=Path(S.FileName).parent.parent/'day15-pi-battery-carrier';P.mkdir(exist_ok=True);D=A.newDocument('DAY15_PI_BATTERY_CARRIER');groups={}
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape;q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for prop in ['AssemblyNote','Status','OriginalSource']:
  if hasattr(o,prop):q.addProperty('App::PropertyString',prop);setattr(q,prop,str(getattr(o,prop)))
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
grp=D.addObject('App::DocumentObjectGroup','PI_FULL_STANDARD_THROUGHSETS_NEEDED_UNCONFIRMED');sets=[]
def hexsolid(af,z,h):
 rr=af/math.sqrt(3);p=[V(rr*math.cos(math.pi/6+i*math.pi/3),rr*math.sin(math.pi/6+i*math.pi/3),z) for i in range(7)];return Part.Face(Part.Wire(Part.makePolygon(p).Edges)).extrude(V(0,0,h))
for i,(x,y) in enumerate([(x,y) for y in [-34.5,14.5] for x in [-74.5,-16.5]]):
 shaft=Part.makeCylinder(1.25,12,V(x,y,88.62));head=Part.makeCylinder(2.25,2.5,V(x,y,100.62));key=hexsolid(2,102.02,1.2);key.translate(V(x,y,0));bolt=shaft.fuse(head).cut(key)
 washerTop=Part.makeCylinder(3,.5,V(x,y,100.12)).cut(Part.makeCylinder(1.35,.5,V(x,y,100.12)));washerBottom=Part.makeCylinder(3,.5,V(x,y,92.02)).cut(Part.makeCylinder(1.35,.5,V(x,y,92.02)));nut=hexsolid(5,90.02,2);nut.translate(V(x,y,0));nut=nut.cut(Part.makeCylinder(1.25,2,V(x,y,90.02)))
 for role,s in [('ISO4762_M2p5x12',bolt),('upper_ISO7089_washer',washerTop),('lower_ISO7089_washer',washerBottom),('full_AF5_nut',nut)]:
  assert s.isValid();o=D.addObject('PartDesign::Feature','PI'+str(i)+'_'+role);o.Shape=s;o.ViewObject.ShapeColor=(.7,.72,.74);grp.addObject(o)
 sets.append(dict(index=i,axis=[x,y],shaft=[88.62,100.62],head=[100.62,103.12],washers=[[92.02,92.52],[100.12,100.62]],nut=[90.02,92.02],underhead_length=12,stack=10.6,tip_beyond_fullnut=1.4,shapes=['PI'+str(i)+'_'+r for r in ['ISO4762_M2p5x12','upper_ISO7089_washer','lower_ISO7089_washer','full_AF5_nut']]))
plan=dict(status='SAVED_FULL_FOUR_THROUGHSETS_BEFORE_PRINT_CUT',utc=datetime.now(timezone.utc).isoformat(),sets=sets,nominal=dict(head_diameter=4.5,head_height=2.5,hex_key_AF=2,socket_depth=1.1,washer_ID=2.7,washer_OD=6,washer_h=.5,nut_AF=5,nut_h=2,stock='NEEDED_UNCONFIRMED; no purchase/inventory'),source='Bossard primary-authored ISO4762/ISO7089 sheets; nutAF5/h2 nominal assembly-demand pending actual chosen supplier',printed_standoff=3,second_standoff=False,actualPCBholes=dict(radius=1.375,X=[-74.5,-16.5],Y=[-34.5,14.5]),physical_pass=False,new_operating_print_cut=False)
(P/'Pi-throughset-plan.json').write_bytes((json.dumps(plan,indent=2)+'\n').encode());D.recompute();D.saveAs(str(P/'pi-battery-carrier.FCStd'))
# Cheap FIRST full actualsteel checks. BNO installcover classification remains separate fromactualbody.
result=dict(status='FULLSET_PRECUT_CHECKS',actualPCB=[],BNO_body=[],BNO_allocation=[],first_unqualified_allocation=None)
for st in sets:
 for n in st['shapes']:
  s=D.getObject(n).Shape
  c=s.common(D.getObject('Pi4B_actual_PCB').Shape);result['actualPCB'].append(dict(a=n,valid=c.isValid(),common_mm3=c.Volume));assert c.isValid() and c.Volume<1e-5
  for target,key in [('BNO085','BNO_body'),('BNO_FULL_SOURCE_INSTALLATION_COVER','BNO_allocation')]:
   gap=s.distToShape(D.getObject(target).Shape)[0];row=dict(a=n,b=target,gap=gap,required=1.25);result[key].append(row)
   if key=='BNO_allocation' and gap<1.25 and result['first_unqualified_allocation'] is None:result['first_unqualified_allocation']=row
result['status']='ACTUAL_PCB_CLEAR_BNO_BODY_CLEAR_BNO_INSTALLATION_ALLOCATION_OPEN' if result['first_unqualified_allocation'] else 'ACTUAL_PCB_AND_NAMED_BNO_CHECKS_CLEAR'
(P/'Pi-precut-result.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(dict(status=result['status'],actualPCBchecks=len(result['actualPCB']),actualBNOminimum=min(x['gap'] for x in result['BNO_body']),first=result['first_unqualified_allocation'])))
