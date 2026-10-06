"""Analytical source-bay recipe. No CAD, selection, purchase or physical PASS.

Separate circuit identity and route arithmetic from expensive Boolean checks.
Coordinates are CP2 world mm. Arc tangents/lengths are computed, not eyeballed.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import time
import sys
import itertools

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/source-bay-plan.json'


def add(a, b):
    return [x+y for x, y in zip(a, b)]


def scale(a, k):
    return [x*k for x in a]


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Route:
    def __init__(self, name, start, tangent, od, radius, allowance, ends):
        self.row = dict(id=name, start_mm=start, OD_mm=od,
                        minimum_radius_mm=radius, termination_allowance_mm=allowance,
                        electrical_ends=ends, segments=[])
        self.p, self.u = start, tangent

    def line(self, length):
        assert length >= 9-1e-8, (self.row['id'], length)
        end = add(self.p, scale(self.u, length))
        self.row['segments'].append(dict(kind='line', start_mm=self.p,
            end_mm=end, tangent=self.u, length_mm=length))
        self.p = end

    def turn(self, tangent, radius):
        assert radius >= self.row['minimum_radius_mm']-1e-8
        theta = math.acos(max(-1, min(1, dot(self.u, tangent))))
        assert 1e-8 < theta < math.pi-1e-8
        v = scale(add(tangent, scale(self.u, -math.cos(theta))), 1/math.sin(theta))
        def point(angle):
            return add(self.p, add(scale(self.u, radius*math.sin(angle)),
                                  scale(v, radius*(1-math.cos(angle)))))
        end, mid = point(theta), point(theta/2)
        self.row['segments'].append(dict(kind='arc', start_mm=self.p,
            mid_mm=mid, end_mm=end, start_tangent=self.u, end_tangent=tangent,
            radius_mm=radius, angle_rad=theta, length_mm=radius*theta))
        self.p, self.u = end, tangent

    def shift(self, displacement, radius):
        h = math.sqrt(dot(displacement, displacement))
        assert abs(dot(self.u, displacement)) < 1e-8 and 0 < h < 2*radius
        theta = math.acos(1-h/(2*radius))
        original = self.u
        oblique = add(scale(original, math.cos(theta)),
                      scale(displacement, math.sin(theta)/h))
        self.turn(oblique, radius)
        self.turn(original, radius)

    def finish(self, target, target_tangent, strip=None):
        assert max(abs(a-b) for a, b in zip(self.p, target)) < 1e-7
        assert abs(dot(self.u, target_tangent)-1) < 1e-8
        row = self.row
        row['end_mm'], row['end_tangent'] = self.p, self.u
        row['centreline_mm'] = sum(s['length_mm'] for s in row['segments'])
        row['nominal_blank_mm'] = row['centreline_mm']+row['termination_allowance_mm']
        row['entry_strip'] = strip
        row['first_straight_mm'] = row['segments'][0]['length_mm']
        row['last_straight_mm'] = row['segments'][-1]['length_mm']
        return row


def main():
    started = datetime.now(timezone.utc); tick = time.monotonic()
    selection_path = ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json'
    selected = json.loads(selection_path.read_text(encoding='utf-8'))
    body_path, stock_path = ROOT/selected['body_harness'], ROOT/selected['local_fuse_stock']
    wires = {r['id']: r for r in json.loads(body_path.read_text(encoding='utf-8'))['conductors']}
    identities = []
    for leg, source_id, output_id, destination in [
            ('FL', 'W041', 'W026', 'P_FRONT.2'), ('FR', 'W042', 'W037', 'P_FRONT.3'),
            ('RL', 'W044', 'W045', 'P_REAR.2'), ('RR', 'W052', 'W053', 'P_REAR.3')]:
        src, out = wires[source_id], wires[output_id]
        assert src['a'] == 'F_'+leg+'.in' and src['b'] == destination
        assert out['a'] == 'F_'+leg+'.out' or out['b'] == 'F_'+leg+'.out'
        identities.append(dict(leg=leg, source=dict(id=source_id, a=src['a'], b=src['b']),
            output=dict(id=output_id, a=out['a'], b=out['b']),
            both_factory_leads_required=True, complete_extension_route_open=True))
    assert wires['W025']['net'] == 'G_SYS' and wires['W036']['net'] == 'G_SYS'
    X, Y, Z = [1, 0, 0], [0, 1, 0], [0, 0, 1]
    nx, ny = scale(X, -1), scale(Y, -1)
    # Reserve the ENTIRE F0 upward service footprint before pipe generation.
    # The unshifted source bay put the G1 rise inside that access column.
    bay_shift = 12
    def shifted(point):
        return add(point, [bay_shift, 0, 0])
    routes = []
    r = Route('W075', shifted([-43.6, 8.5, 52]), ny, 4.5, 10, 5, ['BAT.plus', 'F0.in'])
    r.line(25)
    routes.append(r.finish(shifted([-43.6, -16.5, 52]), ny))
    assert routes[-1]['nominal_blank_mm'] <= 50
    r = Route('W001', shifted([-50.6, 8.5, 52]), ny, 3.1, 12.4, 19, ['BAT.minus', 'G1.1'])
    # The negative cup bends LEFT before F0; a right bend crossed the plus
    # at identical Z. Rise forward of S0, then return below the G1 entry.
    r.line(13); r.turn(nx, 12.4); r.line(bay_shift); r.turn(Z, 12.4)
    # 5.3mm between arcs is not an end restraint: allow only this internal line.
    end = add(r.p, scale(Z, 5.3))
    r.row['segments'].append(dict(kind='line', start_mm=r.p, end_mm=end,
                                  tangent=Z, length_mm=5.3)); r.p = end
    r.turn(ny, 12.4); r.line(17.1); r.turn(X, 12.4); r.turn(Y, 12.4)
    r.turn(Z, 12.4); r.line(9)
    routes.append(r.finish([-50.6, -34, 103.5], Z,
                          dict(start_mm=r.p, direction=Z, length_mm=14, area_mm2=3.31)))
    r = Route('W076_FACTORY', shifted([-43.6, -67.5, 52]), ny, 4.5, 10, 11,
              ['F0.out', 'POST_F0.1'])
    r.line(9); r.turn(X, 10); r.line(15); r.turn(Y, 10); r.line(17)
    routes.append(r.finish(shifted([-8.6, -59.5, 52]), Y,
                          dict(start_mm=r.p, direction=Y, length_mm=11, area_mm2=3.31)))
    assert routes[-1]['nominal_blank_mm'] <= 84.5
    r = Route('W076_EXT', shifted([-1.85, -59.5, 52]), ny, 4.2, 25.2, 26,
              ['POST_F0.2', 'S0.in'])
    r.line(9); r.turn(nx, 25.2); r.line(bay_shift); r.shift([0, 0, 28], 25.2)
    r.turn(Y, 25.2); r.shift([-13, 0, 0], 25.2)
    incoming = [.5, math.sqrt(3)/2, 0]
    tip = add([-89, 16, 80], scale(incoming, -26.9))
    last = (tip[0]-r.p[0]-25.2*(1-math.sqrt(3)/2))/.5
    advance = tip[1]-r.p[1]-12.6-last*math.sqrt(3)/2
    # Deliberately calculate, not round, the short internal link between turns.
    assert advance >= 0 and last >= 9
    end = add(r.p, scale(Y, advance))
    r.row['segments'].append(dict(kind='line', start_mm=r.p, end_mm=end,
        tangent=Y, length_mm=advance)); r.p = end
    r.turn(incoming, 25.2); r.line(last)
    routes.append(r.finish(tip, incoming))
    stock = json.loads(stock_path.read_text(encoding='utf-8'))['LAPP0107001']
    ground = routes[1]
    candidate_lapp = stock['nominal_total_mm']-stock['W001_blank_mm']+ground['nominal_blank_mm']
    report = dict(status='ANALYTICAL_SOURCE_BAY_PLAN_NOT_CAD_VALIDATED', selected=False,
        physical_pass=False, W1_complete=False, W5_complete=False,
        retained_native_sha256=sha(OUT.parent/'WholeCatInterior.FCStd'),
        circuit_identity=identities,
        rejected_diagonal_recipe_identity_error=dict(FL='W025 is FL_G.1 to G1.3, not F_FL.in',
            FR='W036 is FR_G.1 to G1.4, not F_FR.in',
            geometry_contacts_still_rejected=True, old_recipe_disabled=True),
        source_bay=dict(source_bay_shift_x_mm=bay_shift,
            F0=dict(centre_mm=shifted([-43.6, -42, 52]), axis=[0, -1, 0],
            housing_size_mm=[20.25, 51, 22], input_mm=shifted([-43.6, -16.5, 52]),
            output_mm=shifted([-43.6, -67.5, 52]),
            service_bbox_mm=[shifted([-53.725, -67.5, 63]), shifted([-33.475, -16.5, 108])],
            service_reservation_not_supplier_grip=True),
            XT60=dict(plus_cup_mm=shifted([-43.6, 8.5, 52]), minus_cup_mm=shifted([-50.6, 8.5, 52]),
                housing_bbox_mm=[shifted([-55.3, 8.5, 47.4]), shifted([-38.9, 32.4, 56.6])],
                mating_direction=[0, 1, 0], cup_pitch_clocking_provisional=True),
            post_F0=dict(factory_port_mm=shifted([-8.6, -59.5, 52]),
                extension_port_mm=shifted([-1.85, -59.5, 52]), entry_face_normal=[0, -1, 0],
                housing_bbox_mm=[shifted([-14.1, -59.5, 47.5]), shifted([-.1, -40.5, 56.5])],
                extra_installed_quantity_candidate=1, lever_envelope_open=True),
            S0_IN=dict(centre_mm=[-89, 16, 80], tip_mm=tip,
                barrel_direction=scale(incoming, -1), clocking_changed=True),
            retained=['S0 housing', 'S0 OUT/W066', 'S1/all four routes', 'P0/E6', 'ATO bank R47']),
        routes=routes,
        stock=dict(selected_ground_blank_mm=stock['W001_blank_mm'],
            previous_ground_limit_mm=wires['W001']['limit_mm'],
            candidate_ground_nominal_mm=ground['nominal_blank_mm'],
            old_ground_limit_invalidated=True, old_ground_mounts_invalidated=True,
            LAPP_subset_nominal_mm=candidate_lapp, LAPP_stock_candidate_m=stock['candidate_stock_m'],
            subset_not_whole_new_wiring_budget=True,
            factory_W076_available_min_mm=84.5,
            factory_W076_nominal_margin_mm=84.5-routes[2]['nominal_blank_mm'],
            factory_margin_depends_on_provisional_radius_and_exit_datum=True),
        assumptions=['F0 OD4.5/R10/exit datum and XT60 cup pitch7 provisional',
            'S0 stud pitch24/barrel seat height80 and clocking remain provisional',
            '221-412 ports/pitch assumed; actual lever envelope not verified',
            'MTA0100335 L140 is not140per-side or two100mm leads; no dimensioned housing datum'],
        assembly_plan=['Battery absent; install fixed chassis/deck/source supports before wiring',
            'Solder robot XT60 cups with marked polarity; preserve battery factory plug',
            'F0 factory input directly to plus cup, no intervening joint; restrain insulation',
            'Prepare minus/S0 IN protected extension and post-F0 connector before final placement',
            'Keep F0 ATO/factory lead and S0 ring/fastener access independent of MTA banks',
            'Plan mate/release/tool/parking motions before detailed mounts; no live assembly'],
        open=['Actual BRep contacts/enclosure/mating/tool/strain envelopes',
            'Eight complete MTA paths including extensions and restraints, after identity correction',
            'Dimensioned MTA housing/factory leads and WAGO lever evidence',
            'Native supports, joint access, full assembly/removal, stock/E3 and one selection'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in
            [selection_path, body_path, stock_path, OUT.parent/'post-f0-splice-source.json']},
        builder_sha256=sha(Path(__file__)), started_utc=started.isoformat(),
        finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=round(time.monotonic()-tick, 6))
    report['geometry_recipe_sha256'] = hashlib.sha256(json.dumps(
        dict(source_bay=report['source_bay'], routes=report['routes']),
        sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(report['status'])
    for row in routes:
        print(row['id'], 'nominal_mm', round(row['nominal_blank_mm'], 3))
    print('LAPP subset candidate mm', round(candidate_lapp, 3), 'NOT selected')


def cad_preflight():
    """Check only the planned changed source interface; never select CP2."""
    import FreeCAD as A
    import Part
    started = datetime.now(timezone.utc); tick = time.monotonic()
    plan = json.loads(OUT.read_text(encoding='utf-8'))
    assert plan['builder_sha256'] == sha(Path(__file__)), 'Regenerate analytical plan first'
    assert all(sha(ROOT/p) == h for p, h in plan['source_sha256'].items())
    native = OUT.parent/'WholeCatInterior.FCStd'
    assert sha(native) == plan['retained_native_sha256']
    report_path = OUT.parent/'source-bay-preflight.json'
    if report_path.exists():
        prior = json.loads(report_path.read_text(encoding='utf-8'))
        assert prior.get('geometry_recipe_sha256') != plan['geometry_recipe_sha256'], \
            'Already checked geometry: new timestamps/code do not authorize a repeat'
    d = A.openDocument(str(native)); d.recompute()
    changed, bounds, excluded = {}, {}, {}
    def box(name, base, size, rot):
        ob = d.getObject(name) or d.addObject('Part::Box', name)
        ob.Length, ob.Width, ob.Height = size
        ob.Placement = A.Placement(A.Vector(*base), rot); d.recompute()
        changed[name] = ob.Shape.copy()
        reserve = Part.makeBox(*(v+4.8 for v in size), A.Vector(-2.4, -2.4, -2.4))
        reserve.Placement = ob.Placement; bounds[name] = reserve
    c = plan['source_bay']['F0']['centre_mm']
    box('F0_CP2', [c[0]-10.125, c[1]+25.5, c[2]-11],
        [51, 20.25, 22], A.Rotation(A.Vector(0, 0, 1), -90))
    low, high = plan['source_bay']['XT60']['housing_bbox_mm']
    box('XT60_CP2', [high[0], low[1], low[2]],
        [23.9, 16.4, 9.2], A.Rotation(A.Vector(0, 0, 1), 90))
    p = plan['source_bay']['post_F0']['factory_port_mm']
    box('PostF0Splice_CP2', [p[0]-5.5, p[1]+19, p[2]+4.5],
        [14, 19, 9], A.Rotation(A.Vector(1, 0, 0), 180))
    # Confirm both port transforms rather than infer an orientation from bbox.
    joint = d.getObject('PostF0Splice_CP2')
    for local, target in [([5.5, 19, 4.5], p),
            ([12.25, 19, 4.5], plan['source_bay']['post_F0']['extension_port_mm'])]:
        assert (joint.Placement.multVec(A.Vector(*local))-A.Vector(*target)).Length < 1e-7
    ring = d.getObject('S0_ring_IN')
    shape = ring.Shape.copy(); shape.rotate(A.Vector(-89, 16, 80), A.Vector(0, 0, 1), -60)
    ring.Shape = shape; changed[ring.Name] = shape
    excluded[ring.Name] = {'S0_stud_IN', 'S0_washer_IN', 'S0_nut_IN', 'S0_body_CP2', 'W076_EXT_CP2'}
    for row in plan['routes']:
        edges = []
        for segment in row['segments']:
            a, b = A.Vector(*segment['start_mm']), A.Vector(*segment['end_mm'])
            edges.append(Part.makeLine(a, b) if segment['kind'] == 'line' else
                         Part.Arc(a, A.Vector(*segment['mid_mm']), b).toShape())
        for a, b in zip(edges, edges[1:]):
            assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length < 1e-7
            assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length < 1e-7
        path = Part.Wire(edges)
        assert abs(path.Length-row['centreline_mm']) < 1e-7
        def pipe(radius):
            return path.makePipeShell([Part.Wire([Part.makeCircle(radius,
                A.Vector(*row['start_mm']), edges[0].tangentAt(edges[0].FirstParameter))])], True, False)
        # Logical segment ID differs from the preserved native object's name.
        # Replace it, never leave both old and candidate W076 extensions.
        name = 'W076_EXTENSION_CP2' if row['id'] == 'W076_EXT' else row['id']+'_CP2'
        ob = d.getObject(name) or d.addObject('Part::Feature', name)
        ob.Shape = pipe(row['OD_mm']/2); changed[name] = ob.Shape.copy()
        bounds[name] = pipe(row['OD_mm']/2+2.4)
        targets = {'W075': ['XT60_CP2', 'F0_CP2'], 'W001': ['XT60_CP2', 'G1_CP2'],
                   'W076_FACTORY': ['F0_CP2', 'PostF0Splice_CP2'],
                   'W076_EXT': ['PostF0Splice_CP2', 'S0_ring_IN']}[row['id']]
        excluded[name] = set(targets)
        for target in targets:
            excluded.setdefault(target, set()).add(name)
        strip = row['entry_strip']
        if strip:
            sn = row['id']+'_strip_CP2'
            ob = d.getObject(sn) or d.addObject('Part::Feature', sn)
            ob.Shape = Part.makeCylinder(math.sqrt(strip['area_mm2']/math.pi),
                strip['length_mm'], A.Vector(*strip['start_mm']), A.Vector(*strip['direction']))
            changed[sn] = ob.Shape.copy()
            excluded[sn] = set(targets+[name])
            excluded[name].add(sn)
            for target in targets: excluded.setdefault(target, set()).add(sn)
    # Include access as geometry in the SAME gate; not an acceptance claim.
    lo, hi = plan['source_bay']['F0']['service_bbox_mm']
    service = Part.makeBox(*(hi[i]-lo[i] for i in range(3)), A.Vector(*lo))
    changed['F0_upward_access_candidate'] = service
    excluded['F0_upward_access_candidate'] = {'F0_CP2'}
    lo, hi = plan['source_bay']['XT60']['housing_bbox_mm']
    changed['XT60_mate_access_candidate'] = Part.makeBox(hi[0]-lo[0], 25, hi[2]-lo[2],
        A.Vector(lo[0], hi[1], lo[2]))
    excluded['XT60_mate_access_candidate'] = {'XT60_CP2'}
    fixed = {o.Name: o.Shape.copy() for o in d.Objects if 'Shape' in o.PropertiesList
        and o.Name not in changed and o.Name not in ['TorsoEnvelope', 'BatteryNominal']
        and (o.InList and any(parent.Name in ['InteriorReservations', 'HarnessCandidate',
             'S0TerminalCandidates', 'S1TerminalCandidates', 'ServiceReservations'] for parent in o.InList)
             or 'Category' in o.PropertiesList and o.Category != 'electronics')}
    contacts, outside, errors = [], [], []
    tested = 0
    def common(na, a, nb, b):
        nonlocal tested
        if nb in excluded.get(na, set()) or na in excluded.get(nb, set()): return
        if not a.BoundBox.intersect(b.BoundBox): return
        tested += 1
        try:
            assert a.isValid() and b.isValid(), 'Invalid input BRep'
            result = a.common(b)
            assert result.isValid(), 'Invalid common'
            if result.Volume > 1e-5: contacts.append(dict(pair=[na, nb], volume_mm3=result.Volume))
        except Exception as error: errors.append(dict(pair=[na, nb], error=str(error)))
    for name, shape in changed.items():
        assert shape.isValid() and len(shape.Solids) == 1, name
        for other, static in fixed.items(): common(name, shape, other, static)
        if name in bounds:
            try:
                result = bounds[name].cut(d.getObject('TorsoEnvelope').Shape)
                assert result.isValid(), 'Invalid enclosure cut'
                if result.Volume > 1e-5: outside.append(dict(name=name, outside_mm3=result.Volume))
            except Exception as error: errors.append(dict(pair=[name, 'TorsoEnvelope'], error=str(error)))
    for na, nb in itertools.combinations(changed, 2): common(na, changed[na], nb, changed[nb])
    clear = not (contacts or outside or errors)
    report = dict(status='SOURCE_BAY_CANDIDATE_CLEAR_NOT_SELECTED' if clear else 'SOURCE_BAY_REQUIRES_CHANGE',
        selected=False, physical_pass=False, W1_complete=False, W5_complete=False,
        plan_sha256=sha(OUT), original_native_sha256=sha(native),
        geometry_recipe_sha256=plan['geometry_recipe_sha256'], builder_sha256_at_run=sha(Path(__file__)),
        changed_parts=sorted(changed), unchanged_parts_count=len(fixed),
        contacts=contacts, outside=outside, errors=errors, exact_BRep_pairs_tested=tested,
        mating_and_F0_service_reservations_included=True,
        full_MTA_plan_and_mounts_still_open=True, started_utc=started.isoformat(),
        finished_utc=datetime.now(timezone.utc).isoformat(), worker_wall_seconds=round(time.monotonic()-tick, 3))
    if clear:
        candidate = OUT.parent/'SourceBayCandidate.FCStd'
        d.saveAs(str(candidate)); report['candidate_native_sha256'] = sha(candidate)
        report['candidate_reopen_and_parameter_test_pending'] = True
    assert sha(native) == plan['retained_native_sha256']
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    A.closeDocument(d.Name)
    print(report['status'], 'contacts', len(contacts), 'outside', len(outside), 'errors', len(errors), flush=True)


if __name__ == '__main__':
    cad_preflight() if '--cad-preflight' in sys.argv else main()
