"""Whole three-land Hip carrier planning, rooted on actual exposed case.

Mesh/point-cloud reservations only. No native, strength, contact or selection
claim. This uses complete source routes and current head/station geometry,
not earlier disconnected joint sections or obsolete station shoes.
"""
import heapq,itertools,json,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
import check_low_hip_loom_layout as P
import plan_current_head_wiring as H
from plan_continuous_joint_family import parts_for_loom
from plan_current_rigid_factory_joins import moved_parts
from cad_reservation_math import triangle_box


def run():
    tick=time.monotonic();fp=P.OUT/'leg-source-near-member-plan.json'
    family=json.loads(fp.read_text());receipt=P.OUT/'leg-source-near-member-plan-material.json'
    gate=json.loads(receipt.read_text());assert not gate['contacts'] and not gate['errors'] and gate['cases']==108
    assert gate['source_sha256'][fp.relative_to(P.ROOT).as_posix()]==P.SHA(fp)
    targets,old,archive=P.scene();reader=H.P.SavedShapes()
    # Retire only replaced pitch curves, not retained body/yaw wiring.
    import re
    for n in list(old):
        if re.search(r'(?:^|/)(?:XB22|XB23|XS23)(?:/|_|$)',n):old.pop(n)
    sf=P.OUT/'StationFramesCurrent.FCStd';targets.pop('Foundation')
    for n in ('FLStationFrame','FRStationFrame','RLStationFrame','RRStationFrame','FoundationStationSupports'):
        targets[n]=reader.shape(sf,n)
    for n in reader.doc(sf):
        if n.startswith('Ref_'):targets[n[4:]]=reader.shape(sf,n)
    H.HEAD=H.OUT/'HeadNeckFixedJoined.FCStd'
    for n,s in H.head(reader,0,0).items():
        for y,p in {(y if n not in H.FIXED else 0,p if n in H.PITCH else 0) for y,p in itertools.product((-15,0,15),(-10,0,5))}:
            targets[f'head/{y}/{p}/{n}']=H.moved(s,y,p)
    for n in reader.doc(H.HEAD):
        if not n.startswith('Interface_') or n=='Interface_FactoryFreeUncut250':continue
        s=reader.shape(H.HEAD,n);s.translate(H.SHIFT)
        for y in ((-15,0,15) if n.startswith(('Interface_Moving','Interface_Qualified')) else (0,)):
            q=H.moved(s,y)
            if n in ('Interface_XB22','Interface_XB23','Interface_XS23'):old[f'headwire/{y}/{n}']=(q,1.05)
            else:targets[f'headref/{y}/{n}']=q
    ff=H.OUT/'fixed-underneck-rounds-plan.json'
    from plan_fixed_underneck_rounds import RESERVE
    for q in json.loads(ff.read_text())['poses']:
        if q['yaw'] in (-15,0,15):old['factory/'+str(q['yaw'])]=(P.wire(q['parts']),RESERVE)
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    membership={r['name']:r['stage'].split('_')[1:] for r in members if r['stage'].startswith('Motion_')}
    transforms={}
    for code in ('FL','FR','RL','RR'):
        for hh,kk,aa in itertools.product((-15,0,15),repeat=3):
            T=A.Placement()
            for stage,angle in zip(('Hip','Knee','Ankle'),(hh,kk,aa)):
                ax=next(r for r in axes if r['code']==code and r['stage']==stage)
                pv=A.Vector(*ax['pivot_mm']);rot=A.Rotation(A.Vector(*ax['axis']),angle)
                T=T*A.Placement(pv-rot.multVec(pv),rot);transforms[code,hh,kk,aa,stage]=T
    def cloud(s):return [p for e in s.Edges for p in e.discretize(Distance=1)]
    oldpoints=[(n,cloud(s),r) for n,(s,r) in old.items()]
    sourcepoints=[]
    for route in family['routes']:
        for h,k in itertools.product((-15,0,15),repeat=2):
            parts=parts_for_loom(family,route['loom'],h,k,axes)+moved_parts(route['source_parts'],route['source'],h,k,axes)
            sourcepoints.append((route['loom'],route['source']['cad_code'],h,k,cloud(P.wire(parts))))
    half=(2.,3.,2.);margin=.5;cell=10.;mesh_margin=.3
    surface_half=tuple(h+.1+mesh_margin for h in half);meshes={};roots=[]
    def save(status):
        report=dict(status=status,roots=roots,beam_reservation_mm=[4,6,4],wire_margin_mm=margin,
            leg_material_samples=27,wire_inverse_Hip_samples=31,source_coupled_samples=9,
            selected=False,native_changed=False,W5_complete=False,physical_pass=False,
            limitations=['Conservative surface/point-cloud planning only; rejection is not actual BRep contact',
                '4x6x4 beam is a minimum search reservation, not stiffness approval; full ribs/grips/hardware need changed gate',
                'Known exposed case patch needs provisional compatible bond/fit/load/peel/creep trial; no new case holes',
                'Full Knee/source grips and fixed receiving roots/body fans remain OPEN'],
            worker_seconds=round(time.monotonic()-tick,3),source_sha256={p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (fp,receipt,sf,H.HEAD,ff,archive,af,zf,Path(__file__),Path(__file__).with_name('cad_reservation_math.py'))})
        (P.OUT/'complete-source-carriers-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        return report
    for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
        rows=[r for r in family['hips'] if r['physical_leg']==leg];code=rows[0]['cad_code'];side=1 if leg.endswith('Left') else -1
        case=next(m for m in members if m['stage']=='Motion_'+code+'_Hip' and m['label'].startswith('ZK_'))
        casing=targets['P0_'+case['name']];bb=casing.BoundBox;cx=(bb.XMin+bb.XMax)/2
        # Same exposed housing patch qualified geometrically in the old cap:
        # no shaft, casing seam, vent or PCB used as a new mounting datum.
        bond=P.box([cx-4,min(side*8.75,side*15),30,cx+4,max(side*8.75,side*15),32.2])
        for m in members:
            if m['stage']=='Motion_'+code+'_Hip' and m['label'].startswith(('ZK_','SG-ZIJI_','XG-ZIJI_')):bond=bond.cut(targets['P0_'+m['name']])
        assert bond.isValid() and len(bond.Solids)==1 and bond.common(casing).Volume<1e-6
        for x in (cx-3.9,cx+3.9):
            for y in (8.85,14.9):
                hit=casing.common(Part.makeLine(A.Vector(x,side*y,29),A.Vector(x,side*y,32.2)))
                assert hit.Vertexes and 30<max(v.Point.z for v in hit.Vertexes)<32.1
        start=[cx,12,34.2]
        sign=-1 if leg.startswith('Front') else 1
        goals=[[r['moving_anchor_rest_world_mm'][0]+sign*6,abs(r['moving_anchor_rest_world_mm'][1]),r['moving_anchor_rest_world_mm'][2]-4.5] for r in rows]
        low=[min([start[i]]+[p[i] for p in goals])-18 for i in range(3)]
        high=[max([start[i]]+[p[i] for p in goals])+18 for i in range(3)]
        low[1]=8;high[1]=210;low[2]=min(low[2],-30);high[2]=max(high[2],52)
        grid={};surfaces={};materials=[];seen=set()
        def coord(p):return (p.x,side*p.y,p.z)
        def within(p):return all(low[i]-10<=p[i]<=high[i]+10 for i in range(3))
        def putpoint(p,r,n):
            v=coord(p)
            if within(v):grid.setdefault(tuple(math.floor(x/cell) for x in v),[]).append((v,r,n))
        for h in range(-15,16):
            ax=next(r for r in axes if r['code']==code and r['stage']=='Hip');pv=A.Vector(*ax['pivot_mm']);rot=A.Rotation(A.Vector(*ax['axis']),h)
            inv=A.Placement(pv-rot.multVec(pv),rot).inverse()
            for n,pts,rad in oldpoints:
                for p in pts:
                    if low[0]-10<p.x<high[0]+10:putpoint(inv.multVec(p),rad,n)
            if h not in (-15,0,15):continue
            for n,other,oh,ok,pts in sourcepoints:
                if other==code and oh!=h:continue
                for p in pts:putpoint(inv.multVec(p),3,n)
        print('carrier',leg,'complete wire buckets',len(grid),flush=True)
        for h,other_h,k,a in itertools.product((-15,0,15),repeat=4):
            inv=transforms[code,h,k,a,'Hip'].inverse()
            for n,s in targets.items():
                if s.BoundBox.XMax<low[0]-5 or s.BoundBox.XMin>high[0]+5:continue
                mem=membership.get(n.removeprefix('P0_')) if n.startswith('P0_') else None
                # Own children change relative to Hip. Other legs are tested
                # at all27poses pairwise, not assumed permanently at rest.
                tr=inv*(transforms[mem[0],h if mem[0]==code else other_h,k,a,mem[1]] if mem else A.Placement())
                key=(n,tuple(tr.toMatrix().A))
                if key in seen:continue
                seen.add(key);q=s.copy();q.Placement=tr*q.Placement;b=q.BoundBox
                qlo=[b.XMin,min(side*b.YMin,side*b.YMax),b.ZMin];qhi=[b.XMax,max(side*b.YMin,side*b.YMax),b.ZMax]
                if any(qhi[i]<low[i]-4 or qlo[i]>high[i]+4 for i in range(3)):continue
                materials.append((n,q,b))
                if n not in meshes:meshes[n]=s.tessellate(mesh_margin)
                verts,faces=meshes[n];vv=[coord(tr.multVec(p)) for p in verts]
                for inds in faces:
                    tri=tuple(vv[i] for i in inds)
                    lo=[max(low[i],min(p[i] for p in tri)-surface_half[i]) for i in range(3)]
                    hi=[min(high[i],max(p[i] for p in tri)+surface_half[i]) for i in range(3)]
                    if any(x>y for x,y in zip(lo,hi)):continue
                    for bucket in itertools.product(*(range(math.floor(x/cell),math.floor(y/cell)+1) for x,y in zip(lo,hi))):surfaces.setdefault(bucket,[]).append((tri,n))
        print('carrier',leg,'material buckets',len(surfaces),'placements',len(materials),flush=True)
        cache={};blockers={}
        def clear(p):
            key=tuple(p)
            if key in cache:return cache[key]
            bucket=tuple(math.floor(x/cell) for x in p)
            for d in itertools.product((-1,0,1),repeat=3):
                for v,rad,n in grid.get(tuple(x+y for x,y in zip(bucket,d)),()):
                    if sum(max(0,abs(x-y)-hh)**2 for x,y,hh in zip(p,v,half))<(rad+margin+.5)**2:
                        cache[key]=False;blockers[key]='wire reservation/'+n;return False
            for tri,n in surfaces.get(bucket,()):
                if triangle_box(tri,p,surface_half):cache[key]=False;blockers[key]='mesh reservation/'+n;return False
            cache[key]=True;return True
        paths=[];endpoints=[]
        for row,goal in zip(rows,goals):
            sc,gc=clear(start),clear(goal)
            for endpoint in (start,goal):
                p=A.Vector(endpoint[0],side*endpoint[1],endpoint[2])
                for n,s,b in materials:
                    if b.isInside(p) and s.isInside(p,1e-6,False):
                        blockers[tuple(endpoint)]='actual interior/'+n
                        if endpoint==start:sc=False
                        else:gc=False
                        break
            coords=[sorted(set([low[i]+4*j for j in range(math.ceil((high[i]-low[i])/4)+1)]+[start[i],goal[i]])) for i in range(3)]
            first=tuple(v.index(x) for v,x in zip(coords,start));last=tuple(v.index(x) for v,x in zip(coords,goal))
            def point(k):return [v[j] for v,j in zip(coords,k)]
            def heuristic(k):return sum(abs(x-y) for x,y in zip(point(k),goal))
            queue=[(heuristic(first),0,first)];best={first:0};parent={};found=None;count=0;st=time.monotonic()
            while queue and sc and gc and count<12000 and time.monotonic()-st<90:
                _,cost,k=heapq.heappop(queue)
                if cost!=best[k]:continue
                count+=1
                if k==last:found=k;break
                for i in range(3):
                    for step in (-1,1):
                        kk=list(k);kk[i]+=step
                        if not 0<=kk[i]<len(coords[i]):continue
                        kk=tuple(kk);aa,bb=point(k),point(kk)
                        if not clear(bb) or not clear([(x+y)/2 for x,y in zip(aa,bb)]):continue
                        new=cost+math.dist(aa,bb)
                        if new>=best.get(kk,1e30):continue
                        best[kk]=new;parent[kk]=k;heapq.heappush(queue,(new+heuristic(kk),new,kk))
                if count%500==0:print('carrier search',row['loom'],count,round(time.monotonic()-st,2),flush=True)
            path=[]
            if found:
                key=found;path=[point(key)]
                while key!=first:key=parent[key];path.append(point(key))
                path.reverse();simple=[path[0]]
                for aa,bb,cc in zip(path,path[1:],path[2:]):
                    if next(i for i in range(3) if aa[i]!=bb[i])!=next(i for i in range(3) if bb[i]!=cc[i]):simple.append(bb)
                simple.append(path[-1]);path=[[p[0],side*p[1],p[2]] for p in simple]
            paths.append(dict(loom=row['loom'],points_mm=path,expansions=count,search_seconds=round(time.monotonic()-st,3)))
            endpoints.append(dict(loom=row['loom'],start_clear=sc,goal_clear=gc,start_blocker=blockers.get(tuple(start)),goal_blocker=blockers.get(tuple(goal))))
            print('carrier path',row['loom'],len(path),'knots',count,'states',flush=True)
        roots.append(dict(leg=leg,cad_code=code,case=case['name'],bond_bounds_world_mm=[cx-4,min(side*8.75,side*15),30,cx+4,max(side*8.75,side*15),32.2],paths=paths,endpoints=endpoints))
        save('PARTIAL_COMPLETE_SOURCE_CARRIER_RESERVATIONS')
    report=save('COMPLETE_SOURCE_CARRIERS_RESERVED_ACTUAL_NATIVE_OPEN' if all(p['points_mm'] for r in roots for p in r['paths']) else 'COMPLETE_SOURCE_CARRIERS_RESERVATION_INCOMPLETE')
    print(json.dumps({k:report[k] for k in ('status','worker_seconds')}),flush=True)


if __name__=='__main__':run()
