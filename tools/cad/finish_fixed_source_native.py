"""Receive/export saved four SOURCE bases without rebuilding old features.

Receiver clamps/wiring remain OPEN. This closes only the native source-base
checkpoint, not a selected full Frame or whole phase1/physical PASS.
"""
import json,shutil,tempfile,time
from pathlib import Path
import FreeCAD as A
import MeshPart
from build_axial_moving_supports_native import check_time
from build_remaining_loom_supports import print_orientation
from plan_body36_receiver_space import P


def validate(s):assert s.isValid() and len(s.Solids)==1 and not s.check(True)


def run():
    tick=time.monotonic();folder=P.OUT/'current-fixed-receiver-supports';rf=folder/'source-bases-resume.json'
    resume=json.loads(rf.read_text());src=P.ROOT/resume['native'];assert P.SHA(src)==resume['sha256']
    prior=json.loads((folder/'manifest.json').read_text());assert len(prior['source_bases'])==4 and not prior['parts']
    out=P.OUT/'fixed-source-supports';out.mkdir(exist_ok=True);dest=out/'FixedSourceSupports.FCStd';assert not dest.exists()
    files=[rf,src,folder/'manifest.json',Path(__file__)];rows=[];exports=[];expected={}
    def save(status):
        result=dict(status=status,parts=rows,exports=exports,source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files},
            worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
            source_bases_only=True,receiver_clamps_and_routes_open=True)
        file=out/'manifest.json';tmp=file.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(file)
    with tempfile.TemporaryDirectory(prefix='robot-cat-fixed-source-final-') as td:
        copy=Path(td)/'FixedSourceSupports.FCStd';shutil.copy2(src,copy);d=A.openDocument(str(copy));d.recompute()
        par=d.getObject('ReceiverParameters');assert par and abs(par.ArmThickness.Value-4)<1e-8
        try:
            for item in prior['source_bases']:
                check_time();name=item['name'];o=d.getObject(name+'SourceRooted');assert o;validate(o.Shape)
                assert abs(o.Shape.Volume-item['volume_mm3'])<1e-4
                expected[name]=o.Shape.copy();rows.append(dict(name=name,object=o.Name,volume_mm3=o.Shape.Volume,solids=1,BOP_errors=0))
            par.ArmThickness=4.2;d.recompute()
            for row in rows:
                s=d.getObject(row['object']).Shape;validate(s);assert s.Volume>row['volume_mm3']
            par.ArmThickness=4;d.recompute()
            for row in rows:assert abs(d.getObject(row['object']).Shape.Volume-row['volume_mm3'])<1e-4
            for o in d.Objects:
                if hasattr(o,'Visibility'):o.Visibility=False
            for row in rows:d.getObject(row['object']).Visibility=True
            d.saveAs(str(dest));files.append(dest);save('FIXED_SOURCE_NATIVE_PARAMETER_CLEAR_REOPEN_OPEN')
        finally:
            if par.ArmThickness.Value!=4:par.ArmThickness=4;d.recompute()
            A.closeDocument(d.Name)
        reopened=Path(td)/'Relocated.FCStd';shutil.copy2(dest,reopened);d=A.openDocument(str(reopened));d.recompute()
        try:
            for row in rows:
                check_time();s=d.getObject(row['object']).Shape;validate(s);q=expected[row['name']]
                assert max(s.cut(q).Volume,q.cut(s).Volume)<1e-4
                printing=print_orientation(s);assert printing['fits_with_5mm_brim'],row['name']
                s=s.copy();s.Placement=A.Placement(A.Vector(),A.Rotation(*printing['rotation_quaternion']))*s.Placement
                bb=s.BoundBox;s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
                mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
                assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
                file=out/(row['name']+'_x1.stl');mesh.write(str(file));files.append(file)
                row.update(parameter_restore_mm=[4,4.2,4],relocated_reopen=True)
                exports.append(dict(part=row['name'],path=file.relative_to(P.ROOT).as_posix(),sha256=P.SHA(file),printing=printing))
                save('PARTIAL_FIXED_SOURCE_NATIVE_EXPORTS');print('fixed source exported',row['name'],flush=True)
        finally:A.closeDocument(d.Name)
    save('FOUR_FIXED_SOURCE_SUPPORTS_NATIVE_PREPARED_RECEIVERS_OPEN')


if __name__=='__main__':run()
