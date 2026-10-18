"""One source-pinned common-space screen; no native/detail build or selection.

Reuse R5 rear bay and flat-bank R2 case/ATO proof. Check only added backbone,
24 complete first bends, changed JPWM/output bay and 38 new allocations.
Project reservations are not manufacturer dimensions or full wire routes.
"""
import copy
import json
import time
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
    tick=time.monotonic();reader=SavedShapes();dest=OUT/'n01-common-backbone-preflight.json'
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
    scene={};role_of={};changed={};holder_of={};groups={g['role']:g for g in plan['groups']}
    valid={}
    def check(an,a,bn,b,scope):
        gate()
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
            lo,hi=sorted((sign*20,sign*53.5));box(f'BankArm{x}_{sign}',[x-3,lo,52],[x+3,hi,55])
    box('MainRaisedBridge',[-58,-12,91],[-29,12,94])
    box('PWMForeBranch',[-102,15.3,88.5],[-39.77,40.7,91.5])
    ztop={'Pi4':98.1,'BUS':90.72,'MAIN':96.52,'PWM':104}
    zbase={'Pi4':88,'BUS':88,'MAIN':94,'PWM':91.5}
    for group in axes_inventory['groups']:
        role=group['role']
        if role not in ztop:continue
        for i,a in enumerate(group['unique_axes']):
            x,y=a['axis_world_xy_mm'];n=f'Standoff_{role}_{i}'
            parts[n]=Part.makeCylinder(4,ztop[role]-zbase[role],A.Vector(x,y,zbase[role])).cut(
                Part.makeCylinder(3,ztop[role]-zbase[role],A.Vector(x,y,zbase[role])))
            for pn in ('UpperStrip-1','UpperStrip1','MainRaisedBridge','PWMForeBranch'):
                parts[pn]=parts[pn].cut(Part.makeCylinder(3,30,A.Vector(x,y,84)))
            report['recipes'].append(dict(name=n,actual_saved_axis_xy_mm=[x,y],z_mm=[zbase[role],ztop[role]],
                hardware_clearance_D_mm=6,standoff_OD_mm=8,nut_pocket_and_bearing_detail_open=True))
    box('HeadRootPlate',[-204,-30,-21.48],[-180,30,-18.48])
    for x in (-200,-184):
        for y in (-16,16):parts['HeadRootPlate']=parts['HeadRootPlate'].cut(Part.makeCylinder(1.7,5,A.Vector(x,y,-22.48)))
    for sign in (-1,1):
        y=sign*27-2.5;points=[A.Vector(x,y,z) for x,z in ((-183,-21.48),(-75,-21.48),(-75,-2),(-183,-18.48))]
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
