"""One whole allocation: received full units plus the simple comb galleries.

Not an exhaustive new local grid: request only the complete chosen unknown
units, then actual mutual cuts. Keep source fans and all old positive receipts.
No N01 credit before full roots/tools/end-corridor plan.
"""
import hashlib
import ast
import json
import os
import subprocess
import sys
import time
import zipfile
from functools import lru_cache
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_shared_straight_combs import slots,unit
from feline_station_zone_domains import materialise
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from feline_flat_station_templates import box_gap,build
from plan_feline_central_pi_wedge import packed
from feline_persistent_receiver import receive_requested
from feline_component_conflict_alias import extra_case_cuts


_physical_bases={}


def physical_key(st,slot):
    """Exact constructor inputs, independent of logical labels and unused R.

    Only the straight first-land geometry is aliased, never downstream R.
    Handedness and actual occupied cavities/radii are all preserved.
    """
    side=slot['side'];c=np.asarray(slot['centre_mm']);key=(st['ref'],side)
    if key not in _physical_bases:
        # Replay precisely the constructor arithmetic, including floating
        # roundoff at mirrored source mouths; no rounded coordinate alias.
        base=build(dict(st,row_families=['inner','outer']),'outer',1,-side)
        old=np.asarray(base['centre_mm']);rot=np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
        _physical_bases[key]=[(rot@(np.asarray(w['point_mm'])-old),w['radius']) for w in base['wires']]
    ports=[dict(point=(q+c).tolist(),radius=r) for q,r in _physical_bases[key]]
    ports.sort(key=lambda p:tuple(p['point']))
    return hashlib.sha256(json.dumps(dict(slot=slot,ports=ports),sort_keys=True).encode()).hexdigest()


def main():
    tick=time.monotonic();two_lane='--two-lane' in sys.argv;selected_head='--selected-head' in sys.argv or two_lane
    dest=OUT/('n01-two-lane-comb-joint.json' if two_lane else 'n01-selected-t18i-comb-joint.json' if selected_head else 'n01-simple-comb-joint.json')
    planfile=OUT/'n01-flat-station-architecture.json';oldfile=OUT/'n01-station-zone-domains.json';zonefile=OUT/'n01-case-zone-allocation.json';fanfile=OUT/'n01-six-source-shared-lanes.json'
    stations={s['ref']:s for s in json.loads(planfile.read_text())['stations']}
    old=json.loads(oldfile.read_text());zones=json.loads(zonefile.read_text());oldslots={s['id']:s for s in zones['candidates']};newslots={s['id']:s for s in slots()}
    fans=json.loads(fanfile.read_text());_,fanparts,fanmeta=packed(fanfile)
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (Path(__file__),planfile,oldfile,zonefile,fanfile,Path(__file__).with_name('feline_shared_straight_combs.py'),Path(__file__).with_name('feline_beside_bank_receive.py'),Path(__file__).with_name('feline_persistent_receiver.py'))}
    p=Path(__file__).with_name('feline_component_conflict_alias.py');pins[p.relative_to(ROOT).as_posix()]=sha(p)
    if selected_head:
        from feline_t18i_selected_head import SOURCE,source,unit as actual_head_unit
        headsource=source()
        for p in (SOURCE,Path(__file__).with_name('feline_t18i_selected_head.py')):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    if two_lane:
        from feline_t18i_two_lane import unit as two_lane_unit
        from feline_two_lane_receive import receive_requests as receive_long_lanes
        from feline_comb_common_material import receive_common_failures
        for p in (Path(__file__).with_name('feline_t18i_two_lane.py'),Path(__file__).with_name('feline_two_lane_receive.py')):pins[p.relative_to(ROOT).as_posix()]=sha(p)
        p=Path(__file__).with_name('feline_comb_common_material.py');pins[p.relative_to(ROOT).as_posix()]=sha(p)
    result=dict(status='RUNNING_SHARED_SIMPLE_COMB_ALLOCATION',source_sha256=pins,iterations=[],mutual_cache={},cuts=[],errors=[],N01_complete=False,physical_pass=False,selected=False)
    if dest.exists():
        result=json.loads(dest.read_text())
        if result['source_sha256']!=pins and '--receive-controller' in sys.argv:
            own=Path(__file__).relative_to(ROOT).as_posix()
            versions=[subprocess.run(['git','show',c+':'+own],cwd=ROOT,check=True,capture_output=True).stdout for c in ('ac4117a8','e36917e7','2435ccf3','a08eea28','1852c030','9d6e4895')]
            previous=next(s for s in versions if hashlib.sha256(s).hexdigest()==result['source_sha256'][own])
            assert all(pins[n]==v for n,v in result['source_sha256'].items() if n!=own)
            assert set(pins)-set(result['source_sha256'])<= {'tools/cad/feline_persistent_receiver.py','tools/cad/feline_comb_common_material.py','tools/cad/feline_component_conflict_alias.py'}
            before=ast.parse(previous);after=ast.parse(Path(__file__).read_text())
            for name in ('shape','mutual'):
                f=lambda tree:next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
                assert ast.dump(f(before))==ast.dump(f(after)),name
            result.setdefault('controller_repairs',[]).append(dict(old_code_sha256=result['source_sha256'][own],
                reason='Same shape/mutual kernels proven AST-identical. Complete both lanes before resolve; exact shared PETG subset witnesses exclude all label permutations at fixed blocked sites. No geometry or clearance change.'))
            result['source_sha256']=pins
        else:assert result['source_sha256']==pins
        result.setdefault('prior_worker_seconds',[]).append(result['worker_seconds'])
    result['status']='RUNNING_SHARED_SIMPLE_COMB_ALLOCATION'
    if selected_head:result['selected_head_source']=headsource
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        temp=dest.with_suffix('.writing.json');temp.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');temp.replace(dest)
    groups={}
    for ref,st in stations.items():
        rows=[]
        for r in old['domains'].get(ref,[]):
            slot=oldslots[r['slot_id']]
            rows.append(dict(kind='received_legacy_unit',ref=ref,recipe=r,slot=slot,key=ref+':legacy:'+r['geometry_signature']))
        if not st['fixed_identity_pose']:
            profile='large' if st['flat_dimensions_pitch_departure_thickness_mm'][2]>10 else 'standard'
            for slot in newslots.values():
                if slot['profile']==profile:
                    rows.append(dict(kind='straight_comb',ref=ref,slot=slot,key=ref+':straight:'+str(slot['id'])))
                    if two_lane:rows.append(dict(kind='straight_comb',ref=ref,slot=slot,lane=1,key=ref+':straight:'+str(slot['id'])+':lane1'))
        groups[ref]=rows
    for ref,options in fans['domains'].items():
        groups['Source:'+ref]=[dict(kind='source_fan',key='Source:'+ref+':'+str(i),option=r) for i,r in enumerate(options)]
    monitor=[s for s in zones['candidates'] if s['profile']=='monitor' and not zones['received'][str(s['id'])]['failure']]
    groups['Monitor']=[dict(kind='monitor',slot=s,key='Monitor:'+str(s['id'])) for s in monitor]
    choices=[(g,r) for g,rows in groups.items() for r in rows];idx={r['key']:i for i,(g,r) in enumerate(choices)}
    geometry={r['key']:('straight:'+physical_key(stations[g],r['slot'])+(':long' if r.get('lane') else '') if r['kind']=='straight_comb' else
        'legacy:'+r['recipe']['geometry_signature'] if r['kind']=='received_legacy_unit' else r['key']) for g,r in choices}
    bygeometry={}
    for i,(g,r) in enumerate(choices):bygeometry.setdefault(geometry[r['key']],[]).append(i)
    if selected_head and not result.get('prior_generic_head_reconciled'):
        previousfile=OUT/('n01-selected-t18i-comb-joint.json' if two_lane else 'n01-simple-comb-joint.json');previous=json.loads(previousfile.read_text())
        retired=[]
        for key,record in previous['mutual_cache'].items():
            if record['ok']:
                result['mutual_cache'][key]=dict(ok=True,prior_exact_pair_source=previousfile.relative_to(ROOT).as_posix(),
                    prior_pair_key=key,positive_superset_receipt=True,
                    basis='Only new straight heads are exact subsets; other geometry unchanged. Named nylon/jacket threshold follows existing.2policy, rigid1.25 unchanged.',pairs=[])
            elif not two_lane and any('budget' in str(record['pairs'][-1].get(n,'')) for n in ('part','other')):
                retired.append(key)
            else:result['mutual_cache'][key]=record
        for a,b in previous['cuts']:
            key='|'.join(sorted((a,b)))
            if key in result['mutual_cache'] and not result['mutual_cache'][key]['ok']:result['cuts'].append([a,b])
        result['prior_generic_head_reconciled']=dict(previous_sha256=sha(previousfile),
            retained_positive_stronger_geometry_receipts=sum(r['ok'] for r in result['mutual_cache'].values()),
            retained_unchanged_negative_cuts=len(result['cuts']),retired_budget_negative_pairs=retired,
            raw_old_receipts_preserved=True,full6source_heads_unchanged=True)
    case_rows=[r for _,r in choices if r['kind']!='source_fan']
    phase_keys=sorted({(s['side'],s['tier']) for s in newslots.values() if s['profile']=='standard'}) if two_lane else []
    phaseidx={key:len(choices)+i for i,key in enumerate(phase_keys)};total=len(choices)+len(phase_keys)
    parity={}
    for key in phase_keys:
        ordered=sorted((s for s in newslots.values() if s['profile']=='standard' and (s['side'],s['tier'])==key),key=lambda s:s['centre_mm'][0])
        parity.update({s['id']:i%2 for i,s in enumerate(ordered)})
    def cb(r):
        s=r['slot']
        if 'bounds_mm' in s:return np.array(s['bounds_mm'])
        c=np.asarray(s['centre_mm']);d=np.asarray(s['dimensions_mm']);return np.array([c-d/2,c+d/2])
    # Rectangular source case geometry, NOT whole-unit bounding boxes.
    conflicts=[]
    for i,a in enumerate(case_rows):
        for b in case_rows[i+1:]:
            if a.get('ref')==b.get('ref') and a['kind']!='monitor' and b['kind']!='monitor':continue
            if box_gap(cb(a),cb(b))<1.25-1e-6:conflicts.append((idx[a['key']],idx[b['key']]))
    cache=SolidQueries();sourceprior=json.loads((OUT/'n01-source-joint-allocation.json').read_text())
    sourcepairs={tuple(sorted((p['part'],p['other']))):p for p in sourceprior['pairs']}
    @lru_cache(maxsize=96)
    def shape(key):
        _,r=choices[idx[key]];kind=r['kind']
        if kind=='straight_comb':
            m=two_lane_unit(stations[r['ref']],r['slot'],r.get('lane',0)) if two_lane else (actual_head_unit if selected_head else unit)(stations[r['ref']],r['slot'])
            return m['parts'],{n:'wire' if n.startswith('wire:') else 'project_stock_reservation' if 'budget' in n else 'proposal_material' for n in m['parts']}
        if kind=='received_legacy_unit':return materialise(stations[r['ref']],r['slot'],r['recipe'])
        if kind=='source_fan':
            parts={p['name']:fanparts[p['name']] for p in r['option']['parts']}
            return parts,{n:'wire' if fanmeta[n]['kind']=='wire' else 'project_stock_reservation' if 'budget' in fanmeta[n]['kind'] else 'proposal_material' for n in parts}
        lo,hi=cb(r);return {'case':Part.makeBox(*(hi-lo),A.Vector(*lo))},{'case':'proposal_material'}
    def mutual(a,b):
        key='|'.join(sorted((a,b)))
        if key in result['mutual_cache']:return result['mutual_cache'][key]['ok']
        aa,ak=shape(a);bb,bk=shape(b);record=dict(ok=True,pairs=[])
        for n,s in aa.items():
            for other,t in bb.items():
                minimum=pair_spacing(('Current:'+n) if selected_head else n,dict(kind=ak[n]),('Current:'+other) if selected_head else other,dict(kind=bk[other]))
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                oldpair=sourcepairs.get(tuple(sorted((n,other)))) if a.startswith('Source:') and b.startswith('Source:') else None
                if oldpair is not None and abs(oldpair['minimum_mm']-minimum)<1e-7:gap=oldpair['gap_mm'];reuse=True
                else:gap=cache.distance(s,t);reuse=False
                record['pairs'].append(dict(part=n,other=other,gap_mm=gap,minimum_mm=minimum,reused_prior_source_pair=reuse))
                if gap<minimum-1e-6:record['ok']=False;break
            if not record['ok']:break
        result['mutual_cache'][key]=record;save();return record['ok']
    save()
    try:
        for iteration in range(120):
            if time.monotonic()-tick>480:raise TimeoutError('Bounded8minute parent slice; no window closure')
            receiver=json.loads((OUT/'n01-straight-combs-received.json').read_text());received=receiver['units']
            physical=receiver.get('physical_cache',{})
            longfile=OUT/'n01-two-lane-static.json';longdata=json.loads(longfile.read_text()) if two_lane and longfile.exists() else dict(units={})
            common_bad=receive_common_failures(result,longdata,stations) if two_lane else set()
            save()
            bad_cases={r['slot']['id'] for r in received.values() if str(r.get('failure','')).startswith('case|')}
            for rec in received.values():
                if rec.get('physical_key'):assert rec['physical_key']==physical_key(stations[rec['ref']],rec['slot'])
            def receipt(r):
                direct=received.get(r['ref']+':'+str(r['slot']['id']),{})
                if r.get('lane'):
                    failure=direct.get('failure')
                    if failure and (failure.startswith('case|') or failure.startswith('wire:')):return direct
                    return longdata['units'].get(r['ref']+':'+str(r['slot']['id'])+':1',{})
                if 'failure' in direct:return direct
                key=physical_key(stations[r['ref']],r['slot']);r0=physical.get(key,{})
                if 'failure' in r0:
                    result.setdefault('physical_aliases',{})[r['key']]=key
                return r0
            rr=[];cc=[];vv=[];lo=[];hi=[]
            def add(indices,lower,upper,weights=None):
                j=len(lo);rr.extend([j]*len(indices));cc.extend(indices);vv.extend([1.]*len(indices) if weights is None else weights);lo.append(lower);hi.append(upper)
            for g,rows in groups.items():add([idx[r['key']] for r in rows],1,1)
            upper=np.ones(total);cost=np.zeros(total)
            for i,(g,r) in enumerate(choices):
                if r['kind']=='straight_comb':
                    rec=receipt(r)
                    if r['slot']['id'] in bad_cases:upper[i]=0
                    if (r['slot']['id'],r.get('lane',0)) in common_bad:upper[i]=0
                    if 'failure' in rec and rec['failure'] is not None:upper[i]=0
                    cost[i]=0 if 'failure' in rec else 10
                    if two_lane and r['slot']['profile']=='standard':
                        p=phaseidx[(r['slot']['side'],r['slot']['tier'])]
                        if r.get('lane',0)^parity[r['slot']['id']]:add([i,p],-np.inf,0,[1.,-1.])
                        else:add([i,p],-np.inf,1)
                elif r['kind']=='received_legacy_unit' and not stations[r['ref']]['fixed_identity_pose']:
                    cost[i]=100 # Simplicity/load-path preference, not fit credit.
                if 'slot' in r:cost[i]+=abs(r['slot']['centre_mm'][0])/10000
            for a,b in conflicts:add([a,b],-np.inf,1)
            expanded=set()
            for a,b in result['cuts']:
                for ia in bygeometry[geometry[a]]:
                    for ib in bygeometry[geometry[b]]:
                        if choices[ia][0]!=choices[ib][0]:expanded.add(tuple(sorted((ia,ib))))
            component_cuts,component_proof=extra_case_cuts(result['cuts'],result['mutual_cache'],choices,idx,bygeometry,geometry,cb)
            expanded.update(component_cuts)
            result['actual_case_component_alias_receipts']=component_proof
            result['expanded_actual_case_component_cuts']=len(component_cuts)
            for a,b in expanded:add([a,b],-np.inf,1)
            result['expanded_physical_conflict_cuts']=len(expanded)
            matrix=coo_matrix((vv,(rr,cc)),shape=(len(lo),total)).tocsc()
            fit=milp(cost,integrality=np.ones(total),bounds=Bounds(0,upper),constraints=LinearConstraint(matrix,lo,hi),options={'time_limit':30,'mip_rel_gap':0.0})
            if fit.x is None:
                result['status']='BOUNDED_JOINT_CATALOGUE_NO_WHOLE_SET_NOT_GLOBAL_IMPOSSIBILITY';result['solver_message']=fit.message;break
            chosen=[(g,r) for i,(g,r) in enumerate(choices) if fit.x[i]>.5]
            requests=[dict(ref=r['ref'],slot_id=r['slot']['id'],lane=r.get('lane',0)) for g,r in chosen if r['kind']=='straight_comb' and 'failure' not in receipt(r)]
            result['iterations'].append(dict(iteration=len(result['iterations']),chosen={g:r['key'] for g,r in chosen},unknown_units=len(requests)));save()
            print('Whole choice',len(result['iterations']),'unknown',len(requests),'mutualcuts',len(result['cuts']),flush=True)
            if requests:
                baseline=[r for r in requests if not r['lane'] or 'failure' not in received.get(r['ref']+':'+str(r['slot_id']),{})]
                child_tick=time.monotonic()
                if baseline:
                    (OUT/'n01-simple-comb-joint-targets.json').write_text(json.dumps(dict(requests=baseline),indent=2)+'\n',encoding='utf-8',newline='\n')
                    status=receive_requested()
                if two_lane:
                    complete_base=json.loads((OUT/'n01-straight-combs-received.json').read_text())['units']
                    long_requests=[r for r in requests if r['lane'] and 'failure' in complete_base.get(r['ref']+':'+str(r['slot_id']),{})]
                    if long_requests:status=receive_long_lanes(long_requests)['status']
                result.setdefault('persistent_receipts',[]).append(dict(status=status,seconds=round(time.monotonic()-child_tick,3),requested=len(requests)))
                save();continue
            cut=False
            for i,(g,a) in enumerate(chosen):
                for h,b in chosen[i+1:]:
                    if not mutual(a['key'],b['key']):
                        result['cuts'].append([a['key'],b['key']]);cut=True;save();break
                if cut:break
            if cut:continue
            result['status']='WHOLE20_MONITOR_SIX_FANS_FULL_UNITS_STATIC_MUTUAL_RECEIVED_CORRIDORS_ROOTS_TOOLS_OPEN'
            result['chosen']={g:r for g,r in chosen};break
        else:result['status']='BOUNDED_ITERATION_RECEIPT_NOT_N01'
    except TimeoutError as exc:result['status']='PARTIAL_SHARED_COMB_JOINT';result['slice_note']=str(exc)
    except Exception as exc:result['status']='SHARED_COMB_CONTROLLER_ERROR';result['errors'].append(repr(exc))
    save();print(json.dumps(dict(status=result['status'],worker_seconds=result['worker_seconds'],errors=result['errors'])),flush=True)


if __name__=='__main__':
    print('WORKER_PID',os.getpid(),flush=True);main()
