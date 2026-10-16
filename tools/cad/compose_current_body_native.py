"""One13-print current candidate set; four replacements, never duplicates."""
import json,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA


def compose(old,native):
    assert native['status']=='FOUR_CURRENT_FRAMES_THIRTY_SADDLES_NATIVE_COMPLETE'
    rows={r['part']:r for r in native['parts']};exports={r['part']:r for r in native['exports']}
    assert len(rows)==len(exports)==4
    prints=[]
    for r in old['prints']:
        p=dict(r)
        if r['part'] in rows:
            n=rows[r['part']];e=exports[r['part']]
            assert n['relocated_reopen'] and n['original_material_preserved']
            assert n['pilot_Z_allowance_restore_mm']==[0,.2,0] and e['printing']['fits_with_5mm_brim']
            p.update(path=e['path'],sha256=e['sha256'],native=native['native'],native_object=n['object'],
                printing=e['printing'],superseded_export=r['path'],remaining_saddle_groups=len(n['groups']))
        elif not p['native'].startswith('hardware/'):
            p['native']=(OUT/p['native']).relative_to(ROOT).as_posix()
        prints.append(p)
    assert len(prints)==len({r['part'] for r in prints})==13
    assert sum(r.get('remaining_saddle_groups',0) for r in prints)==30
    return prints


def run():
    tick=time.monotonic();oldfile=OUT/'current-body-source-native-set.json';nf=OUT/'remaining-frame-saddles-native/manifest.json'
    old,native=[json.loads(f.read_text()) for f in (oldfile,nf)]
    for p in (old,native):
        for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert SHA(ROOT/native['native'])==native['native_sha256']
    prints=compose(old,native)
    for r in prints:assert SHA(ROOT/r['path'])==r['sha256']
    files=[oldfile,nf,ROOT/native['native'],Path(__file__)]+[ROOT/r['path'] for r in prints]
    result=dict(status='CURRENT13_PRINT_COMPOSITION_WITH_THIRTY_FRAME_SADDLES_NOT_WHOLE_RELEASE',prints=prints,
        replacement_Frame_quantity=4,replacement_UpperCarrier_quantity=1,replacement_LeftRiser_quantity=1,CAP_quantity=7,
        physical_print_quantity=13,new_separate_prints=0,
        prior_lacing_candidate_blanks=old['lacing_candidate_blanks'],new_Frame_lacing_candidate_blanks=30,
        native_current_candidate_lacing_blanks=old['lacing_candidate_blanks']+30,
        candidate_lacing_mm=(old['lacing_candidate_blanks']+30)*150,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files},worker_seconds=round(time.monotonic()-tick,3),
        scope='One replacement print per identity; old snapshots remain provenance only, not extra physical parts. Upper24saddles/bank/service still pending.',
        selected=False,stock_selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
    f=OUT/'current-body-native-composition.json';f.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(prints=len(prints),Frame_groups=30,candidate_lacing_blanks=result['native_current_candidate_lacing_blanks'],seconds=result['worker_seconds'])))


if __name__=='__main__':run()
