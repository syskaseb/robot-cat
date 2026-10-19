"""One shared Pi/USB/seven-wire restraint and rooted carrier proposal.

No new pose catalogue, final cuts, native detail or physical retention claim.
The top U leaves microSD clear; existing M2 hardware is stacked on real axes.
"""
import json,math,zipfile,hashlib
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_positive_service_deck import pipe,circle_arc
from receive_feline_global_case_candidates import placement
from feline_common_retention_roots import face_entries


def saddle(rows,radius):
    """One open-bottom common grooved pad with full selected T18I envelope."""
    starts=np.array([r[0] for r in rows]);t=np.array(rows[0][1],float);t/=np.linalg.norm(t)
    u=np.array([-t[1],t[0],0.]);z=np.array([0.,0,1]);origin=starts[0]
    s=(starts-origin)@t;assert max(s)-min(s)<1e-6
    across=(starts-origin)@u;lo=min(across)-radius-1.7;hi=max(across)+radius+1.7
    # The2mm continuous roof carries load; narrow ribs between grooves do not.
    lower=.15;top=radius+.15+2;tf=placement(np.column_stack([t,u,z]),origin)
    def box(a,b):
        q=Part.makeBox(*(np.array(b)-a),A.Vector(*a));q.Placement=tf*q.Placement;return q
    pad=box([0,lo,lower],[9,hi,top])
    for q in starts:pad=pad.cut(Part.makeCylinder(radius+.15,15,A.Vector(*(q-3*t)),A.Vector(*t)))
    outer=box([3.25,lo-1.2,-radius-.15-1.2],[5.75,hi+1.2,top+1.2])
    inner=box([3.15,lo,-radius-.15],[5.85,hi,top])
    band=outer.cut(inner)
    # Full5axial x4.3cross x5.3height head, above the pad not between wires.
    head=box([2,(lo+hi)/2-2.65,top+1.2],[7,(lo+hi)/2+2.65,top+5.5]) if radius<1 else box([2,hi+1.2,-2.65],[7,hi+5.5,2.65])
    assert pad.isValid() and len(pad.Solids)==1 and band.isValid() and band.Solids
    assert abs(head.Volume-5*4.3*5.3)<1e-5
    return pad,dict(band=band,head=head),dict(axis=t.tolist(),start_mm=origin.tolist(),roof_wall_mm=2.,width_mm=hi-lo,
        per_wire_full9_mm=[[q.tolist(),(q+9*t).tolist()] for q in starts],nominal_channel_clearance_mm=.15,
        actual_OD_individual_pull_and_tightening_phase2_gate=True)


def build():
    from plan_feline_long_return import frozen_core
    pf=OUT/'n01-tail-supported-gallery-r2-canonical-core-received.json';parent=json.loads(pf.read_text())
    wf=OUT/'n01-tail-supported-gallery-r2-canonical-world-received.json';external=json.loads(wf.read_text())
    assert not external['failures'] and not external['errors'] and external['critical_phase_complete']
    world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,recipe=frozen_core(parent)
    baseline={n:s.copy() for n,s in actors.items() if n.startswith(('PiGPIO:','PiPower:'))}
    changed=[];newends=[]
    ends={r['name']:dict(r) for r in recipe['new_Pi_full_ends']}
    four=[ends['PiGPIO:'+tag] for tag in ('PI.H3','PI.H5','PI.H6','PI.H11')]
    t=np.array([math.sqrt(.5),math.sqrt(.5),0]);origin=np.array(four[0]['full9_mm'][0])
    station=max((np.array(e['full9_mm'][0])-origin)@t for e in four)
    for e in four:
        old=np.array(e['full9_mm'][0]);start=old+(station-(old-origin)@t)*t;tip=start+9*t
        q=np.array(e['point_mm']);d=np.array(e['axis']);first=q+1.5*d
        actors[e['name']],path=pipe([Part.makeLine(A.Vector(*q),A.Vector(*first)),circle_arc(first,d,t,10,math.pi/2),Part.makeLine(A.Vector(*old),A.Vector(*tip))],.7)
        # first arc terminates at the old straight start, exactly.
        e.update(full9_mm=[start.tolist(),tip.tolist()],length_mm=path.Length,common_comb_straight_extension_only=True)
        changed.append(e['name']);ends[e['name']]=e
    # W080 already contains the same9mm straight as W079. Move grip station,
    # NOT purchased lead, bend, wire length or connector.
    power=[]
    y=ends['PiPower:W079']['full9_mm'][0][1]
    for tag in ('W079','W080'):
        e=ends['PiPower:'+tag];q=np.array(e['full9_mm'][0]);q[1]=y
        e.update(full9_mm=[q.tolist(),(q+[0,9,0]).tolist()],common_existing_power_straight=True);power.append(e)
    # Match the same selected fasteners to the new measured board/bar stack.
    axes=[]
    for n in list(actors):
        if not n.startswith('Ref_Material_Pi4') or 'NominalPCB' in n:continue
        s=actors[n].copy();b=s.BoundBox;centre=b.Center
        if 'Nut' in n:
            rot=A.Rotation(A.Vector(0,0,1),30);s.Placement=A.Placement(centre-rot.multVec(centre),rot)*s.Placement
            s.translate(A.Vector(0,0,101.6-s.BoundBox.ZMin))
        else:s.translate(A.Vector(0,0,1.6 if centre.y>0 else .6))
        actors[n]=s;roles[n]='PiHWNew';changed.append(n)
        if 'Screw' in n:axes.append([centre.x,centre.y])
    assert len(axes)==4
    rootname='CurrentFoundation:RetainedPWMCarrier';oldroot=parts[rootname];assert oldroot.isValid() and len(oldroot.Solids)==1
    choices=face_entries(oldroot,[-6,-6,105.6],1);assert choices
    anchor=np.array(choices[0]['point_mm']);frame=oldroot.copy();joins=[]
    def join(n,s):
        nonlocal frame
        c=frame.common(s);assert c.isValid() and c.Volume>1e-5,(n,c.Volume)
        frame=frame.fuse(s).removeSplitter();assert frame.isValid() and len(frame.Solids)==1,n
        joins.append(dict(name=n,common_mm3=c.Volume))
    def rod(n,a,b,r=1.5):
        a=np.array(a);b=np.array(b);v=b-a
        join(n,Part.makeCylinder(r,float(np.linalg.norm(v)),A.Vector(*a),A.Vector(*v)))
        join(n+':round',Part.makeSphere(r,A.Vector(*b)))
    join('actual_PWM_root',Part.makeSphere(2,A.Vector(*anchor)))
    stem=np.array([-6.,-5.984390365286,105.6]);rod('common_root',anchor,stem)
    fore=min(y for x,y in axes);rear=max(y for x,y in axes)
    rod('fore_left_entry',stem,[-.5,fore,105.6])
    # Flat top U, closed actual throughholes; no left bar across microSD.
    def bar(a,b,width=4,height=1.6):
        a=np.array(a);b=np.array(b);v=b-a;t=v/np.linalg.norm(v);u=np.array([-t[1],t[0],0]);tf=placement(np.column_stack([t,u,[0,0,1]]),a)
        s=Part.makeBox(float(np.linalg.norm(v)),width,height,A.Vector(0,-width/2,0));s.Placement=tf*s.Placement;return s
    join('top_fore_rail',bar([-.5,fore,104.8],[57.5,fore,104.8]))
    join('right_U_rail',bar([57.5,fore,104.8],[57.5,rear,104.8]))
    join('top_rear_rail',bar([-.5,rear,104.8],[57.5,rear,104.8]))
    for x,y0 in axes:join('actual_M2_pad',Part.makeCylinder(3.5,1.6,A.Vector(x,y0,104.8)))
    h1=ends['PiGPIO:PI.H1'];t1=np.array(h1['full9_mm'][1])-h1['full9_mm'][0];t1/=9
    groups=[('GPIO4',[(e['full9_mm'][0],t) for e in four],.7),('H1',[(h1['full9_mm'][0],t1)],.7),('Power2',[(e['full9_mm'][0],[0,1,0]) for e in power],1.55)]
    kits=[]
    # Carrier branches are allocated together above all source-bank lands.
    rod('H1_upright',stem,[-6,stem[1],79.7])
    rod('GPIO_bridge',[-6,stem[1],79.7],[24,-3,79.7])
    rod('upper_USB_beam',[59.5,29,107.1],[120,28.8581096347,107.1])
    rod('USB_pad_post',[120,28.8581096347,107.1],[120,28.8581096347,102.9])
    join('existing_USB_Pi_pad',actors['USBGrip:Pi:pad']);actors.pop('USBGrip:Pi:pad');roles.pop('USBGrip:Pi:pad');rows.pop('USBGrip:Pi:pad')
    rod('upper_power_beam',[91,29,106.38],[110.65,67.0181096347,107.1])
    rod('power_pad_post',[110.65,67.0181096347,107.1],[110.65,67.0181096347,105.6])
    for name,lands,r in groups:
        pad,kit,proof=saddle(lands,r);join(name+':full9_pad',pad);kits.append(dict(name=name,wire_names=[e['name'] for e in four] if name=='GPIO4' else [h1['name']] if name=='H1' else [e['name'] for e in power],**proof))
        for suffix,s in kit.items():
            n='PiGrip:'+name+':'+suffix;actors[n]=s;roles[n]='PiGrip:'+name;rows[n]=dict(kind='tie_reservation')
    for x,y0 in axes:frame=frame.cut(Part.makeCylinder(1.2,15,A.Vector(x,y0,100)))
    frame=frame.removeSplitter();assert frame.isValid() and len(frame.Solids)==1
    ff=OUT/'n01-shared-Pi-carrier.brep';df=OUT/'n01-shared-Pi-carrier.delta.brep';assert not ff.exists()
    delta=frame.cut(oldroot);assert delta.isValid() and delta.Solids;frame.exportBrep(str(ff));delta.exportBrep(str(df))
    n='SharedPi:Carrier';actors[n]=frame;roles[n]='PiFrameNew';rows[n]=dict(kind='proposal_material')
    recipe=dict(recipe,new_Pi_full_ends=list(ends.values()),Pi_top_actual_axes_mm=axes,Pi_frame_actor=n,Pi_frame_file=ff.relative_to(ROOT).as_posix(),Pi_frame_delta_file=df.relative_to(ROOT).as_posix(),Pi_frame_delta_sha256=sha(df),
        Pi_positive_joints=joins,Pi_full_grip_kits=kits,Pi_actual_root=dict(owner=rootname,**choices[0]),
        Pi_changed_actors=changed,Pi_unchanged_parent_actor_names=[r['name'] for r in parent['geometry'] if r['name'] not in changed and r['name']!='USBGrip:Pi:pad'],
        immutable_parent_core_file=pf.relative_to(ROOT).as_posix(),fixed_replaced_names=recipe['fixed_replaced_names']+[rootname],
        project_mount_keepouts_not_supplier_guarantees=True,individual_jacket_pull_print_fit_and_thermal_phase2=True)
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (pf,wf,ff,df,ROOT/'tools/cad/feline_shared_pi_carrier.py')})
    return world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,recipe
