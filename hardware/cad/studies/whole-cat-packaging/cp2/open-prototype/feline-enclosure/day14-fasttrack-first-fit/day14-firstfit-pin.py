from pathlib import Path
import json,hashlib,zipfile,shutil,os,subprocess
from datetime import datetime,timezone
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit')
MECH=P.parents[7]
def pin(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
shutil.copyfile('C:/Users/Sysq/AppData/Local/Temp/day14-firstfit-freeze.py',P/'day14-firstfit-freeze.py')
shutil.copyfile(__file__,P/'day14-firstfit-pin.py')
d=json.loads((P/'layout.json').read_bytes())
assert len(d['selected_rows'])==57 and d['base']['solids']==126 and len(d['uncertainties'])==3
with zipfile.ZipFile(P/'first-fit.FCStd') as z:
 assert z.testzip() is None
 assert 'Document.xml' in z.namelist()
 native_members=len(z.namelist())
extra=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day11-WORKING_UNSELECTED_N01_0of10.FCStd')
files=[p for p in P.iterdir() if p.is_file() and p.suffix.lower() in ['.json','.md','.csv','.png','.py','.fcstd'] and p.name!='manifest.json']
m=dict(status='FROZEN_ONE_WHOLE_WAVEGO_FIRST_FIT_FOR_REVIEW_NOT_PRINT_PASS',completed_utc=datetime.now(timezone.utc).isoformat(),started_utc='2026-11-14T20:55:50Z',elapsed_wall_seconds=(datetime.now(timezone.utc)-datetime.fromisoformat('2026-11-14T20:55:50+00:00')).total_seconds(),continuous_compute_claim=False,files=[pin(p) for p in sorted(files)],extra_shape_source=pin(extra),native=dict(pid=19584,document=d['document'],object_count=138,pending=None,own_document_modified=False,unsaved=False,gui_left_open=True,observed='mcp list_documents after CtrlS; nativeZIP CRC allmembers',zip_members=native_members,reference_docs='Original WAVEGO source unmodified and old1311reference remain open; old reference Label modified by MCP autobackup only, NOTsaved back or selected'),decision=d['decision'],facts=dict(base_unscaled_126solids=True,all57selected_rows_functionally_retained=True,appearance_extension_explicit=True,neutral_deck_gap_mm=6,s0_battery_gap_mm=4.6801637855,battery_nominal_vertical_access_named_fixed_min_mm=2.5),open=d['uncertainties'],preparation_not_acceptance=['No complete collision/motion/payload/electrical or physical acceptance. Namedchecks only.', 'Native includes sourceparts, installenvelopes and constructive support blanks. Shared blank unions/joints/parting/hole/fastener/guard details not released.', 'Factoryends/selectedsource budgets retained; cut/installedfit/slack NULL until actualproposed paths/assembly fit.', 'Cosmetic volumes are envelopes, not manufactured walls/mass or printable STL. Forward mainfuse and rear service panel interfaces visible; no hidden protruding root.'],reproduce='Open pinned WAVEGO native and pinned day11 source-reference in same GUI only as data sources; run build thencomplete thenfreeze scripts. Do not replay old N01 checks or restore oldprintedparents. Saved first-fit.FCStd is standalone and preferred.',review_request='Parent may dispatch ONE whole review + Beauvoir: simplicity/two-person order, actualhardparts/cableaccess, root/payload/motion and Ola appearance. No reviewer spawned by owner.')
(P/'manifest.json').write_bytes((json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'manifest':pin(P/'manifest.json'),'files':len(files),'native':pin(P/'first-fit.FCStd'),'layout':pin(P/'layout.json')}))
