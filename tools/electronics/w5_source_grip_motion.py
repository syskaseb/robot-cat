"""One coupled nominal motion screen of the12new clips/straps.

Use saved native rigid ownership and actual revolute axes. No P0 source save,
solver run, cable-as-rigid-body fiction or reuse of rest clearance as motion.
The +/-15deg window is an explicit prototype SCREEN, not a servo limit or
an approved operating range. Flexible cable envelopes remain separate.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from check_main_p0_placement import SavedShapes, prop
from w5_leg_corridors_r1 import components
from w5_selected_owners_r52 import cached
from w5_exact_separation import separated
from servo_fuse_inputs_r1 import sha, save
BASE=ROOT/'hardware/electronics/full-cat';OUT=BASE/'w5-source-grip-motion-r1'

def main():
    import FreeCAD as A, Part
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);pins={}
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p);return p
    def read(p):return json.loads(pin(p).read_text(encoding='utf-8'))
    def shape(p):return Part.read(str(pin(p)))
    reader=SavedShapes();entry=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
    objects=reader.doc(entry);component=components(objects)
    axes=read(ROOT/'hardware/simulation/p0/e6-leg-compatibility.json')['axes']
    incoming={}
    for j in axes:
        refs=[prop(objects[j['name']],'Reference'+str(i))[0] for i in (1,2)]
        assert all(not r.get('file') for r in refs)
        a,b=[component(r.get('name')) for r in refs]
        assert a!=b and b not in incoming;incoming[b]=(a,j)
    def ancestors(node):
        chain=[];seen=set()
        while node in incoming:
            assert node not in seen;seen.add(node);node,j=incoming[node];chain.append(j)
        return list(reversed(chain))
    source_map=read(BASE/'w5-leg-source-map-r1/interface.json')['looms']
    source_by_loom={r['loom']:r for r in source_map}
    proposals={}
    for folder,count in [('w5-source-link-grips-r2',40),('w5-source-hip-grips-r3',20)]:
        receipt=read(BASE/folder/'checks.json');assert not receipt['hits'] and not receipt['errors']
        bp=read(BASE/folder/'blueprint.json')
        g=BASE/folder/'TWELVE_SOURCE_CLIPS_AND_STRAPS_PROPOSED_WORLD.brep'
        shapes=shape(g).childShapes();assert len(shapes)==len(bp['roles'])==count
        assert sha(g)==receipt['files'][g.relative_to(ROOT).as_posix()]
        proposals.update(zip(bp['roles'],shapes))
    assert len(proposals)==60
    original,cache=cached();pin(BASE/'w5-installed-r52/owners.json');pin(BASE/'w5-installed-r52'/cache['geometry'])
    members={x.get('value') for x in prop(objects['RobotCatAssembly24'],'Group').findall('.//Link')}
    neighbor_groups={}
    for wrapper in members:
        if not wrapper.startswith('Rigid_'):continue
        group=prop(objects[wrapper],'Group')
        if group is None:continue
        children=group.findall('.//Link')
        if len(children)!=1:continue
        name=children[0].get('value')
        if name in original:neighbor_groups[name]=component(wrapper)
    neighbors={name:original[name] for name in neighbor_groups}
    assert all(r['housing'] in neighbors for r in source_map)
    # Include current new fixed attachments, not just old saved P0.
    for owner in ('FLFixedFrame','FRFixedFrame','RLFixedFrame','RRFixedFrame','SourceEastHood'):
        neighbors[owner]=shape(ROOT/'hardware/cad/studies/w5-loom-fixed-native-r1'/(owner+'_CANDIDATE_WORLD.brep'))
    remote=read(BASE/'w5-remote-end-native-r1/checks.json')
    assert remote['BOP_errors']==0 and remote['closed_STLs']==2
    for owner in ('CompleteDeck','SourceBridge'):
        neighbors[owner]=shape(ROOT/'hardware/cad/studies/w5-remote-end-native-r1'/(owner+'_CANDIDATE_WORLD.brep'))
    for owner in ('SourceCarrier','SourceCover'):
        neighbors[owner]=shape(ROOT/'hardware/cad/studies/w5-side-retention-native-r1'/(owner+'_CANDIDATE_WORLD.brep'))
    neighbors['SourceWestHood']=shape(ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1/SourceWestHood_CANDIDATE_WORLD.brep')
    neighbor_chains={k:ancestors(v) for k,v in neighbor_groups.items()}
    proposal_chains={k:ancestors(component('Rigid_'+source_by_loom[k[:3]]['pcb'])) for k in proposals}
    assert all(1<=len(c)<=2 for c in proposal_chains.values())
    def pose(chain,hip,knee):
        t=A.Placement()
        for j in chain:
            # Ankle motion is left at zero: no new clip is owned by the foot.
            angle=hip if j['stage']=='Hip' else knee if j['stage']=='Knee' else 0
            pivot=A.Vector(*j['pivot_mm']);rotation=A.Rotation(A.Vector(*j['axis']),angle)
            local=A.Placement(pivot,rotation)*A.Placement(-pivot,A.Rotation())
            t=t*local
        return t
    def transformed(s,t):q=s.copy();q.Placement=t*q.Placement;return q
    hits=[];errors=[];pairs=0
    def check(angles,label,s,owner,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox) or separated(a,b):continue
                pairs+=1
                try:
                    c=a.common(b)
                    if c.Volume>1e-5:
                        path=OUT/('HIT_'+str(len(hits)+1)+'.brep');c.exportBrep(str(path))
                        hits.append(dict(hip_knee_deg=angles,part=label,owner=owner,mm3=c.Volume,witness=path.relative_to(ROOT).as_posix()))
                except Exception as ex:errors.append(dict(hip_knee_deg=angles,part=label,owner=owner,error=str(ex)))
    samples=[(h,k) for h in (-15,0,15) for k in (-15,0,15) if (h,k)!=(0,0)]
    # Rest pose already received. In each sample all four legs move together;
    # compare all new clips to other rigid owners and one another in that SAME
    # pose, never a moving clip against an unmoved own carrier.
    for angles in samples:
        moved={k:transformed(s,pose(proposal_chains[k],*angles)) for k,s in proposals.items()}
        rigid={k:transformed(s,pose(neighbor_chains.get(k,[]),*angles)) for k,s in neighbors.items()}
        for label,s in moved.items():
            for owner,t in rigid.items():check(list(angles),label,s,owner,t)
        labels=list(moved)
        for i,a in enumerate(labels):
            for b in labels[i+1:]:
                # Same-loom clip/strap mutual clearances were already received
                # and relative placement is invariant under a rigid transform.
                if a[:3]!=b[:3]:check(list(angles),a,moved[a],b,moved[b])
        save(OUT/'progress.json',dict(sample=list(angles),pairs=pairs,hits=len(hits),errors=len(errors),updated_utc=datetime.now(timezone.utc).isoformat()))
        print('SOURCE_GRIP_MOTION',angles,pairs,len(hits),len(errors),flush=True)
    finish=datetime.now(timezone.utc);pin(Path(__file__))
    save(OUT/'checks.json',dict(status='NEW_SOURCE_GRIP_NOMINAL_SAMPLES_CONFLICT' if hits or errors else 'NEW_SOURCE_GRIP_NOMINAL_SAMPLES_CLEAR',
        physical_looms=12,new_materials=60,P0_rigid_neighbors=len(neighbor_groups),samples_hip_knee_deg=samples,
        prototype_screen_window_deg=15,screen_window_is_not_servo_or_operating_limit=True,
        ankle_motion_tested=False,rigid_ownership_followed=True,native_solver_exercised=False,
        flexible_body_or_factory_cables_moved_as_rigid=False,flexible_cable_envelopes_pending=True,
        P0_documents_unchanged=True,rest_pose_receipts_retained=True,continuous_sweep_verified=False,
        hits=hits,errors=errors,pairs=pairs,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={**reader.hashes,**pins},files={p.relative_to(ROOT).as_posix():sha(p) for p in OUT.glob('HIT_*.brep')},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))

if __name__=='__main__':main()
