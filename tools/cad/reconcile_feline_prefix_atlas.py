"""Receive named existing prefix exits before any new curve construction.

An electrical mouth, owned straight routing land and complete prefix exit are
different datums. Never choose the nearest cap, thin a selected conductor, or
turn an open accounting point into a manufacturer pin. This atlas changes no
geometry or upstream register and does not certify routes or N01.
"""
import collections, gzip, hashlib, json, math, os, time, zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from compose_feline_output_boundaries import current
from feline_selected_material_contract import load as profiles


def cap_matches(caps, point, axis):
    if point is None or axis is None:
        return []
    q, d = A.Vector(*point), A.Vector(*axis)
    return [r for r in caps if (q-A.Vector(*r['point_mm'])).Length < 1e-4
            and d.dot(A.Vector(*r['outward_axis'])) > 1-1e-6]


def main():
    tick = time.monotonic()
    base, ends, files = current()
    contract, pf, bf = profiles()
    sf = OUT/'n01-whole-terminal-escape.json'
    screen = json.loads(sf.read_text())
    rf = ROOT/screen['rows']
    assert sha(rf) == screen['rows_sha256']
    screened = json.loads(gzip.decompress(rf.read_bytes()))
    # Changed method after two failed assumptions: read only the thirteen
    # explicitly named current core lands, not another whole-world build.
    cf = OUT/'n01-six-source-current-core.json'
    core = json.loads(cf.read_text())
    archive = ROOT/core['bundle']
    assert sha(archive) == core['bundle_sha256']
    register_file = OUT/'n01-current-246-end-register.json'
    register = json.loads(register_file.read_text())
    assert register['source_sha256'][cf.relative_to(ROOT).as_posix()] == sha(cf)
    parts = {}
    with zipfile.ZipFile(archive) as z:
        for r in core['parts']:
            if not r['name'].startswith('End:'):
                continue
            raw = z.read(r['entry'])
            assert hashlib.sha256(raw).hexdigest() == r['sha256']
            s = Part.Shape(); s.importBrepFromString(raw.decode())
            parts[r['name']] = s
    assert len(parts) == 13
    pins = {}
    caps = []
    for owner, shape in parts.items():
        assert shape.Solids, owner
        found = []
        for f in shape.Faces:
            if not isinstance(f.Surface, Part.Plane) or len(f.Edges) != 1:
                continue
            c = f.Edges[0].Curve
            if not isinstance(c, Part.Circle) or abs(f.Area-math.pi*c.Radius**2) > 1e-4:
                continue
            q = f.CenterOfMass
            u, U, v, V = f.ParameterRange
            n = f.normalAt((u+U)/2, (v+V)/2)
            if not shape.isInside(q-n*.05, 1e-7, False):
                n = -n
            assert shape.isInside(q-n*.05, 1e-7, False), owner
            found.append(dict(owner=owner, point_mm=list(q), outward_axis=list(n),
                              actual_project_radius_mm=float(c.Radius)))
        if found:
            assert shape.isValid() and all(s.isValid() for s in shape.Solids), owner
            caps.extend(found)
    rows, updates = {}, {}
    for e in ends:
        if screened[e['id']]['status'] != 'ACTUAL_CAP_OR_SELECTED_PROFILE_OPEN':
            continue
        radius = contract['portions'][e['portion_id']]['project_radius_mm']
        hits = cap_matches(caps, e.get('routing_exit_mm'), e.get('routing_exit_axis'))
        r = dict(group=e['group'], endpoint=e['endpoint'],
                 current_boundary_status=e['routing_boundary_status'],
                 current_exact_cap_matches=hits, required_radius_mm=radius,
                 status='NO_CURRENT_OUTWARD_CAP_ALLOCATION_OPEN')
        if hits:
            r['status'] = ('ACTUAL_CURRENT_CAP_RECEIVED_NEEDS_CHANGED_SCREEN' if
                any(abs(h['actual_project_radius_mm']-radius) < 1e-5 for h in hits)
                else 'ACTUAL_CAP_PROFILE_CONFLICT_NOT_NEW_GEOMETRY')
        # This is an explicit existing nine-mm OWNED straight land, not a
        # closest-cap search or a second nine-mm length added to a wire.
        owner = 'End:'+e['id']
        if e['group'].startswith('NineWireCuff') and owner not in parts:
            r['status'] = 'KINEMATIC_CUFF_BOUNDARY_NO_OWNED_PREFIX_SOLID'
        elif e['group'].startswith('NineWireCuff'):
            assert e['point_mm'] is not None and e['departure_axis'] is not None
            p, d = A.Vector(*e['point_mm']), A.Vector(*e['departure_axis'])
            q = p+d*9
            owned = [c for c in caps if c['owner'] == owner]
            inlet = cap_matches(owned, list(p), list(-d))
            outlet = cap_matches(owned, list(q), list(d))
            assert len(inlet) == len(outlet) == 1, e['id']
            actual = outlet[0]['actual_project_radius_mm']
            assert abs(inlet[0]['actual_project_radius_mm']-actual) < 1e-5
            assert abs(parts[owner].Volume-math.pi*actual**2*9) < 1e-4
            compatible = actual >= radius-1e-5
            same_profile = abs(actual-radius) < 1e-5
            updates[e['id']] = dict(routing_exit_mm=list(q), routing_exit_axis=list(d),
                prefix_geometry_owner=owner, source_prefix_length_mm=9,
                routing_boundary_status='CURRENT_OWNED_CUFF_NINE_MM_OUTLET_VERIFIED',
                fixed_kinematic_boundary_mm=list(p), moving_boundary_not_relocated=True,
                complete_individual_termination_relief_NOT_inferred=True,
                actual_saved_cap_radius_mm=actual, selected_profile_matches=same_profile,
                selected_profile_enclosed=compatible,
                full_middle_route_accepted=False, supplier_datum_guaranteed=False)
            r.update(status=('OWNED_CUFF_INLET_TO_EXISTING_OUTLET_RECONCILED' if same_profile
                             else 'CONSERVATIVE_CUFF_CAPACITY_OUTLET_SMALLER_SELECTED_WIRE' if compatible
                             else 'OWNED_CUFF_OUTLET_RECEIVED_PROFILE_CONFLICT_OPEN'),
                     inlet=inlet[0], outlet=outlet[0])
        rows[e['id']] = r
    assert len(rows) == 91 and len(updates) == 9
    assert len(base['portions']) == 123 and len(ends) == 246
    sources = (*files, pf, bf, sf, rf, cf, register_file, archive, Path(__file__))
    pins.update({p.relative_to(ROOT).as_posix(): sha(p) for p in sources})
    result = dict(status='EXISTING_PREFIX_ATLAS_RECEIVED_REMAINING_ALLOCATIONS_OPEN',
        rows=rows, updates=updates, summary=dict(collections.Counter(r['status'] for r in rows.values())),
        source_sha256=pins, actual_jacket_caps=len(caps), native_changed=False,
        existing_geometry_unchanged=True, electrical_identities_unchanged=True,
        selected_wire_not_shrunk=True, N01_complete=False, physical_pass=False,
        source_screen_is_necessary_only_and_NOT_route_acceptance=True,
        worker_seconds=round(time.monotonic()-tick, 3))
    save_json(OUT/'n01-current-prefix-atlas.json', result)
    print(json.dumps(dict(summary=result['summary'], seconds=result['worker_seconds'],
                          cuff_outlets=len(updates), caps=len(caps))), flush=True)


if __name__ == '__main__':
    print('WORKER_PID', os.getpid(), flush=True)
    main()
