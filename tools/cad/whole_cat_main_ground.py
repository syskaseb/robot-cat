"""One analytical MAIN ground path, then an affected-material gate.

Current named datums only; no invented USB or solder-splice endpoint.
The saved candidate is not a full harness or selection. No source overwrite.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import time

from whole_cat_source_bay_plan import Route

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'hardware/cad/studies/whole-cat-packaging/cp2'
MOUNT = BASE/'neck-support/main-mount-sequence'
OUT = BASE/'neck-support/main-ground'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def recipe(start, end):
    # Two equal bends: +Z -> horizontal transfer -> +Z into G1 underside.
    delta = [end[i]-start[i] for i in range(2)]
    h = math.hypot(*delta)
    radius = 18  # Inherited K1474 project bend allowance, not supplier rating.
    first = 9
    last = end[2]-start[2]-first-2*radius
    assert h-2*radius >= 9 and last >= 9
    direction = [delta[0]/h, delta[1]/h, 0]
    r = Route('W060', start, [0,0,1], 3, radius, 8+14,
              ['MAIN.GND','G1.2'])
    r.line(first); r.turn(direction, radius); r.line(h-2*radius)
    r.turn([0,0,1], radius); r.line(last)
    return r.finish(end, [0,0,1], 14)


def main():
    import FreeCAD as A
    import Part
    assert not OUT.exists(), 'Preserve proof; no unchanged rerun'
    started = datetime.now(timezone.utc).isoformat(); tick = time.monotonic()
    paths = [BASE/'BoardDatumCandidate.FCStd', BASE/'whole-harness-board-plan.json',
             MOUNT/'NeckMainMount.FCStd', MOUNT/'checks.json', Path(__file__),
             ROOT/'tools/cad/whole_cat_source_bay_plan.py',
             ROOT/'hardware/electronics/full-cat/pi-interface-final-r2/wiring-card.json']
    pins = {p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    mount = json.loads(paths[3].read_text(encoding='utf-8'))
    assert sha(paths[2]) == mount['native_sha256']
    graph = json.loads(paths[1].read_text(encoding='utf-8'))
    row = next(w for w in graph['body_conductors'] if w['id']=='W060')
    endpoint = next(e for e in row['ends'] if e['role']=='G1.2')
    assert math.dist(endpoint['departure'], [0,0,-1]) < 1e-7
    start = next(e['point_mm'] for e in mount['affected_main_ends'] if e['id']=='W060')
    route = recipe(start, endpoint['point_mm'])
    report = dict(status='PENDING_AFFECTED_MATERIAL_GATE', selected=False,
                  W5_complete=False, physical_pass=False, source_sha256=pins,
                  recipe=route, datum_basis=[
                      'MAIN inherited prototype pad, NOT delivered4853 pin',
                      endpoint['basis']],
                  OD_and_radius_basis='K1474 project OD3/R18, inherited Pi recipe; actual cable phase2',
                  termination='MAIN8mm blank/trim at pad; G1 fresh untinned12..14mm, no tinned WAGO entry',
                  length_basis='Nominal centreline+8mm MAIN+14mm G1; trim only after phase2 dry fit',
                  native_restraints_complete=False,
                  G1_lever_and_wire_insertion_qualified=False,
                  other_MAIN_routes='W078 splice and W079/W080 USB datums still OPEN',
                  started_utc=started)
    OUT.mkdir(parents=True)
    d = A.openDocument(str(paths[0])); mount_doc = A.openDocument(str(paths[2]))
    try:
        edges = []
        for seg in route['segments']:
            if seg['kind']=='line':
                e=Part.makeLine(A.Vector(*seg['start_mm']), A.Vector(*seg['end_mm']))
            else:
                e=Part.Arc(A.Vector(*seg['start_mm']), A.Vector(*seg['mid_mm']),
                           A.Vector(*seg['end_mm'])).toShape()
            edges.append(e)
        spine=Part.Wire(edges); assert spine.isValid()
        pipe=spine.makePipeShell([Part.Wire([Part.makeCircle(1.5,A.Vector(*start),A.Vector(0,0,1))])],True,False)
        assert pipe.isValid() and len(pipe.Solids)==1 and not pipe.check(True)
        material={o.Name:o.Shape for o in d.Objects if 'Shape' in o.PropertiesList
                  and not o.Shape.isNull() and (o.Name.startswith(('P0_','Head_','Tail','MTA_','F_','W0','XA','Factory_','Joint_'))
                  or o.Name.endswith('_CP2')) and o.Name!='MAIN4853_CP2'}
        material.update(LeftRiserWithMain=mount_doc.LeftRiser.Shape,
                        RightRiser=mount_doc.RightRiser.Shape,
                        MainSupplierFamily=mount_doc.MainSupplierFamily.Shape)
        hits=[]; errors=[]; pairs=0
        for name, s in material.items():
            if not pipe.BoundBox.intersect(s.BoundBox): continue
            pairs+=1
            try:
                assert s.isValid()
                hit=pipe.common(s); assert hit.isValid()
                if hit.Volume>1e-5: hits.append(dict(part=name,volume_mm3=hit.Volume))
            except Exception as exc: errors.append(dict(part=name,error=str(exc)))
        report.update(exact_pairs_tested=pairs,contacts=hits,errors=errors,
                      status='STATIC_MAIN_GROUND_CLEAR' if not(hits or errors) else 'MAIN_GROUND_REQUIRES_SHARED_CHANGE')
        if not(hits or errors):
            obj=d.addObject('Part::Feature','W060_MAIN_GROUND');obj.Shape=pipe
            group=d.addObject('App::DocumentObjectGroup','MainNeckGroundCandidate')
            group.addObject(obj)
            for name, s in [('LeftRiserWithMain',mount_doc.LeftRiser.Shape),
                            ('RightRiser',mount_doc.RightRiser.Shape),
                            ('MainSupplierFamily',mount_doc.MainSupplierFamily.Shape)]:
                o=d.addObject('Part::Feature',name);o.Shape=s.copy();group.addObject(o)
            old=d.MAIN4853_CP2; old.Placement.Base += A.Vector(34,0,4.52)
            report['mounts_are_references_not_new_prints']=True
            d.saveAs(str(OUT/'MainGroundCandidate.FCStd'))
            report['native_sha256']=sha(OUT/'MainGroundCandidate.FCStd')
            A.closeDocument(d.Name);d=A.openDocument(str(OUT/'MainGroundCandidate.FCStd'))
            saved=d.W060_MAIN_GROUND.Shape
            assert saved.isValid() and abs(saved.Volume-pipe.Volume)<1e-6
            report['reopen_verified']=True
        assert all(sha(ROOT/p)==h for p,h in pins.items())
        report.update(finished_utc=datetime.now(timezone.utc).isoformat(),
                      worker_wall_seconds=round(time.monotonic()-tick,3))
        (OUT/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(report['status'],pairs,'pairs',hits,errors,
              'blank_mm',route['nominal_blank_mm'],flush=True)
    finally:
        A.closeDocument(d.Name);A.closeDocument(mount_doc.Name)


if __name__=='__main__':main()
