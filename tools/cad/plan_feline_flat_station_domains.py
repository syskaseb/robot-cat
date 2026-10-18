"""One coupled whole20 source-box/fan/clamp/root proposal before exact CAD.

Batched SAME samples, saved per completed source; never serial OCC at each
search node. Numeric fields have explicit loose screens, NOT airgap approval.
All19changed cases and identity P_SYS must coexist before one exact receiver.
"""
import hashlib
import json
import sys
import time
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import cKDTree
from feline_flat_station_templates import build,compatible,compact,box_points,to_box,shared_rail_bounds,self_wire_gap,pier_supported

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    tick=time.monotonic();joint='--joint-space' in sys.argv;suffix='-joint' if joint else ''
    dest=OUT/('n01-flat20-domains'+suffix+'.json');assert not dest.exists()
    planfile=OUT/'n01-flat-station-architecture.json';plan=json.loads(planfile.read_text())
    fieldproof=OUT/('n01-flat20-field'+suffix+'.json');proof=json.loads(fieldproof.read_text())
    assert proof['stage']=='complete' and not proof['errors']
    fieldfile=ROOT/proof['field'];assert sha(fieldfile)==proof['field_sha256']
    for n,h in proof['source_sha256'].items():assert sha(ROOT/n)==h,n
    field=np.load(fieldfile,allow_pickle=False);axes=[field[k] for k in ('x','y','z')]
    fields={k:RegularGridInterpolator(axes,field[k+'_distance'],bounds_error=False,fill_value=0)
            for k in ('material','reservation','curve_hold','motion36','outer')}
    inside=RegularGridInterpolator(axes,field['inside'].astype(float),bounds_error=False,fill_value=0)
    service=RegularGridInterpolator(axes,field['service'].astype(float),method='nearest',bounds_error=False,fill_value=1)
    context=cKDTree(field['P_SYS_context'])
    rails=shared_rail_bounds()
    wirecontext=cKDTree(field['W043_context']) if joint else None
    s1context=cKDTree(field['S1_context']) if joint else None
    required=dict(material=1.25,reservation=1.25,motion36=1.25,outer=3.25,wire_wire=.2)
    screen=dict(material=.2,reservation=.2,motion36=.2,outer=1,curve_hold=3.35)
    result=dict(status='RUNNING_WHOLE20_FLAT_DOMAINS',selected=False,N01_complete=False,physical_pass=False,
        source_sha256={**proof['source_sha256'],**{p.relative_to(ROOT).as_posix():sha(p) for p in
            (planfile,fieldproof,fieldfile,Path(__file__),Path(__file__).with_name('feline_flat_station_templates.py'))}},
        actual_required_airgaps_NOT_changed_mm=required,numeric_loose_prefilter_mm=screen,
        numeric_surface_field_not_solid_interior_or_actual_clearance=True,
        common_rail_bounds_mm=[r.tolist() for r in rails],common_rail_roots_actual_clamps_tools_NOT_approved=True,
        source_nominal_cases_proven_full_boxes_by_validity_solidcount_volume=True,
        all_caps_one_common_head_not_five_heads=True,
        source_lever_UP_uses_actual_source_handedness_not_blanket_pitch_rule=True,
        conditional_frame_replacement=proof['conditional_frame_replacement'],
        complete_grip_external_budget=True,delivered_fit_and_tie_length_stock_still_OPEN=True,
        S1_four_clocked_rings_all8HELU_and123portions246ends_NOT_qualified=True,
        domains={},completed_sources=[],joint_assignment=None,failures=[],errors=[])
    def gate():
        if time.monotonic()-tick>180:raise TimeoutError('180s whole20 domains; completed per-source results retained')
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def batch(templates,centres,identity=False):
        # All objects in each block have the SAME template. Avoid thousands
        # of independent interpolator calls and keep per-source receipts.
        template=templates;p0=template['points'];rr=template['radii'];tt=template['types'];out=[]
        for offset in range(0,len(centres),8):
            gate();cc=np.array(centres[offset:offset+8]);p=p0[None,:,:]+cc[:,None,:]
            flat=p.reshape(-1,3);count=len(p0)
            mask=inside(flat).reshape(len(cc),count).min(1)>=.999
            margin=np.full(len(cc),-1e6);limiting=['outside_numeric_grid']*len(cc)
            for i in np.flatnonzero(mask):
                # No hard rejection from bbox overlap; boxes only bounded
                # the source sampling, and fields only propose geometry.
                margin[i]=1e6;limiting[i]='none'
            live=np.flatnonzero(mask)
            if not len(live):out.extend(zip(margin,limiting));continue
            active=p[live].reshape(-1,3)
            for cat,interp in fields.items():
                values=(interp(active).reshape(len(live),count)-rr-screen[cat]).min(1)
                for i,value in zip(live,values):
                    if value<margin[i]:margin[i]=float(value);limiting[i]=cat
            sv=service(active).reshape(len(live),count).max(1)
            for i,v in zip(live,sv):
                if v>.5 and margin[i]>-.01:margin[i]=-.01;limiting[i]='ATO_functional_reservation'
            if not identity:
                values=(context.query(active,workers=1)[0].reshape(len(live),count)-rr-.2).min(1)
                for i,v in zip(live,values):
                    if v<margin[i]:margin[i]=float(v);limiting[i]='P_SYS_identity_context'
            if joint:
                for label,tree in (('W043_protected_whole',wirecontext),('S1_body_control_studs',s1context)):
                    allowed=np.ones(count,dtype=bool)
                    if identity and label=='W043_protected_whole':allowed=(tt!=0)&(tt!=4)
                    if label=='S1_body_control_studs':allowed=tt!=9
                    if allowed.any():
                        values=(tree.query(p[live][:,allowed].reshape(-1,3),workers=1)[0].reshape(len(live),-1)-rr[allowed]-.2).min(1)
                        for i,v in zip(live,values):
                            if v<margin[i]:margin[i]=float(v);limiting[i]=label
            # Carrier roots may unite with rails. Every purchased case,
            # wire, cap/band/head must independently clear their reserved span.
            nonroot=tt!=3
            for rail in rails:
                for i in live:
                    v=float(np.min(to_box(p[i,nonroot],rail)-rr[nonroot]-.2))
                    if v<margin[i]:margin[i]=v;limiting[i]='common_rail_reservation'
            out.extend(zip(margin,limiting))
        return out
    mapping=json.loads((OUT/'n01-whole-constraint-map.json').read_text())
    def outer_columns(side):
        rows=[r['world_bounds_mm'] for r in mapping['parts'] if r['name'].startswith('Ref_Material_F_') and
              '_Housing_' in r['name'] and np.sign(sum(np.array(r['world_bounds_mm'])[:,1]))==side]
        rows.sort(key=lambda r:r[0][0]);assert len(rows)==6
        mid=[(a[1][0]+b[0][0])/2 for a,b in zip(rows,rows[1:])]
        # Fore/rear columns outside bank extent come from whole torso ends,
        # not a hand adjustment to one failed connector.
        return [-112,-88]+mid+[rows[-1][1][0]+24,rows[-1][1][0]+48,rows[-1][1][0]+72]
    save();domains={};stats={}
    try:
        stations=sorted(plan['stations'],key=lambda s:(not s['fixed_identity_pose'],
                       -s['flat_dimensions_pitch_departure_thickness_mm'][2],-len(s['ports'])))
        for station in stations:
            gate();ref=station['ref'];choices=[];tested=0;rejected={};best=None
            families=['inner'] if station['fixed_identity_pose'] else station['row_families']
            for family in families:
                for side in ([1] if station['fixed_identity_pose'] else (-1,1)):
                    for departure in ([-1] if station['fixed_identity_pose'] else (-1,1)):
                        template=build(station,family,side,departure,0)
                        assert self_wire_gap(template)>=-1e-6
                        if station['fixed_identity_pose']:xx=[0]
                        elif family=='outer':
                            depth=station['flat_dimensions_pitch_departure_thickness_mm'][1]
                            xx=[x-departure*(depth/2+9+station['shared_fan_R_mm']) for x in outer_columns(side)]
                        else:xx=list(range(-112,149,12))
                        cc=[[x,0,0] for x in xx]
                        receipts=batch(template,cc,station['fixed_identity_pose'])
                        for x,(score,layer) in zip(xx,receipts):
                            tested+=1;row=dict(family=family,side=side,departure=departure,centre_x=x,score=float(score),limiting_layer=layer)
                            if score<0:
                                rejected[layer]=rejected.get(layer,0)+1
                                if best is None or score>best['score']:best=row
                                continue
                            m=build(station,family,side,departure,x)
                            if not pier_supported(m):
                                rejected['finite_carrier_pier_missing']=rejected.get('finite_carrier_pier_missing',0)+1
                                continue
                            m['numeric_score']=float(score);choices.append(m)
            choices.sort(key=lambda m:-m['numeric_score'])
            # No top-N pruning removes a necessary location. Preserve all
            # received complete-module domains for the one common CSP.
            domains[ref]=choices
            result['domains'][ref]=[compact(m) for m in choices]
            result['completed_sources'].append(dict(ref=ref,tested=tested,received=len(choices),rejected_layers=rejected,best_rejected_numeric=best))
            save();print(ref,'whole module domains',len(choices),'/',tested,flush=True)
        if joint:
            from feline_flat_s1_templates import candidates,source_pair_compatible
            sourcechoices,sourcepins=candidates();result['source_sha256'].update(sourcepins)
            result['S1_joint_domains']={}
            for name,choices in sourcechoices.items():
                gate();accepted=[];rejected={}
                for m in choices:
                    score,layer=batch(m,[[0,0,0]])[0]
                    if score>=0:m['numeric_score']=float(score);accepted.append(m)
                    else:rejected[layer]=rejected.get(layer,0)+1
                accepted.sort(key=lambda m:-m['numeric_score']);domains[name]=accepted
                result['S1_joint_domains'][name]=[compact(m) for m in accepted]
                result['completed_sources'].append(dict(ref=name,tested=len(choices),received=len(accepted),rejected_layers=rejected))
                save();print(name,'source full ring/fan/grip/head domains',len(accepted),flush=True)
        empty=[n for n,v in domains.items() if not v];result['empty_domains']=empty
        if empty:
            result['status']='WHOLE20_BOUNDED_FLAT_FAMILY_HAS_EMPTY_DOMAINS_NOT_GLOBAL_INFEASIBILITY'
            save();print(json.dumps(dict(status=result['status'],empty=empty,seconds=result['worker_seconds'])),flush=True);return
        memo={};visited=0;cap=10000
        def pair(a,i,b,j):
            key=(a,i,b,j) if a<b else (b,j,a,i)
            if key not in memo:
                aa,bb=domains[a][i],domains[b][j]
                memo[key]=source_pair_compatible(aa,bb) if aa.get('source_ring') or bb.get('source_ring') else compatible(aa,bb)
            return memo[key]
        def solve(chosen,remaining):
            nonlocal visited
            gate();visited+=1
            if visited>cap:raise TimeoutError('10000whole joint search nodes; retain all domains')
            if not remaining:return chosen
            feasible={}
            for name,values in remaining.items():
                values=[i for i in values if all(pair(name,i,a,j) for a,j in chosen.items())]
                if not values:return None
                feasible[name]=values
            name=min(feasible,key=lambda n:len(feasible[n]));nextremaining={n:v for n,v in feasible.items() if n!=name}
            for index in feasible[name]:
                found=solve({**chosen,name:index},nextremaining)
                if found:return found
            return None
        assignment=solve({}, {n:list(range(len(v))) for n,v in domains.items()})
        result['joint_assignment']=assignment;result['search_nodes']=visited;result['numeric_mutual_pairs']=len(memo)
        if assignment:
            result['chosen_templates']={n:compact(domains[n][i]) for n,i in assignment.items()}
            result['chosen_wire_recipes']=[{k:v for k,v in w.items() if k!='points'}
                 for n,i in assignment.items() for w in domains[n][i]['wires']]
            assert len(result['chosen_templates'])==(24 if joint else 20) and len(result['chosen_wire_recipes'])==85
            result['status']='WHOLE20_NUMERIC_PROPOSAL_REQUIRES_ONE_EXACT_RECEIVER_AND_FULL_N01'
        else:result['status']='WHOLE20_NO_JOINT_ASSIGNMENT_IN_THIS_BOUNDED_FAMILY'
    except Exception as e:result['errors'].append(repr(e));result['status']='PARTIAL_WHOLE20_FLAT_DOMAINS'
    save();print(json.dumps({k:result[k] for k in ('status','worker_seconds','joint_assignment','errors')}),flush=True)


if __name__=='__main__':main()
