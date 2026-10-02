"""One continuous provisional lever sector, not the old broad access box.

WAGO installation pictures establish the opening direction only. Pivot,
radius, width and angle below are PROJECT allowances, not measured hinge
dimensions. Keep contacts; never convert this into physical qualification.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'tools/electronics')]
from servo_fuse_inputs_r1 import save, sha
OUT = ROOT / 'hardware/electronics/full-cat/servo-fuse-wago-access-r2'


def main():
    import FreeCAD as A
    import Part
    import servo_fuse_side_bank_r10 as layout
    begin = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT / 'checks.json').exists(), 'Preserve previous results'
    assumptions = dict(pivot_y_from_block_center_toward_inside_mm=4,
                       pivot_z_mm=117.2, sector_radius_mm=14,
                       sector_width_mm=5, angle_deg=110,
                       basis='Project nominal opening envelope, not WAGO hinge measurements',
                       finger_approach_qualified=False)
    save(OUT / 'intent.json', dict(started_utc=begin.isoformat(), selected=False,
         physical_pass=False, assumptions=assumptions,
         supplier_reference='hardware/reference/wago-221415-access-2026-10-02/221-415-WAGO-2021.pdf',
         supplier_reference_scope='Page1 closed product; page6 family installation direction only. No dimensioned open lever.',
         old_broad_probe='servo-fuse-bank-service-r1/checks.json remains a recorded access conflict; not erased.'))
    print('LOAD_CURRENT_OWNERS', flush=True)
    owners, hashes, _ = layout.current_owners()

    def load(p):
        hashes[p.relative_to(ROOT).as_posix()] = sha(p)
        return Part.read(str(p))

    for n in list(owners):
        if any(s in n for s in ('/servo-fuse-bank-restraints-r2/', '/servo-fuse-bank-restraints-fit-r2/')):
            del owners[n]
    owners['R49Deck'] = load(ROOT / 'hardware/cad/studies/servo-fuse-deck-native-r1/Deck_WORLD.brep')
    for p in (ROOT / 'hardware/cad/studies/servo-fuse-bank-clip-access-r1').glob('*_WORLD.brep'):
        owners[p.stem] = load(p)
    # Current inputs, terminals and holder bodies are absent from the inherited
    # body-only collection. Add the installed candidate, not temporary tools.
    for p in (ROOT / 'hardware/electronics/full-cat/servo-fuse-side-bank-r11').glob('*_DESIGN.brep'):
        if p.stem.startswith(('W0', 'F_')):
            owners['R11/' + p.stem] = load(p)
    for folder, pattern in [('servo-fuse-bank-restraints-r3', '*_TIE_DESIGN.brep'),
                            ('servo-fuse-bank-input-fit-r1', '*_TIE_HEAD_RESERVE.brep')]:
        for p in (ROOT / 'hardware/electronics/full-cat' / folder).glob(pattern):
            owners[folder + '/' + p.stem] = load(p)
    mapping_path = ROOT / 'hardware/electronics/full-cat/servo-fuse-wago-map-r1/interface.json'
    hashes[mapping_path.relative_to(ROOT).as_posix()] = sha(mapping_path)
    mapping = json.loads(mapping_path.read_text(encoding='utf-8'))
    pdf = ROOT / 'hardware/reference/wago-221415-access-2026-10-02/221-415-WAGO-2021.pdf'
    hashes[pdf.relative_to(ROOT).as_posix()] = sha(pdf)
    hits, errors, ports = [], [], []
    pairs = 0
    for block in mapping['blocks']:
        side = 1 if block['center_mm'][1] > 0 else -1
        for port in block['ports']:
            label = block['id'] + '_' + str(port['project_slot'])
            x = port['entry_mm'][0]
            pivot = A.Vector(x - 2.5, block['center_mm'][1] - side * 4, 117.2)
            def point(angle):
                return pivot + A.Vector(0, side * 14 * math.cos(angle), 14 * math.sin(angle))
            a, mid, b = point(0), point(math.radians(55)), point(math.radians(110))
            face = Part.Face(Part.Wire([Part.makeLine(pivot, a), Part.Arc(a, mid, b).toShape(), Part.makeLine(b, pivot)]))
            sweep = face.extrude(A.Vector(5, 0, 0))
            assert sweep.isValid() and len(sweep.Solids) == 1
            sweep.exportBrep(str(OUT / (label + '_LEVER_SECTOR.brep')))
            local_hits = []
            print('SECTOR ' + label, flush=True)
            for owner, shape in owners.items():
                if owner == block['id'] + '_design':
                    continue  # intentional hinge-to-own-body contact only
                if not sweep.BoundBox.intersect(shape.BoundBox):
                    continue
                pairs += 1
                try:
                    common = sweep.common(shape)
                    if common.Volume > 1e-5:
                        row = dict(port=label, owner=owner, hit_mm3=common.Volume,
                                   bounds_mm=[getattr(common.BoundBox, k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')])
                        hits.append(row); local_hits.append(row)
                        common.exportBrep(str(OUT / (label + '_HIT_' + str(len(hits)) + '.brep')))
                except Exception as exc:
                    errors.append(dict(port=label, owner=owner, error=str(exc)))
            ports.append(dict(port=label, wire=port['wire_id'], endpoint=port['endpoint'],
                              candidate_sector_clear=not local_hits,
                              nominal_sector_continuous=True, hinge_measured=False))
    end = datetime.now(timezone.utc)
    save(OUT / 'checks.json', dict(status='PROVISIONAL_LEVER_SECTOR_CONFLICTS' if hits or errors else 'PROVISIONAL_LEVER_SECTORS_CLEAR_APPROACH_OPEN',
         selected=False, physical_pass=False, W5_complete=False,
         assumptions=assumptions, ports=ports, hits=hits, errors=errors, pairs=pairs,
         no_obstacle_waiver=True, installed_candidate_included=True,
         actual_lever_motion_qualified=False, finger_approach_qualified=False,
         next='Resolve actual contacts with a single assembly order or changed interface. Do not claim in-situ access while a crossing wire is installed.',
         source_sha256=hashes, script_sha256=sha(Path(__file__)),
         started_utc=begin.isoformat(), finished_utc=end.isoformat(), worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(ports=len(ports), hits=hits, errors=errors, pairs=pairs)), flush=True)


if __name__ == '__main__':
    main()
