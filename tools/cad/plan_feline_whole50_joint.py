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
from feline_flat_station_templates import build,compact,compatible,box_gap,to_box,self_wire_gap,pier_supported,shared_rail_bounds
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


if __name__=='__main__':main()
