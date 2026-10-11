"""Current coupled candidate guides, including qualified DATA and S0 changes.

These are planning guides with native/restraint/wholeW5 gates still open.
No qualified source or unchanged body proof is rerun by loading this scene.
"""
import json
from pathlib import Path
from current_full_harness_context import context as previous,W,Part
from plan_current_main_sources import ROOT,OUT,SHA

def context():
    reader,pins,targets,old=previous();pins.add(Path(__file__))
    for file,status in [('positive-source-manifest.json','FOUR_SOURCE_GUIDES_CLEAR_NATIVE_AND_S0_FIT_OPEN'),
                        ('data-bridges-checks.json','THREE_DATA_BRIDGES_SAMPLED_CLEAR_NATIVE_OPEN')]:
        f=OUT/file;r=json.loads(f.read_text());assert r['status']==status,(file,r['status'])
        for n,h in r['source_sha256'].items():assert SHA(ROOT/n)==h,n
        pins.add(f)
    for tag,names in [('positive-source',('W075','W066')),('data-bridges',('W007','W011','W012')),
                      ('s0-in-extension',('W076_FACTORY','W076_EXTENSION'))]:
        f=OUT/(tag+'-plan.json');p=json.loads(f.read_text());pins.add(f)
        old.update({n:(W.makewire(p['routes'][n]['parts']),p['routes'][n]['radius_mm']) for n in names})
    change=p['source_change'];ring=targets['S0_ring_IN'].copy()
    ring.rotate(W.A.Vector(*change['stud_centre_mm']),W.A.Vector(0,0,1),change['rotation_z_degrees'])
    assert ring.isValid();targets['S0_ring_IN']=ring
    targets['PostF0Splice_CP2']=W.box(p['post_F0']['casing_mm'])
    return reader,pins,targets,old
