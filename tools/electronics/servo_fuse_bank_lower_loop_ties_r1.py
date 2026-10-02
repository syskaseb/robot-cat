"""Check only the new R4 input loops against native-R2's twenty tie reserves.

Other body/Deck pairs are preserved in R4, not re-run here. The changed
lower spans stay below every parent tie, but the installed upper fans also
need checking against the moved FR head. This is five sampled poses only.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-lower-loop-ties-r1'


def main():
    import FreeCAD
    import Part
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists();hashes={}
    def load(p):
        hashes[p.relative_to(ROOT).as_posix()]=sha(p)
        return Part.read(str(p))
    loops=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r4'
    ties=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-feed-grips-native-r2'
    for p in (loops/'checks.json',ties/'checks.json'):
        meta=json.loads(p.read_text(encoding='utf-8'))
        assert not meta['hits'] and not meta['errors'];hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    bands={p.stem:load(p) for p in ties.glob('*_DESIGN.brep')};assert len(bands)==20
    hits=[];errors=[];pairs=0;tested=[]
    for p in sorted(loops.glob('release_*_W*_DESIGN.brep')):
        s=load(p);tested.append(p.stem)
        for n,t in bands.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            pairs+=1
            try:
                c=s.common(t)
                if c.Volume>1e-5:
                    hits.append(dict(wire=p.stem,tie=n,hit_mm3=c.Volume))
                    c.exportBrep(str(OUT/('HIT_'+str(len(hits))+'.brep')))
            except Exception as exc:errors.append(dict(wire=p.stem,tie=n,error=str(exc)))
    assert len(tested)==60
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='SAMPLED_LOWER_LOOPS_PARENT_TIES_CLEAR' if not hits and not errors else 'LOOP_TIE_CONFLICTS',
        selected=False,physical_pass=False,W5_complete=False,sampled_wire_shapes=60,parent_tie_reserves=20,
        hits=hits,errors=errors,pairs=pairs,continuous_deformation_qualified=False,
        inherited_body_Deck_checks='servo-fuse-bank-connected-release-r4/checks.json',
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=len(hits),errors=len(errors),pairs=pairs)),flush=True)


if __name__=='__main__':main()
