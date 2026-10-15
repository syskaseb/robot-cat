"""Reuse five qualified end-support geometries, not old route acceptance.

The component receipt covers its recorded candidate curves only. New route
consumers must test these SAME bodies/bands against every proposed curve.
No old macro file is pinned as a live self-reference in a new route receipt.
"""
import json
from pathlib import Path
from current_g2_feed_restraints import geometry as g2_geometry
from current_fl_ground_feed import geometry as fl_geometry
from plan_body36_receiver_space import P


def prepare():
    f=P.OUT/'remaining-fixed-feed-checks.json';proof=json.loads(f.read_text())
    assert proof['status']=='FIVE_REMAINING_FIXED_FEEDS_COMPONENT_GATE_CLEAR' and not proof['errors']
    assert len(proof['components'])==6 and all(not r['contacts'] for r in proof['components'])
    files=[Path(__file__).with_name(n) for n in ('current_g2_feed_restraints.py','current_fl_ground_feed.py')]
    for source in files:
        assert proof['source_sha256'][source.relative_to(P.ROOT).as_posix()]==P.SHA(source),source
    groups=g2_geometry();groups['FL_G']=fl_geometry()
    assert {n:q['recipe'] for n,q in groups.items()}==proof['recipes'],'Changed fixed feed material'
    material={'FixedFeed/'+n+'/'+k:q[k] for n,q in groups.items() for k in ('body','band')}
    return material,{p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in files+[f,Path(__file__)]}
