"""One neutral assembled wiring snapshot with current editable print links.

Purchased and unchanged module shapes are pinned reference snapshots, not new
print sources. Motion samples are not duplicated as physical parts. The new
body print identities link to native sources and require relocated link tests.
No cosmetic body, collision inference from bounds or physical acceptance.
"""
import json,shutil,tempfile,time
from pathlib import Path
import FreeCAD as A
from bank_upper_retained_context import prepare,P
from check_main_p0_placement import SavedShapes
from current_rest_pose import is_rest,is_physical_reference
from current_work_guard import check


def signature(s):
    b=s.BoundBox
    return [s.Volume,b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]


def run():
    check();tick=time.monotonic();choice_file=P.OUT/'current-operating-native-composition.json'
    choice=json.loads(choice_file.read_text());assert choice['physical_print_quantity']==14
    for n,h in choice['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    print('Preparing pinned current scene',flush=True)
    scene=prepare();targets=scene['targets'];wires=scene['wires'];reader=SavedShapes()
    print('Pinned scene loaded',len(targets),len(wires),flush=True)
    # Integral new material is represented by its one actual native parent,
    # not by both the complete print and its planning children.
    retire=set().union(*scene['owned'].values());retire.add('NewRail/Rail')
    for r in choice['prints']:
        retire.add('CurrentNative/'+r['part'])
        if r['part']=='LeftRiser':retire.update(n for n in targets if n=='neck/LeftRiser' or n.startswith('neck/LeftRiser/'))
        if r['part'].startswith('ReceiverCap'):retire.add('Group_'+r['part'].removeprefix('ReceiverCap')+'/cap')
    reservations=[n for n in targets if not is_physical_reference(n)]
    targets={n:s for n,s in targets.items() if n not in retire and is_rest(n) and is_physical_reference(n)}
    wires={n:v for n,v in wires.items() if is_rest(n)}
    folder=P.OUT/'current-w5-assembly';folder.mkdir(exist_ok=True)
    model=folder/'CurrentW5Assembly.FCStd';receipt=folder/'manifest.json'
    assert not model.exists() and not receipt.exists(),'Receive existing assembly, no duplicate rebuild'
    documents={};links=[];references=[];errors=[]
    doc=A.newDocument('CurrentW5Assembly')
    # FreeCAD requires a saved owner before assigning cross-document links.
    # Keep an incomplete build distinct from the final receipt/model.
    doc.saveAs(str(folder/'CurrentW5Assembly.building.FCStd'))
    try:
        for r in choice['prints']:
            check();f=P.ROOT/r['native'];key=str(f.resolve())
            if key not in documents:documents[key]=A.openDocument(key)
            obj=documents[key].getObject(r['native_object']);assert obj and obj.Shape.isValid()
            link=doc.addObject('App::Link','Print_'+r['part']);link.LinkedObject=obj
            doc.recompute();assert link.LinkedObject==obj
            assert all(abs(a-b)<1e-5 for a,b in zip(signature(link.Shape),signature(obj.Shape)))
            links.append(dict(part=r['part'],object=link.Name,native=r['native'],native_object=r['native_object'],signature=signature(obj.Shape)))
        print('Fourteen native links placed',flush=True)
        for kind,items in [('Material',targets),('Wire',wires)]:
            for name,value in items.items():
                check();s=value[0] if kind=='Wire' else value
                if not s.isValid():errors.append(dict(reference=name,reason='Invalid pinned BRep'));continue
                ref=doc.addObject('Part::Feature','Ref_'+kind+'_'+name);ref.Label=name;ref.Shape=s
                references.append(dict(name=name,kind=kind,object=ref.Name,not_a_new_print_source=True))
        print('Neutral references placed',len(references),'errors',len(errors),flush=True)
        doc.recompute();doc.saveAs(str(model))
    finally:
        A.closeDocument(doc.Name)
        for d in documents.values():
            if d.Name in A.listDocuments():A.closeDocument(d.Name)
    files=[choice_file,Path(__file__),Path(__file__).with_name('current_rest_pose.py')]+[P.ROOT/r['native'] for r in choice['prints']]
    pins=dict(scene['pins']);pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files})
    result=dict(status='CURRENT_W5_ASSEMBLED_SNAPSHOT_LINK_REOPEN_OPEN',native=model.relative_to(P.ROOT).as_posix(),native_sha256=P.SHA(model),
        printed_body_support_links=links,reference_objects=references,errors=errors,source_sha256=pins,
        worker_seconds=round(time.monotonic()-tick,3),neutral_pose_only=True,cosmetic_enclosure_included=False,
        excluded_nonphysical_access_reservations=reservations,
        selected=False,W5_complete=False,A3_complete=False,physical_pass=False,
        scope='One actual neutral assembly snapshot. Fourteen current body support print identities are native links; other unchanged modules/purchased parts/wires are pinned reference geometry, not extra print sources. Whole K1/A3 map remains separate.')
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    assert not errors,errors
    # Preserve relative workspace layout and close originals so a surviving
    # in-memory document cannot hide a broken external native link.
    print('Saved assembly; checking relocated links',flush=True)
    with tempfile.TemporaryDirectory(prefix='robot-cat-w5-relocated-') as td:
        root=Path(td)
        for f in set(files+[model]):
            if f.suffix!='.FCStd':continue
            rel=f.relative_to(P.ROOT);dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
        moved=root/model.relative_to(P.ROOT);doc=A.openDocument(str(moved));doc.recompute();owned=[]
        try:
            for r in links:
                check();o=doc.getObject(r['object']);source=o.LinkedObject;assert source is not None,r['part']
                assert Path(source.Document.FileName).resolve().is_relative_to(root.resolve()),('External link escaped relocated package',r['part'])
                assert all(abs(a-b)<1e-5 for a,b in zip(signature(o.Shape),r['signature'])),r['part']
                owned.append(source.Document.Name)
            assert len(links)==14
        finally:
            A.closeDocument(doc.Name)
            for name in set(owned):
                if name in A.listDocuments():A.closeDocument(name)
    result.update(status='CURRENT_NEUTRAL_W5_ASSEMBLY_FOURTEEN_NATIVE_LINKS_RELOCATED_REOPEN_CLEAR',relocated_reopen=True,
        all_linked_native_sources_within_relocated_package=True,worker_seconds=round(time.monotonic()-tick,3))
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(native_links=14,material_references=len(targets),wire_references=len(wires),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
