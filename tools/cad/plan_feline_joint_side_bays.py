"""Coupled source-side bay allocation after whole REV3 evidence, not offsets.

Retains all unchanged actual material. Reconstructs typed station profiles from
the frozen whole-gate recipes, restores the EXISTING cut MAIN cap proposal,
then allocates all three FHAC complete two-tail packages and monitor together.
Every rejection is explicitly exact-distance or conservative planning screen.
No selected/native source is saved or modified.
"""
import itertools
import json
import math
import sys
import time
from pathlib import Path
import numpy as np
import FreeCAD as A
from scipy.spatial import cKDTree
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT
from feline_rev3_query_scene import build
from feline_current_scene import load
from plan_feline_central_pi_wedge import packed
from check_feline_all_current_lands import near
from check_feline_shared_space import tube_prefix
from plan_feline_front_service_split import line_tube
from compose_feline_shared_space_atlas import inside_ruled
from plan_feline_skin_access import surface_samples


def main():
    tick=time.monotonic();upper='--upper-side-domain' in sys.argv
    dest=OUT/('n01-joint-upper-side-bays.json' if upper else 'n01-joint-side-bays.json')
    previous=json.loads(dest.read_text()) if dest.exists() else None
    if previous:assert previous['status']=='PARTIAL_COUPLED_SIDE_DOMAINS'
    priorfile=OUT/'n01-rev3-whole-profiles.json';prior=json.loads(priorfile.read_text())
    assert prior['status']=='WHOLE_REV3_PROFILE_GATE_RECEIVED_NOT_N01' and not prior['errors']
    for n,h in prior['source_sha256'].items():assert sha(ROOT/n)==h,n
    scene,meta,pins,bus=build();_,oldmeta,templates,data,_,_=load()
    # Replay ALL typed previous profiles exactly; no default cylinder shrink.
    for n,r in prior['recipes'].items():
        q=A.Vector(*r['point_mm']);d=A.Vector(*r['departure_axis']);b=A.Vector(*r['bend_unit'])
        scene[n]=tube_prefix(list(q),list(d),r['radius_mm'],list(b),r['R_mm'],3)
        a,c=r['after_grip_mm'];scene[n+':after9']=line_tube(a,c,r['radius_mm'])
        meta[n]=meta[n+':after9']=dict(kind='wire',wire_owner=r['wire'])
    for file,group in ((OUT/'n01-coupled-clocked-joints.json','F_PWM'),(OUT/'n01-selected-local-head-tail-sources.json',None)):
        _,shapes,rows=packed(file)
        for n,s in shapes.items():
            if group is None or rows[n]['group']==group:scene[n]=s;meta[n]=rows[n]
    clockfile=OUT/'n01-coupled-clocked-joints.json';_,clocked,crows=packed(clockfile)
    cap=clocked['RetainedMAINCutForeCap'];oldstrip=scene['StructureReserve:UpperStrip-1']
    assert cap.isValid() and cap.Solids and cap.cut(oldstrip).Volume<1e-8
    # Source-derived subset, NOT a filled generic box. Structural/root approval
    # remains open; the MAIN functional pocket itself is never removed.
    scene.pop('StructureReserve:UpperStrip-1');meta.pop('StructureReserve:UpperStrip-1')
    scene['RetainedMAINCutForeCap']=cap;meta['RetainedMAINCutForeCap']=crows['RetainedMAINCutForeCap']
    stations={r['ref']:r for r in data['ports']['stations']}
    changed={};newrecipes={};moves={
        'G_TAIL':(-110,True),'P_REAR':(-110,True),
        'D_FL':(-64,False),'FL_G':(-16,False),'FR_P':(32,False),
        'D_FR':(80,False),'FR_G':(128,False)}
    if upper:
        # Directional topology change, not a third fore X-offset trial. Both
        # fore station fans turn INWARD before the taper, away from PWM.
        moves['G_TAIL']=(-110,False);moves['P_REAR']=(-110,False)
        # Opposing fans need >=53.1mm, not a uniform48mm station pitch.
        moves['D_FR']=(72,False)
    def station_group(n):
        if n.startswith('REV3Station:'):return n.split(':')[1].split('.')[0]
        return next((ref for ref,st in stations.items() if oldmeta.get(n,{}).get('role')==st['current_group']),None)
    for ref,(x,flip) in moves.items():
        name=next(n for n,r in oldmeta.items() if r.get('role')==stations[ref]['current_group'])
        case=scene[name];centre=case.BoundBox.Center;rot=A.Rotation(A.Vector(0,1,0),180 if flip else 0)
        target=A.Vector(x,centre.y,centre.z);tf=A.Placement(target-rot.multVec(centre),rot)
        case.Placement=tf*case.Placement;changed[name]=case
        for n,r in prior['recipes'].items():
            if not n.startswith('REV3Station:'+ref+'.'):continue
            q=tf.multVec(A.Vector(*r['point_mm']));d=rot.multVec(A.Vector(*r['departure_axis']));b=A.Vector(*r['bend_unit']);R=r['R_mm']
            if upper and ref in ('G_TAIL','P_REAR'):b=-b
            tip=q+d*(3+R)+b*R;rr=r['radius_mm']
            scene[n]=tube_prefix(list(q),list(d),rr,list(b),R,3)
            scene[n+':after9']=line_tube(list(tip),list(tip+b*9),rr)
            changed[n]=scene[n];changed[n+':after9']=scene[n+':after9']
            newrecipes[n]=dict(r,point_mm=list(q),departure_axis=list(d),bend_unit=list(b),after_grip_mm=[list(tip),list(tip+b*9)])
    # These previous positions are rejected by actual outer/body evidence.
    for n in list(scene):
        if n.startswith(('REV3:F_HY','REV3:F_HP','REV3:F_TY','REV3:Monitor5015')):scene.pop(n);meta.pop(n)
    realloc={'StructureReserve:'+x for x in ('BankArm-69_-1','BankArm-69_1','BankArm105_-1','BankArm105_1','UpperStrip1')}
    fixed={n:s for n,s in scene.items() if n not in realloc and not meta[n].get('role','').startswith('leg:')}
    reader=SavedShapes();outerfile=OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd'
    outer=reader.shape(outerfile,'TorsoEnvelope');assert outer.isValid()
    pins.update(reader.hashes)
    voxel=OUT/'n01-shared-space-atlas-voxels.npz';v=np.load(voxel,allow_pickle=False)['motion36']
    dims=np.array([337,209,173]);ids=np.flatnonzero(v);cloud=np.column_stack((ids//(dims[1]*dims[2]),ids//dims[2]%dims[1],ids%dims[2]))+np.array([-147,-104,-54])
    motion=cKDTree(cloud)
    for p in (priorfile,clockfile,voxel,Path(__file__)):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    result=dict(status='RUNNING_COUPLED_SIDE_BAY_PLAN',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,source_world_gate=priorfile.relative_to(ROOT).as_posix(),
        joint_station_moves={k:dict(centre_X_mm=x,departure_flip_about_Y=flip) for k,(x,flip) in moves.items()},
        station_profile_recipes=newrecipes,MAIN_cap_is_existing_source_subset=True,
        unchanged_pair_evidence_reused=True,base_completed_pairs=[],base_failures=[],base_outer=[],
        candidate_receipts=[],domains={},joint_allocation=None,errors=[],completed_base_parts=[],
        roots_mounts_tools_full123middles_USB_and_continuous_motion_still_open=True,
        sampled_motion_screen='Existing36pose union1mm voxels; conservative4.4162mm surface screen, NOT physical contact proof',
        factory100mm_is_delivery_assumption=True)
    if previous:
        assert previous['source_sha256']==pins,'Inputs changed; do not reuse prior pairs'
        result=previous
        result.setdefault('prior_attempts',[]).append(dict(seconds=result['worker_seconds'],errors=result['errors']))
        result['errors']=[]
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s whole macro cap, completed domain states retained')
    bounds={n:s.BoundBox for n,s in fixed.items()}
    def gap(s,n,t):
        if n==bus['name']:
            s=s.copy();s.Placement=bus['inverse']*s.Placement;return s.distToShape(bus['original'])[0]
        assert t.isValid(),n
        return s.distToShape(t)[0]
    def outer_ok(s):
        # All X section breaks included: conservative BOX capacity screen,
        # never a claim that bbox overlap itself is a physical collision.
        bb=s.BoundBox
        xs=[bb.XMin,bb.XMax]+[x for x in (-141.5,-112,-65,10,55,112,158,183.5) if bb.XMin<x<bb.XMax]
        points=np.array([[x,y,z] for x in xs for y in (bb.YMin,bb.YMax) for z in (bb.ZMin,bb.ZMax)])
        if not np.all(inside_ruled(points)):return False,'conservative_bbox_not_inside_source_sections'
        outside=s.cut(outer).Volume
        if outside>1e-5:return False,dict(actual_outside_volume_mm3=outside)
        distance=s.distToShape(outer.Shells[0])[0]
        return distance>=3.25-1e-5,dict(actual_outer_surface_gap_mm=distance)
    save();seen=set()
    try:
        # This gate rechecks ONLY the changed stations. Existing other module
        # failures are carried, not silently turned green by omitted pairs.
        for n,s in changed.items():
            if n in result['completed_base_parts']:continue
            gate();okay,why=outer_ok(s)
            if not okay:result['base_outer'].append(dict(part=n,evidence=why))
            for m,t in fixed.items():
                if n==m or station_group(n)==station_group(m):continue
                pair=tuple(sorted((n,m)))
                minimum=.2 if meta[n].get('kind')=='wire' and (meta[m].get('kind') in ('wire','actual_wire','proposal_wire') or meta[m].get('wire_owner')) else 1.25
                if pair in seen or not near(s.BoundBox,bounds[m],minimum):continue
                seen.add(pair);gate()
                if not t.Solids:continue # Carried curve-holds, no full-jacket claim.
                distance=gap(s,m,t);row=dict(a=n,b=m,gap_mm=distance,minimum_mm=minimum)
                result['base_completed_pairs'].append(row)
                if distance<minimum-1e-5:result['base_failures'].append(row)
            result['completed_base_parts'].append(n);save()
        # Source templates are identical SKUs but no interchangeable-geometry
        # assumption is used: each role gets its own actual casing and datums.
        extra=json.loads((OUT/'n01-all-extra-interface-contract.json').read_text())
        local={e['endpoint']:e for sec in extra['sections'] for e in sec['ends'] if e.get('local_point_mm') is not None}
        equivalent=False
        if upper:
            canonical=templates['F_HY'][1].copy();canonical.translate(-canonical.BoundBox.Center)
            nominal_datums=sorted((tuple(local['F_HY.'+s]['local_point_mm']),tuple(local['F_HY.'+s]['departure_axis'])) for s in ('in','out'))
            equivalence=[]
            for role in ('F_HP','F_TY'):
                source=templates[role][1].copy();source.translate(-source.BoundBox.Center)
                ab=canonical.cut(source).Volume;ba=source.cut(canonical).Volume
                datums=sorted((tuple(local[role+'.'+s]['local_point_mm']),tuple(local[role+'.'+s]['departure_axis'])) for s in ('in','out'))
                match=all(np.linalg.norm(np.array(a[0])-b[0])<1e-7 and np.linalg.norm(np.array(a[1])-b[1])<1e-7 for a,b in zip(nominal_datums,datums))
                equivalence.append(dict(role=role,both_valid=canonical.isValid() and source.isValid(),
                    source_difference_volume_mm3=[ab,ba],both_unordered_local_mouths_and_departures_equal=match))
            equivalent=all(r['both_valid'] and max(r['source_difference_volume_mm3'])<1e-8 and r['both_unordered_local_mouths_and_departures_equal'] for r in equivalence)
            result['three_template_equivalence']=dict(receipts=equivalence,planning_query_reuse_enabled=equivalent,
                source_identities_and_electrical_sides_not_merged=True)
        packages={}
        geometry_receipts={}
        def package(role,centre,orientation,bend):
            n,source,_=templates[role];rot=A.Rotation(A.Vector(0,1,0),-90) if orientation=='verticalZ' else A.Rotation()
            case=source.copy();case.Placement=A.Placement(A.Vector(*centre)-rot.multVec(source.BoundBox.Center),rot)*case.Placement
            parts={'case':case}
            for side in ('in','out'):
                e=local[role+'.'+side];q=A.Vector(*centre)+rot.multVec(A.Vector(*e['local_point_mm']));d=rot.multVec(A.Vector(*e['departure_axis']));b=A.Vector(*bend)
                end=q+d*21.4+b*12.4;tip=end+b*14
                parts[side+':factory_prefix']=tube_prefix(list(q),list(d),2,list(b),12.4,9)
                parts[side+':factory_land']=line_tube(list(end),list(tip),2)
                parts[side+':sleeve']=line_tube(list(tip-b*14),list(tip+b*6),2.4)
                parts[side+':custom']=line_tube(list(tip-b*8),list(tip+b*18),1.55)
            return parts
        def candidate(role,centre,orientation,bend=None):
            signature=(role,tuple(centre),orientation,tuple(bend) if bend else None)
            geometry_key=(tuple(centre),orientation,tuple(bend) if bend else None)
            received=next((r for r in result['candidate_receipts'] if
                (r['role'],tuple(r['centre_mm']),r['orientation'],tuple(r['bend_unit']) if r['bend_unit'] else None)==signature),None)
            if received and equivalent and role!='Monitor5015':geometry_receipts[geometry_key]=received
            if received and not received['status'].startswith('candidate_whole'):return
            gate();index=len(result['candidate_receipts']);key=received['key'] if received else role+':'+str(index)
            if role=='Monitor5015':
                _,s,_=templates[role];rot=A.Rotation(A.Vector(1,0,0),-90);s=s.copy()
                s.Placement=A.Placement(A.Vector(*centre)-rot.multVec(s.BoundBox.Center),rot)*s.Placement;parts={'case':s}
            else:parts=package(role,centre,orientation,bend)
            if received:
                packages[key]=parts;return # Reconstruct accepted domain only; NO repeated exact queries.
            row=dict(key=key,role=role,centre_mm=centre,orientation=orientation,bend_unit=bend,status='pending')
            cached=geometry_receipts.get(geometry_key) if equivalent and role!='Monitor5015' else None
            if cached:
                row.update(status=cached['status'],exact_geometry_query_reused_from=cached['key'],
                    same_both_mouth_geometry_proved=True,
                    canonical_part_label=cached.get('part'),canonical_evidence={k:v for k,v in cached.items() if k in ('evidence','gap_mm','neighbour','voxel_distance_mm')})
                if row['status'].startswith('candidate_whole'):
                    packages[key]=parts;result['domains'].setdefault(role,[]).append(key)
                result['candidate_receipts'].append(row);save();return
            for pn,s in parts.items():
                gate();okay,why=outer_ok(s)
                if not okay:row.update(status='outer_screen_reject',part=pn,evidence=why);break
                bb=s.BoundBox
                for name,t in fixed.items():
                    if not t.Solids or not near(bb,bounds[name],1.25):continue
                    gate();distance=gap(s,name,t)
                    otherwire=bool(meta[name].get('wire_owner')) or meta[name].get('kind') in ('wire','actual_wire','proposal_wire') or name.startswith(('End:','BankFullPrefix:','Factory:','CustomPrefix:')) or name in ('W043','W077','W078')
                    minimum=.2 if upper and pn!='case' and otherwire else 1.25
                    if distance<minimum-1e-5:
                        row.update(status='exact_static_gap_reject',part=pn,neighbour=name,gap_mm=distance,required_mm=minimum);break
                if row['status']!='pending':break
                vv,ff=s.tessellate(.6);vv=np.array([list(x) for x in vv]);pts=surface_samples(vv[np.array(ff,dtype=int)],2)
                distance=float(motion.query(pts,workers=1)[0].min())
                if distance<4.4162:
                    row.update(status='conservative_motion_surface_screen_reject',part=pn,voxel_distance_mm=distance);break
            if row['status']=='pending':
                row['status']='candidate_whole_two_tail_static_and_sampled_motion_screen_clear_not_selected'
                packages[key]=parts;result['domains'].setdefault(role,[]).append(key)
            result['candidate_receipts'].append(row);save()
            if equivalent and role!='Monitor5015':geometry_receipts[geometry_key]=row
        # Whole side-bottom topology, not another small shift of the rejected
        # vertical outboard cases. Vertical interstitial bays are compared in
        # the SAME common domain, not run as separate blind CAD variants.
        for role in ('F_HY','F_HP','F_TY'):
            if upper:
                for x,side,y,z in itertools.product((-70,-22,26,74),(-1,1),(72,80),(0,24,48,64)):
                    for bend in ([0,0,1],[0,0,-1],[0,-side,0],[0,-side/math.sqrt(2),1/math.sqrt(2)],[0,-side/math.sqrt(2),-1/math.sqrt(2)]):
                        candidate(role,[x,side*y,z],'horizontalX',bend)
                for side in (-1,1):
                    for x,y in itertools.product((-23,25,73) if side<0 else (-11,37,61),(68,72)):
                        candidate(role,[x,side*y,32],'verticalZ',[0,-side,0])
            else:
                for x,side,y,z in itertools.product((-72,-24,24,72),(-1,1),(60,72),(-32,-26)):
                    for bend in ([0,0,1],[0,-side,0]):candidate(role,[x,side*y,z],'horizontalX',bend)
                for x,side,y in itertools.product((-24,24,76),(-1,1),(68,70)):
                    candidate(role,[x,side*y,32],'verticalZ',[0,-side,0])
            print('Received shared domain',role,len(result['domains'].get(role,[])),flush=True)
        for x,side,y in itertools.product((-40,8,48,96),(-1,1),(60,72)):
            candidate('Monitor5015',[x,side*y,-30],'upright')
        # CSP/actual pair distances select ONE simultaneous source assignment.
        def compatible(a,b):
            for s in packages[a].values():
                for t in packages[b].values():
                    if near(s.BoundBox,t.BoundBox,1.25) and s.distToShape(t)[0]<1.25-1e-5:return False
            return True
        roles=sorted(('F_HY','F_HP','F_TY','Monitor5015'),key=lambda r:len(result['domains'].get(r,[])))
        def solve(index,chosen):
            gate()
            if index==len(roles):return dict(chosen)
            role=roles[index]
            for key in result['domains'].get(role,[]):
                if all(compatible(key,other) for other in chosen.values()):
                    answer=solve(index+1,{**chosen,role:key})
                    if answer:return answer
            return None
        result['joint_allocation']=solve(0,{})
        result['status']='COUPLED_SIDE_DOMAINS_RECEIVED_NOT_N01'
    except Exception as e:
        result['status']='PARTIAL_COUPLED_SIDE_DOMAINS';result['errors'].append(repr(e))
    save();print(json.dumps(dict(status=result['status'],domain_sizes={k:len(v) for k,v in result['domains'].items()},
        base_failures=len(result['base_failures']),base_outer=len(result['base_outer']),
        joint_allocation=result['joint_allocation'],errors=result['errors'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
