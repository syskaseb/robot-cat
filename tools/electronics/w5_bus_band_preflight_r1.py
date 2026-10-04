"""Short changed-interface check of proposed bands before expensive Deck export.

Execute the SAME band definition as the native builder, not a second geometry
variant. Original Deck is excluded here because new slots belong to the pending
native proof. Other parts/wires remain installed, including P0Support3.
"""
from datetime import datetime,timezone
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha

def main():
    import FreeCAD as A
    import Part
    from w5_selected_owners_r52 import cached
    start=datetime.now(timezone.utc)
    out=ROOT/'hardware/electronics/full-cat/w5-bus-band-preflight-r1'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'checks.json').exists()
    source=ROOT/'tools/electronics/w5_bus_native_grips_r1.py'
    original=source.read_text(encoding='utf-8')
    fragment=original[original.index('    def box(b):'):original.index('    addition=shape.cut(link.Shape)')]
    fragment='\n'.join(line[4:] if line.startswith('    ') else line for line in fragment.splitlines())
    intent=json.loads((ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json').read_text(encoding='utf-8'))
    sx=sum(intent['source_lead_datums'][w][0] for w in ('W002','W003'))/2
    ctx=dict(A=A,Part=Part,sx=sx)
    exec(compile(fragment,str(source),'exec'),ctx)
    owners,cache=cached();owners.pop('CandidateDeck');owners.pop('W061_tie/G2_end/1')
    # Other portions of W061's SAME physical strap touch its replacement band.
    # Those junctions are not foreign cable/component clearances.
    hits=[];errors=[];pairs=0
    for name,s in ctx['newties'].items():
        for key,owner in owners.items():
            if name=='W061SlopedBand' and key.startswith('W061_tie/G2_end/'):continue
            if not s.BoundBox.intersect(owner.BoundBox):continue
            for j,q in enumerate(owner.Solids):
                if not s.BoundBox.intersect(q.BoundBox):continue
                pairs+=1
                try:
                    v=s.common(q).Volume
                    if v>1e-5:hits.append(dict(band=name,owner=key,solid=j,mm3=v))
                except Exception as e:errors.append(dict(band=name,owner=key,error=str(e)))
    end=datetime.now(timezone.utc)
    save(out/'checks.json',dict(status='BANDS_REJECTED' if hits or errors else 'BANDS_NONDECK_CLEAR_NATIVE_PENDING',
        hits=hits,errors=errors,pairs=pairs,Deck_checked=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [source,Path(__file__),ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json',ROOT/'hardware/electronics/full-cat/w5-installed-r52/owners.json',ROOT/'hardware/electronics/full-cat/w5-installed-r52/installed.brep']},
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,pairs=pairs)),flush=True)

if __name__=='__main__':main()
