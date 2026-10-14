"""Four whole oblique seats/bands plus proven retained frame subsets.

No arm or native build before the complete source-space gate. Prior carriers
are not globally hidden; their unchanged parents/two sibling branches remain.
"""
import copy
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from support_entry_port import build
import build_remaining_loom_supports as G
P=G.P


def run():
    tick=time.monotonic();mf=P.OUT/'body-oblique-port-motion-chosen-plan.json';motion=json.loads(mf.read_text())
    for n,h in motion['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    sf=P.OUT/'body-low-hip-retention-plan.json';old=json.loads(sf.read_text())
    archive=P.ROOT/old['archive'];assert P.SHA(archive)==old['archive_sha256']
    objects={}
    with zipfile.ZipFile(archive) as z:
        index=json.loads(z.read('index.json'))
        for row in old['retained']:
            item=next(r for r in index if r['name']=='Retained_'+row['owner'])
            q=Part.Shape();q.importBrepFromString(z.read(item['file']).decode());objects[item['name']]=q
    pf=P.OUT/'remaining-retention-entry.json';original=json.loads(pf.read_text());ports=[]
    for row in motion['hips']:
        owner=row['physical_leg']+'FixedCarrier';lid=row['loom']+'/Hip/Fixed';part=row['fixed_lands'][0]['parts'][0]
        land=dict(id=lid,loom=row['loom'],owner_stage='Body',start_world_mm=part['start'],end_world_mm=part['end'],
            centre_world_mm=[(a+b)/2 for a,b in zip(part['start'],part['end'])],axis=row['fixed_tangent_world'],length_mm=9)
        port=copy.deepcopy(next(r for g in original['groups'] if g['id']==owner for r in g['ports'] if r['land_id']==lid))
        profile=build(land,port);body=row['loom']+'ObliqueSeat';band=row['loom']+'ObliqueBand'
        objects[body]=profile['body'];objects[band]=profile['band']
        ports.append(dict(owner=owner,land=land,arrival_normal=port['arrival_normal'],arrival_world_mm=profile['arrival_world_mm'],
            recipe=profile['recipe'],body=body,band=band,
            root_world_mm=next(r['root_world_mm'] for r in old['retained'] if r['owner']==owner)))
    dest=P.OUT/'body-oblique-source-ports.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        index=[]
        for i,(name,s) in enumerate(objects.items()):
            assert s.isValid() and len(s.Solids)==1 and not s.check(True),name
            member=f'shape{i}.brep';z.writestr(member,s.exportBrepToString());index.append(dict(name=name,file=member,volume_mm3=s.Volume))
        z.writestr('index.json',json.dumps(index))
    result=dict(status='FOUR_OBLIQUE_PORTS_PREPARED_SOURCE_MATERIAL_ARMS_OPEN',retained=old['retained'],ports=ports,
        archive=dest.relative_to(P.ROOT).as_posix(),archive_sha256=P.SHA(dest),removed_old_bands=[r['land']['id'] for r in ports],
        new_fixed_lands=4,additional_T18I=0,source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (mf,sf,archive,pf,Path(__file__),Path(__file__).with_name('support_entry_port.py'))},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (P.OUT/'body-oblique-source-ports.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(ports=4,shapes=len(objects),worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
