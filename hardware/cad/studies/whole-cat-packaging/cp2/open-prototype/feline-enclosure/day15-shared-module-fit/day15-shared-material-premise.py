import FreeCAD as A,FreeCADGui as G,Part,json,time,math
from pathlib import Path
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-shared-module-fit');D=A.getDocument('DAY15_SHARED_MODULE_PROPOSAL');plan=json.loads((P/'proposal.json').read_bytes());V=A.Vector;T=time.perf_counter();CPU=time.process_time()
# Samewholeproposal: define commonLplatform's complete load envelope before material/portgate. Not a newpose/height family.
D.getObject('CF_upright_logic_strip').Shape=Part.makeBox(122,23.5,4,V(-96,18.5,90));D.getObject('CF_upright_logic_strip').AssemblyNote='Integral commonLwing reachesinnerrail/Pitray; realroot, notfloating8mmstrip. PCA/E1 seat at94. Retention/terminalaccessOPEN.'
master_names=['CF_front_portal','CF_rear_portal','CF_long_rail_m17','CF_long_rail_18','CF_Pi_shared_tray','CF_power_logic_ledge','CF_upright_logic_strip']+['CF_Pi_post_'+str(i) for i in range(4)]+['CL_'+t+'_upper' for t in ['Fm','Fp','Rm','Rp']]
members=[D.getObject(n).Shape for n in master_names];s=members[0]
for m in members[1:]:s=s.fuse(m)
loss=[m.cut(s).Volume for m in members];assert s.isValid() and max(loss)<1e-5
o=D.addObject('PartDesign::Feature','CF_COMMON_LOAD_ENVELOPE');o.Shape=s;o.ViewObject.ShapeColor=(.66,.75,.83);D.getObject('NEW_SHARED_SUPPORT_PROPOSAL_NOT_PRINT_RELEASED').addObject(o)
o.addProperty('App::PropertyString','AssemblyNote').AssemblyNote='CoarseCOMMONrigidmaterialunion, NOTprint/export. Parting into flatendpanels/rails+boltedjoints stillOPEN. Namedmembers hiddenSOURCEFUNCTIONreferences, notduplicateoperatingBOM. No boughtpart/pressurejaw/battery/BUS fusion.'
for n in master_names:D.getObject(n).ViewObject.Visibility=False
bridge_names=['CF_BUS_removable_bridge','CF_BUS_bridge_leg_12','CF_BUS_bridge_leg_62'];bs=D.getObject(bridge_names[0]).Shape
for n in bridge_names[1:]:bs=bs.fuse(D.getObject(n).Shape)
b=D.addObject('PartDesign::Feature','CF_REMOVABLE_BUS_BRIDGE');b.Shape=bs;b.ViewObject.ShapeColor=(.4,.65,.72);D.getObject('NEW_SHARED_SUPPORT_PROPOSAL_NOT_PRINT_RELEASED').addObject(b)
for n in bridge_names:D.getObject(n).ViewObject.Visibility=False
plan['coarse_material_ownership']=dict(master_members=master_names,member_missing_mm3=loss,master_valid=s.isValid(),master_solids=len(s.Solids),BUS_bridge_members=bridge_names,printparting='OPEN beforeSTL; mastercoarseenvelope NOTsingleproductionprint. Mechanicalendjoins/4bridgeties toqualify. Lower4jaws andBUSBODYremainseparate.',factoryparts_never_fused=True)
plan['status']='WHOLE_COARSE_CONFIGURATION_SAVED_BEFORE_MODULE_MATERIAL_GATE';(P/'proposal.json').write_bytes((json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode());D.recompute();D.save()
# FIRST whole occupied modulematerialfalsifier, numericcullthen tinyvalidoperands. No freewire/reference/cosmetic fields as rigid parts.
r=dict(status='CHECKING_WHOLE_MODULE_MATERIAL',checks=[],not_received=[])
def write():r.update(wall_seconds=time.perf_counter()-T,cpu_seconds=time.process_time()-CPU);(P/'whole-material-gate.json').write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
base=json.loads((P.parent/'day14-fasttrack-first-fit/layout.json').read_bytes());physical=[x for x in base['rows'] if x['evidence'] in ['selected_source','nominal_selected_or_extension_installation_envelope'] and D.getObject(x['object']) and 'bracket_space' not in x['object'] and x['object']!='WAVEGO_complete_126_source_solids']
def lower(a,b):return math.sqrt(sum(max(l1-h2,l2-h1,0)**2 for l1,h1,l2,h2 in [(a.XMin,a.XMax,b.XMin,b.XMax),(a.YMin,a.YMax,b.YMin,b.YMax),(a.ZMin,a.ZMax,b.ZMin,b.ZMax)]))
for part in physical:
 n=part['object'];q=D.getObject(n).Shape;lb=lower(s.BoundBox,q.BoundBox)
 if lb>=1.25-1e-6:continue
 # ExplicitPCBmatchedmountcontact onlyafter realPi4axes/3mmpads or statedcommonbareloweredgebearing; complete retentionnotaccepted.
 own=n in ['Pi4B_actual_PCB','PCA9685_Adafruit815_PCB','E1_populated_prototype_board']
 gap=s.distToShape(q)[0];common=s.common(q);row=dict(a='CF_COMMON_LOAD_ENVELOPE',b=n,source_classification=part['evidence'],gap_mm=gap,common_mm3=common.Volume,valid=s.isValid() and q.isValid() and common.isValid(),functional_fit='barePCBmatchedseat ONLY retentionOPEN' if own else 'foreign retainedfullpart/nominaloccupiedmodule')
 r['checks'].append(row);write()
 if (not row['valid']) or common.Volume>1e-5 or (not own and gap<1.25-1e-6):
  r['status']='HOLD_FIRST_WHOLE_OCCUPIED_MODULE_RELATION';r['first_falsifier']=row;r['not_received']=[x['object'] for x in physical[physical.index(part)+1:]];write();q.exportBrep(str(P/'module-hazard-full-operand.brep'));s.exportBrep(str(P/'common-load-full-operand.brep'))
  if common.isValid() and common.Volume>1e-5:common.exportBrep(str(P/'module-hazard-common.brep'))
  print(json.dumps({'status':r['status'],'first_falsifier':row,'seconds':r['wall_seconds']}));break
else:r['status']='WHOLE_MATERIAL_BAY_SCOPED_CLEAR_NOT_PORT_STOCK_OR_ASSEMBLY_ACCEPTANCE';write();print(json.dumps({'status':r['status'],'checks':len(r['checks'])}))
D.Label='DAY15 whole shared module proposal — gate disposition pending';G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();D.save()
