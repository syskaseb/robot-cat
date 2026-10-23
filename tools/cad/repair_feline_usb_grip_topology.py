"""Local topology repair, not service acceptance or a new cable route.

Preserve the rejected receipt. No world rebuild or native master mutation.
"""
import hashlib
import json
import time
import zipfile
from pathlib import Path

import FreeCAD as A
import Part
from scipy.optimize import brentq

import plan_feline_usb_release_grip as prior
from receive_feline_pi_split_service_space import independent
from receive_feline_rrp_shared_height import load
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def strict(shape):
    assert shape.isValid() and len(shape.Solids) == 1
    shape.check(True)


def repair_mobile(mobile):
    # The bad face is a small lens on an existing GPIO R0.85 clearance.
    # Restore that analytic cylinder, not the obsolete entire frame recipe.
    centre = A.Vector(16.521067811865464, -6.690822553420689, 75.7)
    axis = A.Vector(0.7071067811865471, 0.707106781186548, 0)
    candidates = [f for f in mobile.Faces if isinstance(f.Surface, Part.Cylinder)
                  and abs(f.Surface.Radius - .85) < 1e-9
                  and (f.Surface.Center - centre).Length < 1e-7
                  and (f.Surface.Axis - axis).Length < 1e-7]
    assert candidates, 'Pinned GPIO clearance face not found'
    tool = Part.makeCylinder(.85, 5, centre + axis * 13, axis)
    fixed = independent(mobile).fuse(tool).cut(tool)
    strict(fixed)
    return fixed, tool


def build(mobile):
    fixed, tool = repair_mobile(mobile)
    shapes, recipe = prior.build(fixed)
    # removeSplitter created a self-intersection on the valid union.
    shapes['carrier'] = independent(shapes['retained']).fuse(
        independent(shapes['arm'])).fuse(independent(shapes['pad']))
    c = prior.first_curve()
    param = lambda length: brentq(lambda u: c.toShape(0, u).Length-length, 1e-8, .25)
    u1, u2 = param(3.25), param(5.75)
    du = u2-u1
    # One smooth span for the flexible tie envelope. The actual cable and
    # its 9mm pad stay exact. This is a changed tie, NOT inherited clearance.
    b = Part.BezierCurve()
    b.setPoles([c.value(u1), c.value(u1)+c.getD1(u1)[1]*du/3,
                c.value(u2)-c.getD1(u2)[1]*du/3, c.value(u2)])
    edge = b.toShape()
    so, _ = prior.pipe([edge], 5.85)
    si, _ = prior.pipe([edge], 4.65)
    lo, _ = prior.pipe([edge], 3.85)
    li, _ = prior.pipe([edge], 2.65)
    outer = Part.makeBox(40, 40, 31.2, A.Vector(115, 10, 97.5))
    inner = Part.makeBox(40, 40, 30, A.Vector(115, 10, 98.7))
    shapes['band'] = so.common(outer).fuse(lo).cut(si.common(inner).fuse(li))
    for s in shapes.values():
        strict(s)
    recipe.update(GPIO_clearance_radius_mm=.85, GPIO_recut_length_mm=5,
                  no_refine_on_carrier=True, cable_changed=False,
                  band_single_span=True, band_external_clearance_recheck_required=True,
                  sampled_band_centreline_deviation_mm=max(
                      (b.value(i/100)-c.value(u1+du*i/100)).Length for i in range(101)),
                  sampled_deviation_is_not_a_clearance_proof=True)
    return shapes, recipe, fixed, tool


def main():
    start = time.monotonic()
    source = OUT/'n01-Pi-open-cradle-joint.json'
    mobile = load(json.loads(source.read_text()))['mobile']
    shapes, recipe, fixed, tool = build(mobile)
    fresh, _, _, _ = build(mobile)
    comparison = {}
    for name, s in shapes.items():
        restored = independent(s)
        strict(restored)
        differences = [independent(restored).cut(independent(fresh[name])).Volume,
                       independent(fresh[name]).cut(independent(restored)).Volume]
        assert max(differences) < 1e-5, (name, differences)
        comparison[name] = differences
    own = {'band_carrier': shapes['band'].common(shapes['carrier']).Volume,
           'head_carrier': shapes['head'].common(shapes['carrier']).Volume}
    assert max(own.values()) < 1e-7, own
    dest = OUT/'n01-USB-release-grip-topology-repaired.json'
    archive = dest.with_suffix('.breps.zip')
    assert not dest.exists() and not archive.exists()
    geometry = []
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
        for name, shape in {**shapes, 'mobile_repaired': fixed, 'GPIO_recut_tool': tool}.items():
            raw = shape.exportBrepToString().encode()
            entry = str(len(geometry))+'.brep'
            z.writestr(entry, raw)
            geometry.append(dict(name=name, entry=entry, sha256=hashlib.sha256(raw).hexdigest()))
    paths = [Path(__file__), Path(prior.__file__), source,
             ROOT/json.loads(source.read_text())['bundle']]
    result = dict(status='LOCAL_STRICT_BOP_REBUILD_RECEIVED_EXTERNAL_SERVICE_OPEN',
                  geometry=geometry, bundle=archive.relative_to(ROOT).as_posix(),
                  bundle_sha256=sha(archive), source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths},
                  recipe=recipe, fresh_rebuild_difference_mm3=comparison,
                  own_overlap_mm3=own, strict_BOP_all=True,
                  selected=False, N01_complete=False, physical_pass=False,
                  complete_service_received=False,
                  open=['Changed tie external clearance and installation',
                        'USB boot BUS gap0.430475<0.5; service sequence unresolved',
                        'Whole Pi cable parking, tools, lift and full N01'],
                  worker_seconds=round(time.monotonic()-start, 3))
    save_json(dest, result)
    print(json.dumps({k: result[k] for k in ('status', 'worker_seconds', 'own_overlap_mm3')}))


if __name__ == '__main__':
    main()
