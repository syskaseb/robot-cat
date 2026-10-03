"""Receive saved R5 Bank; finish Cover without a deleted-document reference.

No repeated static owner pairs. Preserve R5 error and immutable exported Bank.
Record actual fresh numeric Bank parameter probe/restore, then Cover only.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-service-receive-r6'
CAD=ROOT/'hardware/cad/studies/servo-fuse-rr-output-service-receive-r6'

def main():
    import FreeCAD as A
    import Part,Mesh,MeshPart
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    pins={}
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def read(rel):p=ROOT/rel;pin(p);return json.loads(p.read_text(encoding='utf-8'))
    prior=read('hardware/electronics/full-cat/servo-fuse-rear-output-stations-parameter-r4/checks.json')
    access=read('hardware/electronics/full-cat/servo-fuse-rr-output-disconnect-r2/checks.json')
    pre=read('hardware/electronics/full-cat/servo-fuse-rr-output-service-native-r5/bridge-preflight.json')
    note=read('hardware/electronics/full-cat/servo-fuse-rr-output-service-native-r5/export-receive-note.json')
    assert not pre['hits'] and not pre['errors'] and all(v>0 for v in pre['embeds_mm3'])
    for rev in range(1,6):pin(ROOT/f'tools/electronics/servo_fuse_rr_output_service_native_r{rev}.py')
    for rel,h in access['source_sha256'].items():assert sha(ROOT/rel)==h;pin(ROOT/rel)
    bankfolder=ROOT/'hardware/cad/studies/servo-fuse-rr-output-service-native-r5'
    source=bankfolder/'BankRightRROutputService.FCStd';pin(source)
    for name in ('BankRight_WORLD.brep','BankRight_UNSELECTED.stl'):pin(bankfolder/name)
    d=A.openDocument(str(source))
    try:
        d.recompute();s=d.RROutputServiceFinished.Shape.copy()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        v=s.Volume;d.RRServiceParameters.Clearance=.3;d.recompute();vp=d.RROutputServiceFinished.Shape.Volume
        assert d.RROutputServiceFinished.Shape.isValid() and len(d.RROutputServiceFinished.Shape.Solids)==1 and abs(vp-v)>1e-5
        d.RRServiceParameters.Clearance=.2;d.recompute();assert abs(d.RROutputServiceFinished.Shape.Volume-v)<1e-5
        frame=d.RRIndependentServiceFrame.Shape.copy() # live copy before closing document
        m=Mesh.Mesh(str(bankfolder/'BankRight_UNSELECTED.stl'));assert m.isSolid() and m.countComponents()==1
        dims=[m.BoundBox.XLength,m.BoundBox.YLength,m.BoundBox.ZLength]
        bank=dict(file=source.relative_to(ROOT).as_posix(),final='RROutputServiceFinished',single_solid=True,strict_BOP_errors=0,
            closed_STL=True,relocated_reopen=True,parameter_mm=[.2,.3,.2],volumes_mm3=[v,vp,v],dimensions_mm=dims)
    finally:A.closeDocument(d.Name)
    # R5 already relocated reopened its completed Bank before hitting the
    # Cover error. This receipt supplies the numeric probe instead of guesses.
    row=next(r for r in prior['exports'] if r['tag']=='Cover');cpth=ROOT/row['file'];pin(cpth)
    cd=A.openDocument(str(cpth));dest=CAD/'CoverRROutputService.FCStd'
    try:
        p=cd.addObject('App::VarSet','RRFrameCoverParameters');p.addProperty('App::PropertyLength','Clearance');p.Clearance=.2
        t=cd.addObject('Part::Box','RRSupportFrameOpenSide');t.Placement.Base=A.Vector(-70.4,-111,109.15)
        for prop,value in [('Length',15.2),('Width',15.45),('Height',20.65)]:t.setExpression(prop,f'{value} mm + 2 * RRFrameCoverParameters.Clearance')
        f=cd.addObject('Part::Cut','RROutputServiceCoverFinished');f.Base=cd.RearOutputStationsFinished;f.Tool=t;f.Refine=False
        cd.recompute();cs=f.Shape.copy();assert cs.isValid() and len(cs.Solids)==1 and not cs.check(True)
        assert cs.common(frame).Volume<1e-5
        cv=cs.Volume;p.Clearance=.3;cd.recompute();cvp=f.Shape.Volume
        assert f.Shape.isValid() and len(f.Shape.Solids)==1 and abs(cvp-cv)>1e-5
        p.Clearance=.2;cd.recompute();assert abs(f.Shape.Volume-cv)<1e-5
        cs=f.Shape.copy();cd.saveAs(str(dest));cs.exportBrep(str(CAD/'Cover_WORLD.brep'))
        cm=MeshPart.meshFromShape(Shape=cs,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert cm.isSolid() and cm.countComponents()==1
        bb=cm.BoundBox;dd=[bb.XLength,bb.YLength,bb.ZLength];assert dd[0]+10<256 and dd[1]+10<256 and dd[2]<256
        cm.translate(-bb.XMin,-bb.YMin,-bb.ZMin);cm.write(str(CAD/'Cover_UNSELECTED.stl'))
    finally:A.closeDocument(cd.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-rr-cover-receive-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);r=A.openDocument(str(q))
        try:r.recompute();assert abs(r.RROutputServiceCoverFinished.Shape.Volume-cv)<1e-5
        finally:A.closeDocument(r.Name)
    cover=dict(file=dest.relative_to(ROOT).as_posix(),final='RROutputServiceCoverFinished',single_solid=True,strict_BOP_errors=0,
        closed_STL=True,relocated_reopen=True,parameter_mm=[.2,.3,.2],volumes_mm3=[cv,cvp,cv],dimensions_mm=dd)
    # Only previously obstructed three tool/lever pairs changed. Cover was
    # subtractive and bridge's7 actual installed pairs clear in pinnedR5.
    hits=[]
    for h in access['hits']:
        pth=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-disconnect-r2'/(h['probe']+'.brep');pin(pth)
        c=Part.read(str(pth)).common(s)
        if c.Volume>1e-5:hits.append(dict(probe=h['probe'],mm3=c.Volume))
    assert not hits
    save(OUT/'checks.json',dict(status='RR_OUTWARD_PROJECT_SERVICE_BANK_AND_COVER_COMPLETE',selected=False,physical_pass=False,W5_complete=False,
        exports=[bank,cover],assumptions=access['assumptions'],bridge_embeds_mm3=pre['embeds_mm3'],bridge_pairs=pre['pairs'],
        changed_access_pairs=3,hits=hits,errors=[],actual_manufacturer_lever_motion_qualified=False,shared_bank_release_qualified=False,
        sequence='After ATO/mini holders removed, cut3RR ties, operate upright outward levers. Wire withdrawal/parking and common lift still OPEN.',
        stock_delta=dict(additional_prints=0,fasteners=0,straps=0,replacements=['BankRight','Cover']),
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
    print('RR_SERVICE_RECEIVED',json.dumps(dict(parts=2,hits=len(hits),closed_STL=True)),flush=True)
if __name__=='__main__':main()
