import FreeCAD as A,FreeCADGui as G,Part,math,json
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;S=A.getDocument('DAY15_STRAPPED_CARRIER');P=Path(S.FileName).parent.parent/'day15-direct-carrier-frame-joint';P.mkdir(exist_ok=True);D=A.newDocument('DAY15_DIRECT_CARRIER');groups={}
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape.copy();q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
gr=D.addObject('App::DocumentObjectGroup','DIRECT_PLANNED_INTERFACE_BEFORE_UNION');members=[]
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def put(n,s,role):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.9,.6,.15);o.ViewObject.Transparency=45;gr.addObject(o);members.append(dict(name=n,role=role,bounds=str(s.BoundBox)));return o
put('DIRECT_P12_receiver_tab',box(68,18,88.52,16,23.5,4),'P12 integralreceiver, sourcecommon512 atX68..84/Y18..26. NotP11material')
put('DIRECT_P12_key_cheek_left',box(68,24,84.52,2,17.5,6),'P12 integralXlocatingcheek/antiZrotation atseparatedYpoints')
put('DIRECT_P12_key_cheek_right',box(82,24,84.52,2,17.5,6),'P12 integralXlocatingcheek')
put('DIRECT_P19_loadbeam',box(74,35.5,62,26,6,4),'P19 integratedbeam joiningactualrear crossarm95..100 beforebatteryregion')
put('DIRECT_P19_upriser',box(74,35.5,64,7.6,6,22.52),'P19 upriser onpositiveY outsidebattery, useful7.6x6section')
put('DIRECT_P19_flange',box(70.4,24,84.52,11.2,17.5,4),'P19 keyedunderflange, .4Xclear eachside, matchedtopbearing88.52')
def hx(af,z,h):
 rr=af/math.sqrt(3);pp=[V(76+rr*math.cos(i*math.pi/3),30+rr*math.sin(i*math.pi/3),z) for i in range(7)];return Part.Face(Part.Wire(Part.makePolygon(pp).Edges)).extrude(V(0,0,h))
cone=Part.makeCone(1.5,3.36,1.86,V(76,30,90.66));bolt=Part.makeCylinder(1.5,10.14,V(76,30,80.52)).fuse(cone).cut(hx(2,91.42,1.2));washer=Part.makeCylinder(3.5,.5,V(76,30,84.02)).cut(Part.makeCylinder(1.6,.5,V(76,30,84.02)));nut=hx(5.5,81.62,2.4).cut(Part.makeCylinder(1.5,2.4,V(76,30,81.62)))
steel=[]
for n,s in [('DIRECT_ISO10642_M3x12_full',bolt),('DIRECT_full_OD7_washer',washer),('DIRECT_full_AF5p5_nut',nut)]:
 o=put(n,s,'FullstandardUNCONFIRMEDdemand, M3x12includeshead, noactualinventory/threadclaim');o.ViewObject.Transparency=0;o.ViewObject.ShapeColor=(.7,.72,.75);steel.append(n)
plan=dict(utc=datetime.now(timezone.utc).isoformat(),status='ONE_WHOLE_DIRECT_POSITIVEY_LOAD_HYPOTHESIS_SAVED_BEFORE_GATE',source_document=S.Name,source_native=S.FileName,source_receiver=dict(owner='P12',ROI=[68,18,88.52,84,26,92.52],actual_common=512,P11_common=0),axis=[76,30],members=members,stack=dict(type='ISO10642 M3x12 countersunk standarddemandUNCONFIRMED',length_includes_head=True,headD6p72=True,headheight1p86=True,headtop92p52=True,P12_thickness4=True,P19_flange4=True,washer0p5=True,nut2p4=True,nutbottom81p62=True,tip80p52=True,tip_beyondnut1p1=True,upperwasher=False,upperbearing='nominalactualconicalseat replacesheadwasherfunction, fullheadretained'),loadpath=['P19floor ->existingrearcrossarm95..100 ->newpositivebeam ->upriser7.6x6 ->underflange','completeverticalbolt capturesunderflange toactualP12receiver','two integralP12cheeks .4nominalsidegap plusfullshaft/bore constrainX/Y/Zrotation, notfrictionalone','P12existingwholeframejoints/fourdeckclamps ->foundation; fourP19feet receivedcompressionretained'],initial_order=['P19emptyonfourdeckfeet, allunpowered, oldfrontjointretainedinitialreference','InstallnewP12 byitsrealparting/openframe BEFOREPCB/banks; keyedflange entersopenbottomcheeks, fullnut+washerheldfrompositiveY','FullHEX2/R4.25driverfromabove BEFOREMAIN/P14/touchkit finalattachment. Solderedbenchkitkeptwhole/handlaid, novirtualunplug','Thenfullbanks/4independentMTA220/factoryends; prethreadsame2whole200straps forbatteryONLY, thenPCB/MIC/BUS/XT60balance/cell order'],fulltool='R4.25cylinder92.52..162.52, expectedMAIN/P14phaseoverlap mustbeactualrecorded; no permanentmetaloverlapallowed',source_roles_not_silently_deleted=True,old_rear_actualS0_negative_preserved=True,oldfront_entirejoint_initially_retained=True,no_retirement_before_newproof=True,physical_pass=False,actual_fit_cut_slack=None)
(P/'whole-joint-plan.json').write_bytes((json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode());D.recompute();D.Label='DAY15 DIRECT CARRIER / onepositiveYjoint BEFOREGATE';D.saveAs(str(P/'direct-carrier.FCStd'))
print(json.dumps(dict(saved=D.FileName,objects=len(D.Objects),candidate_members=len(members))))
