"""Four full-depth native source passages in the preserved Pi Carrier.

Cuts only: preserve the received Pi nut pockets/GPIO sleeves and all inherited
supports. Do not select the source family before its roof/supports/assembly.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
PARENT=ROOT/'hardware/cad/studies/pi-complete-native-r2/PiWiringInterface.FCStd'
OUT=ROOT/'hardware/electronics/full-cat/w5-source-carrier-native-r1'
CAD=ROOT/'hardware/cad/studies/w5-source-carrier-native-r1'
PASSAGES={'W064':((-39,36.2),(-39,36.2)),
          'W065':((54.5,0),(57.2,0)),
          'W067':((-69,-15.4),(-69,-11)),
          'W068':((-18.25,-18.2),(-13.9,-18.2))}

def main():
    import FreeCAD as A,Part,MeshPart
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    prior=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r6/checks.json'
    received=json.loads(prior.read_text(encoding='utf-8'))
    assert not received['errors'] and len(received['hits'])==15
    assert all(sha(ROOT/k)==v for k,v in {**received['source_sha256'],**received['files']}.items())
    parent=A.openDocument(str(PARENT));d=A.newDocument('SourceCarrierPassages')
    target=CAD/'SourceCarrierPassages.FCStd';d.saveAs(str(target))
    p=d.addObject('App::VarSet','PassageParameters');p.addProperty('App::PropertyLength','Clearance');p.Clearance=.7
    link=d.addObject('App::Link','ReceivedCarrier');link.setLink(parent.FinalCarrier)
    link.LinkPlacement=parent.FinalCarrier.Placement;tools=[]
    for wire,(a,b) in PASSAGES.items():
        for i,(x,y) in enumerate((a,b) if a!=b else (a,)):
            q=d.addObject('Part::Cylinder',wire+'End'+str(i));q.setExpression('Radius','2.1 mm + PassageParameters.Clearance')
            q.Height=14.2;q.Placement.Base=A.Vector(x,y,139.8);tools.append(q)
        if a!=b:
            q=d.addObject('Part::Box',wire+'Bridge')
            if a[0]!=b[0]:
                q.Length=abs(b[0]-a[0]);q.setExpression('Width','4.2 mm + 2 * PassageParameters.Clearance')
                q.Placement.Base=A.Vector(min(a[0],b[0]),a[1]-2.8,139.8)
                q.setExpression('Placement.Base.y',str(a[1])+' mm - 2.1 mm - PassageParameters.Clearance')
            else:
                q.setExpression('Length','4.2 mm + 2 * PassageParameters.Clearance');q.Width=abs(b[1]-a[1])
                q.Placement.Base=A.Vector(a[0]-2.8,min(a[1],b[1]),139.8)
                q.setExpression('Placement.Base.x',str(a[0])+' mm - 2.1 mm - PassageParameters.Clearance')
            q.Height=14.2;tools.append(q)
    compound=d.addObject('Part::Compound','FourFullDepthPassages');compound.Links=tools
    final=d.addObject('Part::Cut','SourceCarrierFinished');final.Base=link;final.Tool=compound;final.Refine=False
    d.save();d.recompute();d.save()
    s=final.Shape;assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    volume=s.Volume;removed=link.Shape.Volume-volume;assert removed>0
    p.Clearance=.8;d.recompute();assert final.Shape.Volume<volume
    p.Clearance=.7;d.recompute();assert abs(final.Shape.Volume-volume)<1e-5;d.save()
    routes=Part.read(str(prior.parent/'SOURCE_ROUTES_WORLD.brep')).childShapes()
    hits=[]
    for row,route in zip(received['routes'],routes):
        if row['wire'] not in PASSAGES:continue
        for part in route.Solids:
            if not part.BoundBox.intersect(final.Shape.BoundBox):continue
            common=part.common(final.Shape)
            if common.Volume>1e-5:hits.append(dict(wire=row['wire'],mm3=common.Volume))
    assert not hits,hits
    # A pure subtraction cannot introduce any new installed collision; require
    # exact parent subtraction volume, rather than a conservative bbox waiver.
    assert final.Shape.cut(link.Shape).Volume<1e-5
    s=final.Shape.copy();s.exportBrep(str(CAD/'Carrier_WORLD.brep'))
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength];assert max(dims)+10<=256
    mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'Carrier_UNSELECTED_x1.stl'))
    dependencies=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-source-carrier-') as td:
        tmp=Path(td)
        for q in [target,*dependencies]:
            dest=tmp/q.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
        d=A.openDocument(str(tmp/target.relative_to(ROOT)));d.recompute();shape=d.SourceCarrierFinished.Shape
        assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
        assert abs(shape.Volume-volume)<1e-5
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
    end=datetime.now(timezone.utc)
    pins=[Path(__file__),PARENT,prior,*dependencies]
    files=[q for q in CAD.iterdir() if q.suffix in ('.FCStd','.brep','.stl')]
    save(OUT/'checks.json',dict(status='FOUR_SOURCE_CARRIER_PASSAGES_LOCAL_COMPLETE_UNSELECTED',hits=hits,
        full_depth_Z_mm=[139.8,154],native_passages=PASSAGES,clearance_mm=.7,
        valid=True,solids=1,strict_BOP_errors=0,removed_mm3=removed,volume_mm3=volume,
        closed_STL=True,components=1,dimensions_mm=dims,replacement_print_quantity=1,extra_print_quantity=0,
        parameter_recompute=True,relocated_reopen=True,parent_supports_preserved_by_subtraction=True,
        assembly=['Install source platform on bare Deck first. Prewire short XA01 and exchanged P_REAR cages before dressing.',
            'Pass four unterminated source wires through these apertures before fitting their TE ring terminals.',
            'Carrier holes are clearance, NOT strain relief: guards/grips, shared roof and complete removal remain open.'],
        selected=False,W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in dict.fromkeys(pins)},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in files},
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print('SOURCE_CARRIER_COMPLETE',dims,removed,flush=True)

if __name__=='__main__':main()
