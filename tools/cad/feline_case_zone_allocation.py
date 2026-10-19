"""Shared CASE capacity after retiring the obsolete bounded catalogue.

Whole purchased case envelopes against the actual current owners and36poses.
No wire/root/tool acceptance, no new native CAD, no N01 point from this gate.
Identical case profiles share queries; MILP chooses unlabelled slots before
assigning the existing selected references, rather than duplicating16domains.
"""
import itertools
import json
import os
import sys
import time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import coo_matrix
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from feline_candidate_collision_scene import Scene
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from feline_flat_station_templates import box_gap
from receive_feline_global_case_candidates import placement


def slots():
    """Whole functional rows over the permitted body, not witness offsets."""
    profiles={'standard':[19.,30.,9.], 'large':[22.,37.,11.], 'monitor':[41.,25.,12.]}
    result=[]
    for profile, dims in profiles.items():
        pitch=dims[1]
        if profile=='monitor':
            centres=[[-107.5,62.5,46.],[-107.5,62.5,60.],[-32.,0.,36.95]]
        else:
            centres=[[x,side*y,z] for x,side,(y,z) in itertools.product(
                range(-120,121,24),(-1,1),((pitch/2+1.25,48.5),(49.3396+1.25+pitch/2,45.)))]
        for centre in centres:
            bounds=np.array([np.array(centre)-np.array(dims)/2,np.array(centre)+np.array(dims)/2])
            result.append(dict(id=len(result),profile=profile,centre_mm=centre,dimensions_mm=dims,bounds_mm=bounds.tolist()))
    bounds=[[4.55,-1.5,43.],[26.55,35.5,54.]]
    result.append(dict(id=len(result),profile='fixed_P_SYS',centre_mm=[15.55,17.,48.5],dimensions_mm=[22.,37.,11.],bounds_mm=bounds))
    # A flat24mm-pitch case allocation is necessary, not sufficient: its
    # adjacent case can occupy the mandatory9mm departure before any bend.
    # Add ONE different whole architecture, two side tiers with source
    # departure vertical and lever normal lateral; no purchased part change.
    for profile,(pitch,depth,thick) in {'standard':(30.,19.,9.),'large':(37.,22.,11.)}.items():
        dims=np.array([pitch,thick,depth])
        for x,side,z in itertools.product(range(-114,127,40),(-1,1),(18.,90.)):
            centre=np.array([x,side*65.6,z]);bounds=np.array([centre-dims/2,centre+dims/2])
            result.append(dict(id=len(result),profile=profile,centre_mm=centre.tolist(),dimensions_mm=dims.tolist(),
                bounds_mm=bounds.tolist(),pose_family='VERTICAL_DEPARTURE_TWO_SIDE_TIERS'))
    # Changed cause after side tiers fail: lower row is in the folding legs,
    # upper row in the retained bank. Allocate UNDER the central platform,
    # within the approved belly, not another height tweak of those side rows.
    for profile,dims,ys,z in (('standard',[30.,9.,19.],(-40.,-15.,15.,40.),-13.),
                             ('large',[37.,22.,11.],(-40.,40.),-14.)):
        dims=np.array(dims)
        for x,y in itertools.product(range(-114,127,40),ys):
            centre=np.array([x,y,z]);bounds=np.array([centre-dims/2,centre+dims/2])
            result.append(dict(id=len(result),profile=profile,centre_mm=centre.tolist(),dimensions_mm=dims.tolist(),
                bounds_mm=bounds.tolist(),pose_family='UNDER_PLATFORM_SHARED_REMOVABLE_COMBS',
                source_departure='DOWN_Z' if profile=='standard' else 'INWARD_Y',
                full_grip_after_arc_required=True))
    return result


def current_world():
    world=Scene();proof=json.loads((OUT/'n01-flat20-field-modulejoint.json').read_text())
    packet,core,rows=packed(OUT/'n01-six-source-current-core.json')
    for file,groups in (('n01-fore-service-macro.json',{'F_HP','F_TY'}),('n01-fore-topology.json',{'ForeFHAC'})):
        _,extra,rr=packed(OUT/file)
        for n,s in extra.items():
            if rr[n]['group'] in groups:world.parts[n]=s
    fixed={r['source']:world.parts[r['source']] for r in proof['material_clouds']
           if r['category']!='S1_mating_context' and r['source'] not in packet['retired_whole_owners']}
    _,pwm,_=packed(OUT/'n01-pwm-board-shelf.json');fixed.update(pwm);fixed.update(core)
    return world,fixed


def main():
    tick=time.monotonic();dest=OUT/'n01-case-zone-allocation.json';candidates=slots()
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (Path(__file__),OUT/'n01-six-source-current-core.json',OUT/'n01-pwm-board-shelf.json',OUT/'n01-six-source-shared-lanes.outer.brep')}
    result=dict(status='RUNNING_WHOLE_CASE_ZONE_GATE',N01_complete=False,physical_pass=False,selected=False,
        cases_only_not_full_grips_roots_tools_or_wire_acceptance=True,source_sha256=pins,candidates=candidates,received={},errors=[])
    if dest.exists():
        old=json.loads(dest.read_text())
        if any(a in sys.argv for a in ('--receive-own-source','--vertical-zones','--under-platform')):
            own=Path(__file__).relative_to(ROOT).as_posix()
            assert all(old['source_sha256'][n]==v for n,v in pins.items() if n!=own)
            assert old['candidates']==candidates[:len(old['candidates'])]
            old.setdefault('method_repairs',[]).append(dict(previous_code_sha256=old['source_sha256'][own],
                reason='Explicit reception or whole architecture expansion: unchanged exact case receipts retained; own P_SYS W043 mouth uses positive-common test.'))
            old['source_sha256']=pins;old['candidates']=candidates
            if '--receive-own-source' in sys.argv:
                for r in candidates:
                    if r['profile']=='fixed_P_SYS':old['received'].pop(str(r['id']),None)
        else:assert old['source_sha256']==pins,'Changed inputs require explicit affected reuse'
        result=old;result.setdefault('prior_worker_seconds',[]).append(result['worker_seconds'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save();world,fixed=current_world();query=SolidQueries()
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'));assert outer.isValid() and len(outer.Solids)==1
    try:
        for row in candidates:
            key=str(row['id'])
            if key in result['received']:continue
            lo,hi=np.array(row['bounds_mm']);s=Part.makeBox(*(hi-lo),A.Vector(*lo));receipt=dict(pairs=[],failure=None)
            outside=s.cut(outer);assert outside.isNull() or outside.isValid()
            gap=s.distToShape(outer.Shells[0])[0]
            if outside.Volume>1e-5 or gap<3.25-1e-6:receipt['failure']=dict(kind='true_outer',outside_mm3=outside.Volume,gap_mm=gap)
            if not receipt['failure']:
                for n,t in fixed.items():
                    if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
                    q=s
                    if n==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
                    if not t.Solids:receipt['failure']=dict(kind='curve_owner_hold',source=n);break
                    gap=query.distance(q,t);r=dict(source=n,gap_mm=gap,minimum_mm=1.25);receipt['pairs'].append(r)
                    if row['profile']=='fixed_P_SYS' and n=='W043':
                        common=q.copy().common(t.copy());assert common.isValid()
                        r.update(owned_wire_mouth=True,minimum_mm=0.,positive_common_mm3=common.Volume)
                        if common.Volume>1e-5:receipt['failure']=dict(kind='own_mouth_penetration',**r);break
                        continue
                    if gap<1.25-1e-6:receipt['failure']=dict(kind='actual_fixed_gap',**r);break
            if not receipt['failure']:
                for p in world.motion:
                    if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
                    q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
                    gap=query.distance(q,world.rest[p['name']]);r=dict(source=p['name'],pose=p['pose'],gap_mm=gap,minimum_mm=1.25);receipt['pairs'].append(r)
                    if gap<1.25-1e-6:receipt['failure']=dict(kind='actual_motion36_gap',**r);break
            result['received'][key]=receipt;save()
            print('Case zone',row['id'],row['profile'],row['centre_mm'],'blocked:'+str(receipt['failure']) if receipt['failure'] else 'clear',flush=True)
        good=[r for r in candidates if not result['received'][str(r['id'])]['failure']]
        if '--vertical-zones' in sys.argv:
            good=[r for r in good if r.get('pose_family')=='VERTICAL_DEPARTURE_TWO_SIDE_TIERS' or r['profile'] in ('monitor','fixed_P_SYS')]
            result['architecture']='Two side tiers, actual lever and departure axes rotate with source; oldflat receipts retained not mixed as wire proof'
        if '--under-platform' in sys.argv:
            good=[r for r in good if r.get('pose_family')=='UNDER_PLATFORM_SHARED_REMOVABLE_COMBS' or r['profile'] in ('monitor','fixed_P_SYS')]
            result['architecture']='Under-platform removable common combs, within existing belly; flatlarge45deg/downturn and verticalsmall90deg, full9AFTERarc. Wholekits still require receipt.'
        need={'standard':16,'large':3,'monitor':1,'fixed_P_SYS':1};rr=[];cc=[];dd=[];low=[];high=[]
        for profile,count in need.items():
            k=len(low)
            for i,r in enumerate(good):
                if r['profile']==profile:rr.append(k);cc.append(i);dd.append(1.)
            low.append(count);high.append(count)
        conflicts=0
        for i,a in enumerate(good):
            for j in range(i+1,len(good)):
                b=good[j]
                if box_gap(np.array(a['bounds_mm']),np.array(b['bounds_mm']))<1.25-1e-6:
                    k=len(low);rr.extend((k,k));cc.extend((i,j));dd.extend((1.,1.));low.append(-np.inf);high.append(1.);conflicts+=1
        matrix=coo_matrix((dd,(rr,cc)),shape=(len(low),len(good))).tocsc()
        fit=milp(np.array([abs(r['centre_mm'][0])/200 for r in good]),integrality=np.ones(len(good)),bounds=Bounds(0,1),
            constraints=LinearConstraint(matrix,low,high),options={'time_limit':30,'mip_rel_gap':0.0})
        selected=[] if fit.x is None else [r for i,r in enumerate(good) if fit.x[i]>.5]
        result.update(status='WHOLE21_CASE_PROPOSAL_FULL_KITS_OPEN' if len(selected)==21 else 'BOUNDED_NEW_ZONES_NO_WHOLE21_CASE_ASSIGNMENT',
            clear_by_profile={n:sum(r['profile']==n for r in good) for n in need},solver_status=int(fit.status),solver_message=str(fit.message),case_conflicts=conflicts,chosen_cases=selected)
    except Exception as exc:result['errors'].append(repr(exc));result['status']='CASE_ZONE_PARTIAL_OR_ERROR_NOT_ACCEPTANCE'
    save();print(json.dumps({k:result.get(k) for k in ('status','clear_by_profile','solver_status','worker_seconds','errors')}),flush=True)


if __name__=='__main__':
    print('WORKER_PID',os.getpid(),flush=True);main()
