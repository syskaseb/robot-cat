"""One joint allocation using actual bodies, cradle/head and both wire bends.

Six anatomical side bays replace the failed filled96mm macro boxes; no finer
translation grid. Real BRep checks nominate only, not complete N01/wiring.
"""
import hashlib
import itertools
import json
import sys
import time
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,STAGES
from check_feline_all_current_lands import near
from check_feline_shared_space import tube_prefix
from check_feline_leg_body import placement
from feline_current_scene import load,box


def main():
    coherent='--coherent-tiers' in sys.argv
    tick=time.monotonic();dest=OUT/('n01-actual-five-module-plan-r2.json' if coherent else 'n01-actual-five-module-plan.json');assert not dest.exists()
    scene,meta,templates,data,pins,changes=load(negative_row=not coherent,upper_rows=coherent)
    report=dict(status='RUNNING_ACTUAL_JOINT_FIVE_MODULE_PLAN',selected=False,N01_complete=False,
        physical_pass=False,negative_row_changes=changes,domains={},blocked=[],errors=[],pairs=0,
        scope='Actual five templates, provisional cradle/tie/head and BOTH9mm/R12.4departures. All retained tail and sampled36leg poses. Full134routes/other20grips/neck/assembly not qualified.',
        factory100mm_usable_is_project_assumption_not_catalogue=True,source_sha256=pins,
        wire_OD_mm=3.1,hard_clearance_mm=1.25,skin_budget_mm=3.65)
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s actual whole allocation budget')
    reader=SavedShapes();outer=reader.shape(OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd','TorsoEnvelope')
    shell=Part.makeCompound(outer.Shells);motionfile=OUT/'motion-layout.json';motion=json.loads(motionfile.read_text())
    axesfile=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axesfile.read_text())['axes']
    moving={n:s for n,s in scene.items() if meta[n].get('role','').startswith('leg:')}
    obstacles={n:s for n,s in scene.items() if n not in moving};deferred={}
    boxes={n:s.BoundBox for n,s in obstacles.items()}
    # Identical rest geometry not checked twice; actual36transforms cached once.
    for sample in motion['poses'][:36]:
        for code,groups in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==st) for st in STAGES]
            tf=placement(aa,sample['legs'][code]['angles_delta_degrees'])
            for stage,names in groups.items():
                for n in names:
                    key=f'{n}@pose{sample["index"] if "index" in sample else motion["poses"].index(sample)}'
                    b=moving[n].BoundBox
                    corners=[tf[stage].multVec(A.Vector(*q)) for q in itertools.product((b.XMin,b.XMax),(b.YMin,b.YMax),(b.ZMin,b.ZMax))]
                    bb=A.BoundBox()
                    for v in corners:bb.add(v)
                    boxes[key]=bb;deferred[key]=(moving[n],tf[stage]);obstacles[key]=None
    valid={n:None for n in obstacles}
    save();print('Canonical current material',len(scene),'moving samples',len(obstacles)-len(scene)+len(moving),flush=True)
    domains={};geometries={};blocked=[]
    def check(key,components):
        gate();assembly=Part.makeCompound(list(components.values()));bb=assembly.BoundBox
        # Coarse bounds nominate pairs only; valid Boolean or exact distance decides.
        for n,s in obstacles.items():
            if not near(bb,boxes[n],1.25):continue
            if s is None:
                source,tf=deferred[n];s=source.copy();s.Placement=tf*s.Placement
                obstacles[n]=s
            if valid[n] is None:valid[n]=s.isValid() and bool(s.Solids)
            if not valid[n]:return dict(part=n,error='Invalid supplier/current geometry')
            for cn,c in components.items():
                if not near(c.BoundBox,boxes[n],1.25):continue
                gate();report['pairs']+=1
                v=c.common(s);assert v.isNull() or v.isValid(),(key,cn,n)
                if v.Volume>1e-5:return dict(part=n,component=cn,volume_mm3=v.Volume)
                gap=c.distToShape(s)[0]
                if gap<1.25-1e-5:return dict(part=n,component=cn,gap_mm=gap)
        v=assembly.cut(outer);assert v.isNull() or v.isValid()
        if v.Volume>1e-5:return dict(part='TorsoEnvelope',outside_mm3=v.Volume)
        gap=assembly.distToShape(shell)[0]
        if gap<3.65-1e-5:return dict(part='TorsoEnvelope',boundary_gap_mm=gap)
        return None
    def placed(role,centre,rotation=None):
        _,s,_=templates[role];s=s.copy();old=s.BoundBox.Center
        r=rotation or A.Rotation();s.Placement=A.Placement(A.Vector(*centre)-r.multVec(old),r)*s.Placement
        return s
    try:
        # Full first bends for22changed mouths, no declaration of full20WAGO grip.
        rowprefix={};rows=[st for st in data['ports']['stations'] if st['ref'] in {r['ref'] for r in changes}]
        for st in rows:
            for p in st['occupied_ports']:
                key=p['endpoint'];rad=2.1 if st['ref']=='P_AUX' else 1.55
                rowprefix[key]=tube_prefix(p['point_mm'],p['departure_axis'],rad,[0,0,1],12.4,straight_mm=22 if coherent else 9)
        report['negative_row_prefixes']=[]
        if coherent:
            report['changed_case_fit']=[]
            for r in changes:
                own=r['name'];removed=obstacles.pop(own)
                failure=check('case:'+own,{'case':removed});obstacles[own]=removed
                report['changed_case_fit'].append(dict(ref=r['ref'],failure=failure))
        for name,s in rowprefix.items():
            # Own casing intentionally starts at nominal wire mouth. Exclude
            # only this exact mate, not every other casing or planned restraint.
            own=next(r['name'] for r in changes if r['ref']==name.rsplit('.',1)[0]);removed=obstacles.pop(own)
            failure=check('row:'+name,{'wire':s});obstacles[own]=removed
            report['negative_row_prefixes'].append(dict(endpoint=name,failure=failure))
        bays=[(-10,-68,25),(-10,68,25),(65,-68,25)] if coherent else [(x,y,15) for x,y in itertools.product((-85,-10,65),(-68,68))]
        result_cache={}
        for role in ('F_HY','F_HP','F_TY'):
            domains[role]=[]
            for centre in bays:
                for bend_kind in ('up','inboard'):
                    key=role+':'+str(centre)+':'+bend_kind;c=placed(role,centre);b=c.BoundBox
                    cradle=box([b.XMin-1.25,b.YMin-2,b.ZMin-2],[b.XMax+1.25,b.YMax+2,b.ZMin])
                    comps={'case':c,'cradle':cradle}
                    for i,x in enumerate((centre[0]-15,centre[0]+15)):
                        # Complete loop/head reservations, no lever is crossed.
                        out=box([x-1.25,b.YMin-.8,b.ZMin-.8],[x+1.25,b.YMax+.8,b.ZMax+.8])
                        inn=box([x-2,b.YMin,b.ZMin],[x+2,b.YMax,b.ZMax])
                        comps['tie'+str(i)]=out.cut(inn)
                        h=(1 if centre[1]>0 else -1)*(-1 if coherent else 1);y=centre[1]+h*(10.125+3.3)
                        comps['head'+str(i)]=box([x-2.5,y-2.5,centre[2]-2],[x+2.5,y+2.5,centre[2]+2])
                    for side in (-1,1):
                        bend=[0,0,1] if bend_kind=='up' else [0,-np.sign(centre[1]),0]
                        comps['wire'+str(side)]=tube_prefix([centre[0]+side*25.5,centre[1],centre[2]],[side,0,0],1.55,bend,12.4)
                    # Exact normalized source body BRep signatures, not names,
                    # permit reuse among the same purchased FHAC template.
                    sig=tuple(hashlib.sha256(s.exportBrepToString().encode('utf-8')).hexdigest() for s in comps.values())
                    if sig in result_cache:fail=result_cache[sig]
                    else:fail=check(key,comps);result_cache[sig]=fail
                    row=dict(key=key,centre_mm=centre,bend_kind=bend_kind,failure=fail)
                    if fail:blocked.append(row)
                    else:domains[role].append(row);geometries[key]=comps
                print(role,centre,'accepted',len(domains[role]),flush=True);save()
        domains['Monitor5015']=[]
        for centre in ((50,68,0),(50,-68,0),(95,55,88)):
            for vertical in (True,False):
                rot=A.Rotation(A.Vector(1,0,0),90) if vertical else A.Rotation()
                key='Monitor5015:'+str(centre)+':'+str(vertical);c=placed('Monitor5015',centre,rot);b=c.BoundBox
                comps={'case':c,'seat':box([b.XMin-2,b.YMin-2,b.ZMin-2],[b.XMax+2,b.YMax+2,b.ZMin])}
                fail=check(key,comps);row=dict(key=key,centre_mm=centre,vertical=vertical,failure=fail)
                if fail:blocked.append(row)
                else:domains['Monitor5015'].append(row);geometries[key]=comps
        domains['F_PWM']=[]
        for centre in (((60,-76,-20),) if coherent else ((-10,-30,15),(20,30,15),(0,0,15))):
            key='F_PWM:'+str(centre);c=placed('F_PWM',centre);b=c.BoundBox
            comps={'sleeve':c,'seat':box([b.XMin-1,b.YMin-2,b.ZMin-2],[b.XMax+1,b.YMax+2,b.ZMin])}
            for side in (-1,1):comps['wire'+str(side)]=tube_prefix([centre[0]+side*21,centre[1],centre[2]],[side,0,0],1.05,[0,0,1],8.4)
            fail=check(key,comps);row=dict(key=key,centre_mm=centre,failure=fail)
            if fail:blocked.append(row)
            else:domains['F_PWM'].append(row);geometries[key]=comps
        chosen={};order=sorted(domains,key=lambda k:len(domains[k]));pair_cache={}
        def compatible(a,b):
            key=tuple(sorted((a,b)))
            if key not in pair_cache:
                aa=Part.makeCompound(list(geometries[a].values()));bb=Part.makeCompound(list(geometries[b].values()))
                pair_cache[key]=not near(aa.BoundBox,bb.BoundBox,1.25) or aa.distToShape(bb)[0]>=1.25-1e-5
            return pair_cache[key]
        def solve(i):
            if i==len(order):return True
            role=order[i]
            for row in domains[role]:
                if not all(compatible(row['key'],other['key']) for other in chosen.values()):continue
                chosen[role]=row
                if solve(i+1):return True
                del chosen[role]
            return False
        found=solve(0);report.update(domains=domains,blocked=blocked,whole_allocation=chosen if found else {},
            joint_actual_allocation_found=found,intermodule_pairs=len(pair_cache),
            status='ACTUAL_FIVE_MODULE_BAYS_PROPOSED_FULL_WIRING_OPEN' if found else 'ACTUAL_JOINT_FIVE_MODULE_PLAN_UNRESOLVED')
        if found:
            bundle=dest.with_suffix('.zip');parts=[]
            with zipfile.ZipFile(bundle,'x',compression=zipfile.ZIP_DEFLATED) as zz:
                for role,row in chosen.items():
                    for component,s in geometries[row['key']].items():
                        raw=s.exportBrepToString().encode('utf-8');entry=f'{len(parts):03d}.brep';zz.writestr(entry,raw)
                        parts.append(dict(name=role+':'+component,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
            report.update(parts=parts,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle))
    except Exception as exc:report['errors'].append(repr(exc));report['status']='ACTUAL_MODULE_PLAN_PARTIAL'
    report.update(domains=domains,blocked=blocked,source_sha256={**pins,**reader.hashes,
        **{p.relative_to(ROOT).as_posix():sha(p) for p in (motionfile,axesfile,Path(__file__),Path(__file__).with_name('feline_current_scene.py'))}})
    save();print(report['status'],{k:len(v) for k,v in domains.items()},report['worker_seconds'],report['errors'],flush=True)


if __name__=='__main__':main()
