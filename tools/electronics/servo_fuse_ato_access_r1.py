"""Continuous rectangular ATO withdrawal reserve, required before holder release."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-ato-access-r1'
def main():
    import FreeCAD as A
    import Part
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists();hashes={}
    def load(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    cover=load(ROOT/'hardware/cad/studies/servo-fuse-cover-native-r3/Cover_WORLD.brep')
    rows=[];hits=[];errors=[]
    paths=list((ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11').glob('F_*_ATO_DESIGN.brep'));assert len(paths)==12
    for p in paths:
        s=load(p);b=s.BoundBox
        assert abs(s.Volume-b.XLength*b.YLength*b.ZLength)<1e-5
        corridor=Part.makeBox(b.XLength,b.YLength,b.ZLength+20,A.Vector(b.XMin,b.YMin,b.ZMin))
        try:
            c=corridor.common(cover);row=dict(fuse=p.stem,continuous_reserved_lift_mm=20,cover_hit_mm3=c.Volume)
            rows.append(row)
            if c.Volume>1e-5:
                row['bounds_mm']=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')];hits.append(row)
        except Exception as e:errors.append(dict(fuse=p.stem,error=str(e)))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='ATO_WITHDRAWAL_COVER_BLOCKED' if hits or errors else 'ATO20MM_TRANSLATION_CLEAR_TOOL_ACCESS_OPEN',
        selected=False,W5_complete=False,physical_pass=False,hits=hits,errors=errors,rows=rows,
        scope='Exact rectangular sweep of the nominal ATO reservation. No claim about delivered latch, hand/tool reach or complete service.',
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,fuses=12)),flush=True)
if __name__=='__main__':main()
