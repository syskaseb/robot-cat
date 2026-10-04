"""One open-edge source clearance in the selected left-bank top rib.

Preserve four bank mounting axes and all bought fuse holders. A local native
subtraction only: no relocation of the completed bank, wiring or hardware.
Full assembled lift and the source roof remain separate open interfaces.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-source-bank-passage-native-r1'
CAD=ROOT/'hardware/cad/studies/w5-source-bank-passage-native-r1'
PARENT=ROOT/'hardware/cad/studies/servo-fuse-left-mount-service-native-r7/LeftBankServiceMount.FCStd'

def main():
    import FreeCAD as A,Part,MeshPart
    from w5_r53_owners import installed
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    prior=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r8/checks.json'
    r=json.loads(prior.read_text(encoding='utf-8'))
    assert len(r['hits'])==10 and not r['errors'] and set(h['owner'] for h in r['hits'])=={'Cover','BankLeft'}
    assert all(sha(ROOT/k)==v for k,v in {**r['source_sha256'],**r['files']}.items())
    parent=A.openDocument(str(PARENT));d=A.newDocument('SourceBankEdgePassage')
    target=CAD/'SourceBankEdgePassage.FCStd';d.saveAs(str(target))
    link=d.addObject('App::Link','ReceivedBankLeft');link.setLink(parent.BankLeftServiceMountFinished)
    link.LinkPlacement=parent.BankLeftServiceMountFinished.Placement
    p=d.addObject('App::VarSet','SourcePassageParameters');p.addProperty('App::PropertyLength','Allowance');p.Allowance=.7
    tool=d.addObject('Part::Cylinder','OpenEdgeSourcePassage');tool.Placement.Base=A.Vector(69.6766,92,143.6)
    tool.setExpression('Radius','2.1 mm + SourcePassageParameters.Allowance');tool.Height=4.5
    final=d.addObject('Part::Cut','SourceBankLeftFinished');final.Base=link;final.Tool=tool;final.Refine=False
    d.save();d.recompute();d.save();s=final.Shape
    assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    removed=link.Shape.common(tool.Shape);assert removed.Volume>0
    # The notch reaches the existing local Y90 exterior; it is not a closed
    # bore that requires threading a 9.525mm ring through a 5.6mm aperture.
    assert abs(removed.BoundBox.YMin-90)<1e-6
    volume=s.Volume;p.Allowance=.8;d.recompute();assert final.Shape.Volume<volume
    p.Allowance=.7;d.recompute();assert abs(final.Shape.Volume-volume)<1e-5;d.save()
    route=Part.read(str(prior.parent/'SOURCE_ROUTES_WORLD.brep')).childShapes()[2]
    hits=[];errors=[];pairs=0
    def check(label,a,key,b):
        nonlocal pairs
        for aa in a.Solids:
            for bb in b.Solids:
                if not aa.BoundBox.intersect(bb.BoundBox):continue
                pairs+=1
                try:
                    c=aa.common(bb)
                    if c.Volume>1e-5:hits.append(dict(part=label,owner=key,mm3=c.Volume))
                except Exception as exc:errors.append(dict(part=label,owner=key,error=str(exc)))
    check('W067',route,'FinishedBank',final.Shape)
    owners,pins,_=installed(A,Part)
    # Check material removed against actual holders/TE/straps/fasteners, not
    # just four hand-written mounting points. Only Cover is the other pending
    # printed relief and BankLeft is the intentional parent subtraction.
    for key,shape in owners.items():
        if key in ('Cover','BankLeft'):continue
        check('RemovedBankMaterial',removed,key,shape)
    assert not hits and not errors,(hits,errors)
    assert final.Shape.cut(link.Shape).Volume<1e-5
    s=final.Shape.copy();s.exportBrep(str(CAD/'BankLeft_WORLD.brep'))
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength];assert max(dims)+10<=256
    mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'BankLeft_UNSELECTED_x1.stl'))
    deps=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-bank-source-') as td:
        tmp=Path(td)
        for q in [target,*deps]:
            dst=tmp/q.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dst)
        re=A.openDocument(str(tmp/target.relative_to(ROOT)));re.recompute();s=re.SourceBankLeftFinished.Shape
        assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-volume)<1e-5
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
    end=datetime.now(timezone.utc);pins += [prior,PARENT,Path(__file__),*deps]
    files=[q for q in CAD.iterdir() if q.suffix in ('.FCStd','.brep','.stl')]
    save(OUT/'checks.json',dict(status='NATIVE_BANK_OPEN_EDGE_SOURCE_PASSAGE_LOCAL_COMPLETE_UNSELECTED',
        hits=hits,errors=errors,pairs=pairs,open_edge_Y_mm=90,centre_mm=[69.6766,92,143.6],
        allowance_mm=.7,volume_mm3=volume,removed_mm3=removed.Volume,unchanged_parent_mounts=True,
        protected_installed_parts_checked=True,valid=True,solids=1,strict_BOP_errors=0,
        parameter_recompute=True,closed_STL=True,components=1,dimensions_mm=dims,relocated_reopen=True,
        replacement_print_quantity=1,extra_print_quantity=0,new_fasteners=0,selected=False,W5_complete=False,physical_pass=False,
        open=['Whole source supports/roof/dressing/removal and actual bank lift against the new source family. No old lift proof reused for changed interface.'],
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in dict.fromkeys(pins)},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in files},
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print('SOURCE_BANK_PASSAGE_COMPLETE',pairs,removed.Volume,dims,flush=True)

if __name__=='__main__':main()
