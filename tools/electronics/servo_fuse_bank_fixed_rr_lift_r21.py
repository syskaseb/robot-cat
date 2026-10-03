"""Whole paired offset mount, with the new fixed bracket in the owner set.

R20 proved the unchanged arch sweep but rejected the old tab at30mm. The
new Cover is a native Cut of it; check new fixed bracket, installed mate,
all changed interactions and the remaining complete higher module poses.
"""
from pathlib import Path
import runpy
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r20.py')
code=runpy.run_path(str(parent),run_name='service_definition')['code']
code=code.replace('servo-fuse-bank-fixed-rr-lift-r20','servo-fuse-bank-fixed-rr-lift-r21')
marker="    module['Cover']=load('hardware/cad/studies/servo-fuse-cover-source-joint-service-r5/Cover_WORLD.brep')"
assert marker in code
code=code.replace(marker,marker+"""
    pairedpath=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-offset-mount-native-r2/checks.json'
    pins[pairedpath.relative_to(ROOT).as_posix()]=sha(pairedpath)
    paired=json.loads(pairedpath.read_text(encoding='utf-8'))
    assert paired['cover_subtractive_by_native_construction'] and paired['new_Cover_bearing_missing_mm3']<1e-5
    assert all(r['relocated_reopen'] and r['closed_STL'] for r in paired['exports'])
    assert paired['cover_parent_sha256']==pins[paired['cover_parent']]
    for rel,h in paired['source_sha256'].items():assert sha(ROOT/rel)==h,rel;pins[rel]=h
    module['Cover']=load('hardware/cad/studies/servo-fuse-cover-offset-mount-native-r2/Cover_WORLD.brep')
    changed_bracket_key='hardware/electronics/full-cat/servo-fuse-cover-neighbors-r1/CoverBracket_-84_-1'
    assert changed_bracket_key in owners
    owners[changed_bracket_key]=load('hardware/cad/studies/servo-fuse-cover-offset-mount-native-r2/Bracket_WORLD.brep')
    offset_bracket=owners[changed_bracket_key]
""")
start=code.index("    print('WHOLE_NEW_ARCH_SWEEP_0_TO100'")
end=code.index('    lifts=[2,5,10,30,60,100];completed=[]',start)
code=code[:start]+"""    prior20path=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r20/checks.json'
    pins[prior20path.relative_to(ROOT).as_posix()]=sha(prior20path)
    prior20=json.loads(prior20path.read_text(encoding='utf-8'))
    assert prior20['completed_clear_lifts_mm']==[2,5,10] and not prior20['errors'] and len(prior20['hits'])==1
    assert (prior20['hits'][0]['phase'],prior20['hits'][0]['part'],prior20['hits'][0]['owner'])==('sampled_lift_30','Cover','CandidateDeck')
    for rel,h in prior20['source_sha256'].items():
        if rel in pins:assert pins[rel]==h,rel
    # The R20 arch loop finished before the sole later sampled conflict.
    # New fixed bracket is entirely below each unchanged arch primitive.
    assert offset_bracket.BoundBox.ZMax < min(b[2] for b in joint['native_service_arch_boxes_mm'])
    for key,t in owners.items():
        if key==changed_bracket_key:continue
        check('changed_fixed_bracket_installed','OffsetCoverBracket',offset_bracket,key,t)
        if hits or errors:break
    for lift in ([] if hits or errors else [0,2,5,10,30,60,100]):
        for name,s in module.items():
            q=s.copy();q.translate(A.Vector(0,0,lift))
            check('changed_bracket_lift_'+str(lift),name,q,changed_bracket_key,offset_bracket)
            if hits or errors:break
        if hits or errors:break
    print('CHANGED_OFFSET_BRACKET_RESULT',len(hits),len(errors),flush=True)
"""+code[end:]
code=code.replace('if lift in (0,2,5,10) and name in ("BankRight","BankLeft"):continue',
    'if lift in (0,2,5,10,30) and name in ("BankRight","BankLeft"):continue')
code=code.replace('continuous_withdrawal_qualified=False,',
    'continuous_withdrawal_qualified=False,offset_cover_bracket_source=pairedpath.relative_to(ROOT).as_posix(),front_left_Cover_axis_mm=paired["front_left_new_axis_mm"],fixed_bracket_owner_replaced=changed_bracket_key,reused_R20_arch_sweep_0_to100=True,reused_R20_identical_banks_30mm=True,')
code=code.replace('Higher full module samples actual.',
    'R21 native Cut removes obsolete tab, replaces fixed bracket. Every new bracket/static owner and module interaction checked. R20 unchanged banks30mm inherited; higher changed Cover/full remaining poses actual.')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
