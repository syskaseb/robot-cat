"""Open ALL twelve retained output-rib passages downwards, not a wire reroute.

The current printed sides remain linked native parents. Actual native Rib /
WirePass datums supply each U-slot. Two legs and the circular upper arch remain;
shared clearance can be changed and restored without editing upstream files.
Whole module service remains a separate test, never inferred from these cuts.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, shutil, sys, tempfile, os
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-output-rib-exits-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-output-rib-exits-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc)
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Preserve previous result'
    print('OUTPUT_RIB_NATIVE_START',os.getpid(),start.isoformat(),flush=True)
    pins={}
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    fitpath=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-mount-pair-native-r1/checks.json'
    leftpath=ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-stations-parameter-r4/checks.json'
    for fp in (fitpath,leftpath):pin(fp)
    fit=json.loads(fitpath.read_text(encoding='utf-8'))
    lf=json.loads(leftpath.read_text(encoding='utf-8'))
    rightrow=next(r for r in fit['exports'] if r['tag']=='BankRight')
    leftrow=next(r for r in lf['exports'] if r['tag']=='BankLeft')
    assert all(r['relocated_reopen'] and r['single_solid'] for r in (rightrow,leftrow))
    parents={tag:A.openDocument(str(ROOT/row['file'])) for tag,row in [('BankRight',rightrow),('BankLeft',leftrow)]}
    external=[Path(d.FileName) for d in A.listDocuments().values() if d.FileName]
    for fp in external:pin(fp)
    d=A.newDocument('OutputRibDownwardExits');dest=CAD/'OutputRibDownwardExits.FCStd'
    d.saveAs(str(dest))
    par=d.addObject('App::VarSet','OutputExitParameters')
    par.addProperty('App::PropertyLength','ExtraWidth');par.ExtraWidth=0
    specs=[];exports=[];finals={};before={}
    try:
        for tag,row,ids in [('BankRight',rightrow,['W031','W033','W035','W055','W057','W059']),
                            ('BankLeft',leftrow,['W020','W022','W024','W047','W049','W051'])]:
            pd=parents[tag];base=pd.getObject(row['final']);assert base is not None
            link=d.addObject('App::Link',tag+'CurrentParent');link.setLink(base)
            before[tag]=base.Shape.copy();tools=[]
            # Right parent is a linked assembly; its old bank carries the datums.
            datum=pd.OldBankReference.LinkedObject.Document if tag=='BankRight' else pd
            for ident in ids:
                rib=datum.getObject(ident+'Rib');hole=datum.getObject(ident+'WirePass')
                assert rib is not None and hole is not None,ident
                rb=rib.Shape.BoundBox;hb=hole.Shape.BoundBox
                cx=(hb.XMin+hb.XMax)/2;cz=(hb.ZMin+hb.ZMax)/2;diam=hb.XLength
                assert diam>0 and rb.ZMin<cz<rb.ZMax and rb.XLength>diam+4
                q=d.addObject('Part::Box',ident+'DownwardExit')
                q.Length=diam;q.Width=rb.YLength+.2;q.Height=cz-rb.ZMin+.1
                q.Placement.Base=A.Vector(cx-diam/2,rb.YMin-.1,rb.ZMin-.1)
                q.setExpression('Length',f'{diam} mm + OutputExitParameters.ExtraWidth')
                q.setExpression('Placement.Base.x',f'{cx-diam/2} mm - OutputExitParameters.ExtraWidth/2')
                tools.append(q)
                legs=[cx-diam/2-rb.XMin,rb.XMax-(cx+diam/2)]
                # Check the actual rib with its existing circular passage and new opening.
                d.recompute()
                local=rib.Shape.cut(hole.Shape).cut(q.Shape)
                assert local.isValid() and len(local.Solids)==1,(ident,len(local.Solids))
                assert min(legs)>=2.19 and cz+float(hole.Radius)<rb.ZMax
                specs.append(dict(id=ident,owner=tag,datum_document=Path(datum.FileName).relative_to(ROOT).as_posix(),
                    rib_bounds_mm=bounds(rib.Shape),hole_bounds_mm=bounds(hole.Shape),
                    opening_bounds_mm=bounds(q.Shape),retained_leg_widths_mm=legs,
                    upper_arch_retained=True,local_one_solid=True))
            compound=d.addObject('Part::Compound',tag+'ExitTools');compound.Links=tools
            final=d.addObject('Part::Cut',tag+'OutputExitsFinished')
            final.Base=link;final.Tool=compound;final.Refine=False;finals[tag]=final
            print('OUTPUT_RIB_NATIVE_CUT',tag,flush=True);d.recompute()
            s=final.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            assert s.Volume<before[tag].Volume
            nominal=s.Volume
            par.ExtraWidth=.2;d.recompute();probe=final.Shape.Volume;assert probe<nominal
            par.ExtraWidth=0;d.recompute();assert abs(final.Shape.Volume-nominal)<1e-5
            s=final.Shape.copy()
            s.exportBrep(str(CAD/(tag+'_WORLD.brep')))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1
            mesh.rotate(math.pi,0,0);bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
            assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
            mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
            exports.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final=final.Name,
                single_solid=True,strict_BOP_errors=0,closed_STL=True,dimensions_mm=dims,
                volume_mm3=s.Volume,removed_bridge_mm3=before[tag].Volume-s.Volume,
                parameter_mm=[0,.2,0],parameter_volumes_mm3=[nominal,probe,s.Volume]))
            d.save()
            save(OUT/'progress.json',dict(exports=exports,openings=specs,selected=False,physical_pass=False))
            print('OUTPUT_RIB_NATIVE_SAVED',tag,flush=True)
        for o in d.Objects:
            if hasattr(o,'Visibility'):o.Visibility=False
        for q in finals.values():q.Visibility=True
        d.recompute();d.save()
    finally:
        for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-output-exits-') as td:
        tmp=Path(td)
        for fp in [dest]+external:
            target=tmp/fp.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(fp,target)
        r=A.openDocument(str(tmp/dest.relative_to(ROOT)))
        try:
            r.recompute()
            for row in exports:
                s=r.getObject(row['final']).Shape
                assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-row['volume_mm3'])<1e-5
                assert Path(r.getObject(row['tag']+'CurrentParent').LinkedObject.Document.FileName).is_relative_to(tmp)
                row['relocated_reopen']=True
            for doc in A.listDocuments().values():assert Path(doc.FileName).is_relative_to(tmp),doc.FileName
        finally:
            for name in list(A.listDocuments()):A.closeDocument(name)
    end=datetime.now(timezone.utc)
    assert len(specs)==12 and len(exports)==2
    save(OUT/'checks.json',dict(status='TWELVE_DOWNWARD_OUTPUT_EXITS_NATIVE_COMPLETE_MODULE_SERVICE_OPEN',
        selected=False,physical_pass=False,W5_complete=False,exports=exports,openings=specs,
        preserved_bank_mounts=4,added_prints=0,added_fasteners=0,wire_or_SKU_changes=0,
        whole_module_withdrawal_qualified=False,external_documents=[p.relative_to(ROOT).as_posix() for p in external],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds()))
    print('OUTPUT_RIB_NATIVE_COMPLETE',json.dumps(dict(openings=12,exports=2,selected=False)),flush=True)

if __name__=='__main__':main()
