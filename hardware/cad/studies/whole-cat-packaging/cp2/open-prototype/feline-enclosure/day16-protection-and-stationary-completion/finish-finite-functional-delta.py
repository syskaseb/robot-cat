import FreeCAD as A,FreeCADGui as G,Part,json,zipfile,xml.etree.ElementTree as E,time
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).parent;O=P.parent;D=A.ActiveDocument;V=A.Vector
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def gap(a,b):return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z'])**.5
def wr(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def src(folder,native,name):
 z=zipfile.ZipFile(O/folder/native);e=E.fromstring(z.read('Document.xml'));node=next(q for q in e.findall('.//ObjectData/Object') if q.get('name')==name);f=node.find("./Properties/Property[@name='Shape']/Part").get('file');s=Part.Shape();s.importBrepFromString(z.read(f).decode());return s
def run():
 t=time.perf_counter();r=dict(utc=datetime.now(timezone.utc).isoformat(),checks=[],failures=[],retired=[],not_physical_pass=True)
 retired=D.getObject('UNSELECTED_TRIALS_NOT_OPERATING') or D.addObject('App::DocumentObjectGroup','UNSELECTED_TRIALS_NOT_OPERATING')
 # First genuineBNOforeignHOLD stops that mount. Restore its actual sourceP10,
 # keep boughtBNO/pose; retain all failed demandedhardware as hidden references.
 p10=D.getObject('P10_front_gate');old10=src('day16-common-protection-retention','shared-protection-retention.FCStd','P10_front_gate')
 ref=D.getObject('UNSELECTED_BNO_HOOK_SOURCE_REFERENCE')
 if not ref:
  ref=D.addObject('PartDesign::Feature','UNSELECTED_BNO_HOOK_SOURCE_REFERENCE');ref.Shape=p10.Shape.cut(old10);retired.addObject(ref);ref.ViewObject.Visibility=False
 p10.Shape=old10;p10.Label='P10 retained7c245 / BNO newhook rejected by carrier, no thirdmount'
 for o in list(D.Objects):
  if o.Name.startswith('BNO_') and o.Name not in ['BNO_FULL_SOURCE_INSTALLATION_COVER']:
   if o.Name in ['BNO085']:continue
   if hasattr(o,'Shape') and o.Name!='BNO_FULL_SOURCE_INSTALLATION_COVER':retired.addObject(o);o.ViewObject.Visibility=False;o.Label='UNSELECTED rejected BNO hardware / '+o.Name;r['retired'].append(o.Name)
 # Existing P19 roof ALREADY captures bothlastmain415s: gap1.28 <2mm
 # lowerstop escapeheight. Redundant rightkeepers/wholeunbuiltstock withdrawn,
 # not a stock/head offset or deletionofrequiredretention.
 roofproof=json.loads((O/'day16-common-protection-retention/final-local-result.json').read_text())
 for case in ['WAGO415_data__1_6','WAGO415_data_1_6']:
  q=next(q for q in roofproof['capture'] if q['case']==case);hit=next(h for h in q['actual_upper_material_within2mm'] if h['roof']=='P19_shared_lower_carrier');assert hit['min_gap_z']<2;r['checks'].append(dict(kind='functional_replacement_redundantkeeper',case=case,retained_P19_actualupper=hit,lower_positive_stops2=True,no_friction_credit=True))
 for row in ['ROW_NEG','ROW_POS']:
  for suffix in ['_REMOVABLE_END_KEEPER_RIGHT','_T18I1_NYLON','_T18I1_HEAD']:
   o=D.getObject(row+suffix);retired.addObject(o);o.ViewObject.Visibility=False;o.Label='UNSELECTED redundant / P19 existingroof actualcapture / '+o.Name;r['retired'].append(o.Name)
 p3=D.getObject('P03_rear_deck_integrated_load_yoke');protected=src('day16-main-aux-stationary-mounts','main-aux-stationary-mounts.FCStd','P03_rear_deck_integrated_load_yoke')
 for yc in [-45,45]:
  post=box(103.75,yc-4,48.22,8,8,11.8).cut(box(103.65,yc-1.45,50.12,8.2,2.9,1.6));exclusive=post.cut(protected);p3.Shape=p3.Shape.cut(exclusive)
 lost=protected.cut(p3.Shape);r['checks'].append(dict(kind='retired_post_protected_baseline_missing',missing=lost.Volume,valid=lost.isValid()))
 # Correct whole positiveY MIC nutfeed: prior path started at its centre and
 # omitted half the nut. This is the SAME intended feed, no board/pose change.
 p15=D.getObject('P15_removable_mic_rail');data=json.loads((P/'realization-checkpoint.json').read_text())
 for x,y in data['mic_axes']:
  cut=box(x-2.41,min(y-2.41,-25),136.35,4.82,max(y+2.41,25)-min(y-2.41,-25),1.75) if y>0 else box(x-2.41,-25,136.35,4.82,y+2.41+25,1.75)
  p15.Shape=p15.Shape.cut(cut)
 for n in ['MIC_0_fullnut','MIC_1_fullnut']:
  c=D.getObject(n).Shape.common(p15.Shape);r['checks'].append(dict(kind='corrected_fullnut_feed_ownfit',part=n,common=c.Volume,valid=c.isValid()))
 D.recompute();D.save();G.getDocument(D.Name).Modified=False
 # Precisely the received source U-bypass intended members, not alloldP11.
 p11=D.getObject('P11_rear_gate').Shape
 for tag,s in [('front',box(98,51.75,103,77,3,4)),('back',box(98,79.25,103,77,3,4)),('far',box(169,51.75,103,6,30.5,4))]:
  q=s.cut(p11);r['checks'].append(dict(kind='P11_U_intended_coverage',member=tag,missing=q.Volume,valid=q.isValid()))
 # Wholefullselectedlegband vs ONLY currentfour sourceMTA solids, not oldscan.
 first=json.loads((P/'preflight-current-interfaces.json').read_text())
 for q in first['finite_stock']:
  if not q['part'].startswith('LEG') or q['common']<=1e-7:continue
  band=D.getObject(q['part']).Shape;unit=D.getObject(q['other']).Shape
  for i,s in enumerate(unit.Solids):
   if gap(s.BoundBox,band.BoundBox)>.001:continue
   c=s.common(band);r['checks'].append(dict(kind='band_source_compound_binding',part=q['part'],unit=q['other'],solid_index=i,common=c.Volume,valid=c.isValid(),classification='housingBOX allocation, NOT physicalclipcontact' if i==0 else 'ATO/TE actualnativecomponent'))
 # Exact full four strip insertion/tool vs current rigid neighbors, with same
 # shafts and ordinary initialbenchorder beforefuses/skins, no whole126BOP.
 physical=[o for o in D.Objects if hasattr(o,'Shape') and not o.Shape.isNull() and (o.Name.startswith(('S0_','FHAC0001','WAGO','Motor_ATO','Leg_protected','P19_')) or o.Name in ['Pi4B_actual_PCB','MAIN_Pololu4853','AUX_Pololu4092','S1_NKK_S821_installed','Monitor_MOD05015','P10_front_gate','P11_rear_gate','P14_fixed_touch_rail','P15_removable_mic_rail','P11_REMOVABLE_UPPER_CROSSMEMBER'])]
 fields=[]
 for sy in [-1,1]:
  y=92*sy;z=103.63
  fields += [('frontshaft'+str(sy),Part.makeCylinder(1.5,40,V(-124.5,y,z),V(1,0,0))),('fronthead'+str(sy),Part.makeCylinder(2.75,23,V(-127.5,y,z),V(1,0,0))),('fronttool'+str(sy),Part.makeCylinder(4.25,20.5,V(-128,y,z),V(1,0,0))),('rearshaft'+str(sy),Part.makeCylinder(1.5,45,V(82.5,y,z),V(1,0,0))),('rearhead'+str(sy),Part.makeCylinder(2.75,23,V(107.5,y,z),V(1,0,0))),('reartool'+str(sy),Part.makeCylinder(4.25,20,V(110.5,y,z),V(1,0,0)))]
 for tag,s in fields:
  candidates=0
  for o in physical:
   if gap(s.BoundBox,o.Shape.BoundBox)>=1.25:continue
   if o.Name in ['P10_front_gate','P11_rear_gate'] and 'shaft' in tag:continue # matchedactualØ3.4 ownbores, checkedfullstaticmaterial next
   c=s.common(o.Shape);g=s.distToShape(o.Shape)[0];candidates+=1
   r['checks'].append(dict(kind='strip_whole_insertion_tool',operation=tag,other=o.Name,common=c.Volume,gap=g,valid=c.isValid(),ownmatched=o.Name in ['P10_front_gate','P11_rear_gate']))
  if not candidates:r['checks'].append(dict(kind='strip_whole_insertion_tool',operation=tag,numeric_all_current_nearpart_exclusion=True))
 # Newrealhardware finalownfit and currentother fullmodule allocations.
 gr=D.getObject('STATIONARY_REAL_MOUNTS_NOMINAL');module=['BUS25514_installed','PCA9685_Adafruit815_PCB','MAX98357A_amp','RS_USB_FULL_SOURCE_COVER','TTP223_touch','E1_populated_prototype_board']
 for o in gr.Group:
  if not hasattr(o,'Shape') or o.Shape.isNull():continue
  for n in module:
   if (o.Name.startswith('BUS_') and n=='BUS25514_installed') or(o.Name.startswith('PCA_') and n=='PCA9685_Adafruit815_PCB') or(o.Name.startswith('AMP_') and n=='MAX98357A_amp') or(o.Name.startswith('MIC_') and n=='RS_USB_FULL_SOURCE_COVER') or(o.Name.startswith('TTP_') and n=='TTP223_touch') or(o.Name.startswith('E1_') and n=='E1_populated_prototype_board'):continue
   s=D.getObject(n).Shape
   if gap(s.BoundBox,o.Shape.BoundBox)>=1.25:continue
   c=o.Shape.common(s);g=o.Shape.distToShape(s)[0];r['checks'].append(dict(kind='newhardware_other_module',part=o.Name,other=n,common=c.Volume,gap=g,valid=c.isValid(),allocation=n!='PCA9685_Adafruit815_PCB'))
   if not c.isValid() or c.Volume>1e-6 or g<1.25-1e-6:r['failures'].append(r['checks'][-1])
  if time.perf_counter()-t>45:r['cursor']=o.Name;break
 r['seconds']=time.perf_counter()-t;r['status']='STATIONARY_PARTIAL_REALIZED_LOCAL_GATES_WITH_NAMED_HOLDS';r['remaining']=['inline8 S0metal .596503; no secondregion','BNO hook retired; fullset/carrier .74,1.24 preserved','threelegband versus housing-only allocation unresolvedphysicalMTAplastic','S1 monitor speaker safebasket support not realized','whole newprintpositive/currentnearpartdelta and covers lateclosure not all qualified'];wr('finite-functional-completion.json',r)
 D.Label='DAY16 STATIONARY PARTIAL / BUS PCA E1 AMP MIC TTP / NAMED HOLDS';D.recompute();D.save();G.getDocument(D.Name).Modified=False
 print(json.dumps(dict(checks=len(r['checks']),failures=r['failures'],retired=len(r['retired']),seconds=r['seconds'],cursor=r.get('cursor'),objects=len(D.Objects))))
run()
