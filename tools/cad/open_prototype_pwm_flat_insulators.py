"""Simplify the provisional insulating washer, without a thin centering neck.

An optional 0.3mm radial shoulder is unnecessary for the isolation stack and
adds printing risk. Remove it, preserve the 1mm flange and both raised screws.
Geometric subset proof inherits the prior changed-stack/contact checks.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, time, tempfile, shutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/mounting-checkpoint'

def sha(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    import FreeCAD as A, Part, Mesh, MeshPart
    from open_deck_p0_supports import sketch, feature
    from open_deck_p0_plate import circle
    started=datetime.now(timezone.utc).isoformat();tick=time.monotonic()
    assert datetime.now(timezone.utc)<datetime.fromisoformat('2026-10-07T23:10:24+00:00')
    source=OUT/'InsulatedMounts.FCStd';native=OUT/'MountsCurrent.FCStd';proof=OUT/'pwm-flat-insulator-checks.json'
    assert not native.exists() and not proof.exists(),'Receive existing result; no duplicate'
    previous=json.loads((OUT/'pwm-mount-isolation-checks.json').read_text(encoding='utf-8'))
    assert previous['status']=='PWM_MOUNT_ISOLATION_NOMINAL_CLEAR' and sha(source)==previous['native_sha256']
    inputs=[source,OUT/'pwm-mount-isolation-checks.json',Path(__file__)]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in inputs}
    d=A.openDocument(str(source))
    try:
        old=d.PwmInsulatingShoulderWasher;oldshape=old.Shape.copy()
        p=d.Parameters
        washer=d.addObject('PartDesign::Body','PwmInsulatingWasher')
        washer.addProperty('App::PropertyString','Material');washer.Material='PETG; own provisional insulator, physical fit/creep/dielectric OPEN'
        sk=sketch(washer,'FlatInsulatorPlan',0);circle(sk,0,0,5.);circle(sk,0,0,2.4)
        washer.Tip=feature(washer,'Pad','FlatInsulatorThickness',sk,'Parameters.PwmInsulatorThickness')
        for ob in d.Objects:
            if ob.TypeId=='App::Link' and ob.LinkedObject==old:ob.setLink(washer)
        for ob in reversed(list(old.Group)):d.removeObject(ob.Name)
        d.removeObject(old.Name)
        def valid():
            d.recompute();s=washer.Shape
            assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            assert sk.FullyConstrained and sk.solve()==0
            assert all('Invalid' not in o.State and 'Touched' not in o.State for o in washer.Group)
            return s.Volume
        volume=valid();added=washer.Shape.cut(oldshape).Volume;removed=oldshape.cut(washer.Shape).Volume
        assert added<1e-7 and removed>0
        p.PwmInsulatorThickness=1.2;assert valid()>volume
        p.PwmInsulatorThickness=1.;assert abs(valid()-volume)<1e-6
        for row in previous['stacks']:
            assert abs(d.getObject(row['id']+'Screw').Placement.Base.z-.7)<1e-6
        if sk.ViewObject:sk.Visibility=False
        if washer.ViewObject:washer.Visibility=False
        d.saveAs(str(native))
        export=OUT/'PwmInsulatingWasher.stl'
        MeshPart.meshFromShape(Shape=washer.Shape,LinearDeflection=.04,AngularDeflection=.15,Relative=False).write(str(export))
        m=Mesh.Mesh(str(export));assert m.isSolid() and m.countComponents()==1
        bounds=[m.BoundBox.XLength+10,m.BoundBox.YLength+10,m.BoundBox.ZLength];assert max(bounds)<256
        A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-flat-insulator-reopen-') as td:
            path=Path(td)/native.name;shutil.copy2(native,path);d=A.openDocument(str(path));p=d.Parameters
            washer=d.PwmInsulatingWasher;sk=d.FlatInsulatorPlan
            assert abs(valid()-volume)<1e-6
            assert sum(o.TypeId=='App::Link' and o.LinkedObject==washer for o in d.Objects)==2
        result=dict(status='FLAT_INSULATING_WASHERS_NOMINAL_CLEAR',source_sha256=pins,native_sha256=sha(native),
            started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=round(time.monotonic()-tick,3),
            added_volume_mm3=added,removed_volume_mm3=removed,minimum_radial_wall_mm=1.3,
            head_to_pcb_nominal_gap_mm=1.,parameter_roundtrip_mm=[1,1.2,1],relocated_reopen=True,
            inherited_contact_proof='pwm-mount-isolation-checks.json; removed material only, screws/positions unchanged',
            replaced_print='PwmInsulatingShoulderWasher.stl; rejected unnecessary thin neck, not current',
            exports=[dict(part='PwmInsulatingWasher',quantity=2,path=export.relative_to(ROOT).as_posix(),sha256=sha(export),bounds_with_5mm_brim_mm=bounds,
                orientation='Flat on bed +Z, PETG; actual printer/nozzle/profile unknown; fit/creep/insulation coupon required')],
            stage_completed=False,selected=False,physical_pass=False,
            limitations=['No centering claim; hole/washer play retained. Flange separates metal head from PCB by nominal1mm',
                'No material certification or energizing authority; fit, no crush, insulation and creep physically untested'])
        assert all(sha(ROOT/k)==v for k,v in pins.items())
        proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ['status','worker_wall_seconds','added_volume_mm3','removed_volume_mm3','minimum_radial_wall_mm']}),flush=True)
    finally:
        if d.Name in A.listDocuments():A.closeDocument(d.Name)

if __name__=='__main__':main()
