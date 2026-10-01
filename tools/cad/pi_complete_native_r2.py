"""Affected Pi pocket preservation and two enlarged GPIO sleeve clearances."""
import json,math,shutil,tempfile
from pathlib import Path
import FreeCAD as A,Part,MeshPart
import pi_wiring_complete_r1 as M
from upper_cover_mount_r1 import polygon
ROOT=M.ROOT;OLD=ROOT/'hardware/cad/studies/pi-complete-native-r1';OUT=ROOT/'hardware/cad/studies/pi-complete-native-r2'
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    d=A.openDocument(str(OLD/'PiWiringInterface.FCStd'));dest=OUT/'PiWiringInterface.FCStd'
    d.saveAs(str(dest));tools=[];sketches=[]
    for i,(x,y) in enumerate((x,y) for x in (-15.5,42.5) for y in (-24.5,24.5)):
        sk=d.addObject('Sketcher::SketchObject','PiRetainedPocketHex'+str(i));sk.Placement.Base.z=40
        rr=5.3/math.sqrt(3);polygon(sk,[(x+rr*math.cos(j*math.pi/3),y+rr*math.sin(j*math.pi/3)) for j in range(6)])
        ext=d.addObject('Part::Extrusion','PiRetainedPocketCut'+str(i));ext.Base=sk;ext.Dir=A.Vector(0,0,2.2);ext.Solid=True
        cy=d.addObject('Part::Cylinder','PiRetainedBore'+str(i));cy.Radius=1.45;cy.Height=15;cy.Placement.Base=A.Vector(x,y,39)
        tools.extend([ext,cy]);sketches.append(sk)
    cutter=d.addObject('Part::MultiFuse','RetainedPiHoles');cutter.Shapes=tools;cutter.Refine=False
    tray=d.addObject('Part::Cut','FinalPiTray');tray.Base=d.getObject('FinishedPiTray');tray.Tool=cutter;tray.Refine=False
    cuts=[]
    for n,x,y,z,r,h in [('SDA_sleeve_clearance',-57.095,-10,149,1.6,9),('OE_sleeve_clearance',91.54,-6,151.5,1.4,6)]:
        cy=d.addObject('Part::Cylinder',n);cy.Radius=r;cy.Height=h;cy.Placement=A.Placement(A.Vector(x,y,z),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)));cuts.append(cy)
    carrierTools=d.addObject('Part::Compound','GPIO_sleeve_tools');carrierTools.Links=cuts
    carrier=d.addObject('Part::Cut','FinalCarrier');carrier.Base=d.getObject('FinishedCarrier');carrier.Tool=carrierTools;carrier.Refine=False
    d.save();d.recompute()
    finals={'PiTray':tray,'Carrier':carrier,'Deck':d.getObject('FinishedDeck'),'BUSBracket':d.getObject('FinishedBUSBracket')}
    rows={};meshes=[];parent=json.loads((OLD/'checks.json').read_text(encoding='utf-8'))
    for n,f in finals.items():
        s=f.Shape;assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
        s.exportBrep(str(OUT/(n+'_WORLD.brep')))
        if n in ('PiTray','Carrier'):
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1,n
            b=mesh.BoundBox;mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(OUT/(n+'_x1.stl')))
            dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength]
        else:
            shutil.copy2(OLD/(n+'_x1.stl'),OUT/(n+'_x1.stl'));dims=parent['parts'][n]['dimensions_mm']
            assert abs(s.Volume-parent['parts'][n]['volumes'][0])<1e-5
        p=OUT/(n+'_x1.stl');assert max(dims)+10<256
        rows[n]=dict(native_object=f.Name,valid=True,single_solid=True,strict_BOP_errors=0,volume_mm3=s.Volume,STL=p.relative_to(ROOT).as_posix(),sha256=M.sha(p),closed=True,components=1,dimensions_mm=dims,quantity=1,orientation='World+Zup; original lower base on bed; PETG/brim5 fits256; slicer/supports phase2')
        vs,fs=s.tessellate(.5);meshes.append(dict(name=n,vertices=[list(v) for v in vs],triangles=fs))
    for sk in sketches:assert sk.FullyConstrained and sk.solve()==0
    d.save();A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-pi-pocket-') as td:
        p=Path(td)/dest.name;shutil.copy2(dest,p);d=A.openDocument(str(p));d.recompute()
        for n,r in rows.items():
            s=d.getObject(r['native_object']).Shape;assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-r['volume_mm3'])<1e-5
        A.closeDocument(d.Name)
    report=dict(status='NATIVE_PRINT_GEOMETRY_AVAILABLE',new_stls=2,copied_unchanged_stls=2,parts=rows,reopen_recompute=True,fully_constrained_added_sketches=4,
        changes=['Restore original4 AF5.3 nut pockets and2.9mm throughbores after caddy union had refilled one pocket; no P0 redesign','Two GPIO sleeve local clearance cuts; lands/retention require PETG delivery trial'],
        parent_manifest_sha256=M.sha(OLD/'checks.json'),source_scripts={'tools/cad/pi_complete_native_r2.py':M.sha(Path(__file__))},physical_pass=False,selected=False)
    (OUT/'checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');(OUT/'preview-geometry.json').write_text(json.dumps(meshes)+'\n',encoding='utf-8');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
