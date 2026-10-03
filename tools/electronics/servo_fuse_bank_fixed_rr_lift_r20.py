"""One full NEW native arch sweep plus unchanged core/sample evidence."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r19.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r19_definition')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r19','servo-fuse-bank-fixed-rr-lift-r20')
code=code.replace('servo-fuse-cover-source-joint-service-r3','servo-fuse-cover-source-joint-service-r5')
code=code.replace("assert joint['subtractive_R2_bridge_by_native_construction'] and joint['entire_prior_Deck_contact_removed_mm3']<1e-5","assert joint['installed_core_unchanged_R18'] and joint['entire_prior_Deck_contact_removed_mm3']<1e-5")
code=code.replace("rel=joint['subset_parent_cover_brep']","rel=joint['installed_core_R18_parent_cover']")
code=code.replace("joint['subset_parent_cover_brep_sha256']","joint['installed_core_R18_parent_cover_sha256']")
old="""    bridge_sweep=box([-91,-100,130,-84,-88,234])
    print('WHOLE_NEW_BRIDGE_SWEEP_0_TO100',flush=True)
    for key,t in sorted(owners.items(),key=lambda item:item[0]=='CandidateDeck'):
        check('continuous_bridge_0_to100','CoverMountBridge',bridge_sweep,key,t)
        if hits or errors:break"""
new="""    print('WHOLE_NEW_ARCH_SWEEP_0_TO100',flush=True)
    for number,b in enumerate(joint['native_service_arch_boxes_mm']):
        x,y,z,l,w,h=b;sweep=box([x,y,z,x+l,y+w,z+h+100])
        for key,t in sorted(owners.items(),key=lambda item:item[0]=='CandidateDeck'):
            check('continuous_arch_0_to100','CoverArch'+str(number),sweep,key,t)
            if hits or errors:break
        if hits or errors:break"""
assert old in code;code=code.replace(old,new)
code=code.replace('R3 subset of R2; R18 installed sole Deck intersection removed entirely.',
    'Exact same core and sleeve tools as R2; R18 installed core clear after entire Deck intersection removal. New arch checked independently0..100.')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
