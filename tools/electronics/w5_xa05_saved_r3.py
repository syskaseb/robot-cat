"""Receive the already exported R3 construction; do not rebuild the Deck.

Original worker saved every shape but stopped in receipt binding (missing
BASE alias). The source fix changes no geometry; evaluate the saved groups
once and retain the actual negative result, not a fabricated old receipt.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-xa05-joint-repair-r3'


def main():
    import FreeCAD as A
    import Part
    from w5_r53_owners import installed
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    files=list(OUT.glob('*.brep'));assert len(files)==6
    shape={p.stem:Part.read(str(p)) for p in files}
    assert all(s.isValid() for s in shape.values())
    deck=shape['DECK_CANDIDATE_WORLD'];assert len(deck.Solids)==1
    supports=shape['SUPPORTS_WORLD'].childShapes();ties=shape['TIES_WORLD'].childShapes()
    assert len(supports)==len(ties)==2
    owners,pins,omitted=installed(A,Part)
    owners.pop('CandidateDeck');owners['NewDeckXA05']=deck
    owners.pop('hardware/electronics/full-cat/xa05-main-aux-return-r2/XA05_DESIGN.brep')
    hits=[];errors=[];pairs=0
    changed={'XA05':shape['XA05_WORLD'],**{n+'_seat':s for n,s in zip(('North','South'),supports)},
        **{n+'_tie':s for n,s in zip(('North','South'),ties)}}
    for name,s in changed.items():
        for key,t in {**owners,**{n+'_seat':s for n,s in zip(('North','South'),supports)}}.items():
            if name==key or (name.endswith('_seat') and key=='NewDeckXA05'):continue
            if not s.BoundBox.intersect(t.BoundBox):continue
            pairs+=1
            try:
                common=s.common(t)
                if common.Volume>1e-5:
                    b=common.BoundBox
                    hits.append(dict(part=name,owner=key,mm3=common.Volume,
                        bounds_mm=[getattr(b,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
            except Exception as ex:errors.append(dict(part=name,owner=key,error=str(ex)))
        print('XA05_SAVED_GROUP',name,len(hits),flush=True)
    finish=datetime.now(timezone.utc)
    pins += [Path(__file__),ROOT/'tools/electronics/w5_xa05_joint_repair_r3.py',ROOT/'tools/electronics/w5_xa05_joint_repair_r2.py',
        ROOT/'tools/electronics/w5_xa05_joint_repair_r1.py',ROOT/'tools/electronics/w5_s1_source_layout_r2.py',
        ROOT/'tools/electronics/w5_s1_source_layout_r1.py']
    specs=[dict(name=n,y_mm=y,seat_bounds_mm=[89.7,y-3.3,108.8,96.3,y+3.3,114.2],groove_centre=[93,y,113.5],
        groove_R_mm=1.5,tie_SKU='111-02370 T18I-PA66-BK',tie_axis='Y',tie_head_nominal_mm=[5,5,4],actual_head_measured=False)
        for n,y in [('North',20),('South',-20)]]
    save(OUT/'checks.json',dict(status='XA05_ROUTE_REJECTED' if hits or errors else 'XA05_ROUTE_CLEAR_RESTRAINTS_OPEN',
        hits=hits,errors=errors,pairs=pairs,comparison='Saved whole groups, not edge-hit count of the interrupted worker.',
        omitted_retired_carrier_aliases=omitted,source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in [OUT/'intent.json',*files]},
        support_specs=specs,new_ties=2,new_fasteners=0,native_restraints_ready=False,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        original_worker_exit_code=1,original_worker_error='NameError BASE during receipt, after all exports.',original_worker_wall_seconds=None,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('XA05_SAVED_RESULT',pairs,len(hits),len(errors),flush=True)


if __name__=='__main__':main()
