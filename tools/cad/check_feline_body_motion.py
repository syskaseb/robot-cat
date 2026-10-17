"""Whole changed fixed module/known-wire scene vs intermediate lying poses.

Rest/lying endpoint module checks and original P0/feet/head proofs are reused.
This closes neither12moving looms nor80complete electrical paths. Stop after
first rejected pose; do not run unchanged bad topology through the matrix.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from datetime import datetime as task_datetime,timezone as task_timezone
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,STAGES
from check_feline_leg_body import placement
from check_feline_shared_space import tube_prefix


def main():
    tick=time.monotonic();reader=SavedShapes()
    interior=json.loads((OUT/'interior-native-checks.json').read_text());native=ROOT/interior['native']
    assert interior['status']=='COMMON_INTERIOR_ENDPOINTS_CLEAR_MOUNTS_WIRES_SKIN_OPEN'
    assert sha(native)==interior['native_sha256']
    plan=json.loads((OUT/'module-layout.json').read_text());motion=json.loads((OUT/'motion-layout.json').read_text())
    sharedfile=OUT/'shared-parts-checks.json';shared=json.loads(sharedfile.read_text())
    assert shared['status']=='COMMON_PARTS_TWO_POSES_CLEAR_PREFIXES_WIRES_SKIN_OPEN'
    assert shared['source_sha256'][(OUT/'module-layout.json').relative_to(ROOT).as_posix()]==sha(OUT/'module-layout.json')
    fixed={};groups={}
    for g in plan['groups']:
        if g['role']=='HeadMechanism':continue
        parts={n:reader.shape(native,n) for n in g['objects']};fixed.update(parts)
        groups[g['role']]=(parts,Part.makeCompound(list(parts.values())).BoundBox)
    moving={n for g in motion['membership'].values() for ns in g.values() for n in ns}
    leg={n:reader.shape(native,n) for n in moving}
    prefixesfile=OUT/'prefix-allocation.json';factoryfile=OUT/'factory-routes.json'
    prefixes=json.loads(prefixesfile.read_text());factory=json.loads(factoryfile.read_text())
    for p in (prefixesfile,factoryfile):assert interior['reused_qualified_interface_receipts'][p.relative_to(ROOT).as_posix()]==sha(p)
    rows={r['id']:r for r in prefixes['specifications']};wires={}
    for key,k in prefixes['allocation'].items():
        r=rows[key];bend=next(c['bend'] for c in prefixes['domains'][key] if c['option']==k)
        wires[key]=tube_prefix(r['point'],r['direction'],r['radius'],bend,12.4)
    for row in factory['routes']:
        edges=[]
        for e in row['parts']:
            a,b=A.Vector(*e['start']),A.Vector(*e['end']);edges.append(Part.makeLine(a,b) if e['kind']=='line' else Part.Arc(a,A.Vector(*e['mid']),b).toShape())
        w=Part.Wire(edges);e=w.Edges[0];p=e.valueAt(e.FirstParameter);t=e.tangentAt(e.FirstParameter)
        wires['Factory:'+row['wire']]=w.makePipeShell([Part.Wire([Part.makeCircle(row['radius_mm'],p,t)])],True,False)
    bounds={n:s.BoundBox for n,s in {**fixed,**wires}.items()}
    report=dict(status='INTERMEDIATE_BODY_MOTION_RUNNING',selected=False,physical_pass=False,
        contacts=[],clearance_failures=[],errors=[],material_pairs=0,wire_pairs=0,poses=[],
        fixed_module_parts=len(fixed),known_wires=len(wires),
        reused_module_endpoint_pose_indices=[0,35],original_P0_feet_head_scope_reused=True,
        full_wiring_complete=False,moving12looms_complete=False,continuous_motion=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (native,OUT/'module-layout.json',OUT/'motion-layout.json',sharedfile,prefixesfile,factoryfile,Path(__file__))})
    dest=OUT/'body-intermediate-motion.json';deadline=task_datetime.fromisoformat('2026-10-17T07:30:00+00:00')
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);dest.write_text(json.dumps(report,indent=2)+'\n')
    def gate():
        if task_datetime.now(task_timezone.utc)>=deadline:
            report.update(status='BODY_INTERMEDIATE_MOTION_DEADLINE_PARTIAL',deadline_reached=True);save();raise TimeoutError('Deadline')
    def near(a,b,gap=0):
        return sum(max(0,x-y,z-w)**2 for x,y,z,w in [(a.XMin,b.XMax,b.XMin,a.XMax),(a.YMin,b.YMax,b.YMin,a.YMax),(a.ZMin,b.ZMax,b.ZMin,a.ZMax)])<=gap*gap
    def check(n,s,bn,b,index,wire=False):
        gate();report['wire_pairs' if wire else 'material_pairs']+=1
        try:
            c=s.common(b)
            if not c.isNull() and not c.isValid():raise ValueError('Invalid exact intersection')
            if c.Volume>1e-5:
                pts,_=c.tessellate(.2);v=[list(p) for p in pts]
                report['contacts'].append(dict(leg_part=n,other=bn,pose=index,wire=wire,volume_mm3=c.Volume,
                    witness_mesh_bounds_mm=[[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]] if v else None))
            elif wire:
                distance=s.distToShape(b)[0]
                if distance<1.25-1e-5:report['clearance_failures'].append(dict(leg_part=n,wire=bn,pose=index,gap_mm=distance,required_mm=1.25))
        except Exception as exc:report['errors'].append(dict(leg_part=n,other=bn,pose=index,error=str(exc)))
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes'];save()
    for index in range(1,35):
        gate();pose=motion['poses'][index];before=[report['material_pairs'],report['wire_pairs']]
        for code,g in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES];tf=placement(aa,pose['legs'][code]['angles_delta_degrees'])
            for stage,ns in g.items():
                posed={}
                for n in ns:
                    s=leg[n].copy();s.Placement=tf[stage]*s.Placement;posed[n]=(s,s.BoundBox)
                gb=Part.makeCompound([s for s,b in posed.values()]).BoundBox
                for parts,group_box in groups.values():
                    if not near(gb,group_box):continue
                    for n,(s,b) in posed.items():
                        for bn,other in parts.items():
                            if near(b,bounds[bn]):check(n,s,bn,other,index)
                for bn,other in wires.items():
                    if not near(gb,bounds[bn],1.25):continue
                    for n,(s,b) in posed.items():
                        if near(b,bounds[bn],1.25):check(n,s,bn,other,index,True)
        report['poses'].append(dict(index=index,material_pairs=report['material_pairs']-before[0],wire_pairs=report['wire_pairs']-before[1]));save()
        print('Body intermediate',index,'hits',len(report['contacts']),'gaps',len(report['clearance_failures']),'errors',len(report['errors']),flush=True)
        if any(report[k] for k in ('contacts','clearance_failures','errors')):
            report.update(status='INTERMEDIATE_BODY_MOTION_REJECTED_NO_REPEAT_POSES');save();return
    report['source_sha256'].update(reader.hashes)
    report.update(status='CHANGED_FIXED_MODULES_AND69KNOWN_WIRES_INTERMEDIATE_SAMPLES_CLEAR_FULL_LOOMS_OPEN');save()
    print(json.dumps({k:report[k] for k in ('status','material_pairs','wire_pairs','worker_seconds')}),flush=True)


if __name__=='__main__':
    try:main()
    except TimeoutError:print('Deadline: partial saved; no new checks',flush=True)
