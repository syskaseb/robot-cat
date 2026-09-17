"""Restore the continuous v18 shell and create a native PETG fastener gauge.

Uses the saved unsplit checkpoint, never joins tessellated split panels.
No edits to WAVEGO, its legs, electronics poses, or previous files.
"""
from pathlib import Path
from collections import Counter
import json, math, hashlib
import FreeCAD as App
import Part, Sketcher, MeshPart

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v19'
SOURCE=ROOT/'hardware/skorupa/v18/Kot_v18_TRAY_CHECKPOINT.FCStd'
V=App.Vector

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def world(obj):
    s=obj.Shape.copy()
    s.Placement=obj.getGlobalPlacement().multiply(obj.Placement.inverse()).multiply(s.Placement)
    return s

def fixed_geometry(sketch,geo):
    i=sketch.addGeometry(geo,False)
    sketch.addConstraint(Sketcher.Constraint('Block',i))

def polygon(sketch,points):
    for a,b in zip(points,points[1:]+points[:1]): fixed_geometry(sketch,Part.LineSegment(V(*a,0),V(*b,0)))

def gauge():
    doc=App.newDocument('PETG_FitGauge19')
    body=doc.addObject('PartDesign::Body','Gauge')
    sketch=doc.addObject('Sketcher::SketchObject','Outline'); body.addObject(sketch)
    polygon(sketch,[(0,0),(51,0),(56,5),(56,66),(0,66)])
    doc.recompute()
    pad=body.newObject('PartDesign::Pad','Plate6mm'); pad.Profile=sketch; pad.Length=6
    doc.recompute()
    holes=body.newObject('Sketcher::SketchObject','ClearanceHoles'); holes.Placement.Base.z=6
    samples=[]
    for y,kind,values in [(12,'M2.5 clearance',[2.7,2.9,3.1]),(26,'M3 clearance',[3.2,3.4,3.6]),(40,'M2.5 nut AF',[5.1,5.3,5.5]),(54,'M3 nut AF',[5.6,5.8,6.0])]:
        for x,value in zip((12,28,44),values):
            diameter=value if y<40 else (2.9 if y==40 else 3.4)
            fixed_geometry(holes,Part.Circle(V(x,y,0),V(0,0,1),diameter/2))
            samples.append(dict(x=x,y=y,kind=kind,value_mm=value,bore_mm=diameter))
    doc.recompute()
    pocket=body.newObject('PartDesign::Pocket','ThroughHoles'); pocket.Profile=holes; pocket.Length=6
    doc.recompute()
    nuts=body.newObject('Sketcher::SketchObject','HexNutPockets'); nuts.Placement.Base.z=6
    for p in samples:
        if p['y']<40: continue
        r=p['value_mm']/math.sqrt(3)
        polygon(nuts,[(p['x']+r*math.cos(i*math.pi/3),p['y']+r*math.sin(i*math.pi/3)) for i in range(6)])
    doc.recompute()
    finish=body.newObject('PartDesign::Pocket','NutDepth2_8mm'); finish.Profile=nuts; finish.Length=2.8
    doc.recompute()
    assert finish.Shape.isValid() and len(finish.Shape.Solids)==1
    # Exact bores must pass right through, not stop in a hidden skin.
    for p in samples:
        assert finish.Shape.common(Part.makeCylinder(p['bore_mm']/2-0.01,6.2,V(p['x'],p['y'],-0.1))).Volume<0.001
    for o in (sketch,pad,holes,pocket,nuts): o.Visibility=False
    finish.Visibility=True
    body.addProperty('App::PropertyString','Material','Manufacturing').Material='PETG'
    body.addProperty('App::PropertyString','OrientationNote','Manufacturing').OrientationNote='Flat base on bed; clipped corner at lower right of XY map'
    doc.recompute()
    doc.saveAs(str(OUT/'PETG_FitGauge19.FCStd'))
    return finish.Shape.copy(),samples

def export(name,shape):
    assert shape.isValid() and len(shape.Solids)==1,name
    path=OUT/(name+'.brep'); shape.exportBrep(str(path))
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=0.1,AngularDeflection=0.2,Relative=False)
    verts,faces=mesh.Topology
    edges=Counter(tuple(sorted((a,b))) for f in faces for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])))
    bad=sum(n!=2 for n in edges.values()); assert bad==0,(name,bad)
    assert mesh.isSolid(),name
    b=mesh.BoundBox
    matrix=App.Matrix(); matrix.move(V(-b.XMin,-b.YMin,-b.ZMin)); mesh.transform(matrix)
    stl=OUT/'stl-prototype'/(name+'.stl'); mesh.write(str(stl))
    sizes=[b.XLength,b.YLength,b.ZLength]
    fits=sizes[0]+16<=256 and sizes[1]+16<=256 and sizes[2]<=256
    assert fits,(name,sizes)
    print(name,sizes,flush=True)
    return dict(name=name,valid=True,solids=1,volume_mm3=shape.Volume,size_mm=sizes,
        triangles=len(faces),non_manifold_edges=bad,mesh_is_solid=True,
        fits_256_with_8mm_brim=fits,source_sha256=digest(path),stl_sha256=digest(stl))

def main():
    OUT.mkdir(exist_ok=True); (OUT/'stl-prototype').mkdir(exist_ok=True)
    if (OUT/'PETG_FitGauge19.FCStd').exists() or list((OUT/'stl-prototype').glob('*.stl')):
        raise RuntimeError('Preserve existing v19 outputs; choose a new version before rerunning')
    doc=App.openDocument(str(SOURCE))
    shell=world(doc.getObject('BackCover18'))
    tray=world(doc.getObject('PiTray18'))
    old_report=json.loads((ROOT/'hardware/skorupa/v18/tray-validation.json').read_text(encoding='utf-8'))
    for name,s in [('BackCover18',shell),('PiTray18',tray)]:
        expected=next(p for p in old_report['parts'] if p['name']==name)
        assert abs(s.Volume-expected['volume_mm3'])<0.001
    overlap=shell.common(tray).Volume
    assert overlap<0.001
    parts=[export('ShellContinuous19',shell),export('PiTray19',tray)]
    shape,samples=gauge()
    parts.append(export('PETG_FitGauge19',shape))
    report=dict(stage='Continuous PETG shell and fit gauge; NOT complete robot release',material='PETG',
        printer_mm=[256,256,256],source=SOURCE.relative_to(ROOT).as_posix(),source_sha256=digest(SOURCE),
        parts=parts,shell_tray_overlap_mm3=overlap,gauge_samples=samples,
        inherited_static_validation='v18/static-clearance.json applies to unchanged shell receiver and tray',
        removed_from_this_variant=['transverse split','two joining plates','four joining screws','four joining nuts'],
        pending=['chassis attachment','remaining electronics mounts','head and tail interfaces: exact microservo unknown',
                 'three-vs-four auxiliary servo mismatch','cables, dynamic sweep, strength, thermal, slicer supports, physical fit'])
    (OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('v19 geometry and gauge validated',flush=True)

if __name__=='__main__': main()
