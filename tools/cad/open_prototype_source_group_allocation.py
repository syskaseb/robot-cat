"""Allocate coupled source/data/ground cases against retained structural owners.

This is a spatial solver for one open-prototype assembly, not a detailed CAD
generator or a full-harness acceptance. Existing source/tail/data paths are
explicitly invalidated rather than silently frozen across relocated ports.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, itertools, json, time
import FreeCAD as A
import Part
from open_prototype_source_receipt import verified_family
from open_prototype_source_retention import OUT, BASE, ROOT, sha
from open_prototype_source_shared_layout import prism
from open_prototype_tail_clearance import box, near

DEST = OUT / 'source-group-allocation.json'
CHANGED = {'D_RL','D_RR','G_TAIL'}


def station(c, rotation, role):
    size = [30,19,9] if rotation in (0,180) else [19,30,9]
    row = dict(role=role, centre_mm=list(c),size_mm=size,rotation=str(rotation),model='415')
    case=box(c,size); x,y,z=c
    ports={}
    for i in range(1,6):
        s=(i-3)*4.75
        if rotation==0: p,d=[x+s,y-9.5,z],[0,-1,0]
        elif rotation==180:p,d=[x-s,y+9.5,z],[0,1,0]
        elif rotation==90:p,d=[x+9.5,y+s,z],[1,0,0]
        else:p,d=[x-9.5,y-s,z],[-1,0,0]
        ports[f'{role}.{i}']=dict(point_mm=p,departure=d,basis='nominal project cavity, delivery fit OPEN')
    # Project tool/lever budget is separate from delivered material. Keep an
    # actual 9mm straight-entry capsule at EVERY port, including future NC.
    entry=[Part.makeCylinder(2.1,9,A.Vector(*v['point_mm']),A.Vector(*v['departure'])) for v in ports.values()]
    top=box([x,y,z+12.5],[size[0],size[1],16])
    budgets=Part.makeCompound([case,top]+entry)
    return row,ports,case,budgets


def run():
    tick=time.monotonic(); p=copy.deepcopy(verified_family())
    inputs=[OUT/'SourceRetentionCurrent.FCStd',BASE/'mounting-checkpoint/RetentionMountsAssembly.FCStd',
            BASE/'OpenPrototypePlan.FCStd',OUT/'LocalStationsAssembly.FCStd',OUT/'TailLocalCurrent.FCStd',
            OUT/'obstacle-map-current.json',OUT/'source-low-gap-plan.json',Path(__file__)]
    pins={f.relative_to(ROOT).as_posix():sha(f) for f in inputs}
    docs=[]; stats=dict(candidates=0,material_pairs=0,boundary_pairs=0)
    result=dict(selected=False,stage_completed=False,physical_pass=False,native_files_changed=0,
        source_sha256=pins,stats=stats,
        scope='Common whole-source placement, frame retained; full routes/native mounts still OPEN',
        invalidated=['S1 bracket and four full source routes and source grips',
            'D_RL/D_RR all ports, routes and mounts','G_TAIL full receiving/output approaches and mounts'],
        preserved=['R47 bank','all four structural spacers','LowerCarrier and UpperCarrier PCB supports',
                   'both complete MTA exits; altered receiving/source families must be regenerated'],
        reservations_are_not_measured_material=True,errors=[])
    def progress(s): print(json.dumps(dict(phase=s,seconds=round(time.monotonic()-tick,2),**stats)),flush=True)
    def clash(s,scene):
        for n,t in scene:
            if not near(s,t,0):continue
            stats['material_pairs']+=1
            if not t.isValid():raise AssertionError('Invalid retained input '+n)
            if s.common(t).Volume>1e-6:return n
        return None
    try:
        docs=[A.openDocument(str(f)) for f in inputs[:5]]
        native,mount,ctx,local,tail=docs;torso=ctx.TorsoEnvelope.Shape
        assert torso.isValid() and len(torso.Solids)==1
        fixed=[]
        for ob in native.Objects:
            if ob.TypeId!='PartDesign::Body' or ob.Name=='S1Bracket':continue
            s=ob.Shape
            if ob.Name in ('LeftDistributionCarrier','RightDistributionCarrier'):
                s=s.common(prism([-150,-120,0],[200,120,61]))
            fixed.append((ob.Name,s))
        for n in ('LowerCarrier','Spacer1','Spacer2','Spacer3','Spacer4'):fixed.append((n,mount.getObject(n).Shape))
        retired={'UpperCarrier','CommonSourcePlatform','LeftDistributionCarrier','RightDistributionCarrier'}
        for r in json.loads((OUT/'obstacle-map-current.json').read_text())['objects']:
            n=r['name']
            if n in retired or n.startswith('S1_') or r['kind'] in ('candidate_station','service_budget'):continue
            assert r['kind']!='replaceable_support',n
            if r['kind']=='delivery_reservation':v=r['bounds_mm'];s=prism(v[:3],v[3:])
            else:
                ob=tail.CurrentTailSupport if n=='CurrentTailSupport' else ctx.getObject(n) or local.getObject(n) or mount.getObject(n)
                assert ob is not None,n
                s=ob.Shape
            if not any(k==n for k,_ in fixed):fixed.append((n,s))
        unchanged=[(r['role'],box(r['centre_mm'],r['size_mm'])) for r in p['stations']+p['mta']+p['holders'] if r['role'] not in CHANGED]
        scene=fixed+unchanged
        # Two horizontal terminal-plane hypotheses failed. Change the whole
        # mounting architecture to a SIDE-operated source, allocating its
        # four real rings and straight insulation approaches together.
        pivot=A.Vector(126.2,55.5,85); original=[]
        for ob in ctx.Objects:
            if not ob.Name.startswith('S1_') or any(k in ob.Name.lower() for k in ('service','driver')) or not hasattr(ob,'Shape') or ob.Shape.isNull():continue
            s=ob.Shape.copy()
            if ob.Name=='S1_control_CP2':
                s=Part.makeCylinder(6,12,A.Vector(126.2,74,85),A.Vector(0,1,0)).fuse(Part.makeCylinder(14,22,A.Vector(126.2,86,85),A.Vector(0,1,0)))
            original.append((ob.Name,s))
        ring_specs=[]
        for terminal in (2,5,3,6):
            left=terminal in (2,3);eye=[120.2 if left else 132.2,33,85 if terminal in (2,5) else 73]
            direction=[-1,0,0] if left else [1,0,0]
            barrel=[eye[i]+22.123*direction[i] for i in range(3)]
            ring_specs.append(dict(terminal=terminal,eye_mm=eye,barrel_mm=barrel,direction=direction,ring_rotation_z_deg=0))
            original.append((f'S1_{terminal}_insulation_entry',Part.makeCylinder(2.1,9,A.Vector(*barrel),A.Vector(*direction))))
        s1=None;rejected={};poses=0
        for x,y,z,yaw in itertools.product((126.2,106.2,146.2),(55.5,35.5,-35.5),(105,117),(0,90,-90,180)):
            poses+=1;shift=A.Vector(x,y,z)-pivot;items=[];reason=None
            for n,saved in original:
                s=saved.copy();s.rotate(pivot,A.Vector(0,0,1),yaw);s.translate(shift)
                reason=clash(s,scene)
                if reason:break
                if n!='S1_control_CP2':
                    bb=s.BoundBox
                    if not all(torso.isInside(A.Vector(a,b,c),1e-7,True) for a in (bb.XMin,bb.XMax) for b in (bb.YMin,bb.YMax) for c in (bb.ZMin,bb.ZMax)):
                        reason='torso boundary';break
                items.append((n,s))
            if reason:rejected[reason]=rejected.get(reason,0)+1;continue
            if any(s.cut(torso).Volume>1e-6 for n,s in items if n!='S1_control_CP2'):
                rejected['exact torso boundary']=rejected.get('exact torso boundary',0)+1;continue
            s1=items;break
        result['source_pose_allocation']=dict(poses=poses,rejections=rejected,
            architecture='SIDE_OPERATED_COMPLETE_SOURCE_WITH_FOUR_ORIGINAL_RINGS_AND_ENTRY_LANDS',
            source_terminal_service_on_bench=True,operator_external_only=True)
        if s1 is None:result['status']='NO_SIDE_SOURCE_CAPACITY';return
        spec=dict(whole_rotation_deg=0,whole_rotation_z_deg=yaw,pivot_mm=list(pivot),translation_mm=list(shift),rings=[],
            external_control=True,bearing_plane='Transformed XZ, side operator; not upper-deck datum')
        for r in ring_specs:
            r=copy.deepcopy(r)
            for k in ('eye_mm','barrel_mm'):
                v=A.Rotation(A.Vector(0,0,1),yaw).multVec(A.Vector(*r[k])-pivot)+pivot+shift;r[k]=list(v)
            r['direction']=list(A.Rotation(A.Vector(0,0,1),yaw).multVec(A.Vector(*r['direction'])))
            spec['rings'].append(r)
        p['s1_module']=spec;p['s1_routes']=[] # No stale transformed route presented as current.
        result['source_pose_allocation'].update(centre_mm=[x,y,z],yaw_deg=yaw)
        scene+=s1;progress('Side source group allocated; common ground and paired data')
        # Search a limited set of actual mounting levels. The lower vacant
        # RR_P land is first for ground, not a forced datum for BUS_DATA.
        candidates=[]
        positions=[(86,-75,67.99)]+list(itertools.product((140,120,100,80,-80,-60,-40,0,40),(40,60,-60,-40,20,-20,0),(96,112,128)))
        for c in positions:
            for rot in (0,180,90,-90):
                stats['candidates']+=1
                row,ports,case,budget=station(c,rot,'allocation')
                if clash(budget,scene):continue
                bb=budget.BoundBox
                if not all(torso.isInside(A.Vector(x,y,z),1e-7,True)
                           for x in (bb.XMin,bb.XMax) for y in (bb.YMin,bb.YMax) for z in (bb.ZMin,bb.ZMax)):continue
                stats['boundary_pairs']+=1
                if budget.cut(torso).Volume>1e-6:continue
                candidates.append((row,ports,case,budget))
            if len(candidates)>=32:break # A feasible common choice, not exhaustive packing proof.
            if stats['candidates']%100==0:progress('capacity allocation')
        result['feasible_station_candidates']=len(candidates)
        # Prefer same-level adjacent data connectors, with outward entry
        # directions and independent top access. No blocked vertical stack.
        pairs=[]
        for i,a in enumerate(candidates):
            for b in candidates[i+1:]:
                ac,bc=a[0]['centre_mm'],b[0]['centre_mm']
                if ac[2]!=bc[2] or a[0]['rotation']!=b[0]['rotation']:continue
                gap=sum(abs(x-y) for x,y in zip(ac,bc))
                if not 30<=gap<=65:continue
                if near(a[3],b[3],0) and a[3].common(b[3]).Volume>1e-6:continue
                # Proximity to frame roots rather than maximal roof height.
                score=gap+abs(ac[0]-80)+abs(bc[0]-80)+abs(ac[1])+abs(bc[1])+2*abs(ac[2]-96)
                pairs.append((score,a,b))
        pairs.sort(key=lambda v:v[0]);chosen=None
        for _,a,b in pairs:
            for g in candidates:
                if any(near(g[3],d[3],0) and g[3].common(d[3]).Volume>1e-6 for d in (a,b)):continue
                chosen=(a,b,g);break
            if chosen:break
        if not chosen:result['status']='NO_COMMON_DATA_GROUND_CAPACITY';return
        result['chosen_stations']=[];result['candidate_examples']=[r[0] for r in candidates[:12]]
        for role,item in zip(('D_RL','D_RR','G_TAIL'),chosen):
            row,ports,case,budget=station(item[0]['centre_mm'],int(item[0]['rotation']),role)
            current=next(r for r in p['stations'] if r['role']==role);current.update(row)
            p['ports'].update(ports);result['chosen_stations'].append(row)
        for e in p['body_ends']:
            if e['current_role'].split('.')[0] in CHANGED:e['datum']=copy.deepcopy(p['ports'][e['current_role']])
        result.update(status='WHOLE_GROUP_CASE_ENTRY_SERVICE_CAPACITY_ONLY',family=p,
            open=['Regenerate four source routes and all relocated ground/data approaches',
                  'Allocate actual support roots with all retained profiles','14source seats and cable ties',
                  'Full wiring/stock/assembly/selected native package'])
    except Exception as exc:
        result['status']='ERROR_NOT_ACCEPTANCE';result['errors'].append(str(exc));raise
    finally:
        for d in docs:A.closeDocument(d.Name)
        assert all(sha(ROOT/n)==h for n,h in pins.items()),'Changed source during read-only allocation'
        result.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result.get(k) for k in ('status','chosen_stations','feasible_station_candidates','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
