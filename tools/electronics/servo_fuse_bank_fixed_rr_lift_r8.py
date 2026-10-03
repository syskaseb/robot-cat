"""One shared release with accepted bottom-open Cover and four WAGO straps.

Keep all actual fixed wires/closed blocks and the mixed accepted body straps.
Only the explicitly cut33service ties disappear. Cover R7 lip conflict is
not waived; receive its finished native replacement before running this.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r7.py')
ns=dict(__file__=str(parent),__name__='lift_r7_definition_only')
exec(compile(parent.read_text(encoding='utf-8'),str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-fixed-rr-lift-r7','servo-fuse-bank-fixed-rr-lift-r8')
marker="    assert len(parked)==24,parked"
assert marker in code
code=code.replace(marker,"""    coverpath=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-rr-fixed-service-r1/checks.json'
    pins[coverpath.relative_to(ROOT).as_posix()]=sha(coverpath)
    covers=json.loads(coverpath.read_text(encoding='utf-8'));assert len(covers['exports'])==1 and covers['exports'][0]['relocated_reopen']
    module['Cover']=load('hardware/cad/studies/servo-fuse-cover-rr-fixed-service-r1/Cover_WORLD.brep')
    wp=ROOT/'hardware/electronics/full-cat/servo-fuse-p-wago-retention-r3/checks.json';pins[wp.relative_to(ROOT).as_posix()]=sha(wp)
    wago=json.loads(wp.read_text(encoding='utf-8'));assert len(wago['blocks'])==4 and wago['static_contacts']==0 and not wago['errors']
    for row in wago['blocks']:
        for rel in row['geometry']:owners['PWagoTie/'+Path(rel).stem]=load(rel)
    pins['tools/electronics/servo_fuse_bank_fixed_rr_lift_r7.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_fixed_rr_lift_r7.py')
    assert len(parked)==24,parked""")
code=code.replace("installed_changed_interfaces_source='servo-fuse-fr-source-fixed-deck-r3/checks.json'", "installed_changed_interfaces_source='servo-fuse-cover-rr-fixed-service-r1/checks.json',P_WAGO_static_source='servo-fuse-p-wago-retention-r3/checks.json',P_WAGO_body_ties_stationary=4")
code=code.replace('    lifts=[2,10,100];completed=[]', '    lifts=[2,5,10,30,60,100];completed=[]')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
