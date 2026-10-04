"""Recover existing R4 BReps after receipt NameError, without rebuilding paths.

The old worker's unsaved contacts are lost, not fabricated. Verify the saved
compounds and checkpoint each completed route so interruption is recoverable.
Compound volumes are not comparable to per-edge contact counts in R3.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,math,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r4'


def main():
    import FreeCAD as A
    import Part
    from w5_r53_owners import installed
    from w5_leg_fanout_layout import GROUND_DX,GROUND_DY
    start=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    intent_file=OUT/'intent.json';intent=json.loads(intent_file.read_text(encoding='utf-8'))
    planned=intent['routes'];assert len(planned)==36
    geometries=Part.read(str(OUT/'FANOUTS_WORLD.brep')).childShapes()
    paths=Part.read(str(OUT/'CENTERLINES_WORLD.brep')).childShapes()
    assert len(geometries)==len(paths)==36
    assert all(s.isValid() for s in geometries)
    owners,pins,omitted=installed(A,Part)
    mounts={}
    for leg in ('FL','FR','RL','RR'):
        key=leg+'_G_design';shape=owners[key].copy();b=shape.BoundBox
        side=1 if leg.endswith('L') else -1
        shape.rotate(A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2),A.Vector(0,0,1),180)
        shape.translate(A.Vector(GROUND_DX,side*GROUND_DY,0));owners[key]=shape;mounts[key]=shape
    for prefix,dx in {'DATA_tie/W007/1/':-2.5,'DATA_tie/W012/0/':1.5}.items():
        keys=[k for k in owners if k.startswith(prefix)];assert len(keys)==5
        for key in keys:
            shape=owners[key].copy();shape.translate(A.Vector(dx,0,0));owners[key]=shape;mounts[key]=shape
    mount_file=OUT/'RELOCATED_OWNERS_WORLD.brep'
    Part.makeCompound(list(mounts.values())).exportBrep(str(mount_file))
    hits=[];errors=[];pairs=0;built=[]
    def check(w,s,k,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            common=s.common(t)
            if common.Volume>1e-5:
                b=common.BoundBox
                hits.append(dict(wire=w,owner=k,mm3=common.Volume,bounds_mm=[getattr(b,n) for n in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        except Exception as exc:errors.append(dict(wire=w,owner=k,error=str(exc)))
    r3folder=OUT.with_name('w5-leg-fanouts-r3')
    r3=json.loads((r3folder/'checks.json').read_text(encoding='utf-8'))
    assert len(r3['routes'])==36 and not r3['errors']
    assert all(sha(ROOT/k)==v for k,v in {**r3['source_sha256'],**r3['files']}.items())
    prior={r['wire']:r for r in r3['routes']}
    vs={r['wire']:s for r,s in zip(planned,geometries) if r['role']=='V'}
    for key,s in mounts.items():
        if key.startswith('DATA_tie/'):continue
        for k,t in owners.items():
            if k!=key:check('RELOCATED/'+key,s,k,t)
        for w,t in vs.items():check('RELOCATED/'+key,s,w,t)
    placement_hits=hits.copy()
    for row,s,path in zip(planned,geometries,paths):
        if row['role']=='V':
            result=prior[row['wire']]
            for k,t in mounts.items():check(row['wire'],s,k,t)
        else:
            for k,t in owners.items():check(row['wire'],s,k,t)
            length=path.Length+row['moving_candidate_length_mm']+row['bank_local_path_mm']
            strip=row['termination']['strip_mm']
            blank=math.ceil((length+strip+30)/10)*10
            result=dict(wire=row['wire'],loom=row['loom'],role=row['role'],body_fanout_mm=path.Length,
                continuous_external_design_mm=length,provisional_far_end_blank_mm=blank,
                fits_nominal_900_candidate=blank<=900,factory_plug_consumed_length_unknown=True)
        built.append(result)
        save(OUT/'recovery-progress.json',dict(completed_routes=len(built),pairs=pairs,hits=hits,errors=errors,started_utc=start.isoformat()))
        print('RECOVERED',row['wire'],len(hits),flush=True)
    for i,s in enumerate(geometries):
        for j,t in enumerate(geometries[i+1:],i+1):
            if planned[i]['role']=='V' and planned[j]['role']=='V':continue
            check(planned[i]['wire'],s,planned[j]['wire'],t)
    corridors=ROOT/'hardware/electronics/full-cat/w5-leg-corridors-r3/intent.json'
    rows=json.loads(corridors.read_text(encoding='utf-8'))['routes']
    bundles=Part.read(str(OUT/'BUNDLES_WORLD.brep')).childShapes();assert len(bundles)==12
    for row,s in zip(rows,bundles):
        for info,t in zip(built,geometries):
            if info['role']!='V' and info['loom']!=row['loom']:check(row['loom']+'_BUNDLE',s,info['wire'],t)
    finish=datetime.now(timezone.utc)
    pins += [Path(__file__),ROOT/'tools/electronics/w5_leg_fanout_layout.py',ROOT/'tools/electronics/w5_leg_fanouts_r4.py',corridors,r3folder/'checks.json']
    files=[OUT/n for n in ('FANOUTS_WORLD.brep','CENTERLINES_WORLD.brep','BUNDLES_WORLD.brep','intent.json','RELOCATED_OWNERS_WORLD.brep')]
    save(OUT/'checks.json',dict(status='COUPLED_LEG_FANOUT_REJECTED' if hits or errors else 'STATIC_FANOUT_ONLY_GRIPS_AND_MOTION_OPEN',
        routes=built,hits=hits,errors=errors,pairs=pairs,changed_mounts=list(mounts),relocated_block_hits=placement_hits,
        native_supports_ready=False,omitted_retired_carrier_aliases=omitted,
        recovery_reason='Original worker exited1 at Path(M.__file__) after exporting; unsaved hits lost. Saved compounds checked without rebuilding routes.',
        comparison_method='one compound per route, not per-edge hit count',
        candidate_900_complete=all(r['fits_nominal_900_candidate'] for r in built),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins},files={p.relative_to(ROOT).as_posix():sha(p) for p in files},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        selected=False,grips_complete=False,motion_qualified=False,W5_complete=False,physical_pass=False))
    print('RECOVERY_RESULT',len(built),len(hits),len(errors),flush=True)


if __name__=='__main__':main()
