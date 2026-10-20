"""Both occupied Micro-Fit sides; module pair turns BEFORE its full9 grip.

The fixed ATO tool keeps1.25mm. All four selected225+/-5mm parts remain;
these source prefixes are NOT a claim that their whole middles fit.
"""
import math,json
import numpy as np
import FreeCAD as A
import Part
from plan_feline_n01_shared import pipe
from plan_feline_u1_common_restraints import open_seat
from receive_feline_global_case_candidates import placement
from feline_source_restraint_plan import box
from plan_feline_layout import BASE


def factory_gate(ends):
    """Necessary whole-piece check BEFORE source-grip CAD; preserve None pads.

    Routing exits are used, not invented electrical pins. Ignoring prefix,
    insertion and bend debits only weakens this lower bound: a failure even
    against the longest230mm part rejects that nominal placement outright.
    A positive result is NOT a route or shared-space qualification.
    """
    selection=json.loads((BASE/'pwm-branch-checkpoint/selection.json').read_text())
    assert selection['selected'] and all('225+/-5mm' in s for s in selection['factory_leads'].values())
    rows=[]
    for r in (e for e in ends if e.get('group')=='JPWM'):
        others=[e for e in ends if e['portion_id']==r['portion_id'] and e['id']!=r['id']]
        assert len(others)==1,'Need BOTH ends of each physical prefitted225mm lead before any CAD'
        other=others[0];a=r['routing_exit_mm'];b=other['routing_exit_mm']
        assert a is not None and b is not None,'Do not substitute unknown electrical pads'
        d=math.dist(a,b)
        rows.append(dict(wire=r['wire'],straight_boundary_lower_bound_mm=d,
            factory_min_mm=220.,factory_max_mm=230.,hard_hold=d>230.+1e-6))
    assert len(rows)==4
    return dict(pieces=rows,hard_holds=[r for r in rows if r['hard_hold']],
        necessary_bound_only_NOT_route_approval=True,N01_complete=False)


def construct(ends,post_turn=False,enforce_factory=True):
    if enforce_factory:
        gate=factory_gate(ends)
        if gate['hard_holds']:raise ValueError('Relocate whole JPWM before grip CAD: '+str(gate['hard_holds']))
    ends=[r for r in ends if r.get('group')=='JPWM'];assert len(ends)==4
    from feline_selected_piece_contract import load
    contract,_=load();R=max(contract['portions'][r['portion_id']]['minimum_project_R_mm'] for r in ends)
    assert R>=11.1
    actors={};metadata={};lands={};theta=9/R
    def add(n,s,kind,**kw):
        assert s.isValid() and len(s.Solids)==1,n
        actors[n]=s;metadata[n]=dict(kind=kind,**kw)
    def arc(p,phi):return p+np.array([R*math.sin(phi),R*(1-math.cos(phi)),0])
    for r in ends:
        selected=contract['portions'][r['portion_id']];assert selected['project_radius_mm']==.925
        p=np.array(r['point_mm']);d=np.array(r['departure_axis']);d/=np.linalg.norm(d)
        if r['physical_side']=='source':
            e=p+9*d;parts=[dict(kind='line',start=p.tolist(),end=e.tolist())];used=9.
        else:
            assert np.allclose(d,[1,0,0]);a=p+3*d;e=arc(a,theta)
            parts=[dict(kind='line',start=p.tolist(),end=a.tolist()),
                dict(kind='arc',start=a.tolist(),mid=arc(a,theta/2).tolist(),end=e.tolist(),radius_mm=R)];used=12.
            if post_turn:
                a=p+3*d;b=arc(a,math.pi/2);e=b+[0,9,0]
                parts=[dict(kind='line',start=p.tolist(),end=a.tolist()),
                    dict(kind='arc',start=a.tolist(),mid=arc(a,math.pi/4).tolist(),end=b.tolist(),radius_mm=R),
                    dict(kind='line',start=b.tolist(),end=e.tolist())];used=3+R*math.pi/2+9
        n='JPWMSource:'+r['wire'];add(n,pipe(parts,.925),'wire',wire=r['wire'])
        lands[r['id']]=dict(wire=r['wire'],selected_sku=selected['selected_sku'],parts=parts,
            prefix_used_mm=used,full_grip_arclength_mm=[0.,9.] if used==9 else [used-9,used],
            factory_whole_nominal_mm=225.,factory_whole_min_mm=220.,factory_middle_NOT_received=True,
            routing_exit_mm=e.tolist(),source_mouth_mm=p.tolist(),R_mm=R,extra_mandatory9_after_arc=False)
    for side in ('source','module'):
        rs=[r for r in ends if r['physical_side']==side];p=np.mean([r['point_mm'] for r in rs],axis=0)
        if side=='source':kit=open_seat(p.tolist(),rs[0]['departure_axis'],[0,1,0],1.075,2.575)
        elif post_turn:
            a=arc(p+[3,0,0],math.pi/2)
            kit=open_seat(a.tolist(),[0,1,0],[1,0,0],1.075,2.575)
        else:
            p=p+[3,0,0];cap=1.075;h=2.575
            def at(s):
                phi=s/R;return arc(p,phi),np.array([math.cos(phi),math.sin(phi),0]),np.array([-math.sin(phi),math.cos(phi),0])
            def swept(a,b,y0,y1,z0,z1):
                q,t,u=at(a);v=np.cross(t,u)
                cs=[A.Vector(*(q+u*y+v*z)) for y,z in ((y0,z0),(y1,z0),(y1,z1),(y0,z1),(y0,z0))]
                edge=Part.Arc(A.Vector(*at(a)[0]),A.Vector(*at((a+b)/2)[0]),A.Vector(*at(b)[0])).toShape()
                return Part.Wire([edge]).makePipeShell([Part.Wire(Part.makePolygon(cs).Edges)],True,False)
            pad=swept(0,9,cap,cap+2,-h,h)
            band=swept(3.25,5.75,-cap-1.2,cap+3.2,-h-1.2,h+1.2).cut(swept(3.15,5.85,-cap,cap+2,-h,h))
            q,t,u=at(4.5);frame=placement(np.column_stack((t,u,np.cross(t,u))),q.tolist())
            # Quarter-clock the same complete5x4.3x5.3 head to the top,
            # not into the fixed ATO tool or the north Pi carrier.
            head=box([-2.5,-1.65,h+1.2],[2.5,3.65,h+5.5]);head.Placement=frame*head.Placement
            assert abs(head.Volume-5*4.3*5.3)<1e-5
            kit=dict(pad=pad,band=band,head=head)
        assert kit['pad'].copy().common(kit['band'].copy()).Volume<1e-5,side
        nylon=kit['band'].fuse(kit['head']);assert nylon.isValid() and len(nylon.Solids)==1,side
        for k,s in kit.items():add('JPWMGrip:'+side+':'+k,s,'PETG' if k=='pad' else 'T18I',side=side)
    return actors,metadata,lands
