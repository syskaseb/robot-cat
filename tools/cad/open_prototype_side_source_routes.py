"""One coupled full-bend side-source plan, with proposed matched supports.

Finite tangent choices, actual material checks and current retained wire peers.
No case-only allocation can trigger a native export or full wiring acceptance.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, itertools, json, math, time
import FreeCAD as A
import Part
import open_prototype_source_group as B
from open_prototype_source_retention import OUT, BASE, ROOT, sha
from open_prototype_source_shared_layout import prism
from open_prototype_tail_clearance import box, near, wire, profiles, trim
from open_prototype_tangent_routes import terminated
from open_prototype_path_preflight import samples
from open_prototype_s1_shared_routes import source_specs

DEST = OUT/'side-source-full-bend-plan.json'


def load_scene(p):
    paths = [OUT/'SourceRetentionCurrent.FCStd', BASE/'mounting-checkpoint/RetentionMountsAssembly.FCStd',
             BASE/'OpenPrototypePlan.FCStd', OUT/'LocalStationsAssembly.FCStd', OUT/'TailLocalCurrent.FCStd']
    docs = [A.openDocument(str(f)) for f in paths]
    native, mount, ctx, local, tail = docs
    fixed = []
    for ob in native.Objects:
        if ob.TypeId != 'PartDesign::Body' or ob.Name == 'S1Bracket':
            continue
        s = ob.Shape
        if ob.Name in ('LeftDistributionCarrier','RightDistributionCarrier'):
            s = s.common(prism([-150,-120,0], [200,120,61]))
        fixed.append((ob.Name,s,'retained native material'))
    for n in ('LowerCarrier','Spacer1','Spacer2','Spacer3','Spacer4'):
        fixed.append((n,mount.getObject(n).Shape,'retained native material'))
    retired = {'UpperCarrier','CommonSourcePlatform','LeftDistributionCarrier','RightDistributionCarrier'}
    for r in B.read(OUT/'obstacle-map-current.json')['objects']:
        n = r['name']
        if n in retired or n.startswith('S1_') or r['kind'] in ('candidate_station','service_budget'):
            continue
        assert r['kind'] != 'replaceable_support',n
        if r['kind'] == 'delivery_reservation':
            v=r['bounds_mm'];s=prism(v[:3],v[3:]);basis='nominal module reservation, not measured material'
        else:
            ob=tail.CurrentTailSupport if n=='CurrentTailSupport' else ctx.getObject(n) or local.getObject(n) or mount.getObject(n)
            assert ob is not None,n
            s=ob.Shape;basis='retained native material'
        if not any(k==n for k,_,_ in fixed):fixed.append((n,s,basis))
    fixed += [(r['role'], box(r['centre_mm'],r['size_mm']), 'nominal module reservation, not measured material')
              for r in p['stations']+p['mta']+p['holders']]
    spec=p['s1_module'];pivot=A.Vector(*spec['pivot_mm']);shift=A.Vector(*spec['translation_mm'])
    rings={}
    for ob in ctx.Objects:
        n=ob.Name
        if not n.startswith('S1_') or any(k in n.lower() for k in ('service','driver')) or not hasattr(ob,'Shape') or ob.Shape.isNull():continue
        s=ob.Shape.copy()
        if n=='S1_control_CP2':
            s=Part.makeCylinder(6,12,A.Vector(126.2,74,85),A.Vector(0,1,0)).fuse(
                Part.makeCylinder(14,22,A.Vector(126.2,86,85),A.Vector(0,1,0)))
        s.rotate(pivot,A.Vector(0,0,1),spec['whole_rotation_z_deg']);s.translate(shift)
        if n.startswith('S1_ring_'):
            rings[int(n[-1])]=s
        else:fixed.append((n,s,'retained source material'))
    assert len(rings)==4
    assert all(s.isValid() and s.Solids for _,s,_ in fixed)
    assert ctx.TorsoEnvelope.Shape.isValid()
    return docs, fixed, rings, ctx.TorsoEnvelope.Shape, paths


def support_proposals():
    # Shared roots are specified now, not silently carved around later wires.
    s1=prism([120.2,22,77.72],[132.2,46,83]).fuse(prism([120.2,22,80],[170.7,46,83]))
    panel=prism([167.7,21.5,83],[170.7,49.5,119])
    panel=panel.cut(Part.makeCylinder(6.25,3,A.Vector(167.7,35.5,105),A.Vector(1,0,0)))
    panel=panel.cut(Part.makeCylinder(1.5,3,A.Vector(167.7,26.5,105),A.Vector(1,0,0)))
    s1=s1.fuse(panel).removeSplitter()
    data=prism([-58,-29,77.72],[-52,-17,123.5]).fuse(prism([-89.5,-35,120.5],[-30.5,-5,123.5])).removeSplitter()
    mta=[]
    for x,y in ((-25,21),(0,21),(68.8,-21),(94.8,-21)):
        lo,hi=(13.7,38.5) if y>0 else (-40.5,-26.4)
        py=20 if y>0 else -29.5
        s=prism([x-3,py-3,77.72],[x+3,py+3,109]).fuse(prism([x-12,lo,106],[x+12,hi,109])).removeSplitter()
        mta.append(('MtaSupport'+str(len(mta)+1),s,'proposed support'))
    rear=prism([50.3,.5,129.5],[87.3,29,132.5])
    for y in (18,26):rear=rear.fuse(prism([61.8,y-3,77.72],[65.8,y+3,132.5]))
    return [('SideSourceBracket',s1,'proposed support'),('DataShelf',data,'proposed support'),
            ('RearPowerShelf',rear.removeSplitter(),'proposed support')]+mta


def run():
    assert not DEST.exists(),'Do not repeat an unchanged run'
    tick=time.monotonic();allocation=B.read(OUT/'source-group-allocation.json');p=copy.deepcopy(allocation['family'])
    assert allocation['status']=='WHOLE_GROUP_CASE_ENTRY_SERVICE_CAPACITY_ONLY'
    inputs=[OUT/'source-group-allocation.json',OUT/'obstacle-map-current.json',Path(__file__),
            Path(__file__).with_name('open_prototype_tangent_routes.py')]
    report=dict(status='PENDING',selected=False,stage_completed=False,physical_pass=False,
                errors=[],candidates={},support_conflicts=[],joint_conflicts=[],pairs=0,
                invalidated_endpoints=['D_RL','D_RR','G_TAIL','XB33','XP03.source','XL09','XA06'],
                full_wiring_native_retention_stock_and_service_open=True)
    docs=[]
    def progress(phase):print(json.dumps(dict(phase=phase,seconds=round(time.monotonic()-tick,2),pairs=report['pairs'])),flush=True)
    def hit(s,scene,r=0,skip=()):
        for n,t,basis in scene:
            if n in skip or not near(s,t,r):continue
            report['pairs']+=1
            if r:
                d=s.distToShape(t)[0]
                if d<r-1e-6:return dict(name=n,distance_mm=d,required_mm=r,basis=basis)
            else:
                v=s.common(t).Volume
                if v>1e-6:return dict(name=n,volume_mm3=v,basis=basis)
        return None
    try:
        progress('load one shared scene')
        docs,fixed,original_rings,torso,paths=load_scene(p);inputs+=paths
        pins={f.relative_to(ROOT).as_posix():sha(f) for f in inputs};report['source_sha256']=pins
        support=support_proposals()
        # Screen all owners and preserved factory exits before any detailed CAD.
        retained=profiles(p)
        for n,s,_ in support:
            assert s.isValid() and len(s.Solids)==1,n
            clash=hit(s,fixed,skip=('UpperCarrier',))
            if clash:report['support_conflicts'].append(dict(support=n,**clash))
            for m,(parts,r,_,_) in retained.items():
                c=wire(parts)
                if near(c,s,r):
                    d=c.distToShape(s)[0];report['pairs']+=1
                    if d<r-1e-6:report['support_conflicts'].append(dict(support=n,name=m,distance_mm=d,required_mm=r))
            if s.cut(torso).Volume>1e-6:report['support_conflicts'].append(dict(support=n,name='torso boundary'))
        progress('common support envelope checked')
        # Unaccepted supports are not hidden: report them; only unchanged native
        # scene constrains route discovery until owner geometry is corrected.
        peers=[(n,wire(v[0]),v[1]) for n,v in retained.items()]
        candidates={}
        for ident,terminal,target in source_specs(p):
            ring=next(r for r in p['s1_module']['rings'] if r['terminal']==terminal)
            eye=ring['eye_mm'];end=p['ports'][target]['point_mm'];arrival=B.mul(p['ports'][target]['departure'],-1)
            found=[];counts=dict(analytic=0,point_reject=0,radius_gate=0,exact_reject=0,outside=0)
            angles=(180,135,-135,90,-90,45,-45,0) if terminal in (2,3) else (180,135,90,45,0,-45,-90,-135)
            waypoints=[None]
            if ident=='W064':waypoints += [([40,y,z],B.WEST) for y,z in ((-20,124),(-40,120),(40,125))]
            elif ident=='W065':waypoints += [([100,y,z],B.WEST) for y,z in ((50,140),(-10,140),(-30,130))]
            else:waypoints += [([x,y,140],B.WEST) for x,y in ((65,-40),(65,-60),(40,-45))]
            for angle,ratio,waypoint in itertools.product(angles,(1,.5,2,.25,4),waypoints):
                a=math.radians(angle);d=[0,ring['direction'][1]*math.cos(a),ring['direction'][1]*math.sin(a)]
                start=B.add(eye,B.mul(d,22.123))
                try:parts=terminated(start,d,end,arrival,ratio,waypoint)
                except (AssertionError,ValueError,ZeroDivisionError):continue
                counts['analytic']+=1;pts=[v for _,v in samples(parts,5)]
                # Positive points inside canonical cases/native solids are safe
                # rejections. Their absence is NOT a tube-clearance verdict.
                bad=False
                for point in pts[1:-1]:
                    v=A.Vector(*point)
                    for n,s,_ in fixed:
                        if n==target.split('.')[0]:continue
                        if s.BoundBox.isInside(v) and s.isInside(v,1e-7,True):bad=True;break
                    if bad:break
                if bad:counts['point_reject']+=1;continue
                if any(not torso.isInside(A.Vector(*q),1e-7,True) for q in pts):counts['outside']+=1;continue
                rs=original_rings[terminal].copy();rs.rotate(A.Vector(*eye),A.Vector(1,0,0),angle)
                # Only its own bolted eye/seat is an intentional mating pair.
                clash=hit(rs,fixed,skip=('S1_screw_'+str(terminal),'S1_seat_budget_'+str(terminal)))
                if clash:counts['exact_reject']+=1;continue
                c=wire(parts);counts['radius_gate']+=1
                # Exact full-radius against the shell and every current material.
                if c.distToShape(torso.Shells[0])[0]<2.1-1e-6:counts['outside']+=1;continue
                clash=None
                for n,s,basis in fixed:
                    curve=trim(parts,last=2.10001) if n==target.split('.')[0] else c
                    clash=hit(curve,[(n,s,basis)],2.1)
                    if clash:break
                if not clash:clash=hit(trim(parts,first=2.10001),[('own ring',rs,'actual ring material')],2.1)
                if not clash:
                    for n,s,r in peers:
                        clash=hit(c,[(n,s,'retained conductor radius')],2.1+r)
                        if clash:break
                if clash:counts['exact_reject']+=1;continue
                found.append(dict(wire=ident,terminal=terminal,target=target,eye_mm=eye,barrel_mm=start,
                    barrel_direction=d,ring_rotation_x_deg=angle,segments=parts,OD_mm=4.2,min_radius_mm=25.2,
                    centreline_mm=B.check_path(parts),nominal_cut_length_mm=math.ceil(B.check_path(parts)+28.452),
                    termination_allowance_mm=28.452,nominal_fit_only=True))
                if len(found)>=6:break
            report['candidates'][ident]=dict(**counts,full_radius_clear_candidates=len(found))
            candidates[ident]=found;progress(ident+' finite route family checked')
        for rows in itertools.product(*(candidates[n] for n in ('W064','W065','W067','W068'))):
            local=[];clash=None
            for row in rows:
                rs=original_rings[row['terminal']].copy();rs.rotate(A.Vector(*row['eye_mm']),A.Vector(1,0,0),row['ring_rotation_x_deg'])
                c=wire(row['segments'])
                clash=hit(rs,[(n,s,'other ring') for n,s,_ in local if n.startswith('ring')])
                if not clash:clash=hit(c,local,2.1)
                if not clash:
                    for n,s,basis in local:
                        if n.startswith('wire'):
                            clash=hit(c,[(n,s,basis)],4.2)
                            if not clash:clash=hit(s,[('ring'+str(row['terminal']),rs,'other ring')],2.1)
                            if clash:break
                if clash:break
                local += [('ring'+str(row['terminal']),rs,'ring'),('wire'+row['wire'],c,'wire')]
            if clash:continue
            p['s1_routes']=list(rows)
            for row in rows:
                r=next(r for r in p['s1_module']['rings'] if r['terminal']==row['terminal'])
                r.update(barrel_mm=row['barrel_mm'],direction=row['barrel_direction'],ring_rotation_x_deg=row['ring_rotation_x_deg'])
            report['family']=p
            report['status']='FULL_FOUR_SOURCE_RADIUS_FAMILY_SUPPORTS_OPEN' if report['support_conflicts'] else 'FULL_FOUR_SOURCE_RADIUS_FAMILY_AND_SUPPORT_ENVELOPES_CLEAR'
            break
        else:report['status']='NO_COMPLETE_SOURCE_FAMILY_IN_PLANNED_CORRIDORS'
        report['support_plan']=[dict(name=n,bounds_mm=[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]) for n,s,_ in support]
    except Exception as exc:
        report['errors'].append(str(exc));report['status']='ERROR_NOT_ACCEPTANCE';raise
    finally:
        for d in docs:A.closeDocument(d.Name)
        if 'source_sha256' in report:assert all(sha(ROOT/n)==h for n,h in report['source_sha256'].items()),'Changed input'
        report.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        DEST.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:report.get(k) for k in ('status','candidates','support_conflicts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
