"""Fast exact proof of the complete corrected shared band arrangement."""
from datetime import datetime,timezone
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
import w5_bus_restraints_r3 as layout

def main():
    import FreeCAD as A
    import Part
    from w5_selected_owners_r52 import cached
    start=datetime.now(timezone.utc)
    out=ROOT/'hardware/electronics/full-cat/w5-bus-band-preflight-r3'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'checks.json').exists()
    file=ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
    intent=json.loads(file.read_text(encoding='utf-8'))
    sx=sum(intent['source_lead_datums'][w][0] for w in ('W002','W003'))/2
    new=layout.restraints(A,Part,sx);owners,cache=cached()
    for n in layout.removed_owners():owners.pop(n)
    for w in ('W002','W003'):
        owners['BUS/'+w]=Part.read(str(file.parent/(w+'_DESIGN.brep')))
    hits=[];errors=[];pairs=0
    for name,s in new.items():
        for key,owner in owners.items():
            # Same retained W061 head meets its bottom band intentionally.
            if name.startswith('G2shared/') and key=='W061_tie/G2_end/4':continue
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
        new_ties=3,retained_shared_W061_tie=1,original_left_slot=[105.5,11],new_right_slot=[120.2,11],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [Path(layout.__file__),Path(__file__),file,ROOT/'hardware/electronics/full-cat/w5-installed-r52/owners.json',ROOT/'hardware/electronics/full-cat/w5-installed-r52/installed.brep',file.parent/'W002_DESIGN.brep',file.parent/'W003_DESIGN.brep']},
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,pairs=pairs)),flush=True)

if __name__=='__main__':main()
