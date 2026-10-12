"""One linked, editable E1 module assembly from the qualified current masters.

No historical native document is saved or overwritten. Printable owners remain
their existing masters; purchased geometry/route curves are labelled references.
This is module preparation, not a selected whole robot or physical PASS.
"""
import json,shutil,tempfile,time
from pathlib import Path
import FreeCAD as A
import current_u1_saved_scene as C
ROOT,OUT,SHA=C.ROOT,C.OUT,C.SHA
OWNERS={
 'interface-carriers':['UpperCarrier001'],
 'power-grips':['LowerCarrier001','E2Fixture','MAINGrip'],
 'grouped-grips':['GPIOGrip','PCAGrip'],
 'board-grips':['AnchorLeft','AnchorRight'],
 'socket-retainer':['RetainerBar'],
 'socket-population':['Adapter1208PCB','FixedPurchasedReferences','TopFaceReferences'],
}


def run():
    tick=time.monotonic();gatef=OUT/'u1-service-departures-checks.json';g=json.loads(gatef.read_text())
    assert g['status']=='TWO_ROUTES_STATIC_AND_U1_WITHDRAWAL_NOMINAL_CLEAR'
    assert not any(g[k] for k in ('contacts','errors','reservation_resolutions','self_proximity'))
    # E1 uses the already approved staged bench assembly/removal, NOT a new
    # requirement for in-situ socket exchange with BUS left installed. The
    # narrow fast-service attempts remain rejected and are not reused as PASS.
    policy=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/mounting-checkpoint/current-M5-README.md'
    for n,h in g['source_sha256'].items():assert SHA(ROOT/n)==h,n
    model=OUT/'E1CurrentAssembly.FCStd';assert not model.exists(),'Receive existing assembly, do not duplicate'
    reader,pins,targets,curves=C.context();pins.update((gatef,policy))
    docs={};receipts={};baseline={};exports=[]
    for tag,names in OWNERS.items():
        f=OUT/('u1-'+tag+'-native.json');r=json.loads(f.read_text());path=ROOT/r['native']
        assert SHA(path)==r['native_sha256'];pins.update((f,path));receipts[tag]=r
        docs[tag]=A.openDocument(str(path))
        for v in r.get('exports',[]):
            if v['part'] not in names:continue
            assert SHA(ROOT/v['path'])==v['sha256'],v['path'];pins.add(ROOT/v['path']);exports.append(v)
    f=OUT/'e2-tail-insulation-native.json';r=json.loads(f.read_text());path=ROOT/r['native']
    assert SHA(path)==r['native_sha256'];pins.update((f,path));docs['e2-wrap']=A.openDocument(str(path))
    names={**OWNERS,'e2-wrap':[n+'_BoardInsulation' for n in r['envelopes']]}
    d=A.newDocument('E1CurrentAssembly');group=d.addObject('App::Part','CurrentModule')
    info=d.addObject('App::FeaturePython','Qualification')
    for key,value in dict(Readiness='Prototype module preparation, not print-ready',
        PhysicalPass='false',Scope='E1 current signal module; not full W5 or cosmetic enclosure',
        Service='Staged teardown/bench repair per M5; no in-situ socket/BUS parking claim. Whole robot assembly A2 remains open.',
        Ownership='Links to pinned editable masters; purchased board/lead objects are references, not extra prints').items():
        info.addProperty('App::PropertyString',key);setattr(info,key,value)
    # FreeCAD requires a saved owner before creating external document links.
    d.saveAs(str(model))
    links=[]
    for tag,objects in names.items():
        for n in objects:
            source=docs[tag].getObject(n);assert source is not None,(tag,n)
            ob=d.addObject('App::Link',n+'Current');ob.setLink(source);group.addObject(ob)
            if 'Shape' in source.PropertiesList:
                baseline[n]=source.Shape.Volume
                assert abs(ob.Shape.Volume-baseline[n])<1e-5,n
                assert all(abs(getattr(ob.Shape.BoundBox,k)-getattr(source.Shape.BoundBox,k))<1e-6
                    for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')),n
            links.append(dict(name=ob.Name,owner=Path(docs[tag].FileName).relative_to(ROOT).as_posix(),object=n))
    ref=d.addObject('App::Part','RetainedPurchasedBoundaryReferences')
    for n in ('PWM1608NominalPCB','PWM9685NominalPCB'):
        ob=d.addObject('Part::Feature',n);ob.Shape=targets[n];ref.addObject(ob)
        ob.addProperty('App::PropertyString','Evidence');ob.Evidence='Purchased board/reference only; source actual holes, no extra custom print'
    wiregroup=d.addObject('App::Part','CurrentFullGuides')
    pf=OUT/'u1-common-wiring-plan.json';p=json.loads(pf.read_text());pins.add(pf)
    sf=OUT/'u1-service-departures-plan.json';s=json.loads(sf.read_text());pins.add(sf)
    routes={**p['complete_routes'],**p['changed_MAIN_pair'],**s['replacements']}
    assert len(routes)==13
    for n,q in routes.items():
        ob=d.addObject('Part::Feature',n);ob.Shape=curves[n][0];wiregroup.addObject(ob)
        ob.addProperty('App::PropertyLength','JacketRadius');ob.JacketRadius=curves[n][1]
        ob.addProperty('App::PropertyString','Qualification');ob.Qualification='Full centreline reference, no physical cut/fit claim'
    d.recompute();d.saveAs(str(model))
    sources=[Path(doc.FileName) for doc in docs.values()]
    for name in list(A.listDocuments()):A.closeDocument(name)
    # Relative external links must survive relocation with the pinned masters.
    with tempfile.TemporaryDirectory(prefix='robot-cat-e1-linked-') as td:
        copies={}
        for path in sources+[model]:
            f=Path(td)/path.name;shutil.copy2(path,f);copies[path.name]=f
        opened={path.name:A.openDocument(str(copies[path.name])) for path in sources}
        fresh=A.openDocument(str(copies[model.name]));fresh.recompute()
        for row in links:
            ob=fresh.getObject(row['name']);assert ob.LinkedObject is not None,row
            assert str(Path(ob.LinkedObject.Document.FileName).resolve()).startswith(str(Path(td).resolve())),row
            if row['object'] in baseline:assert abs(ob.Shape.Volume-baseline[row['object']])<1e-5,row
        master=opened['U1GroupedGripsCurrent.FCStd'];before=fresh.GPIOGripCurrent.Shape.Volume
        master.GripParameters.GPIOBridgeDepth=2.7;master.recompute();fresh.recompute()
        assert fresh.GPIOGripCurrent.Shape.Volume>before,'Link did not update with editable master'
        master.GripParameters.GPIOBridgeDepth=2.5;master.recompute();fresh.recompute()
        assert abs(fresh.GPIOGripCurrent.Shape.Volume-before)<1e-5
        for name in list(A.listDocuments()):A.closeDocument(name)
    receipt=dict(status='E1_LINKED_NATIVE_ASSEMBLY_PREPARED_SELECTION_OPEN',native=model.relative_to(ROOT).as_posix(),
        native_sha256=SHA(model),links=links,current_print_exports=exports,full_guide_count=13,
        actual_purchased_PCB_holes=True,parameter_link_test_mm=[2.5,2.7,2.5],fresh_relocated_reopen=True,
        selected=False,E1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in pins|{Path(__file__)}},worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'e1-current-assembly-native.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_sha256','links','current_print_exports')}),flush=True)


if __name__=='__main__':run()
