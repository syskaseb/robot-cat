"""One whole power-bay hypothesis; never a partial N01 approval.

Five unchanged P_REAR cavities clock together. Two distinct input9 lands
use the existing XP01<=50 allowance, not a guessed0.6mm nudge. Keep both
E2 sides and the real foot fasteners. Factory maths precedes new supports.
"""
import json,math
import numpy as np
import FreeCAD as A
import Part
import feline_tangent_routes as ft
from plan_feline_layout import OUT
from plan_feline_n01_shared import pipe
from plan_feline_jpwm_factory_middle import parallel_csc,planar_csc
from receive_feline_underplate_return_gallery import bend,forward
from receive_feline_jpwm_whole_pose import short_straight_template
from feline_source_saddles import segment


def e2_z():
    # Complete case above received factory heads, complete bands below
    # actual belly-foot fasteners. These are stored CURRENT world datums.
    lo=-25.9+1.25+6.;hi=-9.3-1.25-3.775
    assert lo<hi
    return (lo+hi)/2


def feed_gate(ends,prear_tf=None,fuse_input_overrides=None):
    """Both mandatory branches, BEFORE CAD. Lower bound, not routed PASS."""
    rows=[]
    for wire in ('XP01','XA01'):
        source=next(e for e in ends if e['id']==wire+'/extra/start')
        target=next(e for e in ends if e['id']==wire+'/extra/end')
        p=A.Vector(*source['point_mm'])
        if prear_tf is not None:p=prear_tf.multVec(p)
        end=(fuse_input_overrides or {}).get(wire) or target.get('point_mm') or target.get('jacket_routing_point_mm')
        assert end is not None,'No invented fuse input pin'
        q=A.Vector(*end);minimum=(q-p).Length
        rows.append(dict(wire=wire,source_mm=list(p),fuse_input_mm=list(q),
            straight_lower_bound_mm=minimum,maximum_whole_unfused_mm=50.,
            hard_hold=minimum>50.,strip_bends_internal_and_slack_NOT_in_lower_bound=True))
    return dict(status='BOTH_FUSE_NECESSARY_GATE_HOLD' if any(r['hard_hold'] for r in rows) else 'BOTH_FUSE_NECESSARY_GATE_ONLY',
        rows=rows,N01_complete=False,not_a_routed_or_electrical_PASS=True)


def construct(fixed,ends,*,scoped_units_only=False):
    actors={};groups={};old=fixed['Station:P_REAR:case'].BoundBox.Center
    rot=A.Rotation(A.Vector(0,0,1),-90)
    tf=A.Placement(A.Vector(122,-45,98)-rot.multVec(old),rot)
    if not scoped_units_only:
        gate=feed_gate(ends,tf,{'XP01':[89.75,-38.5,98]})
        if any(r['hard_hold'] for r in gate['rows']):
            raise ValueError('Whole source pod required: BOTH XP01 and XA01 before more CAD')
    for n,s in fixed.items():
        if n.startswith('Station:P_REAR:'):
            a=s.copy();a.Placement=tf*a.Placement;actors[n]=a;groups[n]='PREAR'
    case=fixed['Ref_Material_JPWM_0_0'];template,_,_=short_straight_template(ends)
    er=A.Rotation(A.Vector(0,0,1),-90)*A.Rotation(A.Vector(0,1,0),180)
    et=A.Placement(A.Vector(116,0,e2_z())-er.multVec(case.BoundBox.Center),er)
    for n,s in {**template,'Ref_Material_JPWM_0_0':case}.items():
        a=s.copy();a.Placement=et*a.Placement;actors[n]=a;groups[n]='JPWM'
    for side in ('source','module'):
        b=actors['JPWMGrip:'+side+':band'].BoundBox;oldhead=actors['JPWMGrip:'+side+':head']
        h=oldhead.BoundBox
        head=Part.makeBox(h.XLength,h.YLength,h.ZLength,A.Vector(b.XMax,h.YMin,h.ZMin))
        assert abs(head.Volume-oldhead.Volume)<1e-7
        assert len(actors['JPWMGrip:'+side+':band'].fuse(head).Solids)==1
        actors['JPWMGrip:'+side+':head']=head
    oldcase=fixed['Station:F_PWM_whole:F_PWM:case'];fr=A.Rotation(A.Vector(0,0,1),A.Vector(-1,0,0))
    fcentre=A.Vector(68.75,-38.5,98)
    ff=A.Placement(fcentre-fr.multVec(oldcase.BoundBox.Center),fr)
    fs=oldcase.copy();fs.Placement=ff*fs.Placement
    actors['FPWM:newcase']=fs;groups['FPWM:newcase']='FPWM'
    actors['FPWM:input_independent9']=pipe([dict(kind='line',start=[98.75,-38.5,98],end=[89.75,-38.5,98])],1.05)
    groups['FPWM:input_independent9']='FPWM_INPUT'
    retired=[n for n in fixed if n.startswith(('Station:P_REAR:','Station:F_PWM_whole:'))]
    retired+=['Ref_Material_JPWM_0_0']
    recipe=dict(topology='ALL_FIVE_PREAR_MINUSX_INLINE_FPWM_AND_TRANSVERSE_E2_SOURCE_MINUSY',
        PREAR_centre_mm=[122,-45,98],PREAR_clock_Z_deg=-90,
        E2_centre_mm=[116,0,e2_z()],E2_source_axis=[0,-1,0],E2_module_axis=[0,1,0],
        E2_Z_interval_mm=[-18.65,-14.325],FPWM_centre_mm=list(fcentre),FPWM_axis=[-1,0,0],
        XP01_case_prefix_mm=12.25,XP01_distinct_input_land_mm=9.,XP01_strip_mm=11.,
        XP01_inside_pigtail_to_fuse_body_mm=16.8,XP01_total_mm=49.05,XP01_max_mm=50.,
        same_physical_PREAR_cavity_ids=True,S1_core_and_R47_unchanged=True,retired=retired,
        source_input9_grip_body_two_ties_output_curved9_roots_and_assembly_OPEN=True,
        scoped_units_only_NOT_a_whole_power_solution=True,
        N01_complete=False,selected=False,physical_pass=False)
    return actors,groups,recipe


def arc_rows(parts):
    result=[]
    for s in parts:
        r=dict(kind=s['kind'],start=s['start'],end=s['end'],length_mm=s['length'])
        if s['kind']=='arc':r.update(mid=list(ft.samples(s,s['length']/2))[1],radius_mm=s['radius'])
        result.append(r)
    return result


def factory_math(ends):
    R=12.4;Z=e2_z();routes={}
    specs=json.loads((OUT/'n01-U1-frontband-common-plan.json').read_text())['specs']
    for w,z in [('XP02.module',Z+1.5),('XP03.module',Z-1.5)]:
        e=next(e for e in ends if e['id']==w+'/extra/end')
        h=z-e['routing_exit_mm'][2];angle=math.acos(1-h/(2*R));rows=[]
        q,d=bend(rows,e['routing_exit_mm'],[0,1,0],[0,0,1],R,angle)
        n=np.array([0,1.,0])-d*d[1];n/=np.linalg.norm(n)
        q,d=bend(rows,q,d,n,R,angle)
        rows+=planar_csc(q,d,[116,24.3,z],[0,-1,0],R)
        bare=sum(segment(r).Length for r in specs[e['id']]['bare_parts'])
        prefix=e['source_prefix_length_mm']
        need=sum(r['length_mm'] for r in rows)+prefix+bare+16.+9.
        routes[w]=dict(parts=rows,nominal_fit_need_mm=need,other_jacket_prefix_mm=prefix,
            actual_formed_bare_mm=bare,selected_additional_allowance_mm=16.,E2_prefix_mm=9.)
    out=[];q=forward(out,[47.75,-38.5,98],[-1,0,0],.25)
    q,d=bend(out,q,[-1,0,0],[0,0,-1],R)
    # Earlier three analytic tangent ratios could not satisfy min220.
    # Ratio4 preserves R>=12.4 and the SAME source/receiver poses.
    arcs=ft.biarc(q,d,[116,-24.3,Z+1.5],[0,1,0],4.)
    assert ft.min_radius(arcs)>=R
    rows=out+arc_rows(arcs)
    routes['XP02.source']=dict(parts=rows,nominal_fit_need_mm=sum(r['length_mm'] for r in rows)+49.,
        selected_additional_allowance_mm=40.,E2_prefix_mm=9.,
        curved_source9_included_in_parts=True,source_prefix_parts=out,source_grip_arc_length_mm=[sum(r['length_mm'] for r in out)-9,sum(r['length_mm'] for r in out)])
    rows=[];q,d=bend(rows,[128,66,80.595],[0,0,1],[0,-1,0],R,math.pi)
    shaft=[116,-36.7,Z-1.5+R];rows+=parallel_csc(q,shaft,d,R)
    q,d=bend(rows,shaft,d,[0,1,0],R)
    routes['XP03.source']=dict(parts=rows,nominal_fit_need_mm=sum(r['length_mm'] for r in rows)+32.25,
        other_jacket_prefix_mm=12.25,selected_additional_allowance_mm=11.,E2_prefix_mm=9.)
    for r in routes.values():
        r.update(minimum_catalogue_mm=220.,minimum_catalogue_margin_mm=220.-r['nominal_fit_need_mm'],
            free_end_fit_cut_only=True,factory_contact_preserved=True,selected_SKU_unchanged=True)
        assert r['minimum_catalogue_margin_mm']>=0
    return dict(status='FOUR_FACTORY_MATH_ONLY_NOT_CLEARANCE',routes=routes,
        need_mm={w:r['nominal_fit_need_mm'] for w,r in routes.items()},
        XP01_mm=49.05,N01_complete=False,physical_pass=False)


def save_units(actors,groups,recipe,receipt,pins):
    """Preserve the received whole bodies; roots/factory solids still OPEN."""
    import hashlib,zipfile
    from check_main_p0_placement import ROOT,sha
    from feline_atomic_save import save_json
    assert receipt['status']=='COUPLED_REAR_POWER_UNITS_STATIC_RECEIVED'
    assert not receipt['failures'] and all(r['ok'] for r in receipt['checks'].values())
    dest=OUT/'n01-coupled-rear-power-units.json';bundle=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in actors.items():
            assert s.isValid() and s.Solids
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            kind='wire' if n.startswith(('JPWMSource:','Station:P_REAR:wire:')) or n=='FPWM:input_independent9' else 'T18I' if n.endswith((':band',':head',':band_budget',':head_budget')) else 'PETG' if n.endswith((':pad',':split_common_comb')) else 'purchased_case_reservation'
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),kind=kind,group=groups[n]))
    r=dict(status='WHOLE_REAR_POWER_UNITS_STATIC_ONLY_ROOTS_FACTORY_ASSEMBLY_OPEN',geometry=geometry,
        bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),recipe=recipe,
        source_sha256=pins,retired=recipe['retired'],failures=[],N01_complete=False,
        physical_pass=False,native_unchanged=True,selected=False)
    save_json(dest,r)
    return r


def factory_shapes(plan):
    shapes={};metadata={};groups={}
    for w,r in plan['routes'].items():
        name='FactoryPower:'+w
        shapes[name]=pipe(r['parts'],.925)
        metadata[name]=dict(kind='wire',wire=w,nominal_profile_radius_mm=.925)
        groups[name]=w
    # Named zero-volume end faces only. Shared supports/other conductors
    # remain in the ordinary tests, including each complete own prefix.
    owners={'XP02.module':('U1Five:XP02.module:jacket','JPWMSource:XP02.module'),
        'XP03.module':('U1Five:XP03.module:jacket','JPWMSource:XP03.module'),
        'XP02.source':('FPWM:newcase','JPWMSource:XP02.source'),
        'XP03.source':('Station:G_TAIL:wire:G_TAIL.3','JPWMSource:XP03.source')}
    mates=[('FactoryPower:'+w,b) for w,bs in owners.items() for b in bs]
    return shapes,metadata,groups,mates
