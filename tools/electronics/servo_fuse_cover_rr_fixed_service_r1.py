"""Extend the existing RR station opening to the Cover lower edge.

R7 found a real lower-lip/fixedDeck contact, not another tie-head contact.
Retain the recorded RR station XY outline and its upper boundary. The
bottom-open continuation is a native subtractive operation; no new piece.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,math,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-rr-fixed-service-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-cover-rr-fixed-service-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    pins={}
    def read(rel):p=ROOT/rel;pins[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    fail=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r7/checks.json')
    assert len(fail['hits'])==1 and fail['hits'][0]['part']=='Cover' and fail['hits'][0]['owner']=='CandidateDeck'
    pre=read('hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r3/preflight.json')
    outline=next(b for name,b in pre['cover_tools'] if name=='RRStationOpenSide')
    native=read('hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-native-r2/checks.json')
    row=next(r for r in native['exports'] if r['tag']=='Cover')
    src=ROOT/row['file'];pins[row['file']]=sha(src)
    d=A.openDocument(str(src));external=[Path(q.FileName) for q in A.listDocuments().values() if q.FileName]
    for fp in external:pins[fp.relative_to(ROOT).as_posix()]=sha(fp)
    dest=CAD/'CoverRRFixedService.FCStd';exports=[]
    try:
        parent=d.getObject(row['final']);b=list(outline);b[2]=parent.Shape.BoundBox.ZMin-.1
        p=d.addObject('App::VarSet','FixedRRServiceParameters');p.addProperty('App::PropertyLength','Allowance');p.Allowance=.3
        tool=d.addObject('Part::Box','RRStationFullBottomServicePassage');tool.Placement.Base=A.Vector(*b[:3])
        tool.Length=b[3]-b[0];tool.Width=b[4]-b[1];tool.Height=b[5]-b[2]
        tool.setExpression('Length',f'{float(tool.Length)-.6} mm + 2*FixedRRServiceParameters.Allowance')
        tool.setExpression('Width',f'{float(tool.Width)-.6} mm + 2*FixedRRServiceParameters.Allowance')
        tool.setExpression('Placement.Base.x',f'{b[0]+.3} mm - FixedRRServiceParameters.Allowance')
        tool.setExpression('Placement.Base.y',f'{b[1]+.3} mm - FixedRRServiceParameters.Allowance')
        final=d.addObject('Part::Cut','CoverFixedRRServiceFinished');final.Base=parent;final.Tool=tool;final.Refine=False
        print('COVER_RR_OPEN_BOTTOM_RECOMPUTE',b,flush=True);d.recompute();s=final.Shape.copy();strict=s.check(True) or []
        state=dict(valid=s.isValid(),solids=len(s.Solids),BOP=[str(v) for v in strict],solid_volumes_mm3=[q.Volume for q in s.Solids])
        if not state['valid'] or state['solids']!=1 or strict:
            d.saveAs(str(dest));s.exportBrep(str(OUT/'REJECTED_COVER.brep'))
            save(OUT/'checks.json',dict(status='RR_FULL_BOTTOM_OPENING_REJECTED_STRUCTURE',state=state,tool_mm=b,
                selected=False,physical_pass=False,source_sha256=pins,script_sha256=sha(Path(__file__))))
            print('COVER_RR_SERVICE_REJECTED',json.dumps(state),flush=True);return
        v=s.Volume;p.Allowance=.4;d.recompute();vp=final.Shape.Volume
        assert vp<v;p.Allowance=.3;d.recompute();assert abs(final.Shape.Volume-v)<1e-5
        s=final.Shape.copy();d.saveAs(str(dest));s.exportBrep(str(CAD/'Cover_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        mesh.rotate(math.pi,0,0);bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
        assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'Cover_UNSELECTED.stl'))
        added=s.cut(parent.Shape).Volume;assert added<1e-5
        exports.append(dict(tag='Cover',file=dest.relative_to(ROOT).as_posix(),final=final.Name,
            single_solid=True,strict_BOP_errors=0,closed_STL=True,dimensions_mm=dims,volume_mm3=v,
            parameter_mm=[.3,.4,.3],added_mm3=added,removed_mm3=parent.Shape.Volume-v))
    finally:
        for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-rr-cover-service-') as td:
        tmp=Path(td)
        for fp in [dest]+external:
            target=tmp/fp.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(fp,target)
        r=A.openDocument(str(tmp/dest.relative_to(ROOT)))
        try:
            r.recompute();s=r.getObject(exports[0]['final']).Shape
            assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-exports[0]['volume_mm3'])<1e-5
            for doc in A.listDocuments().values():assert Path(doc.FileName).is_relative_to(tmp)
            exports[0]['relocated_reopen']=True
        finally:
            for name in list(A.listDocuments()):A.closeDocument(name)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_COVER_RR_FULL_BOTTOM_SERVICE_COMPLETE_SHARED_REMOVAL_OPEN',
        selected=False,physical_pass=False,W5_complete=False,exports=exports,tool_mm=b,
        existing_upper_window_preserved=True,added_parts=0,assembly_ties_cut=33,
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print('COVER_RR_SERVICE_NATIVE_COMPLETE',flush=True)

if __name__=='__main__':main()
