"""Receive a whole neighbouring core with a proved shared circular trunk.

The unchanged W022 motion receipt gives a one-sided Hausdorff bound2.2mm
for matching equal-radius cross sections of the transported trunk. Use
that bound only where sufficient; query the remaining actual solid pairs.
The new bank branch is checked independently against EVERY motion actor.
"""
import hashlib,json,math,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from plan_feline_joint_usb_route import wire
from plan_feline_FL_three_core_shared_trunk import transport
from feline_tangent_routes import min_radius,length
from plan_feline_usb_service_bight import outer_margin


def solid(parts,radius):
    w=wire(parts);e=w.Edges[0]
    s=w.makePipeShell([Part.Wire([Part.makeCircle(radius,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
    assert s.isValid() and len(s.Solids)==1;return s


def receive(world,scene,rows,whole,base_whole,outer):
    tick=time.monotonic();sf=OUT/'n01-FL3-shared-trunk-whole-static.json';static=json.loads(sf.read_text())
    pf=OUT/'n01-FL3-shared-trunk-preflight.json';plan=json.loads(pf.read_text())
    bf=OUT/'n01-current-W022-complete-body-plan.json';base=json.loads(bf.read_text())
    mf=ROOT/base['motion'];motion=json.loads(mf.read_text())
    assert sha(mf)==base['motion_sha256'] and motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
    assert all(motion['source_sha256'].get(p)==h for p,h in world.pins.items())
    checks={k:v for k,v in static['checks'].items() if k.startswith('CurrentMiddle:W024|')}
    assert checks and all(r['ok'] for r in checks.values())
    assert static['failures']==['CurrentMiddle:W020|Ref_Material_F_PI_new_0_0','CurrentMiddle:W020|CurrentFoundation:BankPier:1']
    recipe=plan['recipes']['W024/body'];trunk,v=transport(base['middle_recipe']['parts'][:13],[0,0,2.2])
    for a,b in zip(trunk,recipe['parts'][:13]):
        assert a['kind']==b['kind'] and np.allclose(a['start'],b['start']) and np.allclose(a['end'],b['end'])
        if a['kind']=='arc':assert abs(a['radius']-b['radius'])<1e-6
    assert recipe['radius_mm']==base['middle_recipe']['radius_mm']==1.
    assert min_radius(recipe['parts'])>=recipe['required_R_mm']-1e-6
    assert whole.isValid() and len(whole.Solids)==1
    trunk_solid=solid(trunk,1.);branch=solid(recipe['parts'][13:],1.)
    outer_check=outer_margin(whole,outer);assert outer_check['ok']
    basebb=base_whole.BoundBox;branchbb=branch.BoundBox;query=SolidQueries()
    counts=dict(trunk_prior_exact_bound=0,trunk_bbox_bound=0,trunk_new_exact=0,branch_bbox_bound=0,branch_new_exact=0)
    exact={};lowest_trunk=math.inf;lowest_branch=math.inf
    assert len(world.motion)==3888 and {a['pose'] for a in world.motion}==set(range(36))
    for a in world.motion:
        bb=A.BoundBox(*a['bounds'][0],*a['bounds'][1]);prior_key='CurrentMiddle:W022|motion:'+a['name']+':'+str(a['pose'])
        prior=motion['checks'].get(prior_key);bound=(prior['gap_mm'] if prior else bbox_lower_bound(basebb,bb))-2.2
        if bound>=1.25-1e-6:counts['trunk_prior_exact_bound' if prior else 'trunk_bbox_bound']+=1
        else:
            tf=placement(a['r'],a['t']);s=trunk_solid.copy();s.Placement=tf.inverse()*s.Placement
            bound=query.distance(s,world.rest[a['name']]);counts['trunk_new_exact']+=1
            exact['trunk|'+a['name']+':'+str(a['pose'])]=dict(gap_mm=bound,minimum_mm=1.25,ok=bound>=1.25-1e-6)
        lowest_trunk=min(lowest_trunk,bound)
        branchbound=bbox_lower_bound(branchbb,bb)
        if branchbound>=1.25-1e-6:counts['branch_bbox_bound']+=1
        else:
            tf=placement(a['r'],a['t']);s=branch.copy();s.Placement=tf.inverse()*s.Placement
            branchbound=query.distance(s,world.rest[a['name']]);counts['branch_new_exact']+=1
            exact['branch|'+a['name']+':'+str(a['pose'])]=dict(gap_mm=branchbound,minimum_mm=1.25,ok=branchbound>=1.25-1e-6)
        lowest_branch=min(lowest_branch,branchbound)
    assert all(r['ok'] for r in exact.values())
    assert min(lowest_trunk,lowest_branch)>=1.25-1e-6
    ends=[e for e in rows if e['portion_id']=='W024/body'];assert len(ends)==2
    owners=['FLArcCuff:W024/body/start','Station:Bank:W024/body/end:wire:W024/body/end'];retained=[]
    for e,n in zip(ends,owners):
        p=A.Vector(*e['routing_exit_mm']);caps=[f for f in scene[n].Faces if type(f.Surface).__name__=='Plane' and (f.CenterOfMass-p).Length<1e-6]
        assert len(caps)==1 and abs(caps[0].Area-math.pi)<1e-5
        L=e.get('source_prefix_length_mm')
        if L is None:L=e['current_prefix_entry_mm']+e['received_prefix_R_mm']*math.radians(e['current_prefix_sweep_degrees'])
        assert abs(scene[n].Volume/math.pi-L)<1e-4;retained.append(L)
        assert checks['CurrentMiddle:W024|'+n]['ok'] and checks['CurrentMiddle:W024|'+n]['common_mm3']<1e-5
    dest=OUT/'n01-current-W024-shared-complete-body-plan.json';archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in {'CurrentMiddle:W024':whole,'MotionProof:Trunk':trunk_solid,'MotionProof:Branch':branch,**{n:scene[n] for n in owners}}.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result=dict(status='CURRENT_W024_SHARED_TRUNK_COMPLETE_BODY_AND_SAMPLE36_RECEIVED_NOT_N01',
        portion='W024/body',middle_recipe=recipe,source_prefix_owners=owners,
        current_boundaries=[dict(id=e['id'],point_mm=e['routing_exit_mm'],axis=e['routing_exit_axis'],retained_prefix_length_mm=L) for e,L in zip(ends,retained)],
        complete_body_length_mm=length(recipe['parts'])+sum(retained),middle_length_mm=length(recipe['parts']),
        checks=checks,outer=outer_check,motion_counts=counts,motion_new_exact=exact,
        motion_actors_covered=3888,sampled_poses=36,motion_trunk_minimum_bound_mm=lowest_trunk,
        motion_branch_minimum_bound_mm=lowest_branch,parallel_trunk_one_sided_Hausdorff_bound_mm=2.2,
        motion_proof='Equal-radius sections on exact parallel-transported circles are at most2.2mm from the received W022 solid. New branches checked separately. All insufficient old bounds replaced by actual solid queries.',
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        source_sha256={**static['source_sha256'],**{p.relative_to(ROOT).as_posix():sha(p) for p in (sf,pf,bf,mf,Path(__file__),ROOT/'tools/cad/plan_feline_FL_three_core_shared_trunk.py')}},
        preserved_W020_rejections=static['failures'],whole900_head_tail_motion_stock_and_other101portions_OPEN=True,
        N01_complete=False,physical_pass=False,native_changed=False,selected_SKUs_changed=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);return result
