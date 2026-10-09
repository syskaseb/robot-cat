"""Localize actual editable link targets; reuse checked geometry iff unchanged."""
from pathlib import Path
from datetime import datetime,timezone
import json,time,shutil
import FreeCAD as A
from check_main_p0_placement import sha
from open_prototype_tail_mount import ROOT,OUT

def run():
    tick=time.monotonic();model=OUT/'TailAssemblyCurrent.FCStd'
    path=OUT/'tail-assembly-checks.json';old=json.loads(path.read_text())
    assert old['status']=='ERROR_NO_ACCEPTANCE' and old['errors']==["'App.DocumentObject' object has no attribute 'Shape'"]
    assert not old['contacts'] and len(old['motion_samples'])==13 and old['whole_tail_parameter_restore']
    assert sha(model)==old['model_sha256']
    assert all(sha(ROOT/n)==h for n,h in old['source_sha256'].items())
    parent=OUT/'tail-motion-checks.json';shutil.copy2(path,parent)
    doc=A.openDocument(str(model));doc.recompute();targets={};rows=[]
    links=[o for o in doc.Objects if o.TypeId=='App::Link' and o.getLinkedObject().Document!=doc]
    assert len(links)==11
    for link in links:
        before=link.Shape.copy();placement=link.LinkPlacement
        target=link.getLinkedObject();key=(target.Document.Name,target.Name)
        if key not in targets:
            targets[key]=doc.copyObject(target,True)
            targets[key].Visibility=False
        native=targets[key];link.setLink(native);link.LinkPlacement=placement;doc.recompute()
        after=link.Shape
        assert after.isValid() and abs(before.Volume-after.Volume)<1e-5,link.Name
        assert before.cut(after).Volume<1e-5 and after.cut(before).Volume<1e-5,link.Name
        rows.append(dict(link=link.Name,old_source=list(key),local_target=native.Name,
                         native_type=native.TypeId,unchanged_geometry=True))
    assert all(o.getLinkedObject().Document==doc for o in doc.Objects if o.TypeId=='App::Link')
    doc.TailParameters.TailYaw=0;doc.recompute();doc.saveAs(str(model))
    for d in list(A.listDocuments().values()):A.closeDocument(d.Name)
    old.update(status='CURRENT_TAIL_MECHANICS_NOMINAL_GEOMETRY_PREPARED',errors=[],
        model_sha256=sha(model),native_yaw_parameter_checked=True,
        reopen_verified=False,relocated_reopen_verified=False,
        localization=dict(links=rows,actual_native_targets_copied=True,geometry_symmetric_difference_mm3_max=1e-5,
            reused_motion_proof=parent.name,reused_tested_pairs=old['tested_pairs'],
            prior_failed_in_process_reopen_preserved=True,fresh_reopen_required=True))
    old['source_sha256'].update({parent.relative_to(ROOT).as_posix():sha(parent),
        Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
        'hardware/cad/studies/tail-horn-provisional-r5/TailCartridgeProvisionalR5.FCStd':sha(ROOT/'hardware/cad/studies/tail-horn-provisional-r5/TailCartridgeProvisionalR5.FCStd'),
        'hardware/cad/studies/mg92b-printed-horn-r2/MG92BPrintedHornTopReliefR2.FCStd':sha(ROOT/'hardware/cad/studies/mg92b-printed-horn-r2/MG92BPrintedHornTopReliefR2.FCStd')})
    old['localization_worker_seconds']=round(time.monotonic()-tick,3)
    old['localization_finished_utc']=datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(old,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=old['status'],localized_links=len(rows),seconds=old['localization_worker_seconds'])),flush=True)

if __name__=='__main__':run()
