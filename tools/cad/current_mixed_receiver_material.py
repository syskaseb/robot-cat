"""Materialize only the pinned, accepted bolted/mixed receiver layout.

RR cap screw replaces its wrapping tie. No historical Frame is cut.
"""
import copy,json
from pathlib import Path
from build_front_fixed_port_clearance import placement
from plan_bolted_receiver_layout import material
from plan_body36_receiver_space import shared_context,P


def prepare():
    file=P.OUT/'receiver-joint-selection.json';selection=json.loads(file.read_text())
    assert selection['status']=='BOLTED22_RECEIVER_JOINT_SELECTION_CLEAR_MIDDLES_OPEN'
    assert selection['solver']['status']=='solution' and not selection['errors']
    for n,h in selection['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    domain_file=P.ROOT/selection['domain_receipt'];domains=json.loads(domain_file.read_text())
    options=copy.deepcopy(domains['qualified_options'])
    if selection['override_receipt']:
        extension=json.loads((P.ROOT/selection['override_receipt']).read_text())
        options.update(extension['replacement_options'])
    grips={k:v for k,v in domains.items() if k not in ('qualified_options','groups')}
    grips.update(status='BOLTED36_RECEIVER_LAYOUT_JOINT_CLEAR_MIDDLES_OPEN',
        groups={n:options[n][i] for n,i in selection['selected_options'].items()},source_sha256=selection['source_sha256'])
    assert len(grips['groups'])==22
    assert sorted(n for q in grips['groups'].values() for n in q['wires'])==sorted(
        r['wire'] for r in json.loads((P.OUT/'body36-current-contract.json').read_text())['rows'])
    for n,h in grips['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,wires,pins,_=shared_context();targets={n:s for n,s in targets.items() if not n.startswith('Receiver_')}
    assert not grips['frame_passages'], 'Unexpected historical Frame cut'
    pins.update(grips['source_sha256'])
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (file,domain_file,Path(__file__))})
    return targets,wires,pins,grips
