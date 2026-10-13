"""One shared material gate for all fixed feeds, roots and factory poses.

Exact BRep distances/Commons; bbox only broad phase. Reject before native.
Intended connector/insulation bearing interfaces are explicitly limited.
"""
import json,time,re,hashlib,subprocess
from pathlib import Path
import FreeCAD as A
import Part
import plan_fixed_head_feed_interface as I
from exact_pair_receipts import PairReceipts
from fixed_head_land_profile import flat_land,flat_bend_prefix
H,S,C,Q=I.H,I.S,I.C,I.Q

def nonlocal_edge_pairs(edges,radius,minimum_curve_radius=Q.R):
    """Exact distant portions, excluding the connected tangent neighbourhood.

    Line/circle parameters are uniform in arc length. For a short intervening
    edge, trim the adjoining 4r neighbourhood from each side and test BOTH
    remaining/full pairs. Merely skipping i+2 would miss a genuine folded
    cable; testing untrimmed i+2 labels its own joined insulation a collision.
    The omitted connected interval has total curvature <=8r/R<pi/2, so it
    cannot fold back on itself. This is not an exemption for distant branches.
    """
    import math
    local=4*radius
    assert 2*local/minimum_curve_radius<math.pi/2
    assert all(isinstance(e.Curve,Part.Line) or e.Curve.Radius>=minimum_curve_radius-1e-6 for e in edges)
    def trimmed(e,start=0,end=0):
        assert isinstance(e.Curve,(Part.Line,Part.Circle))
        if start+end>=e.Length-1e-8:return None
        span=e.LastParameter-e.FirstParameter
        return e.Curve.toShape(e.FirstParameter+span*start/e.Length,
                              e.LastParameter-span*end/e.Length)
    for i,e in enumerate(edges):
        for j in range(i+2,len(edges)):
            f=edges[j];middle=sum(a.Length for a in edges[i+1:j])
            if middle>=local:
                yield i,e,j,f
            else:
                cut=local-middle
                a,b=trimmed(e,end=cut),trimmed(f,start=cut)
                if a is not None:yield i,a,j,f
                if b is not None:yield i,e,j,b

def verified_parent(commit):
    """Reuse only completed scopes whose inputs and original checker are pinned."""
    path=H.OUT/'fixed-head-bend-refinement-parent.json'
    parent=json.loads(path.read_text())
    assert parent['status']=='REJECTED_SHARED_FIXED_HEAD_INTERFACE'
    assert parent['stage']=='head yaw-15 whole factory/feed/support material'
    assert parent['poses']==9 and not parent['errors'] and len(parent['contacts'])==1
    hit=parent['contacts'][0]
    assert (hit['a'],hit['b'],hit['pose'])==('FactorySection2','MovingFactoryGrip',[-15,0])
    checker=Path(__file__).relative_to(H.ROOT).as_posix()
    helper=Path(__file__).with_name('fixed_head_land_profile.py').relative_to(H.ROOT).as_posix()
    def historical(name):return subprocess.check_output(['git','show',commit+':'+name],cwd=H.ROOT)
    for name,expected in parent['source_sha256'].items():
        if name in (checker,helper):
            data=historical(name)
            assert hashlib.sha256(data).hexdigest()==expected,('Changed historical source',name)
            if name==helper:
                current=(H.ROOT/name).read_bytes().split(b'# LOCAL_BEND_REFINEMENT')[0]
                assert current.rstrip()==data.rstrip(),'Original flat_land changed'
        else:assert S.SHA(H.ROOT/name)==expected,('Reuse input changed',name)
    assert historical(path.relative_to(H.ROOT).as_posix())==path.read_bytes()
    return dict(parent_commit=commit,parent_sha256=S.SHA(path),
        completed_scopes=['rooted support/static receiving parts','whole fixed interface/head envelope',
                          'whole three fixed source paths'],head_poses=9,
        remaining_scope='Full factory/body/support/self at all3yaws, with local first8mm arc flat refinement')

def run(parent_commit=None):
    reuse=verified_parent(parent_commit) if parent_commit else None
    tick=time.monotonic();p,feeds,roots,meta,fork,reader,allocation,archive=I.prepare()
    targets,old,_=S.scene()
    station,hardware,bonds,_=C.D.allocate(targets)
    targets.pop('Foundation',None)
    targets.update({'station/'+n:s for n,s in {**station,**hardware,**bonds}.items()})
    retired={n for n in old if re.search(r'(?:^|/)(?:XB22|XB23|XS23)(?:/|_|$)',n)}
    assert any('head-supply-checkpoint/' in n for n in retired)
    x,z=p['fixed_receiver_XZ_mm'];y=p['fixed_receiver_Y_mm']
    jr=H.T.box([x-6,y-30,z-5,x+6,y,z+5])
    history=[];previous=H.OUT/'fixed-head-interface-material.json'
    if previous.exists():
        oldreport=json.loads(previous.read_text());history=oldreport.get('previous_failures',[])
        if oldreport['status'].startswith('REJECTED'):
            history.append({k:oldreport[k] for k in ('status','stage','contacts','errors','worker_seconds','source_sha256')})
    report=dict(status='PENDING',previous_failures=history,selected=False,physical_pass=False,native_changed=False,
        W2_complete=False,W3_complete=False,pairs=0,contacts=[],errors=[],poses=0,
        retired_source_paths=sorted(retired),rooted_support=meta,allocation=allocation,
        scope='Three whole fixed feeds, rooted material/bands, unchanged source interfaces and full250factory9sampled head poses; native/assembly/stock still OPEN',
        completed_scope_reuse=reuse,lengths_mm={n:sum(e.Length for e in es) for n,es in feeds.items()},
        factory_self_distance_sampled=False,source_sha256={**reader.hashes,
          archive.relative_to(H.ROOT).as_posix():S.SHA(archive),
          **{Path(f).relative_to(H.ROOT).as_posix():S.SHA(Path(f)) for f in (__file__,I.__file__,C.__file__,C.D.__file__,str(Path(__file__).with_name('fixed_head_land_profile.py')))}})
    cache=PairReceipts(H.OUT/'fixed-head-interface-pairs.json',S.W.near)
    heads={}
    def head_at(yaw,pitch):
        if (yaw,pitch) not in heads:
            h=H.head(reader,yaw,pitch);h['Fork']=H.moved(fork,yaw)
            heads[yaw,pitch]=h
        return heads[yaw,pitch]
    def test(n,s,r,m,t,tr=0,pose=None):
        if not S.W.near(s,t,r+tr+.001):return
        report['pairs']+=1
        try:d,v=cache.check(s,t,r,tr)
        except (AssertionError,ValueError) as exc:report['errors'].append([n,m,str(exc)]);return
        if d<r+tr-1e-4 or v>1e-5:
            dist,witness,_=s.distToShape(t)
            report['contacts'].append(dict(a=n,b=m,pose=pose,gap_mm=d,volume_mm3=v,
                witness_mm=[[list(q) for q in pair] for pair in witness[:1]]))
    def save(stage):
        report.update(stage=stage,worker_seconds=round(time.monotonic()-tick,3),
            exact_pairs_computed=cache.computed,identical_pairs_reused=cache.reused)
        cache.save();H.save('fixed-head-interface-material.json',report)
        print(stage,'pairs',report['pairs'],'contacts',len(report['contacts']),'errors',len(report['errors']),flush=True)
    def blocked(stage):
        save(stage)
        if report['contacts'] or report['errors']:
            report['status']='REJECTED_SHARED_FIXED_HEAD_INTERFACE';save(stage)
            print(json.dumps(report['contacts'][:12]),flush=True);return True
        return False

    # Prepare one geometry set per yaw and receive restraint bearing BEFORE
    # spending minutes on whole-assembly pairs. Reuse those same shapes and
    # nine head snapshots throughout this single gate.
    qualified,qualified_meta=C.F.allocation(60)
    qualified={n:(s,r) for n,(s,r) in qualified.items() if n.startswith('Qualified')}
    report['source_sha256'].update(qualified_meta['source_sha256'])
    if reuse:
        report['poses']=reuse['head_poses']
        report['source_sha256'][(H.OUT/'fixed-head-bend-refinement-parent.json').relative_to(H.ROOT).as_posix()]=reuse['parent_sha256']
    factories={}
    for yaw in (-15,0,15):
        row=next(q for q in p['poses'] if q['yaw']==yaw)
        edges=H.T.wire(row['parts']).Edges
        assert abs(sum(e.Length for e in edges)+p['prefix_mm']-250)<1e-5
        material={i:(flat_land(s),0) if i in (0,1,len(edges)-2,len(edges)-1)
                  else (s,Q.RESERVE) for i,s in enumerate(edges)}
        moving={n:(H.moved(s,yaw),0) for n,s in roots.items() if n.startswith('Moving')}
        shapes={f'FactorySection{i}':v for i,v in material.items()}
        shapes.update({n:(H.moved(s,yaw),r) for n,(s,r) in qualified.items()});shapes.update(moving)
        factories[yaw]=(edges,material,moving,shapes)
        firstflat=material[0][0];lastflat=material[len(edges)-1][0];bearings={}
        for name,flat,host,planes in [('MovingBed',firstflat,moving['MovingFactoryGrip'][0],[152.6]),
                                      ('MovingBand',firstflat,moving['MovingFactoryBand'][0],[152.6,154.4]),
                                      ('FixedBed',lastflat,roots['FixedJRSeat'],[79.1])]:
            common=flat.common(host)
            assert common.isNull() or common.isValid(),('Invalid land bearing',name)
            volume=0 if common.isNull() else common.Volume
            area=sum(C.D.bearing_area(flat,host,z) for z in planes)
            if not(volume<1e-5 and area>8):
                report['errors'].append([name,'Flat cable must actually bear without intrusion',volume,area])
                report['status']='REJECTED_SHARED_FIXED_HEAD_INTERFACE';save('flat land bearing rejected');return
            bearings[name]=dict(area_mm2=area,volume_mm3=volume)
        report.setdefault('flat_land_bearings',[]).append(dict(yaw=yaw,nominal_profile_mm=[3.5,1.8],bearings=bearings))
    save('all flat land bearings received')

    # First receive the real one-solid load path/bands against unrelated
    # static materials and retained wires. No expensive repeated motion on
    # an already disconnected or statically interfering construction.
    fixed={n:s for n,s in roots.items() if not n.startswith('Moving')}
    for n,s in (() if reuse else fixed.items()):
        test(n,s,0,'FixedJR',jr)
        for m,t in targets.items():
            if t.Solids:test(n,s,0,m,t)
        for m,(t,tr) in old.items():
            if m not in retired:test(n,s,0,m,t,tr)
    for i,n in enumerate(() if reuse else fixed):
        for m in list(fixed)[i+1:]:test(n,fixed[n],0,m,fixed[m])
    if blocked('rooted support/static receiving parts'):return

    # Receive the whole current head envelope before the many retained
    # body-wire pairs. Exact members, not a skin bbox or rest-only view.
    for yaw in (() if reuse else (-15,0,15)):
        for pitch in (-10,0,5):
            head=head_at(yaw,pitch)
            # Changed moving restraint first: a known local skin clash must
            # reject before replaying the many fixed feed/body interfaces.
            for n,(s,r) in factories[yaw][3].items():
                for m,t in head.items():
                    if n=='MovingFactoryGrip' and m=='Fork':continue
                    test(n,s,r,'head/'+m,t,pose=[yaw,pitch])
            for n,s in {**fixed,'FixedJR':jr,**{n:Part.Wire(es) for n,es in feeds.items()}}.items():
                for m,t in head.items():
                    if n=='FixedJRSeat' and m=='YawCarrier':continue
                    test(n,s,1.05 if n in feeds else 0,'head/'+m,t,pose=[yaw,pitch])
            report['poses']+=1
    if blocked('whole fixed interface/head envelope'):return

    # Source WAGO housing/case and factory lap are unchanged. Exempt ONLY
    # the assigned outward9mm port land or unchanged lap pairing, not all
    # wires in the same branch. Every newly routed segment remains tested.
    wires={n:Part.Wire(es) for n,es in feeds.items()}
    for n,s in (() if reuse else wires.items()):
        for m,t in targets.items():
            if not t.Solids:continue
            current=s
            if n=='XB23' and m=='W3Ref_G_AUX_case':current=Part.Wire(feeds[n][1:])
            if n=='XS23' and m in ('W3Ref_XS23_FormedInsulation','W3Ref_XS23_JacketOverlap'):
                # Exactly unchanged selected pad/insulation prefix, not an
                # exemption for a new wire crossing unrelated insulation.
                current=Part.Wire(feeds[n][8:])
            test(n,current,1.05,m,t)
        for m,(t,tr) in old.items():
            if m in retired:continue
            if n=='XB22' and m in ('wire/head-supply-checkpoint/F_HP_out','wire/head-supply-checkpoint/XB22_sleeve'):continue
            test(n,s,1.05,m,t,tr)
        for m,t in fixed.items():test(n,s,1.05,m,t)
        for m,t in wires.items():
            if n<m:test(n,s,1.05,m,t,1.05)
        # Only the final9mm straight land intentionally docks at its JR
        # mating face. All upstream bends are unrelated material interfaces.
        test(n+'/beforeJR',Part.Wire(feeds[n][:-1]),1.05,'FixedJR',jr)
        for i,e,j,f in nonlocal_edge_pairs(feeds[n],1.05,I.R):
            test(n+'/self'+str(i),e,1.05,n+'/self'+str(j),f,1.05)
    if blocked('whole three fixed source paths'):return

    for yaw in (-15,0,15):
        edges,material,moving,prepared=factories[yaw];shapes=dict(prepared)
        shapes['FixedJR']=(jr,0);shapes.update({n:(s,0) for n,s in fixed.items()})
        for n,(s,r) in shapes.items():
            if n in fixed or n=='FixedJR':continue
            for m,t in targets.items():
                if t.Solids:test(n,s,r,m,t,pose=[yaw,0])
            for m,(t,tr) in old.items():
                if m not in retired:test(n,s,r,m,t,tr,pose=[yaw,0])
            for m,t in wires.items():test(n,s,r,m,t,1.05,pose=[yaw,0])
            for m,t in fixed.items():
                # Conservative diagonal reservation over-reaches a flat
                # receiving land. Explicit flat3.5x1.8 material must qualify
                # these bearing pairs below, not be silently called clear.
                if n=='FactorySection'+str(len(edges)-1) and m in ('FixedJRSeat','FactoryLandBand'):continue
                test(n,s,r,m,t,pose=[yaw,0])
        # Receive the actual moving restraint interfaces, not just their
        # position relative to distant body objects. Support/head passages
        # must not contain insulation; exact bearing may touch, not overlap.
        for i,(s,r) in material.items():
            for m,(t,tr) in moving.items():
                if i==2:
                    # The circular reservation is intentionally conservative.
                    # Qualify the actual nominal flat first8mm, and retain the
                    # full diagonal reservation on the rest of this same arc.
                    actual,rest=flat_bend_prefix(edges[i])
                    test('FactoryFlatBendFirst8',actual,0,m,t,tr,pose=[yaw,0])
                    test('FactoryBendRemainder',rest,Q.RESERVE,m,t,tr,pose=[yaw,0])
                else:test('FactorySection'+str(i),s,r,m,t,tr,pose=[yaw,0])
            if i>=2:
                for m,(t,tr) in qualified.items():test('FactorySection'+str(i),s,r,m,H.moved(t,yaw),tr,pose=[yaw,0])
        for n,(s,r) in qualified.items():
            for m,(t,tr) in moving.items():test(n,H.moved(s,yaw),r,m,t,tr,pose=[yaw,0])
        test('MovingFactoryGrip',moving['MovingFactoryGrip'][0],0,'MovingFactoryBand',moving['MovingFactoryBand'][0],pose=[yaw,0])
        for i in range(len(edges)-1):
            s,r=material[i];test('FactorySection'+str(i),s,r,'FixedJR',jr,pose=[yaw,0])
        # Actual nominal flat final land against its two intended grips.
        tail=edges[-1];a=tail.valueAt(tail.FirstParameter);b=tail.valueAt(tail.LastParameter)
        flat=H.T.box([a.x-1.75,min(a.y,b.y),79.1,a.x+1.75,max(a.y,b.y),80.9])
        for m in ('FixedJRSeat','FactoryLandBand'):test('FactoryFlatLast9',flat,0,m,fixed[m],pose=[yaw,0])
        # Non-adjacent free-path edges: adjacent tangent joins are the same
        # physical cable. Exclude only the connected join neighbourhood.
        for i,e,j,f in nonlocal_edge_pairs(edges,Q.RESERVE):
            test('FactorySelf'+str(i),e,Q.RESERVE,'FactorySelf'+str(j),f,Q.RESERVE,pose=[yaw,0])
        if blocked('head yaw'+str(yaw)+' whole factory/feed/support material'):return
    report.update(status='SHARED_FIXED_HEAD_INTERFACE_SAMPLED_CLEAR_NATIVE_OPEN',factory_self_distance_sampled=True)
    save('complete sampled shared interface')
    print(json.dumps({k:report[k] for k in ('status','poses','pairs','worker_seconds')}),flush=True)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--parent-commit')
    run(parser.parse_args().parent_commit)
