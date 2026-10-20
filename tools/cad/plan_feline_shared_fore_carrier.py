"""One open bundle saddle and rooted F_HY/FL carrier, not nine cable bores.

Electrical ends retain their independent WAGO grips. FL is a continuous
kinematic bookkeeping seam; full moving-wire qualification belongs to N02.
"""
import hashlib,json,math,time,zipfile
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_source_restraint_plan import box,joined
from receive_feline_global_case_candidates import placement
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json


def construct(fixed,fhy,tf):
    a=9/12.4;theta=.3
    def sector(r0,r1,z0,z1):
        p=lambda r,t:A.Vector(-87+r*math.sin(t),34+r*math.cos(t),z0)
        edges=[Part.Arc(p(r0,0),p(r0,a/2),p(r0,a)).toShape(),Part.makeLine(p(r0,a),p(r1,a)),
            Part.Arc(p(r1,a),p(r1,a/2),p(r1,0)).toShape(),Part.makeLine(p(r1,0),p(r0,0))]
        return Part.Face(Part.Wire(edges)).extrude(A.Vector(0,0,z1-z0))
    trough=joined([sector(8.7,23.3,62.7,64.7),sector(8.7,10.7,62.7,75.3),sector(21.3,23.3,62.7,75.3)])
    t=np.array([math.cos(theta),-math.sin(theta),0]);u=np.array([math.sin(theta),math.cos(theta),0])
    transform=placement(np.column_stack((t,u,[0,0,1])),[-87+16*math.sin(theta),34+16*math.cos(theta),70])
    band=box([-1.25,-8.65,-8.65],[1.25,8.65,6.65]).cut(box([-1.35,-7.45,-7.45],[1.35,7.45,5.45]))
    # Close INBOARD: the outboard side is reserved for the structural hanger.
    head=box([-2.5,-12.95,-3.65],[2.5,-8.65,1.65])
    band.Placement=transform*band.Placement;head.Placement=transform*head.Placement
    assert abs(head.Volume-5*4.3*5.3)<1e-5
    nylon=band.fuse(head);assert nylon.isValid() and len(nylon.Solids)==1
    riser=box([-112.15,55,40.02],[-110.15,57,85.8])
    factory=box([-116.15,60.65,82.0],[-114.15,62.65,94.225]);factory.Placement=tf*factory.Placement
    factory=joined([factory,box([-117.15,71,85.3],[-110.15,73.8,87.3])])
    q=tf.multVec(A.Vector(-68.80574890451304,64.7,72.625));end=np.array([q.y,q.z]);start=np.array([73.,86.3])
    d=(end-start)/np.linalg.norm(end-start);n=np.array([-d[1],d[0]])
    corners=[A.Vector(-69.80574890451304,*p) for p in (start+n,end+n,end-n,start-n,start+n)]
    custom=Part.Face(Part.Wire(Part.makePolygon(corners).Edges)).extrude(A.Vector(2,0,0))
    hanger=joined([box([-76,52,63.2],[-72,56,64.7]),box([-75,54,63.2],[-73,56,85.8])])
    actors={'BundleCuff:FL':trough,'BundleTie:FL':band,'BundleTie:FLHead':head,
        'FrontShared:rail_riser':riser,'FrontShared:factory_rib':factory,
        'FrontShared:custom_rib':custom,'FrontShared:cuff_hanger':hanger}
    assert all(s.isValid() and len(s.Solids)==1 for s in actors.values())
    bases={'ForeFHAC:common_body_saddle':fixed['ForeFHAC:common_body_saddle'],
        'ForeFHAC:out:factory:saddle':fhy['ForeFHAC:out:factory:saddle'],
        'ForeFHAC:out:custom:saddle':fhy['ForeFHAC:out:custom:saddle'],
        'CurrentFoundation:FoundationFlange:1':fixed['CurrentFoundation:FoundationFlange:1']}
    rail=fixed['CurrentFoundation:FoundationRail:1'];contacts=[s for s in rail.Solids if s.common(riser).Volume>1e-5]
    assert len(contacts)==1;bases['CurrentFoundation:FoundationRail:1#contacted_front_solid']=contacts[0]
    prints={**bases,**{n:s for n,s in actors.items() if n not in ('BundleTie:FL','BundleTie:FLHead')}}
    values=list(prints.values());whole=values[0].multiFuse(values[1:])
    assert whole.isValid() and len(whole.Solids)==1,('Shared fore carrier disconnected',whole.isValid(),len(whole.Solids))
    oriented=whole.copy();oriented.rotate(A.Vector(0,0,0),A.Vector(0,0,1),45)
    b=oriented.BoundBox;envelope=[b.XLength,b.YLength,b.ZLength];assert max(envelope)<250
    return actors,dict(print_members=list(prints),planned_shared_positive_foundation_owner=True,
        shared_existing_members_referenced_NOT_duplicated=True,whole_valid=True,whole_solids=1,
        whole_envelope_45Z_mm=envelope,proposed_print_rotation_Z_deg=45,brim_support_reserve_to256_mm=6,
        wall_floor_mm=2,open_trough_not_nine_rigid_bores=True,
        nine_continuous_seams_NOT_nine_electrical_terminations=True,
        original_independent_electrical_end_reliefs_unchanged=True,
        first_at_least9mm_of_all9_arcs_covered=True,
        source_bundle_guide_capacity_radii_mm=[12.4,16,19.6],
        one_full_T18I_section_mm=[2.5,1.2],head_mm=[5,4.3,5.3],
        closure_inboard_opposite_hanger=True,delivered_bundle_tightening_and_N02_flex_OPEN=True)


def receive(world,fixed,metadata,docs,actors,recipe,pins,fl,fhy,monitor,reservations):
    tick=time.monotonic();q=SolidQueries();retired=[*fl,*fhy,*monitor,'BundleCuff:FL','BundleTie:FL','BundleTie:FLHead']
    scene={**{n:s for n,s in fixed.items() if n not in retired},**fl,**fhy,**monitor,**reservations,**actors}
    printed=set(recipe['print_members'])-{'CurrentFoundation:FoundationRail:1#contacted_front_solid'}
    printed.add('CurrentFoundation:FoundationRail:1')
    checks={}
    for n,s in actors.items():
        checks[n+'|outer']=outer_margin(s,docs['outer'])
        for name,target in scene.items():
            if n==name:continue
            if n not in ('BundleTie:FL','BundleTie:FLHead') and name in printed:continue
            same_bundle=name in fl and n in ('BundleCuff:FL','FrontShared:cuff_hanger','BundleTie:FL','BundleTie:FLHead')
            own_fhy=(n=='FrontShared:factory_rib' and name=='ForeFHAC:out:factory97') or (n=='FrontShared:custom_rib' and name=='ForeFHAC:out:custom26')
            limit=.15 if same_bundle or own_fhy else 1.25
            if {n,name}<={'BundleCuff:FL','BundleTie:FL','BundleTie:FLHead'}:limit=0.
            if n=='FrontShared:custom_rib' and name in ('ForeFHAC:out:custom:band_budget','ForeFHAC:out:custom:head_budget'):limit=.2
            if name=='ForeFHAC:case' and n in ('FrontShared:factory_rib','FrontShared:custom_rib'):limit=0.
            if bbox_lower_bound(s.BoundBox,target.BoundBox)>limit+1e-6:continue
            a=s;t=target
            if name==world.bus['name']:a=s.copy();a.Placement=world.bus['inverse']*a.Placement;t=world.bus['original']
            if not t.Solids:row=profile_gap(a,t,metadata.get(name,{}).get('nominal_profile_radius_mm'),limit)
            else:
                gap=q.distance(a,t);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit)
                if limit==0:row['common_mm3']=a.common(t).Volume;row['ok'] &= row['common_mm3']<1e-5
            checks[n+'|'+name]=row
    dest=OUT/'n01-shared-fore-carrier.json';bundle=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in actors.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind='T18I' if n.startswith('BundleTie:') else 'PETG'))
    result=dict(status='SHARED_FORE_CARRIER_STATIC_'+('HOLD' if any(not r['ok'] for r in checks.values()) else 'RECEIVED'),
        recipe=recipe,checks=checks,failures=[k for k,v in checks.items() if not v['ok']],geometry=geometry,
        bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),source_sha256=pins,
        remaining_whole123_corridors_assembly_and_N02_OPEN=True,N01_complete=False,physical_pass=False,
        native_unchanged=True,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],result['failures'],result['worker_seconds'],flush=True)
    return result


def compose_received(world,fixed,metadata,ends,pins,actors,recipe,receipt,fl,flplan,fhy,fhypacket,monitor,monpacket,reservations):
    """Receive changed interactions, reuse unchanged wire-source evidence.

    Previous FL HOLD was ONLY the retired Monitor. Previous FHY HOLD was
    received by the full orthogonal closure; neither old negative is hidden.
    """
    from receive_feline_jpwm_whole_pose import receive_sampled_motion
    tick=time.monotonic();assert receipt['status']=='SHARED_FORE_CARRIER_STATIC_RECEIVED' and not receipt['failures']
    assert fhypacket['status']=='FHY_DIAGONAL_SIDE_HEAD_STATIC36_RECEIVED_ROOT_OPEN' and not fhypacket['failures']
    assert monpacket['status']=='MONITOR_FRONT_TRAY_PORT_STATIC36_RECEIVED_DELIVERED_EDGE_FIT_OPEN' and not monpacket['failures']
    assert all(k.endswith('|Station:Monitor:case') for k in flplan['failures'])
    legtop=max(row['bounds'][1][2] for row in world.motion)
    assert min(s.BoundBox.ZMin for s in fl.values())-legtop>1.25
    riser=json.loads((OUT/'n01-front-shared-rail-riser-motion.json').read_text())
    assert riser['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED' and riser['actor_count']==1
    rest={n:s for n,s in actors.items() if n!='FrontShared:rail_riser'}
    assert min(s.BoundBox.ZMin for s in rest.values())-legtop>1.25
    motion=receive_sampled_motion(world,rest,'n01-front-shared-six-new-motion',pins)
    assert motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
    new={**fl,**fhy,**monitor,**reservations,**actors};changes={};q=SolidQueries()
    # FL vs FHY old -90 receipt is NOT reused for the new45 kit. Check only
    # these changed neighbors plus moved Monitor/port; existing world stays.
    for n,s in fl.items():
        for b,t in {**fhy,**monitor,**reservations}.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
            gap=q.distance(s,t);changes[n+'|'+b]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
    assert all(r['ok'] for r in changes.values()),changes
    updates={}
    for eid,row in flplan['updates'].items():
        u=dict(row);part=flplan['routes'][eid];R=part['radius_mm'];p=np.array(part['start']);theta=9/R
        tip=p+R*np.array([math.sin(theta),-(1-math.cos(theta)),0])
        u.update(jacket_grip9_mm=[p.tolist(),tip.tolist()],full_grip_arclength_mm=[0,9],
            grip_is_curved_not_straight_chord=True,grip_is_common_continuous_bundle_support=True,
            independent_individual_termination_relief_NOT_inferred=True,
            routing_boundary_status='CURRENT_SHARED_FL9_INBOARD_BUNDLE_GUIDE_ROOT_STATIC36_N02_OPEN',
            pose_status='CURRENT_PROJECT_FIXED_CUFF_SEAM_CHANGED_N02_OPEN',
            current_update='Whole common FL cuff fixed seamX-87; moving seam/electrical identities and bought leads unchanged',
            full_moving_flex_NOT_qualified=True,current_restraint_receipt='n01-shared-fore-current-sources.json')
        updates[eid]=u
    updates.update(fhypacket['updates'])
    dest=OUT/'n01-shared-fore-current-sources.json';bundle=dest.with_suffix('.breps.zip');geometry=[]
    for r in updates.values():r['full_middle_route_accepted']=False
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in new.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            kind='wire' if n in fl else 'service_reservation' if n in reservations else 'purchased_case_planning_envelope' if n=='Station:Monitor:case' else metadata.get(n,{}).get('kind','PETG')
            if n.startswith('BundleTie:'):kind='T18I'
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind=kind,
                wire=next((u['wire'] for u in updates.values() if u.get('prefix_geometry_owner')==n),None)))
    sources=('n01-FL9-inboard-whole-plan.json','n01-FHY-diagonal-side-head-source.json',
        'n01-Monitor-front-tray.json','n01-shared-fore-carrier.json','n01-front-shared-rail-riser-motion.json','n01-front-shared-six-new-motion.json')
    result=dict(status='SHARED_FORE28_ROOTED_CURRENT_SOURCES_STATIC36_RECEIVED_WHOLE123_OPEN',
        geometry=geometry,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),
        retired=[*fl,*fhy,'Station:Monitor:case','BundleCuff:FL','BundleTie:FL','BundleTie:FLHead'],
        updates=updates,print_recipe=recipe,changed_source_neighbor_checks=changes,
        existing_positive_FL_world_pairs_reused_except_changed_FHY_Monitor_and_new_roots=True,
        discarded_old_Monitor_negative_rows=flplan['failures'],
        FL_source_bodies_vertical_sample36_separation_mm=min(s.BoundBox.ZMin for s in fl.values())-legtop,
        fixed_FL_seam_shift_mm=-11.5,moving_ends_bought_servo_leads_and_all_electrical_end_reliefs_preserved=True,
        conditional_monitor_mounting_and_balance_gates=monpacket['balance_factory_length_pinout_and_surface_fit_delivery_gates'],
        source_sha256={**pins,**{(OUT/n).relative_to(ROOT).as_posix():sha(OUT/n) for n in sources}},
        failures=[],N01_complete=False,physical_pass=False,native_unchanged=True,
        whole123_factory_middles_corridors_common_assembly_and_N02_OPEN=True,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],len(new),result['worker_seconds'],flush=True)
    return new,result
