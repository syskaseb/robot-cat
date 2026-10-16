"""One replacement per physical identity and one removable source rail.

Do not count old snapshots as extra parts or add four rail laces twice:
the four former integral P_SYS grip laces are explicitly replaced.
"""
import json,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA


def compose(old,native):
    assert native['status']=='FIVE_OPERATING_NATIVE_PRINT_REPLACEMENTS_COMPLETE'
    rows={r['part']:r for r in native['parts']};exports={r['part']:r for r in native['exports']}
    assert set(rows)==set(exports)=={'UpperCarrier001','SourceGripRail','FrontRightFixedCarrier','RearLeftFixedCarrier','RearRightFixedCarrier'}
    prints=[]
    def replacement(name,previous=None):
        r=rows[name];e=exports[name]
        assert r['relocated_reopen'] and r['parameter_restore_mm']==[0,.2,0]
        assert e['printing']['fits_with_5mm_brim']
        p=dict(previous or {},part=name,path=e['path'],sha256=e['sha256'],native=r['native'],native_object=r['object'],quantity=1,printing=e['printing'])
        if previous:p['superseded_export']=previous['path']
        return p
    for r in old['prints']:prints.append(replacement(r['part'],r) if r['part'] in rows else dict(r))
    prints.append(replacement('SourceGripRail'))
    assert len(prints)==len({r['part'] for r in prints})==14
    lace=dict(prior_native_blanks=old['native_current_candidate_lacing_blanks'],retired_integral_P_SYS_blanks=4,
        replacement_detachable_rail_blanks=4,new_Upper_wire_blanks=24)
    lace['current_candidate_blanks']=lace['prior_native_blanks']-4+4+24
    lace['current_candidate_mm']=lace['current_candidate_blanks']*150
    assert lace['current_candidate_blanks']==85
    return prints,lace


def run():
    tick=time.monotonic();oldfile=OUT/'current-body-native-composition.json';nf=OUT/'operating-supports-native/manifest.json'
    old,native=[json.loads(f.read_text()) for f in (oldfile,nf)]
    for receipt in (old,native):
        for n,h in receipt['source_sha256'].items():assert SHA(ROOT/n)==h,n
    for r in native['models']:assert SHA(ROOT/r['path'])==r['sha256']
    prints,lace=compose(old,native)
    for r in prints:assert SHA(ROOT/r['path'])==r['sha256']
    files=[oldfile,nf,Path(__file__)]+[ROOT/r['path'] for r in prints]+[ROOT/r['path'] for r in native['models']]
    result=dict(status='ONE_CURRENT14_PRINT_OPERATING_COMPOSITION_NOT_WHOLE_RELEASE',prints=prints,
        physical_print_quantity=14,replacement_parent_quantity=4,new_separate_rail_quantity=1,lacing=lace,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files},worker_seconds=round(time.monotonic()-tick,3),
        rail_hardware_candidate=native['new_rail_hardware_candidate'],case_only_adhesive_patches=12,
        scope='Current body support subset only, not total cat part count. No duplicate Frames/Upper or historical snapshots in quantities.',
        selected=False,stock_selected=False,W5_complete=False,physical_pass=False)
    f=OUT/'current-operating-native-composition.json';f.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(prints=14,lacing=lace,seconds=result['worker_seconds'])))


if __name__=='__main__':run()
