"""Whole shared release after one native inner passage for stationary FR loop."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r16.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r16_definition')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r16','servo-fuse-bank-fixed-rr-lift-r17')
marker="    print('R15_UNCHANGED_LEFT_SUBSET_PROOF_REUSED',flush=True)"
assert marker in code
code=code.replace(marker,marker+"""
    prior16path=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r16/checks.json'
    pins[prior16path.relative_to(ROOT).as_posix()]=sha(prior16path)
    prior16=json.loads(prior16path.read_text(encoding='utf-8'))
    assert prior16['completed_clear_lifts_mm']==[2,5] and not prior16['errors']
    for rel,h in prior16['source_sha256'].items():
        if rel in pins:assert pins[rel]==h,rel
    innerpath=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-inner-feed-service-r1/checks.json'
    pins[innerpath.relative_to(ROOT).as_posix()]=sha(innerpath)
    inner=json.loads(innerpath.read_text(encoding='utf-8'))
    assert inner['subtractive_by_native_construction'] and inner['exports'][0]['relocated_reopen']
    assert pins[inner['parent_bank_brep']]==inner['parent_bank_brep_sha256']
    module['BankRight']=load('hardware/cad/studies/servo-fuse-bank-inner-feed-service-r1/BankRight_WORLD.brep')
""")
code=code.replace('        if lift==2:', '        if lift in (2,5):')
code=code.replace('completed.append(2);', 'completed.append(lift);')
code=code.replace('reused_R15_full_clear_lifts_mm=[2]', 'reused_R16_full_clear_lifts_mm=[2,5]')
code=code.replace('Exact parent hash; native Cut adds no material; no other interface changed',
                  'Exact Cover/BankRight parent hashes; native Cuts add no material; remaining owners identical')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
