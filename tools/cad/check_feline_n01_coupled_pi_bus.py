"""Read-only changed-interface screen for ONE analytic source/BUS plan.

Only correct saved actual material can establish a collision. Proposed
support/grip/plug boxes are classified separately as reservation overlaps.
No native documents, stock selections or historical results are overwritten.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,BASE
from plan_feline_n01_shared import pipe
from check_feline_shared_space import tube_prefix
from plan_feline_factory_links import routes

def main():
    tick=time.monotonic(); reader=SavedShapes()
    above_frame='--above-frame-joint-bay' in sys.argv
    joint_bay=above_frame or '--joint-power-bay' in sys.argv
    all_ends=joint_bay or '--all-ends' in sys.argv
    spatial=all_ends or '--spatial-unit' in sys.argv
    flat=spatial or '--flat-unit' in sys.argv
    lower=flat or '--lower-fore' in sys.argv
    target=OUT/('n01-joint-power-bay-above-frame.json' if above_frame else 'n01-joint-power-bay.json' if joint_bay else 'n01-coupled-pi-bus-checks-all-ends.json' if all_ends else 'n01-coupled-pi-bus-checks-spatial.json' if spatial else 'n01-coupled-pi-bus-checks-r3.json' if flat else 'n01-coupled-pi-bus-checks-r2.json' if lower else 'n01-coupled-pi-bus-checks.json')
    assert not target.exists(),'Receive existing result; do not repeat unchanged geometry'
    paths=[OUT/n for n in (('n01-coupled-pi-bus-plan-r4.json' if all_ends else 'n01-coupled-pi-bus-plan-r3.json' if flat else 'n01-coupled-pi-bus-plan-r2.json' if lower else 'n01-coupled-pi-bus-plan.json'),'n01-module-plan-r5.json',
        'n01-shared-preflight-r5.json','n01-compact-bank-plan-r2.json',
        'n01-common-backbone-preflight-r4.json','motion-layout.json')]
    candidate,plan,rear,bank,backbone,motion=[json.loads(p.read_text()) for p in paths]
    for p,h in candidate['source_sha256'].items(): assert sha(ROOT/p)==h,p
    assert all(candidate['necessary_length_gate'][k] for k in ('W043','W077','W078','exact_endpoint_match'))
    native=OUT/'FelineInteriorMotion.FCStd'
    assert sha(native)==bank['source_native_sha256']
    report=dict(status='RUNNING',selected=False,N01_complete=False,physical_pass=False,native_changed=False,
        contacts=[],reservation_overlaps=[],errors=[],exact_pairs=0,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths+[Path(__file__),native]},
        scope='Changed complete F_PI/P_SYS/MAIN/JPWM/BUS cases plus full W043/W077/W078, all24bank bends and8MTAfactory routes. Proposed support/plug/grip reservation overlaps distinguished from actual collisions. Not full80nets, tools or motion.',
        old_other_wire_routes_not_accepted=True)
    def save():
        report.update(worker_seconds=round(time.monotonic()-tick,3),updated_utc=datetime.now(timezone.utc).isoformat())
        target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def gate():
        if time.monotonic()-tick>240:
            report['status']='TIME_BOUNDED_PARTIAL_NOT_SELECTED';save();raise TimeoutError('240s cap')
    def placement(rr,t):
        m=A.Matrix()
        for i in range(3):
            for j in range(3):setattr(m,f'A{i+1}{j+1}',rr[i][j])
        return A.Placement(A.Vector(*t),A.Rotation(m))
    scene={}; roles={}; changed={}; bounds={}; valid={}; seen=set()
    splice=candidate['splice'];sv=A.Vector(*splice['tip18_mm']);ev=A.Vector(*splice['tip16_mm']);dd=ev-sv
    allowed_solder_overlap=Part.makeCylinder(1.71,dd.Length,sv,dd)
    report['declared_join_scope']='Only existing8mm solder-overlap cylinder; never exclude whole W077/W078 pair or supports'
    def check(an,a,bn,b,scope,reservation=False):
        gate();key=tuple(sorted((an,bn)))+(scope,)
        if key in seen:return
        seen.add(key)
        if an not in bounds:bounds[an]=a.BoundBox
        if bn not in bounds:bounds[bn]=b.BoundBox
        if not bounds[an].intersect(bounds[bn]):return
        report['exact_pairs']+=1
        try:
            for n,s in ((an,a),(bn,b)):
                if n not in valid:valid[n]=s.isValid() and bool(s.Solids)
                assert valid[n], 'Invalid material is not a clearance proof: '+n
            c=a.common(b);assert c.isNull() or c.isValid(),'Invalid common'
            if {an,bn}=={'W077','W078'} and not c.isNull():
                before=c.Volume;c=c.cut(allowed_solder_overlap)
                assert c.isNull() or c.isValid()
                report['intentional_bare_solder_overlap_mm3']=before-c.Volume
            if c.Volume>1e-5:
                v=c.BoundBox
                row=dict(a=an,b=bn,scope=scope,volume_mm3=c.Volume,
                    witness_bounds_mm=[[v.XMin,v.YMin,v.ZMin],[v.XMax,v.YMax,v.ZMax]])
                report['reservation_overlaps' if reservation else 'contacts'].append(row)
        except Exception as exc:report['errors'].append(dict(a=an,b=bn,scope=scope,error=str(exc)))
        if report['exact_pairs']%15==0:save()
    common_delta={'JPWM':[-90,44,30],'W041_Joint':[0,15,3],'W042_Joint':[0,-15,3]}
    effective=json.loads(json.dumps(plan))
    for g in effective['groups']:
        if g['role'] in common_delta:g['translation_mm']=(np.array(g['translation_mm'])+common_delta[g['role']]).tolist()
    joint_changes={}
    if joint_bay:
        # Cause change: release the whole lower floor bay, not another F_PI
        # offset. Four MTA AND all8 factory-end joints move as one architecture.
        for code,sign in (('FL',1),('FR',-1),('RL',1),('RR',-1)):
            joint_changes['MTA_'+code]=[0,-3*sign,71.5]
        for role,sign in (('W026_Joint',1),('W037_Joint',-1),('W045_Joint',1),('W053_Joint',-1)):
            joint_changes[role]=[0,-3*sign,71.5]
        joint_changes.update(W041_Joint=[0,-3,71.5],W042_Joint=[0,3,71.5],
            W044_Joint=[-23,6,71.5],W052_Joint=[-23,-6,71.5])
        if above_frame:
            # Resolve the actual frame top as one assembly plane, not local
            # case offsets. Rear inward joints and two ordered factory fans
            # are included BEFORE checking any whole Pi placement.
            targets={**{'MTA_'+c:[x,s*12,49] for c,x,s in
                (('FL',-40,1),('FR',-40,-1),('RL',65,1),('RR',65,-1))},
                'W026_Joint':[-97,12,49],'W037_Joint':[-97,-12,49],
                'W045_Joint':[121,12,49],'W053_Joint':[121,-12,49],
                'W041_Joint':[48,47,45],'W042_Joint':[48,-47,45],
                'W044_Joint':[-23,28,49],'W052_Joint':[-23,-28,49]}
            for g in effective['groups']:
                if g['role'] in targets:
                    centre=np.mean(g['candidate_bounds_mm'],axis=0)+np.array(common_delta.get(g['role'],[0,0,0]))
                    joint_changes[g['role']]=(np.array(targets[g['role']])-centre).tolist()
            report['above_frame_basis']={'frame_top_mm':37.02,'source_case_bottom_mm':41,
                'all_joint_centres_mm':targets,'rear_factory_fans_inboard_of_front_fans':True,
                'changes_reason':'First whole bay struck front/rear frame and crossed factory fans. One frame-relative plane and two ordered complete fans replace that layout, not single screw nudges.'}
        for g in effective['groups']:
            if g['role'] in joint_changes:
                g['translation_mm']=(np.array(g['translation_mm'])+joint_changes[g['role']]).tolist()
        report['joint_bay_architecture']={'relative_current_changes_mm':joint_changes,
            'source_cases_centre_z_mm':37.5,'two_factory_sides_each':True,
            'full_lower_bay_released_for_power_unit':True,
            'old_lower_rails_replaced_by_outboard_rails':True,
            'not_a_selected_layout_or_native_mount':True}
    for g in plan['groups']:
        role=g['role']
        for n in g['objects']:
            gate();s=reader.shape(native,n)
            if role in rear['changed_complete_receiving_groups']:
                rr=rear['relative_rotations'].get(role,np.eye(3).tolist())
                s.Placement=placement(rr,rear['changed_complete_receiving_groups'][role])*s.Placement
            if role in common_delta:s.translate(A.Vector(*common_delta[role]))
            if role in joint_changes:s.translate(A.Vector(*joint_changes[role]))
            if role=='F_PI':
                r=candidate['F_PI']; rr=np.array(r['rotation_relative_current'])
                delta=np.array(r['centre_mm'])-rr@np.array(r['old_centre_mm'])
                s.Placement=placement(rr,delta.tolist())*s.Placement; changed[n]=s
            elif role in candidate.get('relative_poses',{}):
                r=candidate['relative_poses'][role]
                s.Placement=placement(r['rotation_rows'],r['translation_mm'])*s.Placement;changed[n]=s
            elif role in candidate['shifts_mm']:
                s.translate(A.Vector(*candidate['shifts_mm'][role]))
                if not lower or role!='BUS':changed[n]=s
            scene[n]=s;roles[n]=role
    holder={}
    for key,p in bank['relative_holder_poses'].items():
        pose=placement(p['rotation_rows'],p['translation_mm'])
        for kind in ('Housing','IN','OUT','ATO'):
            n=f'Ref_Material_F_{key}_CP2_{kind}_0_0'
            scene[n].Placement=pose*scene[n].Placement;holder[n]=key
    stages={n for groups in motion['membership'].values() for ns in groups.values() for n in ns}
    for row in motion['inventory']:
        n=row['object']
        if n not in scene and row['kind']=='surface' and (n in stages or n.startswith(('Print_P0_','Ref_Material_P0_','Battery','Print_CP2_TailRiser'))):
            if not n.startswith('BatteryFrameHardware'):scene[n]=reader.shape(native,n)
    for i in range(1,5):scene[f'BellyFoot{i}']=reader.shape(native,f'BellyFoot{i}')
    current_bus={};current_bus_reserves={};current_bus_roots={}
    if above_frame:
        from plan_feline_n01_bus_complete import main as received_bus_geometry
        actual_bus,current_bus,current_bus_reserves,current_bus_roots,bus_recipe=received_bus_geometry(geometry_only=True)
        for n,s in actual_bus.items():scene[n]=s
        report['BUS_current_r3_not_old_shifted_prefix']={'source':'n01-bus-both-plugs-plan-r3.json',
            'pose':bus_recipe['relative_BUS_pose'],'both_plug_paths_included':True,
            'supplier25_transformed_BRep_gate':'n01-bus-source-cache-qualification.json'}
    wires={};own={}
    for row in backbone['bend_allocations']:
        p=np.array(row['start_mm']);q=np.array(row['end_mm']);b=np.array(row['bend']);R=row['bend_R_mm'];land=row['land_mm']
        d=(q-p-R*b)/(land+R)
        wires[row['id']]=tube_prefix(p,d,row['radius_mm'],b,R,land);own[row['id']]={row['holder']}
    for row in routes(effective):
        n='Factory:'+row['wire'];wires[n]=pipe(row['parts'],row['radius_mm']);own[n]={row['source_group'],row['joint_group']}
    if joint_bay:
        jointparts={n:s for n,s in scene.items() if roles.get(n) in joint_changes}
        report['joint_bay_factory_routes']=routes(effective)
        wires.update({'ReceivedBUS:'+n:s for n,s in current_bus.items()})
        wires.update({'StructureReserve:BUS:'+n:s for n,s in {**current_bus_reserves,**current_bus_roots}.items()})
        # Include whole common backbone reservations before power-unit search.
        # These are planning reserves, not actual finished PETG contact claims.
        for row in backbone['recipes']:
            if 'low_mm' not in row:continue
            n=row['name'];lo=np.array(row['low_mm'],float);hi=np.array(row['high_mm'],float)
            if n.startswith(('PiFuse','MainRaisedBridge','Standoff_MAIN','Standoff_BUS','SelectedSolderSpliceClip')):continue
            if n.startswith('LowerRail'):
                sign=1 if (lo[1]+hi[1])>0 else -1
                lo[1]=sign*35-3;hi[1]=sign*35+3
            if n.startswith('Crossmember'):lo[1]=-38;hi[1]=38
            wires['StructureReserve:'+n]=Part.makeBox(*(hi-lo),A.Vector(*lo));own['StructureReserve:'+n]=set()
        for n,s in jointparts.items():
            for bn,b in scene.items():
                if n==bn or roles.get(n)==roles.get(bn) or bn in changed:continue
                check(n,s,bn,b,'whole_upper_MTA_bay_case_vs_actual_static')
            for bn,b in wires.items():
                if roles.get(n) in own.get(bn,set()):continue
                check(n,s,bn,b,'whole_upper_MTA_bay_case_vs_complete_paths_or_structure',bn.startswith('StructureReserve:'))
        for n,s in wires.items():
            if not n.startswith('Factory:'):continue
            for bn,b in scene.items():
                if bn in changed or roles.get(bn) in own[n]:continue
                check(n,s,bn,b,'whole_upper_MTA_factory_route_vs_actual_static')
            for bn,b in wires.items():
                if n==bn:continue
                if bn.startswith(('Factory:','StructureReserve:')) and n>bn and bn.startswith('Factory:'):continue
                check(n,s,bn,b,'whole_upper_MTA_factory_route_vs_paths_or_structure',bn.startswith('StructureReserve:'))
        save();print('Joint bay preliminary',len(report['contacts']),len(report['reservation_overlaps']),len(report['errors']),flush=True)
        if report['contacts'] or report['reservation_overlaps'] or report['errors']:
            report.update(status='JOINT_POWER_BAY_REJECTED_BEFORE_UNIT_SEARCH',source_sha256={**report['source_sha256'],**reader.hashes})
            save();return
    actual_new={r['wire']:pipe(r['parts'],r['radius_mm']) for r in candidate['routes']}
    if all_ends:
        for row in candidate['additional_end_prefixes']:actual_new[row['wire']]=pipe(row['parts'],row['radius_mm'])
        report['full_unit_end_identities']=candidate['all_unit_ends']
    if flat:
        # All case hardware, ALL segments, full splice/grip envelopes search
        # together. Conservative overlap rejects only this cell, not real
        # material or general physical feasibility. No expensive CAD loop.
        def arraybox(s):
            b=s.BoundBox;return np.array([[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]])
        unit={**changed,**actual_new}
        lo,hi=np.array(candidate['splice']['clip_reservation_mm'])
        unit['UnitSpliceClip']=Part.makeBox(*(hi-lo),A.Vector(*lo))
        if all_ends:
            for n,(lo,hi) in candidate['shared_relief_reservations'].items():
                unit[n]=Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo))
            # Check invariant internal interfaces BEFORE search or details.
            for n,s in actual_new.items():
                for bn,b in changed.items():check(n,s,bn,b,'complete_unit_all_ends_vs_own_actual_cases')
            for n,s in unit.items():
                if n in actual_new or n in changed:continue
                for bn,b in changed.items():check(n,s,bn,b,'whole_unit_relief_reservation_vs_actual_case',True)
            if report['contacts'] or report['reservation_overlaps'] or report['errors']:
                report.update(status='INVARIANT_INTERNAL_UNIT_REJECTED_BEFORE_SEARCH',source_sha256={**report['source_sha256'],**reader.hashes})
                save();print(json.dumps(dict(status=report['status'],contacts=len(report['contacts']),reservations=len(report['reservation_overlaps']),errors=len(report['errors']))),flush=True);return
        else:
            rr=candidate['routes'][0];a=np.array(rr['end_mm'])-np.array([9,0,0])
            unit['InputFullGrip']=Part.makeCylinder(3.7,9,A.Vector(*a),A.Vector(1,0,0))
            rr=candidate['routes'][2];a=np.array(rr['end_mm'])-np.array([0,0,12])
            unit['MainFullGrip']=Part.makeCylinder(3.05,9,A.Vector(*a),A.Vector(0,0,1))
        proxy=[]
        for n,s in unit.items():
            if n not in actual_new:proxy.append(arraybox(s))
        for row in candidate['routes']+candidate.get('additional_end_prefixes',[]):
            for part in row['parts']:proxy.append(arraybox(pipe([part],row['radius_mm'])))
        proxy=np.array(proxy);centre=(proxy[:,0].min(axis=0)+proxy[:,1].max(axis=0))/2
        fixed={n:s for n,s in scene.items() if n not in changed}
        fixed.update(wires)
        for entry in candidate['BUS']['ports']:
            r=entry['first_bend_and_after_bend_grip']
            fixed['Nominal'+r['wire']]=pipe(r['parts'],r['radius_mm'])
        ob=np.array([arraybox(s) for s in fixed.values()]);ol,oh=ob[:,0],ob[:,1]
        candidates=[];stats=[];gap=1.25
        import itertools
        rotations=[]
        for yaw in (0,90,180,270):
            c,s=round(np.cos(np.deg2rad(yaw))),round(np.sin(np.deg2rad(yaw)))
            rotations.append((yaw,np.array([[c,-s,0],[s,c,0],[0,0,1]],float)))
        if spatial:
            prior=OUT/'n01-coupled-pi-bus-checks-r3.json'
            old=json.loads(prior.read_text());assert old['whole_unit_search']['candidates']==0
            report['source_sha256'][prior.relative_to(ROOT).as_posix()]=sha(prior)
            report['unchanged_floor_yaw_search_reused']=True
            rotations=[]
            for order in itertools.permutations(range(3)):
                for signs in itertools.product((-1,1),repeat=3):
                    R=np.zeros((3,3))
                    for i,j in enumerate(order):R[i,j]=signs[i]
                    if np.linalg.det(R)>0:rotations.append((len(rotations),R))
        if all_ends:
            from build_feline_layout_envelope import STATIONS,PROFILE_EXPONENT
            station=np.array(STATIONS,float)
            report['source_sha256']['tools/cad/build_feline_layout_envelope.py']=sha(ROOT/'tools/cad/build_feline_layout_envelope.py')
        for yaw,R in rotations:
            transformed=[]
            for box in proxy:
                corners=np.array(list(itertools.product(*zip(box[0],box[1]))))
                v=(corners-centre)@R.T;transformed.append([v.min(axis=0),v.max(axis=0)])
            transformed=np.array(transformed);mn=transformed[:,0].min(axis=0);mx=transformed[:,1].max(axis=0)
            z=-45.6+gap-mn[2]
            if spatial:
                points=np.array([[x,y,zz] for x in range(-100,141,10) for y in range(-60,61,10)
                    for zz in range(-20,71,10)],float)
            else:points=np.array([[x,y,z] for x in range(-100,141,5) for y in range(-45,46,5)],float)
            inside=np.all(points+mn>=[-139.1+gap,-95.6+gap,-45.6+gap],axis=1)&np.all(points+mx<=[181.1-gap,95.6-gap,109.6-gap],axis=1)
            points=points[inside];initial=len(points)
            if all_ends:
                # Necessary superellipse-corner budget for proposals only.
                # Polygonal/ruled actual volume and normal wall distance still
                # require the received-candidate exact envelope check.
                inset=gap+2.4
                for bb in transformed:
                    if not len(points):break
                    lo=points+bb[0]-inset;hi=points+bb[1]+inset
                    width=np.minimum(np.interp(lo[:,0],station[:,0],station[:,1]),np.interp(hi[:,0],station[:,0],station[:,1]))
                    height=np.minimum(np.interp(lo[:,0],station[:,0],station[:,2]),np.interp(hi[:,0],station[:,0],station[:,2]))
                    for x,w,h in station:
                        mask=(lo[:,0]<=x)&(hi[:,0]>=x)
                        width=np.where(mask,np.minimum(width,w),width);height=np.where(mask,np.minimum(height,h),height)
                    y=np.maximum(abs(lo[:,1]),abs(hi[:,1]));top=np.maximum(0,hi[:,2]-32)
                    good=(lo[:,0]>=station[0,0])&(hi[:,0]<=station[-1,0])&(lo[:,2]>=32-height/2)&(y<=width/2)
                    good&=(y/(width/2))**PROFILE_EXPONENT+(top/(height/2))**PROFILE_EXPONENT<=1
                    points=points[good]
            after_outline=len(points)
            restrictions=[]
            for pbox in transformed:
                gate()
                if not len(points):break
                keep=np.ones(len(points),bool)
                for j in range(0,len(points),256):
                    lows=points[j:j+256,None,:]+pbox[0];highs=points[j:j+256,None,:]+pbox[1]
                    hit=np.all((lows<oh[None,:,:]+gap)&(highs>ol[None,:,:]-gap),axis=2)
                    keep[j:j+256]=~np.any(hit,axis=1)
                points=points[keep]
                restrictions.append(len(points))
            stats.append(dict(orientation_index=yaw,rotation_rows=R.tolist(),inside_cells=initial,after_outline_budget=after_outline,
                conservative_clear_cells=len(points),remaining_after_each_unit_primitive=restrictions))
            report['search_progress']=stats;save()
            for pp in points:
                candidates.append(dict(yaw_deg=yaw,R=R.tolist(),centre_mm=pp.tolist(),
                    translation_mm=(pp-R@centre).tolist(),score=float(np.linalg.norm(pp-centre))))
        report['whole_unit_search']=dict(status='CLEAR_CONSERVATIVE_CELLS' if candidates else 'NO_CONSERVATIVE_CELL_NOT_PHYSICAL_INFEASIBILITY_PROOF',
            yaw_stats=stats,candidates=len(candidates),whole_case_and_route_proxy_boxes=len(proxy),
            fixed_actual_and_path_obstacles=len(fixed),gap_mm=gap,
            lower_deck_replacement_open=True,full_motion_and_other_end_routes_open=True)
        if not candidates:
            report.update(status='NO_CONSERVATIVE_SHARED_UNIT_PLACEMENT',source_sha256={**report['source_sha256'],**reader.hashes})
            save();print(json.dumps(report['whole_unit_search']),flush=True);return
        choice=min(candidates,key=lambda r:r['score']);report['whole_unit_search']['chosen_one']=choice
        T=placement(choice['R'],choice['translation_mm'])
        for n,s in unit.items():
            s.Placement=T*s.Placement
            if n in scene:scene[n]=s
        allowed_solder_overlap.Placement=T*allowed_solder_overlap.Placement
        report['unit_reservations_world_bounds_mm']={n:arraybox(s).tolist() for n,s in unit.items() if n not in changed and n not in actual_new}
        report['current_full_route_parts']={}
        for row in candidate['routes']+candidate.get('additional_end_prefixes',[]):
            parts=[]
            for old in row['parts']:
                new=dict(old)
                for k in ('start','mid','end'):
                    if k in old:new[k]=[float(v) for v in T.multVec(A.Vector(*old[k]))]
                parts.append(new)
            report['current_full_route_parts'][row['wire']]=parts
        # Current module poses are COMPOSED with the template pose; named
        # endpoints and ALL other ends must use the same one transform.
        report['whole_unit_pose_applies_to_all_module_ends']=True
        report['current_unit_case_bounds_mm']={n:arraybox(s).tolist() for n,s in changed.items()}
        save();print('Whole unit chosen',choice['centre_mm'],choice['yaw_deg'],flush=True)
    for n,s in changed.items():
        for bn,b in scene.items():
            if n==bn or roles.get(n)==roles.get(bn):continue
            check(n,s,bn,b,'changed_case_vs_actual_static_material')
        for bn,b in wires.items():check(n,s,bn,b,'changed_case_vs_complete_existing_bank_or_MTA_prefix')
    save();print('Cases',len(report['contacts']),len(report['errors']),flush=True)
    for n,s in actual_new.items():
        for bn,b in scene.items():
            if not lower:
                if n in ('W043','W077') and roles.get(bn)=='F_PI':continue
                if n=='W043' and roles.get(bn)=='WAGO:P_SYS_new':continue
                if n=='W078' and roles.get(bn)=='MAIN':continue
            check(n,s,bn,b,'complete_new_wire_vs_actual_static_material')
        for bn,b in wires.items():check(n,s,bn,b,'complete_new_wire_vs_complete_bank_and_MTA_prefixes')
        for bn,b in actual_new.items():
            if n<bn:check(n,s,bn,b,'new_wires_mutual')
        save();print('Wire',n,'contacts',len(report['contacts']),flush=True)
    reserves={}
    def box(n,lo,hi):
        reserves[n]=Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo))
    # ONE inboard detour around vertical F_PI instead of crossing its case.
    if not lower:
        box('LowerRail1Fore',[-72,17,39.72],[-64,23,42.72])
        box('LowerRail1ForeTurn',[-70,-3,39.72],[-64,23,42.72])
        box('LowerRail1Inboard',[-67,-3,39.72],[-33,3,42.72])
        box('LowerRail1RearTurn',[-36,-3,39.72],[-30,23,42.72])
        box('LowerRail1Rear',[-33,17,39.72],[108,23,42.72])
    if not flat:box('SpliceClip',*candidate['splice']['clip_reservation_mm'])
    if not lower:box('MainCarrier',[-52,-12,84],[-23,12,87])
    # rear branch below BUS, rooted at the existing rear post, not on skin
    for y in (-18.5,18.5):box('BUSRearBranch'+str(y),[102,y-3,67],[145,y+3,70])
    if not lower:box('JPWMForeSeat',[-102,-22,72],[-70,-8,74])
    box('BUSNominalMating',*candidate['BUS']['nominal_mating_reserve_mm'])
    box('BUSSharedTwoLaneGrip',*candidate['BUS']['shared_two_lane_after_bend_grip_mm'])
    for entry in candidate['BUS']['ports']:
        r=entry['first_bend_and_after_bend_grip'];actual_new['Nominal'+r['wire']]=pipe(r['parts'],r['radius_mm'])
    for rn,r in reserves.items():
        if lower and rn.startswith('BUS'):continue # exact received unchanged proof
        for bn,b in scene.items():
            if rn=='BUSNominalMating' and roles.get(bn)=='BUS':continue
            check(rn,r,bn,b,'proposed_reservation_vs_actual_material',True)
        for bn,b in wires.items():check(rn,r,bn,b,'proposed_reservation_vs_bank_and_MTA_prefix',True)
        for bn,b in actual_new.items():
            if rn=='SpliceClip' and bn in ('W077','W078'):continue
            if rn in ('BUSSharedTwoLaneGrip','BUSNominalMating') and bn.startswith('NominalBUS.'):continue
            check(rn,r,bn,b,'proposed_reservation_vs_new_wire',True)
    # Nominal new BUS wire paths against every actual neighbor and prefixes.
    for n,s in actual_new.items():
        if not n.startswith('NominalBUS.'):continue
        if lower:continue # unchanged BUS-vs-bank/fixed pairs already received
        for bn,b in scene.items():
            if roles.get(bn)=='BUS':continue
            check(n,s,bn,b,'nominal_BUS_wire_vs_actual_material')
        for bn,b in wires.items():check(n,s,bn,b,'nominal_BUS_wire_vs_bank_and_MTA_prefix')
    report.update(source_sha256={**report['source_sha256'],**reader.hashes},
        unchanged_BUS_evidence_reused=candidate.get('unchanged_BUS_reuse'),
        changed_case_objects=len(changed),bank_bends_included=24,MTA_factory_paths_included=8,
        proposed_reservations=list(reserves),motion_not_checked=True,full_other80net_curves_open=True,
        status='CHANGED_INTERFACES_REJECTED' if report['contacts'] or report['reservation_overlaps'] or report['errors'] else 'CHANGED_STATIC_INTERFACES_CLEAR_FULL_PLAN_OPEN')
    save();print(json.dumps(dict(status=report['status'],contacts=len(report['contacts']),reservation_overlaps=len(report['reservation_overlaps']),errors=len(report['errors']),pairs=report['exact_pairs'],seconds=report['worker_seconds'])),flush=True)

if __name__=='__main__':main()
