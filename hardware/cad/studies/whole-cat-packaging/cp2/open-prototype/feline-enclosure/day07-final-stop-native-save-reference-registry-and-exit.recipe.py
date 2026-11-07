# FINAL SAVE ONLY: standard Python metadata; no CAD operation, geometry read/test or rebuild.
import os,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
assert os.getpid()==26064
saved95=[]
for n,v in list(globals().items()):
 if isinstance(v,Path) and v.parent==OUT and v.is_file():
  saved95.append(dict(variable=n,path=v.name,bytes=v.stat().st_size))
registries95={}
for n in ['Current35','context230','op106','rest108','MotionSource31']:
 v=globals().get(n)
 if isinstance(v,dict):registries95[n]=dict(type='dict',keys=[str(k) for k in v.keys()],count=len(v))
 elif isinstance(v,(list,tuple)):registries95[n]=dict(type=type(v).__name__,count=len(v))
reg95=OUT/'day07-final-native26064-saved-reference-registry.json'
registry95=dict(id=reg95.stem,status='FINAL_METADATA_SAVE_ONLY_BEFORE_GRACEFUL_SYSTEMEXIT',pid=os.getpid(),session_id=46493,pending_operation=None,unsaved_geometry=False,geometry_operations_this_script=0,saved_native_Path_references=saved95,current_registry_actor_names=registries95,cache_persistence_NOT_promised=True,hydration='Use pinned source1292 sourcechain/base composition and proposed recipe/archive overrides in terminal shutdown receipt; no geometry lives only in this registry. Transient rejected/forensic cache is not current geometry. Future restore requires NEW human window.',last_received_geometry='day07-SPLIT3plus6-Hip-direct10-Knee55-first-layer-bounded-disposition.json',last_received_geometry_sha256=hashlib.sha256((OUT/'day07-SPLIT3plus6-Hip-direct10-Knee55-first-layer-bounded-disposition.json').read_bytes()).hexdigest(),written_utc=datetime.now(timezone.utc).isoformat())
reg95.write_bytes((json.dumps(registry95,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print('FINAL_OWNER95_SAVED',str(reg95),'SHA',hashlib.sha256(reg95.read_bytes()).hexdigest(),'pendingnull unsavedfalse OWN26064 SESSION46493',flush=True)
print('FINAL_OWNER95_GRACEFUL_SYSTEMEXIT_0',datetime.now(timezone.utc).isoformat(),flush=True)
raise SystemExit(0)
