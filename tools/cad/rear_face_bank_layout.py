"""One rear4x3 bank candidate; keep fourMTA/eight factory feeds unchanged.

Rotate the existing48 nominal component BReps as rigid sets. No new vendor
dimensions or terminal pinouts. This is shared-space planning, NOT selection.
"""
import math
import re
import FreeCAD as A
import Part
from current_bank_datums import datums,bounds
from loom_land_port import box

FLANGE_X=170.
COLUMNS={'FL':78.,'FR':-78.,'RL':40.,'RR':-40.}
LEVELS={1:139.,2:89.,3:114.}


def layout(targets,contract,allocation):
    rows=datums(targets);parts={};records=[];sweeps={};jaws={};retired=set()
    voltage={r['loom']:r for r in contract['rows'] if r['core']=='V'}
    assert len(voltage)==12
    input_ends={e['role']:e for e in allocation['ends'] if re.fullmatch(r'F_(?:FL|FR|RL|RR)[123]\.in',e['role'])}
    assert len(input_ends)==12
    panel=box([166,-98,69,168,98,158])
    for r in rows:
        leg=('FL' if r['index']<=3 else 'RL') if r['side']=='L' else ('FR' if r['index']<=3 else 'RR')
        drive=(r['index']-1)%3+1;loom=leg+str(drive);v=voltage[loom]
        centre=r['centre_xy_mm']+[r['flange_top_z_mm']]
        target=[FLANGE_X,COLUMNS[leg],LEVELS[drive]]
        sign=-1 if r['side']=='L' else 1
        matrix=A.Matrix()
        # Original+Z -> rear+X; transverse axes keep INPUT below OUTPUT.
        for j,column in enumerate(([0,sign,0],[0,0,sign],[1,0,0]),1):
            for i,value in enumerate(column,1):setattr(matrix,'A'+str(i)+str(j),value)
        rotation=A.Rotation(matrix);translation=A.Vector(*target)-rotation.multVec(A.Vector(*centre))
        pose=A.Placement(translation,rotation)
        assert (pose.multVec(A.Vector(*centre))-A.Vector(*target)).Length<1e-6
        placed={}
        for kind,p in r['parts'].items():
            name=p['name'];retired.add(name);s=targets[name].copy();s.Placement=pose*s.Placement
            assert s.isValid() and len(s.Solids)==1
            placed[kind]=s;parts['RearBank/'+r['id']+'/'+kind]=s
        a=bounds(placed['ATO']);h=bounds(placed['Housing'])
        assert abs(a[0]-FLANGE_X)<1e-6 and abs(h[3]-FLANGE_X)<1e-6
        assert abs(a[3]-a[0]-18.8)<1e-6
        assert max(abs(h[1]),abs(h[4]))<100 and 0<h[2]<h[5]<160
        sweep=a[:];sweep[3]+=35;sweeps[r['id']]=box(sweep)
        x,y,z=target
        for side in (-1,1):
            lo,hi=(-5.55,-2.55) if side==-1 else (2.55,5.55)
            jaws[r['id']+'/'+str(side)]=box([x+11,y-10.55,z+lo,x+58,y+10.55,z+hi])
        panel=panel.cut(box([165,y-11.1,z-5.65,169,y+11.1,z+5.65]))
        inp=input_ends['F_'+loom+'.in'];in_point=list(pose.multVec(A.Vector(*inp['point_world_mm'])))
        out_point=list(pose.multVec(A.Vector(*v['receiver_point_mm'])))
        source=v['bundle_root_world_mm'];capacity=v['capacity_before_terminal_mm']
        lower=math.dist(source,out_point)+v['terminal_allowance_project_mm']
        assert lower<=capacity,('Factory V length lower bound fails',loom,lower,capacity)
        records.append(dict(id=r['id'],loom=loom,source_parts=r['parts'],
            old_flange_world_mm=centre,new_flange_world_mm=target,rotation_matrix=list(matrix.A),
            translation_mm=list(translation),input_wire=inp['wire'],input_point_mm=in_point,
            output_wire=v['wire'],output_point_mm=out_point,
            output_outward_axis=list(rotation.multVec(A.Vector(*v['receiver_outward_axis']))),
            source_bundle_root_mm=source,V_capacity_before_terminal_mm=capacity,
            V_straight_distance_plus_terminal_lower_bound_mm=lower,
            V_lower_bound_margin_mm=capacity-lower,
            length_status='Necessary lower bound only; full continuous source/body curve with bend limits still OPEN',
            new_pose_is_not_old_retention_or_route_qualification=True))
    panel=panel.removeSplitter();assert panel.isValid() and len(panel.Solids)==1 and not panel.check(True)
    return dict(parts=parts,panel=panel,records=records,sweeps=sweeps,jaws=jaws,retired_targets=retired,
        changed_wire_ids={r['input_wire'] for r in records}|{r['output_wire'] for r in records},
        panel_recipe=dict(bounds_mm=[166,-98,69,168,98,158],thickness_mm=2,
            apertures_mm=[22.2,11.3],b_tolerance_mm=[0,.3],
            source='MTA0300330 B0-100.E10A table for2mm panel; delivered snap/body/TE fit remains gate',
            frame_roots=None,fastener_layout=None,stock_selected=False),
        basis='One rear facade,4columns x3levels, central tail gap52mm. Retain35mm ATO withdrawal in+X; tool motion outside torso is not torso widening. Supersede only12 old bank poses and24 affected wire curves; source4MTA/eightfactory exits,24D/G and19 retained nets unchanged.',
        selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
