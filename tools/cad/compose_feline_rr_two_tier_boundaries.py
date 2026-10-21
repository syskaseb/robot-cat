"""Adopt the coherent RR33 source/receiver, preserving246 electrical identities."""
import json,time,zipfile,hashlib
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_current_cuff_bays import current as parent
from compose_feline_integrated_boundaries import apply_updates
from feline_atomic_save import save_json

DEST=OUT/'n01-RR33-current-boundary-overlay.json'
RECEIPT=OUT/'n01-RR33-two-tier-ground-space.json'


def compose():
    tick=time.monotonic();_,rows,_=parent();byid={r['id']:r for r in rows};p=json.loads(RECEIPT.read_text())
    assert not p['N01_complete'] and all(r['ok'] for r in p['checks'].values())
    assert all(r['ok'] for r in p['outer'].values()) and sha(ROOT/p['bundle'])==p['bundle_sha256']
    wires={}
    with zipfile.ZipFile(ROOT/p['bundle']) as z:
        for r in p['geometry']:
            if not r['name'].startswith('Station:RR_G:wire:'):continue
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());wires[r['name']]=s
    updates={};receipt=RECEIPT.relative_to(ROOT).as_posix()
    for owner,r in p['plan']['source_recipes'].items():
        eid=r['end_id'];old=byid[eid];assert old['group']=='NineWireCuffRR'
        update=dict(current_restraint_receipt=receipt,shared_current_cuff_guide='RRFlatGuide')
        if r['wire'] in ('W072','W073','W074'):
            first=r['parts'][0];update.update(point_mm=first['start'],fixed_kinematic_seam_mm=first['start'],
                departure_axis=[-1,0,0],routing_exit_mm=first['end'],routing_exit_axis=[-1,0,0],
                prefix_geometry_owner=owner,source_prefix_length_mm=9.,jacket_grip9_mm=[first['start'],first['end']],
                full_grip_arclength_mm=[0,9],planned_body_capacity_path_owners=[owner,'RRDirectGround:'+r['wire']],
                moving_side_interface_CHANGED=True,full_flexible_kinematics_NOT_qualified=True)
        updates[eid]=update
    pose=p['plan']['receiver']
    def point(q):
        x,y,z=q;return [78.125+(y+79),-79-(x-78.125),z]
    for eid,v in pose['receiver_updates'].items():
        # This accepted receiver has ZERO translation, unlike an abandoned
        # intermediate. Match actual circular cap faces before adopting it.
        old=byid[eid];assert old['group']=='WAGO:RR_G'
        mouth=point(old['point_mm']);q=point(old['routing_exit_mm']);matches=[]
        for name,s in wires.items():
            if any(type(f.Surface).__name__=='Plane' and (f.CenterOfMass-A.Vector(*q)).Length<1e-6 for f in s.Faces):matches.append(name)
        assert len(matches)==1,(eid,matches)
        grip=[point(q) for q in old['jacket_grip9_mm']]
        updates[eid]=dict(point_mm=mouth,departure_axis=[1,0,0],routing_exit_mm=q,routing_exit_axis=[1,0,0],
            prefix_geometry_owner=matches[0],source_prefix_length_mm=12.25,jacket_grip9_mm=grip,
            current_restraint_receipt=receipt,current_group_root='RRGJointRoot',old_receiver_pose_retired=True,
            full_middle_route_accepted=False,complete_route_verified=False)
    complete=p['complete_body_portions'];assert set(complete)=={'W072/body','W073/body','W074/body'}
    for r in rows:
        if r['portion_id'] not in complete:continue
        updates.setdefault(r['id'],{}).update(full_middle_route_accepted=True,whole_portion_received=True,
            whole_portion_receipt=receipt,whole_body_length_mm=complete[r['portion_id']]['length_mm'],
            whole_factory900_and_moving_portion_NOT_received=True)
    resolved=apply_updates(rows,updates)
    assert len(resolved)==246 and len({r['portion_id'] for r in resolved})==123 and len(updates)==13
    return dict(status='CURRENT_RR33_THREE_BODY_PORTIONS_AND_ALL4_RECEIVER_ENDS_COMPOSED_NOT_N01',
        updates=updates,complete_body_portions=list(complete),source_sha256={
            receipt:sha(RECEIPT),p['bundle']:sha(ROOT/p['bundle']),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
            'tools/cad/compose_feline_current_cuff_bays.py':sha(ROOT/'tools/cad/compose_feline_current_cuff_bays.py')},
        physical_portions=123,ordinary_ends=246,N01_complete=False,physical_pass=False,native_changed=False,
        selected_SKUs_changed=False,W063_new_receiver_end_reroute_OPEN=True,worker_seconds=round(time.monotonic()-tick,3))


def current():
    base,rows,files=parent();p=json.loads(DEST.read_text())
    for name,h in p['source_sha256'].items():assert sha(ROOT/name)==h,name
    return base,apply_updates(rows,p['updates']),(*files,DEST)


if __name__=='__main__':
    assert not DEST.exists(),'Receive current overlay instead of regenerating'
    p=compose();save_json(DEST,p);print(p['status'],len(p['updates']),p['worker_seconds'])
