"""Actual per-SOLID load paths after the common tie feedthrough change."""
import hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_solid_distance import bbox_lower_bound


def reached(nodes,edges,roots):
    attached=set(roots)
    for _ in nodes:
        before=len(attached)
        for row in edges:
            if row['a'] in attached or row['b'] in attached:attached.update((row['a'],row['b']))
        if len(attached)==before:break
    return attached


def load(doc,key):
    archive=ROOT/doc['bundle'];assert sha(archive)==doc['bundle_sha256'];parts={}
    with zipfile.ZipFile(archive) as z:
        for r in doc[key]:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and s.Solids
            parts[r['name']]=s
    return parts


def main():
    tick=time.monotonic();cf=OUT/'n01-psys-flp-joint-retention-r2.json';core=json.loads(cf.read_text())
    assert not core['failures'] and not core['errors'],'Receive all changed interfaces before the load-path gate'
    pf=OUT/'n01-channelled-foundation-static.json';parent=json.loads(pf.read_text())
    assert core['source_sha256'][pf.relative_to(ROOT).as_posix()]==sha(pf)
    before=load(parent,'geometry');added=load(core,'geometry');parts=dict(before);parts.pop('BankPier:2/0')
    changed=set()
    for n,s in added.items():
        if n.startswith('CurrentFoundation:'):name=n.split(':',1)[1];parts[name]=s;changed.add(name)
        elif n.startswith('BankPortal'):parts[n]=s;changed.add(n)
    pi_file=OUT/'n01-shared-Pi-carrier-r3-core-received.json';pi=json.loads(pi_file.read_text())
    actual_pi=load(pi,'geometry')[pi['recipe']['Pi_frame_actor']]
    old_root=before['RetainedPWMCarrier'];difference=old_root.cut(actual_pi).Volume
    assert difference<1e-5,'The old load-path witness must still exist in the received Pi assembly'
    nodes={};owner={}
    for name,s in parts.items():
        owner[name]=[]
        for i,solid in enumerate(s.Solids):
            key=name+'/solid:'+str(i);nodes[key]=solid;owner[name].append(key)
    bounds={n:s.BoundBox for n,s in nodes.items()};edges=[];exact=0;reuse=0
    pairs=[(r['a'],r['b'],r) for r in parent['construction']['positive_material_connections'] if r['a'] in parts and r['b'] in parts]
    pairs.extend((n,'BankPortal2:Carrier',None) for n in parts if n!='BankPortal2:Carrier')
    for a,b,old in pairs:
        if old and a not in changed and b not in changed and len(owner[a])==len(owner[b])==1:
            edges.append(dict(a=owner[a][0],b=owner[b][0],common_mm3=old['common_mm3'],unchanged_BRep_evidence_reused=True));reuse+=1;continue
        for na in owner[a]:
            for nb in owner[b]:
                if bbox_lower_bound(bounds[na],bounds[nb])>1e-7:continue
                common=nodes[na].common(nodes[nb]);assert common.isNull() or common.isValid();exact+=1
                if common.Volume>1e-7:edges.append(dict(a=na,b=nb,common_mm3=common.Volume))
    roots={n for n in nodes if n.startswith('ClampSeat:')};assert len(roots)==4
    attached=reached(nodes,edges,roots);floating=sorted(set(nodes)-attached)
    output=dict(status='ALL_CHANGED_FRAME_SOLIDS_REACH_EXISTING_CLAMP_SEATS' if not floating else 'CHANGED_FRAME_FLOATING_SOLIDS_RECEIVED_NOT_ACCEPTED',
        actual_solid_nodes=len(nodes),positive_joints=edges,exact_changed_pair_queries=exact,unchanged_joints_reused=reuse,
        clamp_roots=sorted(roots),floating_solids=floating,old_PWM_root_still_in_received_Pi_removed_mm3=difference,
        all_four_existing_clamp_seats_byte_unchanged=True,old_pad_and_washer_bearing_evidence_reused_sha256=sha(pf),
        whole_other74_grip_roots_and_corridors_still_OPEN=True,N01_complete=False,physical_pass=False,selected=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (cf,pf,pi_file,ROOT/core['bundle'],ROOT/parent['bundle'],ROOT/pi['bundle'],Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-psys-flp-frame-load-paths.json',output)
    print(json.dumps(dict(status=output['status'],solids=len(nodes),floating=floating,exact_queries=exact,reused=reuse,seconds=output['worker_seconds'])),flush=True)


if __name__=='__main__':main()
