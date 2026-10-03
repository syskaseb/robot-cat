"""Complete fixed front post: foot reaches parent Deck, thin trunk avoids FL.

R1 had a floating foot and a real W026 factory-wire intersection. Retain
the upper two-fastener interface but step the trunk outboard below150mm.
Actual bearing probes are INSIDE the solid, not outside its skin.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_guard_fixed_deck_r1.py')
code=parent.read_text(encoding='utf-8')
def replace(a,b):
    global code
    assert a in code,a
    code=code.replace(a,b)
replace('servo-fuse-guard-fixed-deck-r1','servo-fuse-guard-fixed-deck-r2')
replace("STOCKS=[('GuardFixedFoot',[-113.5,82,109,-94,88,113]),\n        ('GuardFixedFrontPost',[-113.5,85,111,-101,88,159])]", "STOCKS=[('GuardFixedFoot',[-113.5,82,109,-84,88,113]),\n        ('GuardFixedFrontPost',[-113.5,85,111,-104.5,88,153]),\n        ('GuardFixedHeadCap',[-113.5,85,150,-101,88,159])]")
replace('fixture=box(STOCKS[0][1]).fuse(box(STOCKS[1][1]));','fixture=box(STOCKS[0][1]).multiFuse([box(b) for _,b in STOCKS[1:]]);')
replace('V(x,82.9,z)','V(x,83,z)');replace('V(x,82.85,z)','V(x,82.95,z)');replace('V(0,5.1,0)','V(0,4.9,0)')
replace('embed=box([-98,82,109,-94,88,110])','embed=box([-88,82,109,-84,88,110])')
replace('common.Volume>1e-5','abs(common.Volume-embed.Volume)<1e-5 and all(abs(r[k]-r["ring_mm3"])<1e-5 for r in bearings for k in ("guard_head_ring_mm3","post_nut_ring_mm3"))')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
