"""One three-wire P_SYS corridor entry, received as a whole hypothesis."""
import json,math,time,sys,hashlib,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_integrated_space_context import integrated
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from receive_feline_positive_service_deck import pipe,circle_arc
from plan_feline_usb_service_bight import outer_margin


def main():
    tick=time.monotonic();world,parts,meta,pins,context=integrated();query=SolidQueries()
    joint_retention='--joint-retention' in sys.argv;corridor_first=joint_retention or '--corridor-first' in sys.argv
    portal=joint_retention or '--bank-portal' in sys.argv;divergent=portal or corridor_first or '--divergent-prefixes' in sys.argv
    ef=OUT/'n01-shared-routing-boundaries.json';ends=json.loads(ef.read_text())['endpoints']
    curves={};recipe={};checks={};failures=[];bounds={n:s.BoundBox for n,s in parts.items()}
    for terminal,wire in ((1,'W066'),(2,'W067'),(3,'W068')):
        e=next(e for e in ends if e['endpoint']=='P_SYS.'+str(terminal));q=np.array(e['routing_exit_mm']);d=np.array(e['routing_exit_axis']);d/=np.linalg.norm(d)
        source=parts['Station:P_SYS:wire:P_SYS.'+str(terminal)]
        caps=[f for f in source.Faces if isinstance(f.Surface,Part.Plane) and (f.CenterOfMass-A.Vector(*q)).Length<1e-4]
        assert len(caps)==1,'Routing exit must coincide with exactly one actual source cap'
        actual_radius=math.sqrt(caps[0].Area/math.pi)
        radius=float(e['minimum_R_mm'])
        if divergent:
            first=next(f for f in source.Faces if isinstance(f.Surface,Part.Plane) and (f.CenterOfMass-A.Vector(*q)).Length>1)
            q=np.array(list(first.CenterOfMass));u,U,v,V=first.ParameterRange;d=-np.array(list(first.normalAt((u+U)/2,(v+V)/2)))
            if not source.isInside(A.Vector(*(q+d)),1e-7,False):d=-d
            assert source.isInside(A.Vector(*(q+8.9*d)),1e-7,False),'Preserve the actual first9 land'
            assert np.allclose(d,[-1,0,0]),d
            normal=np.array([0.,1 if terminal in (1,2) else -1,0]);angle=math.radians(40 if terminal==2 else 60)
            if corridor_first:angle=math.pi/4
            if portal and not corridor_first and terminal!=2:normal[2]=1;normal/=np.linalg.norm(normal)
            land=q+9*d;edge=circle_arc(land,d,normal,radius,angle)
            s,path=pipe([Part.makeLine(A.Vector(*q),A.Vector(*land)),edge],actual_radius)
            target=math.cos(angle)*d+math.sin(angle)*normal
        else:
            target=np.array([0.,0,1 if '--upper-rise' in sys.argv else -1]);angle=math.acos(float(d@target));normal=(target-math.cos(angle)*d)/math.sin(angle)
            edge=circle_arc(q,d,normal,radius,angle);s,path=pipe([edge],actual_radius)
        name='P_SYS_entry:'+wire;curves[name]=s
        recipe[name]=dict(source_end=e['id'],source_prefix_owner='Station:P_SYS:wire:P_SYS.'+str(terminal),
            start_mm=q.tolist(),start_axis=d.tolist(),normal=normal.tolist(),R_mm=radius,angle_rad=angle,
            exit_mm=list(edge.valueAt(edge.LastParameter)),exit_axis=target.tolist(),length_mm=path.Length,
            radius_mm=actual_radius,radius_from_actual_source_cap=True,whole_middle_and_cut_length_not_selected=True)
    old_prefixes={}
    if divergent:
        for r in recipe.values():old_prefixes[r['source_prefix_owner']]=parts.pop(r['source_prefix_owner'])
    flp_changed=[];flp_unit=None
    if corridor_first:
        from feline_t18i_two_lane import unit
        planfile=OUT/'n01-flat-station-architecture.json';sharedfile=OUT/'n01-shared54-current.json'
        st=next(st for st in json.loads(planfile.read_text())['stations'] if st['ref']=='FL_P')
        choice=json.loads(sharedfile.read_text())['chosen']['FL_P'];assert choice['lane']==1 and choice['slot']['id']==19
        flp_unit=unit(st,choice['slot'],0);case=parts['Station:FL_P:case'];newcase=flp_unit['parts']['case']
        assert case.cut(newcase).Volume+newcase.cut(case).Volume<1e-5,'Do not move or change purchased FL_P'
        for short,s in flp_unit['parts'].items():
            if short=='case':continue
            name='Station:FL_P:'+short;old=parts.pop(name);flp_changed.append(name)
            if short.startswith('wire:'):assert s.cut(old).Volume<1e-5,'First land/source mouth must remain unchanged'
            curves[name]=s;recipe[name]=dict(reused_existing_complete_lane=0,old_lane=1,case_and_all_ports_unchanged=True,
                full9_grips_full_selected_T18I_and_wire_radii_preserved=True)
        assert len(flp_changed)==7
        parts.pop('CurrentFoundation:BankPier:2/0')
        pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (planfile,ROOT/'tools/cad/feline_t18i_two_lane.py',ROOT/'tools/cad/feline_t18i_selected_head.py',ROOT/'tools/cad/feline_shared_straight_combs.py')})
    subset_actors=set();frame_parent={};extra_meta={}
    if joint_retention:
        from feline_shared_frame import box
        # Rotate the same actual head by180 around the unchanged loop axis.
        name='Station:G2:head_budget';head=parts.pop(name).copy();band=parts['Station:G2:band_budget'];centre=band.BoundBox.Center
        rotation=A.Rotation(A.Vector(0,1,0),180);tf=A.Placement(centre-rotation.multVec(centre),rotation)
        rotated=band.copy();rotated.Placement=tf*rotated.Placement
        assert rotated.cut(band).Volume+band.cut(rotated).Volume<1e-5
        head.Placement=tf*head.Placement;curves[name]=head;extra_meta[name]=meta[name]
        recipe[name]=dict(same_T18I_head_rotated_deg=180,axis=[0,1,0],loop_symmetric_difference_mm3=0.,case_wires_comb_band_unchanged=True)
        # Full-height feedthrough for the physical tie, not a thin residual
        # skin. Lower continuous flange remains below the tie clearance.
        stock=curves['Station:FL_P:band_budget'].BoundBox;gap=1.251
        x0,x1=stock.XMin-gap,stock.XMax+gap;y0,y1=stock.YMin-gap,stock.YMax+gap
        for short in ('FoundationRail:1','ClampNeck:2','FoundationFlange:1'):
            name='CurrentFoundation:'+short;old=parts.pop(name);b=old.BoundBox
            if short=='FoundationRail:1':cutter=box([x0,b.YMin-1,b.ZMin-1],[x1,b.YMax+1,b.ZMax+1])
            elif short=='ClampNeck:2':cutter=box([b.XMin-1,y0,b.ZMin-1],[b.XMax+1,b.YMax+1,b.ZMax+1])
            else:cutter=box([x0,b.YMin-1,38.52],[x1,b.YMax+1,b.ZMax+1])
            new=old.cut(cutter).removeSplitter();assert new.isValid() and new.Solids
            assert new.cut(old).Volume<1e-5,'Only own new stock may be removed'
            curves[name]=new;subset_actors.add(name);frame_parent[name]=old;extra_meta[name]=meta[name]
            recipe[name]=dict(only_removed_provisional_PETG_mm3=old.Volume-new.Volume,solids=len(new.Solids),
                old_bought_parts_and_all4_clamp_seats_unchanged=True,root_connectivity_still_requires_receipt=True)
        # Root in the MEASURED surviving neck slice, not its empty bounding
        # height. Restore only provisional material freed by FL_P lane0.
        web=box([-37,34.75,39.8],[-33,45.9,55]);beam=box([-37,33.5,52],[-21,37.5,55])
        base=box([-37,43.5,39.8],[-21,45.9,41.8])
        plug=box([-27,43.5,38.52],[-21,45.9,40.52])
        assert plug.common(base).Volume>=5
        support=web.fuse(beam).fuse(base).fuse(plug).removeSplitter();assert support.isValid() and len(support.Solids)==1
        name='BankPortal2:Carrier';curves[name]=support;joints=[]
        for mate,minimum_common in (('CurrentFoundation:ClampNeck:2',5.),('CurrentFoundation:BankLedge:2',20.)):
            target=curves[mate] if mate in curves else parts[mate];common=support.common(target)
            assert common.isValid() and common.Volume>=minimum_common,(mate,common.Volume)
            joints.append(dict(owner=mate,positive_common_mm3=common.Volume,minimum_mm3=minimum_common))
        recipe[name]=dict(actual_positive_root_joints=joints,retired_only_provisional_support='CurrentFoundation:BankPier:2/0',
            side_wall_mm=[4,11.15,15.2],top_beam_mm=[16,4,3],base_bridge_mm=[16,2.4,2],
            restored_provisional_neck_plug_mm=[6,2.4,2],physical_stiffness_not_qualified=True,
            actual_neck_slices_received_before_root_choice=True)
    if portal and not joint_retention:
        from feline_shared_frame import box
        old_pier='CurrentFoundation:BankPier:2/0';assert old_pier in parts;parts.pop(old_pier)
        foot=box([-37,27,40.52],[-33,52.6,55]);beam=box([-37,42,52],[-21,52.6,55])
        root_bridge=box([-37,27,40.52],[-20,31,42.52])
        support=foot.fuse(beam).fuse(root_bridge).removeSplitter();assert support.isValid() and len(support.Solids)==1
        name='BankPortal2:Carrier';curves[name]=support
        joints=[]
        for mate,minimum_common in (('CurrentFoundation:ClampSeat:2',5.),('CurrentFoundation:BankLedge:2',20.)):
            common=support.common(parts[mate]);assert common.isValid() and common.Volume>=minimum_common,(mate,common.Volume)
            joints.append(dict(owner=mate,positive_common_mm3=common.Volume,minimum_mm3=minimum_common))
        recipe[name]=dict(retired_only_provisional_support=old_pier,vertical_web_mm=[4,25.6,14.48],
            top_beam_mm=[16,10.6,3],lower_bridge_mm=[17,4,2],actual_positive_root_joints=joints,physical_stiffness_not_qualified=True,
            empty_trimmed_rail_foot_rejected_before_collision_checks=True,
            case_W043_P0_bank_bearing_parts_unchanged=True)
    actor_meta={n:dict(kind='proposal_material' if n.startswith('BankPortal') else 'wire') for n in curves}
    for n in flp_changed:actor_meta[n]=meta[n]
    actor_meta.update(extra_meta)
    actor_meta={n:dict(row,kind=row.get('kind','proposal_material')) for n,row in actor_meta.items()}
    portal_delta=curves['BankPortal2:Carrier'].cut(curves['CurrentFoundation:ClampNeck:2']) if joint_retention else None
    if portal_delta is not None:assert portal_delta.isValid() and portal_delta.Solids
    frozen_geometry=None;frozen_archive=None
    if joint_retention:
        frozen_archive=OUT/'n01-psys-flp-joint-retention.breps.zip';frozen_geometry=[]
        with zipfile.ZipFile(frozen_archive,'w',zipfile.ZIP_DEFLATED) as z:
            for i,(name,shape) in enumerate(curves.items()):
                raw=shape.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
                frozen_geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind=actor_meta[name]['kind']))
        save_json(OUT/'n01-psys-flp-joint-construction.json',dict(status='WHOLE_JOINT_CONSTRUCTION_RECEIVED_WORLD_OPEN',
            geometry=frozen_geometry,bundle=frozen_archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(frozen_archive),
            recipe=recipe,source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},N01_complete=False,physical_pass=False))
    for n,s in curves.items():
        b=s.BoundBox;r=outer_margin(s,context['outer']);checks[n+'|outer']=r
        if not r['ok']:failures.append(dict(a=n,b='outer',**r))
        for m,t in {**parts,**curves}.items():
            if m==n:continue
            if n in subset_actors and m not in curves:continue # Exact subsets inherit unchanged external clearance, never new interfaces.
            minimum=pair_spacing(n,actor_meta[n],m,actor_meta[m] if m in curves else meta[m])
            if bbox_lower_bound(b,t.BoundBox if m in curves else bounds[m])>=minimum:continue
            if m==world.bus['name']:
                transformed=s.copy();transformed.Placement=context['inverse']*transformed.Placement
                gap=query.distance(world.bus['original'],transformed)
            elif t.Solids:gap=query.distance(portal_delta if portal_delta is not None and n.startswith('BankPortal') and m not in curves else s,t)
            else:
                rr=meta[m].get('nominal_profile_radius_mm')
                if rr:
                    from plan_feline_pi_root_access import profile_gap
                    r=profile_gap(s,t,rr,minimum);checks[n+'|'+m]=r
                    if not r['ok']:failures.append(dict(a=n,b=m,**r))
                    continue
                raise AssertionError(('Unqualified curve owner',m))
            r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
            if m==recipe[n].get('source_prefix_owner'):
                common=s.common(t);assert common.isNull() or common.isValid()
                r.update(ok=common.Volume<1e-5,actual_own_prefix_end_continuation_common_mm3=common.Volume)
            if divergent and n.startswith('P_SYS_entry:') and m.startswith('Station:P_SYS:') and ':wire:' not in m:
                common=s.common(t);assert common.isNull() or common.isValid()
                old=old_prefixes[recipe[n]['source_prefix_owner']];prior=old.common(t)
                assert prior.isNull() or prior.isValid()
                if m.endswith(':case'):
                    difference=common.cut(prior).Volume+prior.cut(common).Volume
                    r.update(ok=difference<1e-5,actual_same_first9_case_ingress_symmetric_difference_mm3=difference)
                else:
                    inherited=query.distance(old,t)
                    r.update(ok=common.Volume<1e-5 and gap>=min(inherited,minimum)-1e-6,
                        unchanged_own_first9_full_stock_nominal_gap_mm=inherited,actual_new_common_mm3=common.Volume)
            if n.startswith('BankPortal') and m in {j['owner'] for j in recipe[n]['actual_positive_root_joints']}:
                j=next(j for j in recipe[n]['actual_positive_root_joints'] if j['owner']==m)
                r.update(ok=True,intended_same_print_positive_root_joint=j['positive_common_mm3'])
            if n in flp_changed and m.startswith('Station:FL_P:') and not (actor_meta[n]['kind']=='wire' and (actor_meta[m] if m in curves else meta[m]).get('kind')=='wire'):
                common=s.common(t);assert common.isNull() or common.isValid()
                r.update(ok=common.Volume<1e-5,matched_complete_existing_FLP_kit_internal_common_mm3=common.Volume,
                    nominal_own_kit_clearance_not_foreign_part_waiver=True)
            if n in flp_changed and actor_meta[n]['kind']!='wire' and m.startswith('CurrentFoundation:'):
                common=s.common(t);assert common.isNull() or common.isValid()
                if common.Volume<1e-5:
                    r.update(ok=True,actual_common_mm3=common.Volume,
                        proposed_printed_root_interface_gap_mm=gap,positive_root_connection_still_OPEN=True)
            if joint_retention and n=='Station:G2:head_budget' and m=='Station:G2:band_budget':
                common=s.common(t);assert common.isNull() or common.isValid()
                r.update(ok=common.Volume<1e-5,same_selected_head_on_opposite_actual_band_face_common_mm3=common.Volume)
            if joint_retention and n.startswith(('CurrentFoundation:','BankPortal')) and m.startswith(('CurrentFoundation:','BankPortal')):
                r.update(ok=True,intended_one_provisional_printed_frame_not_foreign_parts=True,
                    strong_positive_root_joints_received_separately=True,whole_root_graph_still_OPEN=True)
            checks[n+'|'+m]=r
            if not r['ok']:failures.append(dict(a=n,b=m,**r))
        # Do not audit motion of an already blocked topology. Preserve all
        # static witnesses for all THREE wires before changing the plan.
        if any(f['a']==n for f in failures):continue
        for pose in ([] if n in subset_actors else world.motion):
            if bbox_lower_bound(b,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
            s0=(portal_delta if portal_delta is not None and n.startswith('BankPortal') else s).copy();s0.Placement=placement(pose['r'],pose['t']).inverse()*s0.Placement
            gap=query.distance(s0,world.rest[pose['name']]);r=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            key=n+'|motion:'+pose['name']+':'+str(pose['pose']);checks[key]=r
            if not r['ok']:failures.append(dict(a=n,b=key,**r))
        print('Received actor',n,'checks',len(checks),'holds',len(failures),flush=True)
    result=dict(status='WHOLE_PSYS_CORRIDOR_ENTRY_CONFLICTS_RECEIVED' if failures else 'WHOLE_PSYS_CORRIDOR_ENTRY_RECEIVED_NOT_COMPLETE_HARNESS',
        recipe=recipe,checks=checks,failures=failures,errors=[],N01_complete=False,selected=False,physical_pass=False,
        source_sha256={**pins,ef.relative_to(ROOT).as_posix():sha(ef),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    result['whole_PSYS_case_first9_full_stock_and_W043_unchanged']=divergent
    result['retired_only_own_custom_prefix_actors']=list(old_prefixes)
    if corridor_first:
        result.update(bank_support_temporarily_absent_in_planning_not_an_approved_assembly=True,
            retired_FLP_full_kit_names=flp_changed,all_support_roots_tools_and_full_harness_still_OPEN=True,
            status='PSYS_FLP_COMMON_CORRIDOR_HOLDS_RECEIVED_ROOT_OPEN' if failures else 'PSYS_FLP_COMMON_CORRIDOR_RECEIVED_ROOT_OPEN')
    if joint_retention:
        result.update(bank_support_temporarily_absent_in_planning_not_an_approved_assembly=False,
            bank_portal_present_but_whole_root_graph_OPEN=True,changed_printed_subsets=list(subset_actors),
            G2_case_and_wire_grip_lane_unchanged=True,old_G2_lane1_closed_not_repeated=True)
    if portal:
        archive=frozen_archive if joint_retention else OUT/'n01-psys-bank-portal.breps.zip';geometry=frozen_geometry or []
        if not joint_retention:
            with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
                for i,(n,s) in enumerate(curves.items()):
                    raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
                    geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind=actor_meta[n]['kind']))
        result.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),geometry=geometry,
            retired_printed_support='CurrentFoundation:BankPier:2/0')
    save_json(OUT/('n01-psys-flp-joint-retention.json' if joint_retention else 'n01-psys-flp-corridor-first.json' if corridor_first else 'n01-psys-bank-portal.json' if portal else 'n01-psys-three-divergent-prefixes.json' if divergent else 'n01-psys-three-upper-corridor-entry.json' if '--upper-rise' in sys.argv else 'n01-psys-three-corridor-entry.json'),result)
    print(json.dumps(dict(status=result['status'],checks=len(checks),holds=len(failures),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
