"""One coupled source bay and BUS roof budget, before native details.

Pure analytic construction first; --check uses saved actual BRep, changed
interfaces only, including ALL24 bank bends. No native file is saved. All
nominal plug dimensions remain delivery gates, not manufacturer dimensions.
"""
import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'
BASE = OUT.parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def add(a,b):
    return [x+y for x,y in zip(a,b)]

def scale(a,k):
    return [x*k for x in a]

class Route:
    def __init__(self, p, direction):
        self.parts=[]; self.p=list(p); self.d=list(direction)
    def line(self,length):
        assert length>0
        q=add(self.p,scale(self.d,length))
        self.parts.append(dict(kind='line',start=self.p,end=q,length_mm=length))
        self.p=q
        return self
    def turn(self,direction,R):
        assert abs(sum(a*b for a,b in zip(self.d,direction)))<1e-8
        mid=add(self.p,add(scale(self.d,R/math.sqrt(2)),scale(direction,R*(1-1/math.sqrt(2)))))
        q=add(self.p,scale(add(self.d,direction),R))
        self.parts.append(dict(kind='arc',start=self.p,mid=mid,end=q,radius_mm=R,length_mm=R*math.pi/2))
        self.p=q; self.d=list(direction)
        return self
    def record(self, name, radius):
        return dict(wire=name,parts=self.parts,radius_mm=radius,
            length_mm=sum(p['length_mm'] for p in self.parts),end_mm=self.p,end_direction=self.d)

def build():
    tick=time.monotonic()
    ledger_path=OUT/'n01-complete-end-allocation.json'
    ledger=json.loads(ledger_path.read_text())
    ends={r['role']:r for r in ledger['endpoints']}
    materials_path=BASE/'body-harness-checkpoint/w5-nominal-material-selection.json'
    materials=json.loads(materials_path.read_text())
    current={r['wire']:r for r in materials['portions'] if r['wire'] in ('W043','W077','W078','W060','W079','W080')}
    binding_path=BASE/'body-harness-checkpoint/BUS-port-binding.json'
    binding=json.loads(binding_path.read_text())
    assert binding['installed_candidate_header']=='H5'
    assert all(r['reference_is_not_mating_plug_contact_or_exit'] for r in binding['ports']['H5']['pin_columns'])
    # Input+output+splice+MAIN move together. R5 rear bay and flat bank stay.
    shifts={'WAGO:P_SYS_new':[-16.5,9,-2], 'MAIN':[6,0,-7],
            'BUS':[41,0,-18], 'JPWM':[-21,-15,0]}
    vin=add(ends['MAIN.VIN']['point_mm'],shifts['MAIN'])
    sy=vin[1]
    plan=dict(status='ANALYTIC_CANDIDATE_NOT_SELECTED',selected=False,N01_complete=False,
        native_changed=False,physical_pass=False,relative_to='common-backbone-r4, R5 rear bay and flat-bank-r2',
        shifts_mm=shifts,F_PI=dict(centre_mm=[-50,15.5,37],
            rotation_relative_current=[[0,0,1],[0,1,0],[-1,0,0]],
            old_centre_mm=[-141.99999389648437,0,-32],input_mm=[-50,15.5,11.5],output_mm=[-50,15.5,62.5]),
        splice=dict(centre_mm=[-72,sy,71.5],tip16_mm=[-76,sy,71.5],tip18_mm=[-68,sy,71.5],
            sleeve_blank_mm=20,sleeve_x_mm=[-82,-62],bare_overlap_x_mm=[-76,-68],
            jacket_grip16_x_mm=[-60,-51],jacket_grip18_x_mm=[-93,-84],
            outer_project_OD_mm=4.2,clip_reservation_mm=[[-93,sy-4.1,67.4],[-51,sy+4.1,75.6]],
            grips_outside_sleeve=True,grip_clear_gap_each_mm=2,additional_splice_or_connector=False),
        routes=[],bounds_are_not_actual_contacts=True,full_other80net_routes=False,
        actual_tools_verified=False,nominal_plug_fit_verified=False,all_mounts_complete=False)
    # Full W043 including12mm WAGO strip. The whole station is aligned to
    # this actual complete arc/land, not to a Euclidean distance target.
    source=plan['F_PI']['input_mm']
    r=Route(source,[0,0,-1]).line(15.5).turn([0,1,0],6).line(10.5)
    w=r.record('W043',1.7)
    assert math.dist(w['end_mm'],add(ends['P_SYS.5']['point_mm'],shifts['WAGO:P_SYS_new']))<1e-5
    w.update(strip_mm=12,nominal_fit_blank_mm=50,raw_required_mm=w['length_mm']+12,
        selected_pre_fuse_limit_mm=current['W043']['retained_limit_mm'],
        last_intact_grip_mm=[[-50,23,-10],[-50,32,-10]],factory_tip_removal_max_mm=8.35)
    # W077 includes the whole8mm bare overlap and the25mm terminal domain:
    # 8bare +6sleeve overlap +2clear gap +9intact independent grip.
    r=Route(plan['F_PI']['output_mm'],[0,0,1]).line(3).turn([1,0,0],6).line(2)
    r.turn([0,-1,0],6).line(3.5-sy).turn([-1,0,0],6).line(34)
    out=r.record('W077',1.7)
    assert math.dist(out['end_mm'],plan['splice']['tip16_mm'])<1e-8
    out.update(bare_overlap_included_mm=8,factory_tip_removal_max_mm=8.35,
        supplier_shortest_including_tip_mm=84.5,
        source_draw_required_mm=out['length_mm']+8.35,
        nominal_fit_blank_after_tip_removal_mm=74,old_fit_blank_mm=current['W077']['nominal_fit_blank_mm'])
    # Existing donor wire, no extra splice. Shared MAIN displacement resolves
    # the roof as part of the same route. Do not preserve an obsolete140mm cut.
    R=11.1
    r=Route(plan['splice']['tip18_mm'],[-1,0,0]).line(25).turn([0,0,1],R)
    r.line(vin[2]+1.5-r.p[2]).turn([1,0,0],R)
    r.line(vin[0]-R-r.p[0]).turn([0,0,-1],R).line(1.5)
    donor=r.record('W078',1.05)
    assert math.dist(donor['end_mm'],vin)<1e-6
    donor.update(PCB_insertion_allowance_mm=3,raw_required_mm=donor['length_mm']+3,
        selected_retained_limit_mm=current['W078']['retained_limit_mm'],
        selected_fit_blank_mm=current['W078']['nominal_fit_blank_mm'],
        proposed_fit_blank_mm=150,one_K1474_preserved=True)
    plan['routes']=[w,out,donor]
    plan['length_authority']=dict(current=materials_path.relative_to(ROOT).as_posix(),
        current_rows=current,intermediate_210mm_card_is_not_latest_selection=True,
        pre_fuse50_and_red_donor150_limits_retained=True,
        requested_new_cut_lengths_are_candidate_only=True)
    # Only the old14.05mm nominal mating allowance is reused as a planning
    # reserve. It is NOT manufactured contact/exit data.
    bus=[]
    for row in binding['ports']['H5']['pin_columns']:
        if row['role']=='V':continue
        h=add(row['world_header_top_reference_mm'],[41,0,24]) # motion+42 then new-18
        exit=add(h,[0,0,14.05])
        path=Route(exit,[0,0,1]).turn([1,0,0],10).line(9).record('BUS.'+row['role'],1.55)
        bus.append(dict(role=row['role'],header_reference_mm=h,nominal_exit_mm=exit,
            assumption_not_manufacturer_exit=True,first_bend_and_after_bend_grip=path))
    ylo=min(b['nominal_exit_mm'][1] for b in bus)-3.55
    yhi=max(b['nominal_exit_mm'][1] for b in bus)+3.55
    z=bus[0]['nominal_exit_mm'][2]+10
    x=bus[0]['nominal_exit_mm'][0]+10
    plan['BUS']=dict(ports=bus,nominal_mating_reserve_mm=[
        [bus[0]['header_reference_mm'][0]-4.5,ylo, bus[0]['header_reference_mm'][2]-1],
        [bus[0]['header_reference_mm'][0]+4.5,yhi, bus[0]['nominal_exit_mm'][2]]],
        shared_two_lane_after_bend_grip_mm=[[x,ylo,z-3.55],[x+9,yhi,z+3.55]],
        shared_grip_is_not_two_overlapping_straps=True,main_inner_roof_mm=109.6,
        grip_roof_box_margin_mm=109.6-(z+3.55),
        old_nominal_offset14p05_is_delivery_gate=True,USB_mating_and_complete_DG_middle_open=True)
    plan['necessary_length_gate']=dict(W043=w['raw_required_mm']<=50,
        W077=out['source_draw_required_mm']<=84.5,
        W078=donor['raw_required_mm']<=150,
        exact_endpoint_match=True,full_geometry_and_tools_open=True,ready_for_changed_interface_screen=True)
    plan['stock_candidate']=dict(K1474_units=1,each_colour_available_mm=1000,
        red_W078_candidate_mm=150,black_W060_retained_candidate_mm=280,
        USB_factory_pair_retained_draw_mm=225,
        red_remaining_mm=625,black_remaining_mm=495,
        positive_path_candidate_mm=50+74+150,positive_path_limit_mm=300,
        other_routes_not_accepted=True,selected=False)
    plan['next']='ONE changed-interface BRep screen, all24bank bends and changed supports included. Full80nets/USB/tools still open; no native detail build.'
    plan['source_sha256']={p.relative_to(ROOT).as_posix():sha(p) for p in
        (ledger_path,materials_path,binding_path,ROOT/'hardware/reference/fhac0001zxj-2026-10-02/README.md',Path(__file__))}
    plan.update(worker_seconds=round(time.monotonic()-tick,4),updated_utc=datetime.now(timezone.utc).isoformat())
    return plan

def build_lower_fore():
    p=build();tick=time.monotonic()
    priorpath=OUT/'n01-coupled-pi-bus-checks.json'
    prior=json.loads(priorpath.read_text())
    assert len(prior['contacts'])==11 and not prior['errors']
    ledger=json.loads((OUT/'n01-complete-end-allocation.json').read_text())
    ends={r['role']:r for r in ledger['endpoints']}
    rz=[[0,-1,0],[1,0,0],[0,0,1]]
    station_rotation=[[0,1,0],[1,0,0],[0,0,-1]]
    def pose_to_point(rr,old,new):
        rotated=[sum(a*b for a,b in zip(row,old)) for row in rr]
        return dict(rotation_rows=rr,translation_mm=[b-a for a,b in zip(rotated,new)])
    p['relative_poses']={
        'MAIN':pose_to_point(rz,ends['MAIN.VIN']['point_mm'],[-116,15.8,-2.9052]),
        'WAGO:P_SYS_new':pose_to_point(station_rotation,ends['P_SYS.5']['point_mm'],[-84,4.5,-33.5])}
    p['shifts_mm']={'BUS':[41,0,-18]}
    p['F_PI'].update(centre_mm=[-100,-30,-33.5],rotation_relative_current=rz,
        input_mm=[-100,-4.5,-33.5],output_mm=[-100,-55.5,-33.5])
    p['splice']=dict(centre_mm=[-116,-38.5,-33.5],tip16_mm=[-116,-34.5,-33.5],
        tip18_mm=[-116,-42.5,-33.5],axis=[0,1,0],sleeve_blank_mm=20,
        sleeve_y_mm=[-48.5,-28.5],bare_overlap_y_mm=[-42.5,-34.5],
        jacket_grip16_y_mm=[-59.5,-50.5],jacket_grip18_y_mm=[-25.5,-16.5],
        outer_project_OD_mm=4.2,clip_reservation_mm=[[-120.1,-59.5,-37.6],[-111.9,-16.5,-29.4]],
        grips_outside_sleeve=True,grip_clear_gap_each_mm=2,additional_splice_or_connector=False)
    # Factory input now never passes through the battery plate. Rotate the
    # WHOLE P_SYS, keeping its electrical cavity identities and all other ends.
    r=Route(p['F_PI']['input_mm'],[0,1,0]).line(3).turn([1,0,0],6).line(10)
    w=r.record('W043',1.7);assert math.dist(w['end_mm'],[-84,4.5,-33.5])<1e-8
    w.update(strip_mm=12,nominal_fit_blank_mm=40,raw_required_mm=w['length_mm']+12,
        selected_pre_fuse_limit_mm=50,last_intact_grip_mm=[[-93,4.5,-33.5],[-84,4.5,-33.5]],
        initial3mm_after_molded_relief_is_project_assumption=True,factory_tip_removal_max_mm=8.35)
    # R8 half-turn places the entire sleeve/clip beside, NOT across, F_PI.
    r=Route(p['F_PI']['output_mm'],[0,-1,0]).line(4).turn([-1,0,0],8).turn([0,1,0],8).line(25)
    out=r.record('W077',1.7);assert math.dist(out['end_mm'],p['splice']['tip16_mm'])<1e-8
    out.update(bare_overlap_included_mm=8,factory_tip_removal_max_mm=8.35,
        supplier_shortest_including_tip_mm=84.5,source_draw_required_mm=out['length_mm']+8.35,
        nominal_fit_blank_after_tip_removal_mm=60,old_fit_blank_mm=30)
    vin=[-116,15.8,-2.9052];R=11.1
    r=Route(p['splice']['tip18_mm'],[0,1,0]).line(25).turn([0,0,1],R)
    r.line(vin[2]+12-r.p[2]).turn([0,1,0],R).turn([0,0,-1],R).line(12)
    donor=r.record('W078',1.05);assert math.dist(donor['end_mm'],vin)<1e-8
    donor.update(PCB_insertion_allowance_mm=3,raw_required_mm=donor['length_mm']+3,
        selected_retained_limit_mm=150,selected_fit_blank_mm=140,proposed_fit_blank_mm=140,
        one_K1474_preserved=True)
    p['routes']=[w,out,donor]
    p['necessary_length_gate']=dict(W043=w['raw_required_mm']<=40<=50,
        W077=out['length_mm']<=60 and 60+8.35<=84.5,
        W078=donor['raw_required_mm']<=140<=150,exact_endpoint_match=True,
        full_geometry_and_tools_open=True,ready_for_changed_interface_screen=True)
    p['stock_candidate'].update(red_W078_candidate_mm=140,red_remaining_mm=635,
        positive_path_candidate_mm=40+60+140)
    p['changed_cause']='After one shared rejection, move entire Pi power path to lower fore bay. P_SYS clocked together, MAIN rotated on same fore bridge, full sleeve alongside F_PI. No tall path through battery plate/bank/S0; JPWM restored unchanged. BUS evidence reused unchanged.'
    p['assembly_gates']=['P_SYS down-facing lever access needs a real window in the proposed lower deck; bench preparation does not prove access',
        'MAIN and F_PI lower fore bay require shared rooted removable carrier, not skin support',
        'All four other P_SYS ends and three other MAIN ends transformed together, full downstream routes open',
        'Adopted36leg motion must qualify the new lower fore material before selection']
    p['unchanged_BUS_reuse']=dict(report=priorpath.relative_to(ROOT).as_posix(),sha256=sha(priorpath),
        scope='No BUS-related actual or reservation hits in received trial. Same case pose, nominal mating allowance, both first bends and shared grip; not USB/full cable/actual plug approval.')
    p['source_sha256'][priorpath.relative_to(ROOT).as_posix()]=sha(priorpath)
    p.update(worker_seconds=round(time.monotonic()-tick,4),updated_utc=datetime.now(timezone.utc).isoformat())
    return p

if __name__=='__main__':
    lower='--lower-fore' in sys.argv
    dest=OUT/('n01-coupled-pi-bus-plan-r2.json' if lower else 'n01-coupled-pi-bus-plan.json')
    assert not dest.exists(),'Receive existing result; do not repeat unchanged candidate'
    p=build_lower_fore() if lower else build();dest.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=p['status'],gate=p['necessary_length_gate'],seconds=p['worker_seconds'])))
