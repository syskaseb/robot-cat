"""Receive changed four-hip grips against the pinned current harness material.

Reuse unchanged eight-link/P0 receipts. Load the SAME49bodywires/12factory
bundles/10nativefixedparts, plus all40unchanged link-grip/strap bodies. Test
only changed hip interfaces; no unchanged whole-robot pair audit.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import w5_source_hip_grip_window as H
from servo_fuse_inputs_r1 import save,sha
from w5_exact_separation import separated
ROOT=H.ROOT;BASE=H.BASE;OUT=BASE/'w5-source-hip-harness-interface-r1'
CURRENT=BASE/'w5-source-link-harness-interface-r1/checks.json'


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    proof=read(H.OUT/'checks.json');bp=read(H.OUT/'blueprint.json')
    assert not proof['hits'] and not proof['errors'] and bp['print_quantity']==4
    for rel,h in {**proof['source_sha256'],**proof['files']}.items():assert sha(ROOT/rel)==h,rel
    current=read(CURRENT);assert not current['hits'] and not current['errors']
    pins=dict(current['source_sha256']);pins[CURRENT.relative_to(ROOT).as_posix()]=sha(CURRENT)
    for rel,h in pins.items():assert sha(ROOT/rel)==h,rel
    materials={};bodies=0;native=0;factory=0;link=0
    for rel in current['source_sha256']:
        if not rel.endswith('.brep'):continue
        path=ROOT/rel;s=Part.read(str(path))
        if path.name=='TWELVE_SOURCE_CLIPS_AND_STRAPS_PROPOSED_WORLD.brep':
            rows=read(path.parent/'blueprint.json')['roles'];shapes=s.childShapes();assert len(rows)==len(shapes)==40
            materials.update({'Link/'+n:p for n,p in zip(rows,shapes)});link=40
        elif path.name=='CORRIDORS_WORLD.brep':
            rows=read(path.parent/'intent.json')['routes'];shapes=s.childShapes();assert len(rows)==len(shapes)==12
            materials.update({'Factory/'+r['loom']:p for r,p in zip(rows,shapes)});factory=12
        elif path.name=='FANOUTS_WORLD.brep':
            rows=read(path.parent/'checks.json')['routes'];shapes=s.childShapes();assert len(rows)==len(shapes)==36
            for r,p in zip(rows,shapes):
                if r['role']=='V':materials[r['wire']]=p;bodies+=1
        else:
            name=path.stem
            if name.startswith('W0') or name.startswith('XA05'):bodies+=1;name=name.split('_')[0]
            else:native+=1
            assert name not in materials,name
            materials[name]=s
    assert (bodies,native,factory,link,len(materials))==(49,10,12,40,111)
    geometry=H.OUT/'TWELVE_SOURCE_CLIPS_AND_STRAPS_PROPOSED_WORLD.brep'
    pins[geometry.relative_to(ROOT).as_posix()]=sha(geometry)
    proposed=dict(zip(bp['roles'],Part.read(str(geometry)).childShapes()));assert len(proposed)==20
    hits=[];errors=[];pairs=0;OUT.mkdir(parents=True,exist_ok=True)
    for label,s in proposed.items():
        for owner,t in materials.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            for a in s.Solids:
                for b in t.Solids:
                    if not a.BoundBox.intersect(b.BoundBox) or separated(a,b):continue
                    pairs+=1
                    try:
                        c=a.common(b)
                        if c.Volume>1e-6:hits.append(dict(part=label,owner=owner,mm3=c.Volume))
                    except Exception as ex:errors.append(dict(part=label,owner=owner,error=str(ex)))
        if label.endswith('CableHead'):
            save(OUT/'progress.json',dict(last_part=label,pairs=pairs,hits=hits,errors=errors))
            print('HIP_HARNESS',label,pairs,len(hits),len(errors),flush=True)
    finish=datetime.now(timezone.utc)
    for p in (Path(__file__),H.OUT/'checks.json',H.OUT/'blueprint.json'):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    save(OUT/'checks.json',dict(status='FOUR_HIP_GRIPS_CURRENT_HARNESS_STATIC_CLEAR' if not hits and not errors else 'FOUR_HIP_GRIPS_CURRENT_HARNESS_REJECTED',
        proposed_materials=20,current_body_wires=bodies,current_native_fixed_parts=native,factory_bundles=factory,
        unchanged_link_materials=link,reused_P0_receipt=(H.OUT/'checks.json').relative_to(ROOT).as_posix(),
        pairs=pairs,hits=hits,errors=errors,source_sha256=pins,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        P0_unchanged=True,wire_paths_unchanged=True,whole_motion_mounting_and_stock_pending=True,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False))
    print('HIP_HARNESS_RECEIVED',pairs,len(hits),len(errors),flush=True)


if __name__=='__main__':main()
