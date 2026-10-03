"""Add round-trip parameters to R3's two fixed native casing cuts only.

Run ONLY after receiving all four completed R3 exports. Nominal geometry must
remain identical, so do not repeat unchanged shared wire/strap checks. Deck and
BankRight already have their native sweep clearance round trip; retain them.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-stations-parameter-r4'
CAD=ROOT/'hardware/cad/studies/servo-fuse-rear-output-stations-parameter-r4'
def main():
    import FreeCAD as A
    import Mesh
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    source=ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r3/checks.json'
    j=json.loads(source.read_text(encoding='utf-8'))
    assert not j['hits'] and not j['errors'] and not j['mount_failures'] and not j['strict_BOP']
    assert {r['tag'] for r in j['exports']}=={'Deck','BankRight','Cover','BankLeft'}
    pins={source.relative_to(ROOT).as_posix():sha(source)};exports=[]
    for row in j['exports']:
        assert row['single_solid'] and row['closed_STL'] and row['relocated_reopen']
        tag=row['tag'];gp=ROOT/row['file'];pins[row['file']]=sha(gp)
        if tag not in ('Cover','BankLeft'):
            assert row['parameter_mm']==[.2,.3,.2];exports.append(dict(row,inherited_unchanged=True));continue
        d=A.openDocument(str(gp));dest=CAD/gp.name
        try:
            before=d.RearOutputStationsFinished.Shape.copy();volume=before.Volume
            tools=d.RearGripTools.Shapes if 'Shapes' in d.RearGripTools.PropertiesList else d.RearGripTools.Links
            assert tools and all(o.TypeId=='Part::Box' for o in tools)
            for o in tools:
                length=float(o.Length);o.setExpression('Length',f'{length-.2} mm + RearGripParameters.Clearance')
            d.recompute();f=d.RearOutputStationsFinished
            assert abs(f.Shape.Volume-volume)<1e-5
            assert f.Shape.cut(before).Volume<1e-5 and before.cut(f.Shape).Volume<1e-5
            d.RearGripParameters.Clearance=.3;d.recompute();probe=f.Shape.Volume;assert abs(probe-volume)>1e-4
            d.RearGripParameters.Clearance=.2;d.recompute();assert abs(f.Shape.Volume-volume)<1e-5
            s=f.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            assert s.cut(before).Volume<1e-5 and before.cut(s).Volume<1e-5
            d.saveAs(str(dest))
            # Retain the exact nominal exported geometry and its proven mesh.
            for suffix in ('_WORLD.brep','_UNSELECTED.stl'):
                p=gp.parent/(tag+suffix);pins[p.relative_to(ROOT).as_posix()]=sha(p);shutil.copy2(p,CAD/p.name)
            mesh=Mesh.Mesh(str(CAD/(tag+'_UNSELECTED.stl')));assert mesh.isSolid() and mesh.countComponents()==1
        finally:A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-rear-output-parameter-') as td:
            q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
            try:re.recompute();assert abs(re.RearOutputStationsFinished.Shape.Volume-volume)<1e-5
            finally:A.closeDocument(re.Name)
        exports.append(dict(row,file=dest.relative_to(ROOT).as_posix(),parameter_mm=[.2,.3,.2],
            volumes_mm3=[volume,probe,volume],nominal_geometry_identical_to_R3=True,relocated_reopen=True))
        print('REAR_OUTPUT_CASING_PARAMETER_SAVED',tag,flush=True)
    save(OUT/'checks.json',dict(status='ALL_FOUR_REAR_STATION_NATIVE_ROUND_TRIPS_COMPLETE_SERVICE_OPEN',
        selected=False,physical_pass=False,W5_complete=False,exports=exports,
        unchanged_static_fit=source.relative_to(ROOT).as_posix(),source_sha256=pins,script_sha256=sha(Path(__file__)),
        started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds(),
        open=['Lever/clip access, shared assembly-removal, one selection/stock/E3 still OPEN.']))
if __name__=='__main__':main()
