"""One source-pinned common-space screen; no native/detail build or selection.

Reuse R5 rear bay and flat-bank R2 case/ATO proof. Check only added backbone,
24 complete first bends, changed JPWM/output bay and 38 new allocations.
Project reservations are not manufacturer dimensions or full wire routes.
"""
import copy
import json
import time
import sys
from datetime import datetime, timezone
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT, SavedShapes, sha
from plan_feline_layout import OUT, BASE, MODEL, STAGES
from plan_feline_n01_shared import near, pipe
from plan_feline_factory_links import routes
from check_feline_shared_space import tube_prefix
from check_feline_leg_body import placement


def main():
    tick=time.monotonic();reader=SavedShapes();rev4='--integrated-wire-channels' in sys.argv
    rev3=rev4 or '--washer-plane-carriers' in sys.argv
    rev2=rev3 or '--overhead-bank' in sys.argv
    dest=OUT/('n01-common-backbone-preflight-r4.json' if rev4 else 'n01-common-backbone-preflight-r3.json' if rev3 else 'n01-common-backbone-preflight-r2.json' if rev2 else 'n01-common-backbone-preflight.json')
    assert not dest.exists(), 'Receive existing result; no unchanged rerun'
    native=OUT/'FelineInteriorMotion.FCStd'
    files=[OUT/n for n in ('n01-module-plan-r5.json','n01-shared-preflight-r5.json',
        'n01-compact-bank-plan-r2.json','n01-compact-bank-preflight-r2.json',
        'endpoint-current-receivers.json','prefix-allocation.json','motion-layout.json',
        'current-mount-axis-inventory.json')]
    plan,lower,bank,bankproof,ends,prefixes,motion,axes_inventory=[json.loads(p.read_text()) for p in files]
    assert sha(native)==bank['source_native_sha256']
    assert not any(bankproof[k] for k in ('contacts','grip_conflicts','service_conflicts','errors'))
    report=dict(status='RUNNING',selected=False,N01_complete=False,physical_pass=False,native_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files+[native,Path(__file__)]},
        contacts=[],errors=[],pairs=0,recipes=[],allocations=[],bend_allocations=[],factory_routes=[],motion_samples=[],
        reuse='Exact flat-bank R2 poses/cases/ATO retained; JPWM changed and checked again. R5 rear source bay retained.',
        full_wiring=False,actual_tools_verified=False,all_mounts_complete=False,continuous_motion_verified=False,
        assumptions=['3.1mm max wire OD and 2mm grip wall are project budgets',
            '100mm usable MTA factory wire remains delivery gate','Nominal PCB datums are not delivered measurements'])
    def save():
        report.update(worker_seconds=round(time.monotonic()-tick,3),updated_utc=datetime.now(timezone.utc).isoformat())
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>480:
            report['status']='TIME_BOUNDED_PARTIAL_NOT_SELECTED';save();raise TimeoutError('480s operation cap')
    if rev2:
        parentfile=OUT/'n01-common-backbone-preflight.json';parent=json.loads(parentfile.read_text())
        assert parent['status']=='COMMON_BACKBONE_REJECTED_BEFORE_NATIVE_OR_MOTION' and not parent['errors']
        assert all(c['scope']=='common_structure_vs_actual_fixed_parts' and c['a'] in
            ('BankArm-69_-1','BankArm-69_1','Standoff_BUS_3','NeckWeb-1','NeckWeb1') for c in parent['contacts'])
        for p,h in parent['source_sha256'].items():
            if p!='tools/cad/plan_feline_n01_common_backbone.py':assert sha(ROOT/p)==h,p
        report['reuse_parent']=dict(report=parentfile.relative_to(ROOT).as_posix(),sha256=sha(parentfile),
            committed_source='6f94b1bb:tools/cad/plan_feline_n01_common_backbone.py',
            first_bends24_and_changed_output_bays='Identical recipes; reuse zero contacts/errors',
            changed_structure='Overhead fore-bank hangers instead of crossing P0 mounts; bridge-bottom keepout; sized standoffs; five lower-axis supports')
        if rev3:
            p2=OUT/'n01-common-backbone-preflight-r2.json';r2=json.loads(p2.read_text())
            assert len(r2['contacts'])==22 and not r2['errors']
            assert all('Nut_' in c['b'] or 'BottomWasher_' in c['b'] for c in r2['contacts'])
            report['reuse_r2']=dict(report=p2.relative_to(ROOT).as_posix(),sha256=sha(p2),
                committed_source='9c522c04:tools/cad/plan_feline_n01_common_backbone.py',
                scope='Unchanged frame/neck/lowerdeck clear; generic spacers rejected. Replace with carriers at actual washer/nut TOP planes.')
        if rev4:
            p3=OUT/'n01-common-backbone-preflight-r3.json';r3=json.loads(p3.read_text())
            assert len(r3['contacts'])==5 and not r3['errors']
            assert all(c['a']=='U1CarrierRoot0' or c['b'] in ('NineWireArmFL','NineWireArmFR') for c in r3['contacts'])
            report['reuse_r3']=dict(report=p3.relative_to(ROOT).as_posix(),sha256=sha(p3),
                scope='All PCB/neck/bank fixed contacts resolved. Replace U1 outboard roots with central roots; drill common cuff AND its load arm together.')
    scene={};role_of={};changed={};holder_of={};groups={g['role']:g for g in plan['groups']}
    valid={}
    def check(an,a,bn,b,scope):
        gate()
        if rev2 and scope in ('changed_JPWM_and_output_cases','complete_first_bank_bends',
            'bend_other_grips','bank_bends_mutual','changed_complete_factory_route'):return
        if rev2 and scope.startswith('common_structure_') and not an.startswith((
            'BankArm-69_','BankForeHanger','BankForeToe','NeckWeb','Standoff_',
            'U1Support','AUXSupport','AUXBacker','AUXEar','PiFuseCradle','PiFuseRiser',
            'PCBrail','PCBroot','U1Carrier','AUXCarrier')):return
        if rev3 and scope.startswith('common_structure_') and an.startswith((
            'NeckWeb','AUXBacker','AUXEar','PiFuseCradle','PiFuseRiser')):return
        if rev4 and scope.startswith('common_structure_') and not an.startswith(('U1Carrier','NineWireArm')):return
        if not near(a,b):return
        report['pairs']+=1
        try:
            for n,s in ((an,a),(bn,b)):
                if n not in valid:valid[n]=s.isValid() and bool(s.Solids)
                assert valid[n], 'Invalid/non-solid is not clearance: '+n
            c=a.common(b);assert c.isNull() or c.isValid(), 'Invalid intersection'
            if c.Volume>1e-5:report['contacts'].append(dict(a=an,b=bn,scope=scope,volume_mm3=c.Volume))
        except Exception as exc:report['errors'].append(dict(a=an,b=bn,scope=scope,error=str(exc)))
        if report['pairs']%10==0:save()
    save()
    new_deltas={'JPWM':[-90,44,30],'W041_Joint':[0,15,3],'W042_Joint':[0,-15,3]}
    effective=copy.deepcopy(plan)
    for g in effective['groups']:
        if g['role'] in new_deltas:
            g['translation_mm']=(np.array(g['translation_mm'])+new_deltas[g['role']]).tolist()
    for g in plan['groups']:
        role=g['role']
        for n in g['objects']:
            gate();s=reader.shape(native,n)
            if role in lower['changed_complete_receiving_groups']:
                rot=A.Rotation(A.Vector(1,0,0),90) if role in lower['relative_rotations'] else A.Rotation()
                s.Placement=A.Placement(A.Vector(*lower['changed_complete_receiving_groups'][role]),rot)*s.Placement
            if role in new_deltas:s.translate(A.Vector(*new_deltas[role]));changed[n]=s
            scene[n]=s;role_of[n]=role
    for key,p in bank['relative_holder_poses'].items():
        r=p['rotation_rows'];m=A.Matrix()
        for i in range(3):
            for j in range(3):setattr(m,f'A{i+1}{j+1}',r[i][j])
        pose=A.Placement(A.Vector(*p['translation_mm']),A.Rotation(m))
        for kind in ('Housing','IN','OUT','ATO'):
            n=f'Ref_Material_F_{key}_CP2_{kind}_0_0';s=scene[n].copy();s.Placement=pose*s.Placement
            scene[n]=s;holder_of[n]=key
    stage_of={n:(c,st) for c,g in motion['membership'].items() for st,ns in g.items() for n in ns}
    for row in motion['inventory']:
        n=row['object']
        if n not in scene and n not in stage_of and row['kind']=='surface' and n.startswith(('Print_P0_','Ref_Material_P0_','Battery','Print_CP2_TailRiser')):
            if not n.startswith('BatteryFrameHardware'):scene[n]=reader.shape(native,n)
    for i in range(1,5):scene[f'BellyFoot{i}']=reader.shape(native,f'BellyFoot{i}')
    for n,s in changed.items():
        for bn,b in scene.items():
            if n==bn or role_of.get(n)==role_of.get(bn):continue
            check(n,s,bn,b,'changed_JPWM_and_output_cases')
    wires={};grips={}
    for row in bankproof['grip_allocations']:
        key=row['holder'];p=np.array(row['start_mm']);d=np.array(row['end_mm'])-p;d/=np.linalg.norm(d)
        radius=row['outer_radius_mm']-2;bend=[0,0,-1 if key.startswith('L') else 1]
        wires[row['id']]=tube_prefix(p,d,radius,bend,12.4)
        grips[row['id']]=Part.makeCylinder(radius+2,9,A.Vector(*p),A.Vector(*d))
        end=p+(9+12.4)*d+12.4*np.array(bend)
        report['bend_allocations'].append(dict(id=row['id'],holder=key,start_mm=p.tolist(),end_mm=end.tolist(),
            radius_mm=radius,land_mm=9,bend_R_mm=12.4,bend=bend,full_middle_route=False))
    for n,s in wires.items():
        key=next(r['holder'] for r in bankproof['grip_allocations'] if r['id']==n)
        for bn,b in scene.items():
            if holder_of.get(bn)==key:continue
            check(n,s,bn,b,'complete_first_bank_bends')
        for bn,b in grips.items():
            if n!=bn:check(n,s,'Grip:'+bn,b,'bend_other_grips')
    for i,(n,s) in enumerate(wires.items()):
        for bn,b in list(wires.items())[i+1:]:check(n,s,bn,b,'bank_bends_mutual')
    for row in routes(effective):
        if row['wire'] not in ('W041','W042'):continue
        s=pipe(row['parts'],row['radius_mm']);n='Factory:'+row['wire'];wires[n]=s;report['factory_routes'].append(row)
        for bn,b in scene.items():
            if role_of.get(bn) in (row['source_group'],row['joint_group']):continue
            check(n,s,bn,b,'changed_complete_factory_route')
    save();print('New cases/prefixes',len(report['contacts']),len(report['errors']),flush=True)
    parts={}
    def box(n,lo,hi):
        parts[n]=Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo));report['recipes'].append(dict(name=n,low_mm=lo,high_mm=hi))
    for i,y in enumerate((-20,20)):box('LowerRail'+str(i),[-72,y-3,39.72],[108,y+3,42.72])
    for i,x in enumerate((0,90)):
        box('Crossmember'+str(i),[x-5,-33.5,39.72],[x+5,33.5,42.72])
        for sign in (-1,1):
            y=sign*24.5;n=f'RootBoss{i}_{sign}'
            parts[n]=Part.makeCylinder(9,3,A.Vector(x,y,39.72)).cut(Part.makeCylinder(1.7,3,A.Vector(x,y,39.72)))
            parts['Crossmember'+str(i)]=parts['Crossmember'+str(i)].cut(Part.makeCylinder(1.7,5,A.Vector(x,y,39)))
    for x in (-69,105):
        for sign in (-1,1):box(f'Post{x}_{sign}',[x-3,sign*20-3,42.72],[x+3,sign*20+3,85])
    for sign in (-1,1):
        lo,hi=sorted((sign*10,sign*30));box(f'UpperStrip{sign}',[-65,lo,85],[107,hi,88])
        lo,hi=sorted((sign*39.25,sign*67.75));box(f'BankBed{sign}',[-62,lo,52],[109,hi,55])
        for x in (-69,105):
            lo,hi=sorted((sign*20,sign*53.5));z=85 if rev2 and x==-69 else 52
            box(f'BankArm{x}_{sign}',[x-3,lo,z],[x+3,hi,z+3])
            if rev2 and x==-69:
                hy=sign*(70 if rev3 else 53.5)
                box(f'BankForeHanger{sign}',[-72,hy-3,52],[-66,hy+3,88])
                lo,hi=sorted((sign*53.5,hy))
                box(f'BankForeToe{sign}',[-72,lo-3,52],[-59,hi+3,55])
                if rev3:
                    lo,hi=sorted((sign*20,hy));box(f'BankArm{x}_{sign}',[-72,lo,85],[-66,hi,88])
    box('MainRaisedBridge',[-58,-12,91],[-29,12,94])
    box('PWMForeBranch',[-102,15.3,88.5],[-39.77,40.7,91.5])
    ztop={'Pi4':98.1,'BUS':90.72,'MAIN':96.52,'PWM9685':104}
    zbase={'Pi4':88,'BUS':88,'MAIN':94,'PWM9685':91.5}
    if rev3:
        zbase.update(Pi4=91.9,PWM9685=96)
        for role,xs,ys,z,rootz in (('Pi4',[-19.5,46.5],[-24.5,24.5],91.9,88),
                ('PWM9685',[-102.825,-38.945],[18.475,37.525],96,91.5)):
            for i,y in enumerate(ys):
                box(f'PCBrail{role}_{i}',[xs[0],y-4,z],[xs[1],y+4,z+2])
                for j,x in enumerate((0,30) if role=='Pi4' else (-85,-55)):
                    box(f'PCBroot{role}_{i}_{j}',[x-3,y-3,rootz],[x+3,y+3,z])
    for group in axes_inventory['groups']:
        role=group['role']
        if role not in ztop:continue
        for i,a in enumerate(group['unique_axes']):
            x,y=a['axis_world_xy_mm'];n=f'Standoff_{role}_{i}'
            outer,inner=(3,1.4 if role=='Pi4' else 1.2) if rev2 else (4,3)
            parts[n]=Part.makeCylinder(outer,ztop[role]-zbase[role],A.Vector(x,y,zbase[role])).cut(
                Part.makeCylinder(inner,ztop[role]-zbase[role],A.Vector(x,y,zbase[role])))
            for pn in ('UpperStrip-1','UpperStrip1','MainRaisedBridge','PWMForeBranch'):
                parts[pn]=parts[pn].cut(Part.makeCylinder(3,30,A.Vector(x,y,84)))
            if rev3 and role in ('Pi4','PWM9685'):
                for j in range(2):
                    pn=f'PCBrail{role}_{j}';parts[pn]=parts[pn].cut(Part.makeCylinder(inner,20,A.Vector(x,y,zbase[role]-1)))
            report['recipes'].append(dict(name=n,actual_saved_axis_xy_mm=[x,y],z_mm=[zbase[role],ztop[role]],
                plate_hardware_clearance_D_mm=6,standoff_OD_mm=outer*2,standoff_bore_D_mm=inner*2,nut_pocket_and_bearing_detail_open=True))
    box('HeadRootPlate',[-204,-30,-21.48],[-180,30,-18.48])
    for x in (-200,-184):
        for y in (-16,16):parts['HeadRootPlate']=parts['HeadRootPlate'].cut(Part.makeCylinder(1.7,5,A.Vector(x,y,-22.48)))
    for sign in (-1,1):
        y=sign*27-2.5
        section=((-183,-21.48),(-75,-21.48),(-75,-2),(-163,-18.48),(-183,-18.48)) if rev2 else ((-183,-21.48),(-75,-21.48),(-75,-2),(-183,-18.48))
        points=[A.Vector(x,y,z) for x,z in section]
        s=Part.Face(Part.makePolygon(points+[points[0]])).extrude(A.Vector(0,5,0))
        for x in (-80,-70):s=s.cut(Part.makeCylinder(3,32,A.Vector(x,sign*22.5,-30)))
        parts['NeckWeb'+str(sign)]=s
        report['recipes'].append(dict(name='NeckWeb'+str(sign),section_xz_mm=[[p.x,p.z] for p in points],
            y_range_mm=[y,y+5],root='Front belly-foot bridge -> existing twoM2 frame bolts',strength_verified=False))
    box('LowerDeck',[-85,-26,-44.5],[125,26,-42])
    for sign in (-1,1):
        lo,hi=sorted((sign*26,sign*54));box(f'OutputWing{sign}',[30,lo,-44.5],[66,hi,-42])
        # True joint case pocket, not a falsely ignored solid intersection.
        for n,s in scene.items():
            if role_of.get(n)==('W041_Joint' if sign==1 else 'W042_Joint'):
                parts[f'OutputWing{sign}']=parts[f'OutputWing{sign}'].cut(s)
        for x in (-75.5,117.5):
            lo,hi=sorted((sign*26,sign*36));box(f'LowerDeckRoot{x}_{sign}',[x-4,lo,-44.5],[x+4,hi,-42])
    if rev2:
        box('AUXBacker',[-113,-9,-23.38],[-82,21,-20.38])
        for sign in (-1,1):
            lo,hi=sorted((sign*18,sign*27));box(f'AUXEar{sign}',[-111,lo,-23.38],[-104,hi,-20.38])
        for group in axes_inventory['groups']:
            if group['role'] not in ('PWM1608_U1','AUX4092'):continue
            u1=group['role']=='PWM1608_U1'
            z0,z1=((-33.03,-25.03) if u1 else (-16.28,-8.28)) if rev3 else ((-42,-25.03) if u1 else (-20.38,-8.28))
            for i,a in enumerate(group['unique_axes']):
                x,y=a['axis_world_xy_mm'];n=('U1Support' if u1 else 'AUXSupport')+str(i)
                parts[n]=Part.makeCylinder(3,z1-z0,A.Vector(x,y,z0)).cut(
                    Part.makeCylinder(1.2 if rev3 else 1.7 if u1 else 1.2,z1-z0,A.Vector(x,y,z0)))
                if rev3:
                    if u1:
                        lo,hi=(-7,5) if rev4 else (2,13)
                        box(f'U1CarrierArm{i}',[x-3,lo,z0],[x+3,hi,z0+2])
                        lo,hi=(-7,-1) if rev4 else (7,13)
                        box(f'U1CarrierRoot{i}',[x-3,lo,-42],[x+3,hi,z0])
                        parts[f'U1CarrierArm{i}']=parts[f'U1CarrierArm{i}'].cut(Part.makeCylinder(1.2,4,A.Vector(x,y,z0-1)))
                    else:
                        # Lugs outside the saved PCB perimeter, not through underside pads.
                        ox=-113.5 if x<-100 else -81.1
                        box(f'AUXCarrierArm{i}',[min(ox,x)-3,y-3,z0],[max(ox,x)+3,y+3,z0+2])
                        box(f'AUXCarrierRoot{i}',[ox-3,y-3,-20.38],[ox+3,y+3,z0])
                        parts[f'AUXCarrierArm{i}']=parts[f'AUXCarrierArm{i}'].cut(Part.makeCylinder(1.2,4,A.Vector(x,y,z0-1)))
                report['recipes'].append(dict(name=n,actual_saved_axis_xy_mm=[x,y],z_mm=[z0,z1],
                    bottom_hardware_and_tool_open=True))
        box('PiFuseCradle',[-167.5,-28,-44.5],[-116.5,28,-42.125])
        for x in (-160,-120):
            for sign in (-1,1):box(f'PiFuseRiser{x}_{sign}',[x-3,sign*25-3,-42.125],[x+3,sign*25+3,-21.48])
    contractfile=BASE/'body-harness-checkpoint/body36-current-contract.json'
    contracts={r['wire']:r for r in json.loads(contractfile.read_text())['rows']}
    macrofile=BASE/'body-harness-checkpoint/body36-shared-macro-layout.json'
    for row in json.loads(macrofile.read_text())['changed_rows']:contracts[row['wire']].update(row)
    physical={'FL':('FrontLeft',-75.5,1,1),'FR':('FrontRight',-75.5,-1,1),
        'RL':('RearLeft',117.5,1,-1),'RR':('RearRight',117.5,-1,-1)}
    for code,(leg,x,sign,dx) in physical.items():
        y=sign*50;lo=[min(x,x+9*dx),y-7.15,62.85];hi=[max(x,x+9*dx),y+7.15,77.15]
        box('NineWireCuff'+code,lo,hi)
        px=-69 if x<0 else 105;yl,yh=sorted((sign*20,y))
        box('NineWireArm'+code,[px-3,yl,62.5],[px+3,yh,65.5])
    for row in ends['endpoints']:
        if row['group'] is not None:continue
        role=row['role']
        if role.startswith('SPLICE_PI'):
            p=[-78 if role.endswith('.16') else -86,0,43];axis=[1,0,0];support='SelectedSolderSpliceClip'
        else:
            c=contracts[row['wire']];code,stage=c['loom'][:2],int(c['loom'][2]);leg,x,sign,dx=physical[code]
            assert row['old_restraint_owner']==leg+'FixedCarrier'
            p=[x,sign*50+{'D':-3.6,'G':0,'V':3.6}[c['core']],70+(stage-2)*3.6]
            axis=[dx,0,0];support='NineWireCuff'+code
        report['allocations'].append(dict(id=row['id'],role=role,point_mm=p,bodyward_axis=axis,owner=support,
            status='PROJECT_ALLOCATION_NOT_COMPLETE_ROUTE',old_boundary_retired=True,actual_factory_length_verified=False))
    assert len(report['allocations'])==38 and len({a['id'] for a in report['allocations']})==38
    boundary_wires={}
    if rev3:
        for row in report['allocations']:
            if not row['owner'].startswith('NineWireCuff'):continue
            p=A.Vector(*row['point_mm']);d=A.Vector(*row['bodyward_axis'])
            boundary_wires[row['id']]=Part.makeCylinder(1.55,9,p,d)
            n=row['owner'];parts[n]=parts[n].cut(Part.makeCylinder(1.8,11,p-d,d))
            if rev4:
                arm=n.replace('NineWireCuff','NineWireArm')
                parts[arm]=parts[arm].cut(Part.makeCylinder(1.8,11,p-d,d))
    box('SelectedSolderSpliceClip',[-103,-9,38.9],[-61,9,47.1])
    report['splice_recipe']=dict(type='Existing selected solder overlap, no new connector',overlap_mm=8,
        sleeve_blank_mm=20,existing_material='RNF-100-3/16-0-STK',independent_intact_grips_x_mm=[[-103,-94],[-70,-61]],
        anchor='Split clip to actual front upper flange; retaining bolt outside flange',anchor_detail_open=True)
    # Intended bearing interfaces only; do not suppress neighboring moving parts.
    for n,s in parts.items():
        for bn,b in scene.items():
            if n.startswith(('NeckWeb','LowerDeckRoot')) and bn.startswith('BellyFoot'):continue
            check(n,s,bn,b,'common_structure_vs_actual_fixed_parts')
        for bn,b in wires.items():check(n,s,bn,b,'common_structure_vs_new_full_prefixes')
        for bn,b in grips.items():check(n,s,'Grip:'+bn,b,'common_structure_vs_complete_bank_grips')
        save();print('Structure',n,'contacts',len(report['contacts']),flush=True)
    if rev3:
        # These are real wire cylinders inside perforated cuff reservations;
        # no support is allowed to block a channel, including an intended joint.
        for n,s in boundary_wires.items():
            for bn,b in parts.items():check(n,s,bn,b,'allocated_boundary_wire_vs_all_structure')
    report['source_sha256'].update(reader.hashes)
    for p in (contractfile,macrofile):report['source_sha256'][p.relative_to(ROOT).as_posix()]=sha(p)
    if report['contacts'] or report['errors']:
        report['status']='COMMON_BACKBONE_REJECTED_BEFORE_NATIVE_OR_MOTION';save();return
    axfile=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axfile.read_text())['axes']
    moving={n:reader.shape(MODEL,n) for n in stage_of}
    for index,pose in enumerate(motion['poses']):
        for code,g in motion['membership'].items():
            a=[next(r for r in axes if r['code']==code and r['stage']==st) for st in STAGES]
            transforms=placement(a,pose['legs'][code]['angles_delta_degrees'])
            for st,ns in g.items():
                for n in ns:
                    s=moving[n].copy();s.Placement=transforms[st]*s.Placement
                    for bn,b in parts.items():check(f'pose{index}:'+n,s,bn,b,'added_structure_vs_sampled_leg_motion')
        report['motion_samples'].append(index);save();print('New structure motion',index,flush=True)
    report['source_sha256'].update(reader.hashes);report['source_sha256'][axfile.relative_to(ROOT).as_posix()]=sha(axfile)
    report['status']='COMMON_BACKBONE_SCREEN_CLEAR_FULL_ROUTES_TOOLS_COWLS_OPEN' if not(report['contacts'] or report['errors']) else 'COMMON_BACKBONE_MOTION_REJECTED'
    save()


if __name__=='__main__':main()
