"""Late received U1/power/E2/AUX overlay; no new layout or routing solver.

Keep the immutable246 identities, electrical None contacts and selected stock.
World-space receipts win over earlier local-source coordinates. This closes
the register discrepancy, not shared-corridor capacity or the whole N01 gate.
"""
import copy
import hashlib
import json
import math
import time
import zipfile
from pathlib import Path
import numpy as np
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from compose_feline_received_source_boundaries import current as parent
from compose_feline_integrated_boundaries import apply_updates
from feline_atomic_save import save_json


DEST = OUT/'n01-rooted-current-boundary-overlay.json'


def current():
    base, rows, files = parent()
    packet = json.loads(DEST.read_text())
    for p, h in packet['source_sha256'].items():
        assert sha(ROOT/p) == h, p
    return base, apply_updates(rows, packet['updates']), (*files, DEST)


def compose():
    import FreeCAD as A
    import Part
    tick = time.monotonic()
    base, rows, parents = parent()
    index = {r['id']: r for r in rows}; updates = {}; sources = []
    aliases = {}
    for p in parents:
        if not p.exists():
            assert p.parent == ROOT and (OUT/p.name).exists(), p
            aliases[p.relative_to(ROOT).as_posix()] = (OUT/p.name).relative_to(ROOT).as_posix()
            p = OUT/p.name
        sources.append(p)

    def packet(name):
        path = OUT/(name+'.json'); sources.append(path)
        p = json.loads(path.read_text())
        if p.get('bundle'):
            archive = ROOT/p['bundle']
            assert sha(archive) == p['bundle_sha256'], name
            sources.append(archive)
        assert not p.get('N01_complete') and not p.get('physical_pass')
        return p

    def put(eid, values, receipt):
        r = index[eid]
        v = {k: copy.deepcopy(a) for k, a in values.items()
             if k not in ('id', 'wire', 'portion_id', 'endpoint', 'group')}
        # Clear obsolete geometry-dependent claims instead of inheriting them
        # from a previously rejected position through dict.update().
        v.update(current_restraint_receipt=receipt,
                 routing_boundary_status='CURRENT_ROOTED_RECEIPT_BOUNDARY',
                 pose_status='CURRENT_SOURCE_POSE_RECEIVED_NOT_WHOLE_ROUTE',
                 independent_relief_root_and_shared_neighbors_NOT_received=False,
                 independent_grip_root_and_sampled_leg_motion_received=True,
                 supplier_datum_guaranteed=False)
        if r['point_mm'] is None:
            v['point_mm'] = None
        updates[eid] = {**updates.get(eid, {}), **v}

    coherent = packet('n01-coherent-U1-F0-space-fit')
    east = packet('n01-U1-east-pair-relief')
    carrier = packet('n01-U1-common-carrier')
    with zipfile.ZipFile(ROOT/coherent['bundle']) as z:
        ports = json.loads(z.read(coherent['ports_in_bundle']))
    R = np.asarray(coherent['rotation'], float)
    t = np.asarray(ports[0]['routing_exit_mm'])-R@ports[0]['old_routing_exit_mm']
    point = lambda q: (R@np.asarray(q)+t).tolist()
    axis = lambda q: (R@np.asarray(q)).tolist()
    assert len(ports) == 14
    for port in ports:
        assert np.allclose(point(port['old_routing_exit_mm']), port['routing_exit_mm'], atol=1e-7)
        r = index[port['id']]
        v = {k: point(r[k]) for k in ('point_mm', 'jacket_routing_point_mm') if r.get(k) is not None}
        v.update(routing_exit_mm=port['routing_exit_mm'], routing_exit_axis=port['routing_exit_axis'],
                 source_prefix_length_mm=port['source_prefix_length_mm'],
                 jacket_grip9_mm=[point(q) for q in port['current_grip9_old_mm']],
                 grip_axis=port['routing_exit_axis'], source_coordinate_frame='WORLD_MM',
                 no_external_U1_pinout_inferred=True)
        if r.get('departure_axis') is not None: v['departure_axis'] = axis(r['departure_axis'])
        put(port['id'], v, 'n01-U1-common-carrier.json')
    # The two insulated jackets reflect; their named bare pads do NOT reflect.
    # Curved9 is referenced, never replaced by a fabricated straight9 segment.
    for wire, v in east['new_routes_boundaries'].items():
        eid = wire+'/extra/end'
        put(eid, dict(routing_exit_mm=v['point_mm'], routing_exit_axis=v['axis'],
                      jacket_grip9_mm=None, grip_axis=None,
                      current_full9_curved_grip_receipt='n01-U1-east-pair-relief.json',
                      source_factory_debit_mm=v['factory_debit_mm'],
                      source_prefix_length_mm=next(p['source_prefix_length_mm'] for p in ports if p['id']==eid),
                      source_prefix_length_basis='Insulated-jacket length preserved by received reflection; factory debit also includes retained termination'),
            'n01-U1-east-pair-relief.json')

    power = packet('n01-power30-spatial-source-plan')
    rooted = packet('n01-power42-rooted-joint-space')
    rp = np.asarray(power['power_pose']['rotation'], float)
    centre = np.asarray(power['power_pose']['minimum_penalty_centre_mm'])
    wp = lambda q: (centre+rp@np.asarray(q)).tolist()
    wa = lambda q: (rp@np.asarray(q)).tolist()
    recipes = power['power_plan']['recipes']
    for wire, recipe in recipes.items():
        p = wp(recipe['parts'][0]['start'])
        put(recipe['end_id'], dict(point_mm=p, jacket_routing_point_mm=p,
            routing_exit_mm=wp(recipe['routing_exit_mm']), routing_exit_axis=wa(recipe['routing_exit_axis']),
            grip_axis=None, jacket_grip9_mm=None,
            full9_grip_recipe=recipe['grip'], full9_grip_recipe_frame='POWER_LOCAL_ONCE',
            source_prefix_length_mm=sum(p['length_mm'] for p in recipe['parts']),
            prefix_geometry_owner='PowerFan:wire:'+wire,
            actual_saved_cap_radius_mm=recipe['project_radius_mm'], minimum_R_mm=recipe['R_mm'],
            explicit_same_rail_cavity_swap=power['power_plan']['explicit_same_rail_cavity_swap'],
            physical_cavity_local_mm=power['power_plan']['planned_cavity_points_mm'][wire]),
            'n01-power42-rooted-joint-space.json')
    for wire, eid in [('XA01','XA01/extra/end'), ('XP01','XP01/extra/end')]:
        recipe = recipes[wire]
        p = wp(recipe['routing_exit_mm'])
        put(eid, dict(point_mm=p, jacket_routing_point_mm=p, routing_exit_mm=p,
                      routing_exit_axis=(-np.asarray(wa(recipe['routing_exit_axis']))).tolist(),
                      source_prefix_length_mm=0., full_middle_route_accepted=True,
                      whole_portion_receipt='n01-power42-rooted-joint-space.json'),
            'n01-power42-rooted-joint-space.json')
    auxout = recipes['XA01']['output9']; pwmout = recipes['XP01']
    for eid, parts, tip, direction, grip in [
        ('XA02/extra/start', auxout['parts'], auxout['routing_exit_mm'], auxout['routing_exit_axis'], auxout['grip']),
        ('XP02.source/extra/start', pwmout['output_parts'], pwmout['output_routing_exit_mm'], pwmout['output_routing_axis'], pwmout['output_grip'])]:
        p = wp(parts[0]['start'])
        put(eid, dict(point_mm=p, jacket_routing_point_mm=p, routing_exit_mm=wp(tip),
            routing_exit_axis=wa(direction), source_prefix_length_mm=sum(p['length_mm'] for p in parts),
            full9_grip_recipe=grip, full9_grip_recipe_frame='POWER_LOCAL_ONCE',
            jacket_grip9_mm=None, grip_axis=None), 'n01-power42-rooted-joint-space.json')

    aux = packet('n01-AUX-upper-escape-joint-plan')
    auxjoint = packet('n01-inboard-comb-XA02-joint-plan')
    # Recover the actual rigid transform from all three jacket-mouth datums,
    # not the obsolete board-centre label or a bounding-box origin.
    wires = ('XA02','XA04','XA03')
    ids = ('XA02/extra/end','XA04/extra/start','XA03/extra/start')
    old = np.asarray([aux['recipes'][w]['jacket_parts'][0]['start'] for w in wires])
    new = np.asarray([aux['updates'][eid]['jacket_routing_point_mm'] for eid in ids])
    u, _, vt = np.linalg.svd((old-old.mean(0)).T@(new-new.mean(0)))
    ar = vt.T@u.T
    if np.linalg.det(ar)<0: vt[-1]*=-1; ar=vt.T@u.T
    at = new.mean(0)-ar@old.mean(0)
    assert np.allclose(old@ar.T+at,new,atol=1e-7)
    with zipfile.ZipFile(ROOT/aux['bundle']) as z:
        for wire,eid in zip(wires,ids):
            pad = ar@aux['recipes'][wire]['actual_selected_pad_mm']+at
            g = next(g for g in aux['geometry'] if g['name']=='AuxSource:'+wire+':bare')
            raw = z.read(g['entry']); assert hashlib.sha256(raw).hexdigest()==g['sha256']
            s = Part.Shape(); s.importBrepFromString(raw.decode()); assert s.isValid()
            caps = [f.CenterOfMass for f in s.Faces if isinstance(f.Surface,Part.Plane)
                    and abs(f.Area-math.pi*aux['recipes'][wire]['bare_radius_mm']**2)<1e-5]
            assert len(caps)==2 and min((A.Vector(*pad)-q).Length for q in caps)<1e-6
            v = copy.deepcopy(aux['updates'][eid]);v['point_mm']=pad.tolist()
            put(eid,v,'n01-AUX-upper-escape-joint-received.json')
    sources.append(OUT/'n01-AUX-upper-escape-joint-received.json')
    # XA02 is already whole from its AUX full9 to the full F_AUX output prefix.
    # Its early AUX R15 proposal is replaced by the accepted complete path.
    path = auxjoint['xa02_parts']
    a,b = path[0],path[-1]
    for eid, tip in [('XA02/extra/end',a['start']),('XA02/extra/start',b['end'])]:
        v = dict(routing_exit_mm=tip, full_middle_route_accepted=True,
                 whole_portion_receipt='n01-inboard-comb-XA02-joint-plan.json')
        if eid.endswith('/end'):
            v.update(routing_exit_axis=[0,0,1], source_prefix_length_mm=12.2,
                     prefix_geometry_owners=['AuxSource:XA02:jacket'])
        put(eid,v,'n01-inboard-comb-XA02-joint-plan.json')

    e2 = packet('n01-E2-four-factory-critical-space')
    tray = packet('n01-E2-common-tray')
    with zipfile.ZipFile(ROOT/e2['bundle']) as z:
        plan=json.loads(z.read('plan.json')); lands={}
        for g in e2['geometry']:
            if not g['name'].startswith('JPWMSource:'): continue
            raw=z.read(g['entry']);assert hashlib.sha256(raw).hexdigest()==g['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid()
            lands[g['name'].split(':',1)[1]]=[list(f.CenterOfMass) for f in s.Faces
                if isinstance(f.Surface,Part.Plane)]
    for wire in ('XP02.source','XP03.source','XP02.module','XP03.module'):
        side = 'end' if wire.endswith('source') else 'start'
        if side=='end':
            tip=[126.2999984741211,0,51.5 if wire.startswith('XP02') else 48.5];direction=[1,0,0]
        else:
            cap=plan['module_curved9']['caps'][wire]
            tip=cap['point_mm'];direction=cap['outward_axis']
        caps=lands[wire];assert len(caps)==2
        assert min(np.linalg.norm(np.asarray(c)-tip) for c in caps)<1e-6
        mouth=max(caps,key=lambda c:np.linalg.norm(np.asarray(c)-tip))
        put(wire+'/extra/'+side,dict(routing_exit_mm=tip,routing_exit_axis=direction,
            point_mm=mouth,jacket_routing_point_mm=mouth,source_prefix_length_mm=9.,
            jacket_grip9_mm=None, grip_axis=None, full_middle_route_accepted=True,
            current_full9_curved_grip_receipt='n01-E2-four-factory-critical-space.json',
            whole_portion_receipt='n01-E2-four-factory-critical-space.json',
            whole_factory_required_mm=e2['four_factory_required_mm'][wire],
            factory_minimum_stock_mm=e2['factory_selected_minimum_mm'],
            uncut225_storage_NOT_qualified=True), 'n01-E2-common-tray.json')
    # Mark BOTH boundaries of complete portions. None remains None at F_PWM.
    complete=['XA01/extra','XP01/extra','XA02/extra']+[w+'/extra' for w in plan['routes']]
    for pid in complete:
        for r in rows:
            if r['portion_id']==pid:
                v=updates.setdefault(r['id'],{})
                v.update(full_middle_route_accepted=True,whole_portion_received=True)
    resolved=apply_updates(rows,updates)
    assert len(resolved)==246 and len({r['portion_id'] for r in resolved})==123
    assert [r['id'] for r in rows]==[r['id'] for r in resolved]
    assert all(a['point_mm'] is not None or b['point_mm'] is None for a,b in zip(rows,resolved))
    sources.append(Path(__file__))
    return dict(status='CURRENT_ROOTED246_BOUNDARIES_COMPOSED_SHARED_CORRIDORS_OPEN',
        updates=updates,physical_portions=123,ends=246,complete_late_portions=complete,
        selected_SKUs_changed=False,identities_and_internal_None_preserved=True,
        parent_rows_referenced_not_copied=True,parent_receipt_path_aliases=aliases,
        shared_corridor_capacity_NOT_received=True,
        N01_complete=False,physical_pass=False,native_master_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},
        worker_seconds=round(time.monotonic()-tick,3))


if __name__=='__main__':
    assert not DEST.exists(), 'Receive the existing overlay rather than regenerate'
    result=compose();save_json(DEST,result)
    print(result['status'],len(result['updates']),result['worker_seconds'],flush=True)
