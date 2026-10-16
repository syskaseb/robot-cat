"""Bounded prototype service, not an added zero-disconnection requirement.

Keep P_SYS pose and50mm pre-fuse limit. Four explicit P_SYS disconnections,
one removable restraint rail and an unchanged-length parked F_PI lead replace
the impossible request to pull ATO through fixed occupied P_SYS mouths.
This is a dimensioned proposal; whole geometry/parking/assembly are OPEN.
"""
import json,math,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA,BASE


def line(a,b):return dict(kind='line',start=a,end=b,length_mm=math.dist(a,b))


def quarter(a,u,v,r):
    end=[p+r*(x+y) for p,x,y in zip(a,u,v)];k=math.sqrt(.5)
    mid=[p+r*(x*k+y*(1-k)) for p,x,y in zip(a,u,v)]
    return dict(kind='arc',start=a,mid=mid,end=end,radius_mm=r,length_mm=r*math.pi/2)


def prefuse_park(route,input_point,park_y=70.3):
    length=sum(p['length_mm'] for p in route['parts']);r=6.;up=7.
    last=length-up-r*math.pi/2;radial=r+last;dy=input_point[1]-park_y
    assert 0<dy<radial and last>0
    direction=[-math.sqrt(1-(dy/radial)**2),-dy/radial,0]
    start=input_point;high=[start[0],start[1],start[2]+up]
    arc=quarter(high,[0,0,1],direction,r)
    end=[p+last*v for p,v in zip(arc['end'],direction)]
    parts=[line(start,high),arc,line(arc['end'],end)]
    assert abs(sum(p['length_mm'] for p in parts)-length)<1e-8
    assert abs(end[1]-park_y)<1e-8
    strip=route['rail_strip_mm'];assert length+strip<=50
    return dict(parts=parts,radius_mm=route['radius_mm'],guide_mm=length,rail_strip_mm=strip,
        unchanged_factory_blank_mm=length+strip,source_limit_mm=50,actual_cut_mm=None,
        free_end_mm=end,free_end_axis=direction,
        parking_grip_centre_mm=[p-1.5*v for p,v in zip(end,direction)],
        parking_grip_normal=[0,0,1],parking_grip_foot_sign=-1,
        basis='Keep exactly the existing guide length and R6; redistribute .5mm from final straight to initial UP and rotate bend plane. Detached end may change orientation. Not a straight-line teleport or extra pre-fuse splice.')


def proposal(source,ground,source_roots,service):
    ps=source['P_SYS'];g1=ground['G1'];portmap={'W066':'1','W067':'2','W068':'3','W043':'5'}
    assert ps['entry_axis']==[0,1,0] and source['F_PI']['input_source_limit_mm']==50
    old=source['factory_routes']['W043'];p=source['F_PI']['input_mm']
    bad=[ps['ports']['5'][0],2*ps['centre_mm'][1]-ps['ports']['5'][1],ps['ports']['5'][2]]
    impossible=math.dist(p,bad)+old['rail_strip_mm'];assert impossible>50
    parked=prefuse_park(old,p)
    grip_ids={'W066_0_15','W043_P_SYS','W067_P_SYS','W068_P_SYS'}
    grips=[r for r in source_roots['groups'] if r['id'] in grip_ids];assert len(grips)==4
    jaw_y=-62+5.55;shift=math.ceil((jaw_y+1-g1['casing_mm'][1])*2)/2
    assert shift==4.5
    conflicts=service['nominal_vertical_ATO_service_conflicts'];assert len(conflicts)==41
    return dict(status='ONE_PROTOTYPE_BANK_SERVICE_PLAN_NOT_GEOMETRY_ACCEPTANCE',
        decisions=[
            'No zero-disconnection service requirement. Keep bank/current24wire ends and P_SYS/F_PI/4MTA poses.',
            'Before left bank ATO service, de-energized only: label and release exactly four P_SYS terminals1/2/3/5; never disconnect all20WAGO or74 ends.',
            'Cut only W043 end lacing. Keep other three heavy ends in removable rail; remove its two M3 fasteners. Reorient+90degX about bolt row then park inward/down in defined cradles, not on floating wires.',
            'Park short F_PI lead separately with exact unchanged length/R6 and a defined open parking cradle; no pre-fuse extension.',
            'G1+five current ground ends get one calculated4.5mm northward relocation; whole five full curves and independent lands need changed-interface gate.',
            'Keep normal W041 factory/custom geometry. Permanent UP relocation failed shared S1 wire clearance in0b11f99, so do not rerun it or force global source reroutes. Left-bank service also needs explicit release of two W041 joint ends and qualified temporary parking; joint support/levers still OPEN.',
            'Right bank data W011 and AUX VOUT XA03 need explicit changed route or a qualified limited temporary release/parking; W1 must not inherit invalidated geometry.',
            'Reroot only Upper wire arms intersecting the41service map, using all12ATO/jaw reservations; retain twelve new bank load roots and four native Frames unless a real new contact invalidates them.'],
        P_SYS=ps,F_PI=source['F_PI'],bank_positions_changed=False,
        rejected_P_SYS_inward_rotation=dict(reason='Fails necessary50mm pre-fuse blank bound BEFORE CAD',
            hypothetical_end_mm=bad,straight_distance_plus_strip_lower_bound_mm=impossible,limit_mm=50),
        removable_rail=dict(occupied_ports=portmap,source_grip_records=grips,
            base_bounds_mm=[15,61.5,154.0,49,65,156.0],
            plate_stack_raise_mm=.6,
            plate_raise_basis='Keep current factory wireZ151.4/OD4.2 plus.25margin: plate bottom>=153.75. Use154.0; source clamp lands and all WAGO/holder/wire poses remain unchanged.',
            parking_transform=dict(rotation_deg_X=90,pivot_mm=[0,50,155.4],post_translation_mm=[0,-54,-17.6],
                resulting_free_end_points_mm={w:[ps['ports'][port][0],-10,146.6] for w,port in portmap.items() if w!='W043'},
                resulting_heavy_wire_departure=[0,0,1],
                reason='Changed whole parking bay: central inboard Y-10, terminalZ146.6 above P_REAR nominal top143.5. Former parked rail Y40 crossed stationary W041 joint. Keep departures UP, not down through installed holders. Whole curves/access/physical motion still require validation.'),
            source_grips_geometry_retained=True,old_integral_grips_and_pilots_retired_only_after_new_gate=True,
            bolt_centres_mm=[[8,50,152.0],[56,50,152.0]],
            stationary_boss_bounds_mm=[[3.75,45.75,150.0,12.25,54.25,154.0],[51.75,45.75,150.0,60.25,54.25,154.0]],
            structural_root_goals_mm=[[13.2,50,152.0],[50.8,50,152.0]],
            parked_tab_floor_z_mm=133.55,parked_tab_y_mm=[-4.6,-2.6],
            parking_cradle_candidate_y_mm=[-6.6,-.6],parking_cradle_root_paths=None,
            hardware_candidate={'M3x8':2,'M3_nut':2,'M3_washer':2},
            captive_nut_candidate=dict(AF_mm=5.5,height_mm=2.4,trap_AF_mm=5.7,trap_depth_mm=2.6,
                nut_z_mm=[150.1,152.5],roof_mm=1.4,washer_z_mm=[156.0,156.5],
                screw_shank_z_mm=[148.5,156.5],nominal_tip_below_nut_mm=1.6),
            hardware_basis='Project nominal bolt/nut/washer envelopes must be instantiated in whole assembly; dimensions/stack/access/stock not accepted by this plan.',
            heavy_wire_service_slack_extra_guide_allowance_mm=40,
            slack_caution='Allowance is NOT a routed or selected cut. Installed and parked fixed-length curves both required, no stretching or borrowing unknown delivered length.'),
        W043_park=parked,G1_change=dict(translation_mm=[0,shift,0],
            moved_current_port_points={k:[v[0],v[1]+shift,v[2]] for k,v in g1['ports'].items()},
            required_gap_project_mm=1,nominal_jaw_south_boundary_y_mm=jaw_y,
            caveat='Current37x11x22 G1 casing is project envelope; published WAGO dimensions36.7x10.1x21.1 differ. No claim that .05mm reservation overlap was physical supplier interference. Retain conservative envelope until controlled actual model/fit.',
            current_grounds=['W001','W025','W036','W060','W061']),
        whole_service_conflicts=conflicts,
        sequence=['Full robot unpowered, battery/source disconnected by existing P0 procedure. No energized service.',
                  'Access/label four P_SYS levers and two rail screws from assembled prototype; release terminals, loosen only W043 end lace, park three-end rail and W043 separately.',
                  'Execute explicit qualified right-side exceptions if needed; extract selected ATO with defined tool from actual installed holder.',
                  'Reverse parking, restore same labeled cavities, new W043 lace, fastener inspection; continuity/fit/protection acceptance belongs to delivered unpowered phase2.'],
        open=['Whole operating and parked material incl all hardware, tools, 12bank roots, current native Frames and exact fixed-length curves',
              'Rail/boss/tab load paths/native editable cuts and G1/restraint ownership, no hidden removal of arbitrary material',
              'All source prefuse/factory radius/length limits, A2 restoration and stock reconciliation'],
        selected=False,W5_complete=False,M4_complete=False,A2_complete=False,physical_pass=False)


def run():
    tick=time.monotonic();files=[OUT/(n+'.json') for n in ('source-receiving-plan','ground-tree-plan','local-source-retention-roots','local-bank-cradle-space')]
    result=proposal(*[json.loads(f.read_text()) for f in files])
    files.extend([Path(__file__),ROOT/'hardware/reference/power-distribution-2026-09-23/WAGO-221-615.pdf'])
    result.update(source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files},worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'bank-prototype-service-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(ports=4,rail_park_rotation_X_deg=90,prefuse_blank_mm=result['W043_park']['unchanged_factory_blank_mm'],rejected_inward_blank_lower_bound_mm=result['rejected_P_SYS_inward_rotation']['straight_distance_plus_strip_lower_bound_mm'],seconds=result['worker_seconds'])))


if __name__=='__main__':run()
