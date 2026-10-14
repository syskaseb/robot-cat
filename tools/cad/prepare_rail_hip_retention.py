"""Four COMPLETE changed carriers, not floating ports, for one shared gate.

Preserve original parents and both sibling arm/port recipes. Lower only the
Hip1 vertical land by12mm; extend its existing terminal arm to the new arrival.
This allocation is a candidate, not native or wiring acceptance.
"""
import copy
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import build_remaining_loom_supports as G
from support_entry_port import build as entry_build

P=G.P


def overlay(plan, paths, retention, roots):
    paths,retention,roots=map(copy.deepcopy,(paths,retention,roots))
    selected={r['physical_leg']+'FixedCarrier':r for r in plan['hips']}
    for collection in (paths,retention,roots):
        collection['groups']=[g for g in collection['groups'] if g['id'] in selected]
    changed=[]
    for owner,row in selected.items():
        land_id=row['loom']+'/Hip/Fixed'
        group=next(g for g in roots['groups'] if g['id']==owner)
        land=next(r for r in group['lands'] if r['id']==land_id)
        old_z=land['start_world_mm'][2]
        dz=row['fixed_anchor_world_mm'][2]-old_z
        assert abs(dz+12)<1e-7,(owner,dz)
        for key in ('start_world_mm','end_world_mm','centre_world_mm'):
            land[key][2]+=dz
        port=next(p for g in retention['groups'] if g['id']==owner for p in g['ports'] if p['land_id']==land_id)
        before=list(port['arrival_world_mm'])
        profile=entry_build(land,port)
        after=profile['arrival_world_mm'];port['arrival_world_mm']=after
        path=next(p for g in paths['groups'] if g['id']==owner for p in g['paths'] if p['land_id']==land_id)
        assert max(abs(a-b) for a,b in zip(path['points_mm'][-1],before))<1e-6
        assert abs(after[0]-before[0])+abs(after[1]-before[1])<1e-7
        path['points_mm'].append(after)
        changed.append(dict(owner=owner,land=land,arrival_before_mm=before,arrival_world_mm=after,
                            band='Band_'+land_id))
    return paths,retention,roots,changed


def run():
    tick=time.monotonic();pf=P.OUT/'body-low-hip-rail-exit-plan.json'
    plan=json.loads(pf.read_text())
    for n,h in plan['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    inputs=[P.OUT/n for n in ('remaining-support-shared-paths.json','remaining-retention-entry.json','remaining-loom-roots-plan.json')]
    paths,retention,roots,changed=overlay(plan,*[json.loads(f.read_text()) for f in inputs])
    reader=G.B.H.P.SavedShapes();sf=P.OUT/'StationFramesCurrent.FCStd'
    parents={g['preserved_owner']:reader.shape(sf,g['preserved_owner']) for g in roots['groups']}
    shapes,recipes,bands,bonds,errors=G.allocation(paths,retention,roots,parents)
    assert not errors,errors
    objects=dict(shapes)
    for row in changed:objects[row['band']]=bands[row['band']]
    dest=P.OUT/'body-rail-hip-retention-shapes.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        index=[]
        for i,(name,s) in enumerate(objects.items()):
            member=f'shape{i}.brep';z.writestr(member,s.exportBrepToString())
            index.append(dict(name=name,file=member,volume_mm3=s.Volume,valid=s.isValid(),solids=len(s.Solids)))
        z.writestr('index.json',json.dumps(index))
    overlays={}
    for name,data in (('paths',paths),('ports',retention),('roots',roots)):
        f=P.OUT/('body-rail-hip-'+name+'.json');f.write_text(json.dumps(data,indent=2)+'\n')
        overlays[f.relative_to(P.ROOT).as_posix()]=P.SHA(f)
    result=dict(status='FOUR_COMPLETE_RAIL_EXIT_CARRIERS_PREPARED_SHARED_SPACE_OPEN',
        changed=changed,recipes=recipes,archive=dest.relative_to(P.ROOT).as_posix(),archive_sha256=P.SHA(dest),
        removed_old_bands=[r['land']['id'] for r in changed],additional_T18I=0,new_fixed_lands=4,
        source_sha256={**overlays,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in inputs+[pf,sf,Path(__file__),Path(G.__file__),Path(__file__).with_name('support_entry_port.py')]}},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (P.OUT/'body-rail-hip-retention-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],shapes=len(objects),worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
