from pathlib import Path
import json,hashlib,shutil,zipfile,subprocess
from datetime import datetime,timezone
ROOT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');P=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-audio-region-proof'
def pin(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
for n in ['day15-region-build.py','day15-region-check.py','day15-region-notes.py','day15-region-package.py']:shutil.copyfile(Path('C:/Users/Sysq/AppData/Local/Temp')/n,P/n)
sources=[]
for folder,want in [('day15-audio-module-layer','7ae9fbfd70ab45c57ce7aff7b67a0362c086aa8836a26cc7386e169ef5c68c73'),('day15-shared-module-fit','25528ddb41c2b6a1fca378591a1c934bc339276f7d405290b0083bec4b26adfa'),('day14-fasttrack-first-fit/fit-kit-ready','addaabc4ed3316366fed61812b85e1805013d67ee67cadf5fb96cb165bde2861')]:
 q=P.parent/folder/'manifest.json';assert pin(q)['sha256']==want
 for x in json.loads(q.read_bytes())['files']:assert pin(Path(x['path']))['sha256']==x['sha256'],x['path']
 sources.append(pin(q))
saved=json.loads((P/'native-save-received.json').read_bytes());assert saved['gui_modified'] is False and saved['objects']==267
with zipfile.ZipFile(P/'audio-region-proof.FCStd') as z:assert z.testzip() is None;crc=len(z.namelist())
r=json.loads((P/'local-result.json').read_bytes());plan=json.loads((P/'proposal.json').read_bytes());assert r['first_falsifier']['gap_mm']==1.1842644469722738
files=sorted(x for x in P.iterdir() if x.is_file() and x.suffix!='.FCBak' and x.name!='manifest.json')
m=dict(status='ONE_CONTINUOUS_OCCUPIED_AUDIO_ALLOCATION_HOLD_NO_NEW_MATERIAL',frozen_utc=datetime.now(timezone.utc).isoformat(),files=[pin(x) for x in files],source_manifests=sources,frozen14_21_36_unchanged=True,native=saved,native_crc_members=crc,first_falsifier=r['first_falsifier'],received_foreign_pairs=4,unreceived_foreign_pairs=80,unreceived_packing_pairs=21,feed_capacity_unreceived=True,profiles=7,actual_feed_count=2,upper_Pi_count=5,material_or_bought_pose_changed=False,local_R_basis='4OD project fit assumption, minima11.3 vs required6.4/8.4; no maker claim',constructor_coverage='all7 valid1solid, volume pi*r2*L, nominal missingfromcover0',local_test_wall_seconds=r['wall_seconds'],local_test_cpu_seconds=r['cpu_seconds'],classification='Allocated fullprofile+0.4 vs nominal Pi cooling/component reserve. validcommon0; no deliveredcontact/allroutesimpossible. Firstgeometrycause stops allocation. No secondfamily.',open_interfaces=plan['interfaces'],whole_harness_pass=False,print_release=False,physical_pass=False,actual_cut_fit_slack=None,recovery='SystemExit escaped MCP after saved result; backed up files/temp, ended only verifiedown8920, confirmedabsence/portdown then ONE GUI17796, checkpoint reopened withno geometry replay. Normalreturn check script retained.')
(P/'manifest.json').write_bytes((json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode())
paths=[str(Path(x['path']).relative_to(ROOT)).replace('\\','/') for x in m['files']]+[str((P/'manifest.json').relative_to(ROOT)).replace('\\','/')];cmd=['git','-c','core.autocrlf=false'];subprocess.run(cmd+['add','--']+paths,cwd=ROOT,check=True);subprocess.run(cmd+['commit','--only','-m','Record one occupied audio region and Pi cooling margin HOLD','--']+paths,cwd=ROOT,check=True)
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',str(P.relative_to(ROOT)).replace('\\','/')],cwd=ROOT);cnt=0
for rec in raw.split(b'\0'):
 if not rec:continue
 meta,path=rec.split(b'\t',1);blob=subprocess.check_output(['git','cat-file','blob',meta.split()[2].decode()],cwd=ROOT);assert blob==(ROOT/path.decode()).read_bytes();cnt+=1
actual=subprocess.check_output(['git','diff-tree','--no-commit-id','--name-only','-r',commit],cwd=ROOT,text=True).splitlines();assert sorted(actual)==sorted(paths) and cnt==len(paths)
v=dict(commit=commit,exact_files=cnt,manifest_sha256=pin(P/'manifest.json')['sha256'],native_crc_members=crc);Path('C:/Users/Sysq/AppData/Local/Temp/day15-region-verified.json').write_bytes((json.dumps(v)+'\n').encode());print(json.dumps(v))
