"""Receive full factory/sleeve/custom packages, then mutual three-case packing.

The existing field ranks proposals only. Negative field margins are not
physical contacts; central source-hole candidates receive actual solids too.
No native CAD, selected parts or source electrical mapping are changed.
"""
import itertools
import json
import math
import hashlib
import subprocess
import sys
import time
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_full_factory_domains import full_profile_points
from feline_candidate_collision_scene import Scene
from feline_solid_distance import distance
from receive_feline_global_case_candidates import matrix_rotation,placement

FACTORY_MIN_MM=84.5


def recipe_shapes(row,candidate):
    q=np.array(row['point_mm']);d=np.array(row['departure_axis'])
    b=np.array(candidate['bend_unit']);first=candidate['first_mm'];R=12.4
    assert abs(np.linalg.norm(d)-1)<1e-8 and abs(np.linalg.norm(b)-1)<1e-8 and abs(np.dot(d,b))<1e-8
    assert first>=9 and 3+first+R*math.pi/2+14<=FACTORY_MIN_MM+1e-8
    start=q+d*first;mid=start+d*R/2**.5+b*R*(1-1/2**.5)
    end=start+d*R+b*R;tip=end+b*14
    def vec(x):return A.Vector(*x)
    edges=[]
    if first>9:edges.append(Part.makeLine(vec(q+d*9),vec(start)))
    edges.append(Part.Arc(vec(start),vec(mid),vec(end)).toShape())
    spine=Part.Wire(edges)
    profile=Part.Wire([Part.makeCircle(2,vec(q+d*9),vec(d))])
    continuation=spine.makePipeShell([profile],True,False)
    first9=Part.makeCylinder(2,9,vec(q),vec(d))
    sleeve=Part.makeCylinder(2.4,20,vec(end),vec(b))
    custom=Part.makeCylinder(1.55,26,vec(tip-b*8),vec(b))
    # Factory after-land lies wholly within sleeve, not omitted material.
    remaining=Part.makeCompound([continuation,sleeve,custom])
    whole=Part.makeCompound([first9,continuation,sleeve,custom])
    assert remaining.isValid() and whole.isValid()
    owncase_test=Part.makeCompound([Part.makeCylinder(2,6.5,vec(q+d*2.5),vec(d)),continuation,sleeve,custom])
    return remaining,whole,owncase_test


def all_ranked(row,interpolators):
    """Expand all existing recipes within84.5mm, without trusting field sign."""
    q=np.array(row['point_mm']);d=np.array(row['departure_axis'])
    u=np.eye(3)[int(np.argmin(abs(d)))];u-=d*np.dot(u,d);u/=np.linalg.norm(u);v=np.cross(d,u)
    profiles=[];points=[];radius=[];starts=[];count=0
    for first in (9,18,27,36,45,54,63):
        if 3+first+12.4*math.pi/2+14>FACTORY_MIN_MM+1e-8:continue
        for angle in np.linspace(0,2*math.pi,32,endpoint=False):
            b=u*math.cos(angle)+v*math.sin(angle);parts,_,_=full_profile_points(q,d,b,first)
            pp=np.vstack([parts[n] for n in ('factory','sleeve','custom')])
            rr=np.concatenate([np.full(len(parts[n]),r) for n,r in (('factory',2),('sleeve',2.4),('custom',1.55))])
            starts.append(count);count+=len(pp);points.append(pp);radius.append(rr)
            profiles.append(dict(first_mm=first,bend_unit=b.tolist(),R_mm=12.4))
    points=np.concatenate(points);radius=np.concatenate(radius);minimum=np.full(count,np.inf)
    for category,f in interpolators.items():
        allowance=3.25 if category=='outer' else .2 if category=='material' else 3.35 if category=='curve_hold' else 1.25
        values=f(points);assert np.all(np.isfinite(values))
        minimum=np.minimum(minimum,values-radius-allowance)
    margins=np.minimum.reduceat(minimum,np.array(starts))
    for p,m in zip(profiles,margins):p['numeric_min_surface_margin_mm']=float(m)
    return sorted(profiles,key=lambda p:(-p['numeric_min_surface_margin_mm'],p['first_mm']))


def main():
    tick=time.monotonic();source=OUT/'n01-global-full-factory-domains.json'
    central='--critical-central' in sys.argv;source_commit=None
    if '--source-commit' in sys.argv:
        source_commit=sys.argv[sys.argv.index('--source-commit')+1]
        raw=subprocess.run(['git','show',source_commit+':'+source.relative_to(ROOT).as_posix()],cwd=ROOT,check=True,capture_output=True).stdout
    else:raw=source.read_bytes()
    domains=json.loads(raw)
    assert domains['status']=='GLOBAL_ALL_END_DOMAINS_RECEIVED_FULL_CAD_TAILS_OPEN' or (central and source_commit and domains['status']=='PARTIAL_GLOBAL_FULL_FACTORY_DOMAINS')
    for n,h in domains['source_sha256'].items():assert sha(ROOT/n)==h,n
    scene=Scene();cellsfile=OUT/'n01-global-all-case-cells.json';cells=json.loads(cellsfile.read_text())
    cases={r['id']:r for r in cells['cells']};first={(r['case_id'],r['side']):r for r in domains['first_lands']}
    numeric={(r['case_id'],r['side']):r for r in domains['domains']}
    fieldfile=OUT/'n01-global-current-case-field.npz';field=np.load(fieldfile,allow_pickle=False)
    axes=[field[k] for k in ('x','y','z')]
    interpolators={k:RegularGridInterpolator(axes,field[k+'_distance'],bounds_error=False,fill_value=0) for k in ('material','reservation','motion36','curve_hold','outer')}
    pins=dict(scene.pins)
    reference=ROOT/'hardware/reference/fhac0001zxj-2026-10-02/README.md'
    for p in (cellsfile,fieldfile,reference,Path(__file__),Path(__file__).with_name('feline_solid_distance.py'),Path(__file__).with_name('plan_feline_full_factory_domains.py')):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    if not source_commit:pins[source.relative_to(ROOT).as_posix()]=sha(source)
    source_snapshot=dict(commit=source_commit,path=source.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest())
    dest=OUT/('n01-global-central-factory-packages.json' if central else 'n01-global-full-factory-packages.json')
    result=dict(status='RUNNING_FULL_FACTORY_PACKAGES',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,source_snapshot=source_snapshot,critical_central_only=central,
        ends=[],mutual_pairs=[],errors=[],case_packages=[],three_case_assignment=None,
        accepted_scope='Actual nominal wire/sleeve materials only; printed clamps, roots, tools, full middles and stock remain OPEN',
        factory_minimum_from_exact_SKU_reference_mm=FACTORY_MIN_MM,
        source100mm_assumption_NOT_used_for_acceptance=True,
        source_reference='OL-FHAC0001ZXJ revL:89.5+/-5mm;3mm internal allocation retained as conservative project allowance',
        continuous_motion_not_qualified=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins and result['source_snapshot']==source_snapshot and result['status']=='PARTIAL_FULL_FACTORY_PACKAGES'
        result.setdefault('prior_attempts',[]).append(dict(seconds=result['worker_seconds'],errors=result['errors']));result['errors']=[]
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>180:raise TimeoutError('180s package receive cap; reuse every completed receipt')
    done={(r['case_id'],r['side'],r['rank']):r for r in result['ends']};geometries={};case_shapes={}
    def case_shape(cid):
        if cid not in case_shapes:
            row=cases[cid];source=scene.templates['F_HY'][1];s=source.copy()
            rot=placement(matrix_rotation(row['source_axis_to_world_axis']),[0,0,0]).Rotation
            s.Placement=A.Placement(A.Vector(*row['centre_mm'])-rot.multVec(source.BoundBox.Center),rot)*s.Placement
            assert s.isValid();case_shapes[cid]=s
        return case_shapes[cid]
    def shape(key,candidate):
        if key not in geometries:geometries[key]=recipe_shapes(first[key[:2]],candidate)[1]
        return geometries[key]
    cache={r['key']:r for r in result['mutual_pairs']}
    def compatible(key,a,b,gap):
        if key not in cache:
            gate();g=distance(a,b);row=dict(key=key,gap_mm=g,minimum_mm=gap,clear=g>=gap-1e-5)
            result['mutual_pairs'].append(row);cache[key]=row;save()
        return cache[key]['clear']
    save()
    try:
        # Source-hole cases receive real BRep rather than being discarded by
        # a coarse material field. Rear field-positive cases follow, globally.
        both_first=domains.get('both_first9_case_ids') or [cid for cid in cases if all(first.get((cid,s),{}).get('failure','missing') is None for s in ('in','out'))]
        both_numeric=domains.get('both_numeric_tail_case_ids') or [cid for cid in both_first if all(numeric.get((cid,s),{}).get('numeric_eligible') for s in ('in','out'))]
        ids=[i for i in (6,7) if i in both_first]
        if not central:ids+=sorted(i for i in both_numeric if i not in ids)
        for cid in ids:
            gate()
            for side in ('in','out'):
                row=first[cid,side];ranked=all_ranked(row,interpolators)
                # Bounded first receipt, not exhaustive infeasibility claim.
                for rank,candidate in enumerate(ranked[:12]):
                    key=(cid,side,rank);gate()
                    if key in done:continue
                    remaining,whole,owncase_test=recipe_shapes(row,candidate)
                    failure,queries=scene.receive(remaining,wire=True)
                    if failure is None:
                        gap=distance(owncase_test,case_shape(cid))
                        queries.append(dict(scope='own_full_case_trim_first2_5_only',gap_mm=gap,minimum_mm=1.25))
                        if gap<1.25-1e-5:failure=dict(kind='own_case_tail_gap',gap_mm=gap)
                    receipt=dict(case_id=cid,side=side,rank=rank,recipe=candidate,failure=failure,
                        status='TAIL_CLEAR' if failure is None else 'TAIL_REJECTED',completed_queries=queries,
                        first9_proof_reused=True,numeric_sign_not_contact_proof=True)
                    result['ends'].append(receipt);done[key]=receipt;geometries[key]=whole;save()
                    print('Tail',cid,side,rank,receipt['status'],failure,flush=True)
            ins=[r for r in result['ends'] if r['case_id']==cid and r['side']=='in' and r['failure'] is None]
            outs=[r for r in result['ends'] if r['case_id']==cid and r['side']=='out' and r['failure'] is None]
            for a,b in itertools.product(ins,outs):
                ka=(cid,'in',a['rank']);kb=(cid,'out',b['rank'])
                if not compatible(f'tails:{ka}:{kb}',shape(ka,a['recipe']),shape(kb,b['recipe']),.2):continue
                # Own-case clearance already received above, with only the
                # named initial2.5mm mating trim (never a zero-gap waiver).
                package=dict(case_id=cid,in_rank=a['rank'],out_rank=b['rank'])
                if package not in result['case_packages']:result['case_packages'].append(package);save()
                break
        packages=result['case_packages']
        for trio in itertools.combinations(packages,3):
            gate()
            if len({p['case_id'] for p in trio})<3:continue
            good=True
            for p,q in itertools.combinations(trio,2):
                x,y=p['case_id'],q['case_id']
                if not compatible(f'cases:{min(x,y)}:{max(x,y)}',case_shape(x),case_shape(y),1.25):good=False;break
                for i,j in itertools.product(('in','out'),repeat=2):
                    a=(x,i,p[i+'_rank']);b=(y,j,q[j+'_rank'])
                    if not compatible(f'pairtails:{a}:{b}',shape(a,done[a]['recipe']),shape(b,done[b]['recipe']),.2):good=False;break
                if not good:break
                for p1,p2 in ((p,q),(q,p)):
                    for side in ('in','out'):
                        k=(p1['case_id'],side,p1[side+'_rank'])
                        if not compatible(f'othercase:{k}:{p2["case_id"]}',shape(k,done[k]['recipe']),case_shape(p2['case_id']),1.25):good=False;break
                    if not good:break
                if not good:break
            if good:result['three_case_assignment']=list(trio);break
        result['status']='CRITICAL_CENTRAL_RECEIVED_GLOBAL_PACKING_OPEN' if central else 'FULL_FACTORY_RECEIVE_BOUNDED_DOMAINS_COMPLETE_ROOTS_TOOLS_OPEN'
    except Exception as e:result['status']='PARTIAL_FULL_FACTORY_PACKAGES';result['errors'].append(repr(e))
    save();print(json.dumps({k:result[k] for k in ('status','worker_seconds','three_case_assignment','errors')}),flush=True)


if __name__=='__main__':main()
