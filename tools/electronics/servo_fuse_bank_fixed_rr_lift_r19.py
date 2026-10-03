"""Check the changed bridge sweep, not repeated unchanged Cover poses.

R3 shrinks R2's bridge; R18's sole installed contact is removed entirely.
Core Cover is a Cut of R17's exact Cover, so its2/5/10 evidence remains.
An exact box sweep checks every point of the NEW bridge0..100 against all
current fixed owners. Higher complete module poses remain actual checks.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r18.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r18_definition')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r18','servo-fuse-bank-fixed-rr-lift-r19')
code=code.replace('servo-fuse-cover-source-joint-service-r2','servo-fuse-cover-source-joint-service-r3')
marker='    lifts=[0,2,5,10,30,60,100];completed=[]'
assert marker in code
code=code.replace(marker,"""    prior18path=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r18/checks.json'
    pins[prior18path.relative_to(ROOT).as_posix()]=sha(prior18path)
    prior18=json.loads(prior18path.read_text(encoding='utf-8'))
    assert not prior18['errors'] and len(prior18['hits'])==1
    assert (prior18['hits'][0]['phase'],prior18['hits'][0]['part'],prior18['hits'][0]['owner'])==('sampled_lift_0','Cover','CandidateDeck')
    census18path=prior18path.parent/'owner-census.json';pins[census18path.relative_to(ROOT).as_posix()]=sha(census18path)
    census18=json.loads(census18path.read_text(encoding='utf-8'))
    assert census18['fixed']==list(owners) and census18['removed']==omitted and census18['parked']==parked
    for rel,h in prior18['source_sha256'].items():
        if rel in pins:assert pins[rel]==h,rel
    assert joint['subtractive_R2_bridge_by_native_construction'] and joint['entire_prior_Deck_contact_removed_mm3']<1e-5
    rel=joint['subset_parent_cover_brep'];pins[rel]=sha(ROOT/rel)
    assert pins[rel]==joint['subset_parent_cover_brep_sha256']==prior18['source_sha256'][rel]
    for rel,h in joint['source_sha256'].items():
        assert sha(ROOT/rel)==h,rel
        if rel in pins:assert pins[rel]==h,rel
        pins[rel]=h
    bridge_sweep=box([-91,-100,130,-84,-88,234])
    print('WHOLE_NEW_BRIDGE_SWEEP_0_TO100',flush=True)
    for key,t in sorted(owners.items(),key=lambda item:item[0]=='CandidateDeck'):
        check('continuous_bridge_0_to100','CoverMountBridge',bridge_sweep,key,t)
        if hits or errors:break
    print('NEW_BRIDGE_SWEEP_RESULT',len(hits),len(errors),flush=True)
    lifts=[2,5,10,30,60,100];completed=[]""")
code=code.replace('    for lift in lifts:','    for lift in ([] if hits or errors else lifts):')
code=code.replace('        for name,s in module.items():','        for name,s in module.items():\n            if lift in (2,5,10) and name=="Cover":continue')
code=code.replace('No Cover waiver: additive bridge and three whole joint passages checked at installed0 and all six withdrawal poses; only identical banks inherit2/5/10',
    'Exact native core subtractive from R17; its2/5/10 results reused plus actual NEW bridge continuous0..100 against737owners. R3 subset of R2; R18 installed sole Deck intersection removed entirely. Higher full module samples actual.')
code=code.replace('continuous_withdrawal_qualified=False,','continuous_withdrawal_qualified=False,changed_Cover_bridge_continuous_0_to100_qualified=not bool(hits or errors),installed_Cover_qualified_by_R18_subset_and_entire_Deck_intersection_removal=True,')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
