"""Plan against actual valid geometry BEFORE choosing a whole route.

Unlike the rejected 1000-state mesh grid, each new line/arc/Bezier is screened
against real BReps and exact wire edges with the unchanged1.25mm core budget.
The final existing full-curve gate remains mandatory. No bbox acceptance.
"""
import copy,heapq,itertools,json,math,time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from plan_body36_receiver_space import P,C
from plan_body_fanout_layout import AXES,reverse_part
from shared_body36_macro_routes import packed_front_prefixes,math_gate
from plan_current_moving_looms import exact_quarter,metrics,add,mul
from plan_current_mta_interfaces import line
from current_body36_candidates import resolve
from current_mixed_receiver_material import material
from plan_axial_source_supports import arm_box
from short_feed_lacing_saddle import build as feed_material
from positive_material_witness import witness
from current_work_guard import check as guard
from canonical_body_rows import normalize,selected_rows
from current_route_proposal_screen import clear as proposal_clear
from goal_tangent_handles import pairs as goal_handles

class ExactOracle:
    def __init__(self,targets,wires):
        self.targets=targets;self.wires=wires;self.bounds=C.ImmutableBounds()
        self.cache=C.AtomicMaterial(P.OUT/'exact-corridor-pairs.json',self.bounds.near)
        self.memo={};self.points={};self.checks=0;self.blockers={}

    def clear(self,part,row):
        key=(row['wire'],json.dumps(part,sort_keys=True))
        if key in self.memo:return self.memo[key]
        s=P.wire([part]);rs=1.25
        for name,(t,r) in self.wires.items():
            if name=='fan/'+row['loom']+'/'+row['core']:continue
            if not self.bounds.near(s,t,rs+r+.0001):continue
            # Points ON exact curves can prove rejection cheaply. Absence of
            # a close point still falls through to exact per-edge distance.
            for q in (s,t):
                if id(q) not in self.points:self.points[id(q)]=np.asarray([list(v) for e in q.Edges for v in e.discretize(Distance=.75)])
            aa,bb=self.points[id(s)],self.points[id(t)]
            for p in aa:
                ix=np.all(np.abs(bb-p)<rs+r,axis=1)
                if ix.any() and np.any(np.linalg.norm(bb[ix]-p,axis=1)<rs+r-1e-6):
                    self.blockers[name]=self.blockers.get(name,0)+1;self.memo[key]=False;return False
            for e in t.Edges:
                if not self.bounds.near(s,e,rs+r+.0001):continue
                self.checks+=1;gap,vol=self.cache.check(s,e,rs,r)
                if vol>1e-5 or gap<rs+r-1e-6:
                    self.blockers[name]=self.blockers.get(name,0)+1;self.memo[key]=False;return False
        for name,t in self.targets.items():
            if not self.bounds.near(s,t,rs+.0001):continue
            self.checks+=1
            if witness(s,t,self.bounds,self.points) is not None:
                self.blockers[name]=self.blockers.get(name,0)+1;self.memo[key]=False;return False
            gap,vol=self.cache.check(s,t,rs,0)
            if vol>1e-5 or gap<rs-1e-6:
                self.blockers[name]=self.blockers.get(name,0)+1;self.memo[key]=False;return False
        self.memo[key]=True;return True

class ProposalOracle:
    """Positive witnesses reject; absence is ONLY a proposal for exact testing."""
    def __init__(self,exact,mesh=None):
        self.exact=exact;self.mesh=mesh;self.memo={};self.checks=0;self.blockers={};self.cache=exact.cache

    def clear(self,part,row):
        key=(row['wire'],json.dumps(part,sort_keys=True))
        if key in self.exact.memo:return self.exact.memo[key]
        if key in self.memo:return self.memo[key]
        if self.mesh is not None:
            from plan_body_fanout_layout import part_points
            points=part_points(part)
            points=np.asarray([p for p in points if min(math.dist(p,row['free_start']),math.dist(p,row['free_end']))>1e-7])
            result=not len(points) or proposal_clear(self.mesh,points,row)
            self.memo[key]=result;self.checks+=1;return result
        s=P.wire([part]);rs=1.25;points=self.exact.points;bounds=self.exact.bounds
        for n,(t,r) in self.exact.wires.items():
            if n=='fan/'+row['loom']+'/'+row['core']:continue
            if not bounds.near(s,t,rs+r+.0001):continue
            for q in (s,t):
                if id(q) not in points:points[id(q)]=np.asarray([list(v) for e in q.Edges for v in e.discretize(Distance=.75)])
            aa,bb=points[id(s)],points[id(t)]
            for p in aa:
                ix=np.all(np.abs(bb-p)<rs+r,axis=1)
                if ix.any() and np.any(np.linalg.norm(bb[ix]-p,axis=1)<rs+r-1e-6):
                    self.blockers[n]=self.blockers.get(n,0)+1;self.memo[key]=False;return False
        for n,t in self.exact.targets.items():
            if bounds.near(s,t,rs+.0001) and witness(s,t,bounds,points) is not None:
                self.blockers[n]=self.blockers.get(n,0)+1;self.memo[key]=False;return False
        self.checks+=1;self.memo[key]=True;return True

def lazy_route(exact,row,max_seconds=900,mesh=None):
    tick=time.monotonic();proposal=ProposalOracle(exact,mesh);attempts=0
    source=row.get('source_parts') or [row['source_land']];receiving=row['receiving_parts']
    while time.monotonic()-tick<max_seconds:
        guard();q,error=route(proposal,row,max_seconds=max_seconds-(time.monotonic()-tick))
        if not q:return None,error
        attempts+=1;middle=q['parts'][len(source):-len(receiving)]
        rejected=next((p for p in middle if not exact.clear(p,row)),None)
        exact.cache.save()
        print('lazy exact candidate',row['wire'],attempts,'accepted_middle',rejected is None,'seconds',round(time.monotonic()-tick,1),flush=True)
        if rejected is None:
            q['architecture']='POSITIVE_WITNESS_GRAPH_LAZY_EXACT_MIDDLE_THEN_FULL_CURVE_GATE'
            q['exact_middle_candidates']=attempts;return q,None
        # Exact.memo bans that particular colliding edge on every next search;
        # other graph work and all exact pair receipts remain reusable.
    return None,dict(reason='BOUNDED_LAZY_EXACT_GRAPH_NOT_GEOMETRIC_IMPOSSIBILITY',candidates=attempts,seconds=round(time.monotonic()-tick,3))

def route(oracle,row,max_seconds=900,max_states=15000):
    start=np.asarray(row['free_start']);end=np.asarray(row['free_end'])
    source=row.get('source_parts') or [row['source_land']];receiving=row['receiving_parts']
    fixed=sum(p['length_mm'] for p in source+receiving)
    capacity=row['capacity_before_terminal_mm']-row['terminal_allowance_project_mm']-fixed
    axis=tuple(row.get('source_free_axis',row['bodyward_bundle_tangent']))
    # Feasibility, not shortest-path proof. Weighted search limits spending
    # on lateral cul-de-sacs; curvature/capacity and exact gates are unchanged.
    heuristic_weight=2.0
    first=(0,0,0,AXES.index(axis));serial=itertools.count();queue=[(heuristic_weight*math.dist(start,end),0,next(serial),first)]
    best={first:0};parents={};tick=time.monotonic();last=tick;states=0
    while queue and states<max_states and time.monotonic()-tick<max_seconds:
        _,cost,_,state=heapq.heappop(queue)
        if best.get(state)!=cost:continue
        states+=1;p=(start+10*np.asarray(state[:3])).tolist();u=AXES[state[3]]
        if time.monotonic()-last>20:
            guard();oracle.cache.save();print('exact plan',row['wire'],'states',states,'checks',oracle.checks,'seconds',round(time.monotonic()-tick,1),flush=True);last=time.monotonic()
        distance=math.dist(p,end)
        if cost and cost+distance<capacity:
            for a,b in goal_handles(distance):
                poles=[p,add(p,mul(u,a)),add(end.tolist(),mul(row['receiver_outward_axis'],b)),end.tolist()]
                length,radius,_=metrics(poles,24)
                if radius<10.5 or cost+length>capacity:continue
                length,radius,_=metrics(poles,400)
                if radius<10 or cost+length>capacity:continue
                final=dict(kind='bezier',start=p,end=end.tolist(),poles_mm=poles,length_mm=length,sampled_radius_mm=radius)
                if not oracle.clear(final,row):continue
                parts=[final];key=state
                while key!=first:key,part=parents[key];parts.append(part)
                parts=list(reversed(parts[1:]))+[final]
                q,error=math_gate(row,[*source,*parts,*receiving])
                if q:return dict(q,architecture='ACTUAL_BREP_CURVATURE_GRAPH_BEFORE_FULL_CURVE_GATE',search_states=states,search_seconds=round(time.monotonic()-tick,3)),None
        for i,v in enumerate(AXES):
            if i==state[3]:part=line(p,add(p,mul(u,10)))
            elif sum(a*b for a,b in zip(u,v))==0:part=exact_quarter(p,u,v,10)
            else:continue
            nxt=tuple(round((part['end'][j]-start[j])/10) for j in range(3))+(i,)
            new=cost+part['length_mm']
            if new+math.dist(part['end'],end)>capacity or new>=best.get(nxt,float('inf')):continue
            if not oracle.clear(part,row):continue
            best[nxt]=new;parents[nxt]=(state,part);heapq.heappush(queue,(new+heuristic_weight*math.dist(part['end'],end),new,next(serial),nxt))
    return None,dict(reason='BOUNDED_EXACT_GRAPH_NOT_GEOMETRIC_IMPOSSIBILITY',states=states,seconds=round(time.monotonic()-tick,3),blockers=oracle.blockers.copy())

def run(parent_commit):
    import check_shared_body36_macro as receiver
    import joint_clearance_corridors as dispatch
    original=receiver.prepare;prepared=None
    def shared_prepare():
        nonlocal prepared
        if prepared is None:prepared=original()
        a,b,p,g=prepared
        p={**p,Path(__file__).relative_to(P.ROOT).as_posix():P.SHA(Path(__file__))}
        generated=P.OUT/'exact-corridor-recovery-plan.json'
        if generated.exists():p[generated.relative_to(P.ROOT).as_posix()]=P.SHA(generated)
        helper=Path(__file__).with_name('canonical_body_rows.py')
        p[helper.relative_to(P.ROOT).as_posix()]=P.SHA(helper)
        screen=Path(__file__).with_name('current_route_proposal_screen.py')
        p[screen.relative_to(P.ROOT).as_posix()]=P.SHA(screen)
        handles=Path(__file__).with_name('goal_tangent_handles.py')
        p[handles.relative_to(P.ROOT).as_posix()]=P.SHA(handles)
        return dict(a),dict(b),p,g
    receiver.prepare=shared_prepare
    def choose(parent,base):
        targets,wires,pins,grips=shared_prepare()
        rows=normalize(parent,base,selected_rows(P.OUT/'receiver-joint-selection.json',P.ROOT))
        for name,g in grips['groups'].items():
            profile,parts=material(g)
            targets.update({'Group_'+name+'/'+k:s for k,s in parts.items()})
            if g['kind']=='triple':
                for feed in g['feeds']:
                    support='cap' if name=='D_FL' and feed['wire']=='W002' else 'body'
                    q=feed_material(profile['recipe'],feed,support=support)
                    targets.update({'Feed_'+name+'/'+feed['wire']+'/'+k:q[k] for k in ('body','band')})
        rootfile=P.OUT/'body36-receiver-support-reservations.json'
        for r in json.loads(rootfile.read_text())['groups']:
            for path in r['paths']:
                for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                    targets['ReceiverRoot/'+r['name']+'/'+r['wire']+'/'+str(i)]=arm_box(a,b,r['arm_half_widths_world_mm'])
        current,_=resolve(parent,P.ROOT)
        positive=set(parent['retained_route_ids'])|set(parent['qualified_changed_routes'])
        wires={n:v for n,v in wires.items() if not n.startswith('body/')}
        wires.update({'body/'+n:(P.wire(current[n]['parts']),1) for n in positive})
        for n in ('W013','W047','W069'):
            r=rows[n];wires['fan/'+r['loom']+'/'+r['core']]=(P.wire(r['source_parts']),1)
        # Reuse the received REAL-surface proxy rather than repeating costly
        # OCC inside/distance queries at every graph node. Actual validation
        # below still uses1.25 and all full material, not this planning proxy.
        from current_core_planning_scene import build as proxy_build
        planning=dict(wires)
        for r in rows.values():
            key='fan/'+r['loom']+'/'+r['core']
            if key in planning:planning['new/'+r['wire']+'/source']=planning.pop(key)
        for n in list(planning):
            if n.startswith('chosen/'):planning['leg/'+n.removeprefix('chosen/')]=planning.pop(n)
        mesh=proxy_build(targets,planning)
        # Functional open-prototype corridors may rise beyond the historical
        # Z155 planning cut. Missing proxy material there is NEVER acceptance:
        # lazy exact and the full gate include all actual bodies/motion.
        mesh.data['high']=np.maximum(mesh.data['high'],[210,180,275])
        mesh.data['low']=np.minimum(mesh.data['low'],[-220,-180,-30])
        oracle=ExactOracle(targets,wires);candidates={};failed={};tick=time.monotonic()
        def save():
            out=dict(status='ACTUAL_GEOMETRY_ROUTE_PLANNING_NOT_WHOLE_W5_ACCEPTANCE',candidates=candidates,failures=failed,
                remaining=[n for n in parent['remaining_wire_ids'] if n not in candidates],checks=oracle.checks,
                worker_seconds=round(time.monotonic()-tick,3),parent_commit=parent_commit,selected=False,physical_pass=False)
            f=P.OUT/'exact-corridor-recovery-plan.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(f);oracle.cache.save()
        save()
        for n in parent['remaining_wire_ids']:
            guard();q,error=lazy_route(oracle,rows[n],mesh=mesh)
            if q:
                from plan_body_fanout_layout import part_points
                candidates[n]=q;oracle.wires['body/'+n]=(P.wire(q['parts']),1)
                mesh.add_points('currentbody/'+n,np.concatenate([part_points(p) for p in q['parts']]))
            else:failed[n]=error
            save();print('exact plan result',n,'candidate',q is not None,'seconds',round(time.monotonic()-tick,1),flush=True)
        return rows,candidates,failed
    dispatch.plan=choose
    receiver.run(parent_commit,joint_clearance=True)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--parent-commit',required=True);run(p.parse_args().parent_commit)
