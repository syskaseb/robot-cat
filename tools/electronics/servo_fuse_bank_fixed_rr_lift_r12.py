"""Whole module with matched native fixed-channel Cover and exact gap pruning.

No collider exemption. An OCCT positive solid distance is a separation
certificate; intersecting/touching pairs still receive exact common().
Synthetic nesting/penetration/touch/gap checks guard this optimization.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_fixed_rr_lift_r11.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r11_definition_only');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code']
def replace(a,b):
    global code
    assert a in code,a[:140]
    code=code.replace(a,b)
replace('servo-fuse-bank-fixed-rr-lift-r11','servo-fuse-bank-fixed-rr-lift-r12')
replace('servo-fuse-cover-main-service-r6','servo-fuse-cover-fixed-guard-service-r1')
replace('    hits=[];errors=[];pairs=0',"""    # Verify the kernel treats nested solids as distance0, not merely their
    # boundary distance; otherwise DO NOT use distance as a prune.
    outer=box([0,0,0,10,10,10])
    synthetic=[]
    for b,want_zero in [([2,2,2,3,3,3],True),([9,2,2,11,3,3],True),([10,2,2,11,3,3],True),([11,2,2,12,3,3],False)]:
        q=box(b);distance=outer.distToShape(q)[0];volume=outer.common(q).Volume
        assert (distance<1e-7)==want_zero,(b,distance,volume)
        synthetic.append(dict(box_mm=b,distance_mm=distance,common_mm3=volume))
    hits=[];errors=[];pairs=0;gap_pruned=0;exact_common=0""")
replace('        nonlocal pairs','        nonlocal pairs,gap_pruned,exact_common')
replace('            c=s.common(t)',"""            try:distance=s.distToShape(t)[0]
            except Exception:distance=0
            if math.isfinite(distance) and distance>1e-7:
                gap_pruned+=1;return
            exact_common+=1
            c=s.common(t)""")
replace('hits=hits,errors=errors,pairs=pairs,','hits=hits,errors=errors,pairs=pairs,positive_exact_gap_pruned=gap_pruned,exact_common_pairs=exact_common,distance_kernel_validation=synthetic,')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
