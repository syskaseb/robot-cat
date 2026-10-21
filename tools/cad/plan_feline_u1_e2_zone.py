"""Complete received U1 and E2 as one functional zone, in the actual PCB datum.

No board pinout, stock length, world pose or production mount is inferred here.
Only the two newly changed module links and eleven E2 actors need intrinsic
checks against the 197 retained U1 pieces. Whole-world reception remains open.
"""
import math
import time
import numpy as np
import FreeCAD as A
from feline_tangent_routes import biarc, min_radius
from plan_feline_coupled_rear_power import arc_rows
from plan_feline_n01_shared import pipe
from receive_feline_underplate_return_gallery import forward
from receive_feline_global_case_candidates import placement
from feline_source_saddles import segment


def local_pair(u1_local, e2_local, ends, pivot, specs):
    assert len(u1_local) == 197 and len(e2_local) == 11
    module = {e['wire']: e for e in ends
              if e.get('group') == 'PWM1608_U1' and e['wire'].startswith('XP')}
    assert set(module) == {'XP02.module', 'XP03.module'}
    points = {w: np.asarray(e['routing_exit_mm']) - np.asarray(pivot)
              for w, e in module.items()}
    assert all(np.allclose(e['routing_exit_axis'], [0, 1, 0]) for e in module.values())
    centre = [points['XP02.module'][0], 40.,
              (points['XP02.module'][2] + points['XP03.module'][2])/2]
    rotation = np.diag([-1., -1., 1.])
    tf = placement(rotation, centre)
    changed = {}
    for n, s in e2_local.items():
        a = s.copy(); a.Placement = tf*a.Placement; changed[n] = a
    # Clock the COMPLETE module-side clamp outward, not toward the PCB edge.
    # Both symmetric jacket lands remain the same pair; head is not reduced.
    clamp_clock = A.Placement(A.Vector(*centre), A.Rotation(A.Vector(0,1,0),180))
    clamp_clock = clamp_clock*A.Placement(-A.Vector(*centre), A.Rotation())
    for n in ('JPWMGrip:module:pad', 'JPWMGrip:module:band', 'JPWMGrip:module:head'):
        changed[n].Placement = clamp_clock*changed[n].Placement
    body = e2_local['Ref_Material_JPWM_0_0']
    caps = {}
    for w in ('XP02.source', 'XP03.source', 'XP02.module', 'XP03.module'):
        faces = [f for f in e2_local['JPWMSource:'+w].Faces
                 if f.Surface.__class__.__name__ == 'Plane']
        p = max(faces, key=lambda f: (f.CenterOfMass-body.BoundBox.Center).Length).CenterOfMass
        caps[w] = np.asarray(list(tf.multVec(p)))
    routes = {}
    for w, e in module.items():
        rows = []
        # The received RearRoot extends three mm past the present cable cap.
        q = forward(rows, points[w], [0, 1, 0], 3.)
        curve = biarc(q, [0, 1, 0], caps[w], [0, 1, 0])
        assert min_radius(curve) >= 12.4
        rows += arc_rows(curve)
        n = 'U1E2Link:'+w
        changed[n] = pipe(rows, .925)
        bare = sum(segment(r).Length for r in specs[e['id']]['bare_parts'])
        debit = e['source_prefix_length_mm'] + bare + 16 + 9
        need = debit + sum(r['length_mm'] for r in rows)
        assert need <= 220
        routes[w] = dict(parts=rows, minimum_R_mm=min_radius(curve),
                         factory_debit_mm=debit, required_factory_mm=need,
                         available_lower_mm=220, other_end_id=e['id'])
    for n, s in changed.items():
        assert s.isValid() and len(s.Solids) == 1, n
    return changed, dict(
        status='COMPLETE_U1_E2_LOCAL_ZONE_PROPOSAL_NOT_SELECTED',
        actual_PCB_pivot_world_mm=list(pivot), received_U1_actors=list(u1_local),
        E2_PCB_local_pose=dict(rotation=rotation.tolist(), centre_mm=centre),
        complete_module_clamp_clock_deg=180,
        E2_caps_PCB_local_mm={w: p.tolist() for w, p in caps.items()},
        routes=routes, all14_U1_interfaces_must_transform_once=True,
        old_carrier_arms_NOT_qualified_at_new_pose=True,
        world_roots_tools_motion_and_all_external_routes_OPEN=True,
        selected_SKUs_changed=False, N01_complete=False, physical_pass=False)


def intrinsic(u1_local, changed):
    tick = time.monotonic(); checks = {}; failures = []
    for n, s in changed.items():
        for k, t in u1_local.items():
            b = s.BoundBox; c = t.BoundBox
            lower = math.sqrt(sum(max(0., a-d, e-f)**2 for a,d,e,f in (
                (b.XMin,c.XMax,c.XMin,b.XMax),
                (b.YMin,c.YMax,c.YMin,b.YMax),
                (b.ZMin,c.ZMax,c.ZMin,b.ZMax))))
            if lower >= 1.25: continue
            gap = s.distToShape(t)[0]; minimum = 1.25; reason = 'foreign'
            wire = n.removeprefix('U1E2Link:')
            if n.startswith('U1E2Link:') and k == 'U1Five:'+wire+':jacket':
                minimum = 0.; reason = 'own exact continuation face'
                assert gap < 1e-6
                assert s.common(t).Volume < 1e-5
            elif n.startswith('U1E2Link:') and k == 'U1Relief:RearRoot':
                minimum = 0.; reason = 'existing named own jacket seat policy; positive gap and zero volume required'
                assert s.common(t).Volume < 1e-5
            elif n.startswith('U1E2Link:') and k in ('U1Five:XP02.module:jacket', 'U1Five:XP03.module:jacket'):
                minimum = .2; reason = 'received insulated paired-jacket policy'
            ok = gap >= minimum-1e-6
            key = n+'|'+k
            checks[key] = dict(gap_mm=gap, minimum_mm=minimum, reason=reason, ok=ok)
            if not ok: failures.append(key)
    # E2's eleven retained actors are a rigid unit. Only new links add pairs.
    names = list(changed)
    for n in [n for n in names if n.startswith('U1E2Link:')]:
        s = changed[n]; wire = n.split(':',1)[1]
        for k, t in changed.items():
            if k == n or k.startswith('U1E2Link:') and k < n: continue
            gap = s.distToShape(t)[0]; minimum = 1.25; reason = 'foreign'
            if k == 'JPWMSource:'+wire:
                minimum = 0.; reason = 'own exact continuation face'
                assert gap < 1e-6 and s.common(t).Volume < 1e-5
            elif k == 'U1E2Link:'+('XP03.module' if wire=='XP02.module' else 'XP02.module'):
                minimum = .2; reason = 'separate insulated members of paired link'
            elif k in ('JPWMSource:XP02.module', 'JPWMSource:XP03.module'):
                minimum = .2; reason = 'received insulated paired-jacket policy'
            elif k == 'JPWMGrip:module:pad':
                minimum = 0.; reason = 'existing own jacket seat at continuation; no volume contact'
                assert s.common(t).Volume < 1e-5
            key = n+'|'+k; ok = gap >= minimum-1e-6
            checks[key] = dict(gap_mm=gap, minimum_mm=minimum, reason=reason, ok=ok)
            if not ok: failures.append(key)
    # The module-side clamp alone was clocked; it is NOT covered by the old
    # E2 rigid-unit receipt against the other eight members.
    clocked = {n for n in changed if n.startswith('JPWMGrip:module:')}
    for n in clocked:
        for k, t in changed.items():
            if k in clocked or k.startswith('U1E2Link:'): continue
            gap = changed[n].distToShape(t)[0]; minimum = 1.25
            reason = 'changed complete clamp versus retained E2 unit'
            if k in ('JPWMSource:XP02.module','JPWMSource:XP03.module'):
                minimum = .2 if n.endswith(':head') else 0.
                reason = 'own insulated paired jacket clamp'
                if minimum == 0.: assert changed[n].common(t).Volume < 1e-5
            key = n+'|'+k; ok = gap >= minimum-1e-6
            checks[key] = dict(gap_mm=gap,minimum_mm=minimum,reason=reason,ok=ok)
            if not ok: failures.append(key)
    return dict(status='LOCAL_U1_E2_INTRINSIC_HOLD' if failures else 'LOCAL_U1_E2_INTRINSIC_RECEIVED',
                checks=checks, failures=failures, reused_U1_intrinsic_actors=197,
                reused_E2_intrinsic_actors=11, worker_seconds=round(time.monotonic()-tick,3),
                world_contact_and_assembly_NOT_received=True, physical_pass=False)


def factory_rank(rotation, centres, caps, network_ids, origin, costs, debits, outward_local=(0.,1.,0.)):
    """Rank the whole zone using the TWO fixed source maps already received.

    The two module leads are inside the received local zone. Goal links and
    capacity still require actual curves; this is only a conservative proposal.
    """
    from plan_feline_tangent_corridor_network import DIRECTIONS
    worst = np.zeros(len(centres))
    outward = rotation@np.asarray(outward_local)
    heading = int(np.argmax(DIRECTIONS@(-outward)))
    for w in ('XP02.source', 'XP03.source'):
        targets = centres + np.asarray(caps[w])@rotation.T
        best = np.full(len(centres), np.inf)
        for offset in (8.,16.,24.,32.):
            indices = np.rint((targets+offset*outward-origin)/4).astype(int)
            inside = np.all((indices >= 0)&(indices < np.array(network_ids.shape)),axis=1)
            ix = np.flatnonzero(inside)
            node = network_ids[tuple(indices[ix].T)]
            valid = node >= 0; ix = ix[valid]; node = node[valid]
            positions = origin+4*indices[ix]
            length = costs[w][node*6+heading]+np.linalg.norm(positions-targets[ix],axis=1)+debits[w]
            best[ix] = np.minimum(best[ix],length)
        worst = np.maximum(worst,best)
    return worst


def independent_case_rank(rotation,centres,body_corners,module_caps,cases,return_ids=False):
    """One JOINT necessary-budget filter; E2 is not bolted rigidly to U1.

    Case rows carry whole11 clear-domain witnesses and both fixed-source
    debits. A box separation is sufficient proposal evidence, never a contact
    diagnosis or a global impossibility proof. All fourteen ports remain open.
    """
    corners=np.asarray(body_corners)@rotation.T;lo=corners.min(0);hi=corners.max(0)
    score=np.full(len(centres),np.inf);chosen=np.full(len(centres),-1,int)
    elo=np.asarray([c['low_mm'] for c in cases]);ehi=np.asarray([c['high_mm'] for c in cases])
    source=np.asarray([c['fixed_source_necessary_mm'] for c in cases])
    for start in range(0,len(centres),512):
        cs=centres[start:start+512]
        separate=np.any((cs[:,None,:]+hi+1.25<=elo[None,:,:])|
                        (cs[:,None,:]+lo-1.25>=ehi[None,:,:]),axis=2)
        costs=np.broadcast_to(source,(len(cs),len(cases))).copy()
        for w,prefix_debit in (('XP02.module',49.3036058414),('XP03.module',54.4841357167)):
            p=cs+np.asarray(module_caps[w])@rotation.T
            targets=np.asarray([c['module_caps'][w] for c in cases])
            costs=np.maximum(costs,np.linalg.norm(p[:,None,:]-targets[None,:,:],axis=2)+prefix_debit)
        costs[~separate]=np.inf
        j=np.argmin(costs,axis=1);value=costs[np.arange(len(cs)),j]
        score[start:start+len(cs)]=value;chosen[start:start+len(cs)]=j
    return (score,chosen) if return_ids else score


def common_three_output_fan(fixed,specs):
    """Three named existing pads, one underside plane and one rooted comb.

    Input/output remains in the old U1 world frame. Apply the chosen PCB
    transform ONCE afterwards. Strip length is a project fitting value, not
    manufacturer data or an instruction to cut before delivery.
    """
    from plan_feline_u1_common_restraints import open_seat
    from feline_source_restraint_plan import box,joined
    pcb=fixed['Ref_Material_PWM1608NominalPCB_0_0'];stand=fixed['U1Relief:Stand0']
    radius=1.05;R=12.6;plane=pcb.BoundBox.ZMin-.2-radius
    actors={};routes={};ties=[];centres=(-3.03,4.97,10.97);prefixes={}
    gallery=pcb.BoundBox.YMax+radius+1.25
    for w,x in zip(('XS13','XS23','XS33'),centres):
        source=specs[w+'/extra/start'];sx,sy,_=source['parts'][0]['start']
        # Splay the formed BARE lead before insulation starts. The fixed2.54mm
        # pad pitch cannot accommodate two1.05mm jackets and a foreign bare
        # margin on the same parallel transition; moving a grip cannot fix it.
        sign=0 if w=='XS23' else (-1 if w=='XS13' else 1)
        # Parallel jacket gallery first, spread only beyond the whole PCB.
        # Formed bare biarcs preserve the three named pad axes; no resistor
        # tail or retained local bare lead is moved to make the fan fit.
        initial=0.;d=np.array([0.,1.,0.])
        start=np.array([sx+sign*.6,sy+.6,plane]);rows=[]
        p=forward(rows,start,d,gallery-start[1]);dx=x-p[0]
        peak=math.acos(1-abs(dx)/(2*R))
        from receive_feline_underplate_return_gallery import bend
        sign=math.copysign(1.,dx)
        normal=np.array([sign*math.cos(initial),-math.sin(initial),0.])
        p,d=bend(rows,p,d,normal,R,peak-initial)
        normal=np.array([0.,1,0])-d*d[1];normal/=np.linalg.norm(normal)
        p,d=bend(rows,p,d,normal,R,peak)
        pad=np.array([sx,sy-1,plane+1.5])
        bare_curve=biarc(start,[0,-1,0],pad,[0,0,1]);assert min_radius(bare_curve)>=1
        bare=arc_rows(bare_curve)+[dict(kind='line',start=pad.tolist(),end=source['bare_parts'][-1]['end'])]
        prefixes[w]=(rows,p,d,bare)
    land_start=max(p[1] for _,p,_,_ in prefixes.values());land_end=land_start+9
    for w,x in zip(('XS13','XS23','XS33'),centres):
        source=specs[w+'/extra/start'];rows,p,d,bare=prefixes[w]
        p=forward(rows,p,d,land_start-p[1]);p=forward(rows,p,d,9.)
        assert np.linalg.norm(p-[x,land_end,plane])<1e-6
        actors['U1Five:'+w+':jacket']=pipe(rows,radius)
        actors['U1Five:'+w+':bare']=pipe(bare,source['bare_radius_mm'])
        kit=open_seat([x,land_start,plane],[0,1,0],[0,0,1],radius)
        for k in ('band','head'):
            actors['U1Relief:'+w+':'+k]=kit[k];ties.append(kit[k])
        routes[w]=dict(parts=rows,bare_parts=bare,named_pad=source['selected_carrier_pad_identity'],
            pad_world_mm=source['pad_world_mm'],full9_mm=[[x,land_start,plane],[x,land_end,plane]],
            source_prefix_length_mm=sum(segment(r).Length for r in rows),
            nominal_bare_mm=sum(segment(r).Length for r in bare),delivered_solder_and_strip_fit_OPEN=True)
    # Solid common backing; three complete independent ribbon/head kits.
    x0=centres[0]-radius;x1=centres[-1]+radius;z0=plane+radius;z1=z0+2
    comb=box([x0,land_start,z0],[x1,land_end,z1])
    for n,s in actors.items():
        if n.endswith(':band'):comb=comb.cut(s.makeOffsetShape(.2,1e-6))
    sb=stand.BoundBox;bx0=sb.XMin;bx1=sb.Center.x;by=sb.Center.y
    # Route below the existing stand, then OUTSIDE the PCB edge. The earlier
    # near-PCB beam crossed real header tails; do not nibble around each pin.
    outside=pcb.BoundBox.XMin-3.25
    low=sb.ZMin+1
    root=joined([comb,
        box([sb.XMin,sb.YMin,low],[sb.XMax,sb.YMax,low+2]),
        box([outside,by-1.2,low],[bx1+1.2,by+1.2,low+2]),
        box([outside,by-1.2,low],[outside+2,land_end,low+2]),
        box([outside,land_end-2,low],[outside+2,land_end,z1]),
        box([outside,land_end-2,z0],[x1,land_end,z1])])
    import Part
    bore=min(f.Surface.Radius for f in stand.Faces if isinstance(f.Surface,Part.Cylinder))
    hole=Part.makeCylinder(bore,30,A.Vector(sb.Center.x,sb.Center.y,pcb.BoundBox.ZMin-20))
    root=root.cut(hole).removeSplitter();assert root.isValid() and len(root.Solids)==1
    joint=root.common(stand).Volume;assert joint>1e-5
    assert len(root.fuse(stand).Solids)==1
    actors['U1Relief:ForeRoot']=root
    for n,s in actors.items():assert s.isValid() and len(s.Solids)==1,n
    retired=[n for n in fixed if n=='U1Relief:ForeRoot' or
             any(n.startswith('U1Relief:'+w+':') or n in ('U1Five:'+w+':jacket','U1Five:'+w+':bare')
                 for w in routes)]
    return actors,dict(status='COMMON_THREE_U1_OUTPUT_PLAN_NOT_RECEIVED',routes=routes,
        retired=retired,common_jacket_plane_old_world_Z_mm=plane,minimum_project_R_mm=R,
        parallel_gallery_until_old_world_Y_mm=gallery,common_land_old_world_Y_mm=[land_start,land_end],
        radius_mm=radius,three_full_independent_T18I=True,Stand0_positive_joint_mm3=joint,
        Stand0_bore_preserved_mm=bore,new_PCB_holes=False,new_pinout=False,
        all_other_U1_ports_geometry_unchanged=True,world_contacts_and_all14_roots_OPEN=True,
        N01_complete=False,physical_pass=False)


def receive_common_fan(fixed,changed,plan,metadata,carrier):
    """Changed interfaces only; retain named holes and zero-volume seat rules."""
    import Part
    from feline_solid_distance import bbox_lower_bound
    from receive_feline_u1_common_restraints import minimum
    tick=time.monotonic();checks={};failures=[]
    retained={n:s for n,s in fixed.items() if n not in plan['retired']}
    scene={**retained,**changed};md=dict(metadata)
    own={n for n in retained if n.startswith(('Ref_Material_U1_','Ref_Material_PWM1608'))}
    seats={'U1Relief:ForeRoot':['U1Five:'+w+':jacket' for w in plan['routes']]}
    for w in plan['routes']:
        seats['U1Relief:'+w+':band']=['U1Five:'+w+':jacket']
    policy=dict(intended_insulation_mates=seats,
        named_grip_air_gaps={'U1Relief:ForeRoot':[n for n in changed if n.endswith((':band',':head'))]})
    groups={'root':{'U1Relief:ForeRoot','U1Relief:Stand0'}}
    for n in changed:
        if n.startswith('U1Five:'):
            md[n]=dict(wire=n.split(':')[1],kind='bare' if n.endswith(':bare') else 'wire')
        else:md[n]=dict(kind='PETG' if n.endswith('Root') else 'T18I')
    drills=[p for g in carrier['board']['groups'] for p in g['pads']]
    holes={}
    for n,s in changed.items():
        for k,t in scene.items():
            if k==n or k in changed and k>=n:continue
            limit,reason=minimum(n,k,md,policy,groups,own)
            if limit is None or bbox_lower_bound(s.BoundBox,t.BoundBox)>limit+1e-6:continue
            other=t
            if k=='Ref_Material_PWM1608NominalPCB_0_0' and n.endswith(':bare'):
                w=n.split(':')[1];x,y,_=plan['routes'][w]['pad_world_mm'];bb=t.BoundBox;c=bb.Center
                matches=[p for p in drills if abs(c.x+float(p['x'])-x)<1e-5 and abs(c.y+float(p['y'])-y)<1e-5]
                assert len(matches)==1 and abs(float(matches[0]['drill'])-1.2)<1e-6
                other=t.cut(Part.makeCylinder(.6,bb.ZLength+.2,A.Vector(x,y,bb.ZMin-.1)))
                assert other.isValid()
                holes[w]=dict(pad=plan['routes'][w]['named_pad'],drill_mm=1.2,delivered_fit_OPEN=True)
            gap=s.distToShape(other)[0];ok=gap>=limit-1e-6
            row=dict(gap_mm=gap,minimum_mm=limit,reason=reason,ok=ok)
            if limit==0:
                row['common_mm3']=s.common(other).Volume;row['ok'] &= row['common_mm3']<1e-5
            checks[n+'|'+k]=row
            if not row['ok']:failures.append(n+'|'+k)
    return dict(status='COMMON_U1_THREE_FAN_INTRINSIC_HOLD' if failures else 'COMMON_U1_THREE_FAN_INTRINSIC_RECEIVED',
        checks=checks,failures=failures,named_nominal_holes=holes,
        Stand0_positive_integral_joint_mm3=plan['Stand0_positive_joint_mm3'],
        changed_actors=len(changed),retained_actors=len(retained),
        worker_seconds=round(time.monotonic()-tick,3),world_and_motion_OPEN=True,physical_pass=False)
