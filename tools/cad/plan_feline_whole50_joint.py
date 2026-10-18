"""One source-owned50-node proposal:20WAGO,4S1,24bankends,2clamp pairs.

No frozen obsolete bank bends. All source first9 and TE bodies retained;
actual clamp parents qualified separately. Numeric proposals never award N01.
"""
import json
import math
import sys
import time
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import cKDTree
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_flat_station_templates import build,compact,compatible,box_gap,box_points,to_box,self_wire_gap,pier_supported,shared_rail_bounds
from feline_flat_s1_templates import candidates
from feline_bank_anchor_templates import bank_candidates,anchor_candidates


def main():
    tick=time.monotonic();modulejoint='--module-joint' in sys.argv
    dest=OUT/('n01-whole51-joint-proposal.json' if modulejoint else 'n01-whole50-joint-proposal.json');previous=None
    if dest.exists():
        assert '--receive-partial' in sys.argv
        previous=json.loads(dest.read_text());assert previous['status']=='PARTIAL_WHOLE50_DOMAINS'
        for n,h in previous['source_sha256'].items():assert sha(ROOT/n)==h,n
    proofpath=OUT/('n01-flat20-field-modulejoint.json' if modulejoint else 'n01-flat20-field-bankjoint.json');proof=json.loads(proofpath.read_text())
    assert proof['stage']=='complete' and not proof['errors'] and len(proof['bank_joint_full_source_ports'])==24
    for n,h in proof['source_sha256'].items():assert sha(ROOT/n)==h,n
    planfile=OUT/'n01-flat-station-architecture.json';plan=json.loads(planfile.read_text())
    oldfile=OUT/('n01-whole50-joint-proposal.json' if modulejoint else 'n01-common-low-closure-domains.json');old=json.loads(oldfile.read_text())
    fieldfile=ROOT/proof['field'];assert sha(fieldfile)==proof['field_sha256']
    field=np.load(fieldfile,allow_pickle=False);axes=[field[k] for k in ('x','y','z')]
    monotone=False
    if modulejoint:
        priorfieldproof=json.loads((OUT/'n01-flat20-field-bankjoint.json').read_text())
        priorfield=np.load(ROOT/priorfieldproof['field'],allow_pickle=False)
        assert set(priorfield.files)==set(field.files)
        for k in field.files:
            if k in ('material_distance','reservation_distance','curve_hold_distance'):assert np.all(field[k]>=priorfield[k]-1e-6),k
            else:assert np.array_equal(field[k],priorfield[k]),k
        removed=set(priorfieldproof['old_station_parts_retired'])^set(proof['old_station_parts_retired'])
        assert removed=={'F_PWM:'+s for s in ('case','in_first_bend','in_after_turn_grip','out_first_bend','out_after_turn_grip')}
        monotone=True
    grid=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1);queries=grid.reshape(-1,3)
    fields={k:RegularGridInterpolator(axes,field[k+'_distance'],bounds_error=False,fill_value=0)
        for k in ('material','reservation','curve_hold','motion36','outer')}
    for k in ('P_SYS','W043','S1','BankTerm','P0Rail'):
        dd=cKDTree(field[k+'_context']).query(queries,workers=1)[0].reshape(grid.shape[:3])
        fields[k]=RegularGridInterpolator(axes,dd,bounds_error=False,fill_value=0)
    inside=RegularGridInterpolator(axes,field['inside'].astype(float),bounds_error=False,fill_value=0)
    service=RegularGridInterpolator(axes,field['service'].astype(float),method='nearest',bounds_error=False,fill_value=1)
    source_rows={r['id']:r for r in proof['bank_joint_full_source_ports']}
    bank_others={r['id']:cKDTree(np.vstack([field[x['terminal_context_key']] for x in source_rows.values() if x['id']!=r['id']])) for r in source_rows.values()}
    bank_own={r['id']:cKDTree(field[r['terminal_context_key']]) for r in source_rows.values()}
    screen={k:(1 if k=='outer' else 3.35 if k=='curve_hold' else .2) for k in fields}
    rails=shared_rail_bounds();domains={}
    result=dict(status='RUNNING_WHOLE50_JOINT',selected=False,N01_complete=False,physical_pass=False,
        whole_joint_nodes=51 if modulejoint else 50,source_sha256={**proof['source_sha256'],**{p.relative_to(ROOT).as_posix():sha(p) for p in
            (proofpath,planfile,oldfile,fieldfile,Path(__file__),ROOT/'tools/cad/feline_flat_station_templates.py',
                ROOT/'tools/cad/feline_flat_s1_templates.py',ROOT/'tools/cad/feline_bank_anchor_templates.py')}},
        source_bank_first9_and_TE_unchanged=True,bank_R47_sources_not_overwritten=True,
        all24_bank_caps_bands_full_heads_visible=True,numeric_screens_mm=screen,
        all_domains_rechecked_against_changed_owner_field=True,
        full_root_connections_retained_cuffs_MAIN_bank_boards_tools_STILL_REQUIRED=True,
        actual_source_case_fit_and_band_stock_NOT_qualified=True,
        complete123portions246ends_corridors_NOT_qualified=True,
        domains={},receipts=[],joint_assignment=None,errors=[])
    if monotone:result.update(fixed_source_fields_only_relaxed_by_whole_pigtail_variable=True,
        all_other_field_arrays_exactly_identical=True,
        unchanged50_received_world_domains_can_be_reused_NOT_frozen=True,
        F_PWM_selected_fuse_0242_100UAT1_and_all5_wire_shapes_preserved=True,
        F_PWM_new_before_arc9_strain_relief_sites_design_change=True)
    if modulejoint:
        for name in ('feline_flat_station_templates.py','feline_flat_s1_templates.py','feline_bank_anchor_templates.py'):
            rel='tools/cad/'+name;assert sha(ROOT/rel)==old['source_sha256'][rel],rel
    complete={r['ref'] for r in previous['receipts']} if previous else set()
    if previous:
        result['receipts']=previous['receipts'];result['previous_partial_seconds']=previous['worker_seconds']
        result['resumed_completed_sources_without_queries']=sorted(complete)
        for station in plan['stations']:
            ref=station['ref']
            if ref not in complete:continue
            domains[ref]=[]
            for r in previous['domains'][ref]:
                m=build(station,r['family'],r['side'],r['departure_X'],r['centre_mm'][0],r.get('centre_y_override_mm'),r.get('bend_mode','OUTWARD_CONCENTRIC'),r.get('closure_mode','AUTO'))
                m['numeric_score']=r['numeric_score'];domains[ref].append(m)
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        result['domains']={n:[compact(m) for m in rows] for n,rows in domains.items()}
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s whole50 budget; completed source domains retained')
    def score(m):
        p=m['points'];rr=m['radii'];tt=m['types'];best=1e6;label='none'
        if inside(p).min()<.999:return -1e6,'outside'
        for k,interp in fields.items():
            mask=np.ones(len(p),bool)
            if m.get('fixed_identity'):
                if k=='P_SYS':continue
                if k=='W043':mask=(tt!=0)&(tt!=4)
            if k=='S1' and m.get('source_ring'):mask=tt!=9
            if k=='BankTerm' and m.get('bank_source'):continue
            if k=='P0Rail' and m.get('anchor_source'):continue #Actual own-parent test below, not deletion.
            if not mask.any():continue
            val=float(np.min(interp(p[mask])-rr[mask]-screen[k]))
            if val<best:best=val;label=k
        if m.get('bank_source'):
            identity=m['source_endpoint'];values=bank_others[identity].query(p,workers=1)[0]-rr-.2
            val=float(values.min())
            if val<best:best=val;label='other_TE_terminal'
            # Only declared own entry throat is a mate. All other points see
            # the entire actual own terminal, including return toward it.
            axial=(p-np.array(m['point_mm']))@np.array(m['departure_axis']);mask=axial>3.35
            if mask.any():
                val=float(np.min(bank_own[identity].query(p[mask],workers=1)[0]-rr[mask]-.2))
                if val<best:best=val;label='own_TE_outside_entry_throat'
        if service(p).max()>.5 and best>=0:best=-.01;label='ATO_access'
        if not m.get('anchor_source'):
            nonroot=tt!=3
            for rail in rails:
                val=float(np.min(to_box(p[nonroot],rail)-rr[nonroot]-.2))
                if val<best:best=val;label='common_low_rail'
        return best,label
    save()
    try:
        for station in plan['stations']:
            gate();ref=station['ref'];proposals=[];seen=set()
            if ref in complete:continue
            def add(m):
                key=(m['family'],m['side'],m['departure_X'],tuple(m['centre_mm']),m['bend_mode'],m['closure_mode'])
                if key not in seen:seen.add(key);proposals.append(m)
            for r in old['domains'][ref]:
                m=build(station,r['family'],r['side'],r['departure_X'],r['centre_mm'][0],r.get('centre_y_override_mm'),r.get('bend_mode','OUTWARD_CONCENTRIC'),r.get('closure_mode','AUTO'))
                if monotone:m['numeric_score']=r['numeric_score'];m['reused_monotone_world_domain']=True
                add(m)
            if ref in ('P_REAR','G1','P_FRONT'):
                abs_y=27-station['flat_dimensions_pitch_departure_thickness_mm'][0]/2-1.25
                for side in (-1,1):
                    for departure in (-1,1):
                        for y in (0,abs_y,19.5):
                            for mode in ('OUTWARD_CONCENTRIC','UP_TYPED_RADII','INWARD_UP_TYPED_RADII'):
                                for x in range(-112,149,12):add(build(station,'inner',side,departure,x,side*y,mode,'SIDE'))
            elif modulejoint and ref!='P_SYS':
                for departure in (-1,1):
                    for x in range(-112,149,12):add(build(station,'inner',-1,departure,x,-19.5,'OUTWARD_CONCENTRIC','SIDE'))
            accepted=[];rejected={}
            for m in proposals:
                gate()
                if m.get('reused_monotone_world_domain'):accepted.append(m);continue
                if self_wire_gap(m)<-1e-6:rejected['intrinsic_gap']=rejected.get('intrinsic_gap',0)+1;continue
                if not pier_supported(m):continue
                val,why=score(m)
                if val>=0:m['numeric_score']=val;accepted.append(m)
                else:rejected[why]=rejected.get(why,0)+1
            accepted.sort(key=lambda m:-m['numeric_score']);domains[ref]=accepted
            result['receipts'].append(dict(ref=ref,tested=len(proposals),received=len(accepted),rejected=rejected));save()
            print(ref,'whole50 domains',len(accepted),flush=True)
        groups,pins=candidates();result['source_sha256'].update(pins)
        groups.update(bank_candidates(proof))
        parentreceipts=previous.get('actual_anchor_parent_receipts') if previous else old.get('actual_anchor_parent_receipts') if modulejoint else None
        anchors,mates,pins=anchor_candidates(parentreceipts);result['source_sha256'].update(pins)
        result['actual_anchor_parent_receipts']=mates;groups.update(anchors)
        if modulejoint:
            from feline_pwm_pigtail_templates import candidates as pwm_candidates
            extra,pins=pwm_candidates();groups.update(extra);result['source_sha256'].update(pins)
        for ref,proposals in groups.items():
            if ref in complete:
                def key(r):
                    if r.get('f_pwm_source'):return tuple(r['centre_mm']),tuple(r['head_choices'])
                    if r.get('bank_source'):return r['bend_clock_degrees'],r['complete_band_head_degrees']
                    if r.get('anchor_source'):return r['axis_X_mm']
                    return r['clock_target_degrees'],r['first_mm'],r['bend_degrees']
                bykey={key(m):m for m in proposals};domains[ref]=[]
                for r in previous['domains'][ref]:
                    m=bykey[key(r)];m['numeric_score']=r['numeric_score'];domains[ref].append(m)
                continue
            if monotone and ref in old['domains']:
                def oldkey(r):
                    if r.get('bank_source'):return r['bend_clock_degrees'],r['complete_band_head_degrees']
                    if r.get('anchor_source'):return r['axis_X_mm']
                    return r['clock_target_degrees'],r['first_mm'],r['bend_degrees']
                bykey={oldkey(m):m for m in proposals};domains[ref]=[]
                for r in old['domains'][ref]:
                    m=bykey[oldkey(r)];m['numeric_score']=r['numeric_score'];m['reused_monotone_world_domain']=True;domains[ref].append(m)
                result['receipts'].append(dict(ref=ref,tested=0,received=len(domains[ref]),reused_by_field_monotonicity=True));save()
                continue
            gate();accepted=[];rejected={}
            for m in proposals:
                gate();val,why=score(m)
                if val>=0:m['numeric_score']=val;accepted.append(m)
                else:rejected[why]=rejected.get(why,0)+1
            accepted.sort(key=lambda m:-m['numeric_score']);domains[ref]=accepted
            result['receipts'].append(dict(ref=ref,tested=len(proposals),received=len(accepted),rejected=rejected));save()
            print(ref,'whole50 domains',len(accepted),flush=True)
        assert len(domains)==(51 if modulejoint else 50)
        result['empty_domains']=[n for n,v in domains.items() if not v]
        if result['empty_domains']:
            result['status']='WHOLE50_REQUIRED_DOMAIN_EMPTY_NOT_GLOBAL_INFEASIBILITY';save();return
        trees={};memo={};visited=0
        def pair(a,i,b,j):
            key=(a,i,b,j) if a<b else (b,j,a,i)
            if key in memo:return memo[key]
            aa,bb=domains[a][i],domains[b][j]
            if aa.get('anchor_source') and bb.get('anchor_source'):
                fore=aa if a=='Anchor:Fore' else bb;rear=bb if b=='Anchor:Rear' else aa
                value=rear['axis_X_mm']-fore['axis_X_mm']>=90
            elif not any(x.get('source_ring') or x.get('bank_source') or x.get('anchor_source') or x.get('f_pwm_source') for x in (aa,bb)):
                value=compatible(aa,bb)
            elif box_gap(aa['bounds'],bb['bounds'])>=1.25:value=True
            else:
                value=True
                # Exact filled source-case envelopes cannot hide a kit
                # surface inside their interiors. Roots may receive named
                # anchor bores/washer seats, not purchased-body deletion.
                for group,other in ((aa,bb),(bb,aa)):
                    for box in other['boxes']:
                        if group.get('anchor_source') and box['kind']==3:continue
                        gap=float(np.min(to_box(group['points'],box['bounds'])-group['radii']))
                        if gap<1.25-1e-5:value=False;break
                    if not value:break
                if value:
                    maska=aa['types']!=3 if bb.get('anchor_source') else np.ones(len(aa['points']),bool)
                    maskb=bb['types']!=3 if aa.get('anchor_source') else np.ones(len(bb['points']),bool)
                    cachekey=(id(bb),bool(aa.get('anchor_source')))
                    if cachekey not in trees:trees[cachekey]=(cKDTree(bb['points'][maskb]),bb['radii'][maskb],bb['types'][maskb])
                    tree,radii,types=trees[cachekey];g,ix=tree.query(aa['points'][maska],workers=1)
                    req=np.where((aa['types'][maska]==1)&(types[ix]==1),.2,1.25)
                    value=float(np.min(g-aa['radii'][maska]-radii[ix]-req))>=-1e-5
            memo[key]=value;return value
        trace=[]
        def solve(chosen,remaining):
            nonlocal visited
            gate();visited+=1
            if visited>10000:raise TimeoutError('10000 whole50 nodes; retain domains')
            if not remaining:return chosen
            viable={n:[i for i in rows if all(pair(n,i,a,j) for a,j in chosen.items())] for n,rows in remaining.items()}
            empty=[n for n,v in viable.items() if not v]
            if empty:
                if len(trace)<20:trace.append(dict(chosen=chosen,empty=empty))
                return None
            n=min(viable,key=lambda n:len(viable[n]));other={k:v for k,v in viable.items() if k!=n}
            for i in viable[n]:
                found=solve({**chosen,n:i},other)
                if found:return found
            return None
        assignment=solve({}, {n:list(range(len(v))) for n,v in domains.items()})
        result.update(joint_assignment=assignment,search_nodes=visited,numeric_mutual_pairs=len(memo),first_named_dead_ends=trace)
        if assignment:
            result['chosen_templates']={n:compact(domains[n][i]) for n,i in assignment.items()}
            result['status']='WHOLE50_NUMERIC_PROPOSAL_REQUIRES_EXACT_MATES_ROOTS_AND_FULL_N01'
        else:result['status']='WHOLE50_BOUNDED_FAMILY_HAS_NO_JOINT_ASSIGNMENT'
    except Exception as e:result['errors'].append(repr(e));result['status']='PARTIAL_WHOLE50_DOMAINS'
    save();print(json.dumps({k:result[k] for k in ('status','worker_seconds','joint_assignment','errors')}),flush=True)


def source_saddles_prefix_diagnosis():
    """Locate mandatory-prefix failure before another geometry family."""
    from feline_s1_saddle_layout import load_sources,fan,world_score
    tick=time.monotonic()
    core,packet,_,fields,inside,service,pins=load_sources()
    rows=[]
    for pid,pose in enumerate(core['pose_domains']):
        ends=[]
        for recipe in packet['recipes']:
            m=fan(packet,pose,recipe,pid,0,0)
            # First12mm is invariant across all32 bend/head choices.
            prefix={**m,'points':m['points'][:13],'radii':m['radii'][:13]}
            score,label=world_score(prefix,fields,inside,service)
            p=prefix['points'];rr=prefix['radii']
            if label in fields:
                req=1 if label=='outer' else 3.35 if label=='curve_hold' else .2
                ix=int(np.argmin(fields[label](p)-rr-req))
            elif label=='outside':ix=int(np.argmin(inside(p)))
            else:ix=0
            ends.append(dict(ref=recipe['ref'],margin_mm=score,layer=label,witness_point_mm=p[ix].tolist(),
                             along_first_mm=float(ix),point_mm=m['point_mm'],departure_axis=m['departure_axis']))
        rows.append(dict(core_pose_id=pid,pose=pose,prefixes=ends,all_prefixes_numeric_clear=all(x['margin_mm']>=0 for x in ends),
                         minimum_margin_mm=min(x['margin_mm'] for x in ends)))
    result=dict(status='SOURCE_MANDATORY_PREFIX_DIAGNOSIS_NOT_COLLISION_PROOF',selected=False,N01_complete=False,
                source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
                worker_seconds=round(time.monotonic()-tick,3),rows=rows,
                all_prefix_clear_pose_ids=[r['core_pose_id'] for r in rows if r['all_prefixes_numeric_clear']],
                best_prefix_pose=max(rows,key=lambda r:r['minimum_margin_mm']),
                plan_change_requires_named_witness_before_new_geometry=True)
    (OUT/'n01-source-saddles-whole-joint.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('worker_seconds','all_prefix_clear_pose_ids','best_prefix_pose')}),flush=True)


def source_saddles_complete_orientations():
    """Remaining16 rigid orientations, not smaller margins or scalar retries.

    Old8 orientations/2800poses/34fullfan receipts retained. Test mandatory
    four jacket lands first, before costly core clouds. Resume by cursor.
    """
    import hashlib
    import inspect
    import itertools
    import FreeCAD as A
    from feline_s1_saddle_layout import load_sources,pose_points,fan,world_score
    from plan_feline_joint_fore_domains import rotations
    tick=time.monotonic()
    core,packet,sourcepoints,fields,inside,service,pins=load_sources()
    dest=OUT/'n01-s1-saddle-layout.json';result=json.loads(dest.read_text())
    assert result['source_sha256']==pins
    assert result['status'] in ('S1_SADDLE_DOMAINS_RECEIVED','PARTIAL_S1_COMPLETE_ORIENTATIONS')
    algorithm=hashlib.sha256(inspect.getsource(source_saddles_complete_orientations).encode()).hexdigest()
    if 'extension_algorithm_sha256' in result:assert result['extension_algorithm_sha256']==algorithm
    result['extension_algorithm_sha256']=algorithm
    result['extension_coordinator_sha256']=sha(Path(__file__))
    result.setdefault('extension_attempts',0);result.setdefault('extension_rejected',{})
    result.setdefault('extension_core_proposals',[]);result.setdefault('extension_previous_worker_seconds',[])
    if 'extension_worker_seconds' in result:result['extension_previous_worker_seconds'].append(result['extension_worker_seconds'])
    oldrot=[]
    for yaw,roll in itertools.product((0,90,180,270),(0,90)):
        rr=A.Rotation(A.Vector(0,0,1),yaw)*A.Rotation(A.Vector(1,0,0),roll)
        oldrot.append(np.array([list(rr.multVec(A.Vector(*v))) for v in np.eye(3)]).T)
    missing=[r for r in rotations() if not any(np.allclose(r,o,atol=1e-10) for o in oldrot)]
    assert len(missing)==16
    # Invariant four first12 lands from the actual purchased ring mouths.
    local=np.vstack([np.linspace(np.array(r['point_mm']),np.array(r['point_mm'])+12*np.array(r['departure_axis']),13)
                     for r in packet['recipes']])
    source_group=dict(radii=np.zeros(len(sourcepoints)))
    jacket_group=dict(radii=np.full(len(local),2.1))
    skip=result['extension_attempts']
    def save():
        result['extension_worker_seconds']=round(time.monotonic()-tick,3)
        result['all_four_domain_poses']=[r['core_pose_id'] for r in result['poses'] if r['all_four_nonempty']]
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    result['status']='RUNNING_S1_COMPLETE_ORIENTATIONS';save()
    for index,(x,y,z,ri) in enumerate(itertools.product(range(-108,109,24),range(-36,37,12),(-24,0,24,48,72),range(16))):
        if index<skip:continue
        if time.monotonic()-tick>120:
            result['status']='PARTIAL_S1_COMPLETE_ORIENTATIONS';break
        pose=dict(centre_mm=[x,y,z],rotation_rows=missing[ri].tolist(),extension_rotation_index=ri)
        jacket_group['points']=pose_points(local,packet,pose)
        val,why=world_score(jacket_group,fields,inside,service)
        if val>=0:
            source_group['points']=pose_points(sourcepoints,packet,pose)
            val,why=world_score(source_group,fields,inside,service)
        result['extension_attempts']+=1
        if val<0:
            result['extension_rejected'][why]=result['extension_rejected'].get(why,0)+1
        else:
            pid=34+len(result['extension_core_proposals'])
            pose['numeric_margin_mm']=val
            result['extension_core_proposals'].append(dict(core_pose_id=pid,pose=pose))
            rows={}
            for recipe in packet['recipes']:
                accepted=[]
                for bend,head in itertools.product(range(0,360,45),(0,90,180,270)):
                    m=fan(packet,pose,recipe,pid,bend,head);score,reason=world_score(m,fields,inside,service)
                    if score>=0:m['numeric_score']=score;accepted.append(compact(m))
                rows[recipe['ref']]=sorted(accepted,key=lambda m:-m['numeric_score'])
            result['poses'].append(dict(core_pose_id=pid,pose=pose,fan_domains=rows,
                                       all_four_nonempty=all(rows.values()),extended_orientation=True))
            save();print('Extended source pose',pid,{n:len(v) for n,v in rows.items()},flush=True)
        if result['extension_attempts']%100==0:save()
    else:result['status']='S1_COMPLETE_ORIENTATIONS_RECEIVED'
    save()
    print(json.dumps(dict(status=result['status'],seconds=result['extension_worker_seconds'],
                         attempts=result['extension_attempts'],new_core_proposals=len(result['extension_core_proposals']),
                         all_four_domain_poses=result['all_four_domain_poses'])),flush=True)


def source_saddles_limiting_fan():
    """One named missing fan in the best three-fan whole-source pose."""
    from feline_s1_saddle_layout import load_sources,fan,world_score
    tick=time.monotonic();_,packet,_,fields,inside,service,pins=load_sources()
    layout=json.loads((OUT/'n01-s1-saddle-layout.json').read_text())
    assert layout['status']=='S1_COMPLETE_ORIENTATIONS_RECEIVED'
    eligible=[r for r in layout['poses'] if sum(bool(v) for v in r['fan_domains'].values())==3]
    assert eligible
    def prefix_margin(row):
        missing=next(n for n,v in row['fan_domains'].items() if not v)
        recipe=next(r for r in packet['recipes'] if r['ref']==missing)
        m=fan(packet,row['pose'],recipe,row['core_pose_id'],0,0)
        return world_score({**m,'points':m['points'][:13],'radii':m['radii'][:13]},fields,inside,service)[0]
    # Prefer a pose whose invariant first12 is clear; a known outside prefix
    # cannot diagnose which material blocks the subsequent bend/strain relief.
    pose=max(eligible,key=prefix_margin)
    missing=next(n for n,v in pose['fan_domains'].items() if not v)
    recipe=next(r for r in packet['recipes'] if r['ref']==missing)
    attempts=[]
    import itertools
    for bend,head in itertools.product(range(0,360,45),(0,90,180,270)):
        m=fan(packet,pose['pose'],recipe,pose['core_pose_id'],bend,head)
        val,why=world_score(m,fields,inside,service);p,rr=m['points'],m['radii']
        if why in fields:
            req=1 if why=='outer' else 3.35 if why=='curve_hold' else .2
            ix=int(np.argmin(fields[why](p)-rr-req))
        elif why=='outside':ix=int(np.argmin(inside(p)))
        else:ix=0
        category='wire' if ix<65 else 'saddle' if ix<371 else 'band' if ix<629 else 'head'
        attempts.append(dict(template=compact(m),numeric_margin_mm=val,layer=why,
                             witness_point_mm=p[ix].tolist(),radius_mm=float(rr[ix]),component=category))
    best=max(attempts,key=lambda r:r['numeric_margin_mm'])
    dest=OUT/'n01-source-saddles-whole-joint.json';result=json.loads(dest.read_text())
    result['limiting_fan_diagnosis']=dict(core_pose_id=pose['core_pose_id'],pose=pose['pose'],missing_ref=missing,
        all_other_three_have_domains=True,best_of32=best,worker_seconds=round(time.monotonic()-tick,3),
        geometry_changed=False,not_actual_collision_proof=True)
    result['source_sha256'].update(pins);result['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result['limiting_fan_diagnosis']),flush=True)


def source_saddles_exact_terminal_witness():
    """Actual TE metal vs full S1 wire, not a sampled field/bbox verdict."""
    import hashlib
    import zipfile
    import FreeCAD as A
    import Part
    from check_feline_shared_space import tube_prefix
    from feline_solid_distance import distance
    tick=time.monotonic()
    dest=OUT/'n01-source-saddles-whole-joint.json';result=json.loads(dest.read_text())
    witness=result['limiting_fan_diagnosis'];m=witness['best_of32']['template']
    proofpath=OUT/'n01-flat20-field-modulejoint.json';proof=json.loads(proofpath.read_text())
    materialpath=OUT/'n01-full-material-scene.json';material=json.loads(materialpath.read_text())
    bundle=ROOT/material['bundle'];assert sha(bundle)==material['bundle_sha256']
    records={r['name']:r for r in material['parts']}
    terminals={}
    with zipfile.ZipFile(bundle) as z:
        for name in proof['bank_terminal_context_parts']:
            row=records[name];blob=z.read(row['entry']);assert hashlib.sha256(blob).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(blob.decode());assert s.isValid() and len(s.Solids)==1,name
            terminals[name]=s
    # Verify terminal geometry placement against pinned source context points.
    # Full cached source corners/centre match the field-owned terminal axes.
    f=np.load(ROOT/proof['field'],allow_pickle=False)
    for r in proof['bank_joint_full_source_ports']:
        p=f[r['terminal_context_key']];bb=terminals[r['terminal_name']].BoundBox
        bounds=np.array([[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]])
        assert np.allclose(bounds,np.array([p.min(0),p.max(0)]),atol=1e-4),r['terminal_name']
    q,d,b=(A.Vector(*m[k]) for k in ('point_mm','departure_axis','bend_unit'))
    wire=tube_prefix(list(q),list(d),m['radius_mm'],list(b),m['R_mm'],m['first_mm'])
    end=q+(m['first_mm']+m['R_mm'])*d+m['R_mm']*b
    wire=wire.fuse(Part.makeCylinder(m['radius_mm'],9,end,b))
    assert wire.isValid() and len(wire.Solids)==1
    receipts=[]
    for name,s in terminals.items():
        gap=distance(wire,s)
        if gap>=1.25-1e-6:continue
        volume=None
        if gap<=1e-6:
            common=wire.common(s);assert common.isValid()
            volume=common.Volume
        receipts.append(dict(wire=m['ref'],terminal=name,exact_gap_mm=gap,
                             required_mm=1.25,positive_common_mm3=volume))
    result['actual_terminal_witness']=dict(core_pose_id=witness['core_pose_id'],template=m,
        checked_terminal_count=24,failures=receipts,worker_seconds=round(time.monotonic()-tick,3),
        source_context_placements_verified=True,wire_valid=True,geometry_changed=False,
        N01_complete=False,physical_pass=False)
    result['source_sha256'].update({p.relative_to(ROOT).as_posix():sha(p) for p in
                                   (proofpath,materialpath,bundle,Path(__file__))})
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result['actual_terminal_witness']),flush=True)


def source_outboard_terminal_gallery():
    """Allocate the complete S1 terminal plane outside fixed TE metal.

    Plane comes from actual TE bound +full5.3 tie/saddle+1.25air, not a guessed
    per-wire offset. Preserve all10source parts and intrinsic ring pinwheel.
    Exact changed core/P0/bank pairs precede any carrier detail.
    """
    import hashlib
    import itertools
    import zipfile
    import FreeCAD as A
    import Part
    from feline_s1_saddle_layout import load_sources,fan,world_score,source_core
    from feline_solid_distance import distance
    tick=time.monotonic();core,packet,sourcepoints,fields,inside,service,pins=load_sources()
    dest=OUT/'n01-source-saddles-whole-joint.json';result=json.loads(dest.read_text())
    witness=result['actual_terminal_witness'];assert witness['failures']
    layout=json.loads((OUT/'n01-s1-saddle-layout.json').read_text())
    parent=next(r for r in layout['poses'] if r['core_pose_id']==witness['core_pose_id'])
    pose=dict(parent['pose']);pose['centre_mm']=list(pose['centre_mm'])
    materialpath=OUT/'n01-full-material-scene.json';material=json.loads(materialpath.read_text())
    bundle=ROOT/material['bundle'];assert sha(bundle)==material['bundle_sha256']
    records={r['name']:r for r in material['parts']}
    proof=json.loads((OUT/'n01-flat20-field-modulejoint.json').read_text())
    datum=json.loads((OUT/'n01-s1-current-source-datums.json').read_text())
    needed=set(proof['bank_terminal_context_parts'])|{'Ref_Material_P0_Side'+s+'22_0_0' for s in ('Left','Right')}
    fore_outboard='--source-fore-outboard-core' in sys.argv
    fore_axial='--source-fore-axial-budget' in sys.argv or fore_outboard
    rear_bay='--source-rear-bay-budget' in sys.argv or fore_axial
    key_up='--source-key-up-budget' in sys.argv or rear_bay
    if key_up:needed|={n for n,r in records.items() if r.get('role')=='P0_or_battery' and 'Battery' in n}
    if fore_axial:needed|={n for n,r in records.items() if r.get('role')=='P0_or_battery'}
    needed|={r['name'] for r in datum['source_parts']};shapes={}
    with zipfile.ZipFile(bundle) as z:
        for n in needed:
            row=records[n];blob=z.read(row['entry']);assert hashlib.sha256(blob).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(blob.decode());assert s.isValid() and s.Solids,n
            shapes[n]=s
    if fore_axial:
        from plan_feline_central_pi_wedge import packed
        forefile=OUT/'n01-fore-topology.json';_,foreparts,forerecords=packed(forefile)
        assert foreparts['ForeFHAC:case'].isValid()
    normal_offset=witness['template']['point_mm'][1]-pose['centre_mm'][1]
    # Outer tangent plane common to all24actual TE terminal bounding extents.
    # This is a valid separating-plane bound, not a claimed contact from bbox.
    terminal_min_y=min(shapes[n].BoundBox.YMin for n in proof['bank_terminal_context_parts'])
    qy=terminal_min_y-5.3-1.25
    pose['centre_mm'][1]=qy-normal_offset
    if key_up:
        # Actual upright source case is24X42Y37Z, not42X24Y37. Turn the
        # whole source90about its key axis to put24mm across the bank's
        # central27.74mm admissible case corridor (2*(15.12-1.25)).
        pose=dict(centre_mm=[60,0,0],rotation_rows=[[0,1,0],[1,0,0],[0,0,-1]])
    if fore_axial:
        c=2**-.5
        # Key points+X under F_PI, whole source case stays ahead of the P0
        # plate. Rotate its transverse plane45degrees to allocate all4fans
        # between the true floor and fore body, not one vertical exit.
        pose=dict(centre_mm=[-110,0,0],rotation_rows=[[0,0,-1],[c,c,0],[c,-c,0]])
    if fore_outboard:
        pose=dict(centre_mm=[-99.3,-57.55,0],rotation_rows=[[c,c,0],[0,0,-1],[-c,c,0]])
    body=shapes['Ref_Material_current_S1_body_CP2_0_0']
    rr=A.Rotation(*packet['rotation_quaternion'])
    tf=A.Placement(A.Vector(*packet['centre_mm'])-rr.multVec(body.BoundBox.Center),rr)
    m=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(m,f'A{i+1}{j+1}',pose['rotation_rows'][i][j])
    rot=A.Rotation(m);outer=A.Placement(A.Vector(*pose['centre_mm'])-rot.multVec(A.Vector(*packet['centre_mm'])),rot)
    moved={}
    for row in datum['source_parts']:
        n=row['name'];s=shapes[n].copy();s.Placement=outer*tf*s.Placement;moved[n]=s
    recipes={r['ref']:r for r in packet['recipes']}
    for receipt in datum['receipts']:
        n=receipt['matching_nominal_source_planes'][0]['part']
        number=int(n.split('_ring_')[1].split('_')[0]);screw=shapes[f'Ref_Material_current_S1_screw_{number}_0_0']
        qold,dold=(A.Vector(*receipt[k]) for k in ('source_point_mm','source_departure'))
        eye=A.Vector(screw.BoundBox.Center.x,qold.y,screw.BoundBox.Center.z)
        target=rr.inverted().multVec(A.Vector(*recipes[receipt['endpoint']]['departure_axis']))
        cr=A.Rotation(A.Vector(0,1,0),math.degrees(math.atan2(dold.z,dold.x)-math.atan2(target.z,target.x)))
        clock=A.Placement(eye-cr.multVec(eye),cr)
        s=shapes[n].copy();s.Placement=outer*tf*clock*s.Placement;moved[n]=s
    if key_up:
        battery_names=[n for n in needed if records[n].get('role')=='P0_or_battery' and 'Battery' in n]
        battery_top=max(shapes[n].BoundBox.ZMax for n in battery_names)
        source_min=min(s.BoundBox.ZMin for s in moved.values())
        z=battery_top+1.25-source_min
        if rear_bay:
            cell=shapes['BatterySelectedNominal'].BoundBox
            # Whole left ring mouth stays beyond cell end; its straight jacket
            # crosses ABOVE the cell. Restraints move to the already reserved
            # after-arc9 lands, avoiding rigid bands inside P0's side window.
            radial_min=min(float(rot.multVec(A.Vector(*r['point_mm'])-A.Vector(*packet['centre_mm'])).x)
                           for r in packet['recipes'])
            # Use multVec rather than overloaded multiplication on FreeCAD
            # versions whose Rotation*Vector overload is unavailable.
            target_x=cell.XMax+1.25-radial_min
            target_plane_z=cell.ZMax+2.1+1.25
            plane_offset=rot.multVec(A.Vector(*packet['recipes'][0]['point_mm'])-A.Vector(*packet['centre_mm'])).z
            z=target_plane_z-plane_offset
            dx=target_x-pose['centre_mm'][0];pose['centre_mm'][0]=target_x
            for s in moved.values():s.translate(A.Vector(dx,0,0))
        if fore_axial:
            # Restore the chosen fore bay after the separate rear-bay formula.
            fore_x=-99.3 if fore_outboard else -110
            dx=fore_x-pose['centre_mm'][0];pose['centre_mm'][0]=fore_x
            for s in moved.values():s.translate(A.Vector(dx,0,0))
            plate_top=shapes['Print_P0_BATTERY_PLATE_R4'].BoundBox.ZMax
            # ForeFHAC is the F_HY functional group, NOT protected F_PI.
            fore_fuse_bottom=foreparts['ForeFHAC:case'].BoundBox.ZMin
            key_radius=shapes['Ref_Material_current_S1_control_CP2_0_0'].BoundBox.XLength/2
            low=plate_top+1.25+key_radius;high=fore_fuse_bottom-1.25-key_radius
            assert low<high,'No key corridor between plate and protected F_PI'
            z=(low+high)/2
            if fore_outboard:
                frame_top=max(shapes['Ref_Material_P0_Side'+side+'22_0_0'].BoundBox.ZMax for side in ('Left','Right'))
                case_half_z=moved['Ref_Material_current_S1_body_CP2_0_0'].BoundBox.ZLength/2
                z=frame_top+1.25+case_half_z
        pose['centre_mm'][2]=z
        for s in moved.values():s.translate(A.Vector(0,0,z))
    proposal=dict(pose=pose,parent_core_pose_id=parent['core_pose_id'],terminal_min_Y_mm=terminal_min_y,
        terminal_plane_Y_mm=qy,full_saddle_band_inward_extent_mm=5.3,required_air_mm=1.25,
        independently_offset_wires=False,actual_core_parts=10,core_pair_receipts=[],fan_domains={},
        full_carrier_roots_tools_and_other47_joint_STILL_REQUIRED=True,N01_complete=False)
    if key_up:
        proposal.update(source_key_points_up=True,body_and_ring_plane_horizontal=True,
                        battery_top_mm=battery_top,source_local_min_Z_mm=source_min,
                        derived_centre_Z_mm=z,height_from_whole_core_not_another_offset=True,
                        actual_source_case_short24_axis_across_bank_gap=True)
        if rear_bay:proposal.update(source_behind_actual_cell=True,grip_sites='AFTER_ARC9',
                                   cell_end_X_mm=cell.XMax,jacket_plane_Z_mm=target_plane_z)
        previous=result.get('fore_outboard_budget' if fore_outboard else 'fore_axial_budget' if fore_axial else 'rear_bay_stack_budget' if rear_bay else 'key_up_stack_budget')
        if previous:
            assert previous['pose']!=pose,'Do not repeat unchanged key-up geometry'
            result.setdefault('key_up_stack_budget_prior_rejections',[]).append(previous)
    if fore_axial:
        proposal.update(source_key_points_up=False,body_and_ring_plane_horizontal=False,
                        source_key_axis_toward_positive_X=True,whole_transverse_plane_tilt_degrees=45,
                        key_corridor_centre_interval_Z_mm=[low,high],key_radius_mm=key_radius,
                        plate_top_mm=plate_top,actual_F_HY_fore_case_bottom_mm=fore_fuse_bottom,
                        all_fixed_P0_parts_included=True)
    if fore_outboard:
        proposal.update(source_key_axis_toward_positive_X=False,source_key_axis_toward_positive_Y=True,
                        key_corridor_centre_interval_Z_mm=None,frame_top_mm=frame_top,
                        case_half_height_mm=case_half_z,height_from_full_frame_not_unsigned_field=True,
                        first3mm_then_flexible_bend_and_after_arc_grip_PLAN_ONLY=True,
                        fixed_first12_before_grip_not_a_factory_requirement=True)
    result['fore_outboard_budget' if fore_outboard else 'fore_axial_budget' if fore_axial else 'rear_bay_stack_budget' if rear_bay else 'key_up_stack_budget' if key_up else 'outboard_terminal_gallery']=proposal
    def save():
        proposal['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    obstacles={n:shapes[n] for n in needed if n not in moved}
    if fore_axial:
        for n,s in foreparts.items():
            if forerecords[n]['group']=='ForeFHAC':obstacles[n]=s
        proposal['F_PI_complete_field_owner_checked']=sorted(n for n in foreparts if forerecords[n]['group']=='ForeFHAC')
    for n,s in moved.items():
        assert s.isValid() and s.Solids,n
        for other,t in obstacles.items():
            if fore_axial:
                from feline_solid_distance import bbox_lower_bound
                bound=bbox_lower_bound(s.BoundBox,t.BoundBox)
                if bound>=1.25-1e-6:
                    proposal['core_pair_receipts'].append(dict(source=n,obstacle=other,gap_lower_bound_mm=bound,
                        proof='SEPARATING_BOUND_NOT_CONTACT_VERDICT',required_mm=1.25))
                    continue
            gap=distance(s,t);volume=None
            if gap<1e-6:
                common=s.common(t);assert common.isValid();volume=common.Volume
            proposal['core_pair_receipts'].append(dict(source=n,obstacle=other,exact_gap_mm=gap,
                                                       positive_common_mm3=volume,required_mm=1.25))
        save()
    proposal['core_pair_failures']=[r for r in proposal['core_pair_receipts']
        if (r['exact_gap_mm'] if 'exact_gap_mm' in r else r['gap_lower_bound_mm'])<1.25-1e-6]
    if proposal['core_pair_failures']:
        proposal['status']='SOURCE_GALLERY_REJECTED_BY_ACTUAL_CORE_PAIR';save()
        print(json.dumps(dict(status=proposal['status'],pose=pose,failures=proposal['core_pair_failures'],seconds=proposal['worker_seconds'])),flush=True);return
    if fore_outboard:
        proposal['status']='FORE_OUTBOARD_CRITICAL_CORE_RECEIVED_GLOBAL_GATE_AND_FLEXIBLE_HARNESS_PENDING'
        save();print(json.dumps(dict(status=proposal['status'],pose=pose,critical_pairs=len(proposal['core_pair_receipts']),
                                    failures=0,seconds=proposal['worker_seconds'])),flush=True);return
    cm=source_core(packet,pose,sourcepoints,43);val,why=world_score(cm,fields,inside,service)
    proposal['core_numeric_world']=dict(margin_mm=val,layer=why)
    for recipe in packet['recipes']:
        accepted=[];rejected={}
        for bend,head,side in itertools.product(range(0,360,45),(0,90,180,270),(-1,1) if rear_bay else (1,)):
            fm=fan(packet,pose,recipe,43,bend,head)
            if rear_bay:fm=source_after_arc_saddle(fm,side,head)
            score,label=world_score(fm,fields,inside,service)
            if score>=0:fm['numeric_score']=score;accepted.append(compact(fm))
            else:rejected[label]=rejected.get(label,0)+1
        proposal['fan_domains'][recipe['ref']]=accepted
        proposal.setdefault('fan_rejected',{})[recipe['ref']]=rejected;save()
    proposal['status']='SOURCE_GALLERY_DOMAINS_RECEIVED_NOT_WHOLE_N01'
    proposal['all_four_nonempty']=all(proposal['fan_domains'].values())
    result['source_sha256'].update({**pins,materialpath.relative_to(ROOT).as_posix():sha(materialpath),
                                  bundle.relative_to(ROOT).as_posix():sha(bundle),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
    save();print(json.dumps(dict(status=proposal['status'],pose=pose,core_numeric=proposal.get('core_numeric_world'),
                                fans={k:len(v) for k,v in proposal['fan_domains'].items()},seconds=proposal['worker_seconds'])),flush=True)


def source_after_arc_saddle(m,side,head_angle):
    """Relocate the simple saddle/tie to the existing after-arc9 jacket land.

    The entire wire centreline stays identical. No invented extra wire length,
    smaller radius, connector change or single-wire shift through P0.
    """
    import itertools
    m=dict(m);axis=np.array(m['bend_unit']);normal=side*np.array(m['departure_axis'])
    v=np.cross(axis,normal);q=np.array(m['after_arc_end_mm'])-9*axis
    saddle=[];band=[]
    for x,t,r in itertools.product(np.linspace(0,9,6),np.linspace(math.pi,2*math.pi,17),np.linspace(2.1,4.1,3)):
        saddle.append(q+x*axis+r*(math.cos(t)*v+math.sin(t)*normal))
    for x,t,thick in itertools.product((3.25,4.5,5.75),np.linspace(0,2*math.pi,33),(0.,1.2)):
        r=(2.1 if math.sin(t)>=0 else 4.1)+thick
        band.append(q+x*axis+r*(math.cos(t)*v+math.sin(t)*normal))
    for x,sign,r,z in itertools.product((3.25,4.5,5.75),(-1,1),np.linspace(2.1,5.3,5),(-.6,.6)):
        band.append(q+x*axis+sign*r*v+z*normal)
    ht=math.radians(head_angle);r=2.1 if math.sin(ht)>=0 else 4.1
    h=q+4.5*axis+(r+1.2+3)*(math.cos(ht)*v+math.sin(ht)*normal)
    head=box_points(h-3,h+3)
    # First65 samples are exactly the received whole prefix+arc+after9 wire.
    p=np.vstack((m['points'][:65],np.array(saddle),np.array(band),head))
    rr=np.r_[m['radii'][:65],np.zeros(len(p)-65)]
    tt=np.r_[m['types'][:65],np.full(len(p)-65,2)]
    m.update(points=p,radii=rr,types=tt,bounds=np.array([(p-rr[:,None]).min(0),(p+rr[:,None]).max(0)]),
             grip_site='EXISTING_AFTER_ARC9_JACKET',grip_start_mm=0,grip_side=side,
             grip_point_mm=q.tolist(),grip_axis=axis.tolist(),before_arc_hard_grip_removed=True)
    return m


def source_underbank_owner_diagnosis():
    """Name fixed owners of the horizontal low S1 bay, without new fan trials.

    Existing vertical gallery crosses P0; inspect the whole horizontal branch
    below bank instead of attempting another offset through retained frame.
    """
    import FreeCAD as A
    from feline_current_candidate_scene import current
    from plan_feline_central_pi_wedge import packed
    from feline_solid_distance import distance
    tick=time.monotonic()
    scene,meta,_,pins,bus,*_=current()
    proofpath=OUT/'n01-flat20-field-modulejoint.json';proof=json.loads(proofpath.read_text())
    for file,groups in (('n01-fore-service-macro.json',{'F_HP','F_TY'}),('n01-fore-topology.json',{'ForeFHAC'})):
        _,extra,records=packed(OUT/file)
        for n,s in extra.items():
            if records[n]['group'] in groups:scene[n]=s
        pins[(OUT/file).relative_to(ROOT).as_posix()]=sha(OUT/file)
    packet=json.loads((OUT/'n01-intrinsic-s1-whole-pose.json').read_text())
    body=scene['Ref_Material_current_S1_body_CP2_0_0'];rot=A.Rotation(*packet['rotation_quaternion'])
    # X60 keeps full42mm case beyond P_SYS's maxX26.55+1.25. Y0 stays
    # between P0 side rails. Z24 retains key below and terminals above case.
    rear_owner='--source-rear-owners' in sys.argv
    target=A.Vector(60,0,24);tf=A.Placement(target-rot.multVec(body.BoundBox.Center),rot)
    if rear_owner:
        received=json.loads((OUT/'n01-source-saddles-whole-joint.json').read_text())['rear_bay_stack_budget']['pose']
        target=A.Vector(*received['centre_mm']);matrix=A.Matrix()
        for i in range(3):
            for j in range(3):setattr(matrix,f'A{i+1}{j+1}',received['rotation_rows'][i][j])
        outerrot=A.Rotation(matrix)
        base=A.Placement(A.Vector(*packet['centre_mm'])-rot.multVec(body.BoundBox.Center),rot)
        tf=A.Placement(target-outerrot.multVec(A.Vector(*packet['centre_mm'])),outerrot)*base
    moving={}
    for n in ('Ref_Material_current_S1_body_CP2_0_0','Ref_Material_current_S1_control_CP2_0_0'):
        s=scene[n].copy();s.Placement=tf*s.Placement;assert s.isValid();moving[n]=s
    fixed={r['source'] for r in proof['material_clouds'] if r['category']!='S1_mating_context'}
    pairs=[];failures=[];errors=[]
    dest=OUT/'n01-source-saddles-whole-joint.json';result=json.loads(dest.read_text())
    rec=dict(centre_mm=list(target),source_plane_horizontal=True,source_parts_checked=2,
             whole_four_fans_not_yet_allocated=True,pairs=pairs,failures=failures,errors=errors,
             geometry_changed=False,N01_complete=False,physical_pass=False)
    result['rear_bay_owner_diagnosis' if rear_owner else 'underbank_owner_diagnosis']=rec
    def save():
        rec['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    for n,s in moving.items():
        a=s.BoundBox;ab=np.array([[a.XMin,a.YMin,a.ZMin],[a.XMax,a.YMax,a.ZMax]])
        for other in sorted(fixed):
            if other not in scene:errors.append(dict(source=other,error='Missing field owner in reconstructed scene'));continue
            t=scene[other];bb=t.BoundBox;tb=np.array([[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]])
            if box_gap(ab,tb)>=1.25:continue
            try:
                query=s
                if other==bus['name']:
                    query=s.copy();query.Placement=bus['inverse']*s.Placement;t=bus['original']
                assert t.isValid(),other
                gap=distance(query,t);volume=None
                if gap<1e-6 and t.Solids:
                    common=query.common(t);assert common.isValid();volume=common.Volume
                row=dict(source=n,obstacle=other,kind=meta.get(other,{}),exact_gap_mm=gap,positive_common_mm3=volume)
                pairs.append(row)
                if gap<1.25-1e-6:failures.append(row)
            except Exception as e:errors.append(dict(source=other,error=repr(e)))
        save()
    result['source_sha256'].update(pins)
    result['source_sha256'].update({p.relative_to(ROOT).as_posix():sha(p) for p in (proofpath,Path(__file__))})
    save();print(json.dumps(dict(seconds=rec['worker_seconds'],pairs=len(pairs),failures=failures,errors=errors)),flush=True)


def source_rear_resume_contract(result,packet):
    """Validate interrupted receipt metadata BEFORE loading costly fields."""
    p=result['rear_bay_stack_budget'];pose=p['pose']
    assert len(p['core_pair_receipts'])==380
    p['core_pair_failures']=[r for r in p['core_pair_receipts'] if r['exact_gap_mm']<1.25-1e-6]
    assert p['core_pair_failures']==[]
    assert len({r['source'] for r in p['core_pair_receipts']})==10
    assert np.allclose(pose['centre_mm'],[103.623,0,53.55],atol=1e-8)
    assert pose['rotation_rows']==[[0,1,0],[1,0,0],[0,0,-1]]
    # The source packet pins the datum; the receiver also pins current scene
    # sources. An interrupted receiver need not have duplicated every pin yet.
    inherited={**packet['source_sha256'],**result['source_sha256']}
    for name in ('n01-full-material-scene.json','n01-full-material-scene.zip','n01-s1-current-source-datums.json'):
        rel=(OUT/name).relative_to(ROOT).as_posix()
        assert rel in inherited and sha(ROOT/rel)==inherited[rel],rel
    return p


def source_resume_rear_fans():
    """Resume after wrapper NameError; reuse complete380 actual core pairs."""
    import hashlib
    import inspect
    import itertools
    from feline_s1_saddle_layout import load_sources,fan,world_score,source_core
    tick=time.monotonic()
    dest=OUT/'n01-source-saddles-whole-joint.json';result=json.loads(dest.read_text())
    packet=json.loads((OUT/'n01-intrinsic-s1-whole-pose.json').read_text())
    p=source_rear_resume_contract(result,packet);pose=p['pose']
    _,packet,sourcepoints,fields,inside,service,pins=load_sources()
    algorithm=hashlib.sha256((inspect.getsource(source_after_arc_saddle)+
                              sha(ROOT/'tools/cad/feline_s1_saddle_layout.py')).encode()).hexdigest()
    if 'fan_algorithm_sha256' in p:assert p['fan_algorithm_sha256']==algorithm
    p['fan_algorithm_sha256']=algorithm;p['status']='RUNNING_REAR_AFTER_ARC_FANS'
    p['actual_core_pairs_reused_without_queries']=380
    p.setdefault('fan_domains',{});p.setdefault('fan_rejected',{})
    def save():
        p['fan_worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    cm=source_core(packet,pose,sourcepoints,43);val,why=world_score(cm,fields,inside,service)
    p['core_numeric_world']=dict(margin_mm=val,layer=why);save()
    for recipe in packet['recipes']:
        if recipe['ref'] in p['fan_domains']:continue
        accepted=[];rejected={}
        for bend,head,side in itertools.product(range(0,360,45),(0,90,180,270),(-1,1)):
            m=source_after_arc_saddle(fan(packet,pose,recipe,43,bend,head),side,head)
            score,label=world_score(m,fields,inside,service)
            if score>=0:m['numeric_score']=score;accepted.append(compact(m))
            else:rejected[label]=rejected.get(label,0)+1
        p['fan_domains'][recipe['ref']]=sorted(accepted,key=lambda m:-m['numeric_score'])
        p['fan_rejected'][recipe['ref']]=rejected;save()
        print('Rear source fan',recipe['ref'],len(accepted),flush=True)
    p['status']='REAR_SOURCE_FAN_DOMAINS_RECEIVED_NOT_WHOLE_N01'
    p['all_four_nonempty']=all(p['fan_domains'].values())
    result['source_sha256'].update(pins);result['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    save();print(json.dumps(dict(seconds=p['fan_worker_seconds'],core_numeric=p['core_numeric_world'],
                                domains={k:len(v) for k,v in p['fan_domains'].items()})),flush=True)


def source_exact_core_gate():
    """Actual complete source vs ALL fixed owners before another fan family.

    Reuses43received poses; unsigned surface fields are not interior tests.
    Bbox is only a rigorous separating bound; overlap receives actual solids.
    Completed pose and exact pair receipts survive bounded worker exits.
    """
    import hashlib
    import itertools
    import zipfile
    import FreeCAD as A
    import Part
    from feline_current_candidate_scene import current
    from plan_feline_central_pi_wedge import packed
    from feline_solid_distance import distance,bbox_lower_bound
    tick=time.monotonic()
    dest=OUT/'n01-source-saddles-whole-joint.json';result=json.loads(dest.read_text())
    packetpath=OUT/'n01-intrinsic-s1-whole-pose.json';packet=json.loads(packetpath.read_text())
    datumpath=OUT/'n01-s1-current-source-datums.json';datum=json.loads(datumpath.read_text())
    materialpath=OUT/'n01-full-material-scene.json';material=json.loads(materialpath.read_text())
    bundle=ROOT/material['bundle'];assert sha(bundle)==material['bundle_sha256']
    records={r['name']:r for r in material['parts']};original={}
    with zipfile.ZipFile(bundle) as z:
        for row in datum['source_parts']:
            n=row['name'];r=records[n];blob=z.read(r['entry']);assert hashlib.sha256(blob).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(blob.decode());assert s.isValid() and s.Solids
            original[n]=s
    body=original['Ref_Material_current_S1_body_CP2_0_0'];rr=A.Rotation(*packet['rotation_quaternion'])
    tf=A.Placement(A.Vector(*packet['centre_mm'])-rr.multVec(body.BoundBox.Center),rr)
    base={}
    for n,s0 in original.items():
        s=s0.copy();s.Placement=tf*s.Placement;base[n]=s
    recipes={r['ref']:r for r in packet['recipes']}
    for r in datum['receipts']:
        n=r['matching_nominal_source_planes'][0]['part'];number=int(n.split('_ring_')[1].split('_')[0])
        screw=original[f'Ref_Material_current_S1_screw_{number}_0_0']
        q,d=(A.Vector(*r[k]) for k in ('source_point_mm','source_departure'))
        eye=A.Vector(screw.BoundBox.Center.x,q.y,screw.BoundBox.Center.z)
        target=rr.inverted().multVec(A.Vector(*recipes[r['endpoint']]['departure_axis']))
        cr=A.Rotation(A.Vector(0,1,0),math.degrees(math.atan2(d.z,d.x)-math.atan2(target.z,target.x)))
        clock=A.Placement(eye-cr.multVec(eye),cr)
        s=original[n].copy();s.Placement=tf*clock*s.Placement;base[n]=s
    if '--source-hard-motion' in sys.argv:
        source_hard_motion_receiver(base,packet,result,
            {p.relative_to(ROOT).as_posix():sha(p) for p in (packetpath,datumpath,materialpath,bundle)},tick)
        return
    scene,meta,_,pins,bus,*_=current()
    proofpath=OUT/'n01-flat20-field-modulejoint.json';proof=json.loads(proofpath.read_text())
    for file,groups in (('n01-fore-service-macro.json',{'F_HP','F_TY'}),('n01-fore-topology.json',{'ForeFHAC'})):
        _,extra,rows=packed(OUT/file)
        for n,s in extra.items():
            if rows[n]['group'] in groups:scene[n]=s;meta[n]=rows[n]
        pins[(OUT/file).relative_to(ROOT).as_posix()]=sha(OUT/file)
    fixednames={r['source'] for r in proof['material_clouds'] if r['category']!='S1_mating_context'}
    assert not fixednames-set(scene),fixednames-set(scene)
    categories={r['source']:r['category'] for r in proof['material_clouds']}
    # Hard retained P0/purchased components before mutable planning budgets.
    def priority(n):
        r=meta.get(n,{})
        return ('reservation' in categories[n] or 'budget' in n.lower() or r.get('kind')=='reservation',
                not (r.get('role')=='P0_or_battery' or 'Ref_Material_P0_' in n),n)
    fixed=sorted(fixednames,key=priority)
    layoutpath=OUT/'n01-s1-saddle-layout.json';layout=json.loads(layoutpath.read_text())
    poses=[dict(id=r['core_pose_id'],pose=r['pose']) for r in layout['poses']]
    for name in ('rear_bay_stack_budget','fore_axial_budget','fore_outboard_budget'):
        if name in result:poses.append(dict(id=name,pose=result[name]['pose']))
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (packetpath,datumpath,materialpath,bundle,proofpath,layoutpath)})
    gate=result.get('exact_complete_source_core_gate',dict(status='RUNNING_ACTUAL_COMPLETE_SOURCE_CORE_GATE',
         selected=False,N01_complete=False,physical_pass=False,source_sha256=pins,receipts=[],pair_receipts={},errors=[]))
    assert gate['source_sha256']==pins,'Changed world/source requires affected-core requalification'
    complete={r['id']:r['pose'] for r in gate['receipts']};memo=gate['pair_receipts'];signatures={}
    result['exact_complete_source_core_gate']=gate
    def sig(s):return hashlib.sha256(s.exportBrepToString().encode()).hexdigest()
    def save():
        gate['worker_seconds']=round(time.monotonic()-tick,3)
        gate['received_pose_count']=len(gate['receipts']);gate['proposed_pose_count']=len(poses)
        gate['surviving_core_ids']=[r['id'] for r in gate['receipts'] if r['first_failure'] is None]
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    gate['status']='RUNNING_ACTUAL_COMPLETE_SOURCE_CORE_GATE';save()
    for row in poses:
        if row['id'] in complete:
            assert complete[row['id']]==row['pose'],'Same core id with changed pose is not reusable evidence'
            continue
        if time.monotonic()-tick>180:
            gate['status']='PARTIAL_ACTUAL_COMPLETE_SOURCE_CORE_GATE';break
        pose=row['pose'];matrix=A.Matrix()
        for i in range(3):
            for j in range(3):setattr(matrix,f'A{i+1}{j+1}',pose['rotation_rows'][i][j])
        rotation=A.Rotation(matrix)
        outer=A.Placement(A.Vector(*pose['centre_mm'])-rotation.multVec(A.Vector(*packet['centre_mm'])),rotation)
        rec=dict(id=row['id'],pose=pose,first_failure=None,actual_pairs=0,separating_bounds=0)
        for n in sorted(base,key=lambda n:('body' not in n,'control' not in n,n)):
            s=base[n].copy();s.Placement=outer*s.Placement
            if not s.isValid():rec['first_failure']=dict(source=n,error='Invalid rigid source; no clearance verdict');break
            for other in fixed:
                t=scene[other];minimum=3.35 if not t.Solids else 1.25
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum-1e-6:
                    rec['separating_bounds']+=1;continue
                try:
                    query=s
                    if other==bus['name']:
                        query=s.copy();query.Placement=bus['inverse']*query.Placement;t=bus['original']
                    assert t.isValid(),other
                    if other not in signatures:signatures[other]=sig(t)
                    key=':'.join((sig(query),signatures[other],str(minimum),'solid-distance-v1'))
                    if key not in memo:
                        gap=distance(query,t) if t.Solids else float(query.distToShape(t)[0])
                        volume=None
                        if gap<1e-6 and t.Solids:
                            common=query.copy().common(t.copy());assert common.isValid();volume=common.Volume
                        memo[key]=dict(gap_mm=gap,required_mm=minimum,positive_common_mm3=volume)
                    pair=memo[key];rec['actual_pairs']+=1
                    if pair['gap_mm']<minimum-1e-6:
                        rec['first_failure']=dict(source=n,obstacle=other,category=categories[other],**pair);break
                except Exception as e:
                    rec['first_failure']=dict(source=n,obstacle=other,error=repr(e));gate['errors'].append(rec['first_failure']);break
            if rec['first_failure']:break
        gate['receipts'].append(rec);save()
        print('Actual complete core',row['id'],'clear' if rec['first_failure'] is None else rec['first_failure'],flush=True)
    else:gate['status']='ACTUAL_COMPLETE_SOURCE_CORE_GATE_RECEIVED_NO_N01'
    save();print(json.dumps(dict(status=gate['status'],seconds=gate['worker_seconds'],received=gate['received_pose_count'],
                                survivors=gate['surviving_core_ids'],errors=len(gate['errors']))),flush=True)


def source_hard_motion_receiver(base,packet,result,pins,tick):
    """Qualify the candidate against immutable motion before moving PWM.

    Existing p4 outer is an unselected shape variable inside325x200x160;
    report any required fore-station refinement, never silently widen200.
    """
    import hashlib
    import zipfile
    import FreeCAD as A
    from feline_candidate_collision_scene import Scene
    from feline_solid_distance import distance
    from receive_feline_global_case_candidates import placement
    candidate=result['fore_outboard_budget'];assert candidate['core_pair_failures']==[]
    pose=candidate['pose'];matrix=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(matrix,f'A{i+1}{j+1}',pose['rotation_rows'][i][j])
    r=A.Rotation(matrix);outer=A.Placement(A.Vector(*pose['centre_mm'])-r.multVec(A.Vector(*packet['centre_mm'])),r)
    shapes={}
    for n,source in base.items():
        s=source.copy();s.Placement=outer*s.Placement;assert s.isValid() and s.Solids,n
        shapes[n]=s
    archive=OUT/'n01-current-s1-core.breps.zip';parts=[]
    # One current received source snapshot, not a new native assembly variant.
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for i,(n,s) in enumerate(shapes.items()):
            blob=s.exportBrepToString().encode();entry=f'{i:02d}.brep';z.writestr(entry,blob)
            parts.append(dict(name=n,entry=entry,sha256=hashlib.sha256(blob).hexdigest()))
    bundlehash=sha(archive)
    scene=Scene();pins.update(scene.pins)
    old=result.get('hard_source_motion_receiver')
    if old:
        assert old['bundle_sha256']==bundlehash and old['source_sha256']==pins,'Changed core/motion invalidates receipts'
        rec=old;rec.setdefault('previous_worker_seconds',[]).append(rec['worker_seconds'])
    else:
        rec=dict(status='RUNNING_SOURCE_HARD_MOTION',selected=False,N01_complete=False,physical_pass=False,
                 bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=bundlehash,parts=parts,
                 source_sha256=pins,outer_receipts=[],motion_pairs={},completed_sources=[],first_failure=None,
                 motion_samples=36,continuous_sweep_verified=False,static_PWM_owner_conflict_STILL_OPEN=True,
                 p4_is_not_an_immutable_selected_shell=True,outer_refinement_required=[],errors=[])
    result['hard_source_motion_receiver']=rec
    dest=OUT/'n01-source-saddles-whole-joint.json'
    def save():
        rec['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    rec['status']='RUNNING_SOURCE_HARD_MOTION';save()
    done=set(rec['completed_sources']);outer_done={x['source'] for x in rec['outer_receipts']}
    try:
        for n,s in sorted(shapes.items(),key=lambda x:('body' not in x[0],'control' not in x[0],x[0])):
            if n in done:continue
            if time.monotonic()-tick>180:rec['status']='PARTIAL_SOURCE_HARD_MOTION';break
            bb=s.BoundBox;bounds=np.array([[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]])
            if np.any(bounds[0]<np.array([-141.5,-100,-48])+3.25-1e-5) or np.any(bounds[1]>np.array([183.5,100,112])-3.25+1e-5):
                rec['first_failure']=dict(source=n,kind='Absolute325x200x160 clearance bound exceeded');break
            if n not in outer_done:
                outside=s.copy().cut(scene.outer.copy());assert outside.isNull() or outside.isValid()
                gap=float(s.distToShape(scene.outer.Shells[0])[0])
                entry=dict(source=n,p4_outside_mm3=outside.Volume,gap_to_p4_mm=gap,required_wall_plus_air_mm=3.25)
                rec['outer_receipts'].append(entry)
                if outside.Volume>1e-5 or gap<3.25-1e-5:rec['outer_refinement_required'].append(entry)
                save()
            for p in scene.motion:
                if box_gap(bounds,np.array(p['bounds']))>=1.25-1e-6:continue
                key=n+'|'+p['name']+'|'+str(p['pose'])
                if key in rec['motion_pairs']:pair=rec['motion_pairs'][key]
                else:
                    t=scene.rest[p['name']];assert t.isValid() and t.Solids,p['name']
                    q=s
                    if np.linalg.norm(p['r']-np.eye(3))>1e-12 or np.linalg.norm(p['t'])>1e-7:
                        q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
                    assert q.isValid(),'Invalid inverse source, no clearance verdict'
                    gap=distance(q,t);volume=None
                    if gap<1e-6:
                        common=q.copy().common(t.copy());assert common.isValid();volume=common.Volume
                    pair=dict(source=n,leg_source=p['name'],pose=p['pose'],code=p['code'],stage=p['stage'],
                              gap_mm=gap,required_mm=1.25,positive_common_mm3=volume)
                    rec['motion_pairs'][key]=pair
                    if len(rec['motion_pairs'])%20==0:save()
                if pair['gap_mm']<1.25-1e-5:
                    rec['first_failure']=dict(kind='actual_leg_sample_clearance',**pair);break
            if rec['first_failure']:break
            rec['completed_sources'].append(n);save()
        else:rec['status']='SOURCE_HARD_MOTION_RECEIVED_NOT_WHOLE_N01'
        if rec['first_failure']:rec['status']='SOURCE_HARD_MOTION_REJECTED'
    except Exception as e:
        rec['errors'].append(repr(e));rec['status']='SOURCE_HARD_MOTION_ERROR_NOT_CLEARANCE'
    save();print(json.dumps(dict(status=rec['status'],seconds=rec['worker_seconds'],completed=len(rec['completed_sources']),
                                actual_pairs=len(rec['motion_pairs']),first_failure=rec['first_failure'],
                                outer_refinement_required=rec['outer_refinement_required'],errors=rec['errors'])),flush=True)


def source_saddles_joint():
    """Reuse unchanged47 source domains; bind core and4fans by core_pose_id.

    Persist numeric pair receipts by complete geometry and semantic hashes.
    These rejection-only screens do not accept BRep contact/whole N01.
    """
    import hashlib
    from feline_s1_saddle_layout import load_sources,source_core,fan
    from feline_pwm_pigtail_templates import candidates as pwm_candidates
    tick=time.monotonic()
    core,packet,sourcepoints,_,_,_,pins=load_sources()
    saddlepath=OUT/'n01-s1-saddle-layout.json'
    saddle=json.loads(saddlepath.read_text())
    assert saddle['status'] in ('S1_SADDLE_DOMAINS_RECEIVED','S1_COMPLETE_ORIENTATIONS_RECEIVED')
    assert saddle['source_sha256']==pins
    oldpath=OUT/'n01-whole51-joint-proposal.json';old=json.loads(oldpath.read_text())
    # Only this coordinator changed (added a new entry mode); all underlying
    # world fields, candidate geometry helpers and purchased sources stay pinned.
    own=Path(__file__).relative_to(ROOT).as_posix()
    for name,h in old['source_sha256'].items():
        if name!=own:assert sha(ROOT/name)==h,name
    proof=json.loads((OUT/'n01-flat20-field-modulejoint.json').read_text())
    plan=json.loads((OUT/'n01-flat-station-architecture.json').read_text())
    domains={}
    for station in plan['stations']:
        domains[station['ref']]=[build(station,r['family'],r['side'],r['departure_X'],r['centre_mm'][0],
            r.get('centre_y_override_mm'),r.get('bend_mode','OUTWARD_CONCENTRIC'),r.get('closure_mode','AUTO'))
            for r in old['domains'][station['ref']]]
    extra=bank_candidates(proof)
    anchors,mates,anchor_pins=anchor_candidates(old['actual_anchor_parent_receipts']);extra.update(anchors)
    pwm,pwm_pins=pwm_candidates();extra.update(pwm)
    def row_key(r):
        if r.get('bank_source'):return r['bend_clock_degrees'],r['complete_band_head_degrees']
        if r.get('anchor_source'):return r['axis_X_mm']
        if r.get('f_pwm_source'):return tuple(r['centre_mm']),tuple(r['head_choices'])
        raise AssertionError(r['ref'])
    for name,proposals in extra.items():
        bykey={row_key(m):m for m in proposals}
        domains[name]=[bykey[row_key(r)] for r in old['domains'][name]]
    assert len(domains)==47
    good=[r for r in saddle['poses'] if r['all_four_nonempty']]
    domains['S1_core']=[]
    for recipe in packet['recipes']:domains[recipe['ref']]=[]
    for r in good:
        pid=r['core_pose_id'];pose=r['pose']
        domains['S1_core'].append(source_core(packet,pose,sourcepoints,pid))
        for recipe in packet['recipes']:
            domains[recipe['ref']].extend(fan(packet,pose,recipe,pid,x['bend_degrees'],x['head_degrees'])
                                         for x in r['fan_domains'][recipe['ref']])
    dest=OUT/'n01-source-saddles-whole-joint.json'
    cachepath=OUT/'n01-source-saddles-pair-cache.json'
    algorithm='typed-whole52-source-saddles-v1'
    cache=json.loads(cachepath.read_text()) if cachepath.exists() else dict(algorithm=algorithm,pairs={})
    assert cache['algorithm']==algorithm
    memo=cache['pairs'];trees={};hashes={}
    def identity(m):
        key=id(m)
        if key not in hashes:
            h=hashlib.sha256()
            for k in ('points','radii','types'):
                a=np.ascontiguousarray(m[k]);h.update(str(a.shape).encode());h.update(a.tobytes())
            h.update(json.dumps(compact(m),sort_keys=True).encode())
            for b in m['boxes']:h.update(str(b['kind']).encode());h.update(np.asarray(b['bounds']).tobytes())
            hashes[key]=h.hexdigest()
        return hashes[key]
    result=dict(status='RUNNING_SOURCE_SADDLES_WHOLE52',selected=False,N01_complete=False,physical_pass=False,
                source_sha256={**pins,**anchor_pins,**pwm_pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in
                    (oldpath,saddlepath,Path(__file__))}},whole_joint_nodes=52,
                domain_counts={n:len(v) for n,v in domains.items()},actual_anchor_mates_reused=mates,
                joint_assignment=None,first_named_dead_ends=[],search_nodes=0,errors=[],
                full_roots_tools_all123portions246ends_STILL_REQUIRED=True)
    visited=0;trace=[];assignment=None
    def save():
        result.update(worker_seconds=round(time.monotonic()-tick,3),search_nodes=visited,
                      numeric_pair_receipts=len(memo),first_named_dead_ends=trace)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        cachepath.write_text(json.dumps(cache,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>180:raise TimeoutError('180s whole joint; domains/pair cache retained')
    def pair(a,i,b,j):
        aa,bb=domains[a][i],domains[b][j]
        # All4fan variables MUST share the same rigid core, not four unrelated
        # poses selected independently to produce a misleading feasible layout.
        if 'core_pose_id' in aa and 'core_pose_id' in bb and aa['core_pose_id']!=bb['core_pose_id']:return False
        key=':'.join(sorted((identity(aa),identity(bb))))
        if key in memo:return memo[key]
        if aa.get('anchor_source') and bb.get('anchor_source'):
            fore=aa if a=='Anchor:Fore' else bb;rear=bb if b=='Anchor:Rear' else aa
            value=rear['axis_X_mm']-fore['axis_X_mm']>=90
        elif not any(x.get('source_core') or x.get('source_fan') or x.get('bank_source') or
                     x.get('anchor_source') or x.get('f_pwm_source') for x in (aa,bb)):
            value=compatible(aa,bb)
        elif box_gap(aa['bounds'],bb['bounds'])>=1.25:value=True
        else:
            value=True
            for group,other in ((aa,bb),(bb,aa)):
                for box in other['boxes']:
                    if group.get('anchor_source') and box['kind']==3:continue
                    if float(np.min(to_box(group['points'],box['bounds'])-group['radii']))<1.25-1e-5:
                        value=False;break
                if not value:break
            if value:
                maska=aa['types']!=3 if bb.get('anchor_source') else np.ones(len(aa['points']),bool)
                maskb=bb['types']!=3 if aa.get('anchor_source') else np.ones(len(bb['points']),bool)
                # Only source jacket insertion throat is an intended own mate.
                for group,other,mask in ((aa,bb,maska),(bb,aa,maskb)):
                    if group.get('source_fan') and other.get('source_core'):
                        axial=(group['points']-np.array(group['point_mm']))@np.array(group['departure_axis'])
                        mask &= (group['types']!=1)|(axial>3.35)
                tk=(id(bb),maska.tobytes()[:0],maskb.tobytes())
                if tk not in trees:trees[tk]=(cKDTree(bb['points'][maskb]),bb['radii'][maskb],bb['types'][maskb])
                tree,rr,tt=trees[tk];g,ix=tree.query(aa['points'][maska],workers=1)
                req=np.where((aa['types'][maska]==1)&(tt[ix]==1),.2,1.25)
                value=float(np.min(g-aa['radii'][maska]-rr[ix]-req))>=-1e-5
        memo[key]=bool(value);return bool(value)
    def solve(chosen,remaining):
        nonlocal visited
        gate();visited+=1
        if visited%20==0:save()
        if visited>20000:raise TimeoutError('20000 bounded whole-joint nodes')
        if not remaining:return chosen
        viable={n:[i for i in rows if all(pair(n,i,a,j) for a,j in chosen.items())] for n,rows in remaining.items()}
        empty=[n for n,v in viable.items() if not v]
        if empty:
            if len(trace)<30:trace.append(dict(chosen={n:compact(domains[n][i]) for n,i in chosen.items()},empty=empty))
            return None
        n=min(viable,key=lambda n:len(viable[n]));other={k:v for k,v in viable.items() if k!=n}
        for i in viable[n]:
            found=solve({**chosen,n:i},other)
            if found:return found
        return None
    save()
    try:
        empty=[n for n,v in domains.items() if not v]
        if empty:result.update(status='SOURCE_SADDLES_REQUIRED_DOMAIN_EMPTY_NOT_GLOBAL_INFEASIBILITY',empty_domains=empty)
        else:
            assignment=solve({}, {n:list(range(len(v))) for n,v in domains.items()})
            result['joint_assignment']=assignment
            if assignment:
                result['chosen_templates']={n:compact(domains[n][i]) for n,i in assignment.items()}
                result['status']='SOURCE_SADDLES_NUMERIC_PROPOSAL_REQUIRES_EXACT_ROOTS_TOOLS_WHOLE_N01'
            else:result['status']='SOURCE_SADDLES_BOUNDED_FAMILY_NO_JOINT_ASSIGNMENT'
    except Exception as e:result['errors'].append(repr(e));result['status']='PARTIAL_SOURCE_SADDLES_JOINT'
    save()
    print(json.dumps({k:result[k] for k in ('status','worker_seconds','search_nodes','numeric_pair_receipts','errors')}),flush=True)


if __name__=='__main__':
    import os
    print('WORKER_PID',os.getpid(),flush=True)
    if '--source-hard-motion' in sys.argv:
        source_exact_core_gate()
    elif '--source-fore-outboard-core' in sys.argv:
        source_outboard_terminal_gallery()
    elif '--source-exact-core-gate' in sys.argv:
        source_exact_core_gate()
    elif '--source-fore-axial-budget' in sys.argv:
        source_outboard_terminal_gallery()
    elif '--source-rear-owners' in sys.argv:
        source_underbank_owner_diagnosis()
    elif '--resume-rear-fans' in sys.argv:
        source_resume_rear_fans()
    elif '--source-rear-bay-budget' in sys.argv:
        source_outboard_terminal_gallery()
    elif '--source-key-up-budget' in sys.argv:
        source_outboard_terminal_gallery()
    elif '--source-underbank-owners' in sys.argv:
        source_underbank_owner_diagnosis()
    elif '--source-outboard-terminal-gallery' in sys.argv:
        source_outboard_terminal_gallery()
    elif '--source-exact-terminal-witness' in sys.argv:
        source_saddles_exact_terminal_witness()
    elif '--source-limiting-fan' in sys.argv:
        source_saddles_limiting_fan()
    elif '--source-complete-orientations' in sys.argv:
        source_saddles_complete_orientations()
    elif '--source-saddle-witnesses' in sys.argv:
        source_saddles_prefix_diagnosis()
    elif '--source-saddles-joint' in sys.argv:
        source_saddles_joint()
    elif '--source-saddles' in sys.argv:
        from feline_s1_saddle_layout import receive_domains
        receive_domains()
    else:main()
