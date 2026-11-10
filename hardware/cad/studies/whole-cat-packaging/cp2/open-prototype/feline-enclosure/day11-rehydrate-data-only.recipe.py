from pathlib import Path
import time,json,hashlib,os
assert os.getpid()==11476
import sys
os.chdir(r'C:/Users/Sysq/PycharmProjects/robot-cat-mechanical')
sys.path.insert(0,str(Path.cwd()/'tools/cad'))
T11=time.monotonic();C11=time.process_time();OLD11=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat37-restore-current-inputs-only.py');code11=OLD11.read_text(encoding='utf8');code11=code11[:code11.index('rows=[dict(name=n,bounds_mm=saved_bounds(s)')];exec(compile(code11,'PINNED_CURRENT1292_DATA_ONLY_NO_COLLISION_OR_STRICT_REPLAY','exec'))
import FreeCAD as A,Part
cached11=json.loads((OUT/'day06-recovery-current1292-data-receipt.json').read_bytes());bounds11={q['name']:q['bounds_mm'] for q in cached11['rows']};assert len(Current35)==1292
rp11=OUT/'day11-current1292-one-time-data-rehydration-receipt.json';rr11=dict(id=rp11.stem,status='CURRENT1292_ONE_TIME_DATA_REHYDRATED_NO_OLD_TESTS',pid=os.getpid(),session_id=70789,actor_count=len(Current35),neutral_moving_sources=len(restMotion),MAIN_mm=datum,sourcechain_sha256=hashlib.sha256((OUT/'day02-astra-resume-source-chain.json').read_bytes()).hexdigest(),source_composition_sha256=hashlib.sha256((OUT/'day02-astra-current-composition-resume.json').read_bytes()).hexdigest(),import_recipe_path=str(OLD11),import_recipe_sha256=hashlib.sha256(OLD11.read_bytes()).hexdigest(),saved_numeric_source_bounds_from='day06-recovery-current1292-data-receipt.json',saved_numeric_source_bounds_sha256=hashlib.sha256((OUT/'day06-recovery-current1292-data-receipt.json').read_bytes()).hexdigest(),bounds_recomputed_for_all_actors=False,old_collision_tests=0,old_strict_reopens=0,source_proposed_effective1311_not_yet_newwhole_selected=True,operation_seconds=time.monotonic()-T11,process_cpu_seconds=time.process_time()-C11,N01_complete=False);rp11.write_bytes((json.dumps(rr11,indent=2)+'\n').encode());print('OWNER11_CURRENT1292_DATA_SAVED',len(Current35),rr11['operation_seconds'],rr11['process_cpu_seconds'],'NEUTRAL',len(restMotion),flush=True)
