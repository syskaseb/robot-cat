"""Receive source access for assembly BEFORE crossing harnesses are installed.

R1 rejects in-place service. This receipt does not rename that failure: all
30 exact contacts are wires or the removable P_SYS body band. Assembly opens
the cages first, inserts labelled ends, then closes/dresses and fits that band.
Only receive/export the already calculated native cuts; do not repeat Booleans.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, shutil, tempfile
from servo_fuse_inputs_r1 import save, sha
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'hardware/electronics/full-cat/w5-source-cage-assembly-receive-r1'
CAD = ROOT/'hardware/cad/studies/w5-source-cage-access-native-r1'
RECEIPT = ROOT/'hardware/electronics/full-cat/w5-source-cage-access-native-r1/checks.json'


def main():
    import FreeCAD as A, MeshPart
    begin = datetime.now(timezone.utc)
    assert not (OUT/'assembly.json').exists()
    r = json.loads(RECEIPT.read_text(encoding='utf-8'))
    assert r['status']=='SOURCE_CAGE_ACCESS_REJECTED' and not r['errors']
    assert all(sha(ROOT/k)==v for k,v in {**r['source_sha256'],**r['files']}.items())
    prefixes = ('hardware/electronics/full-cat/pi-wiring-complete-r13/XL05_',
                'hardware/electronics/full-cat/pi-wiring-complete-r13/XL06_',
                'hardware/electronics/full-cat/head-connected-feeds-r8/XB22_',
                'hardware/electronics/full-cat/head-connected-feeds-r8/XB23_',
                'hardware/electronics/full-cat/head-connected-feeds-r8/XS23_',
                'hardware/electronics/full-cat/aux-converter-routes-r5/XA02_',
                'hardware/electronics/full-cat/aux-converter-routes-r5/XA04_',
                'DATA/W007_')
    allowed = {'SourceInlet/BodyTieTop_WORLD','W068'}
    assert len(r['hits'])==30 and r['pairs']==167
    assert all(q['owner'] in allowed or q['owner'].startswith(prefixes) for q in r['hits'])
    target = CAD/'SourceCageServiceWindows.FCStd'
    d = A.openDocument(str(target)); d.recompute()
    dimensions={}; volumes={}; exports={}
    OUT.mkdir(parents=True,exist_ok=True)
    for label,brim in (('Carrier',6),('Cover',10)):
        f=d.getObject('SourceAccess'+label+'Finished')
        assert f.Shape.isValid() and len(f.Shape.Solids)==1
        volumes[label]=f.Shape.Volume
        mesh=MeshPart.meshFromShape(Shape=f.Shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        bb=mesh.BoundBox; dimensions[label]=[bb.XLength,bb.YLength,bb.ZLength]
        assert bb.XLength+brim<=256 and bb.YLength+brim<=256 and bb.ZLength<=256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
        p=OUT/(label+'_ASSEMBLY_ONLY_UNSELECTED_x1.stl'); mesh.write(str(p)); exports[p.relative_to(ROOT).as_posix()]=sha(p)
    deps=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName))
    for name in list(A.listDocuments()): A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-source-assembly-') as td:
        tmp=Path(td)
        for p in deps:
            dest=tmp/p.relative_to(ROOT); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dest)
        rd=A.openDocument(str(tmp/target.relative_to(ROOT))); rd.recompute()
        assert all(abs(rd.getObject('SourceAccess'+label+'Finished').Shape.Volume-v)<1e-5 for label,v in volumes.items())
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
    end=datetime.now(timezone.utc)
    save(OUT/'assembly.json',dict(status='PREWIRING_ASSEMBLY_ACCESS_RECEIVED_INSTALLED_SERVICE_REJECTED',
        inherited_exact_pairs=167,inherited_installed_contacts=30,
        assembly_stage_contact_count=0,assembly_stage_count_basis='All exact R1 hits belong to explicitly not-yet-installed crossing wires/body band; native material and purchased bodies unchanged.',
        absence_before_cages_closed=['XL05','XL06','XB22','XB23','XS23','XA02','XA04','W007','W068','P_SYS body band'],
        sequence=['Disconnect physical battery. Install empty platform, bank, Carrier and Cover without both hoods.',
                  'Before crossing harnesses/body bands, open all source cages through the three native windows; labels and P_REAR same-net port swap preserved.',
                  'Insert each prepared source end with its lever already open, close that lever, then dress that lead. W068 is absent until its own P_REAR lever is opened.',
                  'Fit four source insulation bands, P_SYS body band and crossing GPIO/head/AUX/data harnesses only after all source cages are closed.',
                  'Fit hoods last. Delivered lever/tool/finger fit, strip dimensions and wire insertion trials remain phase2.'],
        installed_service_clear=False,
        service_blocker='R1 retains 30 access contacts. A complete teardown/parking sequence has NOT yet been qualified; do not infer removal from this assembly-only receipt.',
        dimensions_mm=dimensions,closed_STLs=True,relocated_reopen=True,
        native_parameter_probe_inherited=[0,.2,0],source_cuts_remove_material_only=True,
        mounting_seats_and_roof_posts_unchanged=True,
        selected=False,whole_source_assembly_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [RECEIPT,Path(__file__),*deps]},
        files=exports,started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))


if __name__=='__main__': main()
