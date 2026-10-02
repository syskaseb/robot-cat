"""Necessary cover clearance for lifting unclipped, fuse-free holders.

Do not repeat rejected independent cover lift. The insulation backers sit
below TE input ends, so do not assume the female terminal can withdraw
downwards past a backer. Test holder lift relative to stationary cover,
after ATO removal. Nominal MTA snap/flange remains a delivery coupon.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-holder-release-r1'
def main():
    import FreeCAD as A
    import Part
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists();hashes={}
    def load(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    cover=load(ROOT/'hardware/cad/studies/servo-fuse-cover-native-r3/Cover_WORLD.brep')
    paths=list((ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11').glob('F_*_DESIGN.brep'))
    paths=[p for p in paths if p.stem.count('_')==2];assert len(paths)==12
    rows=[];hits=[];errors=[]
    # 10mm exceeds the existing8.30mm planning engagement. It is not a
    # measurement of delivered blade engagement or latch actuation access.
    for p in paths:
        s=load(p)
        for lift in (0,2,5,8.3,10):
            q=s.copy();q.translate(A.Vector(0,0,lift))
            if not q.BoundBox.intersect(cover.BoundBox):v=0
            else:
                try:v=q.common(cover).Volume
                except Exception as e:errors.append(dict(holder=p.stem,lift_mm=lift,error=str(e)));continue
            row=dict(holder=p.stem,lift_mm=lift,cover_hit_mm3=v);rows.append(row)
            if v>1e-5:hits.append(row)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='HOLDER_LIFT_BLOCKED' if hits or errors else 'NECESSARY_HOLDER_COVER_LIFT_CLEAR_NOT_COMPLETE_SERVICE',
        selected=False,W5_complete=False,physical_pass=False,hits=hits,errors=errors,rows=rows,
        holders=12,sampled_lifts_mm=[0,2,5,8.3,10],continuous_release_qualified=False,
        release_direction='Unclip and raise MTA holder with ATO removed; female TE ends stay stationary until blades released.',
        remaining='Actual clip/tool access, complete end parking and disconnected bank+cover module withdrawal. Do not label service complete from this check.',
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,holders=12)),flush=True)
if __name__=='__main__':main()
