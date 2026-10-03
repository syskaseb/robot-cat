"""One bottom-open inner passage for the entire stationary W042 factory loop.

The tool is a conservative design envelope, not a collision measurement.
Native subtraction preserves all holder/end regions and four mount zones.
No wire relocation, extra component or arbitrary collider exemption.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys, math, tempfile, shutil, os
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
from servo_fuse_inputs_r1 import sha, save
OUT = ROOT / 'hardware/electronics/full-cat/servo-fuse-bank-inner-feed-service-r1'
CAD = ROOT / 'hardware/cad/studies/servo-fuse-bank-inner-feed-service-r1'

def main():
    import FreeCAD as A
    import Part, MeshPart
    start = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True); CAD.mkdir(parents=True, exist_ok=True)
    assert not (OUT / 'checks.json').exists()
    pins = {}
    def read(rel):
        pins[rel] = sha(ROOT / rel)
        return json.loads((ROOT / rel).read_text(encoding='utf-8'))
    failure = read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r16/checks.json')
    assert failure['completed_clear_lifts_mm'] == [2, 5] and not failure['errors']
    hit = failure['hits'][0]
    assert (hit['phase'], hit['part'], hit['owner']) == ('sampled_lift_10', 'BankRight', 'RetainedFeed/W042_factory_DESIGN')
    wirepath = 'hardware/electronics/full-cat/servo-fuse-front-source-ports-r2/W042_factory_DESIGN.brep'
    pins[wirepath] = sha(ROOT / wirepath); wire = Part.read(str(ROOT / wirepath))
    receipt = read('hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-native-r2/checks.json')
    row = next(q for q in receipt['exports'] if q['tag'] == 'BankRight')
    d = A.openDocument(str(ROOT / row['file']))
    external = list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName))
    for fp in external: pins[fp.relative_to(ROOT).as_posix()] = sha(fp)
    parent = d.getObject(row['final']); wb = wire.BoundBox
    p = d.addObject('App::VarSet', 'InnerFeedServiceParameters')
    p.addProperty('App::PropertyLength', 'Allowance'); p.Allowance = .35
    bottom = parent.Shape.BoundBox.ZMin - .1
    tool = d.addObject('Part::Box', 'WholeStationaryFactoryLoopPassage')
    for prop, val in [('Length', wb.XLength), ('Width', wb.YLength), ('Height', wb.ZMax-bottom)]:
        tool.setExpression(prop, f'{val} mm + 2*InnerFeedServiceParameters.Allowance')
    for axis, val in [('x', wb.XMin), ('y', wb.YMin), ('z', bottom)]:
        tool.setExpression('Placement.Base.'+axis, f'{val} mm - InnerFeedServiceParameters.Allowance')
    final = d.addObject('Part::Cut', 'BankRightInnerFeedServiceFinished')
    final.Base = parent; final.Tool = tool; final.Refine = False
    dest = CAD / 'BankInnerFeedService.FCStd'; exports = []; protected = []
    try:
        print('INNER_FEED_NATIVE_RECOMPUTE', os.getpid(), flush=True)
        d.recompute(); d.saveAs(str(dest))
        s = final.Shape.copy(); strict = s.check(True) or []
        state = dict(valid=s.isValid(), solids=len(s.Solids), strict_BOP_errors=[str(v) for v in strict])
        save(OUT/'progress.json', dict(stage='NATIVE_CUT', state=state, selected=False))
        assert s.isValid() and len(s.Solids) == 1 and not strict, state
        # All original right holder/end material lies outside this inner notch.
        # Test complete original material within that region, not just centres.
        zones = [('RightHolderAndEndRegions', Part.makeBox(250, 50, 90, A.Vector(-105,-151,80)))]
        for x, y in [(128,-92.5), (128,92.5), (-51,92.5), (-60,-108.5)]:
            zones.append((f'Mount_{x}_{y}', Part.makeBox(10,10,12,A.Vector(x-5,y-5,103))))
        removed = parent.Shape.common(tool.Shape)
        for name, zone in zones:
            loss = removed.common(zone).Volume
            assert loss < 1e-5, (name, loss)
            protected.append(dict(name=name, removed_mm3=loss))
        v = s.Volume; assert removed.Volume > 0 and v < parent.Shape.Volume
        p.Allowance = .45; d.recompute(); probe = final.Shape.Volume; assert probe < v
        p.Allowance = .35; d.recompute(); assert abs(final.Shape.Volume-v) < 1e-5
        s = final.Shape.copy(); assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        d.save(); s.exportBrep(str(CAD/'BankRight_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        mesh.rotate(math.pi,0,0); bb=mesh.BoundBox; dims=[bb.XLength,bb.YLength,bb.ZLength]
        assert dims[0]+10<=256 and dims[1]+10<=256 and dims[2]<=256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin); mesh.write(str(CAD/'BankRight_UNSELECTED.stl'))
        exports.append(dict(tag='BankRight',file=dest.relative_to(ROOT).as_posix(),final=final.Name,
            single_solid=True,strict_BOP_errors=0,closed_STL=True,dimensions_mm=dims,volume_mm3=v,
            parameter_mm=[.35,.45,.35],nominal_probe_volumes_mm3=[v,probe,v]))
    finally:
        for name in list(A.listDocuments()): A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-bank-inner-service-') as td:
        tmp=Path(td)
        for fp in [dest]+external:
            to=tmp/fp.relative_to(ROOT);to.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(fp,to)
        re=A.openDocument(str(tmp/dest.relative_to(ROOT)))
        try:
            re.recompute(); s=re.getObject(exports[0]['final']).Shape
            assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-v)<1e-5
            assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
            exports[0]['relocated_reopen']=True
        finally:
            for name in list(A.listDocuments()): A.closeDocument(name)
    end=datetime.now(timezone.utc)
    parentpath='hardware/cad/studies/servo-fuse-fr-source-fixed-deck-native-r2/BankRight_WORLD.brep'
    save(OUT/'checks.json',dict(status='NATIVE_BANK_INNER_FEED_SERVICE_COMPLETE_WHOLE_RELEASE_OPEN',
        selected=False,physical_pass=False,W5_complete=False,exports=exports,protected_regions=protected,
        subtractive_by_native_construction=True,parent_bank_brep=parentpath,parent_bank_brep_sha256=sha(ROOT/parentpath),
        wire_envelope_basis='Entire stationary W042 loop XY projected to bank bottom; conservative design allowance, not measured witness',
        removed_mm3=removed.Volume,added_parts=0,added_fasteners=0,added_wires=0,
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds()))
    print('INNER_FEED_NATIVE_COMPLETE',flush=True)
if __name__=='__main__': main()
