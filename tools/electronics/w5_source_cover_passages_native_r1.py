"""Exact native curved source passages, not oversized collision bboxes.

Keep received E6 Cover and its complete lower mounting material. Each path
segment is an editable cylinder/torus; the shared subtraction is a replacement
print, not a new outer roof. Above-roof protection/support and service remain
open and must be constructed before selecting the entire source family.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,math,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-source-cover-passages-native-r1'
CAD=ROOT/'hardware/cad/studies/w5-source-cover-passages-native-r1'
PARENT=ROOT/'hardware/cad/studies/servo-fuse-cover-offset-mount-native-r3/OffsetCoverMount.FCStd'

def main():
    import FreeCAD as A,Part,MeshPart
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    prior=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r8/checks.json'
    received=json.loads(prior.read_text(encoding='utf-8'))
    assert not received['errors'] and set(h['owner'] for h in received['hits'])=={'Cover','BankLeft'}
    assert all(sha(ROOT/k)==v for k,v in {**received['source_sha256'],**received['files']}.items())
    parent=A.openDocument(str(PARENT));d=A.newDocument('SourceCoverCurvedPassages')
    target=CAD/'SourceCoverCurvedPassages.FCStd';d.saveAs(str(target))
    link=d.addObject('App::Link','ReceivedCover');link.setLink(parent.OffsetCoverFinished)
    link.LinkPlacement=parent.OffsetCoverFinished.Placement
    params=d.addObject('App::VarSet','PassageParameters');params.addProperty('App::PropertyLength','Allowance');params.Allowance=.7
    tools=[]
    for row in received['routes'][:4]:
        for i,e in enumerate(row['edges']):
            name=row['wire']+'Path'+str(i)
            if e['kind']=='line':
                start=A.Vector(*e['start']);delta=A.Vector(*e['end'])-start
                q=d.addObject('Part::Cylinder',name);q.Height=delta.Length
                q.setExpression('Radius','2.1 mm + PassageParameters.Allowance')
                q.Placement=A.Placement(start,A.Rotation(A.Vector(0,0,1),delta))
            else:
                edge=Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
                start=edge.valueAt(edge.FirstParameter);centre=edge.Curve.Center
                normal=(centre-start);normal.normalize();tangent=edge.tangentAt(edge.FirstParameter)
                q=d.addObject('Part::Torus',name);q.Radius1=e['radius_mm']
                q.setExpression('Radius2','2.1 mm + PassageParameters.Allowance')
                q.Angle1=-180;q.Angle2=180;q.Angle3=e['angle_rad']*180/math.pi
                q.Placement=A.Placement(centre,A.Rotation(-normal,tangent,tangent.cross(normal),'ZXY'))
            tools.append(q)
    cutter=d.addObject('Part::Compound','WholeSourceCurvedPassages');cutter.Links=tools
    final=d.addObject('Part::Cut','SourceCoverFinished');final.Base=link;final.Tool=cutter;final.Refine=False
    d.save();print('SOURCE_COVER_NATIVE_RECOMPUTE',flush=True);d.recompute();d.save()
    assert all(q.Shape.isValid() and len(q.Shape.Solids)==1 for q in tools)
    shape=final.Shape;assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
    removed=link.Shape.common(cutter.Shape);assert removed.Volume>0
    assert removed.BoundBox.ZMin>125,'Lower mounting or bearing material changed'
    volume=shape.Volume;params.Allowance=.8;d.recompute();probe=final.Shape.Volume;assert probe<volume
    params.Allowance=.7;d.recompute();assert abs(final.Shape.Volume-volume)<1e-5;d.save()
    route_shapes=Part.read(str(prior.parent/'SOURCE_ROUTES_WORLD.brep')).childShapes()
    hits=[];errors=[];pairs=0
    for row,route in zip(received['routes'],route_shapes):
        for s in route.Solids:
            if not s.BoundBox.intersect(final.Shape.BoundBox):continue
            pairs+=1
            try:
                c=s.common(final.Shape)
                if c.Volume>1e-5:hits.append(dict(wire=row['wire'],mm3=c.Volume))
            except Exception as exc:errors.append(dict(wire=row['wire'],error=str(exc)))
    assert not hits and not errors,(hits,errors)
    shape=final.Shape.copy();shape.exportBrep(str(CAD/'Cover_WORLD.brep'))
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1;mesh.rotate(math.pi,0,0)
    bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength];assert dims[0]+10<=256 and dims[1]+10<=256 and dims[2]<=256
    mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'Cover_UNSELECTED_x1.stl'))
    deps=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-source-cover-') as td:
        tmp=Path(td)
        for q in [target,*deps]:
            dest=tmp/q.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
        re=A.openDocument(str(tmp/target.relative_to(ROOT)));re.recompute();shape=re.SourceCoverFinished.Shape
        assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True) and abs(shape.Volume-volume)<1e-5
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
    end=datetime.now(timezone.utc);pins=[Path(__file__),prior,PARENT,*deps]
    files=[q for q in CAD.iterdir() if q.suffix in ('.FCStd','.brep','.stl')]
    save(OUT/'checks.json',dict(status='NATIVE_CURVED_SOURCE_COVER_PASSAGES_LOCAL_COMPLETE_UNSELECTED',hits=hits,errors=errors,pairs=pairs,
        removed_mm3=removed.Volume,removed_min_Z_mm=removed.BoundBox.ZMin,all_lower_mounting_material_preserved_below_Z_mm=125,
        volume_mm3=volume,parameter_recompute=True,valid=True,solids=1,strict_BOP_errors=0,closed_STL=True,components=1,
        dimensions_mm=dims,relocated_reopen=True,replacement_print_quantity=1,extra_print_quantity=0,new_fasteners=0,
        exact_curved_primitive_tools=True,no_bbox_cutters=True,selected=False,W5_complete=False,physical_pass=False,
        open=['Above-roof guarded source routes and all strain reliefs.',
            'Whole source/Carrier/Cover/Bank mounting and removal, cut lengths/stock and one selected export.'],
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in dict.fromkeys(pins)},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in files},
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print('SOURCE_COVER_CURVED_PASSAGES_COMPLETE',pairs,dims,flush=True)

if __name__=='__main__':main()
