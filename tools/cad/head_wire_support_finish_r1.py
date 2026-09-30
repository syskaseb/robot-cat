"""Repair only affected cuts, then package changed head wire interfaces."""
import sys,json,tempfile,shutil
from pathlib import Path
import FreeCAD as A,Part,MeshPart
from head_external_wire_support_r1 import ROOT,OUT,CACHE,sha,dump,load
sys.path.insert(0,str(ROOT/'tools/electronics'))
from head_external_yaw_loop_r1 import mv
import xb11_upstream_route as R
def main():
    before=json.loads((OUT/'checks.json').read_text())
    if '--cover-window-r2' in sys.argv:
        assert not (OUT/'checks-before-cover-r2.json').exists();dump('checks-before-cover-r2.json',before)
        d=A.openDocument(str(OUT/'CoverHeadWirePassage.FCStd'));tool=d.getObject('WireInterfaceTool0');tool.Placement.Base=A.Vector(-94,92,120.5);tool.Width=12
        d.recompute();d.save();s=d.getObject('WireInterface0').Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        s.exportBrep(str(OUT/'CoverHeadWirePassage.brep'));m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        bb=m.BoundBox;m.translate(-bb.XMin,-bb.YMin,-bb.ZMin);assert m.isSolid() and m.countComponents()==1;m.write(str(OUT/'CoverHeadWirePassage_candidate_x1.stl'));A.closeDocument(d.Name)
        rows=[r for r in before['changed_pairs'] if r['owner']!='new_cover']
        for yaw in (-15,0,15):
            t=Part.Shape();t.read(str(OUT/f'loop_yaw{yaw:+}.brep'));rows.append(dict(target='loop',yaw=yaw,owner='new_cover',hit_mm3=R.volume(t.common(s))))
        boltland=Part.makeCylinder(4.2,8,A.Vector(-84,94,116),A.Vector(0,1,0));land=R.box([-94,92,120.5,-56,104,127.5]).common(boltland).Volume;assert land<1e-5
        before.update(changed_pairs=rows,hits=[r for r in rows if r['hit_mm3']>1e-5],bolt_land_removed_mm3=land,cover_repair='Extend entry Y94 to92: original tiny positive hits had witnessY93.924. Retain bolt land3.3mm, do not waive0.002mm3 intersection.')
        before['status']='SAMPLED_CHANGED_INTERFACES_CLEAR' if not before['hits'] else 'REJECTED'
        before['geometry']['cover'].update(volume_mm3=s.Volume,fcstd_sha256=sha(OUT/'CoverHeadWirePassage.FCStd'),relocated_recompute_ok=False)
        with tempfile.TemporaryDirectory(prefix='robot-cat-cover-wire-reopen-') as td:
            dest=Path(td)/'CoverHeadWirePassage.FCStd';shutil.copy2(OUT/'CoverHeadWirePassage.FCStd',dest);d=A.openDocument(str(dest));d.recompute();assert abs(d.WireInterface0.Shape.Volume-s.Volume)<1e-5 and not d.WireInterface0.Shape.check(True);A.closeDocument(d.Name)
        before['geometry']['cover']['relocated_recompute_ok']=True
        plan=json.loads((OUT/'plan.json').read_text());plan['cover_window']=[-94,92,120.5,-56,104,127.5];dump('plan.json',plan);dump('checks.json',before)
        print(json.dumps(dict(status=before['status'],hits=before['hits'])),flush=True);return
    assert not (OUT/'checks-before-repair.json').exists()
    dump('checks-before-repair.json',before)
    revised={}
    for name in ('FrontRightWirePassage','CoverHeadWirePassage'):
        d=A.openDocument(str(OUT/(name+'.FCStd')));f=d.getObject('WireInterface0');f.Refine=False
        d.recompute();d.save();s=f.Shape.copy();assert s.isValid() and len(s.Solids)==1;assert not s.check(True)
        s.exportBrep(str(OUT/(name+'.brep')))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
        assert mesh.isSolid() and mesh.countComponents()==1
        mesh.write(str(OUT/(name+'_candidate_x1.stl')))
        revised[name]=s
        dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength];assert max(dims)+10<256
        before['geometry']['front' if name.startswith('Front') else 'cover']=dict(valid=True,single_solid=True,strict_bop_errors=0,stl_closed=True,stl_components=1,stl_dimensions_mm=dims,
          native_refine=False,volume_mm3=s.Volume,fcstd_sha256=sha(OUT/(name+'.FCStd')))
        A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-head-wire-reopen-') as td:
            dest=Path(td)/(name+'.FCStd');shutil.copy2(OUT/(name+'.FCStd'),dest);d=A.openDocument(str(dest))
            d.recompute();assert abs(d.getObject('WireInterface0').Shape.Volume-s.Volume)<1e-5;assert not d.getObject('WireInterface0').Shape.check(True);A.closeDocument(d.Name)
        before['geometry']['front' if name.startswith('Front') else 'cover']['relocated_recompute_ok']=True
    rows=[r for r in before['changed_pairs'] if r['owner'] not in ('FrontRight','new_cover')]
    arm=Part.Shape();arm.read(str(OUT/'UpperForkWireArmSlotted.brep'));arm=arm.cut(load('UpperFork'))
    for yaw in (-15,0,15):
        tube=Part.Shape();tube.read(str(OUT/f'loop_yaw{yaw:+}.brep'))
        for i,s in enumerate(revised['CoverHeadWirePassage'].Solids):rows.append(dict(target='loop',yaw=yaw,owner='new_cover',solid=i,hit_mm3=R.volume(tube.common(s))))
        # Relative arm/front rotation is yaw invariant: only three pitch checks.
        if yaw==0:
            for pitch in (-10,0,5):
                for target,test in [('new_arm',arm),('loop',tube)]:
                    s=mv(revised['FrontRightWirePassage'],0,pitch)
                    if R.overlap(test.BoundBox,s.BoundBox):rows.append(dict(target=target,yaw=0,pitch=pitch,owner='FrontRight',hit_mm3=R.volume(test.common(s))))
        else:
            for pitch in (-10,0,5):
                s=mv(revised['FrontRightWirePassage'],yaw,pitch)
                if R.overlap(tube.BoundBox,s.BoundBox):rows.append(dict(target='loop',yaw=yaw,pitch=pitch,owner='FrontRight',hit_mm3=R.volume(tube.common(s))))
    before.update(status='SAMPLED_CHANGED_INTERFACES_CLEAR' if not any(r['hit_mm3']>1e-5 for r in rows) else 'REJECTED',changed_pairs=rows,hits=[r for r in rows if r['hit_mm3']>1e-5],new_stls=3,
      repair='Native Refine=False preserves valid curves. Refine=True cut was rejected; parent strict BOP and direct unrefined cylindrical cut passed.',
      parent_checks_sha256=sha(OUT/'checks-before-repair.json'),script_sha256=sha(Path(__file__)),physical_pass=False,phase1_complete=False)
    dump('checks.json',before)
    print(json.dumps(dict(status=before['status'],hits=before['hits'])),flush=True)
if __name__=='__main__':main()
