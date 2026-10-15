"""One straight factory approach and moving grip at the actual source axis.

No imposed right-angle before the moving grip. A single continuous free flex
joins the body land to the axial9mm source land and9mm factory straight.
Provisional plug reserve14mm is unchanged; no new connector or supplier claim.
"""
import copy,json,math,time
import current_body_fanout_material as M
from pathlib import Path
from plan_near_axis_hip_sources import OUT,ROOT,SHA
from plan_current_moving_looms import add,sub,mul,rotation
from plan_current_mta_interfaces import line
from spatial_down_axial_flex import build
from plan_continuous_joint_family import self_screen


def ends(row,h):
    pivot=row['pivot_mm'];v=rotation(row['moving_tangent_rest_world'],row['joint_axis'],h)
    moving=add(pivot,rotation(sub(row['moving_anchor_rest_world_mm'],pivot),row['joint_axis'],h))
    return add(row['fixed_anchor_world_mm'],[0,0,-9]),sub(moving,mul(v,9)),v,moving


def run():
    tick=time.monotonic();ff=OUT/'leg-source-near-member-plan.json';family=json.loads(ff.read_text());rejected=[]
    rows=copy.deepcopy([r for r in family['hips'] if r['loom'].endswith('1')])
    for row in rows:
        source=next(r for r in family['routes'] if r['loom']==row['loom'])['source']
        datum=source['connector_reservation_world_mm'][source['project_connector_choice']]
        axis=[float(round(x)) for x in source['cable_exit_world_axis']];side=1 if datum[1]>0 else -1
        row.update(source=source,source_parts=[line(add(datum,mul(axis,23)),add(datum,mul(axis,14)))],
            factory_guide_mm=9,factory_static_R_mm=None,moving_anchor_rest_world_mm=add(datum,mul(axis,23)),
            moving_tangent_rest_world=mul(axis,-1),fixed_tangent_world=[0,0,-1],
            fixed_anchor_world_mm=[-115.5 if row['physical_leg'].startswith('Front') else 170,side*50.,-8.],
            fixed_port_normal_world=[0,-side,0],moving_port_normal_world=[0,0,1])
        choices=[]
        for beta in (0,15,30,45,60,-15,-30,-45,-60):
            for length in range(125,351,5):
                if any(build(*ends(row,h)[:3],length+d,beta) is None for h in (0,-15,15) for d in (-5,0,5)):continue
                poses=[]
                for h in range(-15,16):
                    a,b,v,m=ends(row,h);middle=build(a,b,v,length,beta)
                    if middle is None or any(build(a,b,v,length+d,beta) is None for d in (-5,5)):break
                    parts=[line(row['fixed_anchor_world_mm'],a),*middle,line(b,m)]
                    if self_screen(parts) is not None:break
                    poses.append(dict(angle=h,parts=parts))
                if len(poses)==31:
                    bounds=[M.P.wire(p['parts']).BoundBox for p in poses]
                    if min(b.ZMin-3+168.319012764516 for b in bounds)<5:continue
                    overhang=max(max(-120-b.XMin,b.XMax-205,-100-b.YMin,b.YMax-100,0) for b in bounds)
                    choices.append((overhang,length,beta,poses));break
        if not choices:
            rejected.append(dict(loom=row['loom'],reason='No robust31pose axial source family in bounded space'));row['poses']=[];continue
        overhang,length,beta,poses=min(choices,key=lambda r:(r[0],r[1]));row.update(poses=poses,flex_length_mm=length,guide_mm=length+18,bridge_beta_degrees=beta,
            free_wire_XY_overhang_beyond_torso_mm=overhang,cosmetic_shell_fit_qualified=False,
            fixed_lands=[dict(id=row['loom']+'/Hip/Fixed',parts=[poses[15]['parts'][0]],owner='Body')],
            moving_lands=[dict(id=row['loom']+'/Hip/Moving',parts=[poses[15]['parts'][-1]],owner='Hip')])
        print('axial source',row['loom'],'freeflex',length,'beta',beta,'factory9mm',flush=True)
    result=dict(status='REJECTED_AXIAL_SOURCE_MATH' if rejected else 'FOUR_AXIAL_SOURCES_MATH_ONLY_SHARED_MATERIAL_ARMS_OPEN',
        hips=rows,rejected=rejected,project_length_margin_mm=5,project_jacket_OD_mm=6,project_dynamic_R_mm=31.5,
        changed_cause='Replace imposed90degree factory approach andUPmovingtangent with actual axial factory straight; moving grip close to actual connector, radial lever near Hip axis. No imaginary cable or connector.',
        retained='OriginalPCB/housing/socket/electricalends;other8sourcefamilies;20bodypaths;19bodyguides;P0/E6/15actuators',
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (ff,Path(__file__),Path(__file__).with_name('spatial_down_axial_flex.py'))},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'body-axial-hip-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],rejected=rejected,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
