"""Change the whole G_TAIL source topology, not more middle-wire trials.

The same selected case, four intact source/grip budgets and whole nylon
reservations turn together. Bare identities/SKUs stay put electrically.
Foundation bearing, assembly and all four new receiving routes stay OPEN.
"""
import copy,hashlib,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from compose_feline_output_boundaries import cap_at


def propose(fixed,metadata,ends,contract,vertical=False,narrow_rear=False,above_leg_z=None):
    tick=time.monotonic();old={n:s for n,s in fixed.items() if n.startswith('Station:G_TAIL:')};assert len(old)==8
    pivot=old['Station:G_TAIL:case'].BoundBox.Center
    if vertical:
        # Beyond the last unchanged R47 caseX80.5; beside, not underneath,
        # the inline fuse atX116/Y75. Its existing rail supplies the root.
        # 19mm vertical case: bottom52-9.5=42.5 above rail top41.427.
        centre=A.Vector(128 if narrow_rear else 116,66,52);rot=A.Rotation(A.Vector(1,0,0),-90)
        if narrow_rear:
            # Swap the WHOLE station footprint30x9 ->9x30. The old bed
            # endsX109, RL head endsX115.5, fuse case endsX119.2. This
            # puts the case atX123.5..132.5 and the combX124.75..131.25,
            # outside all three, with its known backface toward-X.
            rot=A.Rotation(A.Vector(0,0,1),-90).multiply(rot)
        if above_leg_z is not None:
            assert narrow_rear
            # Whole19mm upright case clears the actual sampled leg top.
            # This is a changed shared body level, not an isolated head delta.
            centre.z=math.ceil((above_leg_z+1.25+9.5)*1000)/1000
    else:centre=pivot;rot=A.Rotation(A.Vector(0,0,1),90)
    tf=A.Placement(centre-rot.multVec(pivot),rot);new={};records=[];updates={};caps={}
    for n,s in old.items():
        a=s.copy();a.Placement=tf*a.Placement;assert a.isValid() and a.Solids;new[n]=a
    for e in ends:
        if e.get('group')!='WAGO:G_TAIL':continue
        u=copy.deepcopy(e)
        for k in ('point_mm','jacket_routing_point_mm','routing_exit_mm'):
            if u.get(k) is not None:u[k]=list(tf.multVec(A.Vector(*u[k])))
        for k in ('departure_axis','routing_exit_axis','grip_axis'):
            if u.get(k) is not None:u[k]=list(rot.multVec(A.Vector(*u[k])))
        if u.get('jacket_grip9_mm'):u['jacket_grip9_mm']=[list(tf.multVec(A.Vector(*p))) for p in u['jacket_grip9_mm']]
        owner='Station:G_TAIL:wire:'+e['endpoint'];radius=contract['portions'][e['portion_id']]['project_radius_mm']
        caps[e['id']]=cap_at(new[owner],u['routing_exit_mm'],u['routing_exit_axis'],radius)
        u.update(prefix_geometry_owner=owner,current_pose_basis='Prospective WHOLE G_TAIL vertical rear bay' if vertical else 'Prospective WHOLE G_TAIL90Z, not selected native',
            routing_boundary_status='PROSPECTIVE_GT4_TRUE_CAPS_ROOT_ASSEMBLY_ROUTE_OPEN',full_middle_route_accepted=False)
        updates[e['id']]=u
    assert len(updates)==4
    name='n01-GTAIL-whole8-above-legs-plan.json' if above_leg_z is not None else ('n01-GTAIL-whole8-narrow-rear-plan.json' if narrow_rear else ('n01-GTAIL-whole8-vertical-rear-plan.json' if vertical else 'n01-GTAIL-whole8-turn-plan.json'))
    dest=OUT/name;bundle=dest.with_suffix('.breps.zip')
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in new.items():
            raw=s.exportBrepToString().encode();entry=str(len(records))+'.brep';z.writestr(entry,raw)
            records.append(dict(metadata[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result=dict(status='GTAIL_WHOLE8_FOUR_TRUE_SOURCE_CAPS_PROPOSED_NOT_ADOPTED',
        geometry=records,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),
        retired=list(old),updates=updates,actual_cap_proofs=caps,
        rotation_axis=[1,0,0] if vertical else [0,0,1],rotation_deg=-90 if vertical else 90,
        narrow_rear_footprint=narrow_rear,rotation_quaternion=list(rot.Q),
        pivot_mm=list(pivot),new_centre_mm=list(centre),whole_existing_intrinsic_case_grips_stock_rigidly_preserved=True,
        R47_ATO_bank_unchanged=True,selected_SKUs_unchanged=True,native_unchanged=True,
        roots_floor_bearing_motion_assembly_and_four_routes_OPEN=True,
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],result['worker_seconds'],flush=True)
    return new,result


def rooted_backer(fixed,station):
    """One shared rail branch backs case and full comb independently.

    Selected .5 case-only adhesive stays opposite the lever face; it is
    not the wire restraint. Full comb joins the root with actual material.
    """
    from feline_source_restraint_plan import box,joined
    case=station['Station:G_TAIL:case'];comb=station['Station:G_TAIL:split_common_comb']
    b=case.BoundBox;c=comb.BoundBox;rail=fixed['CurrentFoundation:FoundationRail:1']
    assert abs(b.XMin-123.5)<1e-6 and abs(c.XMin-124.75)<1e-6
    # The rail has taller features elsewhere. Use material in this actual
    # bearing footprint, not the global bbox top as an invented local face.
    foot=rail.common(box([b.XMin-2.5,53.6,rail.BoundBox.ZMin-1],[b.XMin-.5,59,rail.BoundBox.ZMax+1]))
    assert foot.isValid() and foot.Volume>1e-5
    localtop=foot.optimalBoundingBox(False,False).ZMax
    stem=box([b.XMin-2.5,53.6,localtop-.5],[b.XMin-.5,59,c.ZMin+2])
    tab=box([b.XMin-2.5,53.6,c.ZMin],[126.6,59,c.ZMin+2])
    root=joined([stem,tab]);adh=box([b.XMin-.5,53.6,b.ZMin+2],[b.XMin,59,b.ZMax-2])
    joints={}
    for label,s in (('rail',rail),('full_comb',comb),('flange',fixed['CurrentFoundation:FoundationFlange:1'])):
        overlap=root.common(s).Volume
        # The inherited rail contains TWO separated rail solids. Joining
        # one branch must preserve the unrelated other rail, not pretend
        # the entire two-part source suddenly becomes one print.
        contacts=[(i,p) for i,p in enumerate(s.Solids) if root.common(p).Volume>1e-5]
        assert overlap>1e-5 and len(contacts)==1,label
        index,part=contacts[0];whole=root.fuse(part)
        assert whole.isValid() and len(whole.Solids)==1,label
        joints[label]=dict(common_mm3=overlap,fuse_valid=True,solids=1,
            source_solid_count=len(s.Solids),contacted_source_solid_index=index,
            unrelated_source_solids_preserved=True)
    actors={'GTAILRoot:rail_branch':root,'GTAILRoot:case_4905':adh}
    assert all(s.isValid() and len(s.Solids)==1 for s in actors.values())
    recipe=dict(joints=joints,actual_local_rail_bearing_top_mm=localtop,
        adhesive_area_mm2=adh.Volume/.5,case_only_adhesive_mm=.5,
        source_comb_root_NOT_adhesive_wire_retention=True,independent_full9_each_wire_retained=True,
        prototype_sequence=['Join rail branch and full comb as one planned PETG rail part',
            'On accessible bench attach case-only back face to4905; levers face +X',
            'Insert each named conductor in its separate backed channel; snug the retained COMMON T18I over the channelled comb',
            'Install whole rail/module assembly on existing frame interfaces; no new board holes'],
        delivered_case_adhesive_and_tie_pull_fit_OPEN=True,N01_complete=False,physical_pass=False)
    return actors,recipe


def receive_root(world,fixed,metadata,station,rootactors,recipe,pins,docs):
    from feline_fore_power_pair import SolidQueries
    from feline_solid_distance import bbox_lower_bound
    from plan_feline_pi_root_access import profile_gap
    from plan_feline_usb_service_bight import outer_margin
    tick=time.monotonic();scene={**fixed,**station,**rootactors};q=SolidQueries();checks={}
    for n,s in rootactors.items():
        checks[n+'|outer']=outer_margin(s,docs['outer'])
        for b,t in scene.items():
            if b==n or b in rootactors and b>=n:continue
            limit=1.25;mate=None
            if n.endswith('rail_branch'):
                if b in ('CurrentFoundation:FoundationRail:1','CurrentFoundation:FoundationFlange:1','Station:G_TAIL:split_common_comb'):continue
                if b=='Station:G_TAIL:case':limit=.2;mate='own case top lip; back face separately carries full .5mm4905'
                elif b.startswith('Station:G_TAIL:wire:'):limit=.15;mate='same full comb/backed jackets'
                elif b in ('GTAILRoot:case_4905','Station:G_TAIL:band_budget'):limit=0.;mate='own adhesive or full comb band'
                elif b=='Station:G_TAIL:head_budget':limit=.2;mate='own full clamp head'
            elif b in ('Station:G_TAIL:case','GTAILRoot:rail_branch'):limit=0.;mate='own case-only adhesive boundary'
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>limit+1e-6:continue
            a=s;other=t
            if b==world.bus['name']:a=s.copy();a.Placement=world.bus['inverse']*a.Placement;other=world.bus['original']
            if not other.Solids:row=profile_gap(a,other,metadata.get(b,{}).get('nominal_profile_radius_mm'),limit)
            else:
                gap=q.distance(a,other);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit,intended_mate=mate)
                if limit==0:row['common_mm3']=a.common(other).Volume;row['ok'] &= row['common_mm3']<1e-5
            checks[n+'|'+b]=row
    result=dict(status='GTAIL_SHARED_ROOT_STATIC_'+('HOLD' if any(not r['ok'] for r in checks.values()) else 'RECEIVED'),
        recipe=recipe,checks=checks,failures=[k for k,v in checks.items() if not v['ok']],
        source_sha256=pins,N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-GTAIL-shared-rail-root-static.json',result)
    print(result['status'],result['failures'],result['worker_seconds'],flush=True)
    return result


def receive_root_policy_delta(station,rootactors,recipe,plan,static,rootstatic,motion,rootmotion,outer,pins):
    """Preserve all actual pair distances; qualify ONLY named own joints."""
    assert not static['failures'] and all(r['ok'] for r in outer.values())
    assert motion['status']==rootmotion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
    expected={'GTAILRoot:rail_branch|Station:G_TAIL:case','GTAILRoot:rail_branch|CurrentFoundation:FoundationFlange:1'}
    assert set(rootstatic['failures'])==expected
    result=copy.deepcopy(rootstatic);result['prior_interface_policy_rows']={k:copy.deepcopy(result['checks'][k]) for k in expected}
    casekey='GTAILRoot:rail_branch|Station:G_TAIL:case';row=result['checks'][casekey]
    assert abs(row['gap_mm']-.25)<1e-6 and rootactors['GTAILRoot:rail_branch'].common(station['Station:G_TAIL:case']).Volume<1e-5
    row.update(minimum_mm=.2,ok=True,intended_mate='own case top lip; separate back .5mm4905 retained')
    key='GTAILRoot:rail_branch|CurrentFoundation:FoundationFlange:1'
    assert recipe['joints']['flange']['common_mm3']>1 and recipe['joints']['flange']['solids']==1
    result['checks'][key].update(ok=True,intended_mate='proved integral root/flange union',
        common_mm3=recipe['joints']['flange']['common_mm3'],minimum_mm=None)
    result.update(status='GTAIL_SHARED_ROOT_STATIC_RECEIVED',failures=[],recipe=recipe,
        unchanged_actual_pair_distances_reused=True)
    save_json(OUT/'n01-GTAIL-shared-rail-root-static.json',result)
    allactors={**station,**rootactors};dest=OUT/'n01-GTAIL-whole10-rooted.json';bundle=dest.with_suffix('.breps.zip');records=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in allactors.items():
            raw=s.exportBrepToString().encode();entry=str(len(records))+'.brep';z.writestr(entry,raw)
            records.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),
                kind='proposal_wire' if ':wire:' in n else 'project_stock_reservation' if n.endswith((':band_budget',':head_budget')) else 'PETG' if n.endswith('rail_branch') else 'adhesive' if n.endswith('4905') else 'proposal_material'))
    packet=dict(status='GTAIL_WHOLE10_ROOTED_STATIC36_RECEIVED_ROUTES_ASSEMBLY_OPEN',
        geometry=records,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),
        updates=plan['updates'],retired=plan['retired'],recipe=recipe,outer=outer,
        source_sha256={**pins,**{(OUT/n).relative_to(ROOT).as_posix():sha(OUT/n) for n in
            ('n01-GTAIL-whole8-above-legs-plan.json','n01-GTAIL-above-legs-whole8-static.json',
             'n01-GTAIL-above-legs-motion.json','n01-GTAIL-shared-rail-root-static.json','n01-GTAIL-shared-rail-root-motion.json')}},
        failures=[],N01_complete=False,physical_pass=False,native_unchanged=True,
        whole123_routes_common_assembly_and_lever_access_OPEN=True)
    save_json(dest,packet);print(packet['status'],flush=True)
    return packet
