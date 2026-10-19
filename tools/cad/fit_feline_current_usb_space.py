"""Coupled USB500 space proposal, not another frozen local prefix.

R30, both actual jacket mouths, first3 and full9 at BOTH ends are fixed.
Both bend angles are design variables: mandatory90 was not supplier data.
Allocate BOTH prefixes WITH the full middle and retained500mm cable.
Signed volume fields propose only; no native/clearance/retention PASS follows.
"""
import json,math,os,sys,time
from pathlib import Path
import numpy as np
from scipy.interpolate import BSpline
from scipy.ndimage import map_coordinates,distance_transform_edt
from scipy.sparse.csgraph import connected_components,dijkstra
from scipy.optimize import least_squares
from scipy.spatial.distance import cdist
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_cubic_curvature import clamped_knots,extrema,exact_length
from propose_feline_current_corridors import nearest_cell
from propose_feline_sparse_corridors import grid_graph


def swept_prefix(mouth,d,b,angle):
    q=np.asarray(mouth,float);d=np.asarray(d,float);b=np.asarray(b,float)
    assert abs(d@b)<1e-8 and abs(np.linalg.norm(d)-1)<1e-8 and abs(np.linalg.norm(b)-1)<1e-8
    a=q+3*d;v=np.linspace(0,angle,41)
    points=a+30*np.sin(v[:,None])*d+30*(1-np.cos(v[:,None]))*b
    tangent=math.cos(angle)*d+math.sin(angle)*b;end=points[-1];tip=end+9*tangent
    return tip,tangent,np.vstack([q,a,points,end+np.linspace(0,9,10)[:,None]*tangent]),12+30*angle


def pi_prefix(mouth,angle,clock):
    return swept_prefix(mouth,[-1,0,0],[0,math.cos(clock),math.sin(clock)],angle)


def bus_prefix(mouth,angle,clock):
    return swept_prefix(mouth,[0,-1,0],[math.cos(clock),0,math.sin(clock)],angle)


def scoring_points(prefix,pos,post):
    # Weights, not variable-length slices: optimization residual dimension
    # must remain fixed when either prefix angle passes the6mm own-boot gate.
    along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(prefix,axis=0),axis=1))]
    postalong=np.r_[0,np.cumsum(np.linalg.norm(np.diff(post,axis=0),axis=1))]
    return np.vstack([prefix,pos,post]),np.r_[(along>=6).astype(float),np.ones(len(pos)),(postalong>=6).astype(float)]


def biarc_join(p,t,q,u,ratio,sample=True):
    """Two exact spatial circular arcs with a common tangent, no soft R."""
    p,t,q,u=map(lambda x:np.asarray(x,float),(p,t,q,u));v=q-p
    alpha=(1-float(t@u))*ratio;beta=float(v@(ratio*t+u));square=float(v@v)
    if alpha<1e-12:
        if beta<=0:return None
        d1=square/(2*beta)
    else:d1=square/(math.sqrt(beta*beta+2*alpha*square)+beta)
    d0=ratio*d1;middle=(d1*p+d0*q+d0*d1*(t-u))/(d0+d1)
    arcs=[]
    for start,tangent,end,reverse in ((p,t,middle,False),(q,-u,middle,True)):
        w=end-start;x=float(w@tangent);normal=w-x*tangent;y=float(np.linalg.norm(normal))
        if y<1e-9:
            if x<=0:return None
            radius=None;angle=0.;L=x;points=np.linspace(start,end,49) if sample else None;final=tangent
        else:
            normal/=y;radius=float(w@w)/(2*y);angle=2*math.atan2(y,x);L=radius*angle
            a=np.linspace(0,angle,97)[:,None];points=start+radius*np.sin(a)*tangent+radius*(1-np.cos(a))*normal if sample else None
            final=math.cos(angle)*tangent+math.sin(angle)*normal
        arcs.append(dict(start_mm=start.tolist(),start_tangent=tangent.tolist(),normal=normal.tolist(),R_mm=radius,angle_rad=angle,
            length_mm=L,reverse=reverse,points_mm=None if points is None else points.tolist(),junction_tangent=final.tolist()))
    assert np.linalg.norm(np.array(arcs[0]['junction_tangent'])+np.array(arcs[1]['junction_tangent']))<1e-6
    return dict(arcs=arcs,length_mm=sum(a['length_mm'] for a in arcs),
        minimum_R_mm=min((a['R_mm'] for a in arcs if a['R_mm'] is not None),default=math.inf))


def main():
    tick=time.monotonic();src=OUT/'n01-current-signed-space.json';doc=json.loads(src.read_text())
    assert doc['status']=='CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY'
    fp=ROOT/doc['field'];assert sha(fp)==doc['field_sha256']
    cp=OUT/'n01-physical-cable-contract.json';usb=json.loads(cp.read_text())['usb']
    with np.load(fp,allow_pickle=False) as a:
        origin=a['origin_mm'];rigid=a['rigid_signed_distance'];motion=a['motion36_signed_distance'];outer=a['outer_distance'];inside=a['inside'];harness=a['harness_signed_distance']
    mouth=usb['pi_jacket_mouth_mm'];busmouth=usb['bus_jacket_mouth_mm']
    free=inside&(rigid>=4.95)&(motion>=4.95)&(outer>=6.95)
    graph_ids,graph=grid_graph(free,3*np.maximum(0,3.9-harness));coarse=graph_ids>=0
    _,components=connected_components(graph,directed=False);main=np.zeros(coarse.shape,bool);main[coarse]=components==int(np.bincount(components).argmax())
    nearest=distance_transform_edt(~main,return_distances=False,return_indices=True);lookup=np.argwhere(coarse)
    field=[rigid,motion,outer]
    count=12;knots=clamped_knots(count);u=np.linspace(0,1,193);basis=BSpline(knots,np.eye(count),3)
    M=basis(u);D1=basis(u,1);D2=basis(u,2);dest=OUT/'n01-current-coupled-usb-space.json'
    result=dict(status='RUNNING_COUPLED_USB_SPACE',source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (src,fp,cp,Path(__file__),Path(__file__).with_name('feline_cubic_curvature.py'),Path(__file__).with_name('propose_feline_sparse_corridors.py'),Path(__file__).with_name('propose_feline_current_corridors.py'))},
        attempts=[],candidate=None,N01_complete=False,physical_pass=False,selected=False,
        cause_change='BOTH artificial90degree design sweeps freed together with WHOLE middle; R30/OD5/first3/full9each/mouths/bought500 unchanged',
        complete_full_grip_body_root_and_exact_BRep_gate_open=True,field_only_not_clearance=True)
    if dest.exists():
        prior=json.loads(dest.read_text());own=Path(__file__).relative_to(ROOT).as_posix()
        assert '--receive-empty-dimension-error' in sys.argv and prior['status']=='RUNNING_COUPLED_USB_SPACE' and not prior['attempts'] and prior['candidate'] is None
        assert prior['source_sha256'][own]=='7821486427284e15188c59719493f9aaee06cf8d42f830771ae646684faba53a'
        assert all(h==result['source_sha256'][p] for p,h in prior['source_sha256'].items() if p!=own)
        result['received_empty_controller_error']=dict(previous_source_sha256=prior['source_sha256'],previous_result_sha256=sha(dest),
            error='ValueError residual changed849to852 before any completed attempt',
            fix='Constant point count with own-boot weights, no variable slice; geometric inputs unchanged; regression added')
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    save()
    class Cap(Exception):pass
    for angle in (math.radians(5),math.radians(30)):
        st=time.monotonic();q0,t0,_,pl=pi_prefix(mouth,angle,math.radians(-60))
        goal,bust,_,bl=bus_prefix(busmouth,angle,math.radians(-90));v1=-bust
        anchors=[]
        for p in (q0,goal):
            cell=np.rint((p-origin)/2).astype(int);assert np.all(cell>=0) and np.all(cell<coarse.shape)
            anchors.append(nearest_cell(nearest,cell))
        start,finish=[int(graph_ids[tuple(a)]) for a in anchors];dist,pred=dijkstra(graph,directed=False,indices=start,return_predecessors=True)
        assert np.isfinite(dist[finish]);nodes=[finish]
        while nodes[-1]!=start:
            previous=int(pred[nodes[-1]]);assert previous>=0 and len(nodes)<=graph.shape[0];nodes.append(previous)
        nodes.reverse()
        poly=np.vstack([q0,origin+2*lookup[nodes],goal]);s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(poly,axis=0),axis=1))]
        keep=np.r_[True,np.diff(s)>1e-8];poly=poly[keep];s=s[keep]
        initial=np.column_stack([np.interp(np.linspace(0,s[-1],count),s,poly[:,i]) for i in range(3)])
        # Entire prefix is variable, not accepted independently and frozen.
        x0=np.r_[initial[2:-2].ravel(),15.,15.,angle,math.radians(-60),angle,math.radians(-90)]
        low=np.r_[np.tile([-136.,-92.,-42.],count-4),1,1,0,math.radians(-165),0,-math.pi]
        high=np.r_[np.tile([178.,92.,106.],count-4),70,70,math.pi/2,math.radians(15),math.pi/2,math.pi]
        x0=np.clip(x0,low+1e-7,high-1e-7);best=dict(score=math.inf,x=x0.copy());calls=0
        def controls(x):
            tip,tangent,prefix,L=pi_prefix(mouth,x[-4],x[-3])
            goal,bust,post,BL=bus_prefix(busmouth,x[-2],x[-1]);v1=-bust
            return np.vstack([tip,tip+tangent*x[-6],x[:-6].reshape(-1,3),goal-v1*x[-5],goal]),prefix,L,post,BL
        def evaluate(x,metrics=False):
            nonlocal calls
            calls+=1
            if not metrics and (time.monotonic()-st>45 or time.monotonic()-tick>115):raise Cap()
            c,prefix,PL,post,BL=controls(x);pos=M@c;v=D1@c;acc=D2@c;speed=np.linalg.norm(v,axis=1)
            curvature=np.linalg.norm(np.cross(v,acc),axis=1)/np.maximum(speed,1e-8)**3
            # Only nominal own-mould neighbourhood is excluded from proposal
            # scoring. Whole first segment remains a required exact interface.
            points,weights=scoring_points(prefix,pos,post);coords=(points-origin).T
            gaps=[map_coordinates(z,coords,order=1,mode='constant',cval=-100,prefilter=False) for z in field]
            L=float(np.trapz(speed,u));whole=np.vstack([prefix,pos,post[::-1]]);along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(whole,axis=0),axis=1))]
            pair=cdist(whole,whole);pair[np.abs(along[:,None]-along[None,:])<=10]=1e6;selfgap=float(pair.min())
            residual=np.r_[3*np.maximum(0,4.1-gaps[0])*weights,3*np.maximum(0,4.1-gaps[1])*weights,3*np.maximum(0,6.1-gaps[2])*weights,
                40*np.maximum(0,30.3*curvature-1),[L+PL+BL-452],
                [5*max(0,5.3-selfgap)],.002*(c[2:-2]-initial[2:-2]).ravel()]
            score=float(residual@residual)
            if score<best['score']:best.update(score=score,x=x.copy())
            if metrics:return dict(score=score,rigid_axis_gap_mm=float(gaps[0][weights>0].min()),motion_axis_gap_mm=float(gaps[1][weights>0].min()),outer_axis_gap_mm=float(gaps[2][weights>0].min()),self_axis_gap_mm=selfgap,sampled_middle_length_mm=L,sampled_full_outside_mm=L+PL+BL)
            return residual
        message='';capped=False
        try:
            opt=least_squares(evaluate,x0,bounds=(low,high),max_nfev=220,diff_step=1e-4,ftol=1e-6,xtol=1e-6,gtol=1e-6);message=str(opt.message)
        except Cap:capped=True;message='Bounded45s attempt/115s whole family; best state saved, not accepted'
        x=best['x'];c,prefix,PL,post,BL=controls(x);metrics=evaluate(x,True);analytic=extrema(knots,c);L,error=exact_length(knots,c)
        R=analytic.get('minimum_radius_mm');eligible=bool(analytic['regular'] and (R is None or R>=30) and abs(L+PL+BL-452)<.05 and metrics['rigid_axis_gap_mm']>=3.75 and metrics['motion_axis_gap_mm']>=3.75 and metrics['outer_axis_gap_mm']>=5.75 and metrics['self_axis_gap_mm']>=5.2)
        row=dict(initial_angle_degrees=math.degrees(angle),Pi_sweep_degrees=math.degrees(x[-4]),Pi_clock_degrees=math.degrees(x[-3]),BUS_sweep_degrees=math.degrees(x[-2]),BUS_clock_degrees=math.degrees(x[-1]),controls_mm=c.tolist(),knots=knots.tolist(),degree=3,
            Pi_prefix_samples_mm=prefix.tolist(),Pi_prefix_length_mm=PL,BUS_prefix_samples_mm=post.tolist(),BUS_prefix_length_mm=BL,whole_external_length_mm=L+PL+BL,quadrature_error_mm=error,
            continuous_curvature=analytic,sampled_metrics=metrics,numeric_eligible_not_BRep_PASS=eligible,seconds=round(time.monotonic()-st,3),calls=calls,capped=capped,message=message)
        result['attempts'].append(row);save();print(json.dumps(dict(initial_angle=row['initial_angle_degrees'],length=row['whole_external_length_mm'],R=R,eligible=eligible,seconds=row['seconds'])),flush=True)
        if eligible:result['candidate']=row;break
    result['status']='COUPLED_USB_NUMERIC_CANDIDATE_EXACT_BODY_GRIPS_ROOTS_OPEN' if result['candidate'] else 'COUPLED_USB_TWO_ATTEMPTS_REQUIRE_CAUSE_REVIEW_NOT_N01'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'])),flush=True)


def planned_pi_transform(pose,centre):
    import FreeCAD as A
    from receive_feline_global_case_candidates import placement
    rot=placement(np.asarray(pose['rotation'],float),np.zeros(3)).Rotation
    target=A.Vector(*pose['target_PCB_centre_mm'])
    return A.Placement(target-rot.multVec(centre),rot)


def screen_rear_facing_pi():
    """One whole-module cause change; no native/source or selected edits."""
    import FreeCAD as A
    import Part
    from feline_common_space_context import current,is_jacket
    from feline_fore_power_pair import SolidQueries,pair_spacing
    from feline_solid_distance import bbox_lower_bound
    from receive_feline_global_case_candidates import placement
    tick=time.monotonic();world,parts,meta,pins,docs=current()
    underhung='--underhung-flat-pi' in sys.argv
    planned=underhung or '--planned-flat-pi' in sys.argv
    if planned:
        planfile=OUT/'n01-whole-pi-rigid-ports-space.json';plan=json.loads(planfile.read_text())
        assert plan['status']=='WHOLE_PI_RIGID_PORT_POSE_PROPOSALS_ALL_NEW_LOOMS_OPEN'
        pose=next(p for p in plan['proposals'] if p['orientation_index']==0) if underhung else plan['proposals'][0]
        pins[planfile.relative_to(ROOT).as_posix()]=sha(planfile)
        lowerfile=OUT/'n01-usb-fore-lower-deck-space.json';lowerdoc=json.loads(lowerfile.read_text())
        assert lowerdoc['status']=='TWO_WHOLE_FORE_KITS_LOWER_DECK_SPACE_RECEIVED_USB_ROOTS_OPEN'
        for n in lowerdoc['changed_owners']:parts[n]=parts[n].copy();parts[n].translate(A.Vector(0,0,-8))
        pins[lowerfile.relative_to(ROOT).as_posix()]=sha(lowerfile)
    coupled='--usb-led-layout' in sys.argv
    own={n:s for n,s in parts.items() if meta[n].get('group')=='PiUpper'}
    assert 'Ref_Material_Pi4NominalPCB_0_0' in own and len(own)>35
    centre=own['Ref_Material_Pi4NominalPCB_0_0'].BoundBox.Center
    inverted='--inverted-pi' in sys.argv
    rot=A.Rotation(A.Vector(1,0,0) if inverted else A.Vector(0,0,1),180)
    target=A.Vector(centre.x,centre.y,99) if inverted else centre
    tf=planned_pi_transform(pose,centre) if planned else A.Placement(target-rot.multVec(centre),rot)
    if planned:rot=tf.Rotation;target=tf.multVec(centre)
    changed={}
    for n,s in own.items():
        if n.startswith('PiUSBData') or (inverted and n.startswith(('PiGPIO:','PiPower:'))):continue
        q=s.copy();q.Placement=tf*q.Placement;assert q.isValid() and q.Solids,n
        changed[n]=q
    cp=OUT/'n01-physical-cable-contract.json';usb=json.loads(cp.read_text())['usb']
    mouth=np.array(list(tf.multVec(A.Vector(*usb['pi_jacket_mouth_mm']))))
    d=np.array([-1.,0,0]) if inverted else np.array([1.,0,0])
    b=np.array([0.,-1,0]) if inverted else np.array([0.,math.sqrt(.84),-.4])
    R=30.5 if inverted else 30.;angle=math.pi/2 if inverted else math.pi;start=mouth+3*d
    if planned:
        d=np.array(pose['USB_departure_axis']);b=np.array([0.,0.,-1.]);R=30.;angle=math.pi/2;start=mouth+12*d
    if underhung:
        a=math.radians(16);b=np.array([0.,-math.cos(a),-math.sin(a)]);start=mouth+3*d
    point=lambda v:start+R*math.sin(v)*d+R*(1-math.cos(v))*b
    tangent=math.cos(angle)*d+math.sin(angle)*b;end=point(angle);tip=end+9*tangent
    path=Part.Wire([Part.makeLine(A.Vector(*mouth),A.Vector(*start)),Part.Arc(A.Vector(*start),A.Vector(*point(angle/2)),A.Vector(*end)).toShape(),Part.makeLine(A.Vector(*end),A.Vector(*tip))])
    if planned and not underhung:
        tip=end.copy();path=Part.Wire([Part.makeLine(A.Vector(*mouth),A.Vector(*start)),Part.Arc(A.Vector(*start),A.Vector(*point(angle/2)),A.Vector(*end)).toShape()])
    prefix=path.makePipeShell([Part.Wire([Part.makeCircle(2.5,A.Vector(*mouth),A.Vector(*d))])],True,False)
    assert prefix.isValid() and len(prefix.Solids)==1 and abs(prefix.Volume-math.pi*2.5**2*path.Length)<1e-4
    changed['RearPiUSBPrefix']=prefix
    cm={**{n:meta[n] for n in own},'RearPiUSBPrefix':dict(kind='proposal_wire')}
    routes={}
    units={n:'Pi' for n in changed};units['RearPiUSBPrefix']='USB'
    if coupled:
        def unit(n):
            g=meta[n].get('group','')
            if g=='S0' or g in ('Source:W066/retained0/start','Source:W076/retained1/end'):return 'S0'
            return g if g in ('MAINUpper','D_RR','Monitor') else None
        own={n:s for n,s in parts.items() if unit(n) is not None or n.startswith('PiUSBData')}
        changed={};units={};cm={}
        pivot=parts['Ref_Material_S0_body_CP2_0_0'].BoundBox.Center
        spin=A.Rotation(A.Vector(0,0,1),90)
        main=parts['Ref_Material_MAIN_CurrentMainSupplierReference_0_0'].BoundBox.Center
        case=parts['Station:D_RR:case'].BoundBox.Center
        poses={'S0':A.Placement(pivot-spin.multVec(pivot),spin),'MAINUpper':A.Placement(A.Vector(125-main.x,64-main.y,0),A.Rotation()),
               'D_RR':A.Placement(A.Vector(125-case.x,-70-case.y,0),A.Rotation()),'Monitor':A.Placement(A.Vector(0,0,-8),A.Rotation())}
        for n,s in own.items():
            group=unit(n)
            if group is None:continue
            q=s.copy();q.Placement=poses[group]*q.Placement;assert q.isValid() and q.Solids,n
            changed[n]=q;units[n]=group;cm[n]=dict(meta[n])
        assert sum(g=='S0' for g in units.values())==19 and sum(g=='MAINUpper' for g in units.values())==18
        mouth=np.asarray(usb['pi_jacket_mouth_mm']);d=np.array([-1.,0,0]);v=math.radians(10);bend=np.array([0.,-math.cos(v),math.sin(v)])
        p=mouth.copy();edges=[]
        def line_to(q):
            nonlocal p
            edges.append(Part.makeLine(A.Vector(*p),A.Vector(*q)));p=q
        def turn(t,b,r,angle):
            nonlocal p
            at=lambda z:p+r*math.sin(z)*t+r*(1-math.cos(z))*b
            end=at(angle);edges.append(Part.Arc(A.Vector(*p),A.Vector(*at(angle/2)),A.Vector(*end)).toShape());p=end
        line_to(p+3*d);turn(d,bend,30.5,math.pi/2);grip_start=p.copy();line_to(p+9*bend);grip_end=p.copy()
        turn(bend,np.array([0.,-math.sin(v),-math.cos(v)]),30,v)
        turn(np.array([0.,-1,0]),np.array([1.,0,0]),30.5,math.pi/2)
        path=Part.Wire(edges);prefix=path.makePipeShell([Part.Wire([Part.makeCircle(2.5,A.Vector(*mouth),A.Vector(*d))])],True,False)
        assert prefix.isValid() and len(prefix.Solids)==1
        changed['RearPiUSBPrefix']=prefix;units['RearPiUSBPrefix']='USB';cm['RearPiUSBPrefix']=dict(kind='proposal_wire');tip=p.copy();R=30.;angle=math.pi/2
        routes['USB_SOURCE']=dict(mouth_mm=mouth.tolist(),full9_mm=[grip_start.tolist(),grip_end.tolist()],tip_mm=tip.tolist(),length_mm=path.Length,minimum_R_mm=30)
        for n,r in cm.items():
            if r.get('kind') in ('band_budget','head_budget'):r['kind']='project_stock_reservation'
    if inverted:
        from check_feline_shared_space import tube_prefix
        from plan_feline_front_service_split import line_tube
        portfile=OUT/'n01-shared-routing-boundaries.json';ends=json.loads(portfile.read_text())['endpoints']
        for e in ends:
            name='PiGPIO:'+e.get('endpoint','') if e.get('endpoint','').startswith('PI.H') else 'PiPower:'+e['wire']
            if e.get('group')!='Pi4' or name not in own:continue
            p=e.get('jacket_routing_point_mm',e.get('point_mm'));v=e.get('jacket_departure_axis',e.get('departure_axis'))
            q=tf.multVec(A.Vector(*p));axis=rot.multVec(A.Vector(*v));axis.normalize()
            desired=A.Vector(0,-1,0) if name.startswith('PiGPIO:') else A.Vector(0,1,0)
            bend=desired-axis*desired.dot(axis);bend.normalize()
            radius=.7 if name.startswith('PiGPIO:') else 1.55
            bendR=10 if name.startswith('PiGPIO:') else 15.9 if e['wire']=='W079' else 12.4
            first=1.5 if name.startswith('PiGPIO:') else 9
            end=q+axis*(first+bendR)+bend*bendR;finish=end+bend*9
            changed[name]=tube_prefix(list(q),list(axis),radius,list(bend),bendR,first)
            changed[name+':grip']=line_tube(list(end),list(finish),radius)
            cm[name]=cm[name+':grip']=dict(kind='proposal_wire')
            routes[e['id']]=dict(point_mm=list(q),departure_axis=list(axis),bend_unit=list(bend),R_mm=bendR,first_mm=first,full9_mm=[list(end),list(finish)])
        assert len(routes)==7
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
    result=dict(status='RUNNING_WHOLE_REAR_FACING_PI_NOT_N01',source_sha256={**pins,cp.relative_to(ROOT).as_posix():sha(cp),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        pivot_mm=list(centre),target_PCB_centre_mm=list(target),rotation_axis='X' if inverted else 'Z',rotation_degrees=180,changed_owners=list(changed),retired_USB_prefixes=[n for n in own if n.startswith('PiUSBData')],
        new_seven_port_prefixes=routes,USB_jacket_mouth_mm=mouth.tolist(),USB_prefix_tip_mm=tip.tolist(),USB_prefix_length_mm=12+R*angle,USB_min_R_mm=R,
        internal_rigid_Pi_relations_reused=True,checks=[],failures=[],N01_complete=False,selected=False,physical_pass=False,
        old_Pi_datums_roots_and_assembly_invalidated_if_adopted=True,whole_USB500_middle_and_full_grips_open=True)
    if coupled:result.update(changed_owners=list(changed),whole_changed_groups=units,Pi_PCB_and_all_other_ports_unchanged=True,old_Pi_datums_roots_and_assembly_invalidated_if_adopted=False,USB_prefix_length_mm=path.Length,USB_min_R_mm=30,new_seven_port_prefixes=routes)
    if planned:result.update(status='RUNNING_PLANNED_FLAT_PI_WHOLE_PORTS_PREFIXES',selected_pose=pose,
        old_unrelated180Z_metadata_not_applicable=True,rotation_matrix=pose['rotation'],rotation_axis=None,rotation_degrees=None,
        USB_prefix_length_mm=path.Length,USB_full9_before_bend_mm=None if underhung else [(mouth+3*d).tolist(),start.tolist()],
        USB_full9_after_bend_mm=[end.tolist(),tip.tolist()] if underhung else None,
        USB_prefix_tip_tangent=tangent.tolist(),other_GPIO_and_power_full_prefixes_rigidly_reoriented_NOT_new_routing_PASS=True)
    dest=OUT/('n01-underhung-flat-pi-port-prefix-space.json' if underhung else 'n01-whole-flat-pi-port-prefix-space.json' if planned else 'n01-usb-led-layout-space.json' if coupled else 'n01-inverted-pi-space.json' if inverted else 'n01-rear-facing-pi-space.json');assert not planned or not dest.exists();query=SolidQueries()
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def record(a,b,gap,minimum):
        r=dict(a=a,b=b,gap_mm=gap,minimum_mm=minimum,ok=gap>=minimum-1e-6);result['checks'].append(r)
        if not r['ok']:result['failures'].append(r)
        if len(result['checks'])%10==0:save()
    save()
    try:
        for n,s in changed.items():
            if time.monotonic()-tick>180:raise TimeoutError('Changed whole-module gate saved, not a geometry verdict')
            outside=s.copy().cut(outer);assert outside.isNull() or outside.isValid()
            record(n,'outer',s.distToShape(outer.Shells[0])[0] if outside.Volume<1e-5 else -outside.Volume,3.25)
            targets={k:v for k,v in parts.items() if k not in own}
            if coupled:
                targets.update({k:v for k,v in changed.items() if units[k]!=units[n]})
                if n=='RearPiUSBPrefix':targets.pop('PiBudget:USB_A_data_boot',None)
            if n=='RearPiUSBPrefix' or ((inverted or planned) and n.startswith(('PiGPIO:','PiPower:'))):
                mates={'PiBudget:USB_A_data_boot'} if n=='RearPiUSBPrefix' else {'PiBudget:GPIO1992OccupiedHousing','PiBudget:GPIO_header'} if n.startswith('PiGPIO:') and not n.endswith(':grip') else {'PiBudget:RetainedK1474Boot'} if n.startswith('PiPower:') and not n.endswith(':grip') else set()
                if n.endswith(':grip'):mates.add(n[:-5])
                else:mates.add(n+':grip')
                targets.update({k:v for k,v in changed.items() if k!=n and k not in mates})
            for other,t in targets.items():
                minimum=pair_spacing(n,cm[n],other,cm.get(other,meta.get(other,{})))
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                q=s
                if other==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
                if not t.Solids:result['failures'].append(dict(a=n,b=other,reason='curve-only source requires physical budget'));continue
                record(n,other,query.distance(q,t),minimum)
            for p in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
                q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
                record(n,'motion:'+p['name']+':'+str(p['pose']),query.distance(q,world.rest[p['name']]),1.25)
            save();print('RECEIVED',n,'failures',len(result['failures']),flush=True)
        result['status']=('PLANNED_FLAT_PI_WHOLE_PORTS_PREFIX_SPACE_ONLY' if not result['failures'] else 'PLANNED_FLAT_PI_WHOLE_PREFIX_INTERFACES_REJECTED') if planned else 'REAR_FACING_PI_AND_PREFIX_SPACE_ONLY' if not result['failures'] else 'WHOLE_REAR_FACING_PI_REJECTED'
    except Exception as exc:result['status']='WHOLE_REAR_FACING_PI_INCOMPLETE';result['error']=repr(exc)
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],failures=result['failures'])),flush=True)


def couple_saved_trees():
    """Join received positive trees, distributing slack at BOTH ends."""
    from scipy.spatial import cKDTree
    from scipy.optimize import brentq
    tick=time.monotonic();paths=[OUT/n for n in ('n01-usb-lower-deck-forward-half-space.json','n01-usb-lower-deck-reverse-biarc-space.json')]
    docs=[json.loads(p.read_text()) for p in paths];trees=[]
    for d in docs:
        p=ROOT/d['tree'];assert sha(p)==d['tree_sha256']
        with np.load(p,allow_pickle=False) as f:trees.append({k:f[k] for k in f.files})
    for key in ('entry','bus_entry','proposal_axis_thresholds_mm','external_target_mm'):
        assert docs[0][key]==docs[1][key],key
    sf=OUT/'n01-two-fore-lower-deck-signed-space.json';s=json.loads(sf.read_text());fp=ROOT/s['field'];assert sha(fp)==s['field_sha256']
    for d in docs:assert d['source_sha256'][fp.relative_to(ROOT).as_posix()]==s['field_sha256']
    with np.load(fp,allow_pickle=False) as f:
        origin=f['origin_mm'];fields=[f[n] for n in ('rigid_signed_distance','motion36_signed_distance','outer_distance')]
    thresholds=np.array(docs[0]['proposal_axis_thresholds_mm']);a,b=trees
    contract=OUT/'n01-physical-cable-contract.json';usb=json.loads(contract.read_text())['usb'];entry=docs[0]['entry']
    length=usb['remaining_middle_budget_mm']-entry['extra_length_mm']
    directional='--directional-tree-pairs' in sys.argv
    dest=OUT/('n01-usb-directional-two-ended-space.json' if directional else 'n01-usb-two-ended-coupled-space.json');assert not dest.exists()
    result=dict(status='RUNNING_RECEIVED_TWO_ENDED_TREE_COUPLING',source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*paths,*(ROOT/d['tree'] for d in docs),sf,fp,contract,Path(__file__))},
        candidate=None,queue_pairs=0,checked_pairs=0,root_matches=0,minimum_R_matches=0,field_matches=0,
        N01_complete=False,physical_pass=False,selected=False,entry=entry,bus_entry=docs[0]['bus_entry'],
        all_received_tree_primitives_reused=True,full_grips_roots_current_harness_BRep_gates_OPEN=True)
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def clear(points):
        coords=(np.asarray(points)-origin).T
        return np.stack([map_coordinates(f,coords,order=1,mode='constant',cval=-100,prefilter=False) for f in fields],axis=1)-thresholds
    def chain(tree,j,reverse=False):
        rows=[]
        while tree['parents'][j]>=0:
            parent=int(tree['parents'][j]);normal=tree['normals'][j]
            rows.append(dict(start_mm=tree['positions_mm'][parent].tolist(),start_tangent=tree['tangents'][parent].tolist(),
                normal=None if np.isnan(normal).all() else normal.tolist(),length_mm=8.,R_mm=30.1,reverse=reverse))
            j=parent
        if not reverse:rows.reverse()
        return rows
    def samples(rows):
        answer=[]
        for r in rows:
            p=np.array(r['start_mm']);t=np.array(r['start_tangent']);u=np.linspace(0,r['length_mm'],33)
            if r['normal'] is None:points=p+u[:,None]*t
            else:
                R=r['R_mm'];n=np.array(r['normal']);v=u[:,None]/R
                points=p+R*np.sin(v)*t+R*(1-np.cos(v))*n
            answer.extend(points[::-1] if r['reverse'] else points)
        return np.array(answer)
    ids=np.flatnonzero((b['lengths_mm']>=24)&(b['lengths_mm']<=208))
    lookup=cKDTree(np.column_stack([b['positions_mm'][ids]/40,-b['tangents'][ids]]));queue=[]
    for i in np.flatnonzero((a['lengths_mm']>=24)&(a['lengths_mm']<=184))[::2]:
        aim=a['positions_mm'][i]+(60*a['tangents'][i] if directional else 0)
        _,near=lookup.query(np.r_[aim/40,a['tangents'][i]],k=24)
        for j in ids[near]:
            remain=length-a['lengths_mm'][i]-b['lengths_mm'][j];chord=float(np.linalg.norm(a['positions_mm'][i]-b['positions_mm'][j]))
            if not (20<remain<150 and chord<remain<2.2*chord):continue
            if directional:
                vector=b['positions_mm'][j]-a['positions_mm'][i]
                if vector@a['tangents'][i]<=0 or vector@(-b['tangents'][j])<=0:continue
            join=biarc_join(a['positions_mm'][i],a['tangents'][i],b['positions_mm'][j],-b['tangents'][j],1.,False)
            if join is None or not .65*remain<join['length_mm']<1.5*remain:continue
            queue.append((abs(join['length_mm']-remain),int(i),int(j),float(remain)))
    queue.sort();result['queue_pairs']=len(queue);save()
    for _,i,j,remain in queue[:6000]:
        if time.monotonic()-tick>100:break
        result['checked_pairs']+=1;previous=None
        for ratio in np.logspace(-3,3,19):
            join=biarc_join(a['positions_mm'][i],a['tangents'][i],b['positions_mm'][j],-b['tangents'][j],float(ratio),False)
            if join is None:continue
            delta=join['length_mm']-remain
            if previous and delta*previous[1]<=0:
                root=brentq(lambda r:biarc_join(a['positions_mm'][i],a['tangents'][i],b['positions_mm'][j],-b['tangents'][j],r,False)['length_mm']-remain,previous[0],ratio,xtol=1e-10)
                result['root_matches']+=1
                join=biarc_join(a['positions_mm'][i],a['tangents'][i],b['positions_mm'][j],-b['tangents'][j],root)
                if join['minimum_R_mm']>=30:
                    result['minimum_R_matches']+=1
                    joined=np.vstack([join['arcs'][0]['points_mm'],join['arcs'][1]['points_mm'][::-1]])
                    if clear(joined).min()>=0:
                        result['field_matches']+=1
                        fore=chain(a,i);rear=chain(b,j,True)
                        whole=np.vstack([entry['source_prefix_samples_mm'],entry['flatten_samples_mm'],samples(fore),joined,samples(rear),docs[0]['bus_entry']['prefix_samples_mm'][::-1]])
                        along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(whole,axis=0),axis=1))]
                        pairs=cdist(whole,whole);pairs[np.abs(along[:,None]-along[None,:])<=10]=1e6;self_gap=float(pairs.min())
                        if self_gap>=5.2:
                            result['candidate']=dict(forward_node=i,backward_node=j,fore_primitives=fore,connector=join,rear_primitives=rear,
                                full_samples_mm=whole.tolist(),sampled_self_axis_gap_mm=self_gap,
                                whole_external_length_mm=usb['pi_prefix_length_mm']+entry['extra_length_mm']+a['lengths_mm'][i]+join['length_mm']+b['lengths_mm'][j]+usb['bus_prefix_length_mm'],
                                nominal_jacket_OD_mm=5,minimum_piecewise_R_mm=min(30.1,join['minimum_R_mm'],30.),all_end_tangents_constructive_C1=True)
                            break
            previous=(ratio,delta)
        if result['candidate']:break
        if result['checked_pairs']%100==0:save()
    result['status']='WHOLE_USB500_TWO_ENDED_NUMERIC_PROPOSAL_EXACT_GATES_OPEN' if result['candidate'] else 'BOUNDED_RECEIVED_TREE_COUPLING_NO_CANDIDATE_NOT_INFEASIBILITY'
    save();print(json.dumps({k:result[k] for k in ('status','worker_seconds','queue_pairs','checked_pairs','root_matches','minimum_R_matches','field_matches')}),flush=True)


def receive_roof_fore_stations():
    """One lower common fore deck, not a cable-only scalar sweep.

    BOTH complete8part WAGO kits move one8mm level; native unchanged.
    Same-unit rigid/jacket relations and the other54units' receipts reused.
    """
    import FreeCAD as A
    import Part
    from feline_common_space_context import current
    from feline_fore_power_pair import SolidQueries,pair_spacing
    from feline_solid_distance import bbox_lower_bound
    from receive_feline_global_case_candidates import placement
    tick=time.monotonic();world,parts,meta,pins,docs=current();dest=OUT/'n01-usb-fore-lower-deck-space.json'
    assert not dest.exists(),'Receive prior whole fore deck gate before another hypothesis'
    own={n:s for n,s in parts.items() if meta[n].get('group') in ('FR_P','RR_P')};assert len(own)==16
    changed={}
    for n,s in own.items():
        q=s.copy();q.translate(A.Vector(0,0,-8));assert q.isValid() and q.Solids;changed[n]=q
    result=dict(status='RUNNING_TWO_WHOLE_FORE_KITS_LOWER_DECK',source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        changed_owners=list(changed),shift_mm=[0,0,-8],checks=[],failures=[],errors=[],N01_complete=False,physical_pass=False,selected=False,
        no_purchased_part_changed=True,full_mouths_first_curves_and9grips_preserved=True,all_old_changed_end_datums_and_roots_require_update_if_adopted=True,
        same_unit_and_unchanged_all_other_geometry_receipts_reused=True,whole_USB500_NOT_accepted=True)
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def record(a,b,gap,minimum):
        r=dict(a=a,b=b,gap_mm=gap,minimum_mm=minimum,ok=bool(gap>=minimum-1e-6));result['checks'].append(r)
        if not r['ok']:result['failures'].append(r)
        save()
    query=SolidQueries();outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'));save()
    try:
        for n,s in changed.items():
            if time.monotonic()-tick>180:raise TimeoutError('Whole changed-kit pairs saved; not geometric rejection')
            outside=s.copy().cut(outer);assert outside.isNull() or outside.isValid()
            record(n,'outer',float(s.distToShape(outer.Shells[0])[0]) if outside.Volume<1e-5 else -float(outside.Volume),3.25)
            targets={k:v for k,v in parts.items() if k not in own}
            targets.update({k:v for k,v in changed.items() if meta[k]['group']!=meta[n]['group']})
            for other,t in targets.items():
                minimum=pair_spacing(n,meta[n],other,meta.get(other,{}))
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                q=s
                if other==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
                if not t.Solids:result['failures'].append(dict(a=n,b=other,reason='curve-only physical occupancy unresolved'));continue
                record(n,other,query.distance(q,t),minimum)
            for p in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
                q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
                record(n,'motion:'+p['name']+':'+str(p['pose']),query.distance(q,world.rest[p['name']]),1.25)
            print('WHOLE_LOWER_FORE',n,'failures',len(result['failures']),flush=True)
        result['status']='TWO_WHOLE_FORE_KITS_LOWER_DECK_SPACE_RECEIVED_USB_ROOTS_OPEN' if not result['failures'] else 'TWO_WHOLE_FORE_KITS_LOWER_DECK_REJECTED'
    except Exception as exc:result.update(status='TWO_WHOLE_FORE_KITS_LOWER_DECK_INCOMPLETE');result['errors'].append(repr(exc))
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],failures=result['failures'],errors=result['errors'])),flush=True)


def usb_space_sections():
    """Inspect received volume slices before another placement proposal."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    sf=OUT/'n01-current-signed-space.json';d=json.loads(sf.read_text());fp=ROOT/d['field'];assert sha(fp)==d['field_sha256']
    usb=json.loads((OUT/'n01-physical-cable-contract.json').read_text())['usb']
    with np.load(fp,allow_pickle=False) as f:
        origin=f['origin_mm'];rigid=f['rigid_signed_distance'];motion=f['motion36_signed_distance'];outer=f['outer_distance']
    gap=np.minimum(np.minimum(rigid-3.75,motion-3.75),outer-5.75)
    fig,axes=plt.subplots(2,3,figsize=(15,9),layout='constrained')
    for ax,Z in zip(axes[0],(80,95,104)):
        idx=int(round(Z-origin[2]));ax.imshow(gap[:,:,idx].T,origin='lower',extent=[origin[0],origin[0]+gap.shape[0]-1,origin[1],origin[1]+gap.shape[1]-1],vmin=-8,vmax=8,cmap='RdYlGn')
        for key,col in (('pi','blue'),('bus','purple')):
            p=np.array(usb[key+'_prefix_exit_mm']);ax.scatter(*p[:2],c=col);ax.annotate(key,(p[0],p[1]))
        ax.set(title=f'XY, Z={Z}mm; USB axis gap surplus',xlabel='X mm',ylabel='Y mm');ax.set_aspect('equal')
    for ax,X in zip(axes[1],(0,60,128)):
        idx=int(round(X-origin[0]));ax.imshow(gap[idx,:,:].T,origin='lower',extent=[origin[1],origin[1]+gap.shape[1]-1,origin[2],origin[2]+gap.shape[2]-1],vmin=-8,vmax=8,cmap='RdYlGn')
        ax.set(title=f'YZ, X={X}mm; green=positive budget',xlabel='Y mm',ylabel='Z mm');ax.set_aspect('equal')
    fig.suptitle('Received conservative volume ONLY; green not exact clearance; R30 direction not shown')
    dest=OUT/'n01-usb-current-space-sections.png';fig.savefig(dest,dpi=120);plt.close(fig);print(dest,flush=True)


def curvature_beam_space():
    """Bounded whole-space search with hard R34 primitives, no soft R penalty.

    Reuses the signed closed-volume field. This can propose another topology,
    never prove infeasibility or qualify a rigid grip/native assembly.
    """
    tick=time.monotonic();lower='--lower-deck-entry' in sys.argv
    sf=OUT/('n01-two-fore-lower-deck-signed-space.json' if lower else 'n01-current-signed-space.json');doc=json.loads(sf.read_text());fp=ROOT/doc['field']
    cp=OUT/'n01-physical-cable-contract.json';usb=json.loads(cp.read_text())['usb'];assert sha(fp)==doc['field_sha256']
    with np.load(fp,allow_pickle=False) as f:
        origin=f['origin_mm'];fields=[f[n] for n in ('rigid_signed_distance','motion36_signed_distance','outer_distance')]
    start=np.array(usb['pi_prefix_exit_mm']);goal=np.array(usb['bus_prefix_exit_mm']);target=-np.array(usb['bus_prefix_exit_axis'])
    roof=lower or '--roof-entry' in sys.argv
    sidebus='--bus-inboard-entry' in sys.argv
    busentry=None
    if sidebus:
        goal,bust,samples,BL=bus_prefix(usb['bus_jacket_mouth_mm'],math.pi/2,math.pi)
        target=-bust;busentry=dict(exit_mm=goal.tolist(),outgoing_tangent=bust.tolist(),prefix_samples_mm=samples.tolist(),
            prefix_length_mm=BL,minimum_R_mm=30.,full9_after_bend=True)
    length=usb['remaining_middle_budget_mm'];step=8.;R=30.1 if roof else 34.;angle=step/R;v=np.linspace(0,1,17)
    entry=dict(p=start.tolist(),t=usb['pi_prefix_exit_axis'],extra_length_mm=0.)
    if roof:
        a=math.pi/12;p,t,source,PL=pi_prefix(usb['pi_jacket_mouth_mm'],math.pi/2,a)
        b=np.array([0.,math.sin(a),-math.cos(a)]);u=np.linspace(0,a,33)
        flatten=p+30*np.sin(u[:,None])*t+30*(1-np.cos(u[:,None]))*b
        start=flatten[-1];length-=30*a
        entry=dict(p=start.tolist(),t=[0.,1.,0.],extra_length_mm=30*a,source_prefix_samples_mm=source.tolist(),
            flatten_samples_mm=flatten.tolist(),source_prefix_length_mm=PL,source_full9_before_flatten=True,minimum_R_mm=30.,
            exact_flat_roof_axis_gap_mm=112-start[2],project_required_axis_gap_mm=5.75)
    # The old filter added1.2mm over the actual acceptance margin. For a
    # PROPOSAL the conservative occupied-volume field may use nominal gates;
    # exact BRep still decides, no clearance or insulation margin is waived.
    thresholds=np.array([3.75,3.75,5.75]) if roof else np.array([4.95,4.95,6.95]);rng=np.random.default_rng(20261019)
    biarc='--biarc-connector' in sys.argv
    reverse='--reverse-entry' in sys.argv
    half='--save-forward-half-tree' in sys.argv
    diverse='--diverse-slack-tree' in sys.argv
    search_tangent=np.array(entry['t'])
    if reverse:
        old_start=start.copy();start=goal.copy();goal=old_start
        old_target=target.copy();target=-search_tangent;search_tangent=-old_target
    dest=OUT/('n01-usb-lower-deck-diverse-slack-space.json' if diverse else 'n01-usb-lower-deck-forward-half-space.json' if half else 'n01-usb-lower-deck-reverse-biarc-space.json' if reverse else 'n01-usb-lower-deck-biarc-space.json' if biarc else 'n01-usb-lower-deck-inboard-bus-space.json' if sidebus else 'n01-usb-lower-deck-hard-curvature-space.json' if lower else 'n01-usb-hard-curvature-roof-space.json' if roof else 'n01-usb-hard-curvature-global-space.json')
    assert not dest.exists(),'Receive previous bounded search before a new attempt'
    result=dict(status='RUNNING_HARD_CURVATURE_GLOBAL_SPACE',source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (sf,fp,cp,Path(__file__))},
        R_primitives_mm=R,step_mm=step,entry=entry,bus_entry=busentry,search_runs_from_BUS_back_to_PI=reverse,proposal_axis_thresholds_mm=thresholds.tolist(),external_target_mm=usb['project_external_target_mm'],levels=[],candidate=None,
        field_only_not_clearance=True,full_source_prefixes_grips_roots_BRep_and_capacity_open=True,N01_complete=False,physical_pass=False,selected=False)
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def clear(points):
        shape=points.shape[:-1];coords=(points.reshape(-1,3)-origin).T
        values=np.stack([map_coordinates(f,coords,order=1,mode='constant',cval=-100,prefilter=False) for f in fields],axis=1)
        return (values-thresholds).min(axis=1).reshape(shape)
    # Nodes retain a parent and exact circular/straight primitive parameters.
    nodes=[dict(p=start,t=search_tangent,L=0.,parent=None,arc=None)]
    frontier=[0];save()
    begin_level=1
    if diverse:
        priorfile=OUT/'n01-usb-lower-deck-forward-half-space.json';prior=json.loads(priorfile.read_text())
        assert prior['entry']==entry and prior['bus_entry']==busentry and prior['source_sha256'][fp.relative_to(ROOT).as_posix()]==sha(fp)
        tree=ROOT/prior['tree'];assert sha(tree)==prior['tree_sha256']
        with np.load(tree,allow_pickle=False) as f:
            keep=np.flatnonzero(f['lengths_mm']<=56);assert np.array_equal(keep,np.arange(len(keep)))
            nodes=[dict(p=f['positions_mm'][i],t=f['tangents'][i],L=float(f['lengths_mm'][i]),parent=None if f['parents'][i]<0 else int(f['parents'][i]),
                arc=None if np.isnan(f['normals'][i]).all() else f['normals'][i].tolist()) for i in keep]
        frontier=[i for i,n in enumerate(nodes) if n['L']==56];begin_level=8
        result['reused_first7_positive_levels']=dict(report=priorfile.relative_to(ROOT).as_posix(),sha256=sha(priorfile),nodes=len(nodes))
    def connect(node):
        remain=length-node['L'];p=node['p'];t=node['t'];chord=np.linalg.norm(goal-p)
        if remain<chord or remain>chord*2.5 or remain>160:return None
        if biarc:
            from scipy.optimize import brentq
            previous=None
            for ratio in np.logspace(-3,3,25):
                join=biarc_join(p,t,goal,target,float(ratio))
                if join is None:continue
                delta=join['length_mm']-remain
                if previous and delta*previous[1]<=0:
                    root=brentq(lambda r:biarc_join(p,t,goal,target,r)['length_mm']-remain,previous[0],ratio,xtol=1e-10)
                    j=biarc_join(p,t,goal,target,root)
                    if j['minimum_R_mm']>=30 and all(clear(np.asarray(a['points_mm'])).min()>=0 for a in j['arcs']):
                        j.update(ratio=root,whole_external_length_mm=j['length_mm']+node['L']+usb['pi_prefix_length_mm']+entry['extra_length_mm']+usb['bus_prefix_length_mm'])
                        return j
                previous=(ratio,delta)
            return None
        for ratio in (.5,1.,2.):
            def evaluate(h,full=False):
                c=np.array([p,p+h*t,goal-h*ratio*target,goal]);uu=np.linspace(0,1,193 if full else 49);z=uu[:,None]
                q=(1-z)**3*c[0]+3*(1-z)**2*z*c[1]+3*(1-z)*z*z*c[2]+z**3*c[3]
                d=3*((1-z)**2*(c[1]-c[0])+2*(1-z)*z*(c[2]-c[1])+z*z*(c[3]-c[2]))
                dd=6*((1-z)*(c[2]-2*c[1]+c[0])+z*(c[3]-2*c[2]+c[1]))
                speed=np.linalg.norm(d,axis=1);L=float(np.trapz(speed,uu))
                if not full:return L
                curvature=np.linalg.norm(np.cross(d,dd),axis=1)/np.maximum(speed,1e-10)**3
                return c,q,float(curvature.max()),L
            lo=.01;hi=180.
            if evaluate(lo)>remain or evaluate(hi)<remain:continue
            for _ in range(24):
                mid=(lo+hi)/2
                if evaluate(mid)<remain:lo=mid
                else:hi=mid
            c,q,curv,L=evaluate((lo+hi)/2,True)
            if curv>1/30.5 or clear(q).min()<0:continue
            knots=[0.,0.,0.,0.,1.,1.,1.,1.];proof=extrema(knots,c);exact,error=exact_length(knots,c)
            if not proof['regular'] or proof['minimum_radius_mm']<30 or abs(exact-remain)>.05:continue
            return dict(controls_mm=c.tolist(),knots=knots,continuous_curvature=proof,length_mm=exact,quadrature_error_mm=error,
                whole_external_length_mm=exact+node['L']+usb['pi_prefix_length_mm']+entry['extra_length_mm']+usb['bus_prefix_length_mm'])
        return None
    for level in range(begin_level,24 if half else 40):
        if time.monotonic()-tick>95:break
        proposed=[]
        for parent in frontier:
            n=nodes[parent];t=n['t'];ref=np.array([0.,0,1.]) if abs(t[2])<.9 else np.array([0.,1.,0])
            b=np.cross(t,ref);b/=np.linalg.norm(b);c=np.cross(t,b)
            for clock in range(9):
                normal=None if clock==8 else b*math.cos(clock*math.pi/4)+c*math.sin(clock*math.pi/4)
                if normal is None:points=n['p']+step*v[:,None]*t;direction=t
                else:
                    a=angle*v[:,None];points=n['p']+R*np.sin(a)*t+R*(1-np.cos(a))*normal
                    direction=math.cos(angle)*t+math.sin(angle)*normal
                proposed.append((parent,points,direction,normal))
        if not proposed:break
        gaps=clear(np.array([r[1] for r in proposed])).min(axis=1);choices=[];seen=set()
        for row,gap in zip(proposed,gaps):
            if gap<0:continue
            parent,points,t,b=row;p=points[-1];used=level*step;delta=goal-p;dist=np.linalg.norm(delta)
            heading=math.acos(float(np.clip(t@target,-1,1)))
            if used+max(dist,R*heading)>length:continue
            key=tuple(np.r_[np.round(p/4),np.round(t*5)].astype(int))
            if key in seen:continue
            seen.add(key)
            if sidebus:
                approach=goal-target*min(22. if reverse else 30.,dist*.5)
                score=np.linalg.norm(approach-p)+18*(1-np.dot(t,delta/max(dist,1e-6)))+12*heading+rng.uniform(0,18)
            else:score=dist+18*(1-np.dot(t,delta/max(dist,1e-6)))+rng.uniform(0,18)
            if diverse:
                estimated=dist+R*heading
                score=abs((length-used)-estimated)+10*(1-np.dot(t,delta/max(dist,1e-6)))+rng.uniform(0,12)
            choices.append((score,parent,p,t,b))
        choices.sort(key=lambda r:r[0]);frontier=[]
        if diverse:
            selected=[];cells={}
            for row in choices:
                cell=tuple(np.rint(row[2]/8).astype(int));count=cells.get(cell,0)
                if count>=2:continue
                cells[cell]=count+1;selected.append(row)
                if len(selected)>=640:break
        else:selected=choices[:320]
        for _,parent,p,t,b in selected:
            nodes.append(dict(p=p,t=t,L=level*step,parent=parent,arc=None if b is None else b.tolist()));frontier.append(len(nodes)-1)
        result['levels'].append(dict(level=level,nodes=len(frontier),proposals=len(proposed),clear_proposals=int(np.sum(gaps>=0)),
            closest_goal_mm=min((float(np.linalg.norm(nodes[j]['p']-goal)) for j in frontier),default=None),
            best_pose=None if not frontier else dict(point_mm=nodes[frontier[0]]['p'].tolist(),tangent=nodes[frontier[0]]['t'].tolist())))
        if level%3==0 and not half:
            for ix in frontier[::5]:
                end=connect(nodes[ix])
                if end:
                    chain=[];j=ix
                    while nodes[j]['parent'] is not None:
                        node=nodes[j];prev=nodes[node['parent']]
                        chain.append(dict(start_mm=prev['p'].tolist(),start_tangent=prev['t'].tolist(),normal=node['arc'],length_mm=step,R_mm=R))
                        j=node['parent']
                    chain.reverse();result['candidate']=dict(primitives=chain,**{'final_biarc' if biarc else 'final_cubic':end});break
        save();print('USB hard curvature level',level,'frontier',len(frontier),'candidate',bool(result['candidate']),flush=True)
        if result['candidate'] or not frontier:break
    result['status']='HARD_CURVATURE_GLOBAL_PROPOSAL_EXACT_GATES_OPEN' if result['candidate'] else 'BOUNDED_HARD_CURVATURE_GLOBAL_SEARCH_NO_CANDIDATE_NOT_INFEASIBILITY'
    # Preserve positive partial states even when the final connector fails.
    # A next coupling method may reuse this unchanged-geometry tree instead
    # of rerunning every accepted mathematical arc.
    tree=dest.with_suffix('.tree.npz')
    np.savez_compressed(tree,positions_mm=np.array([n['p'] for n in nodes]),tangents=np.array([n['t'] for n in nodes]),
        lengths_mm=np.array([n['L'] for n in nodes]),parents=np.array([-1 if n['parent'] is None else n['parent'] for n in nodes]),
        normals=np.array([[np.nan]*3 if n['arc'] is None else n['arc'] for n in nodes]))
    result.update(tree=tree.relative_to(ROOT).as_posix(),tree_sha256=sha(tree))
    save();print(result['status'],result['worker_seconds'],flush=True)


if __name__=='__main__':
    print('WORKER_PID',os.getpid(),flush=True)
    couple_saved_trees() if '--couple-saved-trees' in sys.argv else receive_roof_fore_stations() if '--roof-fore-stations' in sys.argv else usb_space_sections() if '--usb-space-sections' in sys.argv else curvature_beam_space() if '--hard-curvature-global' in sys.argv else screen_rear_facing_pi() if any(x in sys.argv for x in ('--rear-facing-pi','--inverted-pi','--usb-led-layout','--planned-flat-pi','--underhung-flat-pi')) else main()
