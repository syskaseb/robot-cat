"""One rolled four-holder layout and open-bottom RR bank/cover reliefs.

Three free body positions retained. RR moves outboard BELOW horizontal PWM,
away from XA06. Authorized casing alteration preserves the upper bank panel,
24 terminal restraint zones and clip slots; full wire/mount/service fit is open.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
CAD=ROOT/'hardware/cad/studies/servo-fuse-main-reliefs-native-r1'
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-main-reliefs-native-r1'


def build():
    import FreeCAD as A
    import Part,MeshPart
    begin=datetime.now(timezone.utc);CAD.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    pins={};results=[]
    for tag,source,name in [
        ('Bank','hardware/cad/studies/servo-fuse-bank-clip-access-r1/ServoFuseBank.FCStd','RightClipAccessFinished'),
        ('Cover','hardware/cad/studies/servo-fuse-cover-native-r4/FuseBankCover.FCStd','LowerWireCoverCut11')]:
        path=ROOT/source;pins[source]=sha(path);d=A.openDocument(str(path));dest=CAD/(tag+'RRMainRelief.FCStd')
        try:
            parent=d.getObject(name);assert parent is not None,name
            before=parent.Shape.Volume
            par=d.addObject('App::VarSet','RRMainClearance');par.addProperty('App::PropertyLength','Allowance');par.Allowance=1
            tool=d.addObject('Part::Box','OpenBottomRRMainTool')
            tool.Length=37;tool.Width=24;tool.Height=52.5;tool.Placement.Base=A.Vector(27.5,-98,78)
            tool.setExpression('Length','35 mm + 2*RRMainClearance.Allowance')
            tool.setExpression('Width','22 mm + 2*RRMainClearance.Allowance')
            final=d.addObject('Part::Cut','RRMainReliefFinished');final.Base=parent;final.Tool=tool;final.Refine=False
            print('RR_RELIEF_RECOMPUTE',tag,flush=True);d.recompute()
            shape=final.Shape.copy();assert shape.isValid() and len(shape.Solids)==1
            assert not shape.check(True),tag
            volume=shape.Volume
            if tag=='Bank' and abs(volume-before)<1e-5:
                # The real bank may already clear this cavity; do not remove
                # material or duplicate its native files just for consistency.
                results.append(dict(tag=tag,retained_source=source,new_geometry=False,
                    tool_removed_mm3=0,bounds_mm=[getattr(parent.Shape.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                print('BANK_RETAINED_NO_RELIEF_NEEDED',flush=True)
                continue
            assert volume<before,tag+' no actual relief'
            par.Allowance=1.2;d.recompute();probe=final.Shape.Volume;assert probe<volume
            par.Allowance=1;d.recompute();assert abs(final.Shape.Volume-volume)<1e-5
            shape=final.Shape.copy();d.saveAs(str(dest));shape.exportBrep(str(CAD/(tag+'_WORLD.brep')))
            # All previous features remain native. The cut stays below130.5,
            # not an enclosed pocket that catches a fixed MTA during lifting.
            parent.Visibility=False;tool.Visibility=False
            mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1
            bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
            assert max(dims[0]+10,dims[1]+10)<256 and dims[2]<256
            mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
        finally:A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-main-relief-') as td:
            q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
            try:
                re.recompute();assert abs(re.RRMainReliefFinished.Shape.Volume-volume)<1e-5
            finally:A.closeDocument(re.Name)
        results.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final='RRMainReliefFinished',
            single_solid=True,strict_BOP_errors=0,closed_STL=True,relocated_reopen=True,
            parameter_mm=[1,1.2,1],parameter_volumes_mm3=[volume,probe,volume],removed_mm3=before-volume,dimensions_mm=dims))
        save(OUT/'progress.json',dict(parts=results,selected=False,physical_pass=False))
        print('RR_RELIEF_NATIVE_SAVED',tag,flush=True)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_OPEN_BOTTOM_MAIN_RELIEFS_SHARED_FIT_OPEN',parts=results,
        cut_bounds_mm=[27.5,-98,78,64.5,-74,130.5],RR_body_bounds_mm=[28.5,-97,113.5,63.5,-75,129.5],
        scope='One1mm nominal open-bottom clearance, upper panel/terminal restraint regions geometrically outside tool; no separate cover lift or selection.',
        selected=False,physical_pass=False,W5_complete=False,source_sha256=pins,script_sha256=sha(Path(__file__)),
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))


def joint_check():
    base=ROOT/'tools/electronics/servo_fuse_main_joint_layout_r1.py'
    code=base.read_text(encoding='utf-8').replace('servo-fuse-main-joint-layout-r1','servo-fuse-main-joint-layout-r3')
    assert code.count('RR=[74,-66,126]')==1;code=code.replace('RR=[74,-66,126]','RR=[46,-86,121.5]')
    old="    points=dict(FL="
    assert code.count(old)==1
    code=code.replace(old,"""    pin(ROOT/'tools/electronics/servo_fuse_main_joint_layout_r1.py')
    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-main-reliefs-native-r1/checks.json')
    owners['ModifiableCoverR4']=load(ROOT/'hardware/cad/studies/servo-fuse-main-reliefs-native-r1/Cover_WORLD.brep')
    points=dict(FL=""")
    exec(compile(code,str(Path(__file__).resolve()),'exec'),dict(__file__=__file__,__name__='__main__'))


if __name__=='__main__':
    build()
    joint_check()
