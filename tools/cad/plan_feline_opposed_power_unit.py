"""One complete power-source fan, not another hand-picked world pose.

Same-rail XP01/W065 cavity swap is EXPLICIT. Two fuse leads turn to opposite
Z sides; three HELU trunks turn away from their adjacent fuse. Its output
gets a complete curved9 grip, not an obsolete avoid-bank bend. This is planning geometry,
not native production mounts or approval of a delivered fuse-holder drawing.
"""
import math
import copy
import numpy as np
import FreeCAD as A
import Part
from receive_feline_underplate_return_gallery import bend,forward
from plan_feline_n01_shared import pipe
from feline_source_saddles import build as grip,segment


def construct(fixed,ends,contract,shared_rear_interfaces=False,fpwm_output_angle=math.pi/3,fpwm_down_exit=False,fpwm_spatial_exit=None):
    old=fixed['Station:P_REAR:case'];rot=A.Rotation(A.Vector(0,0,1),180)
    tf=A.Placement(-rot.multVec(old.BoundBox.Center),rot)
    source={e['wire']:e for e in ends if e.get('group')=='WAGO:P_REAR'}
    assert set(source)=={'XA01','XP01','W065','W044','W052'}
    points={w:np.array(list(tf.multVec(A.Vector(*e['point_mm'])))) for w,e in source.items()}
    original={w:p.tolist() for w,p in points.items()}
    points['XP01'],points['W065']=points['W065'],points['XP01']
    assert all(abs(p[1]-11)<1e-7 and abs(p[2])<1e-7 for p in points.values())
    assert abs(points['XA01'][0]+13)<1e-7 and abs(points['XP01'][0]-13)<1e-7
    body=old.copy();body.Placement=tf*body.Placement
    actors={'PowerFan:P_REAR:case':body};meta={};groups={};mates=[];recipes={};feeds={}
    def add(n,s,kind,group=None):
        assert s.isValid() and len(s.Solids)==1,n
        actors[n]=s;meta[n]=dict(kind=kind);groups[n]=group or n
    meta['PowerFan:P_REAR:case']=dict(kind='purchased_case_reservation')
    groups['PowerFan:P_REAR:case']='PREAR'
    for w,e in source.items():
        profile=contract['portions'][e['portion_id']]
        R=profile['minimum_project_R_mm'];radius=profile['project_radius_mm']
        sign=1 if w in ('XA01','W065') else -1
        shared_pair=shared_rear_interfaces and w in ('W044','W052','W065')
        angle=math.pi/4 if shared_pair else math.pi/3 if w in ('XA01','XP01') else math.pi/2
        rows=[];p=forward(rows,points[w],[0,1,0],.25)
        normal=[-math.sqrt(.8),0,-math.sqrt(.2)] if shared_pair else [0,0,sign]
        p,d=bend(rows,p,[0,1,0],normal,R,angle)
        if shared_pair:
            normal=np.array([0.,1.,0.])-d*d[1];normal/=np.linalg.norm(normal)
            p,d=bend(rows,p,d,normal,R,angle)
            p=forward(rows,p,d,27.)
        wn='PowerFan:wire:'+w;add(wn,pipe(rows,radius),'wire')
        meta[wn].update(wire=w,nominal_profile_radius_mm=radius)
        mates.append((wn,'PowerFan:P_REAR:case'))
        recipes[w]=dict(end_id=e['id'],parts=rows,project_radius_mm=radius,R_mm=R,
                       routing_exit_mm=p.tolist(),routing_exit_axis=d.tolist())
        if shared_pair:continue # One planar comb below, not three curved pads.
        side=[-1 if w=='XA01' else 1,0,0] if w in ('XA01','XP01') else [0,0,sign]
        # Two complete rows, not overlapping7.6mm tie loops on6.5mm pitch.
        grip_row=2 if shared_pair and w=='W052' else 1
        start=15. if w=='W065' or w=='W052' and not shared_pair else 0.
        edge=segment(rows[grip_row]);u=edge.FirstParameter+(edge.LastParameter-edge.FirstParameter)*start/edge.Length
        tangent=edge.tangentAt(u);side=A.Vector(*side)
        side=side-tangent*side.dot(tangent);side.normalize()
        band_at=2.5 if shared_rear_interfaces and w in ('XA01','XP01') else start+4.5
        kit,proof=grip(rows[grip_row],start,side,band_at,channel_band=True)
        for k,s in kit.items():add('PowerFan:grip:'+w+':'+k,s,'T18I' if k!='pad' else 'PETG','grip:'+w)
        recipes[w]['grip']=proof
        recipes[w]['grip_row']=grip_row
        if w not in ('XA01','XP01'):continue
        internal=25.5 if w=='XA01' else 16.8
        total=sum(r['length_mm'] for r in rows)+11+internal
        assert total<=50
        feeds[w]=dict(total_nominal_unfused_mm=total,maximum_mm=50,
                      internal_project_allowance_mm=internal,not_supplier_guarantee=True)
        name='F_AUX' if w=='XA01' else 'F_PWM'
        oldcase=fixed['Ref_Material_F_AUX_candidate_case_0_0' if w=='XA01' else 'Station:F_PWM_whole:F_PWM:case']
        axis=A.Vector(0,1,0) if w=='XA01' else A.Vector(0,0,1)
        r=A.Rotation(axis,A.Vector(*d));half=25.5 if w=='XA01' else 21.
        ft=A.Placement(A.Vector(*(p+half*d))-r.multVec(oldcase.BoundBox.Center),r)
        case=oldcase.copy();case.Placement=ft*case.Placement
        cn='PowerFan:'+name+':case';add(cn,case,'purchased_case_reservation')
        mates.append((wn,cn))
        if w=='XP01':
            out=[];tip=forward(out,p+42*d,d,.25)
            target=np.array([0.,1.,0.]);normal=target-d*float(d@target);normal/=np.linalg.norm(normal)
            if fpwm_spatial_exit:
                normal=np.array([math.sqrt(.75),math.sqrt(.75)/2,.25])
                assert abs(normal@d)<1e-7
            tip,heading=bend(out,tip,d,normal,12.4,math.pi/2 if fpwm_down_exit or fpwm_spatial_exit else fpwm_output_angle)
            if fpwm_down_exit:tip,heading=bend(out,tip,heading,[1,0,0],12.4,math.pi/2)
            if fpwm_spatial_exit:
                extension=(fpwm_spatial_exit['maximum_local_x_mm']-tip[0])/heading[0]
                assert extension>=0;tip=forward(out,tip,heading,extension)
            add('PowerFan:F_PWM:out9',pipe(out,.925),'wire','FPWMoutput')
            meta['PowerFan:F_PWM:out9'].update(wire='XP02.source',nominal_profile_radius_mm=.925)
            mates.append(('PowerFan:F_PWM:out9',cn))
            side=-np.cross(d,normal) if fpwm_spatial_exit else [1,0,0]
            kit,proof=grip(out[1],0,side,4.5,channel_band=True)
            for k,s in kit.items():add('PowerFan:grip:XP02:'+k,s,'T18I' if k!='pad' else 'PETG','grip:XP02')
            recipes[w]['whole_received_output_kit_transform']=dict(rotation=list(ft.Rotation.Q),translation=list(ft.Base))
            recipes[w].update(output_routing_exit_mm=tip.tolist(),output_routing_axis=heading.tolist(),
                output_prefix_length_mm=sum(s['length_mm'] for s in out),output_parts=out,output_grip=proof,
                old_avoid_bank_turn_and_second_land_removed=True,full9_after_bend_not_extra_straight9=True)
        else:
            q=p+51*d;out=[]
            if shared_rear_interfaces:
                tip=forward(out,q,d,.25)
                tip,od=bend(out,tip,d,[1,0,0],15.,math.pi/4)
                normal=d-od*float(d@od);normal/=np.linalg.norm(normal)
                tip,od=bend(out,tip,od,normal,15.,math.pi/4)
                out_grip=out[1]
            else:
                tip=forward(out,q,d,9.);od=d;out_grip=out[0]
            # Full FHAC tail planning budget; not a claim that HELU OD is4mm.
            add('PowerFan:F_AUX:out9',pipe(out,2.),'insulation_reservation')
            mates.append(('PowerFan:F_AUX:out9',cn))
            kit,proof=grip(out_grip,0,[-1,0,0],4.5,channel_band=shared_rear_interfaces)
            for k,s in kit.items():add('PowerFan:grip:XA02:'+k,s,'T18I' if k!='pad' else 'PETG','grip:XA02')
            if not shared_rear_interfaces:mates.append(('PowerFan:grip:XA02:pad',cn))
            recipes[w]['output9']=dict(parts=out,capacity_radius_mm=2.,delivered_transition_fit_OPEN=True)
            recipes[w]['output9']['grip']=proof
            recipes[w]['output9'].update(routing_exit_mm=tip.tolist(),routing_exit_axis=od.tolist(),
                                         full9_after_bend=shared_rear_interfaces)
    if shared_rear_interfaces:
        pads=[];stock=[]
        for w,start in (('W065',0.),('W044',9.),('W052',18.)):
            # All three full ties/heads face INBOARD together, away from RR_G.
            kit,proof=grip(recipes[w]['parts'][-1],start,[0,0,1],start+4.5)
            pads.append(kit['pad']);recipes[w]['grip']=proof
            for k in ('band','head'):
                n='PowerFan:grip:'+w+':'+k
                add(n,kit[k],'T18I','TRUNK_ASSEMBLY');stock.append((w,n,kit[k]))
        boxes=[s.BoundBox for s in pads]
        lo=np.min([[b.XMin,b.YMin,b.ZMin] for b in boxes],axis=0)
        hi=np.max([[b.XMax,b.YMax,b.ZMax] for b in boxes],axis=0)
        plate=Part.makeBox(*(hi-lo),A.Vector(*lo))
        for w,n,s in stock:
            if n.endswith(':band'):plate=plate.cut(s.makeOffsetShape(.2,1e-6))
        assert plate.isValid() and len(plate.Solids)==1
        for i,(w,n,s) in enumerate(stock):
            assert plate.distToShape(s)[0]>=.2-1e-6,(n,'plate')
            for v,m,t in stock[i+1:]:
                if w!=v:assert s.distToShape(t)[0]>=.2-1e-6,(n,m)
            for v in ('W065','W044','W052'):
                assert s.distToShape(actors['PowerFan:wire:'+v])[0]>=.2-1e-6,(n,v)
        for w in ('W065','W044','W052'):
            assert plate.distToShape(actors['PowerFan:wire:'+w])[0]>=.2-1e-6,w
        add('PowerFan:trunk:comb',plate,'PETG','TRUNK_ASSEMBLY')
    plan=dict(topology='OPPOSED_FUSE_Z_AND_THREE_TYPED_TRUNKS',
        old_cavity_points_mm=original,planned_cavity_points_mm={w:p.tolist() for w,p in points.items()},
        explicit_same_rail_cavity_swap=['XP01','W065'],end_ids_and_materials_preserved=True,
        recipes=recipes,feeds=feeds,shared_three_trunk_comb=shared_rear_interfaces,
        common_comb_grip_rows_mm=[0.,9.,18.] if shared_rear_interfaces else [0.,15.],
        FPWM_output_turn_rad=math.pi/2 if fpwm_down_exit or fpwm_spatial_exit else fpwm_output_angle,
        FPWM_downward_two_quarter_exit=fpwm_down_exit,
        FPWM_spatial_exit=fpwm_spatial_exit,
        root_access_and_four_factory_joint_world_allocation_OPEN=True,
        N01_complete=False,selected=False,physical_pass=False)
    return actors,meta,groups,mates,plan


def own_grip_pairs():
    """Explicit own mount/insulated jacket interfaces, NOT foreign margins."""
    pairs={}
    def add(a,b):pairs['|'.join(sorted((a,b)))]=.2
    for w in ('XA01','XP01','W044','W052','W065'):
        add('PowerFan:wire:'+w,'PowerFan:grip:'+w+':pad')
        for k in ('pad','head','band'):
            add('PowerFan:P_REAR:case','PowerFan:grip:'+w+':'+k)
    for k in ('pad','band'):add('PowerFan:F_AUX:out9','PowerFan:grip:XA02:'+k)
    add('PowerFan:F_AUX:case','PowerFan:grip:XA02:pad')
    add('PowerFan:F_PWM:case','PowerFan:grip:XP02:pad')
    add('PowerFan:F_PWM:out9','PowerFan:grip:XP02:pad')
    for w in ('W065','W044','W052'):add('PowerFan:wire:'+w,'PowerFan:trunk:comb')
    return pairs


def receive_own_grips(raw):
    """Reuse measured gaps, keep all real contacts and every foreign hold."""
    result=copy.deepcopy(raw);policy=own_grip_pairs();changed={}
    for key,row in result['checks'].items():
        canonical='|'.join(sorted(key.split('|')))
        if canonical not in policy:continue
        row['previous_generic_foreign_minimum_mm']=row['minimum_mm']
        row['minimum_mm']=policy[canonical];row['ok']=row['gap_mm']>=policy[canonical]-1e-6
        changed[key]=dict(row)
    result.update(status='OPPOSED_POWER_TWO_ROW_OWN_GRIPS_RECEIVED',
        explicit_own_grip_policy=changed,foreign_margins_unchanged=True,
        original_generic_result_status=raw['status'],new_geometry_queries=0)
    result['failures']=[k for k,v in result['checks'].items() if not v['ok']]
    if result['failures']:result['status']='OPPOSED_POWER_TWO_ROW_OWN_GRIPS_HOLD'
    return result


def current_field_domains(actors,receipt,goal,stem,fixed_overlay=None,overlay_pins=None,overlay_cache=None):
    """Reuse received fields for a WHOLE unit, never a contact acceptance."""
    import itertools,json,time
    from scipy.signal import correlate
    from scipy.ndimage import label,distance_transform_edt
    from feline_signed_voxels import raster,deposit
    from feline_atomic_save import save_json
    from check_main_p0_placement import ROOT,sha
    from plan_feline_layout import OUT
    tick=time.monotonic();doc=json.loads(receipt.read_text());fp=ROOT/doc['field']
    assert doc['status']=='CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY' and sha(fp)==doc['field_sha256']
    with np.load(fp,allow_pickle=False) as f:
        clearance=np.minimum.reduce([f[k+'_signed_distance'][::2,::2,::2] for k in ('rigid','harness','motion36')])
        free=f['inside'][::2,::2,::2]&(clearance>=1.25+math.sqrt(3))&(f['outer_distance'][::2,::2,::2]>=3.25+math.sqrt(3))
        origin=f['origin_mm'].copy()
    overlay_sources=fixed_overlay or {};overlay_pins=overlay_pins or {}
    for p,h in overlay_pins.items():assert sha(ROOT/p)==h,p
    if overlay_sources:
        occupied=np.zeros(free.shape,bool)
        for n,s in overlay_sources.items():
            assert s.isValid() and s.Solids,n
            private=s.copy(True,True);v,faces=private.tessellate(.5)
            triangles=np.asarray([list(p) for p in v])[np.asarray(faces)]
            low,mask=raster(triangles,2.,lambda p:any(q.isInside(A.Vector(*p),1e-7,True) for q in private.Solids))
            deposit(occupied,mask,low,origin,step=2.)
        # Both template and overlay are filled2mm voxels, not exact surfaces.
        # Cover both half diagonals; final actual-geometry checks remain open.
        overlay_distance=distance_transform_edt(~occupied,sampling=2.).astype(np.float32)
        free&=overlay_distance>=1.25+2*math.sqrt(3)
        if overlay_cache:
            np.savez_compressed(overlay_cache,distance_mm=overlay_distance,occupied=occupied,
                origin_mm=origin,grid_mm=2.,source_pins_json=json.dumps(overlay_pins,sort_keys=True))
    cloud=[]
    for n,original in actors.items():
        s=original.copy(True,True);v,faces=s.tessellate(.5)
        triangles=np.asarray([list(p) for p in v])[np.asarray(faces)];solids=s.Solids
        lo,mask=raster(triangles,2.,lambda p:any(q.isInside(A.Vector(*p),1e-7,True) for q in solids))
        cloud.append(lo+2*np.argwhere(mask))
    points=np.unique(np.rint(np.vstack(cloud)/2).astype(int),axis=0);rows=[]
    blocked=(~free).astype(np.float32)
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((-1,1),repeat=3):
            rot=np.eye(3,dtype=int)[list(perm)]*np.asarray(signs)[:,None]
            if round(np.linalg.det(rot))!=1:continue
            p=points@rot.T;lo=p.min(0);hi=p.max(0)
            kernel=np.zeros(tuple(hi-lo+1),np.float32);kernel[tuple((p-lo).T)]=1
            counts=np.rint(correlate(blocked,kernel,mode='valid',method='fft')).astype(np.int32)
            zero=counts==0;components,num=label(zero);proposals=[]
            for component in range(1,num+1):
                ids=np.argwhere(components==component);centres=origin+2*(ids-lo)
                j=int(np.argmin(np.linalg.norm(centres-np.asarray(goal),axis=1)))
                proposals.append(dict(centre_mm=centres[j].tolist(),component_cells=len(ids)))
            best=np.unravel_index(np.argmin(counts),counts.shape)
            rows.append(dict(rotation=rot.tolist(),whole_unit_clear_cells=int(zero.sum()),
                components=proposals,minimum_blocked_pattern_cells=int(counts[best]),
                minimum_penalty_centre_mm=(origin+2*(np.asarray(best)-lo)).tolist()))
            print('WHOLE_POWER_FIELD',stem,len(rows),'clear',int(zero.sum()),'minblocked',int(counts[best]),flush=True)
    result=dict(status='WHOLE_UNIT_CURRENT_FIELD_PROPOSALS_NOT_GEOMETRY_ACCEPTANCE',actors=len(actors),
        source_sha256={receipt.relative_to(ROOT).as_posix():sha(receipt),fp.relative_to(ROOT).as_posix():sha(fp),**overlay_pins},
        complete_fixed_overlay_actors=list(overlay_sources),overlay_voxel_uncertainty_allowance_mm=2*math.sqrt(3),
        source_pattern_cells=len(points),grid_mm=2,whole_inside_filled_sources=True,orientations=rows,
        roots_tools_four_factory_lengths_and_exact_contacts_OPEN=True,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/(stem+'.json'),result)
    return result


def factory_math(power_pose,e2_pose,plan,ends,specs,local_caps=None,route_filter=None):
    """Four preserved factory units; actual U1 bare lengths, no guessed pins."""
    import feline_tangent_routes as ft
    from feline_spatial_csc import spatial_csc
    from plan_feline_coupled_rear_power import arc_rows
    pr,pc=np.asarray(power_pose['rotation']),np.asarray(power_pose['minimum_penalty_centre_mm'])
    er,ec=np.asarray(e2_pose['rotation']),np.asarray(e2_pose['centre_mm'])
    rec=plan['recipes']['XP01']['whole_received_output_kit_transform']
    fuse=A.Placement(A.Vector(*rec['translation']),A.Rotation(*rec['rotation']))
    routes={}
    for w in ('XP02.source','XP03.source','XP02.module','XP03.module'):
        e=next(e for e in ends if e['wire']==w and e.get('group')!='JPWM')
        p=np.array(e['routing_exit_mm']);d=np.array(e['routing_exit_axis'])
        if w=='XP02.source':
            p=pr@np.array(plan['recipes']['XP01']['output_routing_exit_mm'])+pc
            d=pr@np.array(plan['recipes']['XP01']['output_routing_axis'])
            debit=plan['recipes']['XP01']['output_prefix_length_mm']+40+9
        elif w=='XP03.source':debit=12.25+11+9
        else:
            bare=sum(segment(r).Length for r in specs[e['id']]['bare_parts'])
            debit=e['source_prefix_length_mm']+bare+16+9
        side=-1 if w.endswith('source') else 1
        local=local_caps[w] if local_caps is not None else [0,side*24.3,1.5 if w.startswith('XP02') else -1.5]
        target=er@np.array(local)+ec
        arrival=er@np.array([0,-side,0]);options=[]
        if np.linalg.norm(target-p)+debit>220:return None
        for ratio in (.125,.25,.5,1.,2.,4.,8.):
            try:
                arcs=ft.biarc(p,d,target,arrival,ratio)
                if ft.min_radius(arcs)>=12.4-1e-7:options.append(arc_rows(arcs))
            except (ValueError,AssertionError):pass
        try:options.append(spatial_csc(p,d,target,arrival))
        except (ValueError,AssertionError):pass
        if route_filter is not None:options=[rows for rows in options if route_filter(w,rows)]
        if not options:return None
        rows=min(options,key=lambda r:sum(s['length_mm'] for s in r))
        need=sum(s['length_mm'] for s in rows)+debit
        if need>220:return None
        routes[w]=dict(parts=rows,need_mm=need,debit_mm=debit,minimum_stock_mm=220,
                       other_end_id=e['id'],not_clearance_or_self_contact_acceptance=True)
    return routes


def xa02_corridor(start,target,arrival,trunk_bounds,usb_min_x,rr_bounds,aux_min_z,bank_max_z,R=15.,radius=1.25):
    """One dimensioned corridor round all Pi ports, not successive port fixes.

    Uses the received R47 inter-case gap56.5..65.5, the ACTUAL minimum of
    the complete occupied Pi edge, and the newly allocated comb outer face.
    These are planning datums, never a collision or stock acceptance claim.
    """
    margin=1.25;rows=[];q=np.array(start,float);d=np.array([0.,0.,1.])
    q,d=bend(rows,q,d,[1,0,0],R,math.pi/6)
    enddir=np.array([-1.,0,0]);n=enddir-d*float(enddir@d);n/=np.linalg.norm(n)
    q,d=bend(rows,q,d,n,R,2*math.pi/3)
    # Simultaneous WHOLE trunks (including heads), RR_G, G_AUX and bank.
    y_interval=[rr_bounds.YMax+radius+margin,trunk_bounds.YMin-radius-margin]
    z_interval=[bank_max_z+radius+margin,aux_min_z-radius-margin]
    assert y_interval[0]<y_interval[1] and z_interval[0]<z_interval[1]
    gallery_y=sum(y_interval)/2;gallery_z=sum(z_interval)/2
    delta=np.array([0.,gallery_y-q[1],gallery_z-q[2]])
    offset=np.linalg.norm(delta);assert 0<offset<2*R
    angle=math.acos(1-offset/(2*R))
    q,d=bend(rows,q,d,delta/offset,R,angle)
    n=enddir-d*float(enddir@d);n/=np.linalg.norm(n)
    q,d=bend(rows,q,d,n,R,angle)
    lane=[56.5+radius+margin,min(65.5,usb_min_x)-radius-margin]
    assert lane[0]<lane[1]
    x=sum(lane)/2
    q=forward(rows,q,d,q[0]-(x+R))
    q,d=bend(rows,q,d,[0,1,0],R,math.pi/2)
    target=np.array(target,float);arrival=np.array(arrival,float)
    assert abs(arrival[2])<1e-7 and arrival[0]>0 and arrival[1]<0
    a=math.asin(arrival[0]);t=np.array([math.sin(a),math.cos(a),0.])
    turn=math.pi-2*a;normal=np.array([t[1],-t[0],0.])
    arc_delta=R*math.sin(turn)*t+R*(1-math.cos(turn))*normal
    dx=R*(1-math.cos(a));dy=R*math.sin(a)
    L=(target[0]-x-dx-arc_delta[0])/t[0];assert L>0
    yturn=target[1]-dy-L*t[1]-arc_delta[1]
    travel=yturn-q[1];drop=q[2]-target[2]
    assert 0<drop<2*R
    az=math.acos(1-drop/(2*R));footprint=2*R*math.sin(az)
    straight=(travel-footprint)/2;assert straight>=0
    q=forward(rows,q,d,straight)
    q,d=bend(rows,q,d,[0,0,-1],R,az)
    north=np.array([0.,1.,0.]);n=north-d*float(north@d);n/=np.linalg.norm(n)
    q,d=bend(rows,q,d,n,R,az)
    q=forward(rows,q,d,straight)
    q,d=bend(rows,q,d,[1,0,0],R,a)
    q=forward(rows,q,d,L)
    q,d=bend(rows,q,d,normal,R,turn)
    assert np.linalg.norm(q-target)<1e-6 and np.linalg.norm(d-arrival)<1e-6
    return rows,dict(R_mm=R,profile_radius_mm=radius,foreign_margin_mm=margin,
        received_R47_gap_mm=[56.5,65.5],full_Pi_edge_min_X_mm=usb_min_x,
        simultaneous_slot_X_interval_mm=lane,slot_centre_X_mm=x,
        whole_trunk_outer_Y_mm=trunk_bounds.YMin,shared_Y_interval_mm=y_interval,
        shared_high_Z_interval_mm=z_interval,gallery_Y_mm=gallery_y,gallery_Z_mm=gallery_z,
        lower_Pi_gallery_Z_mm=float(target[2]),actual_wire_length_mm=sum(r['length_mm'] for r in rows),
        electrical_stock_and_exact_full_world_gate_OPEN=True)


def vertical_factory_plan(power_pose,power_plan,local_e2,ends,specs,plate,root,carrier):
    """Four shared corridors split at the ACTUAL battery plate edge.

    No E2 mouth coordinates rounded to24.3. Module pair stays below plate;
    source pair descends east of it. This is a single unreceived proposal.
    """
    from receive_feline_global_case_candidates import placement
    from feline_spatial_csc import spatial_csc
    R=12.4;rot=np.array([[-1.,0,0],[0,0,-1],[0,-1,0]])
    body=local_e2['Ref_Material_JPWM_0_0'];local_caps={}
    for w in ('XP02.source','XP03.source','XP02.module','XP03.module'):
        planes=[f for f in local_e2['JPWMSource:'+w].Faces if isinstance(f.Surface,Part.Plane)]
        local_caps[w]=np.array(list(max(planes,key=lambda f:(f.CenterOfMass-body.BoundBox.Center).Length).CenterOfMass))
    # Received whole-E2 field component above the plate, not the hip-blocked
    # east-edge shaft. End colour order is preserved by rigid proper rotation.
    centre=[104.,8.,68.]
    tf=placement(rot,centre);actors={}
    for n,s in local_e2.items():
        a=s.copy();a.Placement=tf*a.Placement;actors[n]=a
    caps={w:rot@p+centre for w,p in local_caps.items()};routes={}
    side_y=max(plate.BoundBox.YMax+.925+1.25,max(caps[w][1]+2*R for w in ('XP02.module','XP03.module')))
    for w in ('XP02.module','XP03.module'):
        e=next(e for e in ends if e['id']==w+'/extra/end')
        q=np.array(e['routing_exit_mm']);d=np.array(e['routing_exit_axis'],float);assert np.allclose(d,[0,1,0])
        rows=[];q=forward(rows,q,d,max(0.,root.BoundBox.YMax-q[1]))
        q,d=bend(rows,q,d,[1,0,0],R)
        offset=side_y-q[1];angle=math.acos(1-abs(offset)/(2*R))
        q,d=bend(rows,q,d,[0,np.sign(offset),0],R,angle)
        normal=np.array([1.,0,0])-d*d[0];normal/=np.linalg.norm(normal)
        q,d=bend(rows,q,d,normal,R,angle)
        q=forward(rows,q,d,caps[w][0]-R-q[0]);q,d=bend(rows,q,d,[0,0,1],R)
        dz=caps[w][2]-2*R-q[2];assert dz>=-1e-6
        q=forward(rows,q,d,max(0.,dz));q,d=bend(rows,q,d,[0,-1,0],R)
        travel=q[1]-(caps[w][1]+R);assert travel>=-1e-6
        q=forward(rows,q,d,max(0.,travel));q,d=bend(rows,q,d,[0,0,1],R)
        assert np.linalg.norm(q-caps[w])<1e-6
        bare=sum(segment(r).Length for r in specs[e['id']]['bare_parts'])
        debit=e['source_prefix_length_mm']+bare+16+9
        routes[w]=dict(parts=rows,debit_mm=debit,other_end_id=e['id'])
    pr=np.array(power_pose['rotation']);pc=np.array(power_pose['minimum_penalty_centre_mm'])
    rec=power_plan['recipes']['XP01'];q=pr@rec['output_routing_exit_mm']+pc
    d=pr@rec['output_routing_axis'];assert np.allclose(d,[1,0,0])
    rows=[];q,d=bend(rows,q,d,[0,1,0],R)
    before=caps['XP02.source']+np.array([0.,-R,R])
    delta=before-q;lateral=delta-d*float(delta@d);D=np.linalg.norm(lateral);h=float(delta@d)
    radius=(D*D+h*h)/(4*D);assert radius>=R and h>0
    angle=2*math.atan2(D,h);q,d=bend(rows,q,d,lateral/D,radius,angle)
    normal=np.array([0.,1,0])-d*d[1];normal/=np.linalg.norm(normal)
    q,d=bend(rows,q,d,normal,radius,angle);assert np.linalg.norm(q-before)<1e-6
    q,d=bend(rows,q,d,[0,0,-1],R);assert np.linalg.norm(q-caps['XP02.source'])<1e-6
    routes['XP02.source']=dict(parts=rows,debit_mm=rec['output_prefix_length_mm']+40+9,
                              other_end_id='XP02.source/extra/start')
    e=next(e for e in ends if e['id']=='XP03.source/extra/start')
    q=np.array(e['routing_exit_mm']);d=np.array(e['routing_exit_axis'],float)
    assert np.allclose(d,[0,0,1]);rows=[]
    lift=caps['XP03.source'][2]-q[2];assert lift>=0
    q=forward(rows,q,d,lift);q,d=bend(rows,q,d,[-1,0,0],R)
    q,d=bend(rows,q,d,[0,-1,0],R)
    offset=caps['XP03.source'][0]-q[0];angle=math.acos(1-abs(offset)/(2*R))
    q,d=bend(rows,q,d,[np.sign(offset),0,0],R,angle)
    normal=np.array([0.,-1,0])-d*(-d[1]);normal/=np.linalg.norm(normal)
    q,d=bend(rows,q,d,normal,R,angle)
    travel=q[1]-(caps['XP03.source'][1]+R);assert travel>=0
    q=forward(rows,q,d,travel);q,d=bend(rows,q,d,[0,0,-1],R)
    assert np.linalg.norm(q-caps['XP03.source'])<1e-6
    routes['XP03.source']=dict(parts=rows,debit_mm=32.25,other_end_id=e['id'])
    for w,r in routes.items():
        r['need_mm']=sum(s['length_mm'] for s in r['parts'])+r['debit_mm']
        r['minimum_stock_mm']=220.;assert r['need_mm']<=220.,(w,r['need_mm'])
    return actors,dict(status='VERTICAL_E2_FOUR_CONSTRUCTIVE_CORRIDORS_NOT_RECEIVED',
        E2_pose=dict(rotation=rot.tolist(),centre_mm=centre),actual_caps_mm={w:p.tolist() for w,p in caps.items()},
        routes=routes,plate_edge_X_mm=plate.BoundBox.XMax,plate_edge_Y_mm=plate.BoundBox.YMax,
        whole_module_pair_side_gallery_Y_mm=side_y,carrier_lower_plane_Z_mm=carrier.BoundBox.ZMin,
        selected_SKUs_changed=False,roots_tools_motion_outer_and_exact_contacts_OPEN=True,
        N01_complete=False,selected=False,physical_pass=False)
