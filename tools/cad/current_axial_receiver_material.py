"""Pinned current receiver context for downstream rooted-arm planning.

Reuses the received integration proof and exact retained parent subsets. The
old body-fanout file/native documents are immutable historical inputs.
"""
import json
from pathlib import Path
import core_receiver_port as T
import check_near_axis_hip_sources as C
P=C.P


def prepare_context(plan):
    proof=P.OUT/'axial-source-receiver-integration.json';receipt=json.loads(proof.read_text())
    assert receipt['status']=='FOUR_SOURCES_TWELVE_BREAKOUTS_TWENTY_RECEIVER_GRIPS_SAMPLED_CLEAR_ROOT_ARMS_OPEN'
    assert len(receipt['completed_fans'])==12 and not receipt['contacts'] and not receipt['errors']
    for name,digest in receipt['source_sha256'].items():assert P.SHA(P.ROOT/name)==digest,name
    result=C.prepare_context(plan)
    targets,old,pins,family,axes,own,bare,files,subsets=result
    layout=P.OUT/'body-receiver-relief-layout.json';gripsfile=P.OUT/'receiver-relief-approach-plan.json'
    current,grips=[json.loads(f.read_text()) for f in (layout,gripsfile)]
    old['body/W024']=(P.wire(current['routes']['W024']['parts']),1)
    for name,q in grips['grips'].items():
        profile=T.build(q['land'],q['normal'],q['offset']);goal=profile['arrival_world_mm']
        profile['seed']=P.box([v-2 for v in goal]+[v+2 for v in goal])
        for kind in ('body','band','seed'):targets['Receiver_'+name+'/'+kind]=profile[kind]
    files.extend([proof,layout,gripsfile,Path(__file__),Path(T.__file__)])
    return result
