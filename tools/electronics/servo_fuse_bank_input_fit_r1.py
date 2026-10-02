"""Correct only RL1 tie-head reserve; preserve twelve native input grips.

R3 failed on its head-to-bridge intersection. Retain that witness and inherit
the other changed-interface checks, then test the shifted head explicitly.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-input-fit-r1'
def main():
    import FreeCAD as A
    import Part
    import servo_fuse_side_bank_r10 as layout
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    parent=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-restraints-r3'
    p=parent/'checks.json';meta=json.loads(p.read_text(encoding='utf-8'))
    assert len(meta['hits'])==1 and meta['hits'][0]['part']=='W046_INPUT_TIE_HEAD_RESERVE'
    assert meta['hits'][0]['owner']=='LeftInputSeatFinished' and not meta['errors']
    assert meta['strict_BOP_errors']==0 and meta['closed_STLs'] and meta['relocated_reopen']
    assert sha(ROOT/'tools/electronics/servo_fuse_bank_restraints_r3.py')==meta['script_sha256']
    hashes={p.relative_to(ROOT).as_posix():sha(p)}
    owners,h,_=layout.current_owners();hashes.update(h)
    for n in list(owners):
        if '/servo-fuse-bank-restraints-r2/' in n:del owners[n]
    def load(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    for folder,pattern in [('hardware/cad/studies/servo-fuse-bank-restraints-r3','*_WORLD.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-side-bank-r11','*_DESIGN.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-bank-restraints-r3','*_INPUT_TIE_*.brep')]:
        for p in (ROOT/folder).glob(pattern):
            if p.stem=='W046_INPUT_TIE_HEAD_RESERVE':continue
            owners[folder+'/'+p.stem]=load(p)
    p=parent/'W046_INPUT_TIE_HEAD_RESERVE.brep';head=load(p);head.translate(A.Vector(0,0,.6))
    head.exportBrep(str(OUT/p.name));hits=[];errors=[];pairs=0
    for n,s in owners.items():
        if not head.BoundBox.intersect(s.BoundBox):continue
        pairs+=1
        try:
            v=head.common(s).Volume
            if v>1e-5:hits.append(dict(part='W046_INPUT_TIE_HEAD_RESERVE',owner=n,hit_mm3=v))
        except Exception as e:errors.append(dict(owner=n,error=str(e)))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='ALL12_INPUT_GRIPS_CLEAR' if not hits and not errors else 'REJECTED',
        selected=False,W5_complete=False,physical_pass=False,hits=hits,errors=errors,pairs=pairs,inherited_pairs=meta['pairs'],
        inherited_native=meta['native'],previous_contact=meta['hits'][0],changed='W046 head only +0.6mm Z; no STL or native change.',
        delivered_tie_head_verified=False,source_sha256=hashes,script_sha256=sha(Path(__file__)),
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,pairs=pairs)),flush=True)
if __name__=='__main__':main()
