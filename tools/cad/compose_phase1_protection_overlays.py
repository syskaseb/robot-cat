"""Reconcile accepted source protection with whole K1/K2/K3/A2, no extra points.

Historical selections are immutable. This generator does not alter score, award
E3 or declare physical/print/power readiness. Every changed native gate required.
"""
import copy,json,math,time
from pathlib import Path
from collections import defaultdict
from plan_current_harness_interfaces import ROOT,BASE,SHA
from current_work_guard import check
from phase1_stl_preflight import inspect,fit
from phase1_filament_budget import volume
from release_check import REQUIRED_GATES,verify

OUT=BASE/'functional-protection'
PINS={}
def read(f):
 f=Path(f);PINS[f.relative_to(ROOT).as_posix()]=SHA(f);return json.loads(f.read_text())
def write(f,q):
 f.write_text(json.dumps(q,indent=2)+'\n',newline='\n');return f
def manifest(result,selection,pins,scope):
 files=dict(pins);files[selection.relative_to(ROOT).as_posix()]=SHA(selection)
 q=dict(schema_version=1,result_id=result,readiness='prototype',scope=scope,selected=True,physical_pass=False,
  selection=selection.relative_to(ROOT).as_posix(),files=[dict(path=n,sha256=h) for n,h in sorted(files.items())],
  gates={n:dict(status='open',reason='Nominal prototype preparation only; delivered fit, PETG, tooling, electrical E3 and power remain separate gates.') for n in REQUIRED_GATES})
 q[result+'_complete']=True;q['gates']['geometry']=dict(status='pass',reason='Changed interfaces use qualified native/space evidence; unchanged interfaces inherited explicitly, not rerun or waived.',evidence=[(OUT/'native-mounts.json').relative_to(ROOT).as_posix(),(OUT/'MAIN-insulated-grip-native.json').relative_to(ROOT).as_posix(),(OUT/'BUS-ground-guide-native.json').relative_to(ROOT).as_posix()])
 receipt=verify(ROOT,q);assert receipt['integrity_ok'],receipt;return q
def selected(result,data,file,scope,pins):
 data.update(result_id=result,selected=True,physical_pass=False,scope=scope);data[result+'_complete']=True
 write(file,data);write(file.with_name(file.name.replace('-selection','-manifest')),manifest(result,file,pins,scope))

def run():
 check();tick=time.monotonic()
 receipts={n:read(OUT/(n+'.json')) for n in ['native-mounts','BUS-ground-guide-native','MAIN-insulated-grip-native',
  'W003RetainedUpperBypass','BUS-ground-guide-west-plan','MAIN-insulated-restraint-plan','source-hardware-checks']}
 for n,p in receipts.items():
  assert not p.get('contacts') and not p.get('errors'),(n,p.get('contacts'))
  assert 'COMPLETE' in p['status'] or 'CLEAR' in p['status'],(n,p['status'])
  for path,h in p.get('source_sha256',{}).items():assert SHA(ROOT/path)==h,path;PINS[path]=h
 for r in receipts['native-mounts']['parts']:
  PINS[r['native']]=SHA(ROOT/r['native']);assert r['sha256']==SHA(ROOT/r['path']);PINS[r['path']]=r['sha256']
 for n in ['BUS-ground-guide-native','MAIN-insulated-grip-native']:
  q=receipts[n];assert SHA(ROOT/q['native'])==q['native_sha256'];PINS[q['native']]=q['native_sha256']
  r=q['part'];assert SHA(ROOT/r['path'])==r['sha256'];PINS[r['path']]=r['sha256']
 PINS[Path(__file__).relative_to(ROOT).as_posix()]=SHA(Path(__file__))
 oldk=read(BASE/'phase1-current-print-selection.json');k1=copy.deepcopy(oldk);parts={r['identity']:r for r in k1['prints']}
 aliases={'FoundationProtectedCurrent':'Foundation','FrontRightFixedCarrierProtectedCurrent':'FrontRightFixedCarrier','S1MountCurrent':'S1MountCurrent'}
 updates=[]
 for raw in receipts['native-mounts']['parts']:
  r=copy.deepcopy(raw);r['identity']=aliases[r['part']];updates.append(r)
 updates.extend(copy.deepcopy(receipts[n]['part']) for n in ['BUS-ground-guide-native','MAIN-insulated-grip-native'])
 # E1 explicitly removed the old unknown external U1 board and its two
 # spacer/insulator sets. Its two existing PCB1 anchors also replace the
 # separate PWM1608 top insulators. They are NOT additional current prints.
 retired_ids=['U1InsulatingSpacer','U1TopInsulator','PwmInsulatingWasher']
 delta_volume=0;superseded=[]
 for identity in retired_ids:
  r=parts.pop(identity);assert r['quantity']==2
  delta_volume-=2*volume((ROOT/r['path']).read_bytes())
 for r in updates:
  r.update(part=r['identity'],material='PETG',print_ready=False,physical_fit_gate_open=True,
   selection_module='functional-protection',verified_export_size_mm=r['printing']['size_mm'],brim_each_mm=5,
   print_orientation='Exported STL Zup, PETG coupons/supports in phase2; not slicer approval')
  measured=inspect((ROOT/r['path']).read_bytes());assert measured['closed'] and measured['components']==1 and fit(measured['size_mm'])
  old=parts.get(r['identity']);delta_volume+=volume((ROOT/r['path']).read_bytes())-(volume((ROOT/old['path']).read_bytes()) if old else 0)
  if old:superseded.append(dict(identity=r['identity'],old_path=old['path'],replacement_path=r['path']))
  parts[r['identity']]=r
 k1.update(prints=list(parts.values()),print_job_count=len(parts),installed_print_quantity=sum(r['quantity'] for r in parts.values()),
  functional_protection_supersessions=superseded,source_sha256=dict(PINS))
 k1['retired_E1_prints']=retired_ids
 assert k1['print_job_count']==84 and k1['installed_print_quantity']==117
 k1pins={**oldk['source_sha256'],**PINS}
 selected('K1',k1,BASE/'phase1-current-print-selection-r2.json','Whole open prototype84print identities/117pieces, five current replacement/new source-protection geometries and6obsolete E1 predecessors removed. Unchanged exports retain qualified preflight; new5 checked. No cosmetic torso or physical print approval.',k1pins)

 old=read(BASE/'phase1-current-purchased-selection-r3.json');k2=copy.deepcopy(old)
 for r in k2['roles']:
  if r['id']=='M5 current boards:M3x45':assert r['installed']==4;r['installed']=3
  if r['id']=='M5 current boards:M3_washer_OD7_ID3p2_t0p5':assert r['installed']==16;r['installed']=15
  if r['id']=='M5 current boards:M2x10':assert r['installed']==2;r['installed']=0
  if r['id']=='M5 current boards:M2_nut_AF4_h1p6':assert r['installed']==19;r['installed']=17
 k2['roles']=[r for r in k2['roles'] if r['installed']]
 k2['roles'].append(dict(id='S1 shared frame:M3x50 DIN965',owner='S1 shared frame',size='M3x50 DIN965',canonical_size='M3x50 DIN965',installed=1,
  source='functional-protection/source-hardware-checks.json',note='Replaces one UpperFrame8M3x45 and its upperwasher, not another fastener; delivered >=6mm tip thread required'))
 counts=defaultdict(int)
 for r in k2['roles']:counts[r['canonical_size']]+=r['installed']
 k2['installed_hardware']=dict(sorted(counts.items()))
 k2['hardware_products'].append(dict(size='M3x50 DIN965',supplier='Wurth',supplier_sku='0048350',
  url='https://eshop.wuerth.de/Countersunk-head-screw-with-recessed-head-H-DIN-965-steel-48-zinc-plated-blue-passivated-A2K-SCR-CS-DIN965-48-H1-A2K-M3X50/00483%20%2050.sku/en/US/EUR/',
  dimensions_mm=dict(d=3,L=50,head_d=5.6,head_h=1.65,pitch=.5),project_spare=1,nominal_pack=100,retail_nominal_order=100,purchased=0,
  delivered_fit_gate='Partial thread product: verify last>=6mm actually threaded. PH1 bench installation before S1 case; no steel torque applied to PETG.'))
 for r in k2['hardware_products']:
  r['installed']=counts[r['size']];r['allocations']=[dict(id=q['id'],installed=q['installed']) for q in k2['roles'] if q['canonical_size']==r['size']]
  credit=2 if r['size']=='M10 nut' else 0;r['factory_included_credit']=credit
  r['planned']=r['installed']+r['project_spare']-credit
  if credit:r['retail_nominal_order']=r['planned']
  r['pack_excess']=r['retail_nominal_order']-r['planned'];assert r['pack_excess']>=0
 k2['substitutions']+=['E1 removes old external unknown U1Mount twoM2x10/twoM2nuts; new PCB1 anchors reuse existing twoM2x14/nuts, not these retired external mounts',
  'S1Mount: one M3x50DIN965 replacesUpperFrame8M3x45 and topwasher; same bottom washer/nut',
  'HELLA002843002 includes two installed M10nuts; credit against separate supply, only spare is additional']
 assert k2['drive_count']==15 and counts['M3x45']==3
 selected('K2',k2,BASE/'phase1-current-purchased-selection-r4.json','Whole current purchased set including source mounting hardware reconciliation; no purchases or E3 power acceptance.',{**old['source_sha256'],**PINS})

 old=read(BASE/'phase1-material-selection.json');k3=copy.deepcopy(old)
 for r in k3['wire_blanks']:
  if r['id']=='W003/factory_BUS_core':assert r['nominal_fit_blank_mm']==395;r['nominal_fit_blank_mm']=310
 k3['sleeves']=[r for r in k3['sleeves'] if not r['id'].startswith(('MAIN inner necks/','MAIN shared outer/'))]
 for n in ('W079','W080','W060','W078'):k3['sleeves'].append(dict(id='MAIN individual '+n,sku='RNF100-3/32-0',nominal_blank_mm=13,actual_cut_mm=None,fit_gate=receipts['MAIN-insulated-restraint-plan']['fit_gate']))
 assert len(k3['sleeves'])==46
 for r in k3['sleeve_stock']:
  r['cut_mm']=sum(q['nominal_blank_mm'] for q in k3['sleeves'] if q['sku']==r['sku'])
 k3['sleeve_stock']=[r for r in k3['sleeve_stock'] if r['cut_mm']>0]
 for r in k3['materials']:
  if r['sku']=='AlphaWire802534B':r['installed_blanks']=90;r['cut_draw_mm']=13500
  if r['sku']=='3M VHB4905':r['patches']=13;r['cut_draw_mm']=392;r['additional_patch_mm']=[8,18,.5]
  if r['sku']=='3M Temflex165 LAPP61721030':
   r.update(source_terminal_blanks_mm=[750,750,500,500,500,500],source_practice_mm=1000,total_nominal_draw_plus_practice_mm=5510)
   assert r['nominal_roll_length_mm']>=5510
  if r['sku']=='Sunlu PETG black1.75mm Botland24167':
   budget=read(BASE/'phase1-filament-budget.json');r['functional_protection_delta_solid_mm3']=delta_volume
   r['updated_solid_upper_with35percent_and200g']=budget['planned_total_g']+delta_volume*.001*1.3*1.35
   assert r['updated_solid_upper_with35percent_and200g']<=3000;r['selected_1kg_spools']=3
 k3.update(review_dispositions=[r for r in k3['review_dispositions'] if r['id']!='CURRENT_MAIN_INSULATION'],current_M4_and_E3_open=False,E3_open=True)
 k3['review_dispositions'].append(dict(id='CURRENT_MAIN_INSULATION',individual_raw13_mm=4,formed_OD_project_mm=3.2,
  old_shared_outer_retired=True,actual_fit_gate=receipts['MAIN-insulated-restraint-plan']['fit_gate']))
 selected('K3',k3,BASE/'phase1-material-selection-r2.json','Complete current nominal materials with new5print deltas, four MAIN sleeves, source6wraps, one BUS lace, one POSTpad and shorterW003. Physical fit/supply/E3 remain open.',{**old['source_sha256'],**PINS})

 a2=read(BASE/'phase1-assembly-selection-r2.json');a2=copy.deepcopy(a2)
 a2['print_allocations']=[dict(identity=r['identity'],quantity=r['quantity'],stage='upper_bench' if r['identity']=='S1MountCurrent' else next(q['stage'] for q in a2['print_allocations'] if q['identity']==r['identity'])) for r in k1['prints']]
 a2['source_protection_sequence']=[
  'On unplugged bench fasten S0 into Foundation panel with published twoM6 axes before head installation; actual flange/studclock/nut/tool fit gate.',
  'Install S1Mount peg and shared frame DIN965M3x50 using PH1 before installing switch case or fixing loose wiring. Remove replacedM3x45/topwasher only; keep bottom washer/nut.',
  'Prethread four13mm MAIN sleeves; solder/recover on bench away from PETG. Inspect actual bare coverage/overlap>=6mm/formedOD<=3.2, then seat into new MAIN grip and hand tension expanded existing T18R.',
  'Tighten source ring terminals on bench, cover each of six exposed groups with two half-lapped Temflex passes/folded tip cushion. Do not insulate hot converter case or rely on tape for strain relief.',
  'Route revised continuousW003 along retained upper route, bind new integral BUS guide with one150mm Alpha blank; original endpoint restraints retained.',
  'Bond POST_F0 case onto integral FRdock with8x18x0.5mm4905; support case by hand on lever operation, retained separate wire restraints.',
  'Deep repair reverses actual assembly with sources absent, support/disconnect wires and replace disturbed sleeve/tape/ties. No zero-disconnection service claim.']
 a2['hardware_role_count']=len(k2['roles']);a2['functional_protection_instruction']=(OUT/'ASSEMBLY.md').relative_to(ROOT).as_posix()
 pins={**a2['source_sha256'],**PINS};pins[(OUT/'ASSEMBLY.md').relative_to(ROOT).as_posix()]=SHA(OUT/'ASSEMBLY.md')
 for f in ['phase1-current-print-selection-r2.json','phase1-current-purchased-selection-r4.json','phase1-material-selection-r2.json']:pins[(BASE/f).relative_to(ROOT).as_posix()]=SHA(BASE/f)
 selected('A2',a2,BASE/'phase1-assembly-selection-r3.json','Whole nominal sequence with all117currentprints and source protection preassembly; old external U1Mount/insulators and PWM topinsulators retired by E1. Ordinary supported deep disconnection, not hot service or physicalPASS.',pins)
 summary=dict(status='CURRENT_PROTECTION_K1_K2_K3_A2_OVERLAYS_PREPARED',selected=False,M4_complete=False,
  print_identities=84,installed_prints=117,wire_blanks=len(k3['wire_blanks']),sleeves=46,additional_Alpha_blanks=1,
  replaced_current_prints=[r['identity'] for r in superseded],new_print='S1MountCurrent',physical_pass=False,
  source_sha256=dict(PINS),worker_seconds=round(time.monotonic()-tick,3))
 write(OUT/'quantity-reconciliation.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='source_sha256'}))
if __name__=='__main__':run()
