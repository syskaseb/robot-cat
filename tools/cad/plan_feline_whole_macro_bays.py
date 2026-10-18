"""Cheap joint bay proposal for omitted selected parts, not a CAD fit verdict.

Uses pinned per-part bounds, all36leg transformed bounds, current126retention
parts and all60tail members. AABB intersection is ONLY unresolved/rejection of
this conservative proposal, never a declaration of physical collision.
Positive separation may nominate a bay; exact actual construction still follows.
"""
import json
import time
import sys
from pathlib import Path
import itertools
import numpy as np
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT,STAGES
from plan_feline_interior import inside
from check_feline_leg_body import placement


def main():
    orthogonal='--all-orthogonal' in sys.argv
    tick=time.monotonic();dest=OUT/('n01-whole-macro-bays-r2.json' if orthogonal else 'n01-whole-macro-bays.json');assert not dest.exists()
    names=dict(scene='n01-full-material-scene.json',lower='n01-lower-bay-world-probe.json',
        common='n01-common-restraint-world-probe.json',extra='n01-remaining-selected-inventory.json',
        motion='motion-layout.json',ports='n01-twenty-wago-port-contract.json')
    files={k:OUT/n for k,n in names.items()};p={k:json.loads(f.read_text()) for k,f in files.items()}
    assert p['extra']['USB_root_scoped_clear']
    retired={'StructureReserve:NineWire'+kind+code for kind in ('Cuff','Arm') for code in ('FL','FR','RL','RR')}
    parts={}
    for key in ('scene','lower','common','extra'):
        for r in p[key]['parts']:
            if r.get('role')=='CurrentCassette' or r['name'] in retired or key=='extra' and not r['placed_current']:continue
            parts[r['name']]=r
    axesfile=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axesfile.read_text())['axes']
    moving={n:r for n,r in parts.items() if r.get('role','').startswith('leg:')}
    boxes=[r['bounds_mm'] for n,r in parts.items() if n not in moving]
    for sample in p['motion']['poses'][:36]:
        for code,groups in p['motion']['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==s) for s in STAGES];tfs=placement(aa,sample['legs'][code]['angles_delta_degrees'])
            for stage,names in groups.items():
                for n in names:
                    bb=np.array(moving[n]['bounds_mm']);vv=[tfs[stage].multVec(A.Vector(*q)) for q in itertools.product(*zip(bb[0],bb[1]))]
                    q=np.array([list(v) for v in vv]);boxes.append([q.min(0).tolist(),q.max(0).tolist()])
    B=np.array(boxes);lo,hi=B[:,0],B[:,1]
    count=0;near_count=0;outside_count=0
    def proposals(dim):
        nonlocal count,near_count,outside_count
        out=[]
        centres=list(itertools.product(range(-100,141,10),(-76,-68,-60,-36,0,36,60,68,76),(-20,0,15,30,50,70,88,96)))
        if orthogonal:
            # Functional datum proposal: above rear cuff, outboard of the
            # positive upper strip. This is not a finer whole-space grid.
            centres.extend([(95,55,88),(95,-55,88),(95,48.75,88),(95,-48.75,88)])
        for x,y,z in centres:
            count+=1;c=np.array([x,y,z]);half=np.array(dim)/2;a,b=c-half,c+half
            corners=np.array(list(itertools.product(*zip(a,b))))
            if not inside(corners,32,3.65).all():outside_count+=1;continue
            gaps=np.maximum(np.maximum(a-hi,lo-b),0)
            if np.any(np.sum(gaps*gaps,axis=1)<1.25**2):near_count+=1;continue
            out.append(dict(centre_mm=c.tolist(),bounds_mm=[a.tolist(),b.tolist()],dimensions_mm=dim,
                conservative_all36leg_and_retained_part_bounds_separate=True,actual_BRep_fit_accepted=False))
        return out
    source=[r for r in p['extra']['parts'] if not r['placed_current']]
    # Whole module budgets: selected51mm FHAC body + BOTH9mm/R12.4
    # departure budgets, clamping/heads. Not a finished cable curve or guarantee.
    domains={role:proposals(dim) for role,dim in (('FHAC',[96,32,30]),('FHAC_turn',[32,96,30]),
        ('Monitor5015',[49,35,18]),('F_PWM',[72,16,16]),('F_PWM_turn',[16,72,16]))}
    if orthogonal:
        prior=OUT/'n01-whole-macro-bays.json';pr=json.loads(prior.read_text())
        assert pr['status']=='CONSERVATIVE_MACRO_BAYS_UNRESOLVED_NOT_PROOF_OF_IMPOSSIBILITY'
        files['prior']=prior
        for role,dims in (('FHAC',(96,32,30)),('Monitor5015',(49,35,18)),('F_PWM',(72,16,16))):
            existing={tuple(row['dimensions_mm']) for rows in domains.values() for row in rows}
            defaults={(96,32,30),(32,96,30)} if role=='FHAC' else {(49,35,18)} if role=='Monitor5015' else {(72,16,16),(16,72,16)}
            for i,dim in enumerate(sorted(set(itertools.permutations(dims))-defaults)):
                domains[role+'_orientation'+str(i)]=proposals(list(dim))
    fuse_options=domains['FHAC']+domains['FHAC_turn'];pwm_options=domains['F_PWM']+domains['F_PWM_turn']
    if orthogonal:
        fuse_options=[r for name,rows in domains.items() if name.startswith('FHAC') for r in rows]
        pwm_options=[r for name,rows in domains.items() if name.startswith('F_PWM') for r in rows]
        monitor_options=[r for name,rows in domains.items() if name.startswith('Monitor') for r in rows]
    else:monitor_options=domains['Monitor5015']
    role_options={'F_HY':fuse_options,'F_HP':fuse_options,'F_TY':fuse_options,
        'Monitor5015':monitor_options,'F_PWM':pwm_options}
    targets={'F_HY':[-90,-60,30],'F_HP':[-50,-60,30],'F_TY':[70,-60,30],
        'Monitor5015':[95,55,88],'F_PWM':[-40,-30,15]}
    ranked={role:sorted(rows,key=lambda r:float(np.linalg.norm(np.array(r['centre_mm'])-targets[role])))[:80]
        for role,rows in role_options.items()}
    order=sorted(ranked,key=lambda k:len(ranked[k]));nodes=0;chosen={}
    def search(i):
        nonlocal nodes
        if i==len(order):return True
        role=order[i]
        for row in ranked[role]:
            nodes+=1
            if nodes>50000:return False
            a,b=np.array(row['bounds_mm'])
            if any(np.all(b+1.25>=np.array(r['bounds_mm'])[0]) and np.all(np.array(r['bounds_mm'])[1]+1.25>=a) for r in chosen.values()):continue
            chosen[role]=row
            if search(i+1):return True
            del chosen[role]
        return False
    solved=search(0);missing=[role for role,rows in ranked.items() if not rows]
    report=dict(status='JOINT_MACRO_BAYS_PROPOSED_NOT_N01_SELECTION' if solved else 'CONSERVATIVE_MACRO_BAYS_UNRESOLVED_NOT_PROOF_OF_IMPOSSIBILITY',
        selected=False,N01_complete=False,physical_pass=False,bay_source_parts=source,
        static_material_part_count=len(parts)-len(moving),sampled_leg_bound_count=len(boxes)-(len(parts)-len(moving)),
        proposed_module_budgets_mm={'FHAC':[96,32,30],'Monitor5015':[49,35,18],'F_PWM':[72,16,16]},
        domains=domains,candidate_counts={k:len(v) for k,v in domains.items()},
        whole_allocation=chosen if solved else {},no_conservative_options=missing,search_nodes=nodes,
        proposals_tested=count,coarse_body_rejected=outside_count,near_material_bounds_unresolved=near_count,
        all_orthogonal_module_orientations_considered=orthogonal,
        bbox_intersections_are_not_actual_contacts=True,native_body_BRep_containment_not_yet_queried=True,
        all36leg_samples_not_continuous_sweep=True,full_ports_grips_89plus45routes_stock_and_old33neck_still_open=True,
        next='Use positive separated whole bays for one actual template/port/retention/assembly plan. If none, inspect actual material/meshes in promising bays; do not declare impossibility or start a scalar microsearch.',
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (*files.values(),axesfile,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(report['status'],report['candidate_counts'],'nodes',nodes,'seconds',report['worker_seconds'],flush=True)


if __name__=='__main__':main()
