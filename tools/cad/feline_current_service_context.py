"""Overlay received body deltas on the historical partial recovery scene.

No archive discovery, geometry rebuild, or claim of full scene coverage.
Call after loading the recovery cache, before adding new service proposals.
"""
import json
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load

RECEIPTS = (
    'n01-current-W009-complete-body-plan.json',
    'n01-current-W020-complete-body-plan.json',
    'n01-current-W022-complete-body-plan.json',
    'n01-current-W024-shared-complete-body-plan.json',
    'n01-current-W047-complete-body-plan.json',
    'n01-current-W069-complete-body-plan.json',
    'n01-FR-W031-W033-common-body-plan.json',
    'n01-current-W035-retained-source-body-plan.json',
    'n01-W046-original-prefix-portal-body.json',
)


def overlay(scene, metadata):
    result=dict(scene); meta=dict(metadata); owners={}; pins={}; excluded=[]
    for filename in RECEIPTS:
        path=OUT/filename; doc=json.loads(path.read_text())
        assert not doc['N01_complete'] and not doc['physical_pass']
        assert all(c['ok'] for c in doc['checks'].values()), filename
        pins[path.relative_to(ROOT).as_posix()]=sha(path)
        # load verifies bundle and every member SHA, not a new CAD evaluation.
        shapes=load(doc)
        for row in doc['geometry']:
            name=row['name']
            if name.startswith('MotionProof:'):
                excluded.append(name); continue
            assert name not in owners, ('Ambiguous current owner',name)
            owners[name]=dict(receipt=filename,sha256=row['sha256'])
            result[name]=shapes[name]
            kind=row.get('kind')
            if name.startswith(('CurrentMiddle:','VerticalCuff:','FLArcCuff:')) or ':wire:' in name:
                kind='actual_wire'
            meta[name]={**meta.get(name,{}),**({'kind':kind} if kind else {})}
    report=dict(status='RECEIVED_BODY_OVERLAY_NOT_FULL_SCENE',owners=owners,
        source_sha256=pins,excluded_proof_shapes=excluded,
        added_names=sorted(set(result)-set(scene)),count_before=len(scene),
        count_after=len(result),whole_scene_received=False,N01_complete=False,
        physical_pass=False,canonical_BUS_and_other_missing_actors_still_required=True)
    return result,meta,report
