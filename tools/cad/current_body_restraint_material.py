"""One current G1/G2/FL_G obstacle set for subsequent whole-route gates.

Reuse unchanged geometry ONLY, never claim the previous route-scene coverage
also covers future wires. Every new whole curve must clear all12 components.
"""
import json
from pathlib import Path
from current_fixed_feed_material import prepare as fixed
from plan_body36_receiver_space import P


def prepare():
    material,pins=fixed()
    proof_file=P.OUT/'g1-rooted-carrier-plan.json';proof=json.loads(proof_file.read_text())
    assert proof['status']=='G1_ROOTED_COMPONENT_GATE_CLEAR' and not proof['errors']
    assert len(proof['components'])==6 and all(not r['contact'] for r in proof['components'])
    from plan_g1_rooted_carrier import geometry
    source=Path(__file__).with_name('plan_g1_rooted_carrier.py')
    native=P.OUT/'U1InterfaceCarriersCurrent.FCStd'
    for f in (source,native):assert proof['source_sha256'][f.relative_to(P.ROOT).as_posix()]==P.SHA(f),f
    body,bands,recipe=geometry(direct_upper=True,upper_portal=True,open_web=True)
    assert recipe==proof['recipe'],'Changed G1 print geometry'
    material['G1/carrier']=body
    material.update({'G1/'+n:band for n,band in bands.items()})
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (proof_file,source,native,Path(__file__))})
    return material,pins
