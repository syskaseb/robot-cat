import FreeCAD as A,Part,Mesh,MeshPart,json,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def low(a,b):
 a=bb(a);b=bb(b);return sum(max(0,a[i]-b[i+3],b[i]-a[i+3])**2 for i in range(3))**.5
def put(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def run():
 t=time.perf_counter();D.save();s=D.getObject('CB_REMOVABLE_BUS_E1_BRIDGE').Shape;old=Part.Shape();old.read(str(P/'source-ebd-BUS-E1-bridge.brep'));delta=s.cut(old);rows=[]
 names=['BUS25514_installed','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','BNO085','MAX98357A_amp','MAIN_Pololu4853','AUX_FULL9p5_POPULATED_SCOPE','FORE_MTA_REMOVABLE_UPPER_RECEIVER','RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER','PBAY_P_SYS','PBAY_F_PI']
 names += [o.Name for o in D.Objects if hasattr(o,'Shape') and o.ViewObject.Visibility and o.Name.startswith(('S0_','Motor_ATO4A','WAGO415_','NIGHT_INLINE_'))]
 for n in names:
  q=D.getObject(n)
  if not q:continue
  l=low(delta,q.Shape)
  if l>=1.25:rows.append({'neighbor':n,'clear':True,'bounds_lower':l});continue
  valid=delta.isValid() and q.Shape.isValid();gap=delta.distToShape(q.Shape)[0] if valid else None
  rows.append({'neighbor':n,'valid':valid,'gap':gap,'clear':valid and gap>=1.25-1e-7})
 # Nominal received primary PCB2bores; populated underboard cavity remains1.5 clear.
 pcb=Part.makeBox(82.023948,34.006975,1.51,V(16,-23.5,147.585))
 for x,y in [(76.201974,-20.838025),(18.491974,8.081975)]:pcb=pcb.cut(Part.makeCylinder(1.1,2,V(x,y,147.4)))
 hardware=[]
 for o in D.Objects:
  if o.Name.startswith('HB_MIC_') and o.Name!='HB_MIC_PRIMARY_POPULATED_SCOPE' and hasattr(o,'Shape'):
   hardware.append({'name':o.Name,'primary_PCB_common':o.Shape.common(pcb).Volume,'gap_to_primary_PCB':o.Shape.distToShape(pcb)[0]})
  if o.Name.startswith('HB_') and o.Name[3:] in ['F_NEG','F_POS','R_NEG','R_POS']:
   o.Label=o.Name+' WORKING HOLLOW BODY / HOLD actual base+receivers; NO STL'
   if 'FitStatus' not in o.PropertiesList:o.addProperty('App::PropertyString','FitStatus')
   o.FitStatus='HOLD_NOT_PRINT_CURRENT_BASE_AND_RECEIVER_INTERFACES'
 # Export only independent completed nominal MIC/BUS/E1 print, never the held cowl.
 q=s.copy();b=q.BoundBox;q.translate(V(-b.XMin,-b.YMin,-b.ZMin));q.exportBrep(str(P/'N2_BUS_E1_MIC_common_bridge.brep'))
 m=MeshPart.meshFromShape(Shape=q,LinearDeflection=.1,AngularDeflection=.25,Relative=False)
 mesh={'closed':m.isSolid(),'volume':m.Volume,'facets':m.CountFacets,'bbox_local':bb(q),'native_volume':q.Volume,'orientation':'sourceXYZ, minXYZ translated0; underside bridge on bed, support under raised MIC ledges if required','support_brim_allowance_mm':8,'fits256_including_allowance':max(q.BoundBox.XLength,q.BoundBox.YLength,q.BoundBox.ZLength)+8<256}
 release=all(r['clear'] for r in rows) and all(r['primary_PCB_common']<1e-7 for r in hardware) and s.isValid() and len(s.Solids)==1 and m.isSolid() and m.Volume>0 and mesh['fits256_including_allowance']
 if release:
  f=P/'N2_BUS_E1_MIC_common_bridge.stl';m.write(str(f));r=Mesh.Mesh(str(f));mesh['reopened_closed']=r.isSolid();mesh['reopened_volume']=r.Volume
  release=release and r.isSolid() and r.Volume>0
 put('independent-MIC-export-gate.json',{'rows':rows,'steel_vs_PRIMARY_PCB':hardware,'mesh':mesh,'conditional_nominal_dryfit_release':release,'source_bridge_material_missing':old.cut(s).Volume,'safe_annulus_components_and_revision':'PHYSICAL_FIT3, not qualified pressure or delivery','new_MIC_scope_has_no_full_actual_populated_STEP_rehydration':True,'wholePASS':False,'physicalPASS':False,'seconds':time.perf_counter()-t})
 # Actual ALL candidate material, including disconnected fragment, not fake mass savings.
 parts=[]
 for n in ['HB_F_NEG','HB_F_POS','HB_R_NEG','HB_R_POS','CB_REMOVABLE_BUS_E1_BRIDGE']:
  q=D.getObject(n).Shape
  if n.startswith('HB_'):q.exportBrep(str(P/(n+'.HOLD.brep')))
  parts.append({'name':n,'valid':q.isValid(),'solids':len(q.Solids),'volume_mm3':q.Volume,'full_PETG_equivalent_g':q.Volume*.00127,'bounds':bb(q),'status':'UNSELECTED_HOLD_NO_STL' if n.startswith('HB_') else 'CONDITIONAL_PRIMARY_NOMINAL_DRYFIT' if release else 'HOLD'})
 put('actual-candidate-print-material.json',{'density_g_cm3':1.27,'parts':parts,'all_body_fragments_counted':True,'body_mass_is_NOT_accepted_totalrobot_mass':True,'body_infill_not_used_for_savings':True,'MIC_delta_g':(s.Volume-old.Volume)*.00127,'actual_fit_cut_slack':None})
 D.save();print(json.dumps({'release':release,'mesh':mesh,'failures':[r for r in rows if not r['clear']],'hardware_failures':[r for r in hardware if r['primary_PCB_common']>=1e-7],'seconds':time.perf_counter()-t}))
run()
