"""Four integral, side-open insulation seats on the received source Carrier.

Check only added material and four nominal supplier-size bands against the
received source family. Clearances are not pull-out/creep certification.
The whole source family remains unselected until roof and removal qualify.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys, math, tempfile, shutil
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
from servo_fuse_inputs_r1 import save, sha
OUT = ROOT / 'hardware/electronics/full-cat/w5-source-grips-native-r1'
CAD = ROOT / 'hardware/cad/studies/w5-source-grips-native-r1'
PARENT = ROOT / 'hardware/cad/studies/w5-source-carrier-native-r1/SourceCarrierPassages.FCStd'
INTENT = ROOT / 'hardware/electronics/full-cat/w5-s1-source-layout-r8/intent.json'
TIE = ROOT / 'hardware/reference/hellermann-11102370-2026-10-04/dimensions.json'
SEATS = {'W064': (-39, 36.2, 157, 0), 'W065': (57.2, 0, 163, 0),
         'W067': (-69, -18.2, 168, 0), 'W068': (-11.1, -18.2, 167, 180)}


def current_owners(A, Part):
    from w5_r53_owners import installed
    owners, pins, omitted = installed(A, Part)
    removed = []
    for key in list(owners):
        if key.startswith(('source-switch-layout-r6/W066_', 'R49/W043_')):
            removed.append(key); owners.pop(key)
    assert len(removed) == 12
    for key in ('P_SYS_design', 'CandidateDeck', 'BankLeft', 'Cover',
                'hardware/cad/studies/pi-complete-native-r2/Carrier_WORLD.brep'):
        assert key in owners; owners.pop(key)
    replacement = {
        'SourceDeck': 'hardware/cad/studies/w5-source-platform-native-r4/Deck_WORLD.brep',
        'SourcePlatform': 'hardware/cad/studies/w5-source-platform-native-r4/Platform_WORLD.brep',
        'SourceBankLeft': 'hardware/cad/studies/w5-source-bank-passage-native-r1/BankLeft_WORLD.brep',
        'SourceCover': 'hardware/cad/studies/w5-source-cover-passages-native-r1/Cover_WORLD.brep',
    }
    for key, rel in replacement.items():
        p = ROOT / rel; owners[key] = Part.read(str(p)); pins.append(p)
    folder = ROOT / 'hardware/electronics/full-cat/w5-source-platform-native-r4'
    for p in folder.glob('*_WORLD.brep'):
        if p.name.startswith(('Platform_', 'DeckBearingPad_')): continue
        owners['SourceInlet/' + p.stem] = Part.read(str(p)); pins.append(p)
    p = ROOT / 'hardware/electronics/full-cat/w5-s1-source-check-r3/CHANGED_BODIES_WORLD.brep'
    owners['P_SYS_received'] = Part.read(str(p)).childShapes()[0]; pins.append(p)
    p = ROOT / 'hardware/electronics/full-cat/w5-s1-source-check-r3/SOURCE_ROUTES_WORLD.brep'
    owners['W066_received'] = Part.read(str(p)).childShapes()[4]; pins.append(p)
    p = ROOT / 'hardware/electronics/full-cat/w5-source-inlet-joint-r2/W043_WORLD.brep'
    owners['W043_received'] = Part.read(str(p)); pins.append(p)
    p = ROOT / 'hardware/electronics/full-cat/w5-s1-source-check-r8/SOURCE_ROUTES_WORLD.brep'
    routes = Part.read(str(p)).childShapes(); pins.append(p)
    for wire, shape in zip(('W064', 'W065', 'W067', 'W068', 'XA01'), routes):
        owners[wire] = shape
    p = p.parent / 'TE_RINGS_WORLD.brep'; pins.append(p)
    for i, s in enumerate(Part.read(str(p)).childShapes()): owners['TE130171/' + str(i)] = s
    owners['S1_reserved_casing'] = Part.makeBox(24, 42, 37, A.Vector(111, 49, 66))
    return owners, pins


def main():
    import FreeCAD as A, Part, MeshPart
    begin = datetime.now(timezone.utc); assert not (OUT / 'checks.json').exists()
    OUT.mkdir(parents=True, exist_ok=True); CAD.mkdir(parents=True, exist_ok=True)
    received = ROOT / 'hardware/electronics/full-cat/w5-source-received-interface-r1/checks.json'
    receipt = json.loads(received.read_text(encoding='utf-8'))
    assert receipt['status'] == 'FIVE_SOURCE_ROUTE_STATIC_INTERFACE_CLEAR_SUPPORTS_SERVICE_OPEN'
    assert all(sha(ROOT / k) == v for k, v in receipt['source_sha256'].items())
    intent = json.loads(INTENT.read_text(encoding='utf-8'))
    tie = json.loads(TIE.read_text(encoding='utf-8'))
    assert [tie['band_width_mm'], tie['band_thickness_mm']] == [2.5, 1.2]
    for row in intent['routes'][:4]:
        x, y, z, angle = SEATS[row['wire']]
        straight = [e for e in row['edges'] if e['kind'] == 'line'
                    and max(abs(e['start'][i] - e['end'][i]) for i in (0, 1)) < 1e-6
                    and abs(e['start'][0] - x) < 1e-6 and abs(e['start'][1] - y) < 1e-6
                    and min(e['start'][2], e['end'][2]) <= z - 3
                    and max(e['start'][2], e['end'][2]) >= z + 3]
        assert len(straight) == 1, row['wire']
    parent = A.openDocument(str(PARENT)); d = A.newDocument('SourceCarrierInsulationGrips')
    target = CAD / 'SourceCarrierInsulationGrips.FCStd'; d.saveAs(str(target))
    parameters = d.addObject('App::VarSet', 'GripParameters')
    parameters.addProperty('App::PropertyLength', 'GrooveAllowance'); parameters.GrooveAllowance = .2
    link = d.addObject('App::Link', 'ReceivedCarrier'); link.setLink(parent.SourceCarrierFinished)
    link.LinkPlacement = parent.SourceCarrierFinished.Placement
    def box(name, b, placement=None):
        q = d.addObject('Part::Box', name)
        q.Length = b[3] - b[0]; q.Width = b[4] - b[1]; q.Height = b[5] - b[2]
        q.Placement.Base = A.Vector(*b[:3])
        if placement: q.Placement = placement.multiply(q.Placement)
        return q
    raw_seats, tools, placements = [], [], {}
    for wire, (x, y, z, angle) in SEATS.items():
        placement = A.Placement(A.Vector(x, y, 0), A.Rotation(A.Vector(0, 0, 1), angle))
        placements[wire] = placement
        raw_seats.append(box(wire + 'OpenSeat', [-5.5, -4, 144, .3, 4, z + 3], placement))
        for sign in (-1, 1):
            lo, hi = ((-3.6, -1.9) if sign < 0 else (1.9, 3.6))
            tools.append(box(wire + 'BandTunnel' + str(sign), [-5.6, lo, z - 1.6, .4, hi, z + 1.6], placement))
    # Exact native cylinders/tori keep the whole curved approach out of the
    # new rising seat, rather than cutting only its straight clamp section.
    for row in intent['routes'][:4]:
        for i, e in enumerate(row['edges']):
            name = row['wire'] + 'Clearance' + str(i)
            if e['kind'] == 'line':
                start = A.Vector(*e['start']); delta = A.Vector(*e['end']) - start
                q = d.addObject('Part::Cylinder', name); q.Height = delta.Length
                q.setExpression('Radius', '2.1 mm + GripParameters.GrooveAllowance')
                q.Placement = A.Placement(start, A.Rotation(A.Vector(0, 0, 1), delta))
            else:
                edge = Part.Arc(A.Vector(*e['start']), A.Vector(*e['mid']), A.Vector(*e['end'])).toShape()
                start = edge.valueAt(edge.FirstParameter); centre = edge.Curve.Center
                normal = centre - start; normal.normalize(); tangent = edge.tangentAt(edge.FirstParameter)
                q = d.addObject('Part::Torus', name); q.Radius1 = e['radius_mm']
                q.setExpression('Radius2', '2.1 mm + GripParameters.GrooveAllowance')
                q.Angle1 = -180; q.Angle2 = 180; q.Angle3 = e['angle_rad'] * 180 / math.pi
                q.Placement = A.Placement(centre, A.Rotation(-normal, tangent, tangent.cross(normal), 'ZXY'))
            tools.append(q)
    raw = d.addObject('Part::MultiFuse', 'CarrierWithFourSeats'); raw.Shapes = [link, *raw_seats]; raw.Refine = False
    cutters = d.addObject('Part::Compound', 'GripAndBandClearances'); cutters.Links = tools
    final = d.addObject('Part::Cut', 'SourceGripsFinished'); final.Base = raw; final.Tool = cutters; final.Refine = False
    d.save(); print('SOURCE_GRIPS_NATIVE_RECOMPUTE', flush=True); d.recompute(); d.save()
    assert final.Shape.isValid() and len(final.Shape.Solids) == 1
    assert not final.Shape.check(True)
    nominal = final.Shape.Volume
    parameters.GrooveAllowance = .3; d.recompute(); assert final.Shape.Volume < nominal
    parameters.GrooveAllowance = .2; d.recompute(); assert abs(final.Shape.Volume - nominal) < 1e-5; d.save()
    added = final.Shape.cut(link.Shape); assert added.Volume > 0
    assert link.Shape.cut(final.Shape).Volume < 1e-5, 'Received Carrier changed beyond added seats'
    for wire, q in zip(SEATS, raw_seats):
        assert q.Shape.common(link.Shape).Volume > 1e-5, (wire, 'No bearing connection')
    bands = {}
    def solid_box(b): return Part.makeBox(b[3]-b[0], b[4]-b[1], b[5]-b[2], A.Vector(*b[:3]))
    for wire, (x, y, z, angle) in SEATS.items():
        front = Part.makeCylinder(3.3, 2.5, A.Vector(0, 0, z - 1.25)).cut(
            Part.makeCylinder(2.1, 2.5, A.Vector(0, 0, z - 1.25)))
        front = front.common(solid_box([0, -3.4, z - 1.3, 3.4, 3.4, z + 1.3]))
        shape = Part.makeCompound([front,
            solid_box([-6.7, -3.3, z - 1.25, 0, -2.1, z + 1.25]),
            solid_box([-6.7, 2.1, z - 1.25, 0, 3.3, z + 1.25]),
            solid_box([-6.7, -3.3, z - 1.25, -5.5, 3.3, z + 1.25]),
            solid_box([-10.2, -2.4, z - 2.25, -6.7, 2.4, z + 2.25])])
        shape.Placement = placements[wire]; bands[wire + '_T18I'] = shape
        shape.exportBrep(str(OUT / (wire + '_T18I_WORLD.brep')))
    owners, pins = current_owners(A, Part)
    hits, errors, pairs = [], [], 0
    def check(label, s, key, t):
        nonlocal pairs
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox): continue
                pairs += 1
                try:
                    c = a.common(b)
                    if c.Volume > 1e-5:
                        bb = c.BoundBox; hits.append(dict(part=label, owner=key, mm3=c.Volume,
                            bounds_mm=[getattr(bb, n) for n in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as exc: errors.append(dict(part=label, owner=key, error=str(exc)))
    for key, t in owners.items(): check('AddedSourceSeats', added, key, t)
    for label, s in bands.items():
        for key, t in owners.items(): check(label, s, key, t)
        check(label, s, 'NewCarrier', final.Shape)
    for i, (label, s) in enumerate(bands.items()):
        for key, t in list(bands.items())[i+1:]: check(label, s, key, t)
    print('SOURCE_GRIPS_CONTACTS', pairs, len(hits), len(errors), flush=True)
    final.Shape.exportBrep(str(CAD / 'Carrier_WORLD.brep')); added.exportBrep(str(OUT / 'ADDED_SEATS_WORLD.brep'))
    dimensions = None; reopened = False; closed = False
    if not hits and not errors:
        mesh = MeshPart.meshFromShape(Shape=final.Shape, LinearDeflection=.08, AngularDeflection=.15, Relative=False)
        assert mesh.isSolid() and mesh.countComponents() == 1; closed = True
        bb = mesh.BoundBox; dimensions = [bb.XLength, bb.YLength, bb.ZLength]; assert max(dimensions) + 10 <= 256
        mesh.translate(-bb.XMin, -bb.YMin, -bb.ZMin); mesh.write(str(CAD / 'Carrier_UNSELECTED_x1.stl'))
    dependencies = list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName) != target))
    for name in list(A.listDocuments()): A.closeDocument(name)
    if not hits and not errors:
        with tempfile.TemporaryDirectory(prefix='robot-cat-source-grips-') as td:
            tmp = Path(td)
            for q in [target, *dependencies]:
                dest = tmp / q.relative_to(ROOT); dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(q, dest)
            restored = A.openDocument(str(tmp / target.relative_to(ROOT))); restored.recompute()
            s = restored.SourceGripsFinished.Shape
            assert s.isValid() and len(s.Solids) == 1 and not s.check(True) and abs(s.Volume - nominal) < 1e-5
            assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values()); reopened = True
    finish = datetime.now(timezone.utc)
    pins += [Path(__file__), PARENT, INTENT, TIE, received, *dependencies]
    files = [*OUT.glob('*.brep'), *CAD.glob('*.FCStd'), *CAD.glob('*.brep'), *CAD.glob('*.stl')]
    save(OUT / 'checks.json', dict(status='SOURCE_INSULATION_GRIPS_REJECTED' if hits or errors else 'FOUR_SOURCE_INSULATION_GRIPS_LOCAL_COMPLETE_UNSELECTED',
        seats=SEATS, pairs=pairs, hits=hits, errors=errors, added_material_mm3=added.Volume,
        groove_allowance_mm=.2, band_tunnels_mm=[1.7,3.2], source_OD_mm=4.2,
        solids=1, strict_BOP_errors=0, received_carrier_material_preserved=True,
        parameter_recompute=True, closed_STL=closed, relocated_reopen=reopened, dimensions_mm=dimensions,
        replacement_Carrier_quantity=1, added_print_quantity=0, new_fasteners=0,
        T18I145_installed_quantity=4, T18I145_service_spares_candidate=4,
        nominal_band_loop_budget_mm=35, minimum_pull_tail_mm=20,
        assembly=['Pass unterminated source wires through Carrier before crimping four TE rings.',
                  'Lay straight insulated segments into side-open seats. Thread four bands through transverse tunnels and hand-tighten; no conductor clamping.',
                  'Cut and replace these bands before removing wires. Complete source/Cover/Carrier removal and upper protection remain open.'],
        physical_tests=['Supplier strap/insulation tolerances, crimp fit, hand-tightening, pull-out and PETG creep in phase2.'],
        roof_protection_complete=False, source_service_complete=False, selected=False, W5_complete=False, physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in dict.fromkeys(pins)},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in files},
        started_utc=begin.isoformat(), finished_utc=finish.isoformat(), worker_wall_seconds=(finish-begin).total_seconds()))
    print('SOURCE_GRIPS_RESULT', len(hits), dimensions, flush=True)


if __name__ == '__main__': main()
