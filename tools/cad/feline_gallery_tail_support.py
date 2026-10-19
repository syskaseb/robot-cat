"""One rooted BUS/tail carrier with independent nominal D/G split clamps.

This replaces an air-gap problem by an explicit mechanical interface. It
does not permit contact with bought parts or waive whole-layout evidence.
Native N03, actual wire OD, tightening and pull tests remain later gates.
"""
import json,math,sys,zipfile,hashlib
import numpy as np
import FreeCAD as A
import Part
from feline_service_gallery import build as gallery_build
from receive_feline_positive_service_deck import pipe,circle_arc,open_grip
from receive_feline_global_case_candidates import placement
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def split_clamp(start,axis):
    t=np.asarray(axis,float);t/=np.linalg.norm(t);u=np.array([0.,0,1]);v=np.cross(t,u)
    tf=placement(np.column_stack([t,u,v]),start)
    def box(lo,hi):
        s=Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo));s.Placement=tf*s.Placement;return s
    groove=Part.makeCylinder(1.7,11,A.Vector(*(np.asarray(start)-t)),A.Vector(*t))
    slot=box([-.15,0,-1.85],[9.15,5.5,1.85])
    body=box([0,-4,-4],[9,4,4]).cut(groove).cut(slot)
    cap=box([0,.2,-1.7],[9,4.2,1.7]).cut(groove)
    band=box([3.25,-5.2,-5.2],[5.75,5.4,5.2]).cut(box([2.25,-4,-4],[6.75,4.2,4]))
    head=box([2,5.4,-2.65],[7,9.7,2.65])
    for n,s in [('body',body),('cap',cap),('band',band),('head',head)]:assert s.isValid() and len(s.Solids)==1,n
    for a,b in [(body,cap),(body,band),(cap,band),(cap,head),(band,head)]:assert a.common(b).Volume<1e-5
    return body,dict(cap=cap,band=band,head=head),slot


def capsule_rail(source,axis_x):
    """Round unused corners about actual bolt axes; retain source holes."""
    b=source.BoundBox;y=b.Center.y;x0,x1=sorted(axis_x);r=3.
    profile=Part.makeBox(x1-x0,2*r,b.ZLength,A.Vector(x0,y-r,b.ZMin))
    for x in (x0,x1):profile=profile.fuse(Part.makeCylinder(r,b.ZLength,A.Vector(x,y,b.ZMin)))
    result=source.common(profile).removeSplitter()
    assert result.isValid() and len(result.Solids)==1
    return result


def keyed_foot(source,obstacle):
    """Open lower foot toward measured component, keep upper rail closed.

    Box is only a conservative construction keepout; exact solids are checked
    afterwards.12mm2 is a provisional bearing-area requirement, not strength.
    """
    b=source.BoundBox;c=b.Center;ymax=max(c.y-1,obstacle.BoundBox.YMax+1.25)
    cut=Part.makeBox(6.2,ymax-(c.y-3.1),b.ZLength+.02,A.Vector(c.x-3.1,c.y-3.1,b.ZMin-.01))
    foot=source.cut(cut).removeSplitter()
    assert foot.isValid() and len(foot.Solids)==1
    contact=sum(f.Area for f in foot.Faces if isinstance(f.Surface,Part.Plane) and abs(f.CenterOfMass.z-b.ZMin)<1e-6)
    assert contact>=12,(contact,c)
    assert foot.distToShape(obstacle)[0]>=1.25-1e-6
    return foot,dict(axis_xy_mm=[c.x,c.y],contact_area_mm2=contact,opening_Ymax_mm=ymax,minimum_contact_area_project_mm2=12)


def build_r2():
    """Edit the exact received single solid, not coincident annular fusions."""
    from plan_feline_long_return import frozen_core
    priorfile=OUT/'n01-tail-supported-gallery-core-received.json';prior=json.loads(priorfile.read_text())
    oldcontrol=prior['source_sha256']['tools/cad/feline_gallery_tail_support.py']
    prior['source_sha256']['tools/cad/feline_gallery_tail_support.py']=sha(ROOT/'tools/cad/feline_gallery_tail_support.py')
    world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,recipe=frozen_core(prior)
    frame=actors[recipe['frame_actor']].copy();old=parts['Ref_Material_tail_TailBridge29_0_0']
    inputs=OUT/'n01-service-gallery-core-received.json';source=json.loads(inputs.read_text());bundle=ROOT/source['bundle'];assert sha(bundle)==source['bundle_sha256']
    originals={}
    with zipfile.ZipFile(bundle) as z:
        for row in source['geometry']:
            if not row['name'].startswith(('CurrentBUS:CarrierRail:','CurrentBUS:BUS_Standoff')):continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());originals[row['name']]=s
    xs=sorted({round(originals[f'CurrentBUS:BUS_Standoff{i}'].BoundBox.Center.x,6) for i in range(4)});assert len(xs)==2
    for n in recipe['BUS_carrier_edge_rails']:
        s=originals[n];rounded=capsule_rail(s,xs);frame=frame.cut(s.cut(rounded))
    proofs=[]
    for i,component_id in ((2,46),(3,94)):
        n=f'CurrentBUS:BUS_Standoff{i}';s=originals[n];obstacle='Ref_Material_BUSsupplier'+str(component_id)+'_0_0'
        keyed,proof=keyed_foot(s,actors[obstacle]);frame=frame.cut(s.cut(keyed));proofs.append(dict(name=n,obstacle=obstacle,**proof))
    for row in recipe['new_BUS_DG_full_ends']:
        end,tip=map(lambda p:np.array(p,float),row['full9_mm']);t=(tip-end)/9
        # Extend only the empty channel, never the retained complete wire.
        channel=Part.makeCylinder(1.7,13,A.Vector(*(end-t)),A.Vector(*t))
        tf=placement(np.column_stack([t,[0,0,1],np.cross(t,[0,0,1])]),end)
        slot=Part.makeBox(13.15,5.5,3.7,A.Vector(-.15,0,-1.85));slot.Placement=tf*slot.Placement
        frame=frame.cut(channel).cut(slot)
    frame=frame.removeSplitter();assert frame.isValid() and len(frame.Solids)==1
    assert frame.cut(actors[recipe['frame_actor']]).Volume<1e-5
    for row in recipe['new_BUS_DG_full_ends']:
        wire=actors[row['name']];assert frame.common(wire).Volume<1e-5
        assert frame.distToShape(wire)[0]>=.149-1e-6
    delta=frame.cut(old);assert delta.isValid() and delta.Solids
    ff=OUT/'n01-supported-BUS-tail-frame-r2.brep';df=OUT/'n01-supported-BUS-tail-frame-r2.delta.brep';assert not ff.exists()
    frame.exportBrep(str(ff));delta.exportBrep(str(df));actors[recipe['frame_actor']]=frame
    recipe.update(frame_file=ff.relative_to(ROOT).as_posix(),frame_delta_file=df.relative_to(ROOT).as_posix(),frame_delta_sha256=sha(df),
        keyed_rear_foot_proofs=proofs,rounded_actual_axis_rails=True,channel_overrun_past_wire_tip_mm=3,
        r2_from_exact_received_frame_sha256=prior['source_sha256'][recipe.get('original_frame_file', 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/n01-supported-BUS-tail-frame.brep')],
        source_constructor_historical_sha256=oldcontrol,old_tail_material_removed_mm3=old.cut(frame).Volume,
        positive_connections_inherited_from_same_connected_single_solid=True)
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (priorfile,inputs,bundle,ff,df)})
    return world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,recipe


def build():
    if '--keyed-feet' in sys.argv:return build_r2()
    r2='--keyed-feet' in sys.argv
    world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,recipe=gallery_build()
    q=np.array(recipe['Pi_mouth_mm']);land=[(q+[6,0,0]).tolist(),(q+[15,0,0]).tolist()]
    for suffix,s in open_grip(land[0],[1,0,0],[0,0,1],7.75).items():actors['USBGrip:Pi:'+suffix]=s
    recipe['Pi_full9_mm']=land;recipe['Pi_USB_band_axis_station_mm']=7.75
    # Only the actual blocked H1 changes, not all five GPIO paths.
    e=next(e for e in recipe['new_Pi_full_ends'] if e['name']=='PiGPIO:PI.H1');q=np.array(e['point_mm']);t=np.array(e['axis']);b=np.array([-.8,.6,0])
    first=q+1.5*t;end=first+10*(t+b);tip=end+9*b
    actors[e['name']],path=pipe([Part.makeLine(A.Vector(*q),A.Vector(*first)),circle_arc(first,t,b,10,math.pi/2),Part.makeLine(A.Vector(*end),A.Vector(*tip))],.7)
    e.update(full9_mm=[end.tolist(),tip.tolist()],length_mm=path.Length,independent_bend=b.tolist())
    diagfile=OUT/'n01-gallery-D-diagonal-received.json';diag=json.loads(diagfile.read_text());df=ROOT/diag['BRep'];assert sha(df)==diag['BRep_sha256']
    assert len(diag['failures'])==1 and diag['failures'][0]['target']=='Ref_Material_tail_TailBridge29_0_0'
    s=Part.Shape();s.read(str(df));actors['CurrentBUS:BUS.D']=s
    # Complete five-part factory output kit, preserving the square case and
    # the whole input branch. No isolated connector movement or lead cut.
    case_name='Station:F_PWM_whole:F_PWM:case';case=parts[case_name]
    pivot=A.Vector(case.BoundBox.Center.x,case.BoundBox.Center.y,case.BoundBox.ZMax);r=A.Rotation(A.Vector(0,0,1),90);tf=A.Placement(pivot-r.multVec(pivot),r)
    c=case.copy();c.Placement=tf*c.Placement;delta=case.cut(c).Volume+c.cut(case).Volume;assert delta<1e-5
    moved=[n for n in parts if meta[n].get('group')=='F_PWM_whole' and (n.endswith(('out_first_bend','out_after_turn_grip')) or ':End1:' in n)];assert len(moved)==5
    for n in moved:
        s=parts[n].copy();s.Placement=tf*s.Placement;actors[n]=s;roles[n]='MovedFPWM';rows[n]=meta[n]
    oldname='Ref_Material_tail_TailBridge29_0_0';old=parts[oldname];assert old.isValid() and len(old.Solids)==1
    anchor=A.Vector(140.231079691734,8.178061652152161,58.89181240855591)
    assert old.isInside(anchor,1e-6,False)
    frame=old.copy();joints=[]
    def join(label,s):
        nonlocal frame
        common=frame.common(s);assert common.isValid() and common.Volume>1e-5,(label,common.Volume)
        joints.append(dict(part=label,positive_union_mm3=common.Volume));frame=frame.fuse(s).removeSplitter()
        assert frame.isValid() and len(frame.Solids)==1,label
    def rod(label,a,b):
        a=A.Vector(*a) if not isinstance(a,A.Vector) else a;b=A.Vector(*b) if not isinstance(b,A.Vector) else b;v=b-a
        join(label,Part.makeCylinder(2,v.Length,a,v));join(label+':round_joint',Part.makeSphere(2,b))
    railnames=recipe['BUS_carrier_edge_rails'];ra=[actors[n] for n in railnames]
    standnames=[f'CurrentBUS:BUS_Standoff{i}' for i in range(4)]
    if r2:
        xs=sorted({round(actors[n].BoundBox.Center.x,6) for n in standnames});assert len(xs)==2
        ra=[capsule_rail(s,xs) for s in ra]
    front,rear=recipe['BUS_carrier_rail_centre_Y_mm'];z=(ra[0].BoundBox.ZMin+ra[0].BoundBox.ZMax)/2;edge=ra[0].BoundBox.XMax-.5
    root=[145.5,13.5,61.5];post=[145.5,13.5,z]
    join('actual_old_bridge_anchor',Part.makeSphere(2.5,anchor));rod('root',anchor,root);rod('front_post',root,post)
    rod('front_elbow',post,[145.5,front,z]);rod('front_rail_arm',[145.5,front,z],[edge,front,z]);join('four_axis_front_rail',ra[0])
    rod('low_side_crossbar',[145.5,13.5,88.75],[145.5,rear,88.75]);rod('rear_post',[145.5,rear,88.75],[145.5,rear,z])
    rod('rear_rail_arm',[145.5,rear,z],[edge,rear,z]);join('four_axis_rear_rail',ra[1])
    # Integrate the four EXISTING printed bosses into the carrier. A0.25mm
    # annular overlap is wholly inside the existing rail/boss material and
    # preserves their external dimensions and original through-holes.
    foot_proofs=[];foot_cuts=[]
    for n in standnames:
        s=actors[n];b=s.BoundBox;c=b.Center;a=A.Vector(c.x,c.y,b.ZMax-.01)
        if r2 and n.endswith(('2','3')):
            component='Ref_Material_BUSsupplier'+('46' if n.endswith('2') else '94')+'_0_0'
            keyed,proof=keyed_foot(s,actors[component]);foot_cuts.append(s.cut(keyed));foot_proofs.append(dict(name=n,obstacle=component,**proof))
        overlap=Part.makeCylinder(3,.26,a).cut(Part.makeCylinder(1.2,.28,a-A.Vector(0,0,.01)))
        join(n+':annular_union',overlap);join(n,s)
    channels=[];slots=[];bands=[];newends=[];mate_names=[]
    for tag,bend in [('D',np.array([-math.sqrt(.5),-math.sqrt(.5),0.])),('G',np.array([0.,1,0]))]:
        name='CurrentBUS:BUS.'+tag;wire=actors[name]
        caps=[f for f in wire.Faces if isinstance(f.Surface,Part.Plane) and abs(f.Area-math.pi*1.55**2)<1e-4];assert len(caps)==2
        q=np.array(list(max(caps,key=lambda f:f.CenterOfMass.z).CenterOfMass));t=np.array([0.,0,-1]);end=q+10*(t+bend);tip=end+9*bend
        land=Part.makeCylinder(1.55,9,A.Vector(*end),A.Vector(*bend));assert land.cut(wire).Volume<1e-5
        body,kit,slot=split_clamp(end,bend)
        if r2:
            tf=placement(np.column_stack([bend,np.array([0.,0,1]),np.cross(bend,[0,0,1])]),end)
            slot=Part.makeBox(13.15,5.5,3.7,A.Vector(-.15,0,-1.85));slot.Placement=tf*slot.Placement
        slots.append(slot)
        p=end+7.75*bend;target=[p[0],p[1],58.]
        if tag=='D':rod('D_saddle_arm',anchor,target)
        else:
            rod('G_side_arm',root,[145.5,p[1],58.]);rod('G_saddle_arm',[145.5,p[1],58.],target)
        join(tag+'_full9_saddle',body)
        through_tip=tip+(3*bend if r2 else 0)
        groove,_=pipe([circle_arc(q,t,bend,10,math.pi/2),Part.makeLine(A.Vector(*end),A.Vector(*through_tip))],1.7);channels.append(groove)
        for suffix,s in kit.items():
            n='DGGrip:'+tag+':'+suffix;actors[n]=s;roles[n]='Grip:'+tag;rows[n]={'kind':'proposal_material'};mate_names.append(n)
        bands.append(kit['band']);newends.append(dict(name=name,point_mm=q.tolist(),full9_mm=[end.tolist(),tip.tolist()],R_mm=10))
    for s in [*foot_cuts,*channels,*slots,*bands]:frame=frame.cut(s).removeSplitter()
    assert frame.isValid() and len(frame.Solids)==1
    # Re-open ALL old through-holes without introducing any new hole. No
    # groove may cut the structural2mm annulus of an old mounting hole.
    removed=old.cut(frame);hole_guards=[];seen=set();bb=old.BoundBox
    for f in old.Faces:
        if not isinstance(f.Surface,Part.Cylinder):continue
        c=f.Surface
        if abs(c.Axis.z)<.99 or not 1<=c.Radius<=3.2:continue
        key=tuple(round(v,5) for v in (c.Center.x,c.Center.y,c.Radius))
        if key in seen:continue
        seen.add(key);a=A.Vector(c.Center.x,c.Center.y,bb.ZMin-1)
        drill=Part.makeCylinder(c.Radius,100,a)
        if old.common(drill).Volume>1e-5:continue
        ring=Part.makeCylinder(c.Radius+2,bb.ZLength+2,a).cut(Part.makeCylinder(c.Radius,bb.ZLength+2,a))
        removal=removed.common(ring).Volume;assert removal<1e-5,('Old mounting seat affected',key,removal)
        frame=frame.cut(drill);hole_guards.append(dict(axis_xy_radius_mm=key,removed_in_2mm_annulus_mm3=removal))
    frame=frame.removeSplitter();assert frame.isValid() and len(frame.Solids)==1
    for tag in ('D','G'):
        assert frame.common(actors['CurrentBUS:BUS.'+tag]).Volume<1e-5
        for suffix in ('cap','band','head'):assert frame.common(actors['DGGrip:'+tag+':'+suffix]).Volume<1e-5,(tag,suffix)
    delta=frame.cut(old);assert delta.isValid() and delta.Solids
    stem='n01-supported-BUS-tail-frame-r2' if r2 else 'n01-supported-BUS-tail-frame'
    deltafile=OUT/(stem+'.delta.brep');framefile=OUT/(stem+'.brep')
    assert not r2 or not framefile.exists(),'Preserve frozen R2 geometry; resume archive instead'
    delta.exportBrep(str(deltafile));frame.exportBrep(str(framefile))
    for n in [*railnames,*standnames]:actors.pop(n);roles.pop(n);rows.pop(n)
    n='SharedBUS:TailCarrier';actors[n]=frame;roles[n]='FrameNew';rows[n]={'kind':'proposal_material'}
    recipe.update(new_BUS_DG_full_ends=newends,frame_actor=n,frame_delta_file=deltafile.relative_to(ROOT).as_posix(),frame_delta_sha256=sha(deltafile),
        frame_file=framefile.relative_to(ROOT).as_posix(),frame_positive_joints=joints,old_tail_hole_seats=hole_guards,
        old_tail_material_removed_mm3=removed.Volume,independent_DG_split_clamps=True,nominal_DG_channel_radius_mm=1.7,jacket_radius_mm=1.55,
        clamp_min_wall_mm=2.15,actual_OD_tightening_pull_and_old_tail_strength_not_physically_qualified=True,
        fixed_replaced_names=[oldname,*moved],FPWM_case_name=case_name,FPWM_moved_whole_output_names=moved,FPWM_case_symmetry_difference_mm3=0.,
        four_printed_boss_axes_and_heights_preserved=standnames,keyed_rear_foot_proofs=foot_proofs,
        rounded_actual_axis_rails=r2,channel_overrun_past_wire_tip_mm=3 if r2 else 0,
        FPWM_rotation_axis_Z_deg=90,FPWM_pivot_mm=list(pivot),seven_Pi_full_grips_roots_tools_capacity_OPEN=True)
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'tools/cad/feline_gallery_tail_support.py',diagfile,df,deltafile,framefile)})
    return world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,recipe
