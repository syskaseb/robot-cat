import FreeCAD as A,Part,json,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def vol(s):return 0. if s.isNull() or not s.Vertexes else s.Volume
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def low(a,b):
 a=bb(a);b=bb(b);return sum(max(0,a[i]-b[i+3],b[i]-a[i+3])**2 for i in range(3))**.5
def run():
 t=time.perf_counter();old=Part.Shape();old.read(str(P/'source6553-front-grid.brep'));new=D.getObject('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER').Shape;delta=new.cut(old)
 rows=[]
 def check(n,s,qn,q,scope,matched=False,field=False):
  l=low(s,q);r={'part':n,'neighbor':qn,'scope':scope,'boundlower':l,'required_foreign':1.25,'matched_intended_contact':matched,'nonliteral_primary_installationfield':field}
  if l>=1.25 and not matched:r.update(clear_scoped=True,method='actual_cached_bounds')
  else:
   valid=s.isValid() and q.isValid();dist=s.distToShape(q)[0] if valid else None;r.update(valid=valid,gap=dist,method='named_delta_geometry')
   if valid and (matched or dist<1.25):r['common']=vol(s.common(q))
   r['clear_scoped']=None if field else (valid and r.get('common',0)<1e-7 if matched else valid and dist>=1.25-1e-7)
  rows.append(r)
  if len(rows)%20==0:put('final-body-neighbor-checks.json',{'rows':rows,'failures':[r for r in rows if r['clear_scoped'] is False],'wholePASS':False,'cursor':len(rows)})
 names=['Battery_GEA223S30X6GT','F0_FHAC0002_30A','XT60H_mated_with_boots','PBAY_POST_F0','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','BUS25514_installed','BNO085','MAX98357A_amp','MAIN_Pololu4853','AUX_Pololu4092','AUX_FULL9p5_POPULATED_SCOPE','ReSpeakerLite_on_REMOVABLE_back','TTP223_touch','Speaker','S1_NKK_S821_installed','Monitor_MOD05015','PBAY_F_PI','PBAY_P_SYS','PBAY_F_AUX','PBAY_P_REAR','PBAY_F_HY','PBAY_F_HP','PBAY_F_TY','Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating','FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER','FORE_MTA_REMOVABLE_UPPER_RECEIVER','MG92B_Tail','Tail608','TAIL_FIXED_BEARING_CARTRIDGE','TAIL_ROTATING_HOLLOW_REAL_ROOT']
 names += [o.Name for o in D.Objects if o.Name.startswith(('S0_','Motor_ATO4A','WAGO415_','WAGO615_','NIGHT_INLINE_')) and o.ViewObject.Visibility and hasattr(o,'Shape')]
 oldrear=Part.Shape();oldrear.read(str(P/'source6553-rear-before-POST.brep'))
 rear_delta=D.getObject('RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER').Shape.cut(oldrear)
 targets=[('new_POST_fixed_delta',rear_delta),('CB_POST_REMOVABLE_OPEN_LEVER_KEEPER',D.getObject('CB_POST_REMOVABLE_OPEN_LEVER_KEEPER').Shape),('new_fixed_common_body_delta',delta),('CB_REMOVABLE_BUS_E1_BRIDGE',D.getObject('CB_REMOVABLE_BUS_E1_BRIDGE').Shape),('CB_REMOVABLE_PSYS_LOWER_BODY_KEEPER',D.getObject('CB_REMOVABLE_PSYS_LOWER_BODY_KEEPER').Shape)]
 for n,s in targets:
  for qn in names:
   o=D.getObject(qn)
   if not o:continue
   matched=qn in ['PCA9685_Adafruit815_PCB','E1_populated_prototype_board','BUS25514_installed','BNO085','MAX98357A_amp','MAIN_Pololu4853','AUX_Pololu4092','PBAY_F_PI','PBAY_P_SYS','PBAY_POST_F0']
   field=matched and qn in ['AUX_FULL9p5_POPULATED_SCOPE']
   # AUX wholecover contains intendedholeposts, notliteralundersideIC.
   if qn=='AUX_FULL9p5_POPULATED_SCOPE':matched=True;field=True
   check(n,s,qn,o.Shape,'newmaterial/currentneighbor',matched,field)
 # All newly modeled complete steel against only nearby currentboughtparts.
 for o in D.Objects:
  if not o.ViewObject.Visibility or not o.Name.startswith('CB_') or o.Name in ['CB_REMOVABLE_BUS_E1_BRIDGE','CB_REMOVABLE_PSYS_LOWER_BODY_KEEPER','CB_POST_REMOVABLE_OPEN_LEVER_KEEPER']:continue
  own='PCA9685_Adafruit815_PCB' if o.Name.startswith('CB_PCA_') else 'BNO085' if o.Name.startswith('CB_BNO_') else 'MAIN_Pololu4853' if o.Name.startswith('CB_MAIN_') else 'AUX_Pololu4092' if o.Name.startswith('CB_AUX_') else 'BUS25514_installed' if o.Name.startswith('CB_BUS_') else 'MAX98357A_amp' if o.Name.startswith('CB_AMP_') else None
  for qn in names:
   q=D.getObject(qn)
   if not q or low(o.Shape,q.Shape)>=1.25:continue
   matched=qn==own;field=matched and own in ['BNO085','BUS25514_installed','MAX98357A_amp']
   if qn=='AUX_FULL9p5_POPULATED_SCOPE' and own=='AUX_Pololu4092':matched=True;field=True
   check(o.Name,o.Shape,qn,q.Shape,'newfullsteel/nearcurrentpart',matched,field)
 # Named addedwing-vs-two unchanged currentminimumfactory fields only.
 for qn in ['CF_W043_raw84p5_ALLOCATED_OD3p1_PLUSp4','CF_XA01_raw84p5_ALLOCATED_OD3p1_PLUSp4']:
  q=D.getObject(qn)
  if q:
   for n,s in targets:check(n,s,qn,q.Shape,'newmaterial/fullselectedminfactoryfield')
 # Actual fixedprintparting, protectedsourcecoverage, printbounds.
 bridge=D.getObject('CB_REMOVABLE_BUS_E1_BRIDGE').Shape;keeper=D.getObject('CB_REMOVABLE_PSYS_LOWER_BODY_KEEPER').Shape
 put('final-common-parting-and-source-coverage.json',{'source6553_missing':vol(old.cut(new)),'newsource_added':vol(new.cut(old)),'front_bridge_common':vol(new.common(bridge)),'front_keeper_common':vol(new.common(keeper)),'bridge_keeper_common':vol(bridge.common(keeper)),'parts':[{'n':n,'valid':s.isValid(),'solids':len(s.Solids),'bounds':bb(s),'maxXYZ_plus8brim':max(s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength)+8} for n,s in [('front',new),('bridge',bridge),('keeper',keeper)]]})
 put('final-body-neighbor-checks.json',{'rows':rows,'failures':[r for r in rows if r['clear_scoped'] is False],'primary_installationunknown':[r for r in rows if r['clear_scoped'] is None],'wholePASS':False,'cursor':len(rows),'seconds':time.perf_counter()-t})
 print(json.dumps({'rows':len(rows),'failures':[r for r in rows if r['clear_scoped'] is False],'fieldunknown':sum(r['clear_scoped'] is None for r in rows),'seconds':time.perf_counter()-t}))
run()
