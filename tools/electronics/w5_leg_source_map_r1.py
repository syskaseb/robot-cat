"""Map all twelve leg looms to saved P0 servo bodies, without solving E6.

Logical FL/FR/RL/RR mean physical front/rear; historical CAD codes do not.
The PCB connector block is source geometry, not a measured cable plug.
Two editable plug datums are prototype reservations, not manufacturer pins.
This preparation neither selects a route nor closes any moving loom.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
sys.path.insert(0, str(ROOT / 'tools/cad'))
from servo_fuse_inputs_r1 import save, sha
from check_main_p0_placement import SavedShapes, prop
from check_p0_leg_geometry import world_shape

OUT = ROOT / 'hardware/electronics/full-cat/w5-leg-source-map-r1'
ENTRY = ROOT / 'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
AXES = ROOT / 'hardware/simulation/p0/e6-leg-compatibility.json'
GRAPH = ROOT / 'hardware/electronics/power-platform/wiring-p0.json'
PHYSICAL = {'FL': 'FrontLeft', 'FR': 'FrontRight', 'RL': 'RearLeft', 'RR': 'RearRight'}
STAGES = ('Hip', 'Knee', 'Ankle')
# Two ports are reserved within the single connector block in source PCB CAD.
# This is deliberately editable and does not infer D/V/G cavity order.
PORT_LOCAL = [[-11.55, -20.5, 5], [-11.55, -20.5, -5]]
EXIT_LOCAL = [0, -1, 0]


def electrical_roles(graph, loom):
    result = {}
    for role in ('D', 'V', 'G'):
        end = loom + '.' + role
        matches = [w for w in graph['wires'] if end in (w['a'], w['b'])]
        assert len(matches) == 1, (loom, role)
        w = matches[0]
        other = w['b'] if w['a'] == end else w['a']
        if role == 'V':
            assert other == 'F_' + loom + '.out', 'Never bypass the individual fuse'
        elif role == 'D':
            assert other == 'D_' + loom[:2] + '.' + str(int(loom[2]) + 1)
        else:
            assert other == loom[:2] + '_G.' + str(int(loom[2]) + 1)
        result[role] = dict(wire=w['id'], servo_end=end, body_end=other)
    return result


def main():
    import FreeCAD as A
    import Part
    begin = datetime.now(timezone.utc)
    assert not (OUT / 'interface.json').exists(), 'Preserve completed source map'
    axes = json.loads(AXES.read_text(encoding='utf-8'))
    assert axes['source_files_sha256'][ENTRY.relative_to(ROOT).as_posix()] == sha(ENTRY)
    graph = json.loads(GRAPH.read_text(encoding='utf-8'))
    reader = SavedShapes()
    objects = reader.doc(ENTRY)
    members = {x.get('value') for x in prop(objects['RobotCatAssembly24'], 'Group').findall('.//Link')}
    assert reader.placement(objects['RobotCatAssembly24']).isIdentity()
    rows, pcbs = [], []
    for leg, physical in PHYSICAL.items():
        for number, stage in enumerate(STAGES, 1):
            axis = next(a for a in axes['axes'] if a['physical_leg'] == physical and a['stage'] == stage)
            # Source assembly groups each drive horn with its PCB and housing.
            # Verify labels before relying on their historical object numbering.
            suffix = int(axis['horn'].removeprefix('Part__Feature'))
            pcb_name = 'Part__Feature%03d' % (suffix - 2)
            case_name = 'Part__Feature%03d' % (suffix - 6)
            label = lambda n: prop(objects[n], 'Label')[0].get('value')
            assert 'PCB-CHAZUO' in label(pcb_name), pcb_name
            assert label(case_name).startswith('ZK_'), case_name
            assert 'HornDisc_Drive' in label(axis['horn']), axis['horn']
            pcb = world_shape(reader, ENTRY, objects, pcb_name, members)
            case = world_shape(reader, ENTRY, objects, case_name, members)
            pose = reader.placement(objects['Rigid_' + pcb_name]) * reader.placement(objects[pcb_name])
            datums = [list(pose.multVec(A.Vector(*p))) for p in PORT_LOCAL]
            exit_axis = list(pose.Rotation.multVec(A.Vector(*EXIT_LOCAL)))
            bounds = lambda s: [getattr(s.BoundBox, k) for k in ('XMin', 'YMin', 'ZMin', 'XMax', 'YMax', 'ZMax')]
            loom = leg + str(number)
            rows.append(dict(loom=loom, physical_leg=physical, cad_code=axis['code'], stage=stage,
                joint=axis['name'], drive_horn=axis['horn'], pcb=pcb_name, housing=case_name,
                pcb_bounds_world_mm=bounds(pcb), housing_bounds_world_mm=bounds(case),
                connector_reservation_world_mm=datums, cable_exit_world_axis=exit_axis,
                connector_datums_provisional=True, pin_cavity_order_known=False,
                electrical=electrical_roles(graph, loom), factory_plugs_installed=1,
                second_servo_socket='NC: no D/V/G daisy chain', route_prepared=False))
            pcbs.append(pcb)
    assert len(rows) == 12 and len({r['pcb'] for r in rows}) == 12
    assert len({e['wire'] for r in rows for e in r['electrical'].values()}) == 36
    OUT.mkdir(parents=True, exist_ok=True)
    geo = OUT / 'PCB_BLOCKS_WORLD.brep'
    Part.makeCompound(pcbs).exportBrep(str(geo))
    end = datetime.now(timezone.utc)
    save(OUT / 'interface.json', dict(status='TWELVE_LEG_LOOMS_SOURCE_MAP_ONLY', looms=rows,
        source_local_port_reservations_mm=PORT_LOCAL, source_local_exit_axis=EXIT_LOCAL,
        source_connector_block_note='Saved PCB single fused block; +/-5 localZ separates two provisional plug centres. No individual cavity or delivered plug is dimensioned by this map.',
        manufacturer_connector_reference=dict(url='https://www.waveshare.com/wiki/ST3215_Servo',
            verified_utc_date='2026-10-04', model='ST3215 12V / Waveshare22414',
            connector='5264/2.54 3P', port_count=2,
            factory_copper_mm2=None, factory_usable_length_mm=None, factory_outer_diameter_mm=None),
        source_sha256={**reader.hashes, **{p.relative_to(ROOT).as_posix(): sha(p) for p in
            (Path(__file__), AXES, GRAPH, ROOT / 'tools/cad/check_main_p0_placement.py', ROOT / 'tools/cad/check_p0_leg_geometry.py')}},
        files={geo.relative_to(ROOT).as_posix(): sha(geo)},
        started_utc=begin.isoformat(), finished_utc=end.isoformat(), worker_wall_seconds=(end-begin).total_seconds(),
        physical_pass=False, W5_complete=False, selected=False, motion_qualified=False))
    print('LEG_SOURCE_MAP', len(rows), 'looms', 36, 'conductors', flush=True)


if __name__ == '__main__':
    main()
