import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;S=A.getDocument('DAY15_PI_BATTERY_CARRIER');P=Path(S.FileName).parent.parent/'day15-p12-integrated-retention';P.mkdir(exist_ok=True);D=A.newDocument('DAY15_P12_INTEGRATED');groups={};exclude=lambda n:n.startswith(('PI0_','PI1_','PI2_','PI3_','COUPON_','VIEW_ACTUAL_','STRAP15_'))
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor') or exclude(o.Name):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape.copy();q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
grp=D.addObject('App::DocumentObjectGroup','PI_INTERNAL_M2p5x8_FULL_STANDARD_SETS');sets=[]
def hx(af,z,h):
 rr=af/math.sqrt(3);p=[V(rr*math.cos(math.pi/6+i*math.pi/3),rr*math.sin(math.pi/6+i*math.pi/3),z) for i in range(7)];return Part.Face(Part.Wire(Part.makePolygon(p).Edges)).extrude(V(0,0,h))
for i,(x,y) in enumerate([(x,y) for y in [-34.5,14.5] for x in [-74.5,-16.5]]):
 shaft=Part.makeCylinder(1.25,8,V(x,y,92.62));head=Part.makeCylinder(2.25,2.5,V(x,y,100.62));key=hx(2,102.02,1.2);key.translate(V(x,y,0));bolt=shaft.fuse(head).cut(key);washer=Part.makeCylinder(3,.5,V(x,y,100.12)).cut(Part.makeCylinder(1.35,.5,V(x,y,100.12)));nut=hx(5,94.52,2);nut.translate(V(x,y,0));nut=nut.cut(Part.makeCylinder(1.25,2,V(x,y,94.52)))
 names=[]
 for role,s in [('full_M2p5x8',bolt),('upper_full_washer',washer),('internal_full_nut',nut)]:
  assert s.isValid();n='INT_PI'+str(i)+'_'+role;o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.7,.72,.75);grp.addObject(o);names.append(n)
 sets.append(dict(axis=[x,y],names=names,roof=[96.52,98.52],nut=[94.52,96.52],floor=[92.42,94.42],tip92p62=True,tip_beyondnut1p9=True,wellY=y+8 if y<0 else y-8,owner='P10_front_gate' if i==0 else 'P12_common_deck_speaker'))
plan=dict(status='SAVED_ONE_WHOLE_INTERNAL_CAPTURE_AND_STRAP_GUIDE_BEFORE_PRINT_CUT',utc=datetime.now(timezone.utc).isoformat(),sets=sets,Pi_stack=dict(length_underhead=8,washer=.5,PCB=1.6,roof2=True,nut2=True,stack=6.1,tip1p9=True,standoff3_unchanged=True,lowerwasher_retired=True,physical_stock='NEEDED_UNCONFIRMED'),Pi_actual_root_ownership='onefrontnegativePi post is ACTUAL P10 member; other3P12, from measured currentfootcommon190.85. Neverjoin differentprintsfictionally.',Pi_capture='EnlargefootOD9 below96.52; taperedroof2 tooldOD5boardcontactat98.52. FullnutAF5 insideAF5.2/2.1slot. Four TOP loadingwells at±8Y ->short sidefeed, beforePi, rather blind sideexit intoE1. Floor2/roof2, no externalcage.',strap_station_basis=dict(actualprotected_BUS_root_inner_faces=[16,66],keepout2each_free=[18,64],channels_width=16.2,whole_two_symmetric_stations=[29.5,52.5],interchannel_web=6.8,outer_margin3p4=True,reason='Only central root-free strip chosen from actual BUSroots and CSseats; no stationgrid or old15/80.5 protection. Two centralbands require actualcarrierendstops.'),strap_guide=dict(stations=[29.5,52.5],width=16.2,fulltwo_layer4p4=True,void_Z=[86.1,91.3],own_clearance_Z=.4,own_clearance_X=.6,remaining_rail_roof=4.7,minimum_rail_section=4*4.7,foreign_required=1.25,material_role='purposeful open-bottom guide throughownrails with surviving continuousroof; no purchasedcut'),whole_stock=dict(units=2,width=15,textile200_each=True,total210inclbuckle_NOTextra=True,bodyloop_R3_project=True,bodyloop_length=2*(44.2+23.7)-24+2*math.pi*3,closure_reserve20_project_not_requiredpull=True,full_remaining_tail=200-(2*(44.2+23.7)-24+2*math.pi*3)-20,buckle_region=[20,12,5],buckleZ=[89.5,94.5],tail='Fullremaining49.35 on uppersecondlayer fromY0to−22, R3quarter toY−25/Z86.8 thenverticaldown; cloththickness/buckle/lapactualFIT, no stockPASS'),carrier='Sameonecommontray+MTA67+twoM3frameanchors/fouractualdeckfeet. Mustprove actualroot/contacts/fullsteel beforeSTL.',bought_poses_unchanged=True,old_negative_scopes_preserved=True,new_operating_print_before_tests=False,actual_fit_cut_slack=None)
(P/'whole-integrated-plan.json').write_bytes((json.dumps(plan,indent=2)+'\n').encode());D.recompute();D.saveAs(str(P/'p12-integrated.FCStd'))
r=dict(status='PI_NEW_FULLSETS_PRECUT_RUNNING',rows=[],first_falsifier=None)
def run():
 for st in sets:
  for n in st['names']:
   s=D.getObject(n).Shape
   for target in ['Pi4B_actual_PCB','BNO085','BNO_FULL_SOURCE_INSTALLATION_COVER']:
    q=D.getObject(target).Shape
    if target=='Pi4B_actual_PCB':c=s.common(q);row=dict(a=n,b=target,valid=c.isValid(),common=c.Volume);ok=c.isValid() and c.Volume<1e-5
    else:gap=s.distToShape(q)[0];row=dict(a=n,b=target,gap=gap,required=1.25);ok=gap>=1.25-1e-6
    r['rows'].append(row)
    if not ok:r['status']='FIRST_FULLSET_HOLD_NO_PRINTCUT';r['first_falsifier']=row;(P/'Pi-new-steel-first.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());return
 r['status']='PI_FOUR_INTERNAL_FULLSETS_PCB_AND_FULL_BNO_COVER_CLEAR_SCOPED';(P/'Pi-new-steel-first.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
run();print(json.dumps(dict(status=r['status'],rows=len(r['rows']),first=r['first_falsifier'],objects=len(D.Objects))))
