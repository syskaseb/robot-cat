"""Change the four-path topology, not a third X shift through output shoes.

Retain factory tails, cases/M2, original feet/P0 and two output tie heads.
Fore first bends OUTWARD before rising; rear positive uses its first S;
rear negative uses a60deg shoulder behind actual S1, within the true torso.
Whole64 kit, complete independent grips and rooted floors precede selection.
"""
import copy,hashlib,json,math,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_plan import box
from plan_feline_remaining_factory_inputs import offset
from receive_feline_underplate_return_gallery import forward,bend
from plan_feline_n01_shared import pipe
from feline_mta_curved_grips import construct
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from feline_atomic_save import save_json


def routes(recipe,s1_xmin):
    side=np.sign(recipe['point_mm'][1]);d=np.asarray(recipe['axis']);fore=d[0]>0
    if fore:
        rows=[];q=forward(rows,np.asarray(recipe['point_mm']),d,.25)
        q,t=bend(rows,q,d,[0,side,0],25.2)
    else:
        rows=copy.deepcopy(recipe['parts'][:3]);q=np.asarray(rows[-1]['end'])
        if side<0:
            q=offset(rows,q,d,[0,-2,0]);target=s1_xmin-2.1-1.25-.4
            advance=25.2*(math.sin(math.pi/3)+math.cos(math.pi/3))
            lead=q[0]-advance-target;assert lead>0;q=forward(rows,q,d,lead)
            q,t=bend(rows,q,d,[0,side,0],25.2,math.pi/3)
        else:q,t=bend(rows,q,d,[0,side,0],25.2)
    q,t=bend(rows,q,t,[0,0,1],25.2)
    assert np.linalg.norm(t-[0,0,1])<1e-6 and q[2]<45.26
    forward(rows,q,t,45.26-q[2]);return rows


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-MTA-whole-corridor.json';prior=json.loads(sf.read_text());old=load(prior)
    assert len(prior['completed_rest'])==64 and not prior['failures']
    for p,h in prior['source_sha256'].items():assert sha(ROOT/p)==h,p
    bf=OUT/'n01-factory-saddles-received.json';base=json.loads(bf.read_text());basekit=load(base)
    s1=[s.BoundBox.XMin for n,s in parts.items() if 'S1' in n and 'body' in n]
    assert len(s1)==1,('Need actual selected S1 body datum',s1)
    actors=dict(old);ameta={r['name']:r for r in prior['geometry']};recipes=copy.deepcopy(prior['recipes']);changed=set();roots={}
    for n,r in recipes.items():
        for stale in ('upper_tilt_sine','first_S_and_grip_recipe_unchanged','first_XY_S_byte_recipe_preserved','portal_X_mm'):r.pop(stale,None)
        path=routes(r,s1[0]);r.update(parts=path,routing_exit_mm=path[-1]['end'],route_topology='OUTBOARD_SHOULDER_NOT_X_BAY',first_arc_R_mm=25.2)
        actors[n]=pipe(path,2.1);changed.add(n);w=n.split(':')[1]
        if w in ('W041','W042'):
            grip,proof=construct(r)
            for k,s in grip.items():gn='ArcGrip:'+w+':'+k;actors[gn]=s;changed.add(gn)
            roots[w]=dict(proof,parent=prior['positive_roots'][w]['parent'])
        else:roots[w]=copy.deepcopy(prior['positive_roots'][w])
    for parent,members in prior['print_groups'].items():
        floor=basekit[parent].copy() if parent in basekit else parts[parent].copy()
        for w,p in roots.items():
            if p['parent']!=parent:continue
            if parent.endswith('ForePanel'):
                lo,hi=p['actual_root_bounds_mm'];floor=floor.fuse(box([lo[0]-.3,lo[1]-.3,-44.3],[-49.25,hi[1]+.3,-42]))
            for k in ('band','head'):
                b=actors['ArcGrip:'+w+':'+k].BoundBox
                floor=floor.cut(box([b.XMin-.2,b.YMin-.2,-44.5],[b.XMax+.2,b.YMax+.2,-41.8]))
        assert floor.isValid() and len(floor.Solids)==1,parent
        actors[parent]=floor;changed.add(parent)
        union=floor.multiFuse([actors.get(n,parts.get(n)) for n in members if n!=parent])
        assert union.isValid() and len(union.Solids)==1,(parent,'Actual root union')
        b=union.BoundBox;assert max(b.XLength,b.YLength,b.ZLength)<250
        for w,p in roots.items():
            if p['parent']==parent:
                c=actors['ArcGrip:'+w+':pad'].common(floor);assert c.isValid() and c.Volume>1e-5
                p['parent_actual_overlap_mm3']=c.Volume
    dest=OUT/'n01-MTA-shoulder-layout.json';archive=dest.with_suffix('.breps.zip')
    assert not dest.exists(),'Receive saved shoulder layout before any restart'
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/prior['bundle'],bf,ROOT/base['bundle'],Path(__file__))})
    geometry=[]
    with zipfile.ZipFile(ROOT/prior['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        previous={r['name']:r for r in prior['geometry']}
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode() if n in changed else src.read(previous[n]['entry'])
            if n not in changed:assert hashlib.sha256(raw).hexdigest()==previous[n]['sha256']
            entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(ameta[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result=dict(prior,status='RUNNING_SHOULDER_REST_CHANGED_ONLY',source_sha256=pins,recipes=recipes,positive_roots=roots,
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        byte_identical_rest_reused=sorted(set(actors)-changed),changed=sorted(changed),completed_rest=sorted(set(actors)-changed),
        actual_S1_body_XMin_mm=s1[0],failures=[],checks=0,completed_static=[],completed_motion=[],N01_complete=False,
        portal_datums={n:r['routing_exit_mm'] for n,r in recipes.items()},rest_reused_from_sha256=sha(sf))
    for stale in ('pair_rows','pair_rows_sha256'):result.pop(stale,None)
    checks={};query=SolidQueries()
    def save(status=None):
        if status:result['status']=status
        result.update(rest_checks=checks,checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    save()
    for n in sorted(changed,key=lambda x:not x.startswith('CustomPrefix:')):
        s=actors[n]
        for m,t in world.rest.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
            gap=query.distance(s,t);checks[n+'|rest:'+m]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if gap<1.25-1e-6:save('SHOULDER_REST_LEG_HOLD');print(result['status'],n,m,gap,flush=True);return
        result['completed_rest'].append(n);save()
    save('SHOULDER64_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN')
    print(result['status'],len(changed),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
