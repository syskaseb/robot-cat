"""Reuse47 received kit domains with all6 current source fans, not oldS1.

This is a joint PROPOSAL, not exact clearance: surface samples can miss
penetration. The selected complete assembly still requires actual solids,
all246ends/factorycorridors/root/access before N01.
"""
import hashlib
import json
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


def saved47():
    path=OUT/'n01-whole51-joint-proposal.json';old=json.loads(path.read_text())
    for n in ('feline_flat_station_templates.py','feline_bank_anchor_templates.py','feline_pwm_pigtail_templates.py'):
        rel='tools/cad/'+n;assert sha(ROOT/rel)==old['source_sha256'][rel],rel
    plan=json.loads((OUT/'n01-flat-station-architecture.json').read_text());groups={}
    for st in plan['stations']:
        groups[st['ref']]=[build(st,r['family'],r['side'],r['departure_X'],r['centre_mm'][0],
            r.get('centre_y_override_mm'),r.get('bend_mode','OUTWARD_CONCENTRIC'),r.get('closure_mode','AUTO')) for r in old['domains'][st['ref']]]
    proof=json.loads((OUT/'n01-flat20-field-modulejoint.json').read_text())
    extra=bank_candidates(proof);anchors,receipts,pins=anchor_candidates(old['actual_anchor_parent_receipts']);extra.update(anchors)
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
    tick=time.monotonic();dest=OUT/'n01-shared53-proposal.json';assert not dest.exists()
    result=dict(status='RUNNING_SHARED53_NUMERIC_PROPOSAL',N01_complete=False,physical_pass=False,selected=False,
        domains={},errors=[],joint_assignment=None,numeric_only_not_actual_clearance=True,
        open=['Actual selected53static/mutual/motion','246ends/factorycorridors/roots/tools/assembly'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    groups,pins=saved47();fanfile=OUT/'n01-six-source-shared-lanes.json';fans=json.loads(fanfile.read_text())
    corefile=OUT/'n01-six-source-current-core.json';core,cp,cr=packed(corefile)
    assert not core['all_current_blockers']['failures'] and not core['all_current_blockers']['errors']
    assert len(fans['complete_ports'])==6 and not fans['errors']
    # Sample only the current macro, never the obsolete original source pose.
    fixed=[];fixednames=[]
    for n,s in cp.items():
        points=cloud(s);fixed.append(points);fixednames.extend([n]*len(points))
    tree=cKDTree(np.vstack(fixed));result['current121_surface_sample_count']=tree.n
    result['old47_source_domains_reused_as_candidates_NOT_old_world_acceptance']=True
    # Conservative sample guard for ranking/rejection; no positive claim from
    # unsigned distance. Named common-carrier root unions are left for actual
    # ownership checks, not treated as purchased module penetration.
    for name,options in list(groups.items()):
        filtered=[];rejected=0;best=None
        for m in options:
            mask=m['types']!=3
            p=m['points'][mask];rr=m['radii'][mask]
            dd,indices=tree.query(p,workers=1);margins=dd-rr;ix=int(np.argmin(margins));gap=float(margins[ix])
            witness=dict(unsigned_surface_gap_minus_radius_mm=gap,source=fixednames[int(indices[ix])],point_mm=p[ix].tolist(),recipe=compact(m))
            if best is None or gap>best['unsigned_surface_gap_minus_radius_mm']:best=witness
            if gap>=2.75:m['current_macro_unsigned_proposal_margin']=gap;filtered.append(m)
            else:rejected+=1
        groups[name]=filtered
        result['domains'][name]=dict(received=len(options),retained=len(filtered),rejected_near_current_macro_samples=rejected,best_received_proposal_witness=best)
        save()
    shapes={}
    with zipfile.ZipFile(ROOT/fans['bundle']) as z:
        for r in fans['parts']:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());shapes[r['name']]=s
    for name,options in fans['domains'].items():
        groups[name]=[]
        for option in options:
            pp=[];tt=[]
            for r in option['parts']:
                points=cloud(shapes[r['name']]);pp.append(points);tt.extend([1 if r['kind']=='wire' else 2]*len(points))
            points=np.vstack(pp)
            groups[name].append(dict(option,ref=name,source_fan_actual=True,points=points,types=np.array(tt),
                radii=np.zeros(len(points)),bounds=np.array([points.min(0),points.max(0)]),boxes=[],wires=[]))
        result['domains'][name]=dict(received=len(options),retained=len(options),individual_actual_received=True)
    result['source_sha256']={**pins,fanfile.relative_to(ROOT).as_posix():sha(fanfile),corefile.relative_to(ROOT).as_posix():sha(corefile),
        core['bundle']:core['bundle_sha256'],Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))}
    empty=[n for n,v in groups.items() if not v];result['empty_domains']=empty;save()
    if empty:
        result['status']='SHARED53_SAMPLE_PREFILTER_EMPTY_NOT_GLOBAL_INFEASIBILITY';save();print(json.dumps(dict(status=result['status'],empty=empty,seconds=result['worker_seconds'])));return
    memo={};trees={};visited=0
    def pair(a,i,b,j):
        key=(a,i,b,j) if a<b else (b,j,a,i)
        if key in memo:return memo[key]
        aa,bb=groups[a][i],groups[b][j]
        if box_gap(aa['bounds'],bb['bounds'])>=2.75:value=True
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
        if time.monotonic()-tick>240 or visited>10000:raise TimeoutError('Bounded joint proposal; preserve domains')
        if not remaining:return chosen
        viable={n:[i for i in opts if all(pair(n,i,o,j) for o,j in chosen.items())] for n,opts in remaining.items()}
        if any(not opts for opts in viable.values()):return None
        n=min(viable,key=lambda n:len(viable[n]));other={k:v for k,v in viable.items() if k!=n}
        for i in viable[n]:
            answer=solve({**chosen,n:i},other)
            if answer is not None:return answer
        return None
    try:
        answer=solve({}, {n:list(range(len(v))) for n,v in groups.items()})
        result.update(joint_assignment=answer,search_nodes=visited,numeric_mutual_pairs=len(memo))
        if answer:result['chosen_templates']={n:compact(groups[n][i]) for n,i in answer.items()}
        result['status']='SHARED53_NUMERIC_PROPOSAL_EXACT_CHECK_REQUIRED' if answer else 'SHARED53_BOUNDED_NO_ASSIGNMENT_NOT_GLOBAL_PROOF'
    except Exception as e:result['errors'].append(repr(e));result['status']='SHARED53_PARTIAL_OR_ERROR_NOT_ACCEPTANCE'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],assignment=result['joint_assignment'],errors=result['errors'])),flush=True)


if __name__=='__main__':
    import os
    print('WORKER_PID',os.getpid(),flush=True);main()
