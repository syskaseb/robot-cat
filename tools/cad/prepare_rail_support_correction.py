"""Build the one preflight-qualified five-owner candidate; no native mutation."""
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import build_remaining_loom_supports as G
P=G.P


def run():
    tick=time.monotonic();pf=P.OUT/'body-rail-support-correction-plan.json';plan=json.loads(pf.read_text())
    assert plan['status']=='RAIL_FIVE_OWNER_CORRECTION_PREFLIGHT_CLEAR_FULL_SPACE_OPEN' and not plan['contacts']
    for n,h in plan['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    files=[P.ROOT/plan['full_plan_files'][key] for key in ('paths','ports','roots')]
    paths,ports,roots=[json.loads(f.read_text()) for f in files]
    sf=P.OUT/'StationFramesCurrent.FCStd';reader=G.B.H.P.SavedShapes()
    parents={g['preserved_owner']:reader.shape(sf,g['preserved_owner']) for g in roots['groups'] if g.get('preserved_owner')}
    shapes,recipes,bands,bonds,errors=G.allocation(paths,ports,roots,parents);assert not errors,errors
    changed_ids=[r['loom']+'/Hip/Fixed' for r in json.loads((P.OUT/'body-low-hip-rail-exit-plan.json').read_text())['hips']]
    changed_ids += ['RR3/Splice/0','RR3/Splice/1']
    objects=dict(shapes);objects.update({'Band_'+lid:bands['Band_'+lid] for lid in changed_ids})
    archive=P.OUT/'body-rail-support-correction-shapes.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        index=[]
        for i,(name,s) in enumerate(objects.items()):
            member=f'shape{i}.brep';z.writestr(member,s.exportBrepToString())
            index.append(dict(name=name,file=member,solids=len(s.Solids),valid=s.isValid(),volume_mm3=s.Volume))
        z.writestr('index.json',json.dumps(index))
    result=dict(status='FIVE_COMPLETE_CORRECTED_SUPPORTS_PREPARED_FULL_SPACE_OPEN',groups=roots['groups'],recipes=recipes,
        changed_band_ids=changed_ids,archive=archive.relative_to(P.ROOT).as_posix(),archive_sha256=P.SHA(archive),
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files+[pf,sf,Path(__file__),Path(G.__file__)]},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (P.OUT/'body-rail-support-correction-material.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],shapes=len(objects),worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
