"""Extend only the received east hood's outer curtain to the S1 approach.

Receive editable R4. Its split-window unintentionally clipped the curtain
atZ180 despite its own baseZ62. Lower only the east split-window. West/Cover/mounts remain unchanged.
An open-bottom curtain is not a sealed S1 terminal enclosure.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,shutil,tempfile
from servo_fuse_inputs_r1 import save,sha
ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'hardware/cad/studies/w5-source-roof-native-r4/SourceProtectiveHoods.FCStd'
RECEIPT=ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r4/checks.json'
CAD=ROOT/'hardware/cad/studies/w5-source-roof-native-r5'
OUT=ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r5'

def main():
    import FreeCAD as A,Part,MeshPart
    from w5_source_grips_native_r1 import current_owners
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    r=json.loads(RECEIPT.read_text(encoding='utf-8'))
    assert not r['hits'] and not r['errors'] and r['closed_STLs'] and r['relocated_reopen']
    assert all(sha(ROOT/k)==v for k,v in {**r['source_sha256'],**r['files']}.items())
    CAD.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    d=A.openDocument(str(PARENT));target=CAD/'SourceProtectiveHoods.FCStd';d.saveAs(str(target))
    original_volumes={n:d.getObject(n).Shape.Volume for n in ('SourceRoofCoverFinished','WestHoodFinished','EastHoodFinished')}
    q=d.EastPrintWindow
    assert q.Placement.Base.z==180 and d.SkirtExtent1.Placement.Base.z==62
    q.Placement.Base=A.Vector(25.6,-50,62);q.Height=178
    print('EAST_SOURCE_CURTAIN_RECOMPUTE',flush=True);d.recompute();d.save()
    east=d.EastHoodFinished.Shape
    assert east.isValid() and len(east.Solids)==1 and not east.check(True)
    for name in ('SourceRoofCoverFinished','WestHoodFinished'):
        assert abs(d.getObject(name).Shape.Volume-original_volumes[name])<1e-5
    assert abs(east.BoundBox.ZMin-62)<1e-5
    nominal=east.Volume;added_mm3=nominal-original_volumes['EastHoodFinished'];assert added_mm3>0
    d.RoofParameters.RoofWall=3.2;d.recompute();assert d.EastHoodFinished.Shape.Volume>nominal
    d.RoofParameters.RoofWall=3;d.recompute();assert abs(d.EastHoodFinished.Shape.Volume-nominal)<1e-5;d.save()
    owners,pins=current_owners(A,Part);owners.pop('SourceCover')
    owners['FinishedCover']=d.SourceRoofCoverFinished.Shape.copy()
    owners['WestHood']=d.WestHoodFinished.Shape.copy()
    p=ROOT/'hardware/cad/studies/w5-source-grips-native-r2/Carrier_WORLD.brep';owners['SourceCarrier']=Part.read(str(p));pins.append(p)
    for wire in ('W064','W065','W067','W068'):
        p=ROOT/f'hardware/electronics/full-cat/w5-source-grips-native-r2/{wire}_T18I_WORLD.brep';owners[wire+'_band']=Part.read(str(p));pins.append(p)
    for p in sorted(RECEIPT.parent.glob('*_WORLD.brep')):
        if p.name.startswith(('Bolt','Nut','Washers')):owners[p.stem]=Part.read(str(p));pins.append(p)
    hits=[];errors=[];pairs=0
    for name,t in owners.items():
        for a in east.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    common=a.common(b)
                    if common.Volume>1e-5:hits.append(dict(part='EastHood',owner=name,mm3=common.Volume))
                except Exception as exc:errors.append(dict(owner=name,error=str(exc)))
    print('EAST_SOURCE_CURTAIN_CONTACTS',pairs,len(hits),len(errors),flush=True)
    dims=dict(r['dimensions_mm']);closed=False;reopened=False
    east.exportBrep(str(OUT/'EastHood_WORLD.brep'))
    if not hits and not errors:
        east.exportBrep(str(CAD/'EastHood_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=east,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1;mesh.rotate(math.pi,0,0)
        bb=mesh.BoundBox;dims['EastHood']=[bb.XLength,bb.YLength,bb.ZLength]
        assert bb.XLength+10<=256 and bb.YLength+10<=256 and bb.ZLength<=256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'EastHood_UNSELECTED_x1.stl'))
        for tag in ('Cover','WestHood'):
            for suffix in ('_WORLD.brep','_UNSELECTED_x1.stl'):
                shutil.copy2(PARENT.parent/(tag+suffix),CAD/(tag+suffix))
        closed=True
    deps=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    for name in list(A.listDocuments()):A.closeDocument(name)
    if not hits and not errors:
        with tempfile.TemporaryDirectory(prefix='robot-cat-source-curtain-') as td:
            tmp=Path(td)
            for path in [target,*deps]:
                dest=tmp/path.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
            rd=A.openDocument(str(tmp/target.relative_to(ROOT)));rd.recompute();s=rd.EastHoodFinished.Shape
            assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-nominal)<1e-5
            assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values());reopened=True
    pins.extend([Path(__file__),RECEIPT,PARENT,*deps]);end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='SOURCE_ROOF_NATIVE_STATIC_COMPLETE_SERVICE_OPEN' if not hits and not errors else 'SOURCE_CURTAIN_REJECTED',
        pairs=pairs,hits=hits,errors=errors,changed_parts=['EastHood'],unchanged_parts=['Cover','WestHood','4posts','4bolt_axes','4source_routes'],
        unchanged_part_volumes_mm3={k:v for k,v in original_volumes.items() if k!='EastHoodFinished'},
        dimensions_mm=dims,closed_STLs=closed,parameter_recompute=True,relocated_reopen=reopened,
        source_routes_unchanged=True,mounts=r['mounts'],installed_counts=r['installed_counts'],
        outer_east_curtain=dict(X_mm=[191.6,194],Y_mm=[-50,140],bottom_Z_mm=62,wall_mm=2.4),
        added_PETG_volume_mm3=added_mm3,received_R4_curtain_clipped_at_Z180=True,inherited_static_receipt=RECEIPT.relative_to(ROOT).as_posix(),
        protection_scope='Top loops and outboard east-side knock protection to Z62. Bottom and front/rear below original Cover remain open; no sealed terminal casing or ingress/thermal certification.',
        sampled_service_pending=True,whole_source_assembly_complete=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in dict.fromkeys(pins)},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in [*OUT.glob('*.brep'),*CAD.glob('*.FCStd'),*CAD.glob('*.brep'),*CAD.glob('*.stl')]},
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print('EAST_SOURCE_CURTAIN_RESULT',dims['EastHood'],flush=True)

if __name__=='__main__':main()


