"""Turn the complete E2 source pair before MTA, not after a straight grip.

N01 constructive geometry only. Preserve the named pads, bare tails, PCB
and existing bolt/stand. Full9 curved backing and full selected T18I/head.
"""
import copy,gzip,hashlib,json,math,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_source_restraint_plan import box,joined
from feline_source_saddles import segment
from plan_feline_n01_shared import pipe
from receive_feline_global_case_candidates import placement
from receive_feline_u1_common_restraints import minimum
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json


def construct(fixed,ends):
    tick=time.monotonic();source=OUT/'n01-U1-frontband-common-plan.json'
    old=json.loads(source.read_text());specs=copy.deepcopy(old['specs'])
    R=12.4;L=R*math.pi/2;cap=1.075;actors={};metadata={};updates={}
    pair=('XP02.module','XP03.module');z=[specs[w+'/extra/end']['parts'][0]['start'][2] for w in pair]
    midz=sum(z)/2;h=abs(z[0]-z[1])/2+.925
    def point(s,zz):a=s/R;return [30.37+R*math.sin(a),-4.35+R*(1-math.cos(a)),zz]
    arc=lambda a,b,zz:dict(kind='arc',start=point(a,zz),mid=point((a+b)/2,zz),end=point(b,zz),radius_mm=R)
    for w in pair:
        eid=w+'/extra/end';spec=specs[eid];start=spec['parts'][0]['start'];zz=start[2]
        parts=([dict(kind='line',start=start,end=point(0,zz))] if start[0]<30.37-1e-6 else [])+[arc(0,L,zz)]
        spec['parts']=parts;n='U1Five:'+w+':jacket';actors[n]=pipe(parts,.925)
        metadata[n]=dict(kind='wire',wire=w)
        end=copy.deepcopy(next(e for e in ends if e['id']==eid))
        end.update(routing_exit_mm=point(L,zz),routing_exit_axis=[0,1,0],
            jacket_grip9_mm=[point(L-9,zz),point(L,zz)],grip_length_mm=9,
            full_grip_arclength_mm=[L-9,L],grip_is_curved_not_straight_chord=True,
            source_prefix_length_mm=sum(segment(r).Length for r in parts),
            restraint_owner='U1Relief:RearRoot',prefix_geometry_owner=n,
            routing_boundary_status='PROSPECTIVE_EARLY_U1_PAIR_FULL123_OPEN',
            full_middle_route_accepted=False)
        updates[eid]=end
        bare=fixed['U1Five:'+w+':bare'];assert bare.isValid()
    def sweep(a,b,y0,y1,z0,z1):
        edge=segment(arc(a,b,midz));p=edge.valueAt(edge.FirstParameter)
        t=edge.tangentAt(edge.FirstParameter);u=A.Vector(-t.y,t.x,0);v=A.Vector(0,0,1)
        corners=[p+u*y+v*z for y,z in ((y0,z0),(y1,z0),(y1,z1),(y0,z1),(y0,z0))]
        return Part.Wire([edge]).makePipeShell([Part.Wire(Part.makePolygon(corners).Edges)],True,False)
    pad=sweep(L-9,L,cap,cap+2,-h,h);bandat=L-9+2.5
    band=sweep(bandat-1.25,bandat+1.25,-cap-1.2,cap+3.2,-h-1.2,h+1.2).cut(
        sweep(bandat-1.35,bandat+1.35,-cap,cap+2,-h,h))
    a=bandat/R;t=np.array([math.cos(a),math.sin(a),0]);u=np.array([-t[1],t[0],0])
    head=box([-2.5,cap+1-2.65,-h-1.2-4.3],[2.5,cap+1+2.65,-h-1.2])
    head.Placement=placement(np.column_stack((t,u,[0,0,1])),point(bandat,midz))*head.Placement
    root=joined([pad,box([28.37,3.2,-30],[30.37,11.05,-28]),
        box([28.37,9.05,-30],[40.5,11.05,-28]),box([38.5,7.3,-30],[40.5,11.05,-28])])
    actors.update({'U1Relief:RearRoot':root,'U1Relief:E2pair:band':band,'U1Relief:E2pair:head':head})
    for n in actors:
        if n not in metadata:metadata[n]=dict(kind='PETG' if n.endswith('RearRoot') else 'T18I')
        assert actors[n].isValid() and len(actors[n].Solids)==1,n
    nylon=band.fuse(head);assert nylon.isValid() and len(nylon.Solids)==1
    assert abs(head.Volume-5*5.3*4.3)<1e-5
    stand=fixed['U1Relief:Stand1'];overlap=root.common(stand).Volume
    assert overlap>1e-5 and len(root.fuse(stand).Solids)==1
    retired=['U1Relief:RearRoot',*[f'U1Relief:E2pair:{k}' for k in ('pad','band','head')],
        *['U1Five:'+w+':jacket' for w in pair]]
    plan=dict(status='PROSPECTIVE_EARLY_U1_PAIR',specs={w+'/extra/end':specs[w+'/extra/end'] for w in pair},
        updates=updates,retired=retired,full_grip_arc_mm=[L-9,L],R_mm=R,
        bare_pads_bolt_axes_and_PCB_unchanged=True,stand1_overlap_mm3=overlap,
        inherited_own_PCB_clearance_mm=.2,foreign_clearance_mm=1.25,
        source_sha256={source.relative_to(ROOT).as_posix():sha(source),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        selected_T18I_count_unchanged=True,external_U1_pinout_NOT_inferred=True,
        roots_and_whole123_assembly_OPEN=True,N01_complete=False,physical_pass=False,
        construction_seconds=round(time.monotonic()-tick,3))
    return actors,metadata,plan


def receive(world,fixed,meta,pins,docs,ends):
    tick=time.monotonic();actors,md,plan=construct(fixed,ends)
    dest=OUT/'n01-U1-early-pair.json';assert not dest.exists(),'Receive existing result first'
    plan.update(source_sha256={**pins,**plan['source_sha256']},geometry=[])
    bundle=dest.with_suffix('.breps.zip')
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in actors.items():
            raw=s.exportBrepToString().encode();entry=str(len(plan['geometry']))+'.brep';z.writestr(entry,raw)
            plan['geometry'].append(dict(md[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    plan.update(bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle))
    scene={**{n:s for n,s in fixed.items() if n not in plan['retired']},**actors}
    fm={**meta,**md};checks={};q=SolidQueries()
    own={n for n in fixed if n.startswith(('Ref_Material_U1_','Ref_Material_PWM1608'))}
    groups={'rear':{'U1Relief:RearRoot','U1Relief:Stand1','StructureReserve:U1CarrierArm1','StructureReserve:U1CarrierRoot1'}}
    policy=dict(intended_insulation_mates={n:['U1Five:'+w+':jacket' for w in ('XP02.module','XP03.module')]
        for n in ('U1Relief:RearRoot','U1Relief:E2pair:band')},
        named_grip_air_gaps={'U1Relief:E2pair:head':['U1Five:'+w+':jacket' for w in ('XP02.module','XP03.module')]})
    def save(status):
        pf=dest.with_suffix('.pairs.json.gz');pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        plan.update(status=status,checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],
            pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,plan)
    save('RUNNING_CHANGED_U1_PAIR')
    for n,s in actors.items():
        checks[n+'|outer']=outer_margin(s,docs['outer'])
        for b,t in scene.items():
            if b==n or b in actors and b>=n:continue
            limit,mate=minimum(n,b,fm,policy,groups,own)
            if {n,b}=={'U1Relief:RearRoot','U1Relief:E2pair:band'}:limit,mate=0.,'same full curved pad and band'
            if {n,b}=={'U1Relief:RearRoot','U1Relief:E2pair:head'}:limit,mate=.2,'same clamp head separate from root'
            if limit is None or bbox_lower_bound(s.BoundBox,t.BoundBox)>limit+1e-6:continue
            a=s;other=t
            if b==world.bus['name']:a=s.copy();a.Placement=world.bus['inverse']*a.Placement;other=world.bus['original']
            if other.Solids:
                gap=q.distance(a,other);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit,intended_mate=mate)
                if limit==0:row['common_mm3']=a.copy().common(other.copy()).Volume;row['ok'] &= row['common_mm3']<1e-5
            else:row=profile_gap(a,other,fm.get(b,{}).get('nominal_profile_radius_mm'),limit)
            checks[n+'|'+b]=row
        save('U1_EARLY_PAIR_STATIC_HOLD' if any(not r['ok'] for r in checks.values()) else 'RUNNING_CHANGED_U1_PAIR')
    if plan['failures']:print(plan['status'],plan['failures'],plan['worker_seconds'],flush=True);return actors,md,plan
    from receive_feline_jpwm_whole_pose import receive_sampled_motion
    motion=receive_sampled_motion(world,actors,'n01-U1-early-pair-motion',plan['source_sha256'])
    plan['motion_receipt']='n01-U1-early-pair-motion.json'
    save('U1_EARLY_PAIR_STATIC36_RECEIVED_FULL123_OPEN' if not any(not r['ok'] for r in motion['checks'].values()) else 'U1_EARLY_PAIR_MOTION_HOLD')
    print(plan['status'],plan['checks'],plan['worker_seconds'],flush=True)
    return actors,md,plan


def receive_own_head_policy_delta(world,actors,plan):
    """Reuse actual distances; named OWN insulated fit is not foreign1.25.

    No geometry is changed. The inherited U1 minimum() already supports
    explicit own-grip air gaps .2; only this same clamp's two jackets qualify.
    """
    from receive_feline_jpwm_whole_pose import receive_sampled_motion
    tick=time.monotonic();dest=OUT/'n01-U1-early-pair.json'
    saved=json.loads(dest.read_text());assert saved==plan
    bundle=ROOT/plan['bundle'];assert sha(bundle)==plan['bundle_sha256']
    with zipfile.ZipFile(bundle) as z:
        for row in plan['geometry']:
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            assert actors[row['name']].exportBrepToString().encode()==raw
    rows=json.loads(gzip.decompress((ROOT/plan['pair_rows']).read_bytes()))
    key='U1Relief:E2pair:head|U1Five:XP03.module:jacket'
    assert plan['failures']==[key] and abs(rows[key]['gap_mm']-1.2)<1e-6
    assert rows[key]['minimum_mm']==1.25 and plan['inherited_own_PCB_clearance_mm']==.2
    plan['prior_wrong_foreign_policy']={key:copy.deepcopy(rows[key])}
    rows[key].update(ok=True,minimum_mm=.2,
        intended_mate='named same-clamp head beside OWN insulated jacket; full band1.2 retained')
    plan['unchanged_geometric_pairs_reused']=len(rows)
    motion=receive_sampled_motion(world,actors,'n01-U1-early-pair-motion',plan['source_sha256'])
    plan.update(motion_receipt='n01-U1-early-pair-motion.json',failures=[],
        policy_delta_seconds=round(time.monotonic()-tick,3),
        status='U1_EARLY_PAIR_STATIC36_RECEIVED_FULL123_OPEN' if not any(not r['ok'] for r in motion['checks'].values()) else 'U1_EARLY_PAIR_MOTION_HOLD')
    pf=ROOT/plan['pair_rows'];pf.write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0))
    plan['pair_rows_sha256']=sha(pf);save_json(dest,plan)
    print(plan['status'],plan['policy_delta_seconds'],flush=True)
    return plan
