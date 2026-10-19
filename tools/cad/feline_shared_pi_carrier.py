"""One shared Pi/USB/seven-wire restraint and rooted carrier proposal.

No new pose catalogue, final cuts, native detail or physical retention claim.
The top U leaves microSD clear; existing M2 hardware is stacked on real axes.
"""
import json,math,zipfile,hashlib,sys
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
    r3='--Pi-carrier-r3' in sys.argv;r2=r3 or '--Pi-carrier-r2' in sys.argv
    pf=OUT/('n01-shared-Pi-carrier-r2-core-received.json' if r3 else 'n01-shared-Pi-carrier-core-received.json' if r2 else 'n01-tail-supported-gallery-r2-canonical-core-received.json');parent=json.loads(pf.read_text())
    wf=OUT/'n01-tail-supported-gallery-r2-canonical-world-received.json';external=json.loads(wf.read_text())
    assert not external['failures'] and not external['errors'] and external['critical_phase_complete']
    historical_constructor=parent['source_sha256'].get('tools/cad/feline_shared_pi_carrier.py')
    if r2:parent['source_sha256']['tools/cad/feline_shared_pi_carrier.py']=sha(ROOT/'tools/cad/feline_shared_pi_carrier.py')
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
        if r2:continue  # ALL received wires/fasteners remain exact parent actors.
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
        if r2:
            if 'Screw' in n:axes.append([centre.x,centre.y])
            continue
        if 'Nut' in n:
            rot=A.Rotation(A.Vector(0,0,1),30);s.Placement=A.Placement(centre-rot.multVec(centre),rot)*s.Placement
            s.translate(A.Vector(0,0,101.6-s.BoundBox.ZMin))
        else:s.translate(A.Vector(0,0,1.6 if centre.y>0 else .6))
        actors[n]=s;roles[n]='PiHWNew';changed.append(n)
        if 'Screw' in n:axes.append([centre.x,centre.y])
    assert len(axes)==4
    rootname='CurrentFoundation:RetainedPWMCarrier';oldroot=parts[rootname];assert oldroot.isValid() and len(oldroot.Solids)==1
    tool_proofs=[];rootplan_file=None
    if r3:
        from plan_feline_pi_root_access import root_arm
        rootplan_file=OUT/'n01-Pi-root-access-plan.json';rp=json.loads(rootplan_file.read_text())
        assert rp['status']=='WHOLE_PI_ROOT_ACCESS_PLAN_RECEIVED' and rp['source_sha256'][pf.relative_to(ROOT).as_posix()]==sha(pf)
        for name,value in rp['source_sha256'].items():
            if name in ('tools/cad/feline_shared_pi_carrier.py','tools/cad/plan_feline_long_return.py','tools/cad/plan_feline_usb_service_bight.py'):continue
            assert sha(ROOT/name)==value,name
        choices=[rp['accepted']];assert oldroot.isInside(A.Vector(*choices[0]['point_mm']),1e-7,False)
        b=actors['PiBudget:UnlabelledTopComponentsBudget'].BoundBox
        ko=Part.makeBox(b.XLength+2.5,b.YLength+2.5,104.8-b.ZMin+1.25,A.Vector(b.XMin-1.25,b.YMin-1.25,b.ZMin-1.25))
        arm=root_arm(choices[0]['point_mm'],choices[0]['stem_mm'],ko)
        for name,s in parts.items():
            if not name.startswith('Ref_Material_PWM9685') or 'Screw' not in name:continue
            faces=[f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Axis.z)>.99]
            head=max(faces,key=lambda f:f.Surface.Radius);b=head.BoundBox;low=b.Center.z<s.BoundBox.Center.z
            entry=A.Vector(b.Center.x,b.Center.y,b.ZMin if low else b.ZMax)
            tool=Part.makeCylinder(2.5,25,entry,A.Vector(0,0,-1 if low else 1));gap=arm.distToShape(tool)[0]
            assert gap>=1.25-1e-6,(name,gap)
            tool_proofs.append(dict(source_screw=name,entry_mm=list(entry),axis=[0,0,-1 if low else 1],radius_mm=2.5,length_mm=25,
                new_root_clearance_mm=gap,scope='Added root only; existing native access remains inherited, not physical PASS',project_tool_budget_not_supplier_drawing=True))
        assert len(tool_proofs)==4,len(tool_proofs)
    else:choices=face_entries(oldroot,[-6,-6,105.6],1)
    assert choices
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
    if r2:
        entry=np.array(h1['full9_mm'][1])+.75*t1
        end4=np.mean([np.array(e['full9_mm'][0]) for e in four],axis=0)+9.75*t
        rod('outside_PCB_column',stem,[-6,stem[1],87.3])
        rod('H1_after_strap_entry',[-6,stem[1],87.3],[entry[0],entry[1],87.3])
        rod('H1_after_strap_post',[entry[0],entry[1],87.3],[entry[0],entry[1],77.55])
        rod('GPIO_above_whole_head',[-6,stem[1],87.3],[end4[0],end4[1],87.3])
        rod('GPIO_after_strap_post',[end4[0],end4[1],87.3],[end4[0],end4[1],77.55])
    else:
        rod('H1_upright',stem,[-6,stem[1],79.7])
        rod('GPIO_bridge',[-6,stem[1],79.7],[24,-3,79.7])
    ux=118.5 if r2 else 120
    rod('upper_USB_beam',[59.5,29,107.1],[ux,28.8581096347,107.1])
    rod('USB_pad_post',[ux,28.8581096347,107.1],[ux,28.8581096347,102.9])
    if r2:
        originfile=OUT/'n01-tail-supported-gallery-r2-canonical-core-received.json';orig=json.loads(originfile.read_text());arc=ROOT/orig['bundle'];assert sha(arc)==orig['bundle_sha256']
        rec=next(r for r in orig['geometry'] if r['name']=='USBGrip:Pi:pad')
        with zipfile.ZipFile(arc) as z:raw=z.read(rec['entry'])
        assert hashlib.sha256(raw).hexdigest()==rec['sha256'];usbpad=Part.Shape();usbpad.importBrepFromString(raw.decode())
    else:
        usbpad=actors.pop('USBGrip:Pi:pad');roles.pop('USBGrip:Pi:pad');rows.pop('USBGrip:Pi:pad')
    join('existing_USB_Pi_pad',usbpad)
    py=72.2681096347 if r2 else 67.0181096347
    rod('upper_power_beam',[91,29,106.38],[110.65,py,107.1])
    rod('power_pad_post',[110.65,py,107.1],[110.65,py,105.6])
    for name,lands,r in groups:
        pad,kit,proof=saddle(lands,r);join(name+':full9_pad',pad);kits.append(dict(name=name,wire_names=[e['name'] for e in four] if name=='GPIO4' else [h1['name']] if name=='H1' else [e['name'] for e in power],**proof))
        for suffix,s in kit.items():
            n='PiGrip:'+name+':'+suffix
            if r2:assert n in actors;continue
            actors[n]=s;roles[n]='PiGrip:'+name;rows[n]=dict(kind='tie_reservation')
    if r2:
        # One coherent tool/PCB keepout, NOT serial corner micro-offsets.
        b=actors['PiBudget:UnlabelledTopComponentsBudget'].BoundBox
        keepout=Part.makeBox(b.XLength+2.5,b.YLength+2.5,104.8-(b.ZMin-1.25),A.Vector(b.XMin-1.25,b.YMin-1.25,b.ZMin-1.25))
        frame=frame.cut(keepout)
        for e in [*four,h1]:
            q=np.array(e['point_mm']);d=np.array(e['axis']);b=np.array(e.get('independent_bend',[math.sqrt(.5),math.sqrt(.5),0]))
            first=q+1.5*d;arcend=first+10*(d+b);tip=np.array(e['full9_mm'][1])+3*b
            clearance,_=pipe([Part.makeLine(A.Vector(*q),A.Vector(*first)),circle_arc(first,d,b,10,math.pi/2),Part.makeLine(A.Vector(*arcend),A.Vector(*tip))],.85)
            frame=frame.cut(clearance)
        for n,s in actors.items():
            if n.startswith(('PiGrip:','USBGrip:Pi:')):frame=frame.cut(s)
            if n.startswith('Ref_Material_Pi4') and 'Screw' in n:
                b=s.BoundBox;c=b.Center;head_bottom=b.ZMax-2
                frame=frame.cut(Part.makeCylinder(2.5,30,A.Vector(c.x,c.y,head_bottom)))
    for x,y0 in axes:frame=frame.cut(Part.makeCylinder(1.2,15,A.Vector(x,y0,100)))
    frame=frame.removeSplitter();assert frame.isValid() and len(frame.Solids)==1
    stemfile='n01-shared-Pi-carrier-r3' if r3 else 'n01-shared-Pi-carrier-r2' if r2 else 'n01-shared-Pi-carrier'
    ff=OUT/(stemfile+'.brep');df=OUT/(stemfile+'.delta.brep');assert not ff.exists()
    delta=frame.cut(oldroot);assert delta.isValid() and delta.Solids;frame.exportBrep(str(ff));delta.exportBrep(str(df))
    n='SharedPi:Carrier';actors[n]=frame;roles[n]='PiFrameNew';rows[n]=dict(kind='proposal_material')
    recipe=dict(recipe,new_Pi_full_ends=list(ends.values()),Pi_top_actual_axes_mm=axes,Pi_frame_actor=n,Pi_frame_file=ff.relative_to(ROOT).as_posix(),Pi_frame_delta_file=df.relative_to(ROOT).as_posix(),Pi_frame_delta_sha256=sha(df),
        Pi_positive_joints=joins,Pi_full_grip_kits=kits,Pi_actual_root=dict(owner=rootname,**choices[0]),
        Pi_changed_actors=changed,Pi_unchanged_parent_actor_names=[r['name'] for r in parent['geometry'] if r['name'] not in changed and r['name']!='USBGrip:Pi:pad'],
        immutable_parent_core_file=pf.relative_to(ROOT).as_posix(),fixed_replaced_names=list(dict.fromkeys(recipe['fixed_replaced_names']+[rootname])),
        project_mount_keepouts_not_supplier_guarantees=True,individual_jacket_pull_print_fit_and_thermal_phase2=True)
    if r2:
        recipe.update(Pi_changed_actors=[n],Pi_unchanged_parent_actor_names=[r['name'] for r in parent['geometry'] if r['name']!=n],
            parent_constructor_historical_sha256=historical_constructor,whole_strap_heads_outside_support_paths=True,actual_M2_head_driver_channels_R_mm=2.5)
    if r3:
        alias='ShelfPWM:carrier';difference=oldroot.cut(parts[alias]).Volume+parts[alias].cut(oldroot).Volume;assert difference<1e-5
        recipe.update(Pi_root_plan_file=rootplan_file.relative_to(ROOT).as_posix(),Pi_root_tool_clearance_proofs=tool_proofs,
            Pi_printed_alias=alias,Pi_printed_alias_symmetric_difference_mm3=difference,
            fixed_replaced_names=list(dict.fromkeys(recipe['fixed_replaced_names']+[alias])),
            world_receipts_for_unchanged_actors=['n01-tail-supported-gallery-r2-canonical-world-received.json','n01-shared-Pi-carrier-r2-world-received.json'])
        pins[rootplan_file.relative_to(ROOT).as_posix()]=sha(rootplan_file)
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (pf,wf,ff,df,ROOT/'tools/cad/feline_shared_pi_carrier.py')})
    return world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,recipe
