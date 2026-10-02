"""Conservative continuous 100mm bank lift over the released R4 inputs.

Inputs remain stationary at the final sampled release pose. Cover and two
bare bank parts move upwards. Per-line/arc-segment boxes enclose each tube
and its relative downwards translation; circular sagitta is added, not
ignored. No continuous flexible-wire deformation or parent-carrier proof.
"""
from pathlib import Path
from datetime import datetime,timezone
import math,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-lower-loop-lift-r1'


def main():
    import FreeCAD as A
    import Part
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists();hashes={}
    def load(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    route_dir=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r4'
    for p in (route_dir/'checks.json',ROOT/'hardware/electronics/full-cat/servo-fuse-bank-service-r3/checks.json'):
        m=json.loads(p.read_text(encoding='utf-8'));assert not m['hits'] and not m['errors']
        hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    module={p.stem:load(p) for p in (ROOT/'hardware/cad/studies/servo-fuse-bank-clip-access-r1').glob('*_WORLD.brep')}
    module['Cover']=load(ROOT/'hardware/cad/studies/servo-fuse-cover-native-r3/Cover_WORLD.brep');assert len(module)==3
    hits=[];errors=[];pairs=0;segments=0;rows=[]
    for p in sorted(route_dir.glob('release_1.0_W*_CENTERLINE.brep')):
        path=load(p);print('LIFT '+p.stem,flush=True);count=0
        for index,edge in enumerate(path.Edges):
            curved=hasattr(edge.Curve,'Radius');N=8 if curved else 1
            delta=(edge.LastParameter-edge.FirstParameter)/N
            sag=edge.Curve.Radius*(1-math.cos(abs(delta)/2)) if curved else 0
            # OD3.1 provisional R4 tube, plus .05mm numerical reserve.
            pad=1.55+sag+.05
            for k in range(N):
                a=edge.valueAt(edge.FirstParameter+k*delta);b=edge.valueAt(edge.FirstParameter+(k+1)*delta)
                q=Part.makeBox(abs(b.x-a.x)+2*pad,abs(b.y-a.y)+2*pad,abs(b.z-a.z)+2*pad+100,
                    A.Vector(min(a.x,b.x)-pad,min(a.y,b.y)-pad,min(a.z,b.z)-pad-100))
                count+=1;segments+=1
                for n,t in module.items():
                    if not q.BoundBox.intersect(t.BoundBox):continue
                    pairs+=1
                    try:
                        c=q.common(t)
                        if c.Volume>1e-5:
                            hits.append(dict(wire=p.stem,edge=index,segment=k,module=n,hit_mm3=c.Volume,
                                enclosure_sagitta_mm=sag,bounds_mm=[getattr(c.BoundBox,v) for v in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                            c.exportBrep(str(OUT/('HIT_'+str(len(hits))+'.brep')))
                    except Exception as exc:errors.append(dict(wire=p.stem,module=n,error=str(exc)))
        rows.append(dict(wire=p.stem,enclosing_segments=count,path_mm=path.Length))
    assert len(rows)==12
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='CONSERVATIVE_CONTINUOUS_BANK_LIFT_OVER_R4_INPUTS_CLEAR' if not hits and not errors else 'CONSERVATIVE_LIFT_ENCLOSURE_CONTACTS',
        selected=False,physical_pass=False,W5_complete=False,relative_module_lift_mm=100,
        stationary_input_configuration='R4 release fraction1; upper WAGO ends remain fixed, inputs released5.5mm inward.',
        conservative_enclosure='Each exact circular edge split8ways; endpoint AABB enlarged by radius1.55+sagitta+.05 and swept continuously100mm downwards relative to module.',
        rows=rows,segments=segments,pairs=pairs,hits=hits,errors=errors,
        rigid_TE_ends_inherited='servo-fuse-bank-service-r3/checks.json',
        open=['Flexible-wire transition remains five R4 samples, not continuous deformation.',
              'Output full leg routes and parent-carrier/module shared lift are not checked by this limited result.',
              'ATO/holders removed, ties cut and actual latch coupon remains phase2.'],
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=len(hits),errors=len(errors),pairs=pairs,segments=segments)),flush=True)


if __name__=='__main__':main()
