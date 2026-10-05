"""Complete source-servo mount profile, before any replacement clip design.

The first clip wrapped only ZK and intersected SG/XG/MOTOR. Receive all
four actual casing pieces and the neighboring carrier/PCB in one datum.
Do not reroute leads, change P0 or search successive clip positions.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tools/electronics'), str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha, save
from check_main_p0_placement import SavedShapes, prop
from check_p0_leg_geometry import world_shape

BASE = ROOT/'hardware/electronics/full-cat'
OUT = BASE/'w5-source-mount-full-profile-r1'
ENTRY = ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
MAP = BASE/'w5-leg-source-map-r1/interface.json'
PLAN = BASE/'w5-moving-grip-space-plan-r1/plan.json'
REJECTED = BASE/'w5-source-grip-common-r1/checks.json'


def main():
    import FreeCAD as A, Part
    start = datetime.now(timezone.utc)
    assert not (OUT/'plan.json').exists()
    source = json.loads(MAP.read_text(encoding='utf-8'))
    initial = json.loads(PLAN.read_text(encoding='utf-8'))
    rejected = json.loads(REJECTED.read_text(encoding='utf-8'))
    assert rejected['hits'] and not rejected['errors']
    for receipt in (initial, rejected):
        for rel, digest in {**receipt['source_sha256'], **receipt.get('files', {})}.items():
            assert sha(ROOT/rel) == digest, rel
    r = SavedShapes(); objects = r.doc(ENTRY)
    members = {x.get('value') for x in prop(objects['RobotCatAssembly24'], 'Group').findall('.//Link')}
    def bounds(s):
        return [getattr(s.BoundBox, k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    rows = []; sections = []
    for row in source['looms']:
        prior = next(p for p in initial['looms'] if p['loom'] == row['loom'])
        pcbpose = r.placement(objects['Rigid_'+row['pcb']])*r.placement(objects[row['pcb']])
        local = {}; labels = {}
        # These consecutive bodies are accepted only after checking their
        # actual labels, not by assuming every neighboring feature is a case.
        index = int(row['housing'].removeprefix('Part__Feature'))
        names = ['Part__Feature'+str(index+i).zfill(3) for i in range(4)]
        for name, prefix in zip(names, ('ZK_', 'SG-ZIJI', 'XG-ZIJI', 'MOTOR-')):
            label = prop(objects[name], 'Label')[0].get('value')
            assert label.startswith(prefix), (row['loom'], name, label)
            s = world_shape(r, ENTRY, objects, name, members)
            s.Placement = pcbpose.inverse()*s.Placement
            assert s.isValid() and s.Solids
            local[name] = s; labels[name] = label
        full = Part.makeCompound(list(local.values()))
        plane = Part.Face(Part.makePolygon([A.Vector(-3.2,y,z) for y,z in [(-70,-70),(70,-70),(70,70),(-70,70),(-70,-70)]]))
        section = full.section(plane)
        assert section.Edges, row['loom']
        section.Placement = pcbpose*section.Placement; sections.append(section)
        neighbors = []
        for name in [row['pcb'], *[p['part'] for p in prior['carriers']]]:
            s = world_shape(r, ENTRY, objects, name, members)
            s.Placement = pcbpose.inverse()*s.Placement
            neighbors.append(dict(name=name, label=prop(objects[name], 'Label')[0].get('value'), bounds_PCB_mm=bounds(s)))
        hits = [h for h in rejected['hits'] if h['part'].startswith(row['loom'])]
        rows.append(dict(loom=row['loom'], complete_case_parts=[dict(name=n,label=labels[n],bounds_PCB_mm=bounds(s)) for n,s in local.items()],
            complete_case_bounds_PCB_mm=bounds(full), carrier_and_PCB=neighbors,
            rejected_clip_contact_owners=sorted({h['owner'] for h in hits}),
            complete_case_section_x_PCB_mm=-3.2, section_edge_count=len(section.Edges),
            received_source_lead_unchanged=True, existing_P0_fastener_stack_unchanged=True))
    OUT.mkdir(parents=True, exist_ok=True)
    geometry = OUT/'TWELVE_COMPLETE_CASE_SECTIONS_WORLD.brep'
    Part.makeCompound(sections).exportBrep(str(geometry))
    finish = datetime.now(timezone.utc)
    save(OUT/'plan.json', dict(status='COMPLETE_CASE_PROFILES_RECEIVED_CLIP_R1_REJECTED', rows=rows,
        rejected_contact_count=len(rejected['hits']), rejected_pairs=rejected['pairs'],
        rejected_worker_wall_seconds=rejected['worker_wall_seconds'],
        mounting_rules=[
            'Never infer complete servo dimensions from the ZK body alone; include SG, XG and MOTOR.',
            'Hip rear source arms must clear FrontRearCover003. Do not notch frozen P0 to rescue the rejected root.',
            'Plan mechanical retention and strap installation from the complete profile before rebuilding twelve clips.',
            'Use distinct hip/link roots only if their actual neighbor constraints require them; avoid twelve custom variants.',
            'Retain the received straight lead and factory connector; do not count a floating saddle as strain relief.'],
        source_clip_R1_rejected=True, selected=False, P0_unchanged=True, W1_complete=False, W5_complete=False, physical_pass=False,
        started_utc=start.isoformat(), finished_utc=finish.isoformat(), worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={**r.hashes, **{p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),MAP,PLAN,REJECTED]}},
        files={geometry.relative_to(ROOT).as_posix():sha(geometry)}))
    print('FULL_SOURCE_PROFILES', len(rows), 'rejected_contacts', len(rejected['hits']), flush=True)


if __name__ == '__main__':
    main()
