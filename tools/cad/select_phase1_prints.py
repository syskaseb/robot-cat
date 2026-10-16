"""K1 selected nominal whole print set, never a print-ready release."""
import json,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,BASE,SHA
from release_check import verify,REQUIRED_GATES


def run():
    tick=time.monotonic();pf=BASE/'phase1-print-set.json';gf=BASE/'phase1-print-preflight.json'
    p,g=[json.loads(f.read_text()) for f in (pf,gf)]
    assert g['status']=='ALL_SELECTED_PRINT_STLS_CLOSED_SINGLE_COMPONENT_FIT256' and not g['errors']
    measured={r['identity']:r for r in g['rows']};assert set(measured)=={r['identity'] for r in p['prints']}
    files={}
    for q in (p,g):
        for n,h in q['source_sha256'].items():assert SHA(ROOT/n)==h,n;files[n]=h
    for f in (pf,gf,Path(__file__)):files[f.relative_to(ROOT).as_posix()]=SHA(f)
    jobs=[]
    for r in p['prints']:
        m=measured[r['identity']];assert m['sha256']==r['sha256'] and m['quantity']==r['quantity']
        assert m['closed'] and m['components']==1 and m['fits_with_5mm_brim']
        jobs.append(dict(r,verified_export_size_mm=m['size_mm'],print_orientation=m['orientation'],brim_each_mm=5))
    selected=dict(p,status='K1_ONE_CURRENT_WHOLE_PROTOTYPE_PRINT_SET_SELECTED',result_id='K1',selected=True,K1_complete=True,
        prints=jobs,print_job_count=len(jobs),physical_pass=False,print_ready=False,
        preflight=gf.relative_to(ROOT).as_posix(),preflight_seconds=g['worker_seconds'],
        scope='One whole open-prototype print set. Inherited P0/E6, current modules and W5 overlays; no cosmetic torso. Physical PETG/load/profile/fit approval remains phase2.',
        source_sha256=files,worker_seconds=round(time.monotonic()-tick,3))
    sf=BASE/'phase1-current-print-selection.json';sf.write_text(json.dumps(selected,indent=2)+'\n');files[sf.relative_to(ROOT).as_posix()]=SHA(sf)
    manifest=dict(schema_version=1,result_id='K1',readiness='prototype',scope=selected['scope'],selected=True,K1_complete=True,physical_pass=False,
        selection=sf.relative_to(ROOT).as_posix(),files=[dict(path=n,sha256=h) for n,h in sorted(files.items())],
        gates={n:dict(status='open',reason='Whole assembly or delivered physical/print/electrical trial remains a separate gate; nominal K1 preparation only.') for n in REQUIRED_GATES})
    manifest['gates']['geometry']=dict(status='pass',reason='Selected STL topology and exported-axis256cube+5mmbrim checked; not wall/load or BRep engineering certification.',evidence=[gf.relative_to(ROOT).as_posix()])
    result=verify(ROOT,manifest);assert result['integrity_ok'],result
    f=BASE/'phase1-print-manifest.json';f.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(status=selected['status'],jobs=len(jobs),installed=selected['installed_print_quantity'],files=len(files),seconds=selected['worker_seconds'])))


if __name__=='__main__':run()
