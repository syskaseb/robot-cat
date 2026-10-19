"""Shared harness SPACE before carrier branches, not final123 wire curves.

Whole functional galleries and a USB service-loop bay are tested against
actual rigid parts/stock/motion. Existing insulated harness prefixes are
occupancy inside this same proposed routing resource, never deleted parts
or a claim that their final individual separation has been qualified.
"""
import hashlib,json,math,os,sys,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_common_retention_roots import archived
from feline_two_lane_receive import world_context
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement


def transition_separation_bound(a,b,intervals=4096):
    """Continuous swept-jacket gap lower bound, not a sample-only verdict.

    A B-spline derivative lies in the convex hull of its control vectors.
    Every parameter value is within half a grid interval of a sample, so
    subtracting both maximum-speed errors bounds the continuous pair distance.
    """
    from scipy.interpolate import BSpline
    from scipy.spatial import cKDTree
    samples=[];errors=[];speeds=[]
    for row in (a,b):
        spline=BSpline(row['knots'],row['poles_mm'],3)
        lo,hi=spline.t[3],spline.t[-4]
        speed=float(np.linalg.norm(spline.derivative().c,axis=1).max())
        samples.append(spline(np.linspace(lo,hi,intervals+1)))
        speeds.append(speed);errors.append(speed*(hi-lo)/(2*intervals))
    sample_gap=float(cKDTree(samples[0]).query(samples[1])[0].min())
    radii=a['radius_mm']+b['radius_mm'];lower=float(sample_gap-sum(errors)-radii)
    return dict(a=a['name'],b=b['name'],gap_lower_bound_mm=lower,
        minimum_mm=.2,ok=lower>=.2,method='derivative_convex_hull_continuous_axis_distance_lower_bound_minus_jacket_radii',
        sample_axis_gap_mm=sample_gap,axis_discretization_error_bound_mm=sum(errors),
        maximum_parameter_speeds=speeds,intervals=intervals,jacket_radii_sum_mm=radii)


def under_bridge_candidates():
    """Whole lower topology: real JR mouths, full9 BEFORE bends, underframe.

    No purchased wire shrink or repeated upper-gap offsets. Current head
    motion, skin and physical carrier roots remain separate open gates.
    """
    rows=[]
    def make(name,start,steps,radius,**data):
        p=np.array(start,float);edges=[];samples=[p.copy()];max_step=0.
        for step in steps:
            if step[0]=='line':
                q=np.array(step[1],float);L=np.linalg.norm(q-p);n=max(1,int(math.ceil(L/.05)))
                samples.extend(p+(q-p)*v for v in np.linspace(0,1,n+1)[1:]);max_step=max(max_step,L/n)
                edges.append(Part.makeLine(A.Vector(*p),A.Vector(*q)));p=q
            else:
                _,t,b,R=step;t=np.array(t,float);b=np.array(b,float)
                at=lambda a:p+R*math.sin(a)*t+R*(1-math.cos(a))*b
                q=at(math.pi/2);n=int(math.ceil(R*math.pi/2/.05))
                samples.extend(at(a) for a in np.linspace(0,math.pi/2,n+1)[1:]);max_step=max(max_step,R*math.pi/2/n)
                edges.append(Part.Arc(A.Vector(*p),A.Vector(*at(math.pi/4)),A.Vector(*q)).toShape());p=q
        path=Part.Wire(edges);normal=A.Vector(0,-1,0) if name.startswith('HP_source:') else A.Vector(1,0,0)
        s=path.makePipeShell([Part.Wire([Part.makeCircle(radius,A.Vector(*start),normal)])],True,False)
        expected=math.pi*radius**2*path.Length
        assert s.isValid() and len(s.Solids)==1 and s.Volume>0 and abs(s.Volume-expected)<expected*1e-5
        rows.append(dict(name=name,shape=s,start_mm=start,end_mm=p.tolist(),radius_mm=radius,path_length_mm=path.Length,
            analytic_expected_volume_mm3=expected,axis_samples_mm=[v.tolist() for v in samples],axis_sample_error_bound_mm=max_step/2,**data))
    Y=-38.320513724211
    for wire,x,R in (('XB22',-238.6,14.94),('XB23',-241.14,17.48),('XS23',-236.06,12.4)):
        start=[x,Y,-10.];grip0=[x,Y-3,-10.];grip1=[x,Y-12,-10.]
        make('HP_source:'+wire,start,[('line',grip1),('arc',[0,-1,0],[0,0,-1],12.4),('arc',[0,0,-1],[1,0,0],R)],1.05,
            kind='head_actual_source_nominal_jacket',wire=wire,full9_grip_mm=[grip0,grip1],minimum_wire_R_mm=12.4,
            source_nominal_radius_unchanged_not_supplier_guarantee=True)
    start=[-223.66,Y-24.4,-37.34]
    central='--head-neck-central-floor' in sys.argv
    finish_y=-14. if central else -20.
    make('HP_central_underfloor' if central else 'HP_under_bridge_and_frame',start,[('arc',[1,0,0],[0,1,0],17.),('line',[-206.66,finish_y-17.,-37.34]),
        ('arc',[0,1,0],[1,0,0],17.),('line',[-70.,finish_y,-37.34])],4.,kind='three_wire_under_frame_resource',
        minimum_inner_resource_bend_R_mm=13.,minimum_wire_R_mm=12.4,source_three_jackets_fit_R4=True,
        body_floor_min_Z_mm=-48.,resource_min_Z_mm=-41.34,roots_skin_current_head_motion_open=True)
    return rows


def candidates():
    if '--head-neck-under-bridge' in sys.argv or '--head-neck-central-floor' in sys.argv:return under_bridge_candidates()
    rows=[]
    flat='--head-neck-flat-ribbon' in sys.argv
    topentry=flat or '--head-neck-top-entry' in sys.argv
    overbridge=topentry or '--head-neck-overbridge' in sys.argv
    if any(a in sys.argv for a in ('--head-neck-only','--head-neck-inboard','--head-neck-overbridge','--head-neck-top-entry','--head-neck-flat-ribbon')):
        # Two separate flexible three-wire groups; C_HY is a continuous-wire
        # accounting plane, NOT a new connector or mandatory extra9mm grip.
        # HP triple needs a raised bypass over the retained yaw JR pair.
        for name,x0,x1,y,z in (('HP_above_yaw_JR',-223.66,-180.,-53.720513724211,26.34),
                               ('head_body_merge',-152.,-120.,-56.,-6.)):
            rows.append(dict(name=name,kind='head_neck_shared_space_proposal',start_mm=[x0,y,z],end_mm=[x1,y,z],radius_mm=6.,
                shape=Part.makeCylinder(6.,x1-x0,A.Vector(x0,y,z),A.Vector(1,0,0)),
                source_boundary_not_new_connector=True,whole_joined_curve_radii_head_motion_and_skin_open=True))
        if '--head-neck-inboard' not in sys.argv and not overbridge:return rows
        rows=rows[:1] # Received HP/JR space is unchanged, never replayed.
        def route(name,start,drop):
            p=np.asarray(start,float);edges=[];R=17.
            def bend(t,b,a,r=17.):
                nonlocal p
                at=lambda z:p+r*math.sin(z)*t+r*(1-math.cos(z))*b
                end=at(a);edges.append(Part.Arc(A.Vector(*p),A.Vector(*at(a/2)),A.Vector(*end)).toShape());p=end
            def s_bend(dz,r):
                sign=1 if dz>0 else -1;angle=math.acos(1-abs(dz)/(2*r))
                bend(np.array([1.,0,0]),np.array([0.,0,sign]),angle,r)
                bend(np.array([math.cos(angle),0,sign*math.sin(angle)]),np.array([math.sin(angle),0,-sign*math.cos(angle)]),angle,r)
            if overbridge and name.startswith('HY_'):
                bend(np.array([0.,1,0]),np.array([1.,0,0]),math.pi/2)
            else:
                if overbridge:s_bend(26.16 if flat else 27.66,17.)
                elif drop:s_bend(-drop,R)
                bend(np.array([1.,0,0]),np.array([0.,1,0]),math.pi/2)
                end=p.copy();end[1]=-35. if overbridge else -24.6;assert end[1]>=p[1]
                edges.append(Part.makeLine(A.Vector(*p),A.Vector(*end)));p=end
                bend(np.array([0.,1,0]),np.array([1.,0,0]),math.pi/2)
                if overbridge and not flat:
                    s_bend(-16.,17.);end=p.copy();end[0]=-75. if topentry else -115.;assert end[0]>p[0]
                    edges.append(Part.makeLine(A.Vector(*p),A.Vector(*end)));p=end;s_bend(-53.,30.)
            normal=A.Vector(0,1,0) if overbridge and name.startswith('HY_') else A.Vector(1,0,0)
            path=Part.Wire(edges);shape=path.makePipeShell([Part.Wire([Part.makeCircle(4.,A.Vector(*start),normal)])],True,False)
            assert shape.isValid() and len(shape.Solids)==1
            expected=math.pi*16*path.Length
            assert shape.Volume>0 and abs(shape.Volume-expected)<max(1e-4,expected*1e-6),(name,shape.Volume,expected)
            return dict(name=name,kind='three_wire_inboard_neck_resource',shape=shape,start_mm=start,end_mm=p.tolist(),radius_mm=4.,
                axis_bend_R_mm=17.,minimum_inner_resource_bend_R_mm=13.,minimum_wire_R_mm=12.4,three_wire_max_radius_budget_mm=1.7,
                space_fill_fraction=3*1.7**2/4**2,path_length_mm=path.Length,analytic_expected_volume_mm3=expected,not_ampacity_or_final_wire_curve=True)
        if overbridge:
            if not topentry:
                rows.append(route('HY_underplate_side_AUX',[-135.,-37.,-4.8],0))
                rows[1]['received_unchanged_source_prefix']='Old acceptedHY firstR17quarter then straight+Y through[-135,-37,-4.8]; subset of received source. Only new final quarter checked.'
            rows.append(route('HP_round_before_flatten' if flat else 'HP_over_bridge_and_plate',[-223.66,-53.720513724211,26.34],0))
            if flat:
                from scipy.interpolate import make_interp_spline
                from feline_cubic_curvature import extrema
                start=np.asarray(rows[-1]['end_mm']);L=32.;v=np.linspace(0,1,161);h=10*v**3-15*v**4+6*v**5
                radius=2.54+1.06*h;theta=math.pi/2*h
                for k,wire in ((-1,'XS23'),(0,'XB22'),(1,'XB23')):
                    points=np.column_stack([start[0]+L*v,start[1]+k*radius*np.sin(theta),start[2]-10.75*h+k*radius*np.cos(theta)])
                    spline=make_interp_spline(L*v,points,k=3,bc_type=([(1,[1.,0,0])],[(1,[1.,0,0])]))
                    proof=extrema(spline.t,spline.c);assert proof['regular'] and proof['minimum_radius_mm']>=12.4,(wire,proof['minimum_radius_mm'])
                    knots,mults=np.unique(spline.t,return_counts=True);curve=Part.BSplineCurve()
                    curve.buildFromPolesMultsKnots([A.Vector(*p) for p in spline.c],mults.tolist(),knots.tolist(),False,3)
                    path=Part.Wire([curve.toShape()]);body=path.makePipeShell([Part.Wire([Part.makeCircle(1.05,A.Vector(*points[0]),A.Vector(1,0,0))])],True,False)
                    expected=math.pi*1.05**2*path.Length;assert body.isValid() and len(body.Solids)==1 and abs(body.Volume-expected)<expected*1e-5
                    rows.append(dict(name='HP_flatten:'+wire,kind='head_transition_nominal_jacket',wire=wire,shape=body,radius_mm=1.05,
                        source_nominal_radius_unchanged_not_supplier_guarantee=True,path_length_mm=path.Length,analytic_expected_volume_mm3=expected,
                        continuous_curvature=proof,knots=spline.t.tolist(),poles_mm=spline.c.tolist(),source_array_pitch_mm=2.54,body_array_pitch_mm=3.6))
                endx=start[0]+L;lo=[endx,-23.3,40.05];hi=[-35.,-12.7,43.45]
                rows.append(dict(name='HP_flat_body_resource',kind='flat_three_wire_capacity_not_native_duct',shape=Part.makeBox(hi[0]-lo[0],10.6,3.4,A.Vector(*lo)),
                    body_reserved_max_wire_radius_mm=1.7,nominal_head_wire_radius_mm=1.05,not_material_thinning_or_diameter_change=True,
                    bounds_mm=[lo,hi],axis_Z_mm=41.75,no_extra_holder_inside_frame_S0_gap=True,full_end_grips_roots_and_final_routes_open=True))
            return rows
        rows.extend([route('HY_inboard_before_forehip',[-152.,-56.8,-4.8],0),
                     route('HP_above_JR_then_inboard',[-180.,-53.720513724211,26.34],16.34)])
        rows.append(dict(name='six_wire_inside_body_merge',kind='six_wire_merge_space',shape=Part.makeBox(32,15,25,A.Vector(-118,-15,-10)),
            new_skin_not_qualified=True,full6independent_grips_roots_and_final_fanout_open=True))
        return rows
    # Two complete levels, not one later tower per cable. Planning capacity
    # is calculated with55% fill; no ampacity/thermal claim follows from it.
    for side in (-1,1):
        for label,x0,x1,y,z in (('fore',-115,-24,30,72),('central',-24,105,24,70),
                              ('upper',-24,105,12,88),('lower',-90,105,28,-10)):
            start=[x0,side*y,z];end=[x1,side*y,z];r=5.
            rows.append(dict(name=label+str(side),kind='shared_harness_corridor',start_mm=start,end_mm=end,radius_mm=r,
                shape=Part.makeCylinder(r,x1-x0,A.Vector(*start),A.Vector(1,0,0)),
                project_wire_area_capacity_mm2=.55*math.pi*r*r,fill_is_space_budget_not_thermal_rating=True,
                complete_individual_wire_routes_accepted=False))
    # Full continuous helical space: extra length can be secured here instead
    # of arbitrarily shortening the selected0.5m cable in a picture.
    R=34.;pitch=7.;turns=1.5;origin=A.Vector(140,0,70)
    path=Part.makeHelix(pitch,pitch*turns,R);path.translate(origin)
    start=origin+A.Vector(R,0,0);tangent=A.Vector(0,R,pitch/(2*math.pi));tangent.normalize()
    profile=Part.Wire([Part.makeCircle(2.5,start,tangent)])
    loop=path.makePipeShell([profile],True,False);assert loop.isValid() and loop.Solids
    rows.append(dict(name='USB_service_loop',kind='selected_USB500_service_capacity',shape=loop,
        project_OD_mm=5,project_minimum_R_mm=30,coil_R_mm=R,pitch_mm=pitch,maximum_turns_reserved=turns,
        centre_mm=list(origin),curve_capacity_mm=path.Length,selected_total_mm=500,
        external452_mm_is_project_mould_allowance_not_supplier_guarantee=True,
        final_joined_USB_curve_and_exact_needed_slack_open=True))
    return rows


def main():
    tick=time.monotonic();rows=candidates();world,fixed=world_context();query=SolidQueries()
    files={k:OUT/n for k,n in dict(shared='n01-shared54-current.json',inline='n01-remaining-inline-body-closure.json',
        frame='n01-channelled-foundation-static.json',ends='n01-shared-routing-boundaries.json').items()}
    docs={k:json.loads(p.read_text()) for k,p in files.items()};assert docs['inline']['status']=='TWO_WHOLE_INLINE_KITS_RECEIVED_ROOTS_CORRIDORS_OPEN'
    shared=archived(docs['shared'],'parts');inline=archived(docs['inline'],'geometry');frame=archived(docs['frame'],'geometry')
    obstacles={**fixed,**shared,**{'CurrentInline:'+n:s for n,s in inline.items()},**{'CurrentFoundation:'+n:s for n,s in frame.items()}}
    for n in ('StructureReserve:BankBed-1','StructureReserve:BankBed1'):obstacles.pop(n,None)
    proposalmeta={r['name']:r for r in docs['shared']['parts']};inlinemeta={r['name']:r for r in docs['inline']['geometry']}
    def kind(n):
        if n in proposalmeta:return proposalmeta[n]['kind']
        if n.startswith('CurrentInline:'):return inlinemeta[n.removeprefix('CurrentInline:')]['kind']
        return world.meta.get(n,{}).get('kind','')
    def jacket(n):
        if ':bare' in n.lower() or kind(n)=='bare':return False
        return kind(n) in ('wire','proposal_wire','actual_wire','insulation_reservation','curve_profile_reservation') or bool(world.meta.get(n,{}).get('wire_owner')) or n.startswith(('End:','Factory:','CustomPrefix:','BankFullPrefix:','ShelfPWM:jacket:','PiGPIO:','PiPower:','PiUSBData')) or n in ('W043','W077','W078')
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
    flat='--head-neck-flat-ribbon' in sys.argv
    topentry=flat or '--head-neck-top-entry' in sys.argv
    overbridge=topentry or '--head-neck-overbridge' in sys.argv
    inboard=overbridge or '--head-neck-inboard' in sys.argv
    central='--head-neck-central-floor' in sys.argv
    under=central or '--head-neck-under-bridge' in sys.argv
    head=under or inboard or '--head-neck-only' in sys.argv
    dest=OUT/('n01-head-neck-central-floor-space.json' if central else 'n01-head-neck-under-bridge-space.json' if under else 'n01-head-neck-flat-ribbon-space.json' if flat else 'n01-head-neck-top-entry-resource-space.json' if topentry else 'n01-head-neck-overbridge-resource-space.json' if overbridge else 'n01-head-neck-inboard-resource-space.json' if inboard else 'n01-head-neck-resource-space.json' if head else 'n01-shared-corridor-space.json');pins={p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),Path(__file__))}
    result=dict(status='RUNNING_SHARED_CORRIDOR_RESOURCE_SPACE',source_sha256=pins,world_source_sha256=world.pins,
        galleries={},errors=[],N01_complete=False,physical_pass=False,selected=False,
        all123_individual_middle_curves_and_all_access_fans_still_open=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['world_source_sha256']==world.pins
        if '--repair-degenerate-HY-profile' in sys.argv:
            own=Path(__file__).relative_to(ROOT).as_posix()
            assert overbridge and not topentry and result['source_sha256'][own]=='883282f0f846cd214fb939a748d34e5b4305840ccad11cc70f67188d1df65030'
            assert all(p==own or h==pins[p] for p,h in result['source_sha256'].items())
            prior=result['galleries'].pop('HY_underplate_side_AUX')
            result['invalid_constructor_history']=dict(old_controller_sha256=result['source_sha256'][own],old_result_sha256=sha(dest),
                old_HY_row=prior,old_volume_mm3=-2.2737367544323206e-12,no_geometric_verdict_from_this_row=True,
                repair='Profile normalY for tangentY, positive analytic pi*r*r*L guard. Closed HP geometry/world unchanged, not repeated.')
            result['source_sha256']=pins
        elif '--receive-empty-separation-serialization-error' in sys.argv:
            own=Path(__file__).relative_to(ROOT).as_posix()
            assert flat and result['source_sha256'][own]=='cb45a95dec01192a583088681e72c7dae8f75603e4645bda364086dfd73b551d'
            assert all(p==own or h==pins[p] for p,h in result['source_sha256'].items())
            assert set(result['galleries'])=={'HP_above_yaw_JR','HY_inboard_before_forehip'} and 'transition_mutual' not in result
            result['received_empty_separation_serialization_error']=dict(previous_source_sha256=result['source_sha256'],
                previous_result_sha256=sha(dest),error='numpy.bool_ at save before new geometry queries',
                fix='Cast bound to Python float; unchanged candidate geometry, regression now serializes all rows')
            result['source_sha256']=pins
        else:assert result['source_sha256']==pins
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    if inboard:
        oldfile=OUT/'n01-head-neck-resource-space.json';old=json.loads(oldfile.read_text());rec=old['galleries']['HP_above_yaw_JR']
        assert old['world_source_sha256']==world.pins and rec['failure'] is None
        source_rows=[r for r in rows if r['name']=='HP_above_yaw_JR'];assert len(source_rows)==1
        for key in ('start_mm','end_mm','radius_mm'):assert rec[key]==source_rows[0][key]
        result['galleries'].setdefault('HP_above_yaw_JR',dict(rec,unchanged_geometry_and_world_receipt_reused_from=oldfile.relative_to(ROOT).as_posix(),received_sha256=sha(oldfile)))
        result['replaced_lower_outboard_merge_rejected_on']='motion:Ref_Material_P0_Part__Feature122_0_0:0'
        if overbridge:
            prefixfile=OUT/'n01-head-neck-inboard-resource-space.json';prefixdoc=json.loads(prefixfile.read_text())
            assert prefixdoc['world_source_sha256']==world.pins and prefixdoc['galleries']['HY_inboard_before_forehip']['failure'] is None
            result['HY_unchanged_source_prefix_receipt']=dict(path=prefixfile.relative_to(ROOT).as_posix(),sha256=sha(prefixfile),subset='First R17quarter and straight to Y-37 unchanged; final quarter and destination newly checked')
            if topentry:
                result['galleries'].setdefault('HY_inboard_before_forehip',dict(prefixdoc['galleries']['HY_inboard_before_forehip'],unchanged_whole_resource_reused_from=prefixfile.relative_to(ROOT).as_posix(),received_sha256=sha(prefixfile)))
                result['HY_body_breakout_around_AUX_remains_OPEN']=True
                result['invalidated_degenerate_old_HY_constructor']=dict(old_report='n01-head-neck-overbridge-resource-space.json',old_volume_mm3=-2.2737367544323206e-12,not_a_contact_or_clearance_verdict=True,reason='Initial profile normalX while tangentY; proper normal and analytic volume guard now mandatory')
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    if under:
        if central:
            oldfile=OUT/'n01-head-neck-under-bridge-space.json';old=json.loads(oldfile.read_text())
            assert old['world_source_sha256']==world.pins
            for row in rows:
                if not row['name'].startswith('HP_source:'):continue
                prior=old['galleries'][row['name']]
                for key in ('start_mm','end_mm','radius_mm','path_length_mm'):assert row[key]==prior[key]
                result['galleries'][row['name']]=dict(prior,unchanged_old_negative_or_mate_receipt_reused=True)
            result['head_stock_and_source_owner_bounds']={n:[[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin],[s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]] for n,s in obstacles.items() if 'Interface_FixedJR' in n or 'FixedYawCarrier' in n or n=='RootWebReserve1'}
            result['source_JR_band_and_mate_exit_not_qualified']=True
        result['unchanged_HY_receipts']=[]
        for file,name in (('n01-head-neck-inboard-resource-space.json','HY_inboard_before_forehip'),
                          ('n01-head-neck-overbridge-resource-space.json','HY_underplate_side_AUX')):
            p=OUT/file;d=json.loads(p.read_text());r=d['galleries'][name]
            assert d['world_source_sha256']==world.pins and r['failure'] is None
            result['unchanged_HY_receipts'].append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),gallery=name,pairs=len(r['pairs'])))
        from scipy.spatial import cKDTree
        actual=[r for r in rows if r['kind']=='head_actual_source_nominal_jacket'];result['source_mutual']=[]
        for i,a in enumerate(actual):
            for b in actual[i+1:]:
                sample=float(cKDTree(a['axis_samples_mm']).query(b['axis_samples_mm'])[0].min())
                error=a['axis_sample_error_bound_mm']+b['axis_sample_error_bound_mm']
                lower=sample-error-a['radius_mm']-b['radius_mm']
                result['source_mutual'].append(dict(a=a['wire'],b=b['wire'],gap_lower_bound_mm=lower,
                    error_bound_mm=error,method='piecewise_arc_length_Lipschitz_bound',ok=bool(lower>=.2)))
        assert all(r['ok'] for r in result['source_mutual'])
    save()
    if flat:
        actual=[r for r in rows if r['kind']=='head_transition_nominal_jacket'];result['transition_mutual']=[]
        for i,r in enumerate(actual):
            for other in actual[i+1:]:
                result['transition_mutual'].append(transition_separation_bound(r,other))
        assert all(r['ok'] for r in result['transition_mutual']),result['transition_mutual']
        save()
    def receive(s,row,rec):
        pairs=rec.setdefault('pairs',{})
        def record(k,op):
            if time.monotonic()-tick>235:raise TimeoutError('Whole-gallery completed pairs saved')
            if k not in pairs:pairs[k]=op();save()
            return pairs[k]['ok']
        def skin():
            common=s.copy().cut(outer);assert common.isNull() or common.isValid();gap=s.distToShape(outer.Shells[0])[0]
            return dict(ok=common.Volume<1e-5 and gap>=3.25-1e-6,gap_mm=gap,outside_mm3=common.Volume,required_mm=3.25)
        if head:
            rec['regional_scope_not_torso_containment_PASS']=True
            rec['new_neck_skin_AND_current_head_sweeps_not_qualified']=True
            rec['changed_old_cosmetic_interfaces']=[]
        elif not record('outer',skin):return 'outer'
        rec['existing_harness_prefix_occupancy']=[]
        for n,t in obstacles.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
            if head and n.startswith('Ref_Material_head_0_0_') and any(n.endswith('_'+v+'_0_0') for v in ('Rear','FrontLeft','FrontRightPorted','Nose','EarL','EarR')):
                rec['changed_old_cosmetic_interfaces'].append(n);continue
            if jacket(n):
                rec['existing_harness_prefix_occupancy'].append(n);continue
            def exact():
                q,target=s,t
                if n==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;target=world.bus['original']
                gap=query.distance(q,target);return dict(ok=gap>=1.25-1e-6,gap_mm=gap,required_mm=1.25)
            if not record('fixed:'+n,exact):return 'fixed:'+n
        for p in world.motion:
            if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
            def moving():
                q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement;gap=query.distance(q,world.rest[p['name']])
                return dict(ok=gap>=1.25-1e-6,gap_mm=gap,required_mm=1.25)
            if not record('motion:'+p['name']+':'+str(p['pose']),moving):return 'motion:'+p['name']+':'+str(p['pose'])
        return None
    try:
        for row in rows:
            rec=result['galleries'].setdefault(row['name'],{k:v for k,v in row.items() if k!='shape'})
            if 'failure' not in rec:rec['failure']=receive(row['shape'],row,rec);save();print('Whole corridor',row['name'],rec['failure'],flush=True)
        result['status']='SHARED_GALLERY_RESOURCES_RECEIVED_ACCESS_ALLOCATION_OPEN' if all(r['failure'] is None for r in result['galleries'].values()) else 'SHARED_GALLERY_ARCHITECTURE_REQUIRES_ALLOCATION_CHANGE_NOT_N01'
    except TimeoutError as exc:result.update(status='PARTIAL_SHARED_CORRIDOR_RESOURCE_SPACE',slice_note=str(exc))
    except Exception as exc:result['errors'].append(repr(exc));result['status']='SHARED_CORRIDOR_RESOURCE_ERROR'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],errors=result['errors'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
