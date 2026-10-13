"""Package the completed native support set; reject partial output or print approval."""
import hashlib,json,time
from pathlib import Path
from release_check import verify,REQUIRED_GATES

ROOT=Path(__file__).resolve().parents[2]
BODY=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'
OUT=BODY/'remaining-supports'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def require_complete(native,material):
    assert native['status']=='REMAINING36LAND_SUPPORT_SET_NATIVE_PREPARED_W5_OPEN'
    assert len(native['native_documents'])==3 and len(native['exports'])==12
    assert native['relocated_reopen'] and native['parameter_restore_mm']==[4,4.2,4]
    assert len({r['part'] for r in native['exports']})==12
    assert all(r['quantity']==1 and max(r['size_mm'])+10<256 for r in native['exports'])
    assert native['installed_new_hardware']=={'independent_T18I_bands':36,'provisional_case_bonds':4,'new_screws':0}
    assert material['status']=='COMBINED_SUPPORT_MATERIAL_CLEAR_NATIVE_OPEN'
    assert len(material['groups'])==12 and not material['contacts'] and not material['errors']
    assert not native['physical_pass'] and not native['W5_complete']

def run():
    start=time.monotonic();nf=OUT/'manifest.json';gf=BODY/'remaining-support-shared-material.json'
    native,material=[json.loads(f.read_text()) for f in (nf,gf)]
    require_complete(native,material)
    pins={}
    for receipt in (native,material):
        for name,digest in receipt['source_sha256'].items():
            assert sha(ROOT/name)==digest,name
            pins[name]=digest
    for row in native['native_documents']+native['exports']:
        assert sha(ROOT/row['path'])==row['sha256'],row['path']
        pins[row['path']]=row['sha256']
    for f in (nf,gf,Path(__file__),ROOT/'tools/cad/resume_remaining_support_gate.py',
              ROOT/'tools/cad/material_pair_receipts.py',ROOT/'tools/cad/component_pair_receipts.py',
              ROOT/'tools/cad/exact_pair_receipts.py'):
        pins[f.relative_to(ROOT).as_posix()]=sha(f)
    reasons=dict(geometry='Local12support set: valid single solids, native material equivalence and sampled moving contacts. Not whole robot or continuous sweep.',
        assembly='Inherited mounting interfaces retained; four new case bonds provisional. Whole harness assembly and body fanouts still open.',
        fit='Nominal lands, sleeves, ties and cases require delivered-part and PETG coupons.',
        petg='12 closed exports have5mm allowance within256cube; no slicer/physical print qualification.',
        loads='No measured bond peel/creep or printed-part load acceptance.',
        electrical='E3 and actual conductor/insulation/pin-cavity qualification remain open.',
        service='Local band-cut removal recipe only; whole final harness service not accepted.')
    report=dict(schema_version=1,readiness='prototype',scope='Remaining36land support set only; no phase score or wholeW5 acceptance',
        files=[dict(path=n,sha256=h) for n,h in sorted(pins.items())],
        gates={k:dict(status='pass' if k=='geometry' else 'open',reason=reasons[k],
            evidence=[nf.relative_to(ROOT).as_posix(),gf.relative_to(ROOT).as_posix()] if k=='geometry' else []) for k in REQUIRED_GATES},
        source_commit='ab9c7f2',selected_as_whole_robot=False,physical_pass=False)
    result=verify(ROOT,report);assert result['integrity_ok'],result
    strict=verify(ROOT,report,True);assert not strict['integrity_ok'],'Must not approve printing'
    report['verification_seconds']=round(time.monotonic()-start,3)
    (OUT/'release.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(integrity=result,print_ready=False,seconds=report['verification_seconds'])))

if __name__=='__main__':run()
