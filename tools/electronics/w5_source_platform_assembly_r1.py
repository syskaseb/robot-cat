"""Receive the completed inlet platform, qualify lower nut access and stock.

Local source inlet only. No whole-source selection or W5 completion claim.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
from servo_fuse_inputs_r1 import save, sha

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'tools/electronics')]
NATIVE = ROOT / 'hardware/electronics/full-cat/w5-source-platform-native-r4/checks.json'
OUT = ROOT / 'hardware/electronics/full-cat/w5-source-platform-assembly-r1'


def main():
    import FreeCAD as A
    import Part
    from w5_r53_owners import installed
    begin = datetime.now(timezone.utc)
    assert not (OUT / 'assembly.json').exists()
    r = json.loads(NATIVE.read_text(encoding='utf-8'))
    assert r['status'] == 'SOURCE_INLET_PLATFORM_LOCAL_COMPLETE_UNSELECTED'
    assert not r['hits'] and not r['errors']
    assert r['closed_STLs'] and r['relocated_reopen']
    assert all(sha(ROOT / k) == v for k, v in {**r['source_sha256'], **r['files']}.items())
    owners, pins, _ = installed(A, Part)
    # Mount the empty platform before W066 wiring; this is an explicit
    # assembly dependency, not a installed-service clearance waiver.
    omitted = [k for k in owners if k.startswith('source-switch-layout-r6/W066_')]
    for k in omitted:
        owners.pop(k)
    shapes_dir = NATIVE.parent
    owners['Platform'] = Part.read(str(shapes_dir / 'Platform_WORLD.brep'))
    owners['Deck'] = Part.read(str(ROOT / 'hardware/cad/studies/w5-source-platform-native-r4/Deck_WORLD.brep'))
    hits, errors, pairs = [], [], 0
    OUT.mkdir(parents=True, exist_ok=True)
    for i, (x, y) in enumerate(r['specification']['bolt_centres']):
        # Project tool-space reserve for a 5.5mm nut socket: nominal OD9.
        # Actual workshop tool envelope is a phase2 check, not supplier data.
        tool = Part.makeCylinder(4.5, 22.1, A.Vector(x, y, 80))
        tool.exportBrep(str(OUT / ('LowerNut' + str(i) + '_ALLOWANCE.brep')))
        for name, shape in owners.items():
            for solid in shape.Solids:
                if not tool.BoundBox.intersect(solid.BoundBox):
                    continue
                pairs += 1
                try:
                    common = tool.common(solid)
                    if common.Volume > 1e-5:
                        hits.append(dict(nut=i, owner=name, mm3=common.Volume))
                except Exception as exc:
                    errors.append(dict(nut=i, owner=name, error=str(exc)))
    fasteners_path = ROOT / 'hardware/manufacturing/one-batch-prototype-r53/fixed-fastener-cart.json'
    stock_path = ROOT / 'hardware/manufacturing/one-batch-prototype-r53/one-order-quantities.json'
    catalog = json.loads(fasteners_path.read_text(encoding='utf-8'))
    stock = json.loads(stock_path.read_text(encoding='utf-8'))
    allocations = []
    for sku, qty, role in [('supplier:BEJMET:SKL000623', 2, 'sourcePlatform:M3x12'),
                           ('supplier:BEJMET:SKL000383', 2, 'sourcePlatform:M3nut'),
                           ('supplier:BEJMET:SKL001158', 4, 'sourcePlatform:M3washer')]:
        row = next(q for q in catalog['rows'] if q['id'] == sku)
        allocations.append(dict(role=role, quantity=qty, supplier_id=sku,
                                dimensions_mm=row['dimensions_mm'], url=row['url'], selected=False))
    tie = next(q for q in stock['lines'] if q['id'] == 'tie:111-02370')
    allocations.append(dict(role='sourcePlatform:T18I', installed=2, service_replacements=2,
                            supplier_sku=tie['supplier_sku'], existing_shared_stock=tie['planning_quantity'],
                            net_stock_delta_not_resolved=True, selected=False))
    pins += [Path(__file__), NATIVE, fasteners_path, stock_path]
    pins += [ROOT / k for k in r['files']]
    end = datetime.now(timezone.utc)
    save(OUT / 'assembly.json', dict(
        status='SOURCE_INLET_LOCAL_ASSEMBLY_READY_UNSELECTED' if not hits and not errors else 'LOWER_NUT_ACCESS_REJECTED',
        hits=hits, errors=errors, pairs=pairs,
        lower_nut_tool_allowance=dict(diameter_mm=9, start_z_mm=80, end_z_mm=102.1,
                                     nominal_project_reserve=True, actual_workshop_tool_verified=False),
        omitted_wire_owners_before_assembly=omitted,
        sequence=['On the bare Deck fit lower washers/nuts and the platform; use M3x12 and upper washers.',
                  'Only then install W066, P_SYS, W043 and the independent body/shared-inlet straps.',
                  'Carrier and Cover fit after the mounting screws. Lever operation precedes strap tightening.',
                  'Disconnect source and cut both straps before later body/inlet removal. Whole source removal remains open.'],
        allocations=allocations,
        stock_rule='Replace obsolete P_SYS/seat strap roles at eventual whole-source selection; do not add old and new variants. No cart change here.',
        prints={'additional_platform': 1, 'replacement_Deck': 1, 'selected': False},
        four_S1_routes_qualified=False, W5_complete=False, selected=False, physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix(): sha(q) for q in dict.fromkeys(pins)},
        files={q.relative_to(ROOT).as_posix(): sha(q) for q in OUT.glob('*.brep')},
        started_utc=begin.isoformat(), finished_utc=end.isoformat(), worker_wall_seconds=(end-begin).total_seconds()))
    print('SOURCE_INLET_ASSEMBLY', pairs, len(hits), len(errors), flush=True)


if __name__ == '__main__':
    main()
