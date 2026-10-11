"""Preserve the scoped, unselected four-holder proof without foreign originals.

This receipt is NOT W5 completion or a selected mechanical/export package.
Historical untracked inputs are exact recoverable archive copies only.
"""
import hashlib,json,subprocess,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'body-harness-checkpoint'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    tick=time.monotonic()
    names=['owner-plan.json','mta-interface-plan.json','mta-interface-checks.json',
           'inline-terminal-data.json','sif-terminal-data.json','allocation-history.json']
    own={OUT/n for n in names}|{Path(__file__),OUT/'.gitattributes'}|{
        ROOT/'tools/cad'/n for n in ('plan_current_body_harness.py','plan_current_mta_interfaces.py','check_current_mta_interfaces.py')}|{
        ROOT/'tests'/n for n in ('test_current_body_harness_plan.py','test_current_mta_interfaces.py')}
    p=json.loads((OUT/'mta-interface-plan.json').read_text())
    q=json.loads((OUT/'mta-interface-checks.json').read_text())
    assert p['allocation_revision']==6 and not q['contacts'] and not q['errors']
    assert len(p['holders'])==4 and len(p['factory_routes'])==8 and len(p['joints'])==8
    pins={f.relative_to(ROOT).as_posix():SHA(f) for f in own}
    for n in names:
        for path,h in json.loads((OUT/n).read_text()).get('source_sha256',{}).items():
            assert SHA(ROOT/path)==h,path
            assert path not in pins or pins[path]==h,path
            pins[path]=h
    tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines())
    previous=BASE/'aux-wiring-checkpoint/retained-inputs.json'
    inherited={r['path']:r['sha256'] for r in json.loads(previous.read_text())['files']}
    copied={};references={}
    ownpaths={f.relative_to(ROOT).as_posix() for f in own}
    for path,h in pins.items():
        if path in tracked or path in ownpaths:continue
        if inherited.get(path)==h:references[path]='aux-wiring-checkpoint/retained-inputs.zip'
        else:copied[path]=h
    archive=OUT/'retained-mta-inputs.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for path in sorted(copied):
            item=zipfile.ZipInfo(path,(2026,10,11,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(item,(ROOT/path).read_bytes())
    with zipfile.ZipFile(archive) as z:
        assert all(hashlib.sha256(z.read(path)).hexdigest()==h for path,h in copied.items())
    for f in (archive,previous,previous.with_name('retained-inputs.zip')):pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    manifest=dict(status='SCOPED_FACTORY_INTERFACES_NOT_W5_SELECTION',selected=False,
        W5_complete=False,physical_pass=False,result_count=11,fixed_total=20,percent=55,
        retained_native='aux-wiring-checkpoint/AUXPowerCurrent.FCStd',
        measured={'worker_seconds':q['worker_seconds'],'actual_pairs':q['pairs'],
                  'contacts':0,'errors':0,'head_poses':9},
        new_native_parts=0,new_STL_exports=0,
        preserved_input_copies=copied,inherited_archive_references=references,
        limitation='Nominal cases/factory-tail guidance only. Complete custom feeds, all other wiring, retention, independent grips, levers/service, stock and one current native set remain OPEN.',
        source_sha256=dict(sorted(pins.items())),verification_seconds=time.monotonic()-tick)
    (OUT/'mta-interface-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'pins':len(pins),'archived_originals':len(copied),'inherited_archive_refs':len(references),
                      'selected':False,'percent':55,'verification_seconds':manifest['verification_seconds']}))
if __name__=='__main__':run()
