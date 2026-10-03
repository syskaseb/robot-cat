"""One shared release after native local Cover edge clearance.

Reuse only completed R15 two-millimetre result and unchanged subset proofs;
new Cover is a native Cut of its exact old source. Higher poses all checked.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r15.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r15_definition');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r15','servo-fuse-bank-fixed-rr-lift-r16')
code=code.replace('servo-fuse-cover-fixed-guard-service-r1','servo-fuse-cover-deck-edge-service-r2')
marker="    assert module['BankLeft'].cut(originalleft).Volume<1e-5"
assert marker in code
code=code.replace(marker,"""    reusepath=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r15/checks.json'
    pins[reusepath.relative_to(ROOT).as_posix()]=sha(reusepath);reuse=json.loads(reusepath.read_text(encoding='utf-8'))
    assert reuse['completed_clear_lifts_mm']==[2] and not reuse['errors'] and len(reuse['hits'])==1
    assert (reuse['hits'][0]['phase'],reuse['hits'][0]['part'],reuse['hits'][0]['owner'])==('sampled_lift_5','Cover','CandidateDeck')
    for rel,h in reuse['source_sha256'].items():
        if rel in pins:assert pins[rel]==h,rel
    edgepath=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-deck-edge-service-r2/checks.json'
    pins[edgepath.relative_to(ROOT).as_posix()]=sha(edgepath);edge=json.loads(edgepath.read_text(encoding='utf-8'))
    assert edge['subtractive_by_native_construction'] and edge['exports'][0]['relocated_reopen']
    assert edge['parent_cover_brep'] in reuse['source_sha256']
    assert edge['parent_cover_brep_sha256']==reuse['source_sha256'][edge['parent_cover_brep']]
    assert sha(ROOT/edge['parent_cover_brep'])==edge['parent_cover_brep_sha256']
    print('R15_UNCHANGED_LEFT_SUBSET_PROOF_REUSED',flush=True)""")
code=code.replace('    for lift in lifts:',"    for lift in lifts:\n        if lift==2:\n            completed.append(2);print('R15_FULL_2MM_REUSED_SUBTRACTIVE_COVER',flush=True);continue")
code=code.replace('hits=hits,errors=errors,pairs=pairs,','hits=hits,errors=errors,pairs=pairs,reused_R15_full_clear_lifts_mm=[2],Cover_reuse_basis="Exact parent hash; native Cut adds no material; no other interface changed",')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
