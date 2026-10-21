"""Close the saved W020 proposal without repeating its static collision batch.

Only the fixed body portion and 36 sampled leg poses are received. The moving
lead, head/tail motion, native restraints and whole N01 remain separate.
"""
import hashlib
import itertools
import json
import math
import time
import zipfile
from pathlib import Path

import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, SavedShapes, sha
from plan_feline_layout import OUT, MODEL, STAGES, transforms
from compose_feline_rr_two_tier_boundaries import current
from receive_feline_W024_shared_body import solid
from plan_feline_usb_service_bight import outer_margin
from feline_tangent_routes import length, min_radius
from feline_atomic_save import save_json

DEST = OUT/'n01-current-W020-complete-body-plan.json'
STATUS = 'CURRENT_W020_COMPLETE_BODY_AND_SAMPLE36_RECEIVED_NOT_N01'
OWNERS = ['FLArcCuff:W020/body/start',
          'Station:Bank:W020/body/end:wire:W020/body/end']


def receive():
    tick = time.monotonic()
    pf = OUT/'joint-corridor-space-20261021/current-exact-linked-body-preflight.json'
    sf = OUT/'n01-current-exact-linked-whole-static.json'
    plan, static = (json.loads(p.read_text()) for p in (pf, sf))
    pins = {**static['source_sha256'], **plan['source_sha256']}
    for p, h in pins.items():
        assert sha(ROOT/p) == h, p
    recipe = plan['paths']['W020/body']
    assert recipe['status'] == 'SELF_SEPARATION_PROPOSAL_POSITIVE'
    assert min_radius(recipe['parts']) >= 12.4-1e-6
    assert abs(length(recipe['parts'])-recipe['length_mm']) < 1e-6
    checks = {k:v for k,v in static['checks'].items() if k.startswith('CurrentMiddle:W020|')}
    assert len(checks) == 118 and all(r['ok'] for r in checks.values())
    middle = solid(recipe['parts'], recipe['radius_mm'])
    outerfile = OUT/'n01-service-gallery.outer.brep'
    outer = Part.Shape(); outer.read(str(outerfile))
    outside = outer_margin(middle, outer)
    assert outside['ok'], outside
    _, rows, _ = current()
    ends = [next(e for e in rows if e['id'] == eid) for eid in ('W020/body/start','W020/body/end')]
    payload = {'CurrentMiddle:W020': middle.exportBrepToString().encode()}
    retained = []
    sources = [pf, sf, outerfile, Path(__file__), ROOT/'tools/cad/receive_feline_W024_shared_body.py']
    for owner, end, filename in zip(OWNERS, ends, ('n01-FL9-common-arc-rooted-space.json','n01-shared54-current.json')):
        f = OUT/filename; p = json.loads(f.read_text()); archive = ROOT/p['bundle']
        assert sha(archive) == p['bundle_sha256']
        record = next(r for r in p.get('geometry',p.get('parts',[])) if r['name'] == owner)
        with zipfile.ZipFile(archive) as z:
            raw = z.read(record['entry'])
        assert hashlib.sha256(raw).hexdigest() == record['sha256']
        shape = Part.Shape(); shape.importBrepFromString(raw.decode())
        assert shape.isValid() and len(shape.Solids) == 1
        caps = [face for face in shape.Faces if type(face.Surface).__name__ == 'Plane'
                and (face.CenterOfMass-A.Vector(*end['routing_exit_mm'])).Length < 1e-6]
        assert len(caps) == 1 and abs(caps[0].Area-math.pi*recipe['radius_mm']**2) < 1e-5
        L = end.get('source_prefix_length_mm')
        if L is None:
            L = end['current_prefix_entry_mm'] + end['received_prefix_R_mm']*math.radians(end['current_prefix_sweep_degrees'])
        assert abs(shape.Volume/(math.pi*recipe['radius_mm']**2)-L) < 1e-4
        old = checks['CurrentMiddle:W020|'+owner]
        assert old['common_mm3'] < 1e-5 and old['gap_mm'] < 1e-6
        assert middle.distToShape(shape)[0] < 1e-6
        payload[owner] = raw; retained.append(L); sources.extend((f,archive))
    # Both endpoints must remain the current physical caps, not remembered rows.
    for part, field, end in ((recipe['parts'][0],'start',ends[0]), (recipe['parts'][-1],'end',ends[1])):
        assert np.allclose(part[field], end['routing_exit_mm'], atol=1e-7, rtol=0)
    # Conservative transformed boxes can PROVE separation, never contact.
    # Recreate the exact same 36-pose membership from pinned saved source parts.
    mf = OUT/'motion-layout.json'
    af = ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    motion = json.loads(mf.read_text()); axes = json.loads(af.read_text())['axes']
    reader = SavedShapes(); maximum_z = -math.inf; count = 0; worst = None
    for code, groups in motion['membership'].items():
        aa = [next(a for a in axes if a['code'] == code and a['stage'] == stage) for stage in STAGES]
        poses = [transforms(aa,p['legs'][code]['angles_delta_degrees']) for p in motion['poses'][:36]]
        assert len(poses) == 36
        for stage, names in groups.items():
            for name in names:
                shape = reader.shape(MODEL,name); bb = shape.BoundBox
                assert shape.isValid() and shape.Solids, name
                corners = np.array(list(itertools.product((bb.XMin,bb.XMax),(bb.YMin,bb.YMax),(bb.ZMin,bb.ZMax))))
                for i, pose in enumerate(poses):
                    r,t = pose[STAGES.index(stage)]; z = float((corners@r.T+t)[:,2].max()); count += 1
                    if z > maximum_z:
                        maximum_z = z; worst = dict(name=name,pose=i)
    gap = middle.BoundBox.ZMin-maximum_z
    assert count == 3888 and gap >= 1.25-1e-6, (count,gap,worst)
    sources.extend((mf,af,MODEL,ROOT/'tools/cad/plan_feline_layout.py',ROOT/'tools/cad/check_main_p0_placement.py'))
    pins.update(reader.hashes)
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in sources})
    archive = DEST.with_suffix('.breps.zip'); geometry = []
    assert not DEST.exists() and not archive.exists(), 'Do not overwrite an existing receipt'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name,raw in payload.items():
            entry = str(len(geometry))+'.brep'; z.writestr(entry,raw)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result = dict(status=STATUS,portion='W020/body',middle_recipe=recipe,
        source_prefix_owners=OWNERS,
        current_boundaries=[dict(id=e['id'],point_mm=e['routing_exit_mm'],axis=e['routing_exit_axis'],retained_prefix_length_mm=L) for e,L in zip(ends,retained)],
        complete_body_length_mm=length(recipe['parts'])+sum(retained),middle_length_mm=length(recipe['parts']),
        checks=checks,outer=outside,motion_actors_covered=count,sampled_poses=36,
        motion_vertical_lower_bound_mm=gap,motion_maximum_z_mm=maximum_z,motion_worst_bound=worst,
        motion_proof='Whole middle above every transformed source bounding box; separation lower bound, not continuous-motion approval. Unchanged prefixes retain their prior receipts.',
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),source_sha256=pins,
        preserved_other_candidate_failures=static['failures'],
        whole900_moving_side_head_tail_motion_stock_and_complete123_OPEN=True,
        native_changed=False,selected_SKUs_changed=False,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(DEST,result)
    return result


if __name__ == '__main__':
    p = receive()
    print(json.dumps({k:p[k] for k in ('status','complete_body_length_mm','outer','motion_vertical_lower_bound_mm','worker_seconds')}),flush=True)
