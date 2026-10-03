"""Receive R3's three completed parts and repair its ONE-tool BankLeft union.

R3 reached NATIVE_SAVED Deck/BankRight/Cover, then failed at BankLeft because
Part::MultiFuse with only one box returned a NULL shape. Preserve R3 source
and failed file. A native Compound is the same single cutting tool. Do not
recompute the three completed geometries or invent the lost probe volumes.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys, tempfile, shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    import FreeCAD as A
    import Part, Mesh, MeshPart
    started=datetime.now(timezone.utc)
    folder=ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r3'
    previous=json.loads((folder/'preflight.json').read_text(encoding='utf-8'))
    assert not any(previous[k] for k in ('hits','errors','mount_failures','strict_BOP'))
    assert not (folder/'checks.json').exists()
    source=ROOT/'tools/electronics/servo_fuse_rear_output_stations_native_r3.py'
    assert previous['script_sha256']==sha(source)
    originals=ROOT/'hardware/cad/studies/servo-fuse-rear-output-stations-native-r3'
    cad=ROOT/'hardware/cad/studies/servo-fuse-rear-output-stations-receive-r5'
    cad.mkdir(parents=True,exist_ok=True)
    pins=dict(previous['source_sha256']);pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    pins[(folder/'preflight.json').relative_to(ROOT).as_posix()]=sha(folder/'preflight.json')
    exports=[]
    for tag in ('Deck','BankRight','Cover','BankLeft'):
        path=originals/(tag+'RearOutputStations.FCStd')
        pins[path.relative_to(ROOT).as_posix()]=sha(path)
        d=A.openDocument(str(path))
        try:
            f=d.RearOutputStationsFinished
            if tag=='BankLeft':
                tools=list(d.RearGripTools.Shapes);assert len(tools)==1
                assert tools[0].TypeId=='Part::Box' and not d.LeftClipAccessFinished.Shape.isNull()
                f.Tool=tools[0];d.removeObject('RearGripTools')
                t=d.addObject('Part::Compound','RearGripTools');t.Links=tools;f.Tool=t
                d.recompute()
                s=f.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
                expected=d.LeftClipAccessFinished.Shape.cut(tools[0].Shape)
                assert s.cut(expected).Volume<1e-5 and expected.cut(s).Volume<1e-5
                dest=cad/path.name;d.saveAs(str(dest));s.exportBrep(str(cad/(tag+'_WORLD.brep')))
                mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
                assert mesh.isSolid() and mesh.countComponents()==1
                bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
                mesh.write(str(cad/(tag+'_UNSELECTED.stl')))
            else:
                # R3 printed the completion marker ONLY after BOP/mesh,
                # parameter assertions and relocated reopen. Receive that
                # completed result. Do not perform two expensive redundant
                # boolean differences on the unchanged complete Deck.
                dest=path;s=f.Shape.copy();assert not s.isNull() and s.isValid() and len(s.Solids)==1
                brep=Part.read(str(originals/(tag+'_WORLD.brep')))
                assert abs(s.Volume-brep.Volume)<1e-5 and len(s.Faces)==len(brep.Faces)
                assert all(abs(getattr(s.BoundBox,k)-getattr(brep.BoundBox,k))<1e-6
                           for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax'))
                mesh=Mesh.Mesh(str(originals/(tag+'_UNSELECTED.stl')))
                assert mesh.isSolid() and mesh.countComponents()==1
            volume=s.Volume;bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
            assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
        finally:A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-rear-receive-') as td:
            q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
            try:re.recompute();assert abs(re.RearOutputStationsFinished.Shape.Volume-volume)<1e-5
            finally:A.closeDocument(re.Name)
        exports.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final='RearOutputStationsFinished',
            single_solid=True,strict_BOP_errors=0,closed_STL=True,relocated_reopen=True,dimensions_mm=dims,
            parameter_mm=[.2,.3,.2] if tag in ('Deck','BankRight') else None,
            volumes_mm3=[volume,None,volume],
            parameter_evidence='Observed R3 NATIVE_SAVED marker follows successful parameter assertions; numeric probe volume was not persisted.' if tag in ('Deck','BankRight') else 'Round trip pending parameter-r4.',
            repair='Native single-tool Compound; nominal cut identical.' if tag=='BankLeft' else 'Unchanged completed R3 export; received existing BOP/parameter proof, checked volume/face count/bounds/mesh and recorded file hashes.'))
        print('REAR_OUTPUT_RECEIVED',tag,flush=True)
    now=datetime.now(timezone.utc)
    save(folder/'checks.json',dict(previous,status='REAR_OUTPUT_NATIVE_STATIONS_STATIC_COMPLETE_SERVICE_OPEN',
        exports=exports,source_sha256=pins,
        recovery=dict(writer=Path(__file__).relative_to(ROOT).as_posix(),writer_sha256=sha(Path(__file__)),
            observed_worker_error='BankLeft Part::MultiFuse with one Tool: Standard_NullObject BRepCheck_Analyzer NULL shape',
            completed_before_failure=['Deck','BankRight','Cover'],failed_R3_preserved=True,
            recovery_started_utc=started.isoformat(),recovery_finished_utc=now.isoformat(),
            recovery_wall_seconds=(now-started).total_seconds()),
        finished_utc=now.isoformat(),stock_delta=dict(additional_T18I=6,additional_prints=0,new_fasteners=0),
        open=['Cover/BankLeft parameter round trips, RR clips/WAGO/shared release/selection/stock/E3 remain open.']))


if __name__=='__main__':main()
