"""Reuse47 received kit domains with all6 current source fans, not oldS1.

This is a joint PROPOSAL, not exact clearance: surface samples can miss
penetration. The selected complete assembly still requires actual solids,
all246ends/factorycorridors/root/access before N01.
"""
import hashlib
import json
import sys
import time
import zipfile
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from plan_feline_joint_fore_domains import cloud
from feline_flat_station_templates import build,compact,compatible,box_gap,to_box
from feline_bank_anchor_templates import bank_candidates,anchor_candidates
from feline_pwm_pigtail_templates import candidates as pwm_candidates
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound


def sparse(shape):
    return np.unique(np.array([list(v.Point) for v in shape.Vertexes]+[list(f.CenterOfMass) for f in shape.Faces]),axis=0)


def saved47(fast=False):
    path=OUT/'n01-whole51-joint-proposal.json';old=json.loads(path.read_text())
    for n in ('feline_flat_station_templates.py','feline_bank_anchor_templates.py','feline_pwm_pigtail_templates.py'):
        rel='tools/cad/'+n;assert sha(ROOT/rel)==old['source_sha256'][rel],rel
    plan=json.loads((OUT/'n01-flat-station-architecture.json').read_text());groups={}
    for st in plan['stations']:
        groups[st['ref']]=[build(st,r['family'],r['side'],r['departure_X'],r['centre_mm'][0],
            r.get('centre_y_override_mm'),r.get('bend_mode','OUTWARD_CONCENTRIC'),r.get('closure_mode','AUTO')) for r in old['domains'][st['ref']]]
    proof=json.loads((OUT/'n01-flat20-field-modulejoint.json').read_text())
    extra=bank_candidates(proof)
    if fast:
        fp=OUT/'n01-flat20-actual-clamp-kits.json';hardware=json.loads(fp.read_text());records={r['name']:r for r in hardware['parts']}
        anchors={};pins={fp.relative_to(ROOT).as_posix():sha(fp)}
        from feline_flat_station_templates import box_points
        for name in ('Anchor:Fore','Anchor:Rear'):
            anchors[name]=[]
            for r in old['domains'][name]:
                points=[];boxes=[];delta=np.array([r['axis_X_mm']-r['source_axis_X_mm'],0,0])
                for part in r['actual_parts']:
                    bounds=np.array(records[part['name']]['bounds_mm'])+delta
                    points.append(box_points(*bounds,step=4));boxes.append(dict(name=part['name'],bounds=bounds,kind=7))
                pp=np.vstack(points)
                anchors[name].append(dict(r,points=pp,types=np.full(len(pp),7),radii=np.zeros(len(pp)),
                    bounds=np.array([pp.min(0),pp.max(0)]),boxes=boxes,wires=[],
                    conservative_per_piece_bboxes_NOT_exact_free_space=True))
    else:anchors,receipts,pins=anchor_candidates(old['actual_anchor_parent_receipts'])
    extra.update(anchors)
    pwm,more=pwm_candidates();extra.update(pwm)
    def key(m):
        if m.get('bank_source'):return m['bend_clock_degrees'],m['complete_band_head_degrees']
        if m.get('anchor_source'):return m['axis_X_mm']
        return tuple(m['centre_mm']),tuple(m['head_choices'])
    for name,options in extra.items():
        bykey={key(m):m for m in options};groups[name]=[bykey[key(r)] for r in old['domains'][name]]
    assert len(groups)==47 and all(groups.values())
    return groups,{**pins,**more,path.relative_to(ROOT).as_posix():sha(path)}


def main():
    tick=time.monotonic();dest=OUT/'n01-shared53-proposal.json';resume='--resume-lazy' in sys.argv;fast='--joint-fast' in sys.argv or resume
    previous=json.loads(dest.read_text()) if dest.exists() else None
    if previous:assert fast and (previous['status']=='INTERRUPTED_EXPENSIVE_UNSIGNED_PREFILTER_NOT_ACCEPTANCE' or resume and 'received_recipes' in previous)
    if resume:
        for name,value in previous['source_sha256'].items():
            if name==Path(__file__).relative_to(ROOT).as_posix():continue
            assert sha(ROOT/name)==value,name
    result=dict(status='RUNNING_SHARED53_NUMERIC_PROPOSAL',N01_complete=False,physical_pass=False,selected=False,
        domains={},errors=[],joint_assignment=None,numeric_only_not_actual_clearance=True,
        open=['Actual selected53static/mutual/motion','246ends/factorycorridors/roots/tools/assembly',
              'Separate P309monitor case/retention and conditional4tap factory balance space; no GTech cavity invention'])
    if previous:
        if 'owned_worker_stop' in previous:result['previous_dense_diagnostic']=dict(commit='b89447bb',receipt_sha256=sha(dest),worker_stop=previous['owned_worker_stop'],saved_nodes=len(previous['domains']))
        else:result['previous_dense_diagnostic']=previous.get('previous_dense_diagnostic')
        result['solver_history']=previous.get('solver_history',[])+[dict(status=previous['status'],worker_seconds=previous['worker_seconds'],errors=previous['errors'],receipt_sha256=sha(dest))]
        if resume:
            result['received_recipes']=previous['received_recipes']
            result['lazy_conflict_cuts']=previous.get('lazy_conflict_cuts',[])
            result['numeric_pair_cache']=previous.get('numeric_pair_cache',[])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    groups,pins=saved47(fast);fanfile=OUT/'n01-six-source-shared-lanes.json';fans=json.loads(fanfile.read_text())
    corefile=OUT/'n01-six-source-current-core.json';core,cp,cr=packed(corefile)
    assert not core['all_current_blockers']['failures'] and not core['all_current_blockers']['errors']
    assert len(fans['complete_ports'])==6 and not fans['errors']
    # Sample only the current macro, never the obsolete original source pose.
    fixed=[];fixednames=[]
    for n,s in (() if resume else cp.items()):
        points=sparse(s) if fast else cloud(s);fixed.append(points);fixednames.extend([n]*len(points))
    tree=None if resume else cKDTree(np.vstack(fixed));result['current121_surface_sample_count']=previous['current121_surface_sample_count'] if resume else tree.n
    if resume:result['domains']=previous['domains'];result['prior_ranker_not_requeried']=True
    result['old47_source_domains_reused_as_candidates_NOT_old_world_acceptance']=True
    # Conservative sample guard for ranking/rejection; no positive claim from
    # unsigned distance. Named common-carrier root unions are left for actual
    # ownership checks, not treated as purchased module penetration.
    for name,options in list(groups.items()):
        if resume:continue
        filtered=[];rejected=0;best=None
        for m in options:
            mask=m['types']!=3
            p=m['points'][mask];rr=m['radii'][mask]
            if fast and len(p)>512:
                ix=np.linspace(0,len(p)-1,512,dtype=int);p=p[ix];rr=rr[ix]
            dd,indices=tree.query(p,workers=1);margins=dd-rr;ix=int(np.argmin(margins));gap=float(margins[ix])
            witness=dict(unsigned_surface_gap_minus_radius_mm=gap,source=fixednames[int(indices[ix])],point_mm=p[ix].tolist(),recipe=compact(m))
            if best is None or gap>best['unsigned_surface_gap_minus_radius_mm']:best=witness
            if fast or gap>=2.75:m['current_macro_unsigned_proposal_margin']=gap;filtered.append(m)
            else:rejected+=1
        groups[name]=filtered
        if fast:groups[name].sort(key=lambda m:-m['current_macro_unsigned_proposal_margin'])
        result['domains'][name]=dict(received=len(options),retained=len(filtered),rejected_near_current_macro_samples=rejected,best_received_proposal_witness=best)
        save()
    shapes={};actualmeta={}
    with zipfile.ZipFile(ROOT/fans['bundle']) as z:
        for r in fans['parts']:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());shapes[r['name']]=s
            actualmeta[r['name']]={'kind':'proposal_wire' if r['kind']=='wire' else 'project_stock_reservation' if 'budget' in r['kind'] else 'proposal_material'}
    for name,options in fans['domains'].items():
        groups[name]=[]
        for option in options:
            pp=[];tt=[]
            for r in option['parts']:
                points=sparse(shapes[r['name']]) if fast else cloud(shapes[r['name']]);pp.append(points);tt.extend([1 if r['kind']=='wire' else 2]*len(points))
            points=np.vstack(pp)
            groups[name].append(dict(option,ref=name,source_fan_actual=True,points=points,types=np.array(tt),
                radii=np.zeros(len(points)),bounds=np.array([points.min(0),points.max(0)]),boxes=[],wires=[]))
        result['domains'][name]=dict(received=len(options),retained=len(options),individual_actual_received=True)
    if fast:
        path=OUT/'n01-bank-W027-open-saddle.json';opened=json.loads(path.read_text());assert opened['domains']
        assert sha(ROOT/opened['bundle'])==opened['bundle_sha256']
        options=[]
        with zipfile.ZipFile(ROOT/opened['bundle']) as z:
            for r in opened['parts']:
                raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode());shapes[r['name']]=s
                actualmeta[r['name']]={'kind':'proposal_wire' if r['kind']=='wire' else 'project_stock_reservation' if 'budget' in r['kind'] else 'proposal_material'}
        for option in opened['domains']:
            chunks=[sparse(shapes[r['name']]) for r in option['parts']];pp=np.vstack(chunks)
            types=np.concatenate([np.full(len(p),1 if r['kind']=='wire' else 2) for p,r in zip(chunks,option['parts'])])
            options.append(dict(option,points=pp,types=types,radii=np.zeros(len(pp)),
                boxes=[],wires=[],bounds=np.array([pp.min(0),pp.max(0)])))
        groups['Bank:W027/single/end']=options
        result['domains']['Bank:W027/single/end']=dict(received=2,retained=len(options),open_saddle_actual_current121_ownTE=True)
        pins.update({path.relative_to(ROOT).as_posix():sha(path),opened['bundle']:opened['bundle_sha256']})
        result['fast_proposal_policy']=dict(vertices_faces_only_ranking_NOT_acceptance=True,max_rank_samples_per_candidate=512,
            old_candidates_not_discarded_by_unsigned_rank=True,anchor_boxes_conservative_per_piece=True,
            requires_exact_selected_solids_and_own_clamp_channels=True)
    if resume:
        def fingerprint(m):
            r=dict(compact(m));r.pop('current_macro_unsigned_proposal_margin',None)
            return json.dumps(r,sort_keys=True,separators=(',',':'))
        for n,options in list(groups.items()):
            bykey={fingerprint(m):m for m in options};ordered=[]
            for r in previous['received_recipes'][n]:
                m=bykey[fingerprint(r)]
                if 'current_macro_unsigned_proposal_margin' in r:m['current_macro_unsigned_proposal_margin']=r['current_macro_unsigned_proposal_margin']
                ordered.append(m)
            groups[n]=ordered
    result['source_sha256']={**pins,fanfile.relative_to(ROOT).as_posix():sha(fanfile),corefile.relative_to(ROOT).as_posix():sha(corefile),
        core['bundle']:core['bundle_sha256'],Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))}
    empty=[n for n,v in groups.items() if not v];result['empty_domains']=empty;save()
    if empty:
        result['status']='SHARED53_SAMPLE_PREFILTER_EMPTY_NOT_GLOBAL_INFEASIBILITY';save();print(json.dumps(dict(status=result['status'],empty=empty,seconds=result['worker_seconds'])));return
    result['received_recipes']={n:[compact(m) for m in options] for n,options in groups.items()}
    memo={};trees={};visited=0;solver_tick=time.monotonic();qcache=SolidQueries()
    priorjoint=json.loads((OUT/'n01-source-joint-allocation.json').read_text())
    actualreceipts={tuple(sorted((r['part'],r['other']))):r for r in priorjoint['pairs']+(previous.get('source_actual_mutual_new_queries',[]) if resume else [])}
    result['source_actual_mutual_new_queries']=[]
    def pair(a,i,b,j):
        key=(a,i,b,j) if a<b else (b,j,a,i)
        if key in memo:return memo[key]
        aa,bb=groups[a][i],groups[b][j]
        if aa.get('anchor_source') and bb.get('anchor_source'):
            fore=aa if a=='Anchor:Fore' else bb;rear=bb if b=='Anchor:Rear' else aa;value=rear['axis_X_mm']-fore['axis_X_mm']>=90
        elif box_gap(aa['bounds'],bb['bounds'])>=2.75:value=True
        elif all(x.get('source_fan_actual') or x.get('bank_simple_source') for x in (aa,bb)):
            value=True
            for ar in aa['parts']:
                for br in bb['parts']:
                    n,o=ar['name'],br['name'];s,t=shapes[n],shapes[o]
                    minimum=pair_spacing(n,actualmeta[n],o,actualmeta[o])
                    if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                    receipt=actualreceipts.get(tuple(sorted((n,o))))
                    if receipt and receipt['minimum_mm']==minimum:gap=receipt['gap_mm']
                    else:
                        gap=qcache.distance(s,t);receipt=dict(part=n,other=o,gap_mm=gap,minimum_mm=minimum)
                        actualreceipts[tuple(sorted((n,o)))]=receipt;result['source_actual_mutual_new_queries'].append(receipt)
                    if gap<minimum-1e-6:value=False;break
                if not value:break
        elif aa.get('anchor_source') and bb.get('anchor_source'):
            fore=aa if a=='Anchor:Fore' else bb;rear=bb if b=='Anchor:Rear' else aa;value=rear['axis_X_mm']-fore['axis_X_mm']>=90
        elif not any(x.get('bank_source') or x.get('anchor_source') or x.get('f_pwm_source') or x.get('source_fan_actual') for x in (aa,bb)):
            value=compatible(aa,bb)
        else:
            value=True
            for group,other in ((aa,bb),(bb,aa)):
                for box in other['boxes']:
                    if group.get('anchor_source') and box['kind']==3:continue
                    if float(np.min(to_box(group['points'],box['bounds'])-group['radii']))<1.25:value=False;break
                if not value:break
            if value:
                keytree=(b,j,bool(aa.get('anchor_source')))
                maskb=bb['types']!=3 if aa.get('anchor_source') else np.ones(len(bb['points']),bool)
                maska=aa['types']!=3 if bb.get('anchor_source') else np.ones(len(aa['points']),bool)
                if keytree not in trees:trees[keytree]=cKDTree(bb['points'][maskb]),bb['radii'][maskb],bb['types'][maskb]
                tr,rr,tt=trees[keytree];dd,ii=tr.query(aa['points'][maska],workers=1)
                req=np.where((aa['types'][maska]==1)&(tt[ii]==1),.2,1.25)
                value=float(np.min(dd-aa['radii'][maska]-rr[ii]-req))>=-1e-5
        memo[key]=value;return value
    def solve(chosen,remaining):
        nonlocal visited
        visited+=1
        if time.monotonic()-solver_tick>120 or visited>10000:raise TimeoutError('Bounded joint solver after setup; retain ALL recipes, no repeated preprocessing')
        if not remaining:return chosen
        viable={n:[i for i in opts if all(pair(n,i,o,j) for o,j in chosen.items())] for n,opts in remaining.items()}
        if any(not opts for opts in viable.values()):return None
        n=min(viable,key=lambda n:len(viable[n]));other={k:v for k,v in viable.items() if k!=n}
        for i in viable[n]:
            answer=solve({**chosen,n:i},other)
            if answer is not None:return answer
        return None
    def lazy_milp():
        from scipy.optimize import milp,Bounds,LinearConstraint
        from scipy.sparse import coo_matrix
        names=list(groups);variables=[(n,i) for n in names for i in range(len(groups[n]))];index={v:i for i,v in enumerate(variables)}
        cuts={tuple(sorted(c)) for c in (previous.get('lazy_conflict_cuts',[]) if resume else [])}
        # Fast exact case-envelope exclusions establish the SHARED layout,
        # not just repeated choices around the last failed wire.
        for ia,a in enumerate(names):
            for b in names[ia+1:]:
                if a.startswith('Anchor:') and b.startswith('Anchor:'):
                    for i in range(len(groups[a])):
                        for j in range(len(groups[b])):
                            if not pair(a,i,b,j):cuts.add(tuple(sorted((index[a,i],index[b,j]))))
                ac=[(i,next((x['bounds'] for x in m['boxes'] if x['kind']==0),None)) for i,m in enumerate(groups[a])]
                bc=[(j,next((x['bounds'] for x in m['boxes'] if x['kind']==0),None)) for j,m in enumerate(groups[b])]
                for i,aa in ac:
                    if aa is None:continue
                    for j,bb in bc:
                        if bb is not None and box_gap(aa,bb)<1.25-1e-5:cuts.add(tuple(sorted((index[a,i],index[b,j]))))
        result['lazy_iterations']=[];result['lazy_engine']='InstalledSciPyHiGHS one-hot with exactcase exclusions and learned numeric kit conflicts; still a proposal'
        objective=np.array([i/max(1,len(groups[n])) for n,i in variables],float)
        for iteration in range(100):
            if time.monotonic()-solver_tick>240:raise TimeoutError('Lazy solver budget; all recipes/cuts retained')
            row=[];col=[];data=[];lo=[];hi=[]
            for n in names:
                rr=len(lo)
                for i in range(len(groups[n])):row.append(rr);col.append(index[n,i]);data.append(1.)
                lo.append(1.);hi.append(1.)
            for x,y in sorted(cuts):
                rr=len(lo);row.extend((rr,rr));col.extend((x,y));data.extend((1.,1.));lo.append(-np.inf);hi.append(1.)
            matrix=coo_matrix((data,(row,col)),shape=(len(lo),len(variables))).tocsc()
            fit=milp(objective,integrality=np.ones(len(variables)),bounds=Bounds(0,1),
                constraints=LinearConstraint(matrix,lo,hi),options={'time_limit':15,'mip_rel_gap':0.0,'presolve':True})
            result['lazy_conflict_cuts']=[list(c) for c in sorted(cuts)]
            if fit.x is None:
                result['lazy_iterations'].append(dict(iteration=iteration,solver_status=int(fit.status),cuts=len(cuts),message=str(fit.message)));save()
                if fit.status==2:return None
                raise TimeoutError('MIP has no incumbent within its bounded slice; cuts/recipes saved')
            chosen={n:max(range(len(groups[n])),key=lambda i:fit.x[index[n,i]]) for n in names}
            assert all(fit.x[index[n,i]]>.5 for n,i in chosen.items())
            bad=[]
            for ia,a in enumerate(names):
                for b in names[ia+1:]:
                    if not pair(a,chosen[a],b,chosen[b]):bad.append((a,chosen[a],b,chosen[b]))
            for a,i,b,j in bad:cuts.add(tuple(sorted((index[a,i],index[b,j]))))
            result['lazy_iterations'].append(dict(iteration=iteration,solver_status=int(fit.status),cuts=len(cuts),failed_selected_pairs=len(bad)))
            result['lazy_conflict_cuts']=[list(c) for c in sorted(cuts)]
            result['numeric_pair_cache']=[list(k)+[v] for k,v in memo.items()]
            save();print('Whole53 lazy',iteration,'conflicts',len(bad),'cuts',len(cuts),flush=True)
            if not bad:return chosen
        raise TimeoutError('100 bounded whole-layout iterations; recipes/cuts retained')
    if resume:
        for record in previous.get('numeric_pair_cache',[]):
            a,i,b,j,value=record
            if not (a.startswith('Anchor:') and b.startswith('Anchor:')):memo[(a,i,b,j)]=value
    save()
    try:
        answer=lazy_milp() if resume else solve({}, {n:list(range(len(v))) for n,v in groups.items()})
        result.update(joint_assignment=answer,search_nodes=visited,numeric_mutual_pairs=len(memo))
        if answer:result['chosen_templates']={n:compact(groups[n][i]) for n,i in answer.items()}
        result['status']='SHARED53_NUMERIC_PROPOSAL_EXACT_CHECK_REQUIRED' if answer else 'SHARED53_BOUNDED_NO_ASSIGNMENT_NOT_GLOBAL_PROOF'
    except Exception as e:
        result['errors'].append(repr(e));result['status']='SHARED53_PARTIAL_OR_ERROR_NOT_ACCEPTANCE'
        result['numeric_pair_cache']=[list(k)+[v] for k,v in memo.items()]
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],assignment=result['joint_assignment'],errors=result['errors'])),flush=True)


def case_packing_diagnosis():
    """Test the actual whole20 case catalogue before changing any wire."""
    from scipy.optimize import milp,Bounds,LinearConstraint
    from scipy.sparse import coo_matrix
    tick=time.monotonic();path=OUT/'n01-shared53-proposal.json';doc=json.loads(path.read_text())
    plan=json.loads((OUT/'n01-flat-station-architecture.json').read_text());models={};variables=[];bounds=[]
    for st in plan['stations']:
        name=st['ref'];models[name]=[]
        for r in doc['received_recipes'][name]:
            m=build(st,r['family'],r['side'],r['departure_X'],r['centre_mm'][0],r.get('centre_y_override_mm'),r.get('bend_mode','OUTWARD_CONCENTRIC'),r.get('closure_mode','AUTO'))
            b=next(x['bounds'] for x in m['boxes'] if x['kind']==0)
            models[name].append(m);variables.append((name,len(models[name])-1));bounds.append(b)
    row=[];col=[];data=[];low=[];high=[];names=list(models)
    for name in names:
        rr=len(low)
        for v,(n,i) in enumerate(variables):
            if n==name:row.append(rr);col.append(v);data.append(1.)
        low.append(0.);high.append(1.)
    conflicts=0
    for x,(a,i) in enumerate(variables):
        for y in range(x+1,len(variables)):
            b,j=variables[y]
            if a==b:continue
            if box_gap(bounds[x],bounds[y])<1.25-1e-5:
                rr=len(low);row.extend((rr,rr));col.extend((x,y));data.extend((1.,1.));low.append(-np.inf);high.append(1.);conflicts+=1
    matrix=coo_matrix((data,(row,col)),shape=(len(low),len(variables))).tocsc()
    fit=milp(-np.ones(len(variables)),integrality=np.ones(len(variables)),bounds=Bounds(0,1),
        constraints=LinearConstraint(matrix,low,high),options={'time_limit':20,'mip_rel_gap':0.0})
    chosen={} if fit.x is None else {n:i for v,(n,i) in enumerate(variables) if fit.x[v]>.5}
    result=dict(status='BOUNDED_CASE_CATALOGUE_MAX_PACKING_NOT_N01',solver_status=int(fit.status),message=str(fit.message),
        optimal_proven=fit.status==0,case_count=len(names),incumbent_case_count=len(chosen),conflict_pairs=conflicts,
        omitted=[n for n in names if n not in chosen],selected={n:compact(models[n][i]) for n,i in chosen.items()},
        no_selected_parts_deleted_or_moved=True,bounded_catalogue_only_NOT_all_possible_layouts=True,
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3),
        generator_sha256=sha(Path(__file__)))
    doc['whole20_case_capacity']=result
    path.write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('solver_status','optimal_proven','incumbent_case_count','omitted','worker_seconds')}),flush=True)


if __name__=='__main__':
    import os
    print('WORKER_PID',os.getpid(),flush=True)
    if '--case-diagnose' in sys.argv:case_packing_diagnosis()
    else:main()
