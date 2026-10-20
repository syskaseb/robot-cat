"""Reuse whole shoulder kit; rear+ adopts rear-'s60deg bypass topology.

The90deg rear+ path intersects actual knee056 at rest. Do not move purchased
modules or roots: reuse their bytes; only one entire wire corridor changes.
All12 not-yet-received actors still require their own rest checks.
"""
import copy,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from plan_feline_n01_shared import pipe
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();sf=OUT/'n01-MTA-shoulder-layout.json';prior=json.loads(sf.read_text())
    assert prior['status']=='SHOULDER_REST_LEG_HOLD' and len(prior['failures'])==1
    for p,h in prior['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors=load(prior);recipes=copy.deepcopy(prior['recipes']);n='CustomPrefix:W044';rows=copy.deepcopy(recipes['CustomPrefix:W052']['parts'])
    for p in rows:
        for k in ('start','mid','end'):
            if k in p:p[k][1]*=-1
    recipes[n].update(parts=rows,routing_exit_mm=rows[-1]['end'],route_topology='REAR_60DEG_BYPASS_KNEE_NOT_REAR90')
    assert rows[0]['start']==recipes[n]['point_mm'];actors[n]=pipe(rows,2.1)
    world,_,_,pins,_=compose();dest=OUT/'n01-MTA-rear-shoulders.json';archive=dest.with_suffix('.breps.zip')
    assert not dest.exists(),'Receive existing rear-shoulder result before any restart'
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/prior['bundle'],Path(__file__))})
    geometry=[]
    with zipfile.ZipFile(ROOT/prior['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,r in enumerate(prior['geometry']):
            name=r['name'];raw=actors[name].exportBrepToString().encode() if name==n else src.read(r['entry'])
            if name!=n:assert hashlib.sha256(raw).hexdigest()==r['sha256']
            entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(r,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    done=[name for name in prior['completed_rest'] if name!=n];checks={}
    result=dict(prior,status='RUNNING_REAR_SHOULDER_REST',source_sha256={**prior['source_sha256'],**pins},
        recipes=recipes,geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        byte_identical_actors_from_prior=63,completed_rest=done,failures=[],checks=0,
        portal_datums={name:r['routing_exit_mm'] for name,r in recipes.items()},N01_complete=False)
    query=SolidQueries()
    def save(status=None):
        if status:result['status']=status
        result.update(rest_checks=checks,checks=len(checks),failures=[key for key,row in checks.items() if not row['ok']],worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    save()
    for name in sorted(actors,key=lambda x:(not x.startswith('CustomPrefix:'),x)):
        if name in done:continue
        s=actors[name]
        for m,t in world.rest.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
            gap=query.distance(s,t);checks[name+'|rest:'+m]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if gap<1.25-1e-6:
                _,pts,_=s.distToShape(t);checks[name+'|rest:'+m]['witness_mm']=[[list(a),list(b)] for a,b in pts[:1]]
                save('REAR_SHOULDER_REST_HOLD');print(result['status'],name,m,gap,flush=True);return
        done.append(name);save()
    save('REAR_SHOULDER64_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN')
    print(result['status'],len(done),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
