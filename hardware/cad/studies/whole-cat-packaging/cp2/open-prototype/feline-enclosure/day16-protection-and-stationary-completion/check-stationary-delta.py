import FreeCAD as A,FreeCADGui as G,Part,json,time
from pathlib import Path
from datetime import datetime,timezone
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def gap(a,b):return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z'])**.5
def wr(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def run():
 t=time.perf_counter();gr=D.getObject('STATIONARY_REAL_MOUNTS_NOMINAL');assert gr
 # Full nutcorner clearance and actual slot, same intended normal mounting interface.
 p12=D.getObject('P12_common_deck_speaker');p15=D.getObject('P15_removable_mic_rail')
 for i,x in enumerate([-54.85,-42.15]):p12.Shape=p12.Shape.cut(box(x-2.5,20.4,112.885,9.9,1.8,4.2))
 data=json.loads((P/'realization-checkpoint.json').read_text())
 for x,y in data['mic_axes']:p15.Shape=p15.Shape.cut(box(x-2.41,min(y,-25 if y<0 else 25),136.35,4.82,abs(y-(-25 if y<0 else 25))+2,1.75))
 for n in ['TTP_2_ordinaryspacer','TTP_32_ordinaryspacer']:
  o=D.getObject(n)
  if o:D.removeObject(n)
 for i in range(2):
  head=D.getObject('E1_T18I_'+str(i)+'_head');b=head.Shape.BoundBox;x=-32.65 if i==0 else 27.85;s=head.Shape.copy();s.translate(V(x-b.XMin,0,0));head.Shape=s
  band=D.getObject('E1_T18I_'+str(i)+'_nylon');p12.Shape=p12.Shape.cut(band.Shape)
 D.recompute();D.save();G.getDocument(D.Name).Modified=False
 r=dict(utc=datetime.now(timezone.utc).isoformat(),checks=[],failures=[],physical_pass=False,wholekit_ready=False,actual_cut_fit_slack=None,scope='ONLY genuinely newstationarymaterial/fullnewhardware/currentrigidneighbors/actual7audioCOVERS; invalidBUSwholeSTEP NEVER used')
 def ck(q,ok):
  r['checks'].append(q)
  if not ok:r['failures'].append(q)
 owners=['P10_front_gate','P12_common_deck_speaker','P13_BUS_bridge','P14_fixed_touch_rail','P15_removable_mic_rail']
 for n in owners:
  s=D.getObject(n).Shape;ck(dict(kind='changed_print',name=n,valid=s.isValid(),solids=len(s.Solids)),s.isValid() and len(s.Solids)==1)
 for o in gr.Group:
  if not hasattr(o,'Shape') or o.Shape.isNull():continue
  if o.Name.endswith(('KEEPER','nylon','head')):continue
  owner='P13_BUS_bridge' if o.Name.startswith('BUS_') else 'P10_front_gate' if o.Name.startswith('BNO_') else 'P15_removable_mic_rail' if o.Name.startswith('MIC_') else 'P14_fixed_touch_rail' if o.Name.startswith('TTP_') else 'P12_common_deck_speaker'
  s=D.getObject(owner).Shape
  if gap(s.BoundBox,o.Shape.BoundBox)>.02:continue
  c=o.Shape.common(s);ck(dict(kind='fullnewmetal_vs_intended_ownprint',part=o.Name,owner=owner,common=c.Volume,valid=c.isValid()),c.isValid() and c.Volume<1e-5)
 # Actual sourcePCA bores are checked once against true supplier PCB geometry.
 for q in data['proof']:
  if 'primary_PCA_bore' in q:ck(q,q['valid'] and q['common']<1e-5)
 # Current new hardware vs true foreign parts and full kept connector/cooling allocations.
 names=['P19_shared_lower_carrier','Pi4B_actual_PCB','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','Pi_GPIO1992_factory_female','S1_NKK_S821_installed','Monitor_MOD05015','MAIN_Pololu4853','AUX_Pololu4092','E1_populated_prototype_board','BNO_FULL_SOURCE_INSTALLATION_COVER','Speaker','P11_rear_gate','P11_REMOVABLE_UPPER_CROSSMEMBER']
 names += [o.Name for o in D.Objects if o.Name.startswith(('S0_','Motor_ATO','FHAC0001','Leg_protected','COVER_'))]
 pairs=0
 for o in gr.Group:
  if not hasattr(o,'Shape') or o.Shape.isNull() or o.Name.endswith(('KEEPER','nylon','head')):continue
  for n in names:
   target=D.getObject(n)
   if not target or not hasattr(target,'Shape') or target.Shape.isNull():continue
   if (o.Name.startswith('BNO_') and n=='BNO_FULL_SOURCE_INSTALLATION_COVER'):continue
   if gap(o.Shape.BoundBox,target.Shape.BoundBox)>=1.25:continue
   c=o.Shape.common(target.Shape);g=o.Shape.distToShape(target.Shape)[0];pairs+=1
   row=dict(kind='newfullhardware_foreign',part=o.Name,other=n,common=c.Volume,gap=g,valid=c.isValid(),allocated_not_delivered_contact=n in ['E1_populated_prototype_board','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','Pi_GPIO1992_factory_female','BNO_FULL_SOURCE_INSTALLATION_COVER'])
   ck(row,c.isValid() and c.Volume<1e-5 and g>=1.25-1e-6)
   if len(r['failures'])>=12:break
  if len(r['failures'])>=12:break
 r['new_foreign_exact']=pairs;r['seconds']=time.perf_counter()-t;r['status']='LOCAL_STATIONARY_DELTA_HOLD_FINITE_CAUSES' if r['failures'] else 'LOCAL_STATIONARY_HARDWARE_SCOPED_CLEAR_MATERIAL_COVERAGE_OPEN'
 # Explicit remaining full-stock failure from same previous-family screen.
 r['protection_pending']={'inline8':'onefirstcandidate rejected S0_OUTmetal gap0.596503; no secondregion built','negative415right_keeper_fullstock':'actualS0body commonband35.5368/head75.2666; no deliveredcontact waiver','threelegbands':'each common6.305 with nominalMTAhousingallocation; sourcewholecompound split needed before physicalcontact classification','upper_capture_415':'bothrear cases have actualREAR_PAIR keeper hits per final-local result, not missing','P11_MAIN_AUX_roots_and_captivefeeds':'current actualmissing0 / fullnutwasherfeedscommon0'}
 wr('stationary-delta-result.json',r);D.save();G.getDocument(D.Name).Modified=False
 print(json.dumps(dict(status=r['status'],checks=len(r['checks']),failures=r['failures'],seconds=r['seconds'],objects=len(D.Objects))))
run()
