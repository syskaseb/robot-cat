"""Shared withdrawal after full joint passages and native mount bridge.

The Cover is additive, so all its poses including installed0mm are checked.
Only identical banks inherit R17 clear2/5/10; no Cover subset waiver.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r17.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r17_definition')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r17','servo-fuse-bank-fixed-rr-lift-r18')
marker="    assert leftnative['deck_subtractive_by_native_construction']"
assert marker in code
code=code.replace(marker,"""    prior17path=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r17/checks.json'
    pins[prior17path.relative_to(ROOT).as_posix()]=sha(prior17path)
    prior17=json.loads(prior17path.read_text(encoding='utf-8'))
    assert prior17['completed_clear_lifts_mm']==[2,5,10] and not prior17['errors']
    assert prior17['hits'][0]['owner']=='RetainedFeed/W042_BareExtension_DESIGN'
    for rel,h in prior17['source_sha256'].items():
        if rel in pins:assert pins[rel]==h,rel
    jointpath=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-source-joint-service-r2/checks.json'
    pins[jointpath.relative_to(ROOT).as_posix()]=sha(jointpath)
    joint=json.loads(jointpath.read_text(encoding='utf-8'))
    assert not joint['subtractive_by_native_construction'] and joint['exports'][0]['relocated_reopen']
    assert pins[joint['parent_cover_brep']]==joint['parent_cover_brep_sha256']
    module['Cover']=load('hardware/cad/studies/servo-fuse-cover-source-joint-service-r2/Cover_WORLD.brep')
    assert leftnative['deck_subtractive_by_native_construction']""")
skip="""        if lift in (2,5):
            completed.append(lift);print('R15_FULL_2MM_REUSED_SUBTRACTIVE_COVER',flush=True);continue
"""
assert skip in code
code=code.replace(skip,'')
code=code.replace('lifts=[2,5,10,30,60,100]','lifts=[0,2,5,10,30,60,100]')
code=code.replace('if lift==2 and name in ("BankRight","BankLeft"):continue','if lift in (0,2,5,10) and name in ("BankRight","BankLeft"):continue')
code=code.replace('        completed.append(lift)','        if lift>0:completed.append(lift)')
code=code.replace('reused_R16_full_clear_lifts_mm=[2,5]','reused_R17_identical_banks_clear_lifts_mm=[2,5,10]')
code=code.replace('Cover_reuse_basis="Exact Cover/BankRight parent hashes; native Cuts add no material; remaining owners identical"','Cover_reuse_basis="No Cover waiver: additive bridge and three whole joint passages checked at installed0 and all six withdrawal poses; only identical banks inherit2/5/10"')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
