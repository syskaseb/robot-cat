"""Matched geometry, exact common with cheap conservative surface pruning.

R12's solid-distance optimization was withdrawn:12min in the first large
Deck pair. No R12 completion is inferred. Reuse ONLY R11's two full2mm bank
checks because only Cover changed; all fixed files/census must match.
For other pairs, disjoint per-face bounds plus no solid containment prove
separation. If any bound overlaps or classification is uncertain use the
original exact common(). No mesh approximation/collider exemption.
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
replace('servo-fuse-bank-fixed-rr-lift-r11','servo-fuse-bank-fixed-rr-lift-r13')
replace('servo-fuse-cover-main-service-r6','servo-fuse-cover-fixed-guard-service-r1')
marker='    assert len(parked)==24,parked'
replace(marker,"""    previouspath=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r11/checks.json'
    pins[previouspath.relative_to(ROOT).as_posix()]=sha(previouspath);previous=json.loads(previouspath.read_text(encoding='utf-8'))
    assert len(previous['hits'])==1 and previous['hits'][0]['part']=='Cover' and previous['hits'][0]['owner']=='FixedGuard' and not previous['errors']
    census=json.loads((previouspath.parent/'owner-census.json').read_text(encoding='utf-8'))
    assert census['fixed']==list(owners) and census['removed']==omitted and census['parked']==parked
    for rel,h in previous['source_sha256'].items():
        if rel in pins and 'servo-fuse-cover-main-service-r6' not in rel:assert pins[rel]==h,rel
    assert len(parked)==24,parked""")
replace('    hits=[];errors=[];pairs=0',"""    hits=[];errors=[];pairs=0;surface_pruned=0;exact_common=0
    facecache={k:[f.BoundBox for f in t.Faces] for k,t in owners.items()}
    def separated(s,key,t):
        try:
            if any(a.intersect(b) for a in (f.BoundBox for f in s.Faces) for b in facecache[key]):return False
            # Test every connected solid component, not one vertex of a
            # compound: nesting has overlap despite disjoint boundaries.
            if not s.Solids or not t.Solids:return False
            for a,b in ((s,t),(t,s)):
                for component in a.Solids:
                    if b.isInside(component.Vertexes[0].Point,1e-7,True):return False
            return True
        except Exception:return False
    # Required algorithm sanity: actual overlapping/nested solids cannot
    # be pruned just because their whole-shape bounds are conservative.
    outer=box([0,0,0,10,10,10]);facecache['synthetic']=[f.BoundBox for f in outer.Faces]
    synthetic=[]
    for b,want_clear in [([2,2,2,3,3,3],False),([9,2,2,11,3,3],False),([10,2,2,11,3,3],False),([11,2,2,12,3,3],True)]:
        q=box(b);clear=separated(q,'synthetic',outer);volume=q.common(outer).Volume
        assert clear==want_clear,(b,clear,volume);synthetic.append(dict(box_mm=b,separated=clear,common_mm3=volume))
    del facecache['synthetic']""")
replace('        nonlocal pairs','        nonlocal pairs,surface_pruned,exact_common')
replace('            c=s.common(t)',"""            if separated(s,key,t):surface_pruned+=1;return
            exact_common+=1
            c=s.common(t)""")
replace('        for name,s in module.items():','        for name,s in module.items():\n            if lift==2 and name in ("BankRight","BankLeft"):continue')
replace('hits=hits,errors=errors,pairs=pairs,','hits=hits,errors=errors,pairs=pairs,surface_bounds_and_containment_pruned=surface_pruned,exact_common_pairs=exact_common,surface_kernel_validation=synthetic,reused_R11_clear_at_2mm=["BankRight","BankLeft"],')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
