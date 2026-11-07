from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,html
from PIL import Image,ImageDraw
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['day07-FPI-cradle-preserved-V-root-functional-joint-proposal.json','day07-FPI-real-cradle-preserved-V-root-first-gates.json','day07-FPI-real-cradle-preserved-V-root-first-gates.breps.zip','day07-FPI-case-cradle-SideLeft-function-and-components.json','day07-FPI-cradle-SideLeft-actual-component-witness.breps.zip','day07-FPI-cradle-rear-tail-portal-loadpath-correction1.json','day07-FPI-rear-portal-correction1-current-material.json','day07-FPI-rear-portal-correction1-current-material.breps.zip','day07-FPI-cradle-C0-C1-actual-received-sections.json']
b=json.loads((out/names[1]).read_bytes());a=json.loads((out/names[3]).read_bytes());c=json.loads((out/names[6]).read_bytes());v=json.loads((out/names[8]).read_bytes())
assert b['cursor']==4 and b['unreceived']==19 and c['cursor']==1 and c['unreceived']==4
assert abs(c['first_falsifier']['common_mm3']-10.092776504840048)<1e-7 and c['actual_root_mm3']>0
assert all(q['missing_mm3']<1e-7 for q in c['coverage'])
checks=[]
for n in names:
 if n.endswith('.zip'):
  with zipfile.ZipFile(out/n) as z:
   assert z.testzip() is None
   ge=json.loads(z.read('manifest.json'))['geometry']
   for q in ge:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
   checks.append(dict(path=n,crc_ok=True,member_sha_verified=len(ge)))
colors={'NEW_CRADLE':'#e88613','OLD_V_ROOT':'#4475ca','FRAME_FRONT20':'#cf2945','SIDE_LEFT22':'#a43280','FULL_CASE':'#1a955d','FIVE_TAIL_FIELD':'#874db4','T30L_BAND':'#303030','T30L_HEAD_NECK':'#36a4ab'}
im=Image.new('RGB',(1300,840),'white');d=ImageDraw.Draw(im);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="840" viewBox="0 0 1300 840"><rect width="1300" height="840" fill="white"/>']
def text(x,y,s,fill='#222'):
 d.text((x,y),s,fill=fill);svg.append(f'<text x="{x}" y="{y+13}" font-family="sans-serif" font-size="14" fill="{fill}">{html.escape(s)}</text>')
text(24,15,'FPI cradle C0/C1: HOLD / NOT SELECTED / N01 0/10')
text(24,40,'Actual world YZ sections from saved native operands. Projection is context, not a clearance proof.')
for j,xx in enumerate([-66.55,-40]):
 ox=35+j*640;oy=620;scale=6.4
 text(ox,82,'World X='+str(xx)+' mm; Y horizontal, Z vertical')
 for row in v['sections']:
  if row['X_mm']!=xx:continue
  col=colors[row['name']]
  for curve in row['curves_yz']:
   pts=[(ox+(y+35)*scale,oy-(z-28)*scale) for y,z in curve]
   if len(pts)>1:
    d.line(pts,fill=col,width=3);svg.append('<polyline fill="none" stroke="'+col+'" stroke-width="2" points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+'"/>')
 for y in [-20,0,20,40]:text(ox+(y+35)*scale,634,str(y))
 text(ox,665,'C0 SideLeft22: common16.500000 mm3; 4/23, 19 unreceived')
 text(ox,690,'C1 FrameFront20: common10.092777 mm3; 1/5, 4 unreceived')
for i,(n,col) in enumerate(colors.items()):text(24+(i%4)*315,740+(i//4)*27,n,col)
text(24,805,'No old V/cap/BankPad/case pose changed. Real frame conflicts stop this strategy; no third offset.')
svg.append('</svg>');png=out/'day07-FPI-cradle-C0-C1-received-sections.png';sp=png.with_suffix('.svg');im.save(png);sp.write_bytes(('\n'.join(svg)+'\n').encode());names +=[png.name,sp.name]
recipes=['robot-cat72-save-real-case-root-interface.py','robot-cat72-real-cradle-root-stock-first-gates.py','robot-cat72-actual-frame-source-component-fact.py','robot-cat72-save-one-portal-correction.py','robot-cat72-native-rear-portal-correction.py','robot-cat72-save-current-sections-only.py','robot-cat72-package-received-cradle.py']
for src in recipes:
 n='day07-'+src.removeprefix('robot-cat72-').removesuffix('.py')+'.recipe.py';assert not(out/n).exists();(out/n).write_bytes((temp/src).read_bytes());names.append(n)
source=[q for q in json.loads((out/names[0]).read_bytes())['source_pins']]
for q in source:assert sha(out/q['path'])==q['sha256']
p=out/'day07-FPI-real-cradle-V-load-interface-bounded-disposition.json';assert not p.exists()
timings=[dict(receipt=n,operation_seconds=r['operation_seconds'],process_cpu_seconds=r['process_cpu_seconds']) for n,r in [(names[1],b),(names[3],a),(names[6],c),(names[8],v)]]
r=dict(id=p.stem,status='C0_C1_REAL_FRAME_CONFLICTS_STRATEGY_EXHAUSTED_NO_NEW_CURRENT_PARENT',selected=False,N01_complete=False,
 closed_problem='A nominal logical V pressure envelope cannot become FPI OWN fit by name. Actual functional cradle/whole band contact and preserved real V material were built and measured; TWO real frame conflicts reject both loadpath allocations. No third pillar/foot/case nudge and no V source geometry changed.',
 C0=dict(root_mm3=b['actual_root_probe_mm3'],case_floor_contact_mm2=b['actual_case_capture_contacts'],member_count=len(b['new_union']['member_coverage']),missing_max_mm3=max(q['missing_mm3'] for q in b['new_union']['member_coverage']),positive_junctions=len(b['new_union']['positive_joints']),first_falsifier=b['first_falsifier'],received=b['cursor'],total=b['total'],unreceived=b['unreceived']),
 actual_V_component_accounting=dict(old_solids=a['source_old_V_root_solids'],new_C0_solids=a['new_preserved_root_plus_cradle_solids'],changed_case_component=a['case_holding_component'],source_material_not_silently_fused=True,no_strength_claim=True),
 C1=dict(root_mm3=c['actual_root_mm3'],intended_member_count=len(c['coverage']),member_coverage=c['coverage'],positive_junctions=c['positive_joints'],old_solids=c['source_old_solids'],new_solids=c['new_union_solids'],own_material_checks=c['own_material_checks'],stock_portals=c['stock_portals'],first_falsifier=c['first_falsifier'],received=c['cursor'],total=c['total'],unreceived=c['unreceived'],two_cause_attempts_exhausted=True),
 preserved='Original V:new_root_material ALL material/3 full9caps/BankPads/sourceports/crown5/4; b-17.3case/Rx180 and PiSOURCE computer pose; selectedparts/R47P0E6MAIN46.52/foreign1.25/BodyOuter3.25/four independent220/both4MTA. No actual current parent replacement.',
 remaining_OPEN=['Original case/V raw positivegap .750416551 HOLD not reclassified OWN','Four independent wire9 strain lands/actual roots/full head feeds/stock rolls/initial assembly','W0682whole145/root pressure9/S0pair/5tail connected stock current-space acceptance','W078input210 MAINpad-full12/newdebit; currentSOURCE outsideDGV R35.1/55EACH FL2/all9ID12portion4MAX3 AUfit_slackNULL/actualcutNULL','Global123/246/headNorth/U1far/R6/invalid3/Pimates/changedmotion-outline; wholeN01 remains0'],
 next='STOP this C0/C1 cradle strategy. Do not thin/shift a third foot or V bar. Before another FPI support, choose whole fore-neck/PWM/S0/case support-and-stock layer/interface using actual retained frame loadinterfaces and preserve V3 source prerequisite. Independent USB3 current-invalid operand/source-cover disposition is safe next work while whole SOURCE AU/850/MAX3 remainsOPEN; no replay accepted pairs.',
 view=dict(path=png.name,sha256=sha(png),source=names[8],actual_sections=True,no_projection_contact_claim=True,visually_inspected=False),timings=timings,measured_native_wall_seconds=sum(q['operation_seconds'] for q in timings),measured_native_CPU_seconds=sum(q['process_cpu_seconds'] for q in timings),source_pins=source,packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=checks,native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False),written_utc=datetime.now(timezone.utc).isoformat())
p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(dict(receipt=p.name,sha256=sha(p),packet_pins=len(names),source_pins=len(source),archives=checks,wall=r['measured_native_wall_seconds'],CPU=r['measured_native_CPU_seconds']),indent=2))
