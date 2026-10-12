"""Bounded common route search using current actual surface reservations.

Reuse the existing routing/sampling machinery. Reserve every terminal first,
route constrained MAIN pair first, then complete real wires. No selection,
no new native variant per search state, no bbox-as-contact claim.
"""
import heapq,itertools,json,math,time
from pathlib import Path
import plan_u1_common_departures as C
import plan_current_main_pi_wiring as M
from plan_current_main_sources import ROOT,OUT,SHA
from route_current_leg_fanouts import sampling_parts
from open_prototype_path_preflight import samples
from open_prototype_source_group import segment_geometry,unit,dot,sub
from plan_current_moving_looms import poles,metrics,exact_turn_to

AXES=tuple((round(math.cos(math.pi*i/8),12),round(math.sin(math.pi*i/8),12),0) for i in range(16))+((0,0,1),(0,0,-1))


class Space:
    def __init__(self,cache):
        self.wires={};self.faces={};self.cell=8;self.radius=.7
        # The nominal S0 body is an actual native Cylinder. Its curved
        # surface's bounding rectangle blocks a known clear MAIN exit.
        # Use its exact finite-cylinder distance, NOT remove the obstacle.
        import FreeCAD as A
        model=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/OpenPrototypePlan.FCStd'
        assert cache['source_sha256'][model.relative_to(ROOT).as_posix()]==SHA(model)
        doc=A.openDocument(str(model));body=doc.getObject('S0_body_CP2')
        assert body.TypeId=='Part::Cylinder' and abs(body.Radius.Value-28.5)<1e-6 and abs(body.Height.Value-40)<1e-6
        assert (body.Placement.Base-A.Vector(-77,16,65)).Length<1e-6
        A.closeDocument(doc.Name)
        s0=[r['bounds_mm'] for r in cache['boxes'] if r['owner']=='S0_body_CP2']
        assert [min(b[j] for b in s0) for j in range(3)]+[max(b[j] for b in s0) for j in range(3,6)]==[-105.5,-12.5,65.,-48.5,44.5,105.]
        for row in cache['boxes']:
            if row['owner']=='S0_body_CP2':continue
            b=row['bounds_mm']
            ranges=[range(math.floor((b[j]-2)/self.cell),math.floor((b[j+3]+2)/self.cell)+1) for j in range(3)]
            for key in itertools.product(*ranges):self.faces.setdefault(key,[]).append(b)
        for row in cache['retained_wires']:self.insert(row['wire'],row['segments'],row['OD_mm']/2)

    def insert(self,name,parts,radius):
        for _,p in samples(sampling_parts(parts),step=.7):
            if not all(lo<=x<=hi for lo,x,hi in zip((-100,-90,40),p,(160,90,190))):return False
            self.wires.setdefault(tuple(math.floor(x/self.cell) for x in p),[]).append((p,radius,name))

    def clear(self,parts,ignore=()):
        for _,p in samples(sampling_parts(parts),step=.7):
            key=tuple(math.floor(x/self.cell) for x in p);clearance=self.radius+.35
            radial=max(0,math.hypot(p[0]+77,p[1]-16)-28.5);axial=max(65-p[2],p[2]-105,0)
            if math.hypot(radial,axial)<clearance:return False
            if any(all(b[j]-clearance<p[j]<b[j+3]+clearance for j in range(3)) for b in self.faces.get(key,())):return False
            for delta in itertools.product((-1,0,1),repeat=3):
                for q,r,n in self.wires.get(tuple(x+y for x,y in zip(key,delta)),()):
                    if n not in ignore and math.dist(p,q)<r+clearance:return False
        return True


def validate(parts,radius):
    last=None;tangent=None;length=0
    for p in parts:
        if p['kind']=='bezier':
            size,minimum,_=metrics(p['poles_mm'],400)
            assert minimum>=radius-1e-6,(minimum,radius)
            first=unit(sub(p['poles_mm'][1],p['poles_mm'][0]));final=unit(sub(p['poles_mm'][3],p['poles_mm'][2]))
        else:size,first,final,rr=segment_geometry(p);assert rr is None or rr>=radius-1e-6
        if last is not None:
            assert math.dist(last,p['start'])<1e-6,'Disconnected route'
            assert dot(tangent,first)>1-1e-7,'Route kink'
        last=p['end'];tangent=final;length+=size
    return length


def search(space,start,start_axis,target,outward,radius,budget,ignore=(),max_states=650):
    step=max(2,radius);axis=AXES.index(tuple(start_axis));first=tuple(start)+(axis,)
    count=itertools.count();queue=[(math.dist(start,target),0,next(count),first)];best={first:0};parents={};states=0
    while queue and states<max_states:
        _,cost,_,state=heapq.heappop(queue)
        if cost!=best.get(state):continue
        states+=1;point=list(state[:3]);u=AXES[state[3]]
        # Whole spatial completion preserves both real endpoint tangents.
        for h,b in ((10,10),(20,20),(30,30),(50,30),(30,50),(50,50),(80,30),(30,80),(80,80)):
            ps=poles(point,list(u),target,outward,h,b);length,min_r,_=metrics(ps,32)
            if min_r<radius*1.02 or cost+length>budget:continue
            end=dict(kind='bezier',start=point,end=target,poles_mm=ps,length_mm=length,
                project_sampled_min_R_mm=min_r,planning_curvature_samples=32)
            if not space.clear([end],ignore):continue
            _,fine_r,_=metrics(ps,400)
            if fine_r<radius:continue
            end['project_sampled_min_R_mm']=fine_r;end['planning_curvature_samples']=400
            pieces=[];s=state
            while s!=first:previous,part=parents[s];pieces.append(part);s=previous
            return list(reversed(pieces))+[end],states
        for k,v in enumerate(AXES):
            if k==state[3]:part=M.line(point,[point[j]+step*u[j] for j in range(3)])
            elif abs(dot(u,v))<1-1e-8:
                part=exact_turn_to(point,u,v,step)
            else:continue
            end=part['end']
            if not all(lo<=x<=hi for lo,x,hi in zip((-100,-90,40),end,(160,90,190))):continue
            new=cost+part['length_mm'];lower=math.dist(end,target)
            if new+lower>budget:continue
            nxt=tuple(round(end[j],9) for j in range(3))+(k,)
            if new>=best.get(nxt,float('inf')) or not space.clear([part],ignore):continue
            best[nxt]=new;parents[nxt]=(state,part)
            heapq.heappush(queue,(new+lower*1.15,new,next(count),nxt))
    return None,states


def run():
    tick=time.monotonic();cachefile=OUT/'u1-current-routing-space.json';cache=json.loads(cachefile.read_text())
    for n,h in cache['source_sha256'].items():assert SHA(ROOT/n)==h,('Stale routing space',n)
    p=C.build();space=Space(cache);ends={};routes={};failed=[]
    for wid,r in p['routes'].items():
        ends[wid]={s:dict(parts=e['parts'],point=e['end_mm'],axis=e['end_axis'],radius=e['radius']) for s,e in r['ends'].items()}
    for wid,x in [('W079',-48.68),('W080',-45.18)]:
        mouth=p['USB_receiver']['free_wire_mouths_mm'][wid]
        # This complete vertical land was already clear against actual MAIN
        # in the239pair receipt. Start search above its conservative face
        # boxes, not inside the component's non-solid bounding reservation.
        a=[x,21.289,51.0948];land=p['changed_MAIN_pair'][wid]['parts'][0]['end'];b=[mouth[0]+9,*mouth[1:]]
        ends[wid]={'a':dict(parts=[M.line(a,land)],point=land,axis=M.U,radius=1.05),
                   'b':dict(parts=[M.line(mouth,b)],point=b,axis=M.E,radius=1.05)}
    for wid,row in ends.items():
        for side,e in row.items():space.insert(wid+'/'+side,e['parts'],e['radius'])
    order=['W079','W080','XL05','XL06','XL01','XL07','XL10','XL02','XL08','XL09','XS11','XS21','XS31']
    for wid in order:
        e=ends[wid];a,b=e['a'],e['b'];space.radius=a['radius']
        radius=11.1 if wid.startswith('W') else 10 if p['routes'][wid]['source'].get('AWG')==26 else .5 if wid.startswith('XS') else 6
        limit=447 if wid.startswith('W') else 564 if p['routes'][wid]['source'].get('AWG')==26 else 450
        fixed=sum(v['length_mm'] for side in e.values() for v in side['parts'])
        middle,states=search(space,a['point'],a['axis'],b['point'],b['axis'],radius,limit-fixed,(wid+'/a',wid+'/b'))
        if middle is None:
            failed.append(dict(wire=wid,cause='NO_BOUNDED_COMMON_CHANNEL',states=states));print('No channel',wid,states,flush=True);break
        whole=a['parts']+middle+M.reverse(b['parts']);length=validate(whole,radius)
        routes[wid]=dict(parts=whole,middle_parts=middle,radius=a['radius'],guide_mm=length,
            nominal_blank_mm=math.ceil(length+(36 if limit==564 else 3 if wid.startswith('W') else 6)),
            min_fixed_radius_mm=radius,search_states=states,actual_cut_mm=None,native_grips_open=True,physical_pass=False)
        space.insert(wid,whole,a['radius']);print('Allocated',wid,states,round(length,2),round(time.monotonic()-tick,2),flush=True)
    p['complete_routes']={n:r for n,r in routes.items() if not n.startswith('W')}
    for n,r in p['complete_routes'].items():r['source']=p['routes'][n]['source']
    p['changed_MAIN_pair']={n:dict(r,radius_mm=r['radius']) for n,r in routes.items() if n.startswith('W')}
    if len(p['changed_MAIN_pair'])==2:
        longest=max(r['guide_mm']+3 for r in p['changed_MAIN_pair'].values())
        main=M.plan();offcut=max(main['routes'][n]['guide_mm']+3+(14 if n=='W060' else 0) for n in ('W060','W078'))
        loop=.0175*(1+.00393*40)*2*longest/1000/.823
        p['PI_CABLE_P0_proposed_routing_cap_supersession'].update(longest_required_mm=longest,
            remaining_single1m_cut_after_output_and_INPUT_offcut_mm=1000-longest-offcut,
            conditional_copper_loop_60C_ohm=loop,conditional_drop_3A_V=3*loop,
            conditional_remaining_total_loop_budget_ohm=(5.08-4.95)/3-loop)
    p['allocated_end_prefixes']=ends;p['search_failures']=failed;p['search_scope_bounds_mm']=[-100,-90,40,160,90,190]
    p['source_sha256'].update({cachefile.relative_to(ROOT).as_posix():SHA(cachefile),Path(__file__).relative_to(ROOT).as_posix():SHA(Path(__file__))})
    p['status']='REJECTED_BOUNDED_COMMON_U1_CHANNELS' if failed else 'COMMON_U1_CHANNELS_SAMPLED_ONLY_ACTUAL_GATE_OPEN'
    p['planning_seconds']=round(time.monotonic()-tick,3)
    (OUT/'u1-free-channels-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=p['status'],routes=len(routes),failed=failed,seconds=p['planning_seconds'])),flush=True)


if __name__=='__main__':run()
