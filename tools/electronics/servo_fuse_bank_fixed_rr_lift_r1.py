"""Whole CURRENT bank+Cover withdrawal with the RR station FIXED on Deck.

No repeated search for holder positions, cage parking or independent Cover
lift. Unplug head and remove all12 ATO/mini holders, release24TE ends and
bank strain ties. Keep RR cage/3ties/both wires fixed, as designed. Sample
the real complete owners first; refuse to qualify any colliding sequence.
Only if those are clear, test changed100mm continuous end/input envelopes.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r1'

def main():
    import FreeCAD as A
    import Part
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Preserve result'
    loader=ROOT/'tools/electronics/servo_fuse_rr_clip_approach_r1.py'
    code=loader.read_text(encoding='utf-8');code=code[:code.index('    # These boxes are exactly')]
    code=code.replace('servo-fuse-rr-clip-approach-r1','servo-fuse-bank-fixed-rr-lift-r1')+'    return owners,pins,final\n'
    ns=dict(__file__=str(loader),__name__='owners_only');exec(compile(code,str(loader),'exec'),ns)
    owners,pins,native=ns['main']();pins[loader.relative_to(ROOT).as_posix()]=sha(loader)
    def load(rel):p=ROOT/rel;pins[rel]=sha(p);return Part.read(str(p))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    proofpath=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-fixed-station-native-r1/checks.json'
    pins[proofpath.relative_to(ROOT).as_posix()]=sha(proofpath)
    proof=json.loads(proofpath.read_text(encoding='utf-8'));assert proof['exports'][0]['relocated_reopen']
    owners['CandidateDeck']=load('hardware/cad/studies/servo-fuse-rr-fixed-station-native-r1/Deck_WORLD.brep')
    right='Bank/RightClipAccessFinished_WORLD';left='Bank/LeftClipAccessFinished_WORLD'
    module={'BankRight':load('hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1/BankRight_WORLD.brep'),
            'BankLeft':owners.pop(left),'Cover':owners.pop('ModifiableCover')}
    owners.pop(right)
    omitted=[];parked=[];released_inputs=[]
    for key in list(owners):
        # Only explicit released physical parts, not arbitrary collisions.
        if key.endswith('_ATO_DESIGN') or ('F_' in key and key.endswith('_DESIGN') and key.rsplit('/',1)[-1].count('_')==2):
            omitted.append(key);del owners[key]
        elif key.rsplit('/',1)[-1].startswith('F_') and key.endswith(('_IN_DESIGN','_OUT_DESIGN')):
            ident=key.rsplit('/',1)[-1]
            p='hardware/electronics/full-cat/servo-fuse-bank-service-r3/'+ident+'_PARKED.brep'
            owners[key]=load(p);parked.append(key)
        elif any(s in key for s in ('/servo-fuse-bank-restraints-', '/servo-fuse-bank-restraints-fit-')):
            omitted.append(key);del owners[key]
    # Replace connected input route0 by accepted released input route1.
    for key in list(owners):
        if 'release_0.0_W' in key:
            rel=next((r for r in pins if r.endswith(key.rsplit('/',1)[-1]+'.brep')),None)
            assert rel,key
            owners[key]=load(rel.replace('release_0.0_','release_1.0_'));released_inputs.append(key)
    assert len(parked)==24,parked
    assert len(released_inputs)==12,released_inputs
    save(OUT/'owner-census.json',dict(fixed=list(owners),removed=omitted,parked=parked,released_inputs=released_inputs))
    print('FIXED_RR_OWNER_CENSUS',len(owners),len(omitted),len(parked),len(released_inputs),flush=True)
    hits=[];errors=[];pairs=0
    def check(phase,name,s,key,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:
                hits.append(dict(phase=phase,part=name,owner=key,mm3=c.Volume,bounds_mm=bounds(c)))
                c.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
        except Exception as e:errors.append(dict(phase=phase,part=name,owner=key,error=str(e)))
    lifts=[0,2,5,10,30,60,100]
    for lift in lifts:
        for name,s in module.items():
            q=s.copy();q.translate(A.Vector(0,0,lift))
            for key,t in owners.items():check('sampled_lift_'+str(lift),name,q,key,t)
        print('FIXED_RR_BANK_LIFT_SAMPLE',lift,len(hits),len(errors),flush=True)
    save(OUT/'checks.json',dict(status='FIXED_RR_COMMON_MODULE_LIFT_CONFLICTS' if hits or errors else 'FIXED_RR_COMMON_MODULE_SAMPLES_CLEAR_CONTINUOUS_PENDING',
        selected=False,physical_pass=False,W5_complete=False,sampled_lifts_mm=lifts,hits=hits,errors=errors,pairs=pairs,
        module=list(module),omitted_after_explicit_release=omitted,RR_output_owner='FIXED_DECK',RR_cages_opened=False,
        bank_mounts_preserved=4,continuous_withdrawal_qualified=False,
        sequence='Disconnect battery/head. Remove12ATOs/holders, release24TE ends/ties; input inward5.5mm, output axes unchanged. Unbolt4bank+4Cover mounts. Lift bank+Cover together while ALL RR output wires/cage/3ties stay fixed.',
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
    print('FIXED_RR_COMMON_LIFT_RESULT',json.dumps(dict(pairs=pairs,hits=len(hits),errors=len(errors))),flush=True)
if __name__=='__main__':main()
