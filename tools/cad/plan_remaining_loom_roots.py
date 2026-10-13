"""One current ownership/land contract for ALL remaining leg support roots.

No routes change and no mechanical selection follows from this ledger. The
36 new lands must be allocated together with existing12Hip lands, four real
source-owned extensions, their insulation and current body fanouts.
"""
import hashlib
import json
import math
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def land(identifier, loom, stage, a, b, kind):
    length = math.dist(a, b)
    assert abs(length - 9) < 1e-6, (identifier, length)
    return dict(id=identifier, loom=loom, owner_stage=stage,
                purpose=kind, start_world_mm=a, end_world_mm=b,
                centre_world_mm=[(x+y)/2 for x, y in zip(a, b)],
                axis=[(y-x)/length for x, y in zip(a, b)],
                length_mm=9, installed_independent_bands=1,
                band_head_is_project_reservation=True,
                native_root_qualified=False)


def build(family, extensions, carriers):
    groups = []
    for leg in ('FrontLeft', 'FrontRight', 'RearLeft', 'RearRight'):
        hips = [r for r in family['hips'] if r['physical_leg'] == leg]
        knees = [r for r in family['knees'] if r['physical_leg'] == leg]
        assert len(hips) == 3 and len(knees) == 2
        code = hips[0]['cad_code']
        oldroot = next(r for r in carriers['roots'] if r['leg'] == leg)
        a = oldroot['bond_bounds_world_mm']
        hip_root = [(a[i]+a[i+3])/2 for i in range(3)]
        hip_root[2] = a[5]+2  # Inside the retained4mm cap, not a new case hole.
        joint_lands = []
        source_lands = []
        body_lands = []
        for r in hips:
            # Hip recipes may store analytical circular parts or an expanded
            # curve descriptor. Their unchanged first9mm land is explicit in
            # the common fixed anchor/tangent, independent of representation.
            first = dict(start=r['fixed_anchor_world_mm'],
                         end=[x+9*u for x, u in zip(r['fixed_anchor_world_mm'],
                                                   r['fixed_tangent_world'])])
            body_lands.append(land(r['loom']+'/Hip/Fixed', r['loom'],
                                   'Body', first['start'], first['end'],
                                   'Fixed end of complete Hip flex'))
        for r in knees:
            pose = next(p for p in r['poses'] if p['angle'] == 0)
            first, last = pose['parts'][0], pose['parts'][-1]
            assert first['kind'] == last['kind'] == 'line'
            joint_lands.append(land(r['loom']+'/Knee/Fixed', r['loom'],
                                    'Motion_'+code+'_Hip', first['start'],
                                    first['end'], 'Hip-owned end of Knee flex'))
            source_lands.append(land(r['loom']+'/Knee/Moving', r['loom'],
                                     'Motion_'+code+'_Knee', last['start'],
                                     last['end'], 'Knee-owned end of Knee flex'))
        role3 = next(r for r in hips if r['loom'].endswith('3'))['loom']
        ext = next(r for r in extensions['four_source_owned_extension_candidates']
                   if r['loom'] == role3)
        schedule = ext['staggered_core_schedule']
        p, q = schedule[0]['joint_centre_world_mm'], schedule[-1]['joint_centre_world_mm']
        axis = [(y-x)/44 for x, y in zip(p, q)]
        assert abs(sum(v*v for v in axis)-1) < 1e-7
        for index, centre in enumerate(ext['independent_land_centres_world_mm']):
            source_lands.append(land(role3+'/Splice/'+str(index), role3,
                                     'Motion_'+code+'_Knee',
                                     [x-4.5*u for x, u in zip(centre, axis)],
                                     [x+4.5*u for x, u in zip(centre, axis)],
                                     'Independent jacket land outside staggered sleeve zone'))
        source_rows = [r['source'] for r in family['routes']
                       if r['source']['physical_leg'] == leg
                       and r['source']['moving_saved_stage'] == 'Motion_'+code+'_Knee']
        short = {'FrontLeft':'FL','FrontRight':'FR','RearLeft':'RL','RearRight':'RR'}[leg]
        groups += [
            dict(id=leg+'HipExtension', owner_stage='Motion_'+code+'_Hip',
                 preserved_owner=leg+'SourceCarrier', root_world_mm=hip_root,
                 root_basis='Join the existing actual case cap; preserve its12-land geometry. New branches require changed material gate.',
                 lands=joint_lands),
            dict(id=leg+'KneeCarrier', owner_stage='Motion_'+code+'_Knee',
                 root_case_candidates=['P0_'+s['housing'] for s in source_rows],
                 root_basis='Inspect real planar case patches from these same-stage bodies; no invented screw holes, shaft or PCB attachment.',
                 sleeve_zone=dict(loom=role3, centre_world_mm=ext['centre_world_mm'],
                                  axis=axis, length_project_mm=64,
                                  sleeve_count=3, sleeve_length_project_mm=20,
                                  sleeve_OD_manufacturer_mm=None,
                                  sleeve_SKU=None,
                                  actual_material_check_open=True),
                 lands=source_lands),
            dict(id=leg+'FixedCarrier', owner_stage='Body',
                 preserved_owner=short+'StationFrame',
                 root_basis='Extend current native frame after shared allocation; no old LowPowerStationShoe or duplicate chassis.',
                 lands=body_lands),
        ]
    lands = [r for g in groups for r in g['lands']]
    assert len(groups) == 12 and len(lands) == 36
    assert len({r['id'] for r in lands}) == 36
    assert sum(r['owner_stage'] == 'Body' for r in lands) == 12
    return groups


def run():
    tick = time.monotonic()
    files = [OUT/'leg-source-near-member-plan.json',
             OUT/'leg-extension-budget-plan.json',
             OUT/'complete-source-carriers-plan.json']
    groups = build(*(json.loads(p.read_text()) for p in files))
    result = dict(status='REMAINING36LANDS_COMMON_OWNERSHIP_PLAN_GEOMETRY_OPEN',
                  groups=groups, preserved_Hip_moving_lands=12,
                  new_lands=36, total_joint_and_splice_lands=48,
                  selected=False, native_changed=False, W5_complete=False,
                  physical_pass=False,
                  assembly=['Bench-fit insulation and all unpowered source-owned joins before attaching carrier.',
                            'Attach supports to their actual owner, never across a moving joint. Support wires while fastening.',
                            'Insert complete uncut flex between corresponding two jacket lands, with unchanged R31.5 project reservation.',
                            'Only after full source and body fanout lengths fit, select blanks and stock. No short offcut counted as whole spare.'],
                  open=['Exact roots and shared full material, load paths and native geometry',
                        'Actual sleeve SKU/OD/Cu and delivered case/cable fit, no invented pin cavity order',
                        '36 leg core fanouts and other19 body guides, terminations/cut lengths/stock',
                        'Complete current export/assembly and phase1 selection'],
                  source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files+[Path(__file__)]},
                  worker_seconds=round(time.monotonic()-tick, 3))
    (OUT/'remaining-loom-roots-plan.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','new_lands','total_joint_and_splice_lands','worker_seconds')}))


if __name__ == '__main__':
    run()
