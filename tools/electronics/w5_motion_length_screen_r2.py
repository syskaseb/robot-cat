"""Bound endpoint reach from saved rigid ownership, before motion CAD checks.

No arbitrary Gazebo limits or cable bending rating. Free revolute endpoint
distance bounds are conservative length screens, NOT routed/swept clearance.
Keep the factory cable untrimmed until unpowered fitting in phase2.
"""
from pathlib import Path
from datetime import datetime, timezone
import math, json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from check_main_p0_placement import SavedShapes, prop
from w5_leg_corridors_r1 import components
from servo_fuse_inputs_r1 import sha, save
BASE=ROOT/'hardware/electronics/full-cat'
OUT=BASE/'w5-motion-length-screen-r2'

def sub(a,b):return [x-y for x,y in zip(a,b)]
def norm(a):return math.sqrt(sum(x*x for x in a))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def rotate(p,pivot,axis,angle):
    u=sub(p,pivot);a=[x/norm(axis) for x in axis];c,s=math.cos(angle),math.sin(angle)
    cross=[a[1]*u[2]-a[2]*u[1],a[2]*u[0]-a[0]*u[2],a[0]*u[1]-a[1]*u[0]]
    return [pivot[i]+u[i]*c+cross[i]*s+a[i]*dot(a,u)*(1-c) for i in range(3)]
def one_axis_maximum(p,f,pivot,axis):
    u=sub(p,pivot);v=sub(f,pivot);a=[x/norm(axis) for x in axis]
    uz,vz=dot(u,a),dot(v,a)
    ur=math.sqrt(max(0,dot(u,u)-uz*uz));vr=math.sqrt(max(0,dot(v,v)-vz*vz))
    return math.hypot(uz-vz,ur+vr)

def two_axis_maximum_upper(p,f,first,second):
    # Exact outer-axis maximum at each inner sample, plus a rigorous gap
    # bound. Every inner angle is within0.5deg of one of360samples. Rotation
    # preserves distance; max outer-axis distance is1-Lipschitz in p.
    q=sub(p,second['pivot_mm']);axis=second['axis'];unit=[v/norm(axis) for v in axis]
    radial=math.sqrt(max(0,dot(q,q)-dot(q,unit)**2))
    values=[one_axis_maximum(rotate(p,second['pivot_mm'],axis,math.radians(i)),
        f,first['pivot_mm'],first['axis']) for i in range(360)]
    uncertainty=2*radial*math.sin(math.radians(.25))
    return max(values)+uncertainty,uncertainty

def main():
    start=datetime.now(timezone.utc);assert not (OUT/'screen.json').exists()
    pins=[]
    def read(rel):
        p=ROOT/rel;pins.append(p);return json.loads(p.read_text(encoding='utf-8'))
    entry=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
    reader=SavedShapes();objects=reader.doc(entry);component=components(objects)
    axes=read('hardware/simulation/p0/e6-leg-compatibility.json')['axes']
    sources=read('hardware/electronics/full-cat/w5-leg-source-map-r1/interface.json')['looms']
    mounts=read('hardware/electronics/full-cat/w5-moving-grip-space-plan-r1/plan.json')['looms']
    grips={r['loom']:r for r in mounts}
    connection=read('hardware/electronics/full-cat/w5-whole-connection-plan-r1/plan.json')
    frames={r['loom']:r for r in connection['split_interfaces']}
    lengths=read('hardware/electronics/full-cat/w5-leg-length-ledger-r1/ledger.json')
    ledger={r['loom']:r for r in lengths['looms']}
    # Direction is the received native Reference1->Reference2 hierarchy.
    incoming={};roots=set()
    for row in axes:
        refs=[prop(objects[row['name']],'Reference'+str(i))[0] for i in (1,2)]
        assert all(not r.get('file') for r in refs)
        a,b=[component(r.get('name')) for r in refs]
        assert a!=b and b not in incoming
        incoming[b]=(a,row);roots.add(a)
    root_nodes=roots-set(incoming);assert len(root_nodes)==1
    rows=[]
    for source in sources:
        loom=source['loom'];node=component('Rigid_'+source['pcb']);chain=[]
        seen=set()
        while node in incoming:
            assert node not in seen;seen.add(node)
            node,joint=incoming[node];chain.append(joint)
        assert node in root_nodes
        chain.reverse();assert 1<=len(chain)<=2
        assert all(j['physical_leg']==source['physical_leg'] for j in chain)
        moving=grips[loom]['proposed_source_grip_mm'];fixed=frames[loom]['fixed_split_axis_mm']
        if len(chain)==1:
            bound=one_axis_maximum(moving,fixed,chain[0]['pivot_mm'],chain[0]['axis'])
            method='Exact maximum endpoint separation for one unlimited revolute axis.'
            uncertainty=0
        else:
            bound,uncertainty=two_axis_maximum_upper(moving,fixed,*chain)
            method='Exact outer-axis maximum,360inner-axis samples and Lipschitz gap bound; covers all angle pairs, not obstacle-avoiding cable routes.'
        l=ledger[loom];reserve=max(c['external_candidate_mm'] for c in l['cores'])
        # Existing full route includes the20mm plug-side straight piece up to
        # this grip. Subtract it from the free-moving segment, not from stock
        # twice. Current corridor uses no new connector at its fixed split.
        corridors=read('hardware/electronics/full-cat/w5-leg-corridors-r3/checks.json') if not rows else corridors
        route=next(r for r in corridors['routes'] if r['loom']==loom)
        moving_route=route['path_mm']
        available=moving_route-20
        assert available>0
        rows.append(dict(loom=loom,physical_leg=source['physical_leg'],moving_component=component('Rigid_'+source['pcb']),
            moving_ancestor_joints=[j['name'] for j in chain],moving_grip_mm=moving,fixed_grip_mm=fixed,
            current_rest_endpoint_distance_mm=math.dist(moving,fixed),current_rest_free_route_mm=available,
            endpoint_separation_upper_bound_mm=bound,bound_method=method,angular_discretization_bound_mm=uncertainty,
            conservative_rest_route_minus_bound_mm=available-bound,
            endpoint_reach_bound_covered_by_rest_route=available>=bound,
            nominal_factory_mm=900,retained_common_blank_mm=l['common_uncut_blank_mm'],
            nominal_stock_margin_mm=l['nominal900_margin_mm'],maximum_rest_core_route_mm=reserve,
            trim_policy='Do not trim900mm factory loom before unpowered joint travel and body-end fitting.',
            bound_is_not_obstacle_avoiding_route=True,continuous_swept_clearance=False,
            cable_torsion_or_dynamic_radius_verified=False,physical_usable_factory_length_mm=None))
    assert len(rows)==12
    finish=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'screen.json',dict(status='TWELVE_LOOM_RIGID_CHAIN_ENDPOINT_REACH_SCREEN',looms=rows,
        supported_loom_count=12,one_axis_looms=sum(len(r['moving_ancestor_joints'])==1 for r in rows),
        two_axis_looms=sum(len(r['moving_ancestor_joints'])==2 for r in rows),
        endpoint_bound_covered_count=sum(r['endpoint_reach_bound_covered_by_rest_route'] for r in rows),
        no_simulation_joint_limits_assumed=True,no_joint_or_route_modified=True,
        next='Use these bounds to allocate motion reserve before changing paths. Receive changed clip/frame swept clearance separately; endpoint reach is not a cable envelope.',
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={**reader.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),*dict.fromkeys(pins)]}},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print(json.dumps(dict(looms=12,endpoint_bound_covered=sum(r['endpoint_reach_bound_covered_by_rest_route'] for r in rows),
        margins_mm={r['loom']:round(r['conservative_rest_route_minus_bound_mm'],2) for r in rows})))

if __name__=='__main__':main()
