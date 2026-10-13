"""Actual new carrier land boxes versus complete own-leg wire jackets.

Diagnose the planner's conservative wire rejections, not a whole mount PASS.
The new carrier is Hip-owned; source2/3 still include actual Knee motion.
"""
import itertools,json,time
from pathlib import Path
import FreeCAD as A
import Part
from plan_current_main_sources import ROOT,OUT,SHA
from plan_continuous_joint_family import parts_for_loom
from plan_current_rigid_factory_joins import moved_parts
from current_prototype_harness_scene import wire
from immutable_bounds import ImmutableBounds


def run():
    tick=time.monotonic();fp=OUT/'leg-source-near-member-plan.json';family=json.loads(fp.read_text())
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    bounds=ImmutableBounds();contacts=[];pairs=0;minimum=[]
    for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
        rows=[r for r in family['hips'] if r['physical_leg']==leg];sign=-1 if leg.startswith('Front') else 1
        own=[r for r in family['routes'] if r['source']['physical_leg']==leg];code=rows[0]['cad_code']
        ax=next(r for r in axes if r['code']==code and r['stage']=='Hip')
        for h,k in itertools.product((-15,0,15),repeat=2):
            rot=A.Rotation(A.Vector(*ax['axis']),h);pv=A.Vector(*ax['pivot_mm']);T=A.Placement(pv-rot.multVec(pv),rot)
            cables={r['loom']:wire(parts_for_loom(family,r['loom'],h,k,axes)+moved_parts(r['source_parts'],r['source'],h,k,axes)) for r in own}
            for row in rows:
                point=row['moving_anchor_rest_world_mm'];x,y,z=point[0]+sign*6,point[1],point[2]-4.5
                box=Part.makeBox(4,6,4,A.Vector(x-2,y-3,z-2));box.Placement=T*box.Placement
                for n,s in cables.items():
                    if not bounds.near(box,s,3.001):continue
                    pairs+=1;gap,points,_=box.distToShape(s)
                    minimum.append(dict(land=row['loom'],wire=n,Hip=h,Knee=k,gap_mm=gap))
                    if gap<3-1e-5:contacts.append(dict(land=row['loom'],wire=n,Hip=h,Knee=k,gap_mm=gap,required_mm=3,witness_mm=[list(p) for p in points[0]]))
        print('actual carrier lands',leg,'pairs',pairs,'contacts',len(contacts),flush=True)
    report=dict(status='NEW_CARRIER_LANDS_OWN_WIRES_CLEAR_FULL_ROOTS_OPEN' if not contacts else 'REJECTED_NEW_CARRIER_LAND_WIRE_CONTACT',
        pairs=pairs,contacts=contacts,nearest=sorted(minimum,key=lambda q:q['gap_mm'])[:12],sampled_coupled_poses=36,
        selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        scope='Only12new4x6x4mm carrier land search boxes versus complete own3wire jackets,9coupledHip/Kneeposes each; not full body/roots/ties/strength',
        worker_seconds=round(time.monotonic()-tick,3),source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (fp,af,Path(__file__))})
    (OUT/'complete-source-carrier-lands-material.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','pairs','contacts','worker_seconds')}),flush=True)


if __name__=='__main__':run()
