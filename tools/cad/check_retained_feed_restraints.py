"""TEN new fixed feed seats/bands in the SAME real body/motion scene.

Only same-owner printed material can union. No WAGO glue, clearance-hole
retention claim, extra separate Frame prints or physical grip approval.
"""
import json,time,hashlib,subprocess
from pathlib import Path
import FreeCAD as A
from current_mixed_receiver_material import prepare,material
from plan_body36_receiver_space import P,C
from plan_axial_source_supports import arm_box
from short_feed_lacing_saddle import build
from loom_land_port import box
from build_front_fixed_port_clearance import placement
from current_work_guard import check as guard
from current_body36_candidates import resolve

def old_shapes(recipe):
    """Reconstruct exactly the received recipe, not the changed helper code."""
    body=box(recipe['pads'][0]['bounds_mm']).fuse(box(recipe['pads'][1]['bounds_mm'])).cut(
        box(recipe['ring_cut']['outer']).cut(box(recipe['ring_cut']['inner']))).removeSplitter()
    r=recipe['project_wire_radius_mm'];t,w=recipe['project_lacing_section_mm'];z=-4.5
    frame=placement(recipe['local_to_world']);centre=frame.inverse().multVec(A.Vector(*recipe['contact_world_centre_mm']));y=centre.y
    band=box([-r-.2-t,y-r-.2-t,z-w/2,r+4.5+t,y+r+.2+t,z+w/2]).cut(
        box([-r-.2,y-r-.2,z-w,r+4.5,y+r+.2,z+w]))
    band=band.fuse(box(recipe['project_knot_bounds_local_mm'])).removeSplitter()
    for s in (body,band):s.Placement=frame*s.Placement
    return dict(body=body,band=band)

def run(parent_commit=None):
    guard();tick=time.monotonic();planfile=P.OUT/'retained-feed-restraints-plan.json';plan=json.loads(planfile.read_text())
    for n,h in plan['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    assert not plan['missing'] and len(plan['restraints'])==10
    mf=P.OUT/'body36-shared-macro-layout.json';macro=json.loads(mf.read_text())
    for n,h in macro['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    # Reconstruct inherited geometry directly, not from an unspecified latest.
    bf=P.ROOT/macro['inherited_receipt'];base=json.loads(bf.read_text())
    effective,ancestry=resolve(macro,P.ROOT)
    parent=None;inherited=None
    if parent_commit:
        path=(P.OUT/'retained-feed-restraints-checks.json').relative_to(P.ROOT).as_posix()
        raw=subprocess.check_output(['git','show',parent_commit+':'+path],cwd=P.ROOT);parent=json.loads(raw)
        mutable={Path(__file__).relative_to(P.ROOT).as_posix(),Path(__file__).with_name('short_feed_lacing_saddle.py').relative_to(P.ROOT).as_posix()}
        for n,h in parent['source_sha256'].items():
            actual=hashlib.sha256(subprocess.check_output(['git','show',parent_commit+':'+n],cwd=P.ROOT)).hexdigest() if n in mutable else P.SHA(P.ROOT/n)
            assert actual==h,('Inherited feed input changed',n)
        inherited=dict(commit=parent_commit,receipt_sha256=hashlib.sha256(raw).hexdigest(),unchanged_components=[])
    targets,wires,pins,grips=prepare();profiles={};owners={}
    for name,g in grips['groups'].items():
        p,components=material(g);profiles[name]=p
        for kind,s in components.items():
            if kind=='seed':continue # Actual attachment arms below include this material.
            key='Group_'+name+'/'+kind;targets[key]=s
            if kind=='body':owners[key]=g['owner']
            elif kind=='cap':owners[key]='CAP/'+name
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
    files=[planfile,mf,bf,rf,Path(__file__),Path(__file__).with_name('short_feed_lacing_saddle.py'),Path(__file__).with_name('current_body36_candidates.py')]
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files})
    if parent:
        for old in parent['restraints']:
            if not old['accepted_in_this_scope']:continue
            group=grips['groups'][old['group']];feed=next(f for f in group['feeds'] if f['wire']==old['wire'])
            new=build(profiles[old['group']]['recipe'],feed);previous=old_shapes(old['recipe'])
            for kind in ('body','band'):
                a,b=new[kind],previous[kind]
                assert a.cut(b).Volume<1e-6 and b.cut(a).Volume<1e-6,('Changed previously accepted feed',old['group'],old['wire'],kind)
            name=old['group']+'/'+old['wire'];accepted[name]=dict(owner=old['owner'],shapes=previous)
            records.append(old);inherited['unchanged_components'].append(name)
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
            restraints=records,checks=checks,errors=errors,source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),inherited_qualified_receipt=inherited,
            selected=False,W5_complete=False,physical_pass=False,
            full_body_curves_accepted=not macro['remaining_wire_ids'],
            candidate_receipt_ancestry=ancestry,
            scope='Changed10seats/bands vs realretained/current36candidatecurves/roots/allmotion. Unqualifiedbodyroutes remain OPEN; this does not certifywholeW5.',
            open=['Whole36routeacceptance','Native4replacementFrames/7caps withfeedseats','Lacingstock/mounting/physicalsample'])
        f=P.OUT/'retained-feed-restraints-checks.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f);cache.save()
    for row in plan['restraints']:
        guard();name=row['group']+'/'+row['wire'];profile=profiles[row['group']]
        if name in accepted:continue
        g=grips['groups'][row['group']];feed=next(f for f in g['feeds'] if f['wire']==row['wire'])
        support='cap' if name=='D_FL/W002' else 'body';physical_owner='CAP/'+row['group'] if support=='cap' else row['owner']
        new=build(profile['recipe'],feed,support=support);joined=profile[support].fuse(new['body']).removeSplitter()
        assert joined.isValid() and len(joined.Solids)==1 and not joined.check(True),name
        contact=None
        for kind,s in ((k,new[k]) for k in ('body','band')):
            for target,t in targets.items():
                if kind=='body' and owners.get(target)==physical_owner:continue
                if hit(s,t):contact=kind+':'+target;break
            if contact:break
            for target,(w,r) in wires.items():
                own=target in ('wire/'+row['wire'],'body/'+row['wire'])
                if hit(s,w,r if own and kind=='band' else r+.25):contact=kind+':'+target;break
            if contact:break
            for other,q in accepted.items():
                for k,t in q['shapes'].items():
                    if kind==k=='body' and q['owner']==physical_owner:continue
                    if hit(s,t):contact=kind+':new/'+other+'/'+k;break
                if contact:break
            if contact:break
        records.append(dict(group=row['group'],wire=row['wire'],owner=row['owner'],recipe=new['recipe'],
            parent_component=support,physical_print_owner=physical_owner,new_separate_prints=0,new_screws=0,
            rooted_to_existing_group_body_one_solid=True,contact=contact,accepted_in_this_scope=contact is None and not errors))
        if not contact and not errors:accepted[name]=dict(owner=physical_owner,shapes={k:new[k] for k in ('body','band')})
        save();print('feed common',name,'clear',name in accepted,'first',contact,flush=True)
    save()

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--resume-commit');run(p.parse_args().resume_commit)
