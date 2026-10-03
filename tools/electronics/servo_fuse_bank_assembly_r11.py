"""One local order with preserved mounts and whole stationary-feed passage."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_assembly_r10.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
ns=dict(__file__=str(parent),__name__='assembly_r10_definition')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-assembly-r10','servo-fuse-bank-assembly-r11').replace('servo-fuse-bank-stock-budget-r11','servo-fuse-bank-stock-budget-r12').replace('servo-fuse-bank-fixed-rr-lift-r15','servo-fuse-bank-fixed-rr-lift-r17')
marker='    clips=read('
assert marker in code
code=code.replace(marker,"""    coveredge=read('hardware/electronics/full-cat/servo-fuse-cover-deck-edge-service-r2/checks.json')
    bankinner=read('hardware/electronics/full-cat/servo-fuse-bank-inner-feed-service-r1/checks.json')
    assert coveredge['exports'][0]['relocated_reopen'] and bankinner['exports'][0]['relocated_reopen']
    assert all(q['removed_mm3']<1e-5 for q in bankinner['protected_regions'])
    clips=read(""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
