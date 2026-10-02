"""Recover current native Deck,24 end recipes and changed clip-access proof."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r3'

def main():
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'manifest.json').exists()
    parent_path=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r2/manifest.json'
    parent=json.loads(parent_path.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in parent['files']}
    files[parent_path.relative_to(ROOT).as_posix()]=sha(parent_path);reports={}
    for folder,filename,scriptname in [
        ('servo-fuse-deck-native-r1','checks.json','servo_fuse_deck_native_r1.py'),
        ('servo-fuse-bank-electrical-r1','interface.json','servo_fuse_bank_electrical_r1.py'),
        ('servo-fuse-bank-service-r1','checks.json','servo_fuse_bank_service_r1.py'),
        ('servo-fuse-bank-clip-access-r1','checks.json','servo_fuse_bank_clip_access_r1.py'),
        ('servo-fuse-bank-service-r2','checks.json','servo_fuse_bank_service_r2.py'),
        ('servo-fuse-bank-service-r3','checks.json','servo_fuse_bank_service_r3.py')]:
        p=ROOT/'hardware/electronics/full-cat'/folder/filename
        meta=json.loads(p.read_text(encoding='utf-8'));reports[folder]=meta
        script=ROOT/'tools/electronics'/scriptname;assert sha(script)==meta['script_sha256'],script
        files[script.relative_to(ROOT).as_posix()]=sha(script)
        for rel,h in meta['source_sha256'].items():
            assert sha(ROOT/rel)==h,rel
            if rel in files:assert files[rel]==h,rel
            files[rel]=h
        for q in p.parent.iterdir():
            if q.suffix in ('.json','.brep'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    for folder in ('servo-fuse-deck-native-r1','servo-fuse-bank-clip-access-r1'):
        for p in (ROOT/'hardware/cad/studies'/folder).iterdir():
            if p.suffix in ('.FCStd','.brep','.stl'):files[p.relative_to(ROOT).as_posix()]=sha(p)
    service=reports['servo-fuse-bank-service-r3']
    assert not service['hits'] and not service['errors']
    assert reports['servo-fuse-deck-native-r1']['full_through_portals']==12
    assert reports['servo-fuse-bank-electrical-r1']['input_ends']==12 and reports['servo-fuse-bank-electrical-r1']['output_ends']==12
    assert reports['servo-fuse-bank-service-r1']['hits'] and not reports['servo-fuse-bank-service-r1']['errors']
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    now=datetime.now(timezone.utc);manifest=dict(parent)
    manifest.update(recorded_utc=now.isoformat(),started_utc='2026-10-02T19:51:41Z',
        elapsed_turn_seconds=(now-datetime(2026,10,2,19,51,41,tzinfo=timezone.utc)).total_seconds(),
        completed='Native retained Deck with12 full portal sweeps/4 mounting bores and full bearing, exported closed STL, parameter/reopen proof.24 explicit end recipes and2180mm conductor budget. Two native bank parts gain24 vertical clip-tool slots. Tool access and inward5.5mm input release leave no shared contacts;100mm continuous relative bank withdrawal over24 rigid ends is clear. Broad-access/outward-parking failures retained. Cover3/head datums unchanged.',
        remaining=['P-WAGO approach/lever access and four parent factory feeds/restraints.',
                   'Nominal latch actuation remains a coupon condition; rigid service-r3 replaces the failed outward-parking proposal, not the P-WAGO gate.',
                   'Full output flexible lead service allowance remains W5; rigid TE parking is not a flexible lead test.',
                   'Select one coherent export and update stock3m LAPP/E3 assumptions and mounting order, then local completion commit.'],
        files=[dict(path=p,sha256=h) for p,h in sorted(files.items())])
    manifest['gates']=dict(parent['gates'])
    manifest['gates']['geometry']=dict(status='pass',reason='Limited native parts only: Deck12 full portals/bearing and bank24 tool-slot cuts, strict BOP/closed STL/parameter restore/relocated reopen. Shared service conflicts are separate, not a whole-cat clearance claim.',
        evidence=['hardware/electronics/full-cat/servo-fuse-deck-native-r1/checks.json','hardware/electronics/full-cat/servo-fuse-bank-clip-access-r1/checks.json'])
    manifest['gates']['service']=dict(status='open',reason='service-r1 broad access failed. Changed vertical tools and rigid end parking are bounded evidence only; P-WAGO approach and full flexible output allowance still open.')
    manifest['service_summary']=dict(changed_hits=len(service['hits']),changed_errors=len(service['errors']),
        nominal_clip_tools=service['clip_tools'],rigid_parked_ends=service['parked_ends'],physical_latch_actuation_verified=False)
    manifest['files'].append(dict(path=Path(__file__).relative_to(ROOT).as_posix(),sha256=sha(Path(__file__))))
    save(OUT/'manifest.json',manifest)
    print(json.dumps(dict(files=len(manifest['files']),selected=False,phase1_percent=75,changed_service_hits=len(service['hits']),elapsed_turn_seconds=manifest['elapsed_turn_seconds'])),flush=True)
if __name__=='__main__':main()
