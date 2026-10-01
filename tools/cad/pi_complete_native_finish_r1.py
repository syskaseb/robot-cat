"""Recover saved native graph; correct BUS line-touch and 13um post overhang.

Do not fill a mesh hole or invent manifold PASS. Correct editable primitives,
then regenerate unchanged three prints and the one new BUS print.
"""
import json,shutil,tempfile
from pathlib import Path
import FreeCAD as A,Part,MeshPart
import pi_wiring_complete_r1 as M
ROOT=M.ROOT;OUT=ROOT/'hardware/cad/studies/pi-complete-native-r1'
def main():
    assert not (OUT/'checks.json').exists()
    path=OUT/'PiWiringInterface.FCStd';d=A.openDocument(str(path))
    old={n:d.getObject('Finished'+n).Shape.Volume for n in ('PiTray','Deck','Carrier','BUSBracket')}
    d.getObject('BUSBaseBox0').Width=34
    for i in range(4):d.getObject('BUSStand'+str(i)).Radius=2.45
    d.save();d.recompute()
    names=('PiTray','Deck','Carrier','BUSBracket');finals={n:d.getObject('Finished'+n) for n in names}
    def valid():
        for n,f in finals.items():assert not f.Shape.isNull() and f.Shape.isValid() and len(f.Shape.Solids)==1 and not f.Shape.check(True),n
        for i in range(4):s=d.getObject('BUSNutHex'+str(i));assert s.FullyConstrained and s.solve()==0
        return {n:f.Shape.Volume for n,f in finals.items()}
    first=valid();p=d.getObject('Parameters');p.PassageRadius=1.3;p.PiRaise=7.2;d.recompute();changed=valid()
    assert changed['Carrier']<first['Carrier'] and changed['PiTray']>first['PiTray']
    p.PassageRadius=1.2;p.PiRaise=7;d.recompute();restored=valid()
    assert all(abs(restored[n]-first[n])<1e-5 for n in names)
    for n in names[:3]:assert abs(first[n]-old[n])<1e-5
    d.save();rows={};meshes=[]
    for n,f in finals.items():
        s=f.Shape.copy();s.exportBrep(str(OUT/(n+'_WORLD.brep')))
        m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert m.isSolid() and m.countComponents()==1,n
        b=m.BoundBox;m.translate(-b.XMin,-b.YMin,-b.ZMin);dims=[m.BoundBox.XLength,m.BoundBox.YLength,m.BoundBox.ZLength]
        assert max(dims)+10<256;npath=OUT/(n+'_x1.stl');m.write(str(npath))
        rows[n]=dict(native_object=f.Name,valid=True,single_solid=True,strict_BOP_errors=0,
            volumes=[first[n],changed[n],restored[n]],STL=npath.relative_to(ROOT).as_posix(),sha256=M.sha(npath),
            closed=True,components=1,dimensions_mm=dims,quantity=1,
            orientation='World+Zup, original bottom on bed; brim5 geometrically fits256; slicer/support/PETG phase2')
        vs,fs=s.tessellate(.4);meshes.append(dict(name=n,vertices=[list(v) for v in vs],triangles=fs))
    A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-pi-interface-') as td:
        cp=Path(td)/path.name;shutil.copy2(path,cp);d=A.openDocument(str(cp));d.recompute()
        for n in names:
            s=d.getObject('Finished'+n).Shape;assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-first[n])<1e-5
        A.closeDocument(d.Name)
    report=dict(status='NATIVE_PRINT_GEOMETRY_AVAILABLE',new_stls=4,parts=rows,fully_constrained_hex_sketches=4,reopen_recompute=True,
        BUS_correction={'platform_Ymax':34,'post_OD':4.9,'mount_axes_unchanged':True,
            'reason':'Previously platform/beam touched along one edge giving 4incident mesh faces; posts overhung by13um at source Y2.499987. Genuine solid shape correction, not mesh hole filling.',
            'before_volume_mm3':old['BUSBracket'],'after_volume_mm3':first['BUSBracket']},
        physical_pass=False,selected=False,remaining=['Final sleeves/stacks/lift','Single selected print/quantity set'],
        inherited_source_SHA256={p:M.sha(ROOT/p) for p in ['hardware/cad/studies/pwm-branch-restraints-r4/DeckPWMGroundTerminal.brep','hardware/cad/studies/pwm-board-end-restraint-r1/CarrierPWMService_WORLD.brep']},
        source_scripts={p:M.sha(ROOT/p) for p in ['tools/cad/pi_complete_native_r1.py','tools/cad/pi_complete_native_finish_r1.py']})
    (OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (OUT/'preview-geometry.json').write_text(json.dumps(meshes)+'\n',encoding='utf-8')
    print(json.dumps(report),flush=True)
if __name__=='__main__':main()
