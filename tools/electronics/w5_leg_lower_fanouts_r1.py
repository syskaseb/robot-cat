"""A common under-Deck fanout, preserving ground blocks and all 12 V paths.

Rejected R5 raised D/G into the bank, head feeds and DATA grips. Route all
24 continuous D/G cores below those occupied height bands, then rise outside
the Deck to unchanged loom breakouts. Any PETG contact remains a failure until
its actual native owner is changed; never waive a collision by material.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math
from servo_fuse_inputs_r1 import save, sha
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/w5-leg-lower-fanouts-r1'


def plan(rows):
    result=[]
    for old in rows:
        row=dict(old)
        if row['role']=='V': result.append(row); continue
        leg=row['loom'][:2]; side=1 if leg.endswith('L') else -1
        peers=sorted((q for q in rows if q['loom'][:2]==leg and q['role']==row['role']),key=lambda q:q['waypoints_mm'][0][0])
        index=next(i for i,q in enumerate(peers) if q['wire']==row['wire'])
        rank=index if leg.startswith('F') else 2-index
        end=list(row['waypoints_mm'][0]); end[1]=side*30.5
        tail=list(row['waypoints_mm'][-1]); lane=side*14.5
        low=(75 if row['role']=='D' else 87)+3*rank
        high=(130 if row['role']=='D' else 142)+3*rank
        row['waypoints_mm']=[end,[end[0],lane,end[2]],[end[0],lane,low],
            [tail[0],lane,low],[tail[0],lane,high],[tail[0],tail[1],high],tail]
        row['body_entry_tangent']=[0,-side,0]
        row['ground_orientation_180_same_footprint']=False
        result.append(row)
    assert len(result)==36
    return result


def main():
    import FreeCAD as A, Part
    from w5_source_grips_native_r1 import current_owners
    from w5_rounded_path import rounded
    start=datetime.now(timezone.utc); assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    folder=ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r3'
    r3=json.loads((folder/'checks.json').read_text(encoding='utf-8'))
    assert not r3['errors'] and len(r3['routes'])==36
    assert not any(h['wire'] in {r['wire'] for r in r3['routes'] if r['role']=='V'} for h in r3['hits'])
    assert all(sha(ROOT/k)==v for k,v in {**r3['source_sha256'],**r3['files']}.items())
    intent_file=ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json'
    old=json.loads(intent_file.read_text(encoding='utf-8')); rows=plan(old['routes'])
    shapes=Part.read(str(folder/'FANOUTS_WORLD.brep')).childShapes()
    paths=Part.read(str(folder/'CENTERLINES_WORLD.brep')).childShapes()
    inherited={r['wire']:(r,s,p) for r,s,p in zip(r3['routes'],shapes,paths) if r['role']=='V'}
    owners,pins=current_owners(A,Part)
    for label,rel in (
        ('SourceCarrier','hardware/cad/studies/w5-source-cage-access-native-r1/Carrier_WORLD.brep'),
        ('SourceCover','hardware/cad/studies/w5-source-cage-access-native-r1/Cover_WORLD.brep')):
        p=ROOT/rel; owners[label]=Part.read(str(p)); pins.append(p)
    for wire in ('W064','W065','W067','W068'):
        p=ROOT/f'hardware/electronics/full-cat/w5-source-grips-native-r2/{wire}_T18I_WORLD.brep'
        owners[wire+'_band']=Part.read(str(p)); pins.append(p)
    for key in ('source-switch-restraints-r2/P_SYS_seat_DESIGN','source-switch-restraints-r2/P_SYS_tie_DESIGN'): owners.pop(key)
    save(OUT/'intent.json',dict(status='COMMON_LOWER_FANOUT_CANDIDATE',routes=rows,
        source_selection='R53 plus explicitly unselected received source family',
        core_OD_assumption_mm=2.4,static_radius_assumption_mm=10,
        ground_blocks_unmoved_unrotated=True,existing_V_unchanged=True,
        selected=False,physical_pass=False))
    built=[]; geometries=[]; centerlines=[]; hits=[]; errors=[]; pairs=0
    def check(wire,s,key,t):
        nonlocal pairs
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox): continue
                pairs+=1
                try:
                    common=a.common(b)
                    if common.Volume>1e-5:
                        bb=common.BoundBox
                        hits.append(dict(wire=wire,owner=key,mm3=common.Volume,
                            bounds_mm=[getattr(bb,q) for q in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as exc: errors.append(dict(wire=wire,owner=key,error=str(exc)))
    for row in rows:
        try:
            if row['role']=='V':
                prior,shape,path=inherited[row['wire']]
                result=dict(prior)
                # New source material/wires are not part of the old V proof.
                for key,t in owners.items():
                    if key.startswith(('Source','W064','W065','W067','W068','XA01','TE130171','P_SYS_received','W066_received','W043_received','S1_reserved')): check(row['wire'],shape,key,t)
            else:
                path=rounded(A,Part,[A.Vector(*p) for p in row['waypoints_mm']],10)
                pieces=[Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(1.2,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False) for e in path.Edges]
                assert all(s.isValid() and len(s.Solids)==1 for s in pieces)
                shape=Part.makeCompound(pieces)
                for key,t in owners.items(): check(row['wire'],shape,key,t)
                length=path.Length+row['moving_candidate_length_mm']
                blank=math.ceil((length+11+30)/10)*10
                result=dict(wire=row['wire'],loom=row['loom'],role=row['role'],body_fanout_mm=path.Length,
                    continuous_external_design_mm=length,provisional_far_end_blank_mm=blank,
                    fits_nominal_900_candidate=blank<=900,factory_plug_consumed_length_unknown=True)
            built.append(result); geometries.append(shape); centerlines.append(path)
            save(OUT/'progress.json',dict(completed_routes=len(built),pairs=pairs,hits=hits,errors=errors))
            print('LOWER_FANOUT',row['wire'],round(path.Length,1),len(hits),len(errors),flush=True)
        except Exception as exc:
            errors.append(dict(wire=row['wire'],stage='build',error=str(exc)))
            print('LOWER_BUILD_ERROR',row['wire'],str(exc),flush=True)
    for i,s in enumerate(geometries):
        for j,t in enumerate(geometries[i+1:],i+1):
            if built[i]['role']=='V' and built[j]['role']=='V': continue
            check(built[i]['wire'],s,built[j]['wire'],t)
    corridor_file=ROOT/'hardware/electronics/full-cat/w5-leg-corridors-r3/intent.json'
    corridors=json.loads(corridor_file.read_text(encoding='utf-8'))['routes']
    bundles=Part.read(str(folder/'BUNDLES_WORLD.brep')).childShapes()
    for row,s in zip(corridors,bundles):
        for info,t in zip(built,geometries):
            if info['role']!='V' and info['loom']!=row['loom']: check(row['loom']+'_BUNDLE',s,info['wire'],t)
    files=[OUT/'intent.json']
    for name,group in (('FANOUTS_WORLD.brep',geometries),('CENTERLINES_WORLD.brep',centerlines)):
        p=OUT/name; Part.makeCompound(group).exportBrep(str(p)); files.append(p)
    pins += [Path(__file__),Path(__file__).with_name('w5_rounded_path.py'),intent_file,corridor_file,
        folder/'checks.json',folder/'FANOUTS_WORLD.brep',folder/'CENTERLINES_WORLD.brep',folder/'BUNDLES_WORLD.brep']
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='LOWER_FANOUT_REJECTED' if hits or errors or len(built)!=36 else 'LOWER_FANOUT_STATIC_CLEAR_RESTRAINTS_MOTION_OPEN',
        routes=built,hits=hits,errors=errors,pairs=pairs,ground_blocks_unmoved_unrotated=True,
        inherited_only='12 V against unchanged installed owners, moving bundle baseline; all new source owners and all 24 D/G checked',
        candidate_900_complete=len(built)==36 and all(r['fits_nominal_900_candidate'] for r in built),
        grips_complete=False,motion_qualified=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in files},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))


if __name__=='__main__': main()
