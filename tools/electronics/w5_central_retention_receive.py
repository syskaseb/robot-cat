"""Receive R3 with only four G2 tie-head corrections; no repeated routing.

All previous fixed-owner, support and passage checks remain pinned. Move the
three near-port heads0.5mm axially and BUS head0.35mm south, keeping the
band and wire stations. The fourth correction clears the neighbouring strap.
This is a nominal supplier envelope, not a physical tightening qualification.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import w5_central_retention_layout_r3 as R3
from servo_fuse_inputs_r1 import sha, save

N = R3.N
OUT = N.BASE/'w5-central-retention-layout-r4'
CORRECTIONS = {'XA05Head': [.5,0,0], 'W061_BHead': [.5,0,0],
               'W062Head': [.5,0,0], 'W003Head': [0,-.35,0]}
SHIFTED = tuple(CORRECTIONS)


def main():
    import FreeCAD as A, Part
    from w5_exact_separation import separated
    begin = datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    prior_path = R3.OUT/'checks.json'
    prior = json.loads(prior_path.read_text(encoding='utf-8'))
    assert not prior['errors'] and not prior['received_passage_hits']
    assert all(row['part'] in SHIFTED or row['owner'] in SHIFTED for row in prior['hits']), prior['hits']
    assert all(v > 0 for v in prior['stop_bearing_join_mm3'].values())
    pins = [Path(__file__), Path(R3.__file__), prior_path]
    for rel, digest in {**prior['source_sha256'], **prior['files']}.items():
        p = N.ROOT/rel
        assert sha(p)==digest, rel
        pins.append(p)
    fixed, printed, _, _, _, loaded, _, _ = R3.received.load(A, Part)
    pins += loaded
    central = json.loads(N.CENTRAL.read_text(encoding='utf-8'))
    for wire, row in central['routes'].items():
        p = N.ROOT/row['geometry']
        fixed[wire] = Part.read(str(p))
        pins.append(p)
    for owner in ('SourceDeck', 'SourceCarrier', 'SourceCover', 'SourceEastHood', 'SourceWestHood'):
        p = N.CAD/(owner+'_CANDIDATE_WORLD.brep')
        printed[owner] = Part.read(str(p))
        pins.append(p)
    for owner in N.OWNER_ALIASES:
        printed.pop(owner, None)
    bands = {p.name.removesuffix('_WORLD.brep'): Part.read(str(p)) for p in R3.OUT.glob('*_WORLD.brep')
             if not p.name.endswith(('Stop_WORLD.brep', 'InsulationSeat_WORLD.brep'))}
    supports = {p.name.removesuffix('_WORLD.brep'): Part.read(str(p)) for p in R3.OUT.glob('*_WORLD.brep')
                if p.name.endswith(('Stop_WORLD.brep', 'InsulationSeat_WORLD.brep'))}
    assert (len(bands), len(supports))==(60, 16)
    for name in SHIFTED:
        bands[name].translate(A.Vector(*CORRECTIONS[name]))
    hits, errors, head_joins, pairs = [], [], {}, 0

    def check(label, s, owner, t):
        nonlocal pairs
        if not s.Solids or not t.Solids or not s.BoundBox.intersect(t.BoundBox):
            return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):
                    continue
                pairs += 1
                if separated(a, b):
                    continue
                try:
                    common = a.common(b)
                    if common.Volume > 1e-6:
                        hits.append(dict(part=label, owner=owner, mm3=common.Volume,
                                         bounds_mm=[getattr(common.BoundBox, k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as exc:
                    errors.append(dict(part=label, owner=owner, error=str(exc)))

    suffixes = ('South', 'North', 'Top', 'Bottom', 'Head', 'Left', 'Right')
    group = lambda name: next(name[:-len(s)] for s in suffixes if name.endswith(s))
    OUT.mkdir(parents=True, exist_ok=True)
    geometries = {p.name.removesuffix('_WORLD.brep'): p.relative_to(N.ROOT).as_posix() for p in R3.OUT.glob('*_WORLD.brep')}
    for label in SHIFTED:
        s = bands[label]
        for owner, t in {**fixed, **printed, **supports}.items():
            check(label, s, owner, t)
        for other, t in bands.items():
            if group(label) != group(other):
                check(label, s, other, t)
        top = bands[group(label)+'Top']
        distance = s.distToShape(top)[0]
        # common() of solids can omit lower-dimensional touching faces. These
        # supplier envelopes are orthogonal boxes, so measure their nominal
        # coplanar rectangular interface, additionally verifying actual distance.
        h, t = s.BoundBox, top.BoundBox
        area = max(0, min(h.XMax,t.XMax)-max(h.XMin,t.XMin))*max(0, min(h.YMax,t.YMax)-max(h.YMin,t.YMin))
        assert distance < 1e-7 and abs(h.ZMin-t.ZMax) < 1e-7 and area > 0, label
        head_joins[label] = dict(actual_distance_mm=distance, nominal_planar_area_mm2=area,
                                basis='Coplanar orthogonal box faces; not physical retention strength')
        p = OUT/(label+'_WORLD.brep')
        s.exportBrep(str(p))
        geometries[label] = p.relative_to(N.ROOT).as_posix()
        print('RECEIVED_CENTRAL_HEAD', label, len(hits), len(errors), flush=True)
    finish = datetime.now(timezone.utc)
    result = dict(prior)
    for row in result['endpoint_recipes']:
        row['head_world_shift_mm'] = CORRECTIONS.get(row['key']+'Head', [0,0,0])
    result.update(status='CENTRAL_RETENTION_LAYOUT_REJECTED' if hits or errors else 'CENTRAL_RETENTION_LAYOUT_STATIC_CLEAR_NATIVE_PENDING',
                  hits=hits, errors=errors, pairs=pairs,
                  head_band_closure=head_joins,
                  inherited_layout_receipt=prior_path.relative_to(N.ROOT).as_posix(),
                  unchanged_actual_material_checks_reused=True,
                  world_geometries=geometries,
                  head_world_shifts_mm=CORRECTIONS, shifted_heads=list(SHIFTED),
                  started_utc=begin.isoformat(), finished_utc=finish.isoformat(),
                  worker_wall_seconds=(finish-begin).total_seconds(),
                  source_sha256={p.relative_to(N.ROOT).as_posix(): sha(p) for p in dict.fromkeys(pins)},
                  files={p.relative_to(N.ROOT).as_posix(): sha(p) for p in OUT.glob('*.brep')})
    save(OUT/'checks.json', result)


if __name__ == '__main__':
    main()
