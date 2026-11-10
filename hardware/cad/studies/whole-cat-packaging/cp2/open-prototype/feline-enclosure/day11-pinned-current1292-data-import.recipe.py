import time,json,hashlib,zipfile,math,os
from pathlib import Path
restore35_t=time.monotonic();restore35_c=time.process_time()
FROZEN35=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat35-pinned-source-read')
source=(FROZEN35/'robot-cat29-resume-n01.py').read_text(encoding='utf-8');exec(compile(source[:source.index('fam=json.loads')],'pinned native/source data only','exec'))
print('RESTORE35_STAGE1_BASE',len(material),len(restMotion),flush=True)
source=(FROZEN35/'robot-cat31-astra-restore56-strict16.py').read_text(encoding='utf-8');source=source[:source.index('assert len(Current56)')];a=source.index(' if row.get(');b=source.index('for z in archives.values():z.close()',a);source=source[:a]+source[b:];exec(compile(source,'current56 imports ONLY no strict tests','exec'))
print('RESTORE35_STAGE2_CURRENT56',len(Current56),flush=True)
source=(FROZEN35/'robot-cat31-astra-restore-named-context.py').read_text(encoding='utf-8');source=source[:source.index("r={'status':'NAMED_CURRENT_CONTEXT")];exec(compile(source,'pinned named context only no old audits','exec'))
print('RESTORE35_STAGE3_NAMED',len(G3IntegrationWorld31),flush=True)
source=(FROZEN35/'robot-cat32-astra-current-composition.py').read_text(encoding='utf-8');exec(compile(source,'pinned current1288 imports only','exec'))
sc35=json.loads((OUT/'day02-astra-resume-source-chain.json').read_bytes())
for filename35 in list(sc35['current_module_manifests'])[-4:]:
 assert hashlib.sha256((OUT/filename35).read_bytes()).hexdigest()==sc35['current_module_manifests'][filename35]
 load_current32(filename35)
resume35=json.loads((OUT/'day02-astra-current-composition-resume.json').read_bytes());wanted35=set(resume35['current_actor_names']);Current35={n:s for n,s in Current32.items() if n in wanted35};Sources35={n:Source32.get(n,{'source':'pinned_named_current_recipe'}) for n in Current35}
for name,rec in resume35['source_overrides'].items():
 if 'archive' not in rec:continue
 ap=OUT/rec['archive'];assert hashlib.sha256(ap.read_bytes()).hexdigest()==rec['archive_sha256']
 with zipfile.ZipFile(ap) as z:raw=z.read(rec['entry'])
 digest=rec.get('brep_sha256',rec.get('sha256'));assert hashlib.sha256(raw).hexdigest()==digest
 s=Part.Shape();s.importBrepFromString(raw.decode());Current35[name]=s;Sources35[name]=dict(rec)
name='North:G2_existing_bed_support_OPEN';ap=OUT/'day02-astra-recovered-G2-standalone-bed.breps.zip'
with zipfile.ZipFile(ap) as z:
 mm=json.loads(z.read('manifest.json'));raw=z.read(mm['entry'])
assert hashlib.sha256(raw).hexdigest()==mm['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());Current35[name]=s;Sources35[name]={'archive':ap.name,'entry':mm['entry'],'brep_sha256':mm['sha256']}
roleindex35=json.loads((OUT/'day02-astra-current1288-restored-source-index.json').read_bytes())['roles']
for n in sorted(wanted35-set(Current35)):
 role=roleindex35[n]
 if role.get('source')=='day31-astra-carrier-current-selection-stop-limit.json':
  Current35[n]=Current56[role['source_role']];Sources35[n]=role
 elif role.get('source_name')=='W041:current_full_factory':
  fn=role['manifest'];meta=json.loads((OUT/fn).read_bytes());g=next(x for x in meta['geometry'] if x['name']==role['source_name']);ap=OUT/meta['archive']
  with zipfile.ZipFile(ap) as z:raw=z.read(g['entry'])
  assert hashlib.sha256(raw).hexdigest()==role['brep_sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());Current35[n]=s;Sources35[n]=dict(role,archive=ap.name,entry=g['entry'])
 else:raise RuntimeError(('UNRESOLVED_CURRENT_SOURCE',n,role))
assert set(Current35)==wanted35,(len(Current35),sorted(wanted35-set(Current35)),sorted(set(Current35)-wanted35))
assert datum==46.52
rows=[dict(name=n,bounds_mm=saved_bounds(s),source=Sources35[n]) for n,s in sorted(Current35.items())]
r=dict(id='day06-recovery-current1292-data-receipt',status='CURRENT1292_RESTORED_DATA_ONLY_NO_COLLISION_OR_STRICT_REPLAY',pid=os.getpid(),session_id=46493,MAIN_mm=datum,actor_count=len(rows),neutral_moving_sources=len(restMotion),rows=rows,source_chain_sha256=hashlib.sha256((OUT/'day02-astra-resume-source-chain.json').read_bytes()).hexdigest(),composition_sha256=hashlib.sha256((OUT/'day02-astra-current-composition-resume.json').read_bytes()).hexdigest(),frozen_recipes_sha256='4bcaa7ae83cb0bfb9e2d2acc38dac75f7f64d699f51f3b0f504d04338ca8b2ca',source_pins=LoadPins32,named_source_pins=NamedPins31,operation_seconds=time.monotonic()-restore35_t,process_cpu_seconds=time.process_time()-restore35_c,old_collision_checks_repeated=0,old_strict_tests_repeated=0,N01_complete=False)
p=OUT/'day06-recovery-current1292-data-receipt.json';q=p.with_suffix('.tmp');q.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());os.replace(q,p);print('RESTORE35_CURRENT1292',len(rows),r['operation_seconds'],r['process_cpu_seconds'],hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
