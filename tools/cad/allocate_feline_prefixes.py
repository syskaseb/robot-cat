"""One coupled domain allocation of complete9mm+quarter-bend end approaches.

Actual saved rigid material and rest/lie P0 scene. No full cable length,
continuous sweep, tool, new mount or shell approval follows from this gate.
"""
import json
import math
import time
import sys
import ast
import subprocess
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import MODEL,BASE,OUT,STAGES
from build_feline_interior_candidate import transform
from check_feline_leg_body import placement
from plan_feline_endpoints import owner,source_port_frames,transfer_port
from plan_feline_interior import inside
from check_feline_shared_space import tube_prefix


def factory_gate(plan,scene,bounds,reader,tick):
    from plan_feline_factory_links import routes
    rows=routes(plan);groups={g['role']:g for g in plan['groups']}
    report=dict(status='FACTORY_LINKS_CHECK_RUNNING',routes=rows,contacts=[],errors=[],outside=[],
        pairs=0,selected=False,physical_pass=False,full_wiring_complete=False,
        scope='All8 complete MTA factory portions against common actual499parts and rest/lie frame/pads, plus mutual wires. Custom extensions/skin/motion still OPEN.')
    sourcefiles=[OUT/'module-layout.json',OUT/'motion-layout.json',OUT/'shared-parts-checks.json',
        BASE/'body-harness-checkpoint/remaining25-interface-allocation.json',
        BASE/'body-harness-checkpoint/leg-stations-plan.json',Path(__file__),
        Path(__file__).with_name('plan_feline_factory_links.py'),Path(__file__).with_name('plan_feline_endpoints.py')]
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        report['source_sha256']={**reader.hashes,**{f.relative_to(ROOT).as_posix():sha(f) for f in sourcefiles}}
        (OUT/'factory-routes.json').write_text(json.dumps(report,indent=2)+'\n')
    def wire(parts):
        edges=[]
        for p in parts:
            start,end=A.Vector(*p['start']),A.Vector(*p['end'])
            edges.append(Part.makeLine(start,end) if p['kind']=='line' else Part.Arc(start,A.Vector(*p['mid']),end).toShape())
        return Part.Wire(edges)
    def pipe(w,r):
        e=w.Edges[0];p=e.valueAt(e.FirstParameter);d=e.tangentAt(e.FirstParameter)
        s=w.makePipeShell([Part.Wire([Part.makeCircle(r,p,d)])],True,False)
        assert s.isValid() and len(s.Solids)==1
        return s
    def near(a,b,gap):
        return sum(max(0,x-y,z-w)**2 for x,y,z,w in [(a.XMin,b.XMax,b.XMin,a.XMax),
            (a.YMin,b.YMax,b.YMin,a.YMax),(a.ZMin,b.ZMax,b.ZMin,a.ZMax)])<=gap*gap
    pipes={}
    save()
    for row in rows:
        name=row['wire'];parts=row['parts'];w=wire(parts);s=pipe(w,row['radius_mm']);pipes[name]=s
        trimmed=[dict(p) for p in parts]
        for index,first in ((0,True),(-1,False)):
            p=trimmed[index];a,b=np.array(p['start']),np.array(p['end']);d=(b-a)/np.linalg.norm(b-a)
            if first:p['start']=(a+2.5*d).tolist()
            else:p['end']=(b-2.5*d).tolist()
        short=pipe(wire(trimmed),row['radius_mm'])
        samples=np.array([list(p) for p in w.discretize(Deflection=.2)])
        if not inside(samples,32,2+row['radius_mm']).all():report['outside'].append(name)
        mates=set(groups[row['source_group']]['objects']+groups[row['joint_group']]['objects'])
        for n,material in scene.items():
            tested=short if n in mates else s
            if not near(tested.BoundBox,bounds[n],1.25):continue
            report['pairs']+=1
            try:
                c=tested.common(material)
                if not c.isNull() and not c.isValid():raise ValueError('Invalid intersection')
                if c.Volume>1e-5:report['contacts'].append(dict(wire=name,part=n,volume_mm3=c.Volume))
                elif tested.distToShape(material)[0]<1.25-1e-5:
                    report['contacts'].append(dict(wire=name,part=n,kind='clearance_below1.25'))
            except Exception as e:report['errors'].append(dict(wire=name,part=n,error=str(e)))
        print('Factory link',name,'length',round(row['guide_mm'],3),'contacts',len(report['contacts']),flush=True);save()
    for i,(an,a) in enumerate(pipes.items()):
        for bn,b in list(pipes.items())[i+1:]:
            if not near(a.BoundBox,b.BoundBox,.2):continue
            report['pairs']+=1
            try:
                if a.distToShape(b)[0]<.2-1e-5:report['contacts'].append(dict(wire=an,part=bn,kind='jacket_gap_below0.2'))
            except Exception as e:report['errors'].append(dict(wire=an,part=bn,error=str(e)))
    report['status']='EIGHT_COMPLETE_FACTORY_LINKS_CLEAR_CUSTOM_WIRING_OPEN' if not any(report[k] for k in ('contacts','errors','outside')) else 'FACTORY_LINKS_REJECTED'
    save();print(json.dumps({k:report[k] for k in ('status','pairs','contacts','errors','outside','worker_seconds')}),flush=True)


def main():
    tick=time.monotonic();reader=SavedShapes();planfile=OUT/'module-layout.json'
    plan=json.loads(planfile.read_text());motionfile=OUT/'motion-layout.json';motion=json.loads(motionfile.read_text())
    receiptfile=OUT/'shared-parts-checks.json';receipt=json.loads(receiptfile.read_text())
    assert receipt['status']=='COMMON_PARTS_TWO_POSES_CLEAR_PREFIXES_WIRES_SKIN_OPEN'
    assert receipt['source_sha256'][planfile.relative_to(ROOT).as_posix()]==sha(planfile)
    groups={g['role']:g for g in plan['groups']};frames=source_port_frames(plan);parts={};part_owner={}
    inputfiles=[BASE/'body-harness-checkpoint/remaining25-interface-allocation.json',
        BASE/'body-harness-checkpoint/w5-current-end-coverage.json',
        BASE/'body-harness-checkpoint/leg-stations-plan.json',Path(__file__).with_name('plan_feline_endpoints.py')]
    for role,g in groups.items():
        t=transform(g)
        for n in g['objects']:
            replacement=plan['reference_substitutions'].get(n)
            if replacement:
                s=reader.shape(ROOT/replacement['source'],replacement['object'])
                s.Placement=t*A.Placement(A.Vector(*replacement['world_shift_before_head_drop_mm']),A.Rotation())*s.Placement
            else:
                s=reader.shape(MODEL,n)
                override=plan.get('part_pose_overrides',{}).get(n)
                if override:s.Placement=transform(override)*s.Placement
                if not t.isIdentity():
                    if t.Rotation.isIdentity():s.translate(t.Base)
                    else:s.Placement=t*s.Placement
            parts[n]=s;part_owner[n]=role
    retained={}
    for r in motion['inventory']:
        n=r['object']
        if n in parts or r['kind']!='surface':continue
        if r['label'].startswith(('P0_','tail/')) or n.startswith(('Print_P0_','Print_CP2_TailRiser','Battery')):
            retained[n]=reader.shape(MODEL,n)
    for i in range(1,5):
        n=f'BellyPadReservation{i}';retained[n]=reader.shape(OUT/'FelineLayoutEnvelope.FCStd',n)
    stage_of={n for g in motion['membership'].values() for ns in g.values() for n in ns}
    scene={**parts,**{n:s for n,s in retained.items() if n not in stage_of}}
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    for index in (0,35):
        pose=motion['poses'][index]
        for code,g in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
            tf=placement(aa,pose['legs'][code]['angles_delta_degrees'])
            for stage,ns in g.items():
                for n in ns:
                    s=retained[n].copy();s.Placement=tf[stage]*s.Placement;scene[f'Pose{index}:{n}']=s
    bounds={n:s.BoundBox for n,s in scene.items()}
    if '--factory-only' in sys.argv:
        factory_gate(plan,scene,bounds,reader,tick);return
    assert '--factory-reuse-git' in sys.argv,'Receive complete factory links before custom prefix allocation'
    parent=sys.argv[sys.argv.index('--factory-reuse-git')+1]
    def gitread(relative):
        return subprocess.run(['git','show',parent+':'+relative],cwd=ROOT,capture_output=True,check=True).stdout
    factoryfile=OUT/'factory-routes.json';factory=json.loads(gitread(factoryfile.relative_to(ROOT).as_posix()))
    assert factory['status']=='EIGHT_COMPLETE_FACTORY_LINKS_CLEAR_CUSTOM_WIRING_OPEN'
    relative=Path(__file__).relative_to(ROOT).as_posix()
    def function_ast(source):
        return ast.dump(next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='factory_gate'),include_attributes=False)
    executed_script=gitread(relative).decode('utf-8')
    assert function_ast(executed_script)==function_ast(Path(__file__).read_text()),'Factory checker changed'
    for n,h in factory['source_sha256'].items():
        if n==relative:
            import hashlib
            assert hashlib.sha256(executed_script.encode()).hexdigest()==h
        else:assert sha(ROOT/n)==h,n
    for row in factory['routes']:
        edges=[]
        for p in row['parts']:
            start,end=A.Vector(*p['start']),A.Vector(*p['end'])
            edges.append(Part.makeLine(start,end) if p['kind']=='line' else Part.Arc(start,A.Vector(*p['mid']),end).toShape())
        w=Part.Wire(edges);e=w.Edges[0];p=e.valueAt(e.FirstParameter);d=e.tangentAt(e.FirstParameter)
        s=w.makePipeShell([Part.Wire([Part.makeCircle(row['radius_mm'],p,d)])],True,False)
        assert s.isValid() and len(s.Solids)==1
        name='FactoryRoute:'+row['wire'];scene[name]=s;bounds[name]=s.BoundBox
    report=dict(status='PREFIX_DOMAIN_ALLOCATION_RUNNING',selected=False,physical_pass=False,
        domains={},missing_first_departures=[],first_land_blocked=[],candidate_errors=[],domain_rejections={},
        source_port_frames=frames,complete_factory_links_reused_from_git=parent,
        factory_checker_AST_unchanged=True,full_factory_routes_not_forced_quarter_prefixes=True,
        material_pairs=0,wire_pairs=0,straight_mm=9,project_R_mm=12.4,
        R_basis='Existing prototype12.4 projectbudget, not manufacturer guaranteed flex/bend data; physicalqualification remains open.',
        factory_lead_budget_mm=100,factory_budget_is_not_catalogue_L140_guarantee=True,
        full_paths_complete=False,hard_material_clearance_mm=1.25,jacket_jacket_gap_mm=.2,
        bundle_basis='Insulated static leads may share a restrainedbundle;1.25air is not imposed betweeneveryjacket. This doesnotqualify exposedends or physicalinsulation.',
        remaining='Allcompleteleadlengths,W1/W3/W4,movinglooms/headposes,newnativegrips/skin/stock/service')
    destination=OUT/'prefix-allocation.json'
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        report['source_sha256']={**reader.hashes,planfile.relative_to(ROOT).as_posix():sha(planfile),
            motionfile.relative_to(ROOT).as_posix():sha(motionfile),receiptfile.relative_to(ROOT).as_posix():sha(receiptfile),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
            **{f.relative_to(ROOT).as_posix():sha(f) for f in inputfiles}}
        destination.write_text(json.dumps(report,indent=2)+'\n')
    specs=[];landfile=BASE/'body-harness-checkpoint/remaining25-interface-allocation.json'
    report['nominal_source_land_file']=landfile.relative_to(ROOT).as_posix()
    def moved(row,point,direction):
        return transfer_port(plan,row['role'],point,direction,frames)
    for row in json.loads(landfile.read_text())['ends']:
        if row['segment']=='factory':continue
        role=owner(row['role'],groups)
        if role not in groups:continue
        land=row['land'];p=np.array(row['point_world_mm']);c=np.array(land['centre_world_mm'])
        direction=None;basis=None
        if role in frames:
            direction=frames[role]['nominal_outward_axis'];basis='Explicit source nominal station-local port'
        elif role.startswith('WAGO:') and groups[role].get('source_entry_axis') is not None:
            direction=groups[role]['source_entry_axis'];basis='Source-end verified nominal casing entry face'
        elif role.endswith('_Joint'):
            g=groups[role];lo,hi=np.array(g['current_bounds_mm']);axis=int(np.argmax(hi-lo))
            direction=np.eye(3)[axis]*np.sign(p[axis]-(hi[axis]+lo[axis])/2)
            assert min(abs(p[axis]-lo[axis]),abs(p[axis]-hi[axis]))<.03,row['id']
            basis='Existing nominal inline case terminal plane, both ends retained'
        elif role.startswith('Bank'):
            base,side=row['role'].split('.');code=base[2:4];index=int(base[4:])+ (3 if code in ('RL','RR') else 0)
            n=f'Ref_Material_F_{"L" if code in ("FL","RL") else "R"}{index}_CP2_{side.upper()}_0_0'
            raw=reader.shape(MODEL,n);bb=raw.BoundBox
            assert min(abs(p[2]-bb.ZMin),abs(p[2]-bb.ZMax))<.03,(row['id'],p[2],bb.ZMin,bb.ZMax)
            direction=[0,0,-1 if abs(p[2]-bb.ZMin)<abs(p[2]-bb.ZMax) else 1]
            basis='Nominal existing TE wire exit point on source terminal Z end, not guessed IN/OUT sign'
        elif role=='S1':
            pin=int(row['role'].split('.')[1]);direction=[0,1 if pin in (2,3) else -1,0]
            basis='Existing ring crimp along +/-Y before actual bore-axis lug clock'
        elif land['intervening_guide_mm']<=1e-6 and abs(np.linalg.norm(c-p)-4.5)<=.05:
            direction=(c-p)/4.5;basis='Verified first9mm source guide land'
        if direction is None:
            report['missing_first_departures'].append(dict(id=row['id'],role=row['role'],reason='Source land downstream, do notinvent first departure'));continue
        role,p,d=moved(row,p,direction)
        specs.append(dict(id=row['id'],wire=row['wire'],segment=row['segment'],role=role,
            point=p.tolist(),direction=d.tolist(),radius=row['project_radius_mm'],departure_basis=basis))
    endfile=BASE/'body-harness-checkpoint/w5-current-end-coverage.json'
    for row in json.loads(endfile.read_text())['body_fixed_boundary_ends']:
        role=owner(row['role'],groups)
        if not role or not role.startswith('Bank'):continue
        role,p,d=moved(row,row['point_world_mm'],[0,0,-1])
        specs.append(dict(id=row['id'],wire=row['wire'],segment='body',role=role,point=p.tolist(),direction=d.tolist(),radius=1))
    report['specifications']=specs
    # Nominal root mates are not required to have1.25air at the wire entry
    # face. Whole tube still may NOT penetrate any root. Own-root distance
    # begins2.5mm outside the mating plane; other material remains full-scope.
    def material(shape,root_names,trimmed):
        b=shape.BoundBox
        for n,s in scene.items():
            bb=bounds[n]
            gap2=sum(max(0,a-c,d-e)**2 for a,c,d,e in [
                (b.XMin,bb.XMax,bb.XMin,b.XMax),(b.YMin,bb.YMax,bb.YMin,b.YMax),(b.ZMin,bb.ZMax,bb.ZMin,b.ZMax)])
            own=n in root_names
            gap=.2 if n.startswith('FactoryRoute:') else 1.25
            if gap2>gap**2:continue
            report['material_pairs']+=1
            try:
                overlap=shape.common(s)
                if not overlap.isNull() and not overlap.isValid():raise ValueError('Invalid intersection')
                if overlap.Volume>1e-5:return dict(part=n,kind='contact',volume_mm3=overlap.Volume)
                if (trimmed if own else shape).distToShape(s)[0]<gap-1e-5:return dict(part=n,kind='insufficient_clearance',required_mm=gap)
            except Exception as e:return dict(part=n,kind='kernel_error',error=str(e))
        return None
    shapes={};domain_points={}
    for spec in specs:
        if time.monotonic()-tick>300:
            report['status']='COMPUTE_BUDGET_REACHED_PARTIAL_DOMAINS';save();print(report['status'],flush=True);return
        p=np.array(spec['point']);d=np.array(spec['direction']);d=d/np.linalg.norm(d);r=spec['radius']
        vertex=Part.Vertex(A.Vector(*p));root_names=set()
        for n in groups[spec['role']]['objects']:
            if vertex.distToShape(scene[n])[0]<=r+1.25:root_names.add(n)
        straight=Part.makeCylinder(r,9,A.Vector(*p),A.Vector(*d))
        trimmed_straight=Part.makeCylinder(r,6.5,A.Vector(*(p+2.5*d)),A.Vector(*d))
        blocked=material(straight,root_names,trimmed_straight)
        if blocked:
            report['first_land_blocked'].append(dict(id=spec['id'],**blocked));report['domains'][spec['id']]=[];save();continue
        u=np.array([1.,0,0]) if abs(d[0])<.9 else np.array([0.,1,0]);u-=d*np.dot(u,d);u/=np.linalg.norm(u);v=np.cross(d,u)
        candidates=[];rejections=[]
        for k in range(8):
            bend=np.cos(k*np.pi/4)*u+np.sin(k*np.pi/4)*v
            q=p+d*9;t=np.linspace(0,np.pi/2,25)
            samples=np.r_[np.array([p+d*l for l in np.linspace(0,9,6)]),q+12.4*(np.sin(t)[:,None]*d+(1-np.cos(t))[:,None]*bend)]
            fits=inside(samples,32,margin=2+r)
            if not fits.all() and spec['role']!='S0':
                rejections.append(dict(option=k,kind='outside_proposed_inner_space'));continue
            try:s=tube_prefix(p,d,r,bend,12.4)
            except Exception as e:report['candidate_errors'].append(dict(id=spec['id'],option=k,error=str(e)));continue
            trimmed=tube_prefix(p+2.5*d,d,r,bend,12.4,straight_mm=6.5)
            collision=material(s,root_names,trimmed)
            if collision:
                rejections.append(dict(option=k,**collision));continue
            key=(spec['id'],k);shapes[key]=s;domain_points[key]=samples[-1]
            candidates.append(dict(option=k,bend=bend.tolist(),end_mm=samples[-1].tolist(),main_loft_contains_samples=bool(fits.all())))
        report['domains'][spec['id']]=candidates
        report['domain_rejections'][spec['id']]=rejections
        print('Prefix domain',spec['id'],len(candidates),'materialpairs',report['material_pairs'],flush=True);save()
    # Pair predicates are cached; MRV forward checking selects the whole set,
    # not a greedy firstgood direction that blocks the remaining neighbours.
    compatibility={};spec_by_id={s['id']:s for s in specs}
    def compatible(a,b):
        key=tuple(sorted((a,b)))
        if key in compatibility:return compatibility[key]
        sa,sb=spec_by_id[a[0]],spec_by_id[b[0]]
        if sa['wire']==sb['wire'] and sa['segment']==sb['segment']=='factory':
            lower_bound=2*(9+np.pi*12.4/2)+np.linalg.norm(domain_points[a]-domain_points[b])
            if lower_bound>100+1e-6:compatibility[key]=False;return False
        aa,bb=shapes[a],shapes[b];ba,bc=aa.BoundBox,bb.BoundBox
        gap2=sum(max(0,x-y,z-w)**2 for x,y,z,w in [(ba.XMin,bc.XMax,bc.XMin,ba.XMax),(ba.YMin,bc.YMax,bc.YMin,ba.YMax),(ba.ZMin,bc.ZMax,bc.ZMin,ba.ZMax)])
        if gap2>=.2**2:compatibility[key]=True;return True
        report['wire_pairs']+=1
        try:ok=aa.distToShape(bb)[0]>=.2-1e-5
        except Exception:ok=False
        compatibility[key]=ok;return ok
    domains={n:[(n,c['option']) for c in cs] for n,cs in report['domains'].items()}
    nodes=0
    def solve(remaining,chosen):
        nonlocal nodes
        nodes+=1
        if time.monotonic()-tick>300:raise TimeoutError('300s computation budget')
        if not remaining:return chosen
        n=min(remaining,key=lambda key:len(remaining[key]))
        for a in remaining[n]:
            new={m:[b for b in ds if compatible(a,b)] for m,ds in remaining.items() if m!=n}
            if any(not ds for ds in new.values()):continue
            result=solve(new,{**chosen,n:a[1]})
            if result is not None:return result
        return None
    try:solution=None if any(not d for d in domains.values()) else solve(domains,{})
    except TimeoutError:solution=None;report['solve_timeout']=True
    report.update(status='COUPLED_KNOWN_PREFIXES_CLEAR_FULL_WIRING_OPEN' if solution else 'PREFIX_ALLOCATION_REJECTED_OR_INCOMPLETE',
        allocation=solution,nodes=nodes,supported_prefix_count=len(specs),complete_prefix_scope=False,
        all52_not_all_robot_ends=True,stock_or_full_factory_route_qualified=False)
    save();print(json.dumps(dict(status=report['status'],prefixes=len(specs),empty_domains=[n for n,d in domains.items() if not d],nodes=nodes,
        material_pairs=report['material_pairs'],wire_pairs=report['wire_pairs'],seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()
