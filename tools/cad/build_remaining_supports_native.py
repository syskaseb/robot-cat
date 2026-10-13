"""Append native supports only after one accepted combined material gate."""
import json,shutil,tempfile,time
from pathlib import Path
import FreeCAD as A
import MeshPart
import build_complete_source_carriers as B
from build_front_fixed_port_clearance import placement
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect
import build_remaining_loom_supports as G
from resume_remaining_support_gate import cached_allocation
P=B.P

def add_feature(d,b,row,name,cut=False):
    x,y,z,X,Y,Z=row['bounds_mm'];old=b.Tip
    sk=sketch(b,name+'Plan',Z if cut else z)
    if row.get('placement'):sk.Placement=placement(row['placement'])*sk.Placement
    rect(sk,x,y,X-x,Y-y)
    feature=b.newObject('PartDesign::Pocket' if cut else 'PartDesign::Pad',name)
    feature.Profile=sk
    if old:feature.BaseFeature=old
    if not cut and row['name'].startswith('Arm'):
        feature.setExpression('Length',f'{Z-z-4} mm + LoomParameters.BackboneDepth')
    else:feature.Length=Z-z
    feature.Refine=True;b.Tip=feature;d.recompute()
    assert not feature.Shape.isNull() and feature.Shape.isValid(),(name,feature.State)
    sk.Visibility=False
    if old:old.Visibility=False
    assert sk.FullyConstrained,(name,'Unconstrained sketch')
    return feature

def run(shared_candidate=False):
    tick=time.monotonic();gf=P.OUT/('remaining-support-shared-material.json' if shared_candidate else 'remaining-support-material.json');gate=json.loads(gf.read_text())
    assert gate['status']=='COMBINED_SUPPORT_MATERIAL_CLEAR_NATIVE_OPEN' and not gate['contacts'] and not gate['errors']
    for n,h in gate['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    nf=P.OUT/'front-fixed-port-clearance-native.json';source=P.ROOT/json.loads(nf.read_text())['native']
    sf=P.OUT/'StationFramesCurrent.FCStd'
    out=P.OUT/'remaining-supports';out.mkdir(exist_ok=True)
    pf=P.OUT/('remaining-support-shared-paths.json' if shared_candidate else 'remaining-support-final-paths.json')
    assert gate.get('route_contract',pf.relative_to(P.ROOT).as_posix())==pf.relative_to(P.ROOT).as_posix()
    assert gate['source_sha256'][pf.relative_to(P.ROOT).as_posix()]==P.SHA(pf),'Wrong route revision for accepted material'
    paths=json.loads(pf.read_text())
    retention=json.loads((P.OUT/'remaining-retention-entry.json').read_text())
    roots=json.loads((P.OUT/'remaining-loom-roots-plan.json').read_text())
    reader=B.H.P.SavedShapes();parents={}
    for recipe in gate['recipes'].values():
        name=recipe['preserved_owner']
        if name:parents[name]=reader.shape(source if name.endswith('SourceCarrier') else sf,name)
    expected,_,bands,bonds,errors=cached_allocation(paths,retention,roots,parents);assert not errors
    outputs=[];exports=[];names={};sketches=0
    def progress():
        receipt=dict(status='PARTIAL_NATIVE_SUPPORT_BUILD_NOT_SELECTED',native_documents=outputs,exports=exports,
            fully_constrained_new_sketches=sketches,source_material_sha256=P.SHA(gf),selected=False,physical_pass=False,
            worker_seconds=round(time.monotonic()-tick,3))
        (out/'build-progress.json').write_text(json.dumps(receipt,indent=2)+'\n')
    jobs=[('HipExtension',source,'SourceCarriersCurrent.FCStd'),('FixedCarrier',sf,'StationFramesSupported.FCStd'),('KneeCarrier',None,'KneeLoomCarriers.FCStd')]
    for suffix,src,filename in jobs:
        dest=out/filename;assert not dest.exists(),'Never overwrite an unreceived native output'
        with tempfile.TemporaryDirectory(prefix='robot-cat-remaining-native-') as td:
            if src:
                copy=Path(td)/filename;shutil.copy2(src,copy);d=A.openDocument(str(copy))
            else:d=A.newDocument('KneeLoomCarriers')
            par=d.addObject('App::VarSet','LoomParameters');par.addProperty('App::PropertyLength','BackboneDepth');par.BackboneDepth=4
            volumes={};changed=[]
            try:
                for name,recipe in gate['recipes'].items():
                    if not name.endswith(suffix):continue
                    b=d.getObject(recipe['preserved_owner']) if recipe['preserved_owner'] else d.addObject('PartDesign::Body',name)
                    names[name]=(filename,b.Name);changed.append(b)
                    for i,row in enumerate(recipe['pads']):add_feature(d,b,row,name+'LoomPad'+str(i));sketches+=1
                    for i,row in enumerate(recipe['cuts']):add_feature(d,b,row,name+'LoomCut'+str(i),True);sketches+=1
                    B.validate(b);q=expected[name]
                    assert b.Shape.cut(q).Volume<1e-4 and q.cut(b.Shape).Volume<1e-4,(name,'Native differs from tested material')
                    volumes[b.Name]=b.Shape.Volume
                    print('remaining native',name,'volume',b.Shape.Volume,flush=True)
                par.BackboneDepth=4.2;d.recompute()
                for b in changed:B.validate(b);assert b.Shape.Volume>volumes[b.Name],b.Name
                par.BackboneDepth=4;d.recompute()
                for b in changed:B.validate(b);assert abs(b.Shape.Volume-volumes[b.Name])<1e-4,b.Name
                d.saveAs(str(dest))
            finally:A.closeDocument(d.Name)
            outputs.append(dict(path=dest.relative_to(P.ROOT).as_posix(),sha256=P.SHA(dest),volumes_mm3=volumes))
            progress()
        with tempfile.TemporaryDirectory(prefix='robot-cat-remaining-reopen-') as td:
            reopened=Path(td)/filename;shutil.copy2(dest,reopened);d=A.openDocument(str(reopened));d.recompute()
            try:
                for name,(file,obj) in names.items():
                    if file!=filename:continue
                    b=d.getObject(obj);B.validate(b);assert abs(b.Shape.Volume-volumes[obj])<1e-4
                    printing=next(r['printing'] for r in gate['groups'] if r['name']==name)
                    q=G.moved(b.Shape,A.Placement(A.Vector(),A.Rotation(*printing['rotation_quaternion'])))
                    bb=q.BoundBox;q.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
                    mesh=MeshPart.meshFromShape(Shape=q,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
                    assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1,name
                    bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256,name
                    f=out/(name+'_x1.stl');mesh.write(str(f))
                    exports.append(dict(part=name,path=f.relative_to(P.ROOT).as_posix(),sha256=P.SHA(f),quantity=1,size_mm=size,printing=printing))
                    progress()
            finally:A.closeDocument(d.Name)
    manifest=dict(status='REMAINING36LAND_SUPPORT_SET_NATIVE_PREPARED_W5_OPEN',native_documents=outputs,exports=exports,
        fully_constrained_new_sketches=sketches,parameter_restore_mm=[4,4.2,4],relocated_reopen=True,
        installed_new_hardware={'independent_T18I_bands':36,'provisional_case_bonds':4,'new_screws':0},
        assembly=['Unpowered bench assembly: complete staggered insulated joins first; fit the two jacket lands outside each sleeve zone.',
            'Attach four Knee feet to qualified casing patches only after adhesive compatibility/cure/load coupon. Do not drill cases or bond across seams.',
            'Replace four SourceCarrier and four StationFrame parts with their extended versions, retaining their original mounting interfaces.',
            'Seat uncut joint loops on their OWN rigid members, then install separate cuttable bands. Keep all articulation loops free.',
            'During deep removal support the harness first, cut only the assigned bands, then release the frame or provisional case bond.'],
        remaining=['Full36core body fanouts and19other body guides/independent restraints, actual cut stock and current whole selection',
            'PETG orientation supports/slicer, bond peel and creep, actual wire OD/pin cavities and sleeve/tie dimensions require phase2 fit trials',
            'Sampled motion is not a continuous swept-volume or physical PASS'],
        selected=False,W5_complete=False,physical_pass=False,
        source_sha256={gf.relative_to(P.ROOT).as_posix():P.SHA(gf),Path(__file__).relative_to(P.ROOT).as_posix():P.SHA(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(status=manifest['status'],exports=len(exports),worker_seconds=manifest['worker_seconds'])),flush=True)
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--shared-candidate',action='store_true')
    run(parser.parse_args().shared_candidate)
