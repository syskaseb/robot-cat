"""Demand-driven whole station allocation, not exhaustive local variants.

Choose all20station poses + monitor + six source fans together. Request exact
static proof only for currently useful full units, learn negative actual
mutual pairs, retain cache. Cases are actual solid boxes, not arbitrary BBoxes.
Other27kits, roots/tools/allends still required before N01.
"""
import hashlib
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
from feline_flat_station_templates import box_gap
from feline_station_zone_domains import catalogue,signature,materialise
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound


def main():
    tick=time.monotonic();dest=OUT/'n01-station-joint-allocation.json'
    zonefile=OUT/'n01-case-zone-allocation.json';zones=json.loads(zonefile.read_text());slots={r['id']:r for r in zones['candidates']}
    planfile=OUT/'n01-flat-station-architecture.json';plan=json.loads(planfile.read_text());stations={s['ref']:s for s in plan['stations']}
    fanfile=OUT/'n01-six-source-shared-lanes.json';fans=json.loads(fanfile.read_text())
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (zonefile,planfile,fanfile,Path(__file__),Path(__file__).with_name('feline_station_zone_domains.py'))}
    result=dict(status='RUNNING_COMMON_STATION_ALLOCATION',source_sha256=pins,iterations=[],actual_mutual_cache={},conflict_cuts=[],errors=[],
        N01_complete=False,physical_pass=False,selected=False,open=['Other27kits','Fullroots/tools/service/assembly','All123portions246ends/factory corridors','Monitor retention/conditional balance interface'])
    if dest.exists():
        old=json.loads(dest.read_text());assert old['source_sha256']==pins
        result=old;result.setdefault('prior_worker_seconds',[]).append(result['worker_seconds'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    groups={name:[dict(r,key=signature(st,r)) for r in catalogue(st,zones)] for name,st in stations.items()}
    for name,options in fans['domains'].items():groups['Source:'+name]=[dict(fan_index=i,key='Source:'+name+':'+str(i)) for i in range(len(options))]
    variables=[(n,i) for n,opts in groups.items() for i in range(len(opts))];idx={v:i for i,v in enumerate(variables)}
    active_slots=sorted({r['slot_id'] for n,opts in groups.items() if n in stations for r in opts})
    monitor_slots=[r['id'] for r in zones['candidates'] if r['profile']=='monitor' and not zones['received'][str(r['id'])]['failure']]
    active_slots+=monitor_slots;slotidx={s:len(variables)+i for i,s in enumerate(active_slots)};total=len(variables)+len(active_slots)
    caseconflicts=[(a,b) for i,a in enumerate(active_slots) for b in active_slots[i+1:] if box_gap(np.array(slots[a]['bounds_mm']),np.array(slots[b]['bounds_mm']))<1.25-1e-6]
    bykey={}
    for n,i in variables:bykey.setdefault(groups[n][i]['key'],[]).append(idx[n,i])
    fanparts={};fankinds={}
    with zipfile.ZipFile(ROOT/fans['bundle']) as z:
        for r in fans['parts']:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());fanparts[r['name']]=s;fankinds[r['name']]='wire' if r['kind']=='wire' else 'project_stock_reservation' if 'budget' in r['kind'] else 'proposal_material'
    qcache=SolidQueries();cuts={tuple(c) for c in result['conflict_cuts']}
    @lru_cache(maxsize=64)
    def shapes(name,index):
        r=groups[name][index]
        if name in stations:return materialise(stations[name],slots[r['slot_id']],r)
        option=fans['domains'][name.removeprefix('Source:')][r['fan_index']]
        return {p['name']:fanparts[p['name']] for p in option['parts']},{p['name']:fankinds[p['name']] for p in option['parts']}
    def mutual(a,i,b,j):
        ka,kb=groups[a][i]['key'],groups[b][j]['key'];key='|'.join(sorted((ka,kb)))
        if key in result['actual_mutual_cache']:return result['actual_mutual_cache'][key]['ok']
        aa,ak=shapes(a,i);bb,bk=shapes(b,j);receipt=dict(ok=True,pairs=[])
        for n,s in aa.items():
            for o,t in bb.items():
                minimum=pair_spacing(n,{'kind':ak[n]},o,{'kind':bk[o]})
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                gap=qcache.distance(s,t);receipt['pairs'].append(dict(part=n,other=o,gap_mm=gap,minimum_mm=minimum))
                if gap<minimum-1e-6:receipt['ok']=False;break
            if not receipt['ok']:break
        result['actual_mutual_cache'][key]=receipt;save();return receipt['ok']
    save()
    try:
        for iteration in range(200):
            domainfile=OUT/'n01-station-zone-domains.json';received=json.loads(domainfile.read_text());cache=received['geometry_cache']
            rr=[];cc=[];dd=[];low=[];high=[]
            def constraint(indices,coefficients,lo,hi):
                k=len(low);rr.extend([k]*len(indices));cc.extend(indices);dd.extend(coefficients);low.append(lo);high.append(hi)
            for n,options in groups.items():constraint([idx[n,i] for i in range(len(options))],[1.]*len(options),1,1)
            for s in active_slots:
                vv=[idx[n,i] for n,i in variables if groups[n][i].get('slot_id')==s]
                if s in monitor_slots:continue
                constraint(vv+[slotidx[s]],[1.]*len(vv)+[-1.],0,0)
            constraint([slotidx[s] for s in monitor_slots],[1.]*len(monitor_slots),1,1)
            for a,b in caseconflicts:constraint([slotidx[a],slotidx[b]],[1.,1.],-np.inf,1.)
            for a,b in cuts:
                vv=bykey[a]+bykey[b];constraint(vv,[1.]*len(vv),-np.inf,1.)
            for hold in result.get('monitor_conflicts',[]):
                vv=bykey[hold['key']]+[slotidx[hold['slot']]];constraint(vv,[1.]*len(vv),-np.inf,1.)
            upper=np.ones(total);objective=np.zeros(total)
            for n,i in variables:
                r=groups[n][i];entry=cache.get(r['key'],{})
                if entry.get('failure') is not None:upper[idx[n,i]]=0
                objective[idx[n,i]]=0 if 'failure' in entry and entry['failure'] is None else 1.
                if n in stations:objective[idx[n,i]]+=abs(slots[r['slot_id']]['centre_mm'][0])/10000
            matrix=coo_matrix((dd,(rr,cc)),shape=(len(low),total)).tocsc()
            fit=milp(objective,integrality=np.ones(total),bounds=Bounds(0,upper),constraints=LinearConstraint(matrix,low,high),options={'time_limit':30,'mip_rel_gap':0.0})
            if fit.x is None:
                result.update(status='BOUNDED_COMMON_KIT_CATALOGUE_NO_ASSIGNMENT_NOT_GLOBAL_IMPOSSIBILITY',solver_status=int(fit.status),solver_message=str(fit.message));save();return
            chosen={n:max(range(len(opts)),key=lambda i:fit.x[idx[n,i]]) for n,opts in groups.items()}
            assert all(fit.x[idx[n,i]]>.5 for n,i in chosen.items())
            selected_monitor=next(s for s in monitor_slots if fit.x[slotidx[s]]>.5)
            result['current_choices']={n:groups[n][i] for n,i in chosen.items()};result['current_monitor_slot']=selected_monitor;save()
            requested={n:[groups[n][i]] for n,i in chosen.items() if n in stations and 'failure' not in cache.get(groups[n][i]['key'],{})}
            if requested:
                (OUT/'n01-station-joint-targets.json').write_text(json.dumps(dict(source_sha256=pins,requests=requested),indent=2)+'\n',encoding='utf-8',newline='\n')
                print('Common choice',iteration,'request',len(requested),'exact full units, cuts',len(cuts),flush=True)
                child=subprocess.run([sys.executable,str(Path(__file__).with_name('feline_station_zone_domains.py')),'--requested-only','--receive-controller-only'],cwd=ROOT)
                assert child.returncode==0
                after=json.loads(domainfile.read_text());assert not after['errors'],after['errors']
                pending=any('failure' not in after['geometry_cache'].get(r[0]['key'],{}) for r in requested.values())
                if pending:continue
                if any(after['geometry_cache'][r[0]['key']]['failure'] is not None for r in requested.values()):continue
            bad=[];items=list(chosen.items())
            for ia,(a,i) in enumerate(items):
                for b,j in items[ia+1:]:
                    if not mutual(a,i,b,j):
                        cut=tuple(sorted((groups[a][i]['key'],groups[b][j]['key'])));cuts.add(cut);bad.append(cut)
            # Monitor is a separate selected source, not an absent inventory item.
            lo,hi=np.array(slots[selected_monitor]['bounds_mm']);monitor=Part.makeBox(*(hi-lo),A.Vector(*lo))
            monitor_bad=0
            for a,i in items:
                shapes_a,kinds=shapes(a,i)
                for n,s in shapes_a.items():
                    if bbox_lower_bound(s.BoundBox,monitor.BoundBox)>=1.25:continue
                    gap=qcache.distance(s,monitor)
                    if gap<1.25-1e-6:
                        # Store a forbidden option/monitor-slot relation separately.
                        result.setdefault('monitor_conflicts',[]).append(dict(key=groups[a][i]['key'],slot=selected_monitor,part=n,gap_mm=gap))
                        monitor_bad+=1;break
            result['conflict_cuts']=[list(c) for c in sorted(cuts)];result['iterations'].append(dict(iteration=iteration,solver_status=int(fit.status),bad_selected_pairs=len(bad),monitor_conflicts=monitor_bad));save()
            print('Common actual mutual',iteration,'failed pairs',len(bad),flush=True)
            if not bad and not monitor_bad:result['status']='WHOLE20_SIXSOURCES_MONITOR_FULL_UNITS_RECEIVED_ROOTS_OTHER27_OPEN';save();return
        result['status']='PARTIAL_COMMON_KIT_ALLOCATION_CUTS_RETAINED'
    except Exception as exc:result['errors'].append(repr(exc));result['status']='COMMON_KIT_ALLOCATION_ERROR_NOT_ACCEPTANCE'
    save()


if __name__=='__main__':
    print('WORKER_PID',os.getpid(),flush=True);main()
