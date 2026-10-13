"""Prepare one shared8-port set and EXACT retained4frame subsets before arms.

Remove only the four superseded Hip1-owned port/arm recipes. Rebuild from the
unchanged native parents plus both untouched sibling arms/ports, and prove
every retained subset remains inside its previous accepted carrier. No global
owner exclusion, no native mutation, and no whole-wiring acceptance.
"""
import copy
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import build_remaining_loom_supports as G
from support_entry_port import build as entry_build
from current_body_fanout_material import load

P=G.P


def run():
    tick=time.monotonic();pf=P.OUT/'body-low-hip-exit-plan.json'
    plan=json.loads(pf.read_text());assert plan['chosen_common_flex_mm'] and not plan['errors']
    for n,h in plan['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    files=[P.OUT/n for n in ('remaining-support-shared-paths.json','remaining-retention-entry.json','remaining-loom-roots-plan.json')]
    paths,retention,roots=[json.loads(f.read_text()) for f in files]
    selected={r['physical_leg']+'FixedCarrier':r for r in plan['hips']}
    kept=[]
    for collection,key in ((paths,'paths'),(retention,'ports'),(roots,'lands')):
        collection['groups']=[g for g in collection['groups'] if g['id'] in selected]
        for group in collection['groups']:
            loom=selected[group['id']]['loom']
            group[key]=[r for r in group[key] if r.get('land_id',r.get('id'))!=loom+'/Hip/Fixed']
    actual,wires,pins=load();reader=G.B.H.P.SavedShapes();sf=P.OUT/'StationFramesCurrent.FCStd'
    parents={g['preserved_owner']:reader.shape(sf,g['preserved_owner']) for g in roots['groups']}
    shapes,recipes,bands,bonds,errors=G.allocation(paths,retention,roots,parents)
    assert not errors,errors
    for name,s in shapes.items():
        previous=actual[name+'/0/0'];outside=s.copy().cut(previous.copy())
        assert outside.isValid() and outside.Volume<1e-5,(name,'Changed retained sibling geometry',outside.Volume)
        kept.append(dict(owner=name,preserved_owner=recipes[name]['preserved_owner'],
            retained_volume_mm3=s.Volume,outside_previous_mm3=outside.Volume,
            removed_only=selected[name]['loom']+'/Hip/Fixed owned arm/port recipe',
            root_world_mm=next(g['root_world_mm'] for g in paths['groups'] if g['id']==name)))
    objects={'Retained_'+n:s for n,s in shapes.items()};ports=[]
    for row in plan['hips']:
        owner=row['physical_leg']+'FixedCarrier'
        normal=[1 if row['physical_leg'].startswith('Front') else -1,0,0]
        for index,record in enumerate(row['fixed_lands']):
            segment=record['parts'][0];a,b=segment['start'],segment['end']
            land=dict(id=record['id'],loom=row['loom'],owner_stage='Body',start_world_mm=a,end_world_mm=b,
                centre_world_mm=[(x+y)/2 for x,y in zip(a,b)],axis=[(y-x)/9 for x,y in zip(a,b)],length_mm=9)
            port=dict(land_id=land['id'],arrival_normal=normal,
                recipe=dict(construction='single_post_axial_entry_below_band',band_axial_offset_mm=0,
                    axial_entry_extension_mm=2))
            profile=entry_build(land,port)
            key=row['loom']+('Horizontal' if index==0 else 'BendBoundary')
            objects[key+'Body']=profile['body'];objects[key+'Band']=profile['band']
            ports.append(dict(owner=owner,land=land,arrival_normal=normal,arrival_world_mm=profile['arrival_world_mm'],
                recipe=profile['recipe'],body=key+'Body',band=key+'Band',
                root_world_mm=next(r['root_world_mm'] for r in kept if r['owner']==owner)))
    dest=P.OUT/'body-low-hip-retention-shapes.zip';index=[]
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(name,s) in enumerate(objects.items()):
            member=f'shape{i}.brep';data=s.exportBrepToString();z.writestr(member,data)
            index.append(dict(name=name,file=member,volume_mm3=s.Volume,valid=s.isValid(),solids=len(s.Solids)))
        z.writestr('index.json',json.dumps(index))
    result=dict(status='EIGHT_FIXED_PORTS_AND_FOUR_EXACT_RETAINED_FRAME_SUBSETS_PREPARED_SPACE_OPEN',
        retained=kept,ports=ports,archive=dest.relative_to(P.ROOT).as_posix(),archive_sha256=P.SHA(dest),
        removed_old_bands=[row['loom']+'/Hip/Fixed' for row in plan['hips']],
        additional_T18I=4,new_fixed_lands=8,body_groups=4,
        open=['Actual8profiles/new4wholeflexes vs retained assembly/current11bodycurves and each other',
            'Both independently rooted arms pergroup, complete shared material/motion/assembly before native',
            'Corrected four source/breakout guides/cut/stock; no implicit inherited acceptance'],
        source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files+[pf,sf,Path(__file__),Path(G.__file__),Path(__file__).with_name('compact_loom_land_port.py'),Path(__file__).with_name('support_entry_port.py')]}},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (P.OUT/'body-low-hip-retention-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],ports=len(ports),retained_frames=len(kept),shapes=len(objects),worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
