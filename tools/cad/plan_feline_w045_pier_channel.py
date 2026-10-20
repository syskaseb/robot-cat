"""Keep R47/RL_P and its full grip; relieve the printed corner, not the bolt.

One quarter after the received prefix. This is an N01 escape, not the whole
custom wire. Native manufacturing features and strength remain later gates.
"""
import copy,hashlib,json,math,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_n01_shared import pipe
from feline_source_restraint_plan import box
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from compose_feline_output_boundaries import cap_at
from feline_atomic_save import save_json


def receive(world,fixed,metadata,pins,docs,ends):
    tick=time.monotonic();e=next(e for e in ends if e['id']=='W045/custom/end')
    cap=cap_at(fixed['Station:RL_P:wire:RL_P.1'],e['routing_exit_mm'],e['routing_exit_axis'],2.1)
    p=np.array(e['routing_exit_mm']);R=25.2
    assert np.allclose(e['routing_exit_axis'],[0,-1,0])
    point=lambda a:(p+R*np.array([-(1-math.cos(a)),-math.sin(a),0])).tolist()
    parts=[dict(kind='arc',start=point(0),mid=point(math.pi/4),end=point(math.pi/2),radius_mm=R)]
    wire=pipe(parts,2.1);clearance=pipe(parts,3.35)
    owner='CurrentFoundation:BankPier:4';old=fixed[owner];new=old.cut(clearance)
    assert new.isValid() and len(new.Solids)==1
    assert new.cut(old).Volume<1e-5
    b=old.BoundBox;kept={}
    for role,z0,z1 in (('foot',b.ZMin,b.ZMin+1),('roof',b.ZMax-1,b.ZMax)):
        clip=box([b.XMin-1,b.YMin-1,z0],[b.XMax+1,b.YMax+1,z1])
        before=old.common(clip);after=new.common(clip)
        assert before.Volume>1e-5 and before.cut(after).Volume<1e-5 and after.cut(before).Volume<1e-5
        kept[role]=dict(original_material_unchanged=True,volume_mm3=before.Volume,z_mm=[z0,z1])
    q=SolidQueries();checks={};actors={owner:new,'W045:PierEscape':wire}
    scene={**fixed,**actors}
    for n,s in actors.items():
        checks[n+'|outer']=outer_margin(s,docs['outer'])
        if n==owner:continue # subset cannot add a foreign contact
        for name,target in scene.items():
            if name==n:continue
            same=name=='Station:RL_P:wire:RL_P.1'
            limit=0. if same else .2 if metadata.get(name,{}).get('kind') in ('wire','proposal_wire','actual_wire') else 1.25
            if bbox_lower_bound(s.BoundBox,target.BoundBox)>limit+1e-6:continue
            a=s;t=target
            if name==world.bus['name']:a=s.copy();a.Placement=world.bus['inverse']*a.Placement;t=world.bus['original']
            if not t.Solids:row=profile_gap(a,t,metadata.get(name,{}).get('nominal_profile_radius_mm'),limit)
            else:
                gap=q.distance(a,t);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit)
                if same:row['common_mm3']=a.common(t).Volume;row['ok'] &= row['common_mm3']<1e-5
            checks[n+'|'+name]=row
    dest=OUT/'n01-W045-printed-pier-channel.json';bundle=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in actors.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind='PETG' if n==owner else 'wire',wire=None if n==owner else 'W045',nominal_profile_radius_mm=None if n==owner else 2.1))
    update=copy.deepcopy(e);update.update(routing_exit_mm=parts[-1]['end'],routing_exit_axis=[-1,0,0],
        source_prefix_length_mm=e.get('source_prefix_length_mm',12.25)+R*math.pi/2,
        prefix_geometry_owner='W045:PierEscape',prefix_geometry_owners=['Station:RL_P:wire:RL_P.1','W045:PierEscape'],
        received_prefix_R_mm=25.2,routing_boundary_status='PROSPECTIVE_W045_POST_GRIP_PIER_ESCAPE',
        full_middle_route_accepted=False)
    result=dict(status='W045_PIER_CHANNEL_STATIC_'+('HOLD' if any(not r['ok'] for r in checks.values()) else 'RECEIVED'),
        checks=checks,failures=[k for k,v in checks.items() if not v['ok']],geometry=geometry,
        bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),parts=parts,updates={e['id']:update},
        preserved_existing_cap=cap,kept_original_pier_regions=kept,original_pier_sha256=hashlib.sha256(old.exportBrepToString().encode()).hexdigest(),
        printed_only_subset_cut_mm3=old.Volume-new.Volume,R47_bought_parts_and_mount_datum_unchanged=True,
        original_RL_P_full9_restraint_unchanged=True,source_sha256=pins,
        full_custom_route_native_strength_and_whole_N01_OPEN=True,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],result['failures'],result['worker_seconds'],flush=True)
    return actors,result


def receive_seat_delta(world,fixed,actors,result,pins):
    """Same channel through the WHOLE connected printed portal, not a bolt.

    All prior actual wire distances are retained; only this connected
    printed seat changes. The unchanged pier foot still joins its seat.
    """
    from receive_feline_jpwm_whole_pose import receive_sampled_motion
    tick=time.monotonic();owner='CurrentFoundation:BankPier:4';seatname='CurrentFoundation:ClampSeat:4'
    key='W045:PierEscape|'+seatname;assert result['failures']==[key]
    old=fixed[seatname];clearance=pipe(result['parts'],3.35);seat=old.cut(clearance)
    assert seat.isValid() and len(seat.Solids)==1 and seat.cut(old).Volume<1e-5
    before=fixed[owner].common(old);after=actors[owner].common(seat)
    assert before.Volume>1e-5 and after.Volume>1e-5 and after.cut(before).Volume<1e-5
    from feline_channelled_foundation import bearing_area
    bearing={}
    for role,name,top in (('pad','Station:Anchor:Rear:TopClampPad4',True),('washer','Station:Anchor:Rear:RailClamp4TopWasher',False)):
        mate=fixed[name];z=mate.BoundBox.ZMax if top else mate.BoundBox.ZMin
        a=bearing_area(old,mate,z);b=bearing_area(seat,mate,z)
        assert abs(a-b)<1e-5 and b>=(60 if top else 10),role
        bearing[role]=dict(before_mm2=a,after_mm2=b,actual_bearing_unchanged=True)
    union=actors[owner].fuse(seat);assert union.isValid() and len(union.Solids)==1
    q=SolidQueries();gap=q.distance(actors['W045:PierEscape'],seat);assert gap>=1.25-1e-6
    result['prior_same_portal_seat_row']={key:copy.deepcopy(result['checks'][key])}
    result['checks'][key].update(ok=True,gap_mm=gap,minimum_mm=1.25)
    actors={**actors,seatname:seat};result['portal_seat_joint']=dict(common_mm3=after.Volume,
        old_joint_mm3=before.Volume,removed_corner_mm3=before.cut(after).Volume,
        actual_bearings=bearing,whole_portal_1Solid=True,unchanged_original_joint=False)
    motion=receive_sampled_motion(world,actors,'n01-W045-portal-channel-motion',pins)
    assert motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
    dest=OUT/'n01-W045-printed-pier-channel.json';bundle=ROOT/result['bundle'];records=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in actors.items():
            raw=s.exportBrepToString().encode();entry=str(len(records))+'.brep';z.writestr(entry,raw)
            records.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind='wire' if n=='W045:PierEscape' else 'PETG',
                wire='W045' if n=='W045:PierEscape' else None,nominal_profile_radius_mm=2.1 if n=='W045:PierEscape' else None))
    for e in result['updates'].values():e.update(prefix_geometry_owner='W045:PierEscape',routing_boundary_status='CURRENT_W045_FULL_GRIP_AND_POST_GRIP_PORTAL_CHANNEL_STATIC36')
    result.update(status='W045_WHOLE_PRINTED_PORTAL_CHANNEL_STATIC36_RECEIVED',failures=[],geometry=records,
        bundle_sha256=sha(bundle),motion_receipt='n01-W045-portal-channel-motion.json',
        seat_subset_removed_mm3=old.Volume-seat.Volume,unchanged_positive_pairs_reused=len(result['checks'])-1,
        delta_worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],result['portal_seat_joint'],result['delta_worker_seconds'],flush=True)
    return actors,result
