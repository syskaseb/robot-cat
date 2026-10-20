"""One provisional Monitor5015 tray near battery, with full port space.

41x25x12 is the selected planning envelope, NOT manufacturer mounting pads.
No unknown pads are clamped: adjustable PCB-edge keepers are fitted only
after delivery. This receives space/root, not native or delivered retention.
"""
import hashlib,json,time,zipfile
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_source_restraint_plan import box,joined
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json


def receive(world,fixed,meta,pins,docs,case,port):
    from receive_feline_jpwm_whole_pose import receive_sampled_motion
    tick=time.monotonic();plate='Print_P0_BATTERY_PLATE_R4';old=fixed[plate]
    floor=box([-71.5,-23.5,9.5],[-40.5,23.5,11.5])
    pieces=[floor,box([-71.5,-23.5,11.5],[-69.5,23.5,23.5]),
        box([-42.5,-23.5,11.5],[-40.5,23.5,23.5]),box([-71.5,-23.5,11.5],[-40.5,-21.5,23.5])]
    for y in (-22.5,22.5):pieces.append(box([-62,y-1,-.5],[-60,y+1,11.5]))
    tray=joined(pieces);overlap=tray.common(old).Volume;whole=tray.fuse(old)
    assert overlap>1 and whole.isValid() and len(whole.Solids)==1
    assert old.cut(whole).Volume<1e-5
    actors={'Station:Monitor:case':case,'MonitorTray:rooted_pocket':tray}
    reservations={'MonitorTray:full_header_access':port};checks={};q=SolidQueries()
    scene={**fixed,**actors}
    for n,s in {**actors,**reservations}.items():
        checks[n+'|outer']=outer_margin(s,docs['outer'])
        for b,t in {**scene,**reservations}.items():
            if n==b or n=='Station:Monitor:case' and b=='Station:Monitor:case':continue
            if n=='MonitorTray:rooted_pocket' and b==plate:continue
            if {n,b}<={'Station:Monitor:case','MonitorTray:rooted_pocket','MonitorTray:full_header_access'}:
                limit=0. # own nominal envelope/port boundaries only
            else:limit=1.25
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>limit+1e-6:continue
            a=s;other=t
            if b==world.bus['name']:a=s.copy();a.Placement=world.bus['inverse']*a.Placement;other=world.bus['original']
            if not other.Solids:row=profile_gap(a,other,meta.get(b,{}).get('nominal_profile_radius_mm'),limit)
            else:
                gap=q.distance(a,other);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit)
                if limit==0:row['common_mm3']=a.common(other).Volume;row['ok'] &= row['common_mm3']<1e-5
            checks[n+'|'+b]=row
    motion=receive_sampled_motion(world,{**actors,**reservations},'n01-Monitor-whole-tray-port-motion',pins)
    dest=OUT/'n01-Monitor-front-tray.json';bundle=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in {**actors,**reservations}.items():
            assert s.isValid() and len(s.Solids)==1
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),
                kind='service_reservation' if n in reservations else 'purchased_case_planning_envelope' if n=='Station:Monitor:case' else 'PETG'))
    result=dict(status='MONITOR_FRONT_TRAY_PORT_STATIC36_RECEIVED_DELIVERED_EDGE_FIT_OPEN' if all(r['ok'] for r in checks.values()) and motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED' else 'MONITOR_FRONT_TRAY_PORT_HOLD',
        checks=checks,failures=[k for k,v in checks.items() if not v['ok']],geometry=geometry,
        bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),retired=['Station:Monitor:case'],
        root_joint=dict(original_plate_preserved=True,overlap_mm3=overlap,whole_1Solid=True,
            unchanged_existing_four_battery_bolt_interfaces=True,maximum_print_dimensions_mm=[whole.BoundBox.XLength,whole.BoundBox.YLength,whole.BoundBox.ZLength]),
        assembly=['Form one planned battery plate/tray on the original4bolt interfaces; no new board holes',
            'Bench-fit insulating adjustable PCB-edge keepers after delivery; do not clamp unknown pads or components',
            'Orient complete monitor/header toward+Y in the planned20mm port space',
            'Fit selected3S factory4tap balance interface only after unpowered delivered compatibility/length check',
            'Install labels/retention then common carrier; deep repair may disconnect labelled balance plug'],
        actual_monitor_mounting_pads_NOT_inferred=True,keeper_adjustment_within_reserved_pocket_is_N03=True,
        no_new_balance_extension_or_SKU_authorized=True,nominal_current_housing_41x25x12_NOT_real_pad_model=True,
        balance_factory_length_pinout_and_surface_fit_delivery_gates=True,
        motion_receipt='n01-Monitor-whole-tray-port-motion.json',source_sha256=pins,
        N01_complete=False,physical_pass=False,native_unchanged=True,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],result['failures'],result['worker_seconds'],flush=True)
    return actors,reservations,result
