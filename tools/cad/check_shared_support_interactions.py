"""Actual changed fixed bodies against complete new support/tie set.

Scoped changed-interface gate only. Retained assembly/wires and native CAD
must still be qualified before selection; no whole-W5 claim.
"""
import json,time,itertools
from pathlib import Path
import FreeCAD as A
import build_remaining_loom_supports as G
from resume_remaining_support_gate import cached_allocation
from material_pair_receipts import MaterialPairReceipts
from immutable_bounds import ImmutableBounds
P=G.P

def run():
    tick=time.monotonic()
    names=('remaining-support-shared-paths.json','remaining-retention-entry.json','remaining-loom-roots-plan.json','remaining-support-shared-recovery-plan.json','front-fixed-port-clearance-native.json')
    files=[P.OUT/n for n in names];paths,retention,roots,recovery,native=[json.loads(f.read_text()) for f in files]
    assert paths['status']=='SHARED_SUPPORT_RESERVATIONS_ACTUAL_NATIVE_OPEN'
    for n,h in paths['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    source=P.ROOT/native['native'];sf=P.OUT/'StationFramesCurrent.FCStd'
    reader=G.B.H.P.SavedShapes();parents={}
    for group in roots['groups']:
        name=group.get('preserved_owner')
        if name:parents[name]=reader.shape(source if name.endswith('SourceCarrier') else sf,name)
    shapes,recipes,bands,bonds,errors=cached_allocation(paths,retention,roots,parents)
    assert not errors,errors
    axes=json.loads((P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    changed={r['group'] for r in recovery['changed_fixed_groups']}
    targets=[]
    for group in roots['groups']:
        name=group['id'];owner=group['owner_stage'];stage=owner.split('_')[-1]
        items=[(name,shapes[name])]+[(k,s) for k,s in bands.items() if k.removeprefix('Band_') in {l['id'] for l in group['lands']}]
        if name+'Bond' in bonds:items.append((name+'Bond',bonds[name+'Bond']))
        poses=list(itertools.product(G.ANGLES,repeat=2)) if stage=='Knee' else [(h,0) for h in G.ANGLES] if stage=='Hip' else [(0,0)]
        for h,k in poses:
            tr=G.transform(axes,owner.split('_')[1],h,k,stage) if stage!='Body' else A.Placement()
            for label,s in items:targets.append((label,G.moved(s,tr),[h,k]))
    bounds=ImmutableBounds();cache=MaterialPairReceipts(P.OUT/'remaining-shared-interaction-pairs.json',bounds.near)
    contacts=[];pairs=0;printing={}
    for name in sorted(changed):
        s=shapes[name];printing[name]=G.print_orientation(s)
        for label,t,pose in targets:
            if label==name or not bounds.near(s,t,.001):continue
            _,v=cache.check(s,t);pairs+=1
            if v>1e-5:contacts.append(dict(group=name,target=label,other_pose=pose,volume_mm3=v))
    cache.save()
    result=dict(status='CHANGED_SHARED_SUPPORT_INTERFACES_CLEAR_WHOLE_ASSEMBLY_OPEN' if not contacts else 'REJECTED_CHANGED_SHARED_SUPPORT_INTERFACES',
        changed_groups=sorted(changed),pairs=pairs,contacts=contacts,printing=printing,
        valid_single_solid_bodies=len(shapes),selected=False,native_complete=False,W5_complete=False,physical_pass=False,
        remaining=['Changed supports versus full retained assembly and all wire radii','Native editable construction, parameter/reopen/exports and current selection'],
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files+[source,sf,Path(__file__)]},worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'remaining-support-shared-interactions.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
if __name__=='__main__':run()
