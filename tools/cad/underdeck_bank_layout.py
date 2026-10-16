"""One side-access underdeck bank, same12 nominal holders/24 TE parts.

Keep the protected central MAIN area free inX, stay below the upper platform,
and use outward service, not vertical extraction through the source module.
All wire/fastener/root/native qualifications remain OPEN.
"""
import math,re
import FreeCAD as A
import Part
from current_bank_datums import datums,bounds
from loom_land_port import box

CENTRES=[-100.,-15.,15.,45.,75.,105.]
FLANGE_Y=65.
FLANGE_Z=47.


def layout(targets,contract,allocation):
    rows=datums(targets);parts={};records=[];sweeps={};jaws={};retired=set();panels=[]
    voltage={r['loom']:r for r in contract['rows'] if r['core']=='V'}
    inputs={e['role']:e for e in allocation['ends'] if re.fullmatch(r'F_(?:FL|FR|RL|RR)[123]\.in',e['role'])}
    assert len(voltage)==len(inputs)==12
    for row in rows:
        leg=('FL' if row['index']<=3 else 'RL') if row['side']=='L' else ('FR' if row['index']<=3 else 'RR')
        drive=(row['index']-1)%3+1;loom=leg+str(drive);side=1 if row['side']=='L' else -1
        rotation=A.Rotation(A.Vector(1,0,0),-side*90)
        old=row['centre_xy_mm']+[row['flange_top_z_mm']]
        target=[CENTRES[row['index']-1],side*FLANGE_Y,FLANGE_Z]
        pose=A.Placement(A.Vector(*target)-rotation.multVec(A.Vector(*old)),rotation)
        placed={}
        for kind,p in row['parts'].items():
            retired.add(p['name']);s=targets[p['name']].copy();s.Placement=pose*s.Placement
            assert s.isValid() and len(s.Solids)==1;placed[kind]=s
            parts['UnderdeckBank/'+row['id']+'/'+kind]=s
        a=row['parts']['ATO']['bounds_mm'];sweep=a[:];sweep[5]+=35
        s=box(sweep);s.Placement=pose*s.Placement;sweeps[row['id']]=s
        cx,cy=row['centre_xy_mm'];z=row['flange_top_z_mm']
        for sign in (-1,1):
            lo,hi=(-5.55,-2.55) if sign==-1 else (2.55,5.55)
            s=box([cx-10.55,cy+lo,z+11,cx+10.55,cy+hi,z+58]);s.Placement=pose*s.Placement
            jaws[row['id']+'/'+str(sign)]=s
        v=voltage[loom];inp=inputs['F_'+loom+'.in']
        input_point=list(pose.multVec(A.Vector(*inp['point_world_mm'])))
        output_point=list(pose.multVec(A.Vector(*v['receiver_point_mm'])))
        for kind,point in [('IN',input_point),('OUT',output_point)]:
            b=bounds(placed[kind]);assert all(lo-1e-5<=p<=hi+1e-5 for p,lo,hi in zip(point,b[:3],b[3:])),(loom,kind,point,b)
        lower=math.dist(v['bundle_root_world_mm'],output_point)+v['terminal_allowance_project_mm']
        assert lower<=v['capacity_before_terminal_mm'],('Insufficient V necessary bound',loom)
        records.append(dict(id=row['id'],loom=loom,new_flange_world_mm=target,old_flange_world_mm=old,
            rotation_matrix=list(rotation.toMatrix().A),translation_mm=list(pose.Base),
            input_wire=inp['wire'],input_point_mm=input_point,output_wire=v['wire'],output_point_mm=output_point,
            output_outward_axis=list(rotation.multVec(A.Vector(*v['receiver_outward_axis']))),
            V_capacity_before_terminal_mm=v['capacity_before_terminal_mm'],
            V_straight_distance_plus_terminal_lower_bound_mm=lower,V_lower_bound_margin_mm=v['capacity_before_terminal_mm']-lower,
            length_status='Necessary bound ONLY, full curves/radii/material still OPEN',
            source_bundle_root_mm=v['bundle_root_world_mm'],new_pose_is_not_old_retention_or_route_qualification=True))
    for side in (1,-1):
        rotation=A.Rotation(A.Vector(1,0,0),-side*90);pose=A.Placement(A.Vector(0,side*FLANGE_Y,FLANGE_Z),rotation)
        for start,stop in ((0,3),(3,6)):
            xs=CENTRES[start:stop];p=box([xs[0]-20,-9.3,-4,xs[-1]+20,9.3,-2])
            for x in xs:p=p.cut(box([x-11.1,-5.8,-5,x+11.1,5.8,-1]))
            p=p.removeSplitter();assert p.isValid() and len(p.Solids)==1 and not p.check(True)
            p.Placement=pose*p.Placement;panels.append(p)
    return dict(parts=parts,panel=Part.makeCompound(panels),records=records,sweeps=sweeps,jaws=jaws,retired_targets=retired,
        component_prefix='UnderdeckBank/',changed_wire_ids={r['input_wire'] for r in records}|{r['output_wire'] for r in records},
        panel_recipe=dict(quantity=4,thickness_mm=2,apertures_mm=[22.2,11.6],
            b_basis='Use upper11.6 of manufacturer11.3(+0.3/-0), d2mm; delivered snap/body/TE fit remains gate',
            source='hardware/reference/servo-holder-p0-2026-09-24/0300330.png',frame_roots=None,fastener_layout=None,stock_selected=False),
        basis='One underdeck horizontal/outward bank. FlangesY+/-65,Z47; all old48 nominal component BReps transformed rigidly, no body-profile reduction. Central MAIN Xgap retained.4small2mm panels; installed bounds below upper platform and inside200mm width.35mm ATO/projectjaw withdrawal to sides, no vertical source-module teardown.',
        selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
