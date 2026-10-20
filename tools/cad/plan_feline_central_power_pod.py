"""One shared SOURCE POD + upper E2 + printed-frame wire portal hypothesis.

No native N03. Keep both short branches and all four physical225 pigtails
in the initial arithmetic. FHAC internal allowance is a PROJECT budget,
not a manufacturer drawing dimension or permission to energize.
"""
import math,json
import numpy as np
import FreeCAD as A
import Part
import feline_tangent_routes as ft
from plan_feline_layout import OUT
from feline_source_saddles import segment
from receive_feline_underplate_return_gallery import bend,forward
from plan_feline_jpwm_factory_middle import parallel_csc
from plan_feline_coupled_rear_power import arc_rows


def plan(ends):
    specs=json.loads((OUT/'n01-U1-frontband-common-plan.json').read_text())['specs']
    feeds={};rows=[]
    q=forward(rows,[-13,0,54],[0,0,1],.25)
    faux_in,faux_axis=bend(rows,q,[0,0,1],[-math.sqrt(3)/2,.5,0],12.4,math.pi/4)
    feeds['XA01']=dict(parts=rows,input_mm=faux_in.tolist(),axis=faux_axis.tolist(),
        jacket_mm=sum(r['length_mm'] for r in rows),strip_mm=11.,
        internal_project_allowance_mm=25.5,internal_allowance_NOT_manufacturer_guarantee=True,
        internal_must_be_measured_before_energizing=True)
    rows=[];q=forward(rows,[-6.5,0,54],[0,0,1],2.)
    fpwm_in,fpwm_axis=bend(rows,q,[0,0,1],[0,-1,0],12.6,math.pi/4)
    feeds['XP01']=dict(parts=rows,input_mm=fpwm_in.tolist(),axis=fpwm_axis.tolist(),
        jacket_mm=sum(r['length_mm'] for r in rows),strip_mm=11.,internal_project_allowance_mm=16.8)
    for r in feeds.values():
        r['total_nominal_unfused_mm']=r['jacket_mm']+r['strip_mm']+r['internal_project_allowance_mm']
        r['maximum_mm']=50.;assert r['total_nominal_unfused_mm']<=50
    routes={}
    zs=[next(e['routing_exit_mm'][2] for e in ends if e['id']==w+'/extra/end') for w in ('XP02.module','XP03.module')]
    for index,(w,yend) in enumerate((('XP02.module',-1.5),('XP03.module',1.5))):
        e=next(e for e in ends if e['id']==w+'/extra/end');R=12.4+(zs[0]-zs[index]);rows=[]
        q=forward(rows,e['routing_exit_mm'],[0,1,0],18.85-e['routing_exit_mm'][1])
        q,d=bend(rows,q,[0,1,0],[0,0,1],R)
        shaft_start=q.tolist();q=forward(rows,q,d,42.-q[2])
        upper=[42.77,yend,77.6];rows+=parallel_csc(q,upper,d,12.4)
        q,d=bend(rows,upper,d,[1,0,0],12.4)
        assert np.linalg.norm(q-[55.17,yend,90])<1e-6
        bare=sum(segment(r).Length for r in specs[e['id']]['bare_parts'])
        other=e['source_prefix_length_mm']+bare
        routes[w]=dict(parts=rows,need_mm=sum(r['length_mm'] for r in rows)+other+16+9,
            counterpart_jacket_and_formed_bare_mm=other,allowance_mm=16.,E2_prefix_mm=9.,
            lower_vertical_portal_start_mm=shaft_start)
    # Clock toward the negative gallery, ABOVE the negative bank but outside
    # Pi's Y footprint. Whole opposite-tangent bridge, not a radius waiver.
    out=np.asarray(fpwm_in)+42*np.asarray(fpwm_axis);rows=[]
    q,d=bend(rows,out,fpwm_axis,[1,0,0],12.4)
    choices=[]
    for ratio in (.5,1.,2.):
        try:
            s=ft.biarc(q,d,[103.77,-1.5,90],[-1,0,0],ratio)
            if ft.min_radius(s)>=12.4:choices.append(s)
        except ValueError:pass
    assert choices,'No radius waiver in whole source pigtail'
    rows+=arc_rows(min(choices,key=ft.length))
    routes['XP02.source']=dict(parts=rows,need_mm=sum(r['length_mm'] for r in rows)+49.,allowance_mm=40.,E2_prefix_mm=9.,
        curved_source9_to_be_allocated_ON_the_same_whole_path=True)
    rows=[];q=forward(rows,[128,66,80.595],[0,0,1],12.)
    q,d=bend(rows,q,[0,0,1],[0,-1,0],12.4)
    choices=[]
    for ratio in (.5,1.,2.):
        try:
            s=ft.biarc(q,d,[103.77,1.5,90],[-1,0,0],ratio)
            if ft.min_radius(s)>=12.4:choices.append(s)
        except ValueError:pass
    assert choices,'No actual factory radius may be relaxed'
    rows+=arc_rows(min(choices,key=ft.length))
    routes['XP03.source']=dict(parts=rows,need_mm=sum(r['length_mm'] for r in rows)+32.25,
        counterpart_jacket_mm=12.25,allowance_mm=11.,E2_prefix_mm=9.)
    for r in routes.values():
        r.update(minimum_catalogue_mm=220.,margin_mm=220-r['need_mm'],free_end_fit_cut_only=True)
        assert r['margin_mm']>=0
    return dict(status='CENTRAL_POD_ALL_FEED_FACTORY_MATH_ONLY_NOT_GEOMETRY',feeds=feeds,routes=routes,
        PREAR=dict(centre_mm=[0,0,43],rotation_X_deg=-90,physical_XA01_W065_slots_swapped_same_bus=True),
        F_AUX=dict(input_mm=faux_in.tolist(),axis=faux_axis.tolist(),
            centre_mm=(faux_in+25.5*faux_axis).tolist(),closed_case_envelope_mm=[22,51,20.25],
            body_ENVELOPE_not_detailed_supplier_material=True),
        F_PWM=dict(input_mm=fpwm_in.tolist(),axis=fpwm_axis.tolist(),
            centre_mm=(fpwm_in+21*fpwm_axis).tolist(),sleeved_body_envelope_mm=[6.4,42]),
        E2=dict(centre_mm=[79.47,0,90],source_axis=[1,0,0],module_axis=[-1,0,0],
            red_relative_Y_mm=-1.5,black_relative_Y_mm=1.5,whole_heads_close_below_bands=True),
        portal=dict(owner='Ref_Material_P0_SideLeft22_0_0',centre_X_mm=42.77,
            shaft_Y_mm=[routes[w]['lower_vertical_portal_start_mm'][1] for w in ('XP02.module','XP03.module')],
            jacket_radius_mm=.925,foreign_material_margin_mm=1.25,
            battery_straps_bolt_bearings_and_frame_connectivity_NOT_yet_received=True),
        native_changed=False,N01_complete=False,physical_pass=False,selected=False)


def bodies(fixed,ends,recipe):
    """Read-only copies of four bought envelopes and full E2 source kits.

    Source comb/clocks/retention/load paths are explicit subsequent shared
    geometry. No operator may call these bare bodies a complete source pod.
    """
    from receive_feline_global_case_candidates import placement
    from receive_feline_jpwm_whole_pose import short_straight_template
    from plan_feline_n01_shared import pipe
    actors={};metadata={};groups={};mates=[]
    r=A.Rotation(A.Vector(1,0,0),-90);old=fixed['Station:P_REAR:case']
    tf=A.Placement(A.Vector(*recipe['PREAR']['centre_mm'])-r.multVec(old.BoundBox.Center),r)
    s=old.copy();s.Placement=tf*s.Placement;actors['CentralPod:P_REAR:case']=s
    for w,x in (('W065',13.),('W044',0.),('W052',6.5),('XP01',-6.5),('XA01',-13.)):
        rr=recipe['feeds'][w]['parts'] if w in recipe['feeds'] else [dict(kind='line',start=[x,0,54],end=[x,0,63.25])]
        radius={'W065':2.1,'W044':2.1,'W052':2.1,'XP01':1.05,'XA01':2.}[w]
        name='CentralPod:wire:'+w;actors[name]=pipe(rr,radius);metadata[name]=dict(kind='wire',wire=w)
        mates.append((name,'CentralPod:P_REAR:case'))
    fr=A.Rotation(A.Vector(0,0,1),A.Vector(*recipe['F_PWM']['axis']))
    old=fixed['Station:F_PWM_whole:F_PWM:case'];tf=A.Placement(A.Vector(*recipe['F_PWM']['centre_mm'])-fr.multVec(old.BoundBox.Center),fr)
    s=old.copy();s.Placement=tf*s.Placement;actors['CentralPod:F_PWM:case']=s
    axis=np.asarray(recipe['F_AUX']['axis']);lateral=np.array([.5,math.sqrt(3)/2,0.]);up=np.cross(lateral,axis)
    rot=np.column_stack((lateral,axis,up));old=fixed['Ref_Material_F_AUX_candidate_case_0_0']
    tf=placement(rot,np.asarray(recipe['F_AUX']['centre_mm'])-rot@np.asarray(list(old.BoundBox.Center)))
    s=old.copy();s.Placement=tf*s.Placement;actors['CentralPod:F_AUX:case']=s
    mates.extend([('CentralPod:wire:XP01','CentralPod:F_PWM:case'),('CentralPod:wire:XA01','CentralPod:F_AUX:case')])
    template,_,_=short_straight_template(ends);case=fixed['Ref_Material_JPWM_0_0']
    er=A.Rotation(A.Vector(0,0,1),180)*A.Rotation(A.Vector(1,0,0),90)
    et=A.Placement(A.Vector(*recipe['E2']['centre_mm'])-er.multVec(case.BoundBox.Center),er)
    for n,s in {**template,'Ref_Material_JPWM_0_0':case}.items():
        a=s.copy();a.Placement=et*a.Placement;actors[n]=a;groups[n]='JPWM'
        metadata[n]=dict(kind='wire',wire=n.split(':',1)[1]) if n.startswith('JPWMSource:') else dict(kind='PETG' if n.endswith(':pad') else 'T18I')
    for side in ('source','module'):
        b=actors['JPWMGrip:'+side+':band'].BoundBox;old=actors['JPWMGrip:'+side+':head'];h=old.BoundBox
        head=Part.makeBox(h.XLength,h.YLength,h.ZLength,A.Vector(h.XMin,h.YMin,b.ZMin-h.ZLength))
        assert abs(head.Volume-old.Volume)<1e-6 and len(actors['JPWMGrip:'+side+':band'].fuse(head).Solids)==1
        actors['JPWMGrip:'+side+':head']=head
    for n in actors:
        if n not in metadata:metadata[n]=dict(kind='purchased_case_reservation')
        if n not in groups:groups[n]=n # changed intrinsic pairs must NOT be silently skipped
    metadata['Ref_Material_JPWM_0_0']=dict(kind='purchased_case_reservation')
    retired=[n for n in fixed if n.startswith(('Station:P_REAR:','Station:F_PWM_whole:'))]
    retired+=['Ref_Material_JPWM_0_0','Ref_Material_F_AUX_candidate_case_0_0']
    return actors,metadata,groups,mates,retired
