"""Native service notch for the bank's existing inboard locator.

R13 rejected at5mm: BankRight against stationary Guard, x/y -97..-95.
Open that locator's upward path above144.25mm, not the entire channel.
Preserve the output restraint below the notch and the front M3 mounting.
This is a subtractive replacement of the SAME Guard, no new hardware.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,math,tempfile,shutil,os
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-guard-fixed-service-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-guard-fixed-service-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists();pins={}
    def read(rel):pins[rel]=sha(ROOT/rel);return json.loads((ROOT/rel).read_text(encoding='utf-8'))
    failure=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r13/checks.json')
    assert len(failure['hits'])==1 and failure['hits'][0]['part']=='BankRight' and failure['hits'][0]['owner']=='FixedGuard'
    native=read('hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-native-r1/checks.json')
    row=next(q for q in native['exports'] if q['tag']=='Guard')
    src=ROOT/row['file'];pins[row['file']]=sha(src)
    d=A.openDocument(str(src));external=[Path(q.FileName) for q in A.listDocuments().values() if q.FileName]
    for fp in external:pins[fp.relative_to(ROOT).as_posix()]=sha(fp)
    dest=CAD/'GuardFixedService.FCStd';exports=[]
    try:
        parent=d.getObject(row['final']);before=parent.Shape.copy()
        p=d.addObject('App::VarSet','BankLocatorServiceParameters');p.addProperty('App::PropertyLength','Allowance');p.Allowance=.35
        tool=d.addObject('Part::Box','BankLocatorUpwardPassage')
        tool.Height=23.1;tool.Placement.Base=A.Vector(-97.35,-97.35,144.25)
        tool.setExpression('Length','2 mm + 2 * BankLocatorServiceParameters.Allowance')
        tool.setExpression('Width','2 mm + 2 * BankLocatorServiceParameters.Allowance')
        tool.setExpression('Placement.Base.x','-97 mm - BankLocatorServiceParameters.Allowance')
        tool.setExpression('Placement.Base.y','-97 mm - BankLocatorServiceParameters.Allowance')
        final=d.addObject('Part::Cut','GuardFixedServiceFinished');final.Base=parent;final.Tool=tool;final.Refine=False
        print('GUARD_BANK_LOCATOR_NOTCH',os.getpid(),flush=True);d.recompute();s=final.Shape.copy()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        removed=before.cut(s);assert s.cut(before).Volume<1e-5 and removed.Volume>0
        # All channel/output restraint geometry below140mm and the entire
        # front bolted attachment remain exactly unchanged by subtraction.
        zones={'output_restraint':[-130,-150,0,-80,100,140],'front_mount':[-130,75,140,-98,95,180]}
        preserved={}
        for name,b in zones.items():
            q=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]));loss=removed.common(q).Volume
            assert loss<1e-5,(name,loss);preserved[name]=dict(box_mm=b,removed_mm3=loss)
        bankpath='hardware/cad/studies/servo-fuse-fr-source-fixed-deck-native-r2/BankRight_WORLD.brep';pins[bankpath]=sha(ROOT/bankpath)
        bank=Part.read(str(ROOT/bankpath));local=[]
        for z in (0,2,5,10,30,60,100):
            b=bank.copy();b.translate(A.Vector(0,0,z));v=b.common(s).Volume;assert v<1e-5,(z,v)
            local.append(dict(lift_mm=z,common_mm3=v))
        vol=s.Volume;p.Allowance=.45;d.recompute();probe=final.Shape.Volume;assert probe<vol
        p.Allowance=.35;d.recompute();assert abs(final.Shape.Volume-vol)<1e-5
        s=final.Shape.copy();d.saveAs(str(dest));s.exportBrep(str(CAD/'Guard_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        mesh.rotate(0,math.pi/2,0);bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
        assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'Guard_UNSELECTED.stl'))
        exports.append(dict(tag='Guard',file=dest.relative_to(ROOT).as_posix(),final=final.Name,single_solid=True,
            strict_BOP_errors=0,closed_STL=True,dimensions_mm=dims,volume_mm3=vol,parameter_mm=[.35,.45,.35],
            parameter_volumes_mm3=[vol,probe,vol],added_mm3=0,removed_mm3=removed.Volume))
    finally:
        for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-guard-service-') as td:
        tmp=Path(td)
        for fp in [dest]+external:
            target=tmp/fp.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(fp,target)
        re=A.openDocument(str(tmp/dest.relative_to(ROOT)))
        try:
            re.recompute();s=re.getObject(exports[0]['final']).Shape
            assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-vol)<1e-5
            assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
            exports[0]['relocated_reopen']=True
        finally:
            for name in list(A.listDocuments()):A.closeDocument(name)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_FIXED_GUARD_LOCATOR_PASSAGE_COMPLETE_SHARED_SERVICE_OPEN',selected=False,physical_pass=False,
        W5_complete=False,exports=exports,preserved_zones=preserved,local_BankRight_Guard_samples=local,
        notch_mm=[-97.35,-97.35,144.25,-94.65,-94.65,167.35],added_prints=0,added_fasteners=0,added_wires=0,Guard_owner='FIXED_DECK',
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds()))
    print('GUARD_BANK_LOCATOR_NATIVE_COMPLETE',flush=True)

if __name__=='__main__':main()
