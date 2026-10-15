"""TEN new fixed feed seats/bands in the SAME real body/motion scene.

Only same-owner printed material can union. No WAGO glue, clearance-hole
retention claim, extra separate Frame prints or physical grip approval.
"""
import json,time
from pathlib import Path
import FreeCAD as A
from current_mixed_receiver_material import prepare,material
from plan_body36_receiver_space import P,C
from plan_axial_source_supports import arm_box
from short_feed_lacing_saddle import build
from current_work_guard import check as guard

def run():
    guard();tick=time.monotonic();planfile=P.OUT/'retained-feed-restraints-plan.json';plan=json.loads(planfile.read_text())
    for n,h in plan['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    assert not plan['missing'] and len(plan['restraints'])==10
    mf=P.OUT/'body36-shared-macro-layout.json';macro=json.loads(mf.read_text())
    for n,h in macro['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    # Reconstruct inherited geometry directly, not from an unspecified latest.
    bf=P.ROOT/macro['inherited_receipt'];base=json.loads(bf.read_text())
    effective={n:base['routes'][n] for n in macro['retained_route_ids']}
    effective.update(macro['qualified_changed_routes']);effective.update(macro['proposed_routes'])
    assert len(effective)==36
    targets,wires,pins,grips=prepare();profiles={};owners={}
    for name,g in grips['groups'].items():
        p,components=material(g);profiles[name]=p
        for kind,s in components.items():
            if kind=='seed':continue # Actual attachment arms below include this material.
            key='Group_'+name+'/'+kind;targets[key]=s
            if kind=='body':owners[key]=g['owner']
    rf=P.OUT/'body36-receiver-support-reservations.json';roots=json.loads(rf.read_text())
    for n,h in roots['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    for r in roots['groups']:
        for path in r['paths']:
            for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                key='ReceiverRoot/'+r['name']+'/'+r['wire']+'/'+str(i)
                targets[key]=arm_box(a,b,r['arm_half_widths_world_mm']);owners[key]=r['name']
    for n in list(wires):
        if n.startswith('body/'):wires.pop(n)
    wires.update({'body/'+n:(P.wire(r['parts']),1) for n,r in effective.items()})
    for n,s in targets.items():
        if n.startswith('Source/') and '/body/' in n:owners[n]=n.split('/')[1]
        elif n.startswith('Root/'):owners[n]=n.split('/')[1]
        elif n.split('/')[0] in {r['owner'] for r in plan['restraints']}:owners[n]=n.split('/')[0]
    samples={};checks=0;records=[];accepted={};errors=[]
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'retained-feed-restraints-pairs.json',bounds.near)
    files=[planfile,mf,bf,rf,Path(__file__),Path(__file__).with_name('short_feed_lacing_saddle.py')]
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files})
    def hit(a,b,rb=0):
        nonlocal checks
        if not bounds.near(a,b,rb+1e-4):return False
        checks+=1
        if rb and not b.Solids and len(b.Edges)>1:return any(hit(a,e,rb) for e in b.Edges)
        try:
            gap,volume=cache.check(a,b,0,rb)
            return volume>1e-5 or (rb and gap<rb-1e-6)
        except (RuntimeError,AssertionError,ValueError) as e:errors.append(str(e));return True
    def save():
        result=dict(status='TEN_FEED_COMMON_COMPONENT_GATE_COMPLETE' if len(accepted)==10 else 'FEED_COMMON_COMPONENT_GATE_OPEN',
            restraints=records,checks=checks,errors=errors,source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),
            selected=False,W5_complete=False,physical_pass=False,
            full_body_curves_accepted=not macro['remaining_wire_ids'],
            scope='Changed10seats/bands vs realretained/current36candidatecurves/roots/allmotion. Unqualifiedbodyroutes remain OPEN; this does not certifywholeW5.',
            open=['Whole36routeacceptance','Native4replacementFrames/7caps withfeedseats','Lacingstock/mounting/physicalsample'])
        f=P.OUT/'retained-feed-restraints-checks.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f);cache.save()
    for row in plan['restraints']:
        guard();name=row['group']+'/'+row['wire'];profile=profiles[row['group']]
        g=grips['groups'][row['group']];feed=next(f for f in g['feeds'] if f['wire']==row['wire'])
        new=build(profile['recipe'],feed);joined=profile['body'].fuse(new['body']).removeSplitter()
        assert joined.isValid() and len(joined.Solids)==1 and not joined.check(True),name
        contact=None
        for kind,s in ((k,new[k]) for k in ('body','band')):
            for target,t in targets.items():
                if kind=='body' and owners.get(target)==row['owner']:continue
                if hit(s,t):contact=kind+':'+target;break
            if contact:break
            for target,(w,r) in wires.items():
                own=target in ('wire/'+row['wire'],'body/'+row['wire'])
                if hit(s,w,r if own and kind=='band' else r+.25):contact=kind+':'+target;break
            if contact:break
            for other,q in accepted.items():
                for k,t in q['shapes'].items():
                    if kind==k=='body' and q['owner']==row['owner']:continue
                    if hit(s,t):contact=kind+':new/'+other+'/'+k;break
                if contact:break
            if contact:break
        records.append(dict(group=row['group'],wire=row['wire'],owner=row['owner'],recipe=new['recipe'],
            rooted_to_existing_group_body_one_solid=True,contact=contact,accepted_in_this_scope=contact is None and not errors))
        if not contact and not errors:accepted[name]=dict(owner=row['owner'],shapes={k:new[k] for k in ('body','band')})
        save();print('feed common',name,'clear',name in accepted,'first',contact,flush=True)
    save()

if __name__=='__main__':run()
