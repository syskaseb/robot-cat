"""One common four-holder/eight-factory-end allocation before native CAD.

Allocate BOTH ends using real opposed-port inline connectors, not a
return-cavity221-412. This is a factory-interface plan, not complete W5 or a clearance
claim. All custom continuations and supports must pass together before CAD.
"""
import json,math,time
from pathlib import Path
from plan_current_body_harness import ROOT,BASE,OUT,SHA
R=25.2
def add(a,b):return [x+y for x,y in zip(a,b)]
def mul(a,k):return [x*k for x in a]
def line(a,b):return dict(kind='line',start=a,end=b,length_mm=math.dist(a,b))
def curve(a,b,m,r,angle):return dict(kind='arc',start=a,mid=m,end=b,radius_mm=r,length_mm=r*angle)
def shift(a,u,v,d):
    phi=math.acos(1-d/(2*R));sn,cs=math.sin(phi),math.cos(phi)
    p=add(add(a,mul(u,R*sn)),mul(v,R*(1-cs)))
    q=add(add(p,mul(u,R*sn)),mul(v,R*(1-cs)))
    m1=add(add(a,mul(u,R*math.sin(phi/2))),mul(v,R*(1-math.cos(phi/2))))
    m2=add(add(p,mul(u,R*(sn-math.sin(phi/2)))),mul(v,R*(math.cos(phi/2)-cs)))
    return [curve(a,p,m1,R,phi),curve(p,q,m2,R,phi)]
def quarter(a,u,v):
    b=add(add(a,mul(u,R)),mul(v,R));k=math.sqrt(.5)
    mid=add(add(a,mul(u,R*k)),mul(v,R*(1-k)))
    return curve(a,b,mid,R,math.pi/2)
def factory(start,u,v,offset=None):
    end=add(start,mul(u,9));parts=[line(start,end)]
    parts+=shift(end,u,v,offset) if offset is not None else [quarter(end,u,v)]
    end=parts[-1]['end'];parts.append(line(end,add(end,mul(u if offset is not None else v,9))))
    return parts
def plan():
    owners=json.loads((OUT/'owner-plan.json').read_text())
    current={r['id']:r for r in owners['body_conductors']}
    poses={'FL':[-15,80.5,151.4],'FR':[-57.5,-80.5,151.4],
           'RL':[130,80.5,151.4],'RR':[136,-80.5,151.4]}
    ids={'FL':('W041','W026'),'FR':('W042','W037'),
         'RL':('W044','W045'),'RR':('W052','W053')}
    holders=[];routes={};joints=[]
    for leg,c in poses.items():
        x,y,z=c;side=1 if y>0 else -1
        holders.append(dict(leg=leg,body_centre_mm=c,
            casing_mm=[x-17.5,y-11,z-8,x+17.5,y+11,z+8],
            yaw_deg=180 if leg in ('FL','FR') else 0,
            input_mm=[x+(17.5 if leg in ('FL','FR') else -17.5),y,z],
            output_mm=[x+(-17.5 if leg in ('FL','FR') else 17.5),y,z],
            nominal_body_basis='Existing MTA family35x22x16 allowance, actual supplied lead/lid fit gate',
            native_mount_status='OPEN_NOT_MODELED'))
        for is_input,wid in zip((True,False),ids[leg]):
            ux=(-1 if is_input else 1)*(-1 if leg in ('FL','FR') else 1)
            start=[x+ux*17.5,y,z]
            u=[ux,0,0]
            # All joints stay inboard within the fixed200mm width.
            # Return cavity is outside the MTA casing, not aimed
            # straight back into it. Rear output uses the rear-centre aisle.
            v=[0,-side,0]
            if leg=='FL' and not is_input:
                q=factory(start,u,v,12)
                connection_axis=u
            elif leg=='FL' or not is_input and leg in ('RL','RR'):
                q=factory(start,u,v)
                connection_axis=v
            else:
                q=[line(start,add(start,mul(u,9))),line(add(start,mul(u,9)),add(start,mul(u,18)))]
                connection_axis=u
            end=q[-1]['end'];length=sum(p['length_mm'] for p in q)
            assert length<=84.5 and q[0]['length_mm']==q[-1]['length_mm']==9
            fuse_role='F_'+leg+('.in' if is_input else '.out')
            roles=[current[wid]['a'],current[wid]['b']]
            assert fuse_role in roles,(wid,roles)
            remote=next(role for role in roles if role!=fuse_role)
            assert remote in (
                'P_FRONT.2','P_FRONT.3','P_REAR.2','P_REAR.3',
                'FL_P.1','FR_P.1','RL_P.1','RR_P.1'),wid
            second=add(end,mul(connection_axis,35.5))
            if connection_axis[0]:
                lo,hi=sorted((end[0],second[0]))
                box=[lo,end[1]-4.05,z-4.45,hi,end[1]+4.05,z+4.45]
            else:
                lo,hi=sorted((end[1],second[1]))
                box=[end[0]-4.05,lo,z-4.45,end[0]+4.05,hi,z+4.45]
            dep=connection_axis
            routes[wid+'_FACTORY']=dict(body_conductor_id=wid,parts=q,radius_mm=2.1,
                guide_mm=length,nominal_strip_mm=11,usable_lead_assumption_mm=84.5,
                margin_mm=84.5-length,manufacturer_two100mm_lead_claim=False,
                actual_delivered_cut_mm=None)
            joints.append(dict(id=wid+'_Joint',sku='WAGO221-2411',casing_mm=box,
                factory_entry_mm=end,custom_entry_mm=second,
                custom_departure_axis=dep,
                custom_continuation_to=remote,
                current_custom_route='OPEN_MUST_JOIN_FULL_SHARED_ALLOCATION',
                supports_and_lever_space='OPEN_NO_PREWIRING_WAIVER',
                envelope_basis='WAGO datasheet2026-01-23:35.5depthx8.1widthx8.9height, opposed entries. Entry-axis vertical datum is nominal; delivery fit gate. Fine-strandedCu4mm2 max, strandedCu2.5mm2 max must not be conflated.'))
    return dict(status='CURRENT_FOUR_MTA_FACTORY_INTERFACE_PLAN_ONLY',
        allocation_revision=6,
        selected=False,W5_complete=False,physical_pass=False,holders=holders,
        factory_routes=routes,joints=joints,
        quantity_reconciliation={'installed_joint_candidates':8,
            'replace_unselected_old_output_joint_roles':4,
            'old_XB11_221412_role_released_by_selected_W1_lap':True,
            'extra_input_joints':4,'spares':1,'candidate_total_not_purchase':9},
        next='Complete all eight custom continuations, twelve ATO input feeds, moving leg looms, ground/data/source/local wiring with registered CURRENT bank retention and native W1. Old bank plastics are superseded CP2 references. No native mounts until the shared routing/access gate.',
        no_rejected_geometry_reuse='MTA6 preserves three clear MTA4 families/FL body+input. FL output whole S-guide crosses inboard before XB22 vertical, then inline liesY64.45..72.55,Z146.95..155.85 between actual lower/upper head returns, outside S0keyY1..31. No deleting key or moving retained wires. Opposed-port221-2411; all guides/joints and moving head still require gate.',
        source_sha256={(OUT/'owner-plan.json').relative_to(ROOT).as_posix():SHA(OUT/'owner-plan.json'),
                       (OUT/'inline-terminal-data.json').relative_to(ROOT).as_posix():SHA(OUT/'inline-terminal-data.json'),
                       Path(__file__).relative_to(ROOT).as_posix():SHA(Path(__file__))})
def run():
    tick=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-tick
    (OUT/'mta-interface-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],holders=len(p['holders']),factory_ends=len(p['factory_routes']),
        all_factory_lengths_mm={k:round(v['guide_mm'],3) for k,v in p['factory_routes'].items()},selected=False)))
if __name__=='__main__':run()
