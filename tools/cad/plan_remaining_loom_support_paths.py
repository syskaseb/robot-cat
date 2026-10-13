"""One bounded shared36land support-space plan, before detailed native CAD.

Actual meshes are reservations, never a collision proof. Owner-relative
sampling includes retained head/current source carriers, all leg stages and
all current source-wire poses. No wire path or supplier dimension is changed.
"""
import heapq
import copy
import itertools
import json
import math
import sys
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import numpy as np
import build_complete_source_carriers as B
from fast_carrier_reservations import TriangleBucket,WireBucket
from loom_land_port import build as build_port
from compact_loom_land_port import build as build_compact_port
from support_entry_port import build as build_entry_port

P=B.P
ANGLES=(-15,0,15)


def search(start,goal,low,high,clear,existing_points=()):
    coords=[sorted(set([low[i]+4*j for j in range(math.ceil((high[i]-low[i])/4)+1)]
                       +[start[i],goal[i]]+[p[i] for p in existing_points if low[i]<=p[i]<=high[i]])) for i in range(3)]
    first=tuple(v.index(x) for v,x in zip(coords,start))
    last=tuple(v.index(x) for v,x in zip(coords,goal))
    def point(k):return [v[j] for v,j in zip(coords,k)]
    def estimate(k):return sum(abs(x-y) for x,y in zip(point(k),goal))
    sc,gc=clear(start),clear(goal)
    if not sc or not gc:
        return dict(points_mm=[],start_clear=sc,goal_clear=gc,expansions=0,
                    search_seconds=0,rejection='Endpoint reservation occupied; inspect exact material before rerouting')
    queue=[(estimate(first),0,first)];best={first:0};parents={}
    tick=time.monotonic();count=0;found=None
    while queue and count<20000 and time.monotonic()-tick<12:
        _,cost,k=heapq.heappop(queue)
        if cost!=best[k]:continue
        count+=1
        if k==last:found=k;break
        for axis in range(3):
            for step in (-1,1):
                kk=list(k);kk[axis]+=step
                if not 0<=kk[axis]<len(coords[axis]):continue
                kk=tuple(kk);a,b=point(k),point(kk)
                if not clear(b) or not clear([(x+y)/2 for x,y in zip(a,b)]):continue
                distance=cost+math.dist(a,b)
                if distance>=best.get(kk,math.inf):continue
                best[kk]=distance;parents[kk]=k
                heapq.heappush(queue,(distance+estimate(kk),distance,kk))
    path=[]
    if found is not None:
        key=found;raw=[point(key)]
        while key!=first:key=parents[key];raw.append(point(key))
        raw.reverse();path=[raw[0]]
        for a,b,c in zip(raw,raw[1:],raw[2:]):
            if next(i for i in range(3) if a[i]!=b[i])!=next(i for i in range(3) if b[i]!=c[i]):path.append(b)
        path.append(raw[-1])
    return dict(points_mm=path,start_clear=sc,goal_clear=gc,expansions=count,
                search_seconds=round(time.monotonic()-tick,3),
                rejection=None if path else 'Bounded planning search exhausted, NOT proof of geometric impossibility')


def run():
    tick=time.monotonic();pf=P.OUT/'remaining-loom-roots-plan.json';ff=P.OUT/'remaining-loom-root-faces.json'
    plan,faces=[json.loads(p.read_text()) for p in (pf,ff)]
    shared_mode='--shared-recovery' in sys.argv
    entry_mode='--entry-ports' in sys.argv or shared_mode
    resolving='--resolve-boundaries' in sys.argv or entry_mode
    priorfile=P.OUT/('remaining-support-entry-received.json' if '--resume-entry' in sys.argv else 'remaining-support-resolved-paths.json' if entry_mode else 'remaining-support-current-paths.json')
    recoveryfile=P.OUT/'remaining-support-shared-recovery-plan.json'
    recovery=json.loads(recoveryfile.read_text()) if shared_mode else None
    if shared_mode:
        assert not recovery['unresolved'],'Resolve actual witness ownership before rerouting'
        for name,digest in recovery['source_sha256'].items():assert P.SHA(P.ROOT/name)==digest,name
        priorfile=P.OUT/'remaining-support-final-paths.json'
    boundaryfile=P.OUT/'remaining-support-boundaries.json'
    prior=json.loads(priorfile.read_text()) if resolving else None
    boundary=json.loads(boundaryfile.read_text()) if resolving else None
    if resolving:
        for name,digest in boundary['source_sha256'].items():assert P.SHA(P.ROOT/name)==digest,name
    for receipt in (plan,faces):
        for name,digest in receipt['source_sha256'].items():assert P.SHA(P.ROOT/name)==digest,name
    nf=P.OUT/('front-fixed-port-clearance-native.json' if '--front-clearance' in sys.argv else 'complete-source-carriers-native.json')
    native=json.loads(nf.read_text())
    model=P.ROOT/native['native'];assert P.SHA(model)==native['native_sha256']
    familyfile=P.OUT/'leg-source-near-member-plan.json';family=json.loads(familyfile.read_text())
    seedfile=P.OUT/'remaining-carrier-seed-proof.json';seedproof=json.loads(seedfile.read_text())
    assert seedproof['status']=='FOUR_HIP_ROOT_SEEDS_EXACT_UNCHANGED_SUBSETS'
    for name,digest in seedproof['source_sha256'].items():assert P.SHA(P.ROOT/name)==digest,name
    retentionfile=P.OUT/('remaining-retention-entry.json' if entry_mode else 'remaining-retention-current.json' if '--current-retention' in sys.argv else 'remaining-retention-rest.json');retention=json.loads(retentionfile.read_text())
    if '--current-retention' in sys.argv:assert not retention['errors'],retention['errors']
    for name,digest in retention['source_sha256'].items():assert P.SHA(P.ROOT/name)==digest,name
    complete_groups=[g for g in retention['groups'] if g['root_world_mm'] and not any('error' in p for p in g['ports'])]
    lands={r['id']:r for g in plan['groups'] for r in g['lands']}
    profile_parts={};arrival_failures=[]
    for group in complete_groups:
        for port in group['ports']:
            builder=build_compact_port if port['recipe'].get('construction')=='single_post_axial_entry_below_band' else build_port
            shapes=build_entry_port(lands[port['land_id']],port)
            x,y,z=port['arrival_world_mm'];seed=P.box([x-2,y-3,z-2,x+2,y+3,z+2])
            overlap=seed.common(shapes['band']).Volume;joined=seed.common(shapes['body']).Volume
            if overlap>1e-5 or joined<1:
                arrival_failures.append(dict(land_id=port['land_id'],band_intersection_mm3=overlap,post_connection_mm3=joined))
            profile_parts[port['land_id']]=(shapes,group)
    if arrival_failures:
        receipt=dict(status='REJECTED_COMPLETE_ARM_ARRIVAL_SEEDS_BEFORE_MESH',failures=arrival_failures,
                     inherited_open_groups=retention['errors'],selected=False,W5_complete=False,physical_pass=False,
                     decision='Complete port was statically clear, but world-aligned4x6x4arm arrival conflicts with rotated band. Choose a manufacturable approach direction/oriented stub BEFORE mesh/path search; do not move cable lands.',
                     source_sha256={p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (pf,retentionfile,Path(__file__),Path(__file__).with_name('loom_land_port.py'))},
                     worker_seconds=round(time.monotonic()-tick,3))
        (P.OUT/'remaining-arm-arrival-checks.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(receipt),flush=True)
        return
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    membership={'P0_'+r['name']:r['stage'].split('_')[1:] for r in members if r['stage'].startswith('Motion_')}
    reader=B.H.P.SavedShapes();targets,wires,archive,sf,headwires=B.current_scene(reader)
    for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
        code=next(r['cad_code'] for r in family['hips'] if r['physical_leg']==leg)
        name=leg+'SourceCarrier';targets[name]=reader.shape(model,name);membership[name]=(code,'Hip')
        # Old cap subset proof also applies to this precise native candidate
        # only after confirming its same seed remains entirely in the body.
        group=next(g for g in plan['groups'] if g['id']==leg+'HipExtension')
        x,y,z=group['root_world_mm'];seed=P.box([x-2,y-3,z-2,x+2,y+3,z+2])
        assert seed.cut(targets[name]).Volume<1e-6,(name,'Native cap seed changed')
    for name in reader.doc(model):
        if not name.startswith('Ref_'):continue
        actual=name[4:];targets[actual]=reader.shape(model,name)
        if actual.endswith('SourceCaseBond'):
            leg=actual.removesuffix('SourceCaseBond')
            code=next(r['cad_code'] for r in family['hips'] if r['physical_leg']==leg)
        else:
            loom=actual.removesuffix('IndependentBand')
            code=next(r['cad_code'] for r in family['hips'] if r['loom']==loom)
        membership[actual]=(code,'Hip')
    for land_id,(shapes,group) in profile_parts.items():
        for prefix,key in (('PlannedPort_','body'),('PlannedBand_','band')):
            name=prefix+land_id;targets[name]=shapes[key]
            if group['owner_stage']!='Body':membership[name]=group['owner_stage'].split('_')[1:]
    for sleeve in retention['sleeve_reservations']:
        axis=A.Vector(*sleeve['axis']);centre=A.Vector(*sleeve['centre_world_mm'])
        targets[sleeve['name']]=B.Part.makeCylinder(sleeve['diameter_project_mm']/2,sleeve['length_mm'],centre-axis*sleeve['length_mm']/2,axis)
        membership[sleeve['name']]=sleeve['owner_stage'].split('_')[1:]
    shared_inputs=[]
    if shared_mode:
        # Frozen COMPLETE new supports are moving obstacles, not just ports.
        # Other changed groups retain their old shape conservatively during
        # planning; a final joint actual-material gate is still mandatory.
        seen_shared=set()
        for cf in (P.OUT/'remaining-support-cache').glob('*/manifest.json'):
            data=json.loads(cf.read_text());group=data['contract']['group'];name=group['id']
            if data['contract']['paths']!=next((g for g in prior['groups'] if g['id']==name),None):continue
            assert name not in seen_shared,'Ambiguous shared support cache'
            seen_shared.add(name);shared_inputs.append(cf)
            row=data['shapes'][name];bf=cf.parent/row['file'];assert P.SHA(bf)==row['sha256']
            s=B.Part.Shape();s.read(str(bf));assert s.isValid(),name
            key='SharedSupport_'+name;targets[key]=s;shared_inputs.append(bf)
            if group['owner_stage']!='Body':membership[key]=group['owner_stage'].split('_')[1:]
        assert len(seen_shared)==12,'Need complete shared obstacle set'
        shared_inputs.append(recoveryfile)
    transforms={}
    for code in ('FL','FR','RL','RR'):
        for h,k,a in itertools.product(ANGLES,repeat=3):
            T=A.Placement()
            for stage,angle in zip(('Hip','Knee','Ankle'),(h,k,a)):
                ax=next(r for r in axes if r['code']==code and r['stage']==stage)
                p=A.Vector(*ax['pivot_mm']);r=A.Rotation(A.Vector(*ax['axis']),angle)
                T=T*A.Placement(p-r.multVec(p),r);transforms[code,h,k,a,stage]=T
    wirecurves=[(name,s,rad,None,None,None) for name,(s,rad) in wires.items()]
    wirepoints=[(name,[p for e in s.Edges for p in e.discretize(Distance=1)],rad,None,None,None)
                for name,(s,rad) in wires.items()]
    for route in family['routes']:
        code=route['source']['cad_code']
        for h,k in itertools.product(ANGLES,repeat=2):
            s=P.wire(B.parts_for_loom(family,route['loom'],h,k,axes)+B.moved_parts(route['source_parts'],route['source'],h,k,axes))
            wirecurves.append((route['loom'],s,3,code,h,k))
            wirepoints.append((route['loom'],[p for e in s.Edges for p in e.discretize(Distance=1)],3,code,h,k))
    existingfile=P.OUT/'complete-source-carriers-plan.json';existing=json.loads(existingfile.read_text())
    inputs=(pf,ff,nf,model,familyfile,seedfile,retentionfile,af,zf,archive,sf,B.H.HEAD,headwires,existingfile,
            Path(__file__),Path(B.__file__),Path(__file__).with_name('fast_carrier_reservations.py'),Path(__file__).with_name('compact_loom_land_port.py'),Path(__file__).with_name('support_entry_port.py'))
    inputs=inputs+tuple(shared_inputs)
    result=dict(status='PARTIAL_REMAINING_SUPPORT_PATH_RESERVATIONS',groups=[],
                beam_reservation_mm=[4,6,4],material_margin_project_mm=.3,
                wire_margin_project_mm=.5,selected=False,native_changed=False,
                W5_complete=False,physical_pass=False,continuous_sweep_verified=False,
                source_sha256={p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in inputs},
                open=['Actual combined arm/grip/tie/sleeve material gate and precise new intersections',
                      'Case bond/load/creep and sleeve dimensions are provisional; no new holes in bought cases',
                      'Native current frame extension/export/assembly/stock and whole body fanouts'])
    destination=P.OUT/('remaining-support-current-paths.json' if '--current-retention' in sys.argv else 'remaining-loom-support-paths.json')
    if resolving:
        destination=P.OUT/('remaining-support-final-paths.json' if entry_mode else 'remaining-support-resolved-paths.json')
        if shared_mode:destination=P.OUT/'remaining-support-shared-paths.json'
        result['groups']=copy.deepcopy(prior['groups'])
        result['source_sha256'].update({p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (priorfile,boundaryfile)})
        result['inherited_found_paths']=sum(bool(p['points_mm']) for g in prior['groups'] for p in g['paths'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    meshes={};half=(2,3,2);surfacehalf=tuple(v+.4 for v in half);cell=10
    result['inherited_open_groups']=retention['errors']
    for group in (g for g in plan['groups'] if g['id'] in {r['id'] for r in complete_groups}):
        oldgroup=next(g for g in prior['groups'] if g['id']==group['id']) if prior else None
        failed_ids={p['land_id'] for p in oldgroup['paths'] if not p['points_mm']} if prior else None
        if shared_mode:
            change=next((r for r in recovery['changed_fixed_groups'] if r['group']==group['id']),None)
            failed_ids={p['land_id'] for p in change['branches']} if change else set()
        if resolving and not failed_ids:continue
        group_tick=time.monotonic()
        stage=group['owner_stage'].split('_')[-1]
        code=group['owner_stage'].split('_')[1] if stage!='Body' else None
        selected=next(r for r in complete_groups if r['id']==group['id'])
        start=selected['root_world_mm'];choice=selected['root_choice']
        goals=[]
        for land in group['lands']:
            if resolving and land['id'] not in failed_ids:continue
            port=next(r for r in selected['ports'] if r['land_id']==land['id'])
            goals.append((land,port['arrival_world_mm'],port['arrival_normal']))
        inherited_prefix=[];branch_source=None
        if entry_mode and len(goals)==1 and not shared_mode:
            # Join the nearest already-received SAME-owner branch, rather
            # than re-searching its unchanged trunk from the case foot.
            goal=goals[0][1];choices=[]
            for path in oldgroup['paths']:
                for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                    delta=[y-x for x,y in zip(a,b)];den=sum(v*v for v in delta)
                    if den<1e-12:continue
                    t=max(0,min(1,sum((g-x)*v for g,x,v in zip(goal,a,delta))/den))
                    q=[x+t*v for x,v in zip(a,delta)]
                    prefix=path['points_mm'][:i if t<1e-8 else i+1]
                    choices.append((math.dist(goal,q),q,prefix,path['land_id']))
            _,start,inherited_prefix,branch_source=min(choices,key=lambda r:r[0])
        # Include all eight meaningful radial port orientations in ONE
        # planning space. No new jacket land position or cable radius.
        low=[min([start[i]]+[r['centre_world_mm'][i] for r in group['lands']])-38 for i in range(3)]
        high=[max([start[i]]+[r['centre_world_mm'][i] for r in group['lands']])+38 for i in range(3)]
        if branch_source:
            low=[min([start[i]]+[r[1][i] for r in goals])-18 for i in range(3)]
            high=[max([start[i]]+[r[1][i] for r in goals])+18 for i in range(3)]
        poses=list(itertools.product(ANGLES, repeat=2)) if stage=='Knee' else [(h,0) for h in ANGLES] if stage=='Hip' else [(0,0)]
        surfaces={};cloud={};seen=set();interiors=[];exact_wires=[];wire_seen=set()
        print('remaining common root',group['id'],'lands',len(goals),'bounds',low,high,flush=True)
        for h,k in poses:
            inv=transforms[code,h,k,0,stage].inverse() if code else A.Placement()
            if resolving:
                for name,s,rad,other,oh,ok in wirecurves:
                    if other==code and code and (oh!=h or (stage=='Knee' and ok!=k)):continue
                    key=(name,oh,ok,tuple(round(v,9) for v in inv.toMatrix().A))
                    if key in wire_seen:continue
                    wire_seen.add(key);q=s.copy();q.Placement=inv*q.Placement;b=q.BoundBox
                    if b.XMax>=low[0]-6 and b.XMin<=high[0]+6 and b.YMax>=low[1]-6 and b.YMin<=high[1]+6 and b.ZMax>=low[2]-6 and b.ZMin<=high[2]+6:
                        exact_wires.append((name,q,rad,b,[(e,e.BoundBox) for e in q.Edges]))
            for name,points,rad,other,oh,ok in wirepoints:
                if other==code and code and (oh!=h or (stage=='Knee' and ok!=k)):continue
                for p in points:
                    v=list(inv.multVec(p))
                    if all(low[i]-6<=v[i]<=high[i]+6 for i in range(3)):
                        bucket=tuple(math.floor(x/cell) for x in v)
                        cloud.setdefault(bucket,[]).append((v,rad,name))
            for name,s in targets.items():
                # Joining a printed parent's material is intentional. All its
                # hardware/bands/cables remain obstacles. Bought cases never
                # disappear from the scene just because they own a root.
                if name==group.get('preserved_owner'):continue
                if shared_mode and name=='SharedSupport_'+group['id']:continue
                if name.startswith('PlannedPort_') and name.removeprefix('PlannedPort_') in {r['id'] for r in group['lands']}:
                    continue  # New seat and arm are the SAME printed owner.
                mem=membership.get(name)
                if not mem:
                    options=[(0,0,0)]
                elif mem[0]!=code:
                    options=itertools.product(ANGLES,repeat=3)
                elif stage=='Knee':
                    # A same-owner Knee case cannot move independently of
                    # its own carrier. Only the child Ankle has relative motion.
                    options=[(h,k,aa) for aa in ANGLES]
                else:
                    options=[(h,kk,aa) for kk,aa in itertools.product(ANGLES,repeat=2)]
                for hh,kk,aa in options:
                    world=transforms[mem[0],hh,kk,aa,mem[1]] if mem else A.Placement()
                    tr=inv*world;key=(name,tuple(round(v,10) for v in tr.toMatrix().A))
                    if key in seen:continue
                    seen.add(key);q=s.copy();q.Placement=tr*q.Placement;b=q.BoundBox
                    bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
                    if any(bounds[i+3]<low[i]-4 or bounds[i]>high[i]+4 for i in range(3)):continue
                    interiors.append((name,q,b))
                    if name not in meshes:
                        vv,tt=s.tessellate(.3);meshes[name]=(np.asarray([list(p) for p in vv]),np.asarray(tt,dtype=int))
                    vv,tt=meshes[name];matrix=np.asarray(tr.toMatrix().A).reshape(4,4)
                    triangles=(vv@matrix[:3,:3].T+matrix[:3,3])[tt]
                    lows=np.maximum(low,triangles.min(axis=1)-surfacehalf)
                    highs=np.minimum(high,triangles.max(axis=1)+surfacehalf)
                    chosen=np.all(lows<=highs,axis=1)
                    for triangle,a,b in zip(triangles[chosen],lows[chosen],highs[chosen]):
                        for bucket in itertools.product(*(range(math.floor(x/cell),math.floor(y/cell)+1) for x,y in zip(a,b))):
                            surfaces.setdefault(bucket,[]).append((triangle,name))
        cloud={key:WireBucket(v) for key,v in cloud.items()}
        surfaces={key:TriangleBucket(v) for key,v in surfaces.items()}
        print('remaining space prepared',group['id'],round(time.monotonic()-group_tick,2),flush=True)
        cache={};blockers={};subset_proofs=[];exact_wire_fallbacks=[]
        parent=targets.get(group.get('preserved_owner'))
        existing_points=[]
        if group['id'].endswith('HipExtension') and not resolving:
            oldroot=next(r for r in existing['roots'] if r['leg']==group['id'].removesuffix('HipExtension'))
            existing_points=[p for path in oldroot['paths'] for p in path['points_mm']]
        def clear(point):
            key=tuple(point)
            if key in cache:return cache[key]
            bucket=tuple(math.floor(x/cell) for x in point)
            wire_hit=None
            for delta in itertools.product((-1,0,1),repeat=3):
                rows=cloud.get(tuple(x+y for x,y in zip(bucket,delta)))
                name=rows.hit(point,half,.5) if rows else None
                if name is not None:wire_hit=name;break
            if wire_hit is not None:
                if not resolving:cache[key]=False;blockers[key]='wire reservation/'+wire_hit;return False
                # The sampled cloud includes0.5mm discretization inflation.
                # Refine a rejection with exact curves, keeping the actual
                # radius PLUS0.5mm design margin for every arm, including its
                # own loom. Never turn a sampled rejection into assumed free.
                x,y,z=point;q=P.box([x-2,y-3,z-2,x+2,y+3,z+2]);bb=q.BoundBox
                minimum=1e9
                for name,w,rad,b,edges in exact_wires:
                    gap=rad+.5
                    if b.XMin>bb.XMax+gap or b.XMax<bb.XMin-gap or b.YMin>bb.YMax+gap or b.YMax<bb.YMin-gap or b.ZMin>bb.ZMax+gap or b.ZMax<bb.ZMin-gap:continue
                    # Same exact clearance, but reject far individual edges
                    # before OCC extrema. A whole multi-loop wire has a very
                    # loose box and can spend minutes on irrelevant curves.
                    for e,eb in edges:
                        if eb.XMin>bb.XMax+gap or eb.XMax<bb.XMin-gap or eb.YMin>bb.YMax+gap or eb.YMax<bb.YMin-gap or eb.ZMin>bb.ZMax+gap or eb.ZMax<bb.ZMin-gap:continue
                        d=q.distToShape(e)[0];minimum=min(minimum,d-rad)
                        if d<gap-1e-6:cache[key]=False;blockers[key]='exact wire clearance/'+name;return False
                exact_wire_fallbacks.append(dict(point=point,minimum_jacket_gap_mm=minimum,sampled_blocker=wire_hit))
            rows=surfaces.get(bucket);name=rows.hit(point,surfacehalf) if rows else None
            if name is not None:
                # Reuse only entirely existing parent material, never waive
                # added arms. This lets an extension depart along a received
                # cap/branch rather than trapping its start in the inflated
                # adhesive reservation. New bands/ports/sleeves still block.
                if parent is not None and not resolving and not name.startswith(('Planned','SpliceReserve')):
                    x,y,z=point;q=P.box([x-2,y-3,z-2,x+2,y+3,z+2])
                    bb=parent.BoundBox
                    if bb.isInside(A.Vector(x-2,y-3,z-2)) and bb.isInside(A.Vector(x+2,y+3,z+2)):
                        outside=q.cut(parent)
                        if (outside.isNull() or outside.isValid()) and outside.Volume<1e-6:
                            # Check every local triangle from NEW interfaces,
                            # because the first returned blocker may be old.
                            newitems=[(tri,n) for tri,n in zip(rows.tri,rows.names) if n.startswith(('Planned','SpliceReserve'))]
                            if not newitems or TriangleBucket(newitems).hit(point,surfacehalf) is None:
                                cache[key]=True;subset_proofs.append(dict(point=point,outside_mm3=outside.Volume,conservative_old_blocker=name));return True
                cache[key]=False;blockers[key]='mesh reservation/'+name;return False
            cache[key]=True;return True
        paths=copy.deepcopy([p for p in oldgroup['paths'] if p['points_mm'] and (not shared_mode or p['land_id'] not in failed_ids)]) if resolving else []
        prefix=inherited_prefix
        if resolving and group['id'].endswith('HipExtension'):
            proof=next(r for r in boundary['existing_exits'] if r['group']==group['id'])
            assert proof['valid'] and proof['outside_mm3']<1e-6
            assert start==proof['start']
            prefix=[start];start=proof['end']
            subset_proofs.append(proof)
        for land,goal,normal in goals:
            if group['id'].endswith('HipExtension'):
                # Nominal4x6x4seed is ENTIRELY unchanged received cap material.
                # Keep all mesh margins for added material. This narrowly
                # resolves the intended tangent bond at the immutable seed,
                # rather than moving a root or ignoring collisions of arms.
                proof=next(r for r in seedproof['rows'] if r['group']==group['id'])
                assert proof['seed_outside_received_cap_mm3']<1e-6
                cache[tuple(start)]=True
            # Face reservations alone cannot see an entire solid's interior.
            for endpoint in (start,goal):
                p=A.Vector(*endpoint)
                for name,s,b in interiors:
                    if b.isInside(p) and s.isInside(p,1e-6,False):
                        cache[tuple(endpoint)]=False;blockers[tuple(endpoint)]='actual interior/'+name;break
            path=search(start,goal,low,high,clear,existing_points)
            if prefix and path['points_mm']:path['points_mm']=prefix+path['points_mm']
            paths.append(dict(land_id=land['id'],post_arrival_normal=normal,
                              complete_port_retention_rest_preflight=True,
                              start_blocker=blockers.get(tuple(start)),goal_blocker=blockers.get(tuple(goal)),**path))
            print('remaining support path',land['id'],len(path['points_mm']),path['expansions'],flush=True)
        record=dict(id=group['id'],owner_stage=group['owner_stage'],
                                      root_choice=choice,root_world_mm=selected['root_world_mm'],paths=paths,
                                      existing_parent_subset_proofs=subset_proofs,
                                      exact_wire_fallbacks=exact_wire_fallbacks,
                                      inherited_same_owner_branch=branch_source,
                                      sampled_owner_poses=len(poses),relative_material_placements=len(interiors),
                                      group_seconds=round(time.monotonic()-group_tick,3))
        if resolving:result['groups']=[record if g['id']==record['id'] else g for g in result['groups']]
        else:result['groups'].append(record)
        save()
    result['status']='COMPLETE_INDEPENDENT_GROUP_SUPPORT_RESERVATIONS_ACTUAL_NATIVE_OPEN' if all(r['points_mm'] for g in result['groups'] for r in g['paths']) else 'REMAINING_SUPPORT_RESERVATIONS_INCOMPLETE_DIAGNOSE_CAUSE'
    if shared_mode:
        result['status']='SHARED_SUPPORT_RESERVATIONS_ACTUAL_NATIVE_OPEN' if all(r['points_mm'] for g in result['groups'] for r in g['paths']) else 'SHARED_SUPPORT_RESERVATIONS_INCOMPLETE_DIAGNOSE_CAUSE'
        result['joint_actual_material_gate_required']=True
    save();print(json.dumps(dict(status=result['status'],worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
