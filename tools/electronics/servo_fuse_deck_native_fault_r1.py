"""Localize current Deck BOP failure in cached native stages, not whole cat."""
from pathlib import Path
from datetime import datetime, timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    import FreeCAD as A
    import Part
    start=datetime.now(timezone.utc);pins={};rows=[]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-deck-native-fault-r1'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'checks.json').exists()
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def record(label,s):
        print('NATIVE_FAULT_STAGE '+label,flush=True)
        try: errors=s.check(True)
        except ValueError as exc:errors=[str(exc)]
        b=s.BoundBox
        rows.append(dict(stage=label,isValid=s.isValid(),solids=len(s.Solids),edges=len(s.Edges),faces=len(s.Faces),
            volume_mm3=s.Volume,bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],strict_BOP=errors))
        save(out/'progress.json',dict(selected=False,physical_pass=False,stages=rows,complete=False,source_sha256=pins))
        print('NATIVE_FAULT_RESULT '+label+' '+('FAIL' if errors else 'OK'),flush=True)
    for rel,label in [('hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2/Deck_WORLD.brep','retained_R2_export'),
                      ('hardware/cad/studies/servo-fuse-parent-complete-layout-r7/Deck_WORLD.brep','R7_export')]:
        p=ROOT/rel;pin(p);record(label,Part.read(str(p)))
    for rel,names in [('hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2/DeckParentFeedGrips.FCStd',['ParentFeedGripFinished']),
                      ('hardware/cad/studies/servo-fuse-parent-complete-layout-r7/DeckMainHolders.FCStd',
                       ['ParentFeedGripFinished','AllFourMainSeats','AllMainTiePassTools','MainTiePassFinished'])]:
        p=ROOT/rel;pin(p);d=A.openDocument(str(p))
        try:
            # Inspect saved stage shapes before a recompute can change evidence.
            for name in names:
                obj=d.getObject(name);assert obj is not None,name
                record(Path(rel).stem+'/'+name,obj.Shape.copy())
        finally:A.closeDocument(d.Name)
    end=datetime.now(timezone.utc)
    save(out/'checks.json',dict(selected=False,physical_pass=False,stages=rows,complete=True,
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds(),
        scope='Seven cached/exported stages of the one failing Deck interface; no source edits, no full robot audit.'))
    print(json.dumps(dict(stages=len(rows),failed=sum(bool(r['strict_BOP']) for r in rows))),flush=True)


if __name__=='__main__':main()
