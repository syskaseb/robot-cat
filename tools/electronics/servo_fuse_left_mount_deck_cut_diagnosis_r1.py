"""Receive failed native Deck cut; identify exact BRep versus Link failure.
Read-only parent geometry, two deliberate drill extents, preserve diagnostics.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
def main():
    import FreeCAD as A,Part
    t=datetime.now(timezone.utc);out=ROOT/'hardware/electronics/full-cat/servo-fuse-left-mount-deck-cut-diagnosis-r1';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'checks.json').exists()
    rel='hardware/cad/studies/servo-fuse-guard-fixed-deck-native-r1/Deck_WORLD.brep';s=Part.read(str(ROOT/rel));rows=[]
    for z,h in [(104.9,8.3),(104.9,4.2)]:
        tool=Part.makeCylinder(1.2,h,A.Vector(-51,92.5,z));row=dict(z=z,height=h,source_valid=s.isValid(),source_solids=len(s.Solids))
        try:
            q=s.cut(tool);row.update(null=q.isNull(),valid=q.isValid(),solids=len(q.Solids),volume_mm3=q.Volume,BOP=[str(v) for v in q.check(True) or []])
            q.exportBrep(str(out/('Deck_drill_'+str(h)+'.brep')))
        except Exception as e:row['error']=str(e)
        rows.append(row);print('LEFT_DECK_CUT_DIAGNOSIS',row,flush=True)
    save(out/'checks.json',dict(selected=False,physical_pass=False,rows=rows,source_sha256={rel:sha(ROOT/rel)},script_sha256=sha(Path(__file__)),started_utc=t.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat()))
if __name__=='__main__':main()
