import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;S=A.getDocument('DAY15_CARRIER_CONTOUR');P=Path(S.FileName).parent.parent/'day15-carrier-capture-first-fit';P.mkdir(exist_ok=True)
screen=json.loads((P/'finite-missing-screen.json').read_bytes());assert json.loads((P/'front-receiver-source.json').read_bytes())['actual_source_common']>0
plan=dict(utc=datetime.now(timezone.utc).isoformat(),status='ONE_COHERENT_CAPTURE_AND_LINKED_BELT_ARCHITECTURE_BEFORE_MATERIAL',finite_screen='finite-missing-screen.json',causes=['FixedP05+currentM3x50 guard, replaceFULLWIDTHwall withbroadrearstop +openpostbay','PreservefrontfullM3x16axis/steel byREALP10receivingear, actual48sourcecommon; no newbolt/rootfamily','Bothloops mustlinkactualclosedcarrierwindows, notbattery-onlyfields'],rear=dict(bay_actual_post=[107,12,48.52,113,18,88.52],guard1p5_includes1p25plusp25_trial=True,bay=[105.5,10.5,47.02,114.5,19.5,90.02],working_stopY=[-21,9.5],rear_cell_face_covered27=True,full_cell_floor_preserved_to104p5=True,oldnegativeS0_R5_unchanged=True),anchors=dict(stations=[29.5,52.5],side=['positiveY','negativeY'],barY=[[18.75,20.5],[-20.5,-18.75]],barZ=[67.4,71.4],full_bar_X_length21=True,endwebs2p4_outside15band_withp6each=True,window_X_width16p2=True,window_floor62p8_roof67p4_height4p6=True,whole15x2p2profile_unchanged=True,buckle_stays_outside_thread_freeend_beforecell=True,bar_in_actual_closedcavity_required=True,cell_foreign_min1p25=True),front=dict(axis_unchanged=[-104.5,-35,70],full_M3x16_two_washers_nut_unchanged=True,P10ear=[-104,-39,64.5,-98,-31,76],actual_root48=True),all_other_poses_parts_stock_unchanged=True,initial_order=['BareP10/P11/foundation withP19, fullfrontjoint andverticalP12joint driverbeforeMAIN','Prethreadfreeends ofbothwhole200throughclosedcarrierwindows; buckleout, no metalbuckleforcedthroughslot','Dummy/cell onopenP19 BEFOREP12closure; P12 actualXYcolumn minZ88 vs86.5 provescellverticalapproach boundonly, otherprintlinkscheckedseparately','CloseP12 onactualparting, wholebenchE1/TTPkit notunplugged; installnuts/driver beforeMAIN/banks, then4independentMTA220bothends andothermoduleassemblies','Closeactualbuckles/wholeuncuttails, thenMAIN/MIC/BUS; laterbatterychange requireslegitimatepartialP12release inclPi-on-P10corner andselectedrealplugs, factoryleadreachFIT2'],physical_strength_stock_lap_ends_FIT=True,actual_fit_cut_slack=None)
(P/'whole-capture-plan.json').write_bytes((json.dumps(plan,indent=2)+'\n').encode())
D=A.newDocument('DAY15_CARRIER_CAPTURE');groups={}
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor') or o.Name.startswith('COUPON_'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape.copy();q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
old19=D.getObject('P19_shared_lower_carrier').Shape.copy();old10=D.getObject('P10_front_gate').Shape.copy();guard=box(105.5,10.5,47.02,9,9,43);stopopen=box(104.5,9.5,65,4,12,3.1)
p19=old19.cut(guard).cut(stopopen);members=[]
for i,x in enumerate([29.5,52.5]):
 y=18.75 if i==0 else -20.5
 for role,s in [('bar',box(x-10.5,y,67.4,21,1.75,4)),('endwebA',box(x-10.5,y,61.8,2.4,1.75,7.6)),('endwebB',box(x+8.1,y,61.8,2.4,1.75,7.6))]:
  n='CAPTURE_ANCHOR'+str(i)+'_'+role;members.append((n,s));p19=p19.fuse(s)
ear=box(-104,-39,64.5,6,8,11.5);bore=Part.makeCylinder(1.65,12,V(-106,-35,70),V(1,0,0));p10=old10.fuse(ear).cut(bore)
assert p19.isValid() and p10.isValid()
D.getObject('P19_shared_lower_carrier').Shape=p19;D.getObject('P10_front_gate').Shape=p10
gr=D.addObject('App::DocumentObjectGroup','CAPTURE_CONSTRUCTION_OPERANDS_NOT_EXTRA_PARTS')
for n,s in members+[('CAPTURE_FRONT_RECEIVER_EAR',ear)]:
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.Visibility=False;gr.addObject(o)
D.recompute();D.Label='DAY15 CAPTURE / onewholecandidate / BEFOREGATE';D.saveAs(str(P/'carrier-capture.FCStd'))
r=dict(status='SAVED_COHERENT_CAPTURE_BEFORE_CHECKS',members=[],junctions=[],preserved=[],belt_links=[],first_falsifier=None)
for n,s in members:
 m=s.cut(p19);r['members'].append(dict(name=n,missing=m.Volume,valid=m.isValid(),extent=str(s.BoundBox)));assert m.isValid() and m.Volume<1e-5
q=ear.cut(bore).cut(p10);r['members'].append(dict(name='P10frontreceiver',missing=q.Volume,valid=q.isValid()));assert q.Volume<1e-5
for n,expected,now in [('P19source_exceptplannedbay',old19.cut(guard).cut(stopopen),p19),('P10source_exceptexistingaxisbore',old10.cut(bore),p10)]:
 m=expected.cut(now);r['preserved'].append(dict(name=n,missing=m.Volume,valid=m.isValid()));assert m.Volume<1e-5
for i,x in enumerate([29.5,52.5]):
 names=['CAPTURE_ANCHOR'+str(i)+'_'+t for t in ['bar','endwebA','endwebB']];bar=dict(members)[names[0]];wa=dict(members)[names[1]];wb=dict(members)[names[2]]
 for tag,a,b in [('barA',bar,wa),('barB',bar,wb),('rootA',wa,old19),('rootB',wb,old19)]:
  c=a.common(b);r['junctions'].append(dict(anchor=i,name=tag,positive=c.Volume,valid=c.isValid()));assert c.isValid() and c.Volume>1e-5
 # Same receivedclosedloop cavity; bar inside it and connected outsideband atbothends is a REALlinkedwindow.
 y=-21;z=65;w=42;h=21.5;rr=1.9;cavity=box(x-7.5,y+rr,z,15,w-2*rr,h).fuse(box(x-7.5,y,z+rr,15,w,h-2*rr))
 for yy in [y+rr,y+w-rr]:
  for zz in [z+rr,z+h-rr]:cavity=cavity.fuse(Part.makeCylinder(rr,15,V(x-7.5,yy,zz),V(1,0,0)))
 inside=bar.common(cavity);stock=D.getObject('STRAP'+str(i)+'_bodyloop_full2p2').Shape;c=stock.common(p19)
 r['belt_links'].append(dict(anchor=i,bar_inside_closed_cavity=inside.Volume,stock_vsprint_common=c.Volume,valid=c.isValid(),endweb_gap_to_band_X=.6,closed_window=[16.2,4.6],not_volumealone='bar21 spansfull15band;2actualendwebsoutsidebandjoinfullfloor; closedXZwindowlinkedbyclosedYZbelt. Freeendthread beforecell, buckleoutside.'));assert inside.Volume>1e-5 and c.Volume<1e-5 and c.isValid()
r['front_root']=dict(positive=ear.common(old10).Volume,fullfrontaxis_preserved=True)
r['separate_prints']=[dict(pair=a+'/'+b,common=D.getObject(a).Shape.common(D.getObject(b).Shape).Volume) for a,b in [('P19_shared_lower_carrier','P10_front_gate'),('P19_shared_lower_carrier','P12_common_deck_speaker')]]
assert all(x['common']<1e-5 for x in r['separate_prints'])
r['new_solids']=[len(p10.Solids),len(p19.Solids)];r['planned_source_replacement_removed']=old19.cut(p19).Volume;r['status']='MATERIAL_AND_ACTUAL_BOTH_CLOSED_BELT_LINKS_SCOPED_CLEAR';(P/'capture-material-proof.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(dict(status=r['status'],members=len(r['members']),links=r['belt_links'],front=r['front_root'],junctions=r['junctions'],solids=r['new_solids'])))
