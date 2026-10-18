"""Actual selected-source size/type contract before the next coupled geometry.

Nominal source geometry is NOT manufacturer measurement. A named solder pad
is NOT automatically an insulated jacket exit, even when its position is fixed.
"""
import hashlib
import json
import math
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def compose():
    tick=time.monotonic()
    files={k:OUT/n for k,n in dict(inventory='n01-remaining-selected-inventory.json',
        map='n01-whole-constraint-map.json',ports='n01-twenty-wago-port-contract.json',
        external='n01-extra-circuit-source-ends.json',world='n01-coupled-world-static.json').items()}
    docs={k:json.loads(p.read_text()) for k,p in files.items()}
    templates=[]
    for r in docs['inventory']['parts']:
        if r['placed_current']:continue
        lo,hi=r['bounds_mm'];size=[round(b-a,8) for a,b in zip(lo,hi)]
        item=dict(role=r['role'],name=r['name'],source_bounds_mm=r['bounds_mm'],source_dimensions_XYZ_mm=size,
            source_is_selected_project_reference_not_measurement=True)
        if r['role'] in ('F_HY','F_HP','F_TY'):
            assert size==[51,20.25,22],(r['role'],size)
            item.update(vertical_X_to_minusZ_dimensions_XYZ_mm=[size[2],size[1],size[0]],
                horizontal_X_to_plusY_dimensions_XYZ_mm=[size[1],size[0],size[2]],
                source_factory_exit_local_Z_mm=-1,
                earlier_assumed_15_5mm_cross_section_is_invalid=True)
        if r['role']=='Monitor5015':
            assert size==[41,25,12]
            item['upright_Rx_minus90_dimensions_XYZ_mm']=[size[0],size[2],size[1]]
        templates.append(item)
    assert len(templates)==5
    station_sizes=[]
    for st in docs['ports']['stations']:
        refs=[r for r in docs['map']['parts'] if r['source_record'].get('role')==st['current_group']]
        if not refs:
            station_sizes.append(dict(ref=st['ref'],current_group=st['current_group'],preserve_fixed_source=True,
                extraction='P_SYS belongs to current shared overlay, not a guessed generic station'))
            assert st['ref']=='P_SYS';continue
        assert len(refs)==1,(st['ref'],len(refs));r=refs[0];lo,hi=r['world_bounds_mm'];span=[b-a for a,b in zip(lo,hi)]
        slot=st['prototype']['port_pitch_vector_mm'];pitch=math.sqrt(sum(x*x for x in slot));slot=[x/pitch for x in slot]
        d=st['prototype']['departure_axis']
        size=[round(sum(abs(v[i])*span[i] for i in range(3)),8) for v in (slot,d,[0,0,1])]
        station_sizes.append(dict(ref=st['ref'],name=r['name'],current_group=st['current_group'],
            dimensions_slot_departure_thickness_mm=size,slot_pitch_mm=pitch,
            occupied=len(st['occupied_ports']),source_basis='Actual named source case bounds projected on calibrated proper port frame, broad planning size only'))
    assert len(station_sizes)==20
    interfaces=[]
    for r in docs['external']['current_external_ends']:
        k=r['source_kind'];pad='pad' in k.lower()
        interfaces.append(dict(wire=r['wire'],side=r['side'],physical_interface=r['named_physical_interface'],
            source_kind=k,group=r['current_group'],current_point_mm=r['point_mm'],
            source_point_mm=r['source_point_mm'],departure_axis=r['departure_axis'],
            nominal_OD_project_upper_mm=r['nominal_OD_mm'],minimum_fixed_project_R_mm=r['minimum_fixed_radius_mm'],
            interface_type='KNOWN_NAMED_PAD_NOT_AUTOMATIC_JACKET_MOUTH' if pad else 'RETAINED_SOURCE_INTERFACE_REQUIRES_MATE_CLASSIFICATION',
            jacket_point_and_bare_form_must_be_explicit=pad,
            no_external_U1_pinout_inferred=True,manufacturer_OD_or_R_guaranteed=False))
    PCA=[r for r in interfaces if r['group']=='PWM9685'];assert len(PCA)==7
    assert all(r['source_kind']=='supplier815revCpad' for r in PCA)
    assert sorted(r['nominal_OD_project_upper_mm'] for r in PCA)==[.8,.8,.8,1.4,1.4,1.4,1.4]
    fixednames={'Ref_Material_P0_Part__Feature012_0_0','Ref_Material_P0_Part__Feature020_0_0',
        'Ref_Material_P0_FrameFront20_0_0','Ref_Material_P0_SideRight22_0_0','Ref_Material_P0_SideLeft22_0_0'}
    obstacles=[dict(name=r['name'],world_bounds_mm=r['world_bounds_mm'],kind=r['geometry_category'],
        bounds_are_not_collision_evidence=True) for r in docs['map']['parts'] if r['name'] in fixednames]
    assert len(obstacles)==5
    return dict(status='SELECTED_SOURCE_BOUNDARIES_TYPED_NOT_A_LAYOUT_SELECTION',selected=False,N01_complete=False,physical_pass=False,
        unplaced_component_dimensions=templates,all20_WAGO_station_sizes=station_sizes,
        selected11_external_route_interfaces=interfaces,seven_PCA_solder_pads=PCA,
        preserved_fore_frame_and_side_wall_bounds=obstacles,
        actual_received_world_gate=dict(pairs=docs['world']['pairs'],
            nominal_source_geometry_clearance_failures=len(docs['world']['actual_geometry_clearance_failures']),
            reservation_holds=len(docs['world']['reservation_holds']),worker_seconds=docs['world']['worker_seconds']),
        required_next=['Use actual22x20.25 FHAC cross section, not guessed15.5',
            'PCA7 current positions are supplier815revC solder pads. Allocate bare form/insulation/jacket point/grip, not pipe start on PCB',
            'Use each selected OD/R: PCA3signals0.8OD/R0.5, PCA4logic1.4OD/R6or10 are PROJECT fit data, not supplier guarantees',
            'Full 500mm USB BOTH plug exits and a route/capacity together; do not freeze independent doglegs then discover length failure',
            'Actual P0 side walls reachY49.3396/Z38.52: no vertical51mm fuse centred25 atY43',
            'Head+35 was not selected; preserve baseline pose unless current packaging evidence requires it'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,4))


if __name__=='__main__':
    dest=OUT/'n01-component-boundary-contract.json';assert not dest.exists();p=compose()
    dest.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=p['status'],templates=5,WAGO=20,PCA_solder_pads=7,seconds=p['worker_seconds'])))
