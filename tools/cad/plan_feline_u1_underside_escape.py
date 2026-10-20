"""One14-mouth U1 plan: same selected through-holes, all escapes underneath.

No purchased body, board pad/net, selected wire OD or R changes. Nine old
upper local ends hit the anchors as a FAMILY. Reflect their recipes through
the REAL PCB midplane, not repeated wire/anchor offsets. Add the three
already-underside output recipes and both actual named E2 carrier pads.
This is a constructive space proposal, NOT shared/static/root acceptance.
"""
import copy,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT,BASE
from plan_feline_n01_shared import pipe
from feline_source_saddles import segment
from feline_atomic_save import save_json


def construct(board):
    tick=time.monotonic();rf=OUT/'n01-current-source-MTA-boundary-overlay.json';registry=json.loads(rf.read_text())
    assert len(registry['U1_local_prefix_source_allocations'])==9
    for p,h in registry['source_sha256'].items():assert sha(ROOT/p)==h,p
    cf=BASE/'body-harness-checkpoint/u1-socket-carrier-plan.json';carrier=json.loads(cf.read_text())
    assert carrier['board']['thickness_mm']==1.6002
    assert abs(board.BoundBox.ZLength-1.6002)<1e-5
    zsum=board.BoundBox.ZMin+board.BoundBox.ZMax;delta=A.Vector(-80,2,-107.75)
    actors={};specs={};updates={}
    def store(eid,parts,bare,radius,bradius,basis,pad,terminal):
        assert eid not in specs
        wire=eid.split('/')[0];jname='U1Under:'+wire+':jacket';bname='U1Under:'+wire+':bare'
        jacket=pipe(parts,radius);metal=pipe(bare,bradius);last=segment(parts[-1]);assert last.Length>=9-1e-6
        q=last.valueAt(last.LastParameter);d=last.tangentAt(last.LastParameter)
        seam=A.Vector(*parts[0]['start']);assert min((seam-A.Vector(*bare[i][k])).Length for i in (0,-1) for k in ('start','end'))<1e-5
        actors[jname]=jacket;actors[bname]=metal
        specs[eid]=dict(wire=wire,parts=parts,bare_parts=bare,radius_mm=radius,bare_radius_mm=bradius,
            selected_carrier_pad_identity=terminal,pad_world_mm=pad,source_basis=basis,
            physical_hole_and_solder_fit_phase2=True,external_U1_pinout_NOT_inferred=True)
        updates[eid]=dict(prefix_geometry_owner=jname,jacket_routing_point_mm=parts[0]['start'],
            routing_exit_mm=list(q),routing_exit_axis=list(d),jacket_grip9_mm=[list(q-9*d),list(q)],
            grip_length_mm=9,nominal_profile_radius_mm=radius,source_prefix_length_mm=sum(segment(p).Length for p in parts),
            physical_carrier_pad_identity_NOT_changed=True,independent_grip_root_and_world_OPEN=True,
            routing_boundary_status='WHOLE14_U1_UNDERSIDE_SPACE_PROPOSAL_NOT_RECEIVED')
    for eid,a in registry['U1_local_prefix_source_allocations'].items():
        def mirror(rows):return [dict(p,**{k:[p[k][0],p[k][1],zsum-p[k][2]] for k in ('start','mid','end') if k in p}) for p in rows]
        store(eid,mirror(a['parts']),mirror(a['bare_parts']),a['radius_mm'],a['bare_radius_mm'],
              'Same selected local recipe/length/R, underside of same PermaProto through-hole; copper layer16',
              a['pad_world_mm'],a['named_physical_source_terminal'])
    hf=BASE/'head-supply-checkpoint/plan.json';head=json.loads(hf.read_text());tf=BASE/'tail-wiring-checkpoint/selection.json';tail=json.loads(tf.read_text())
    def moved(rows):return [dict(p,**{k:list(A.Vector(*p[k])+delta) for k in ('start','mid','end') if k in p}) for p in rows]
    def prefix(rows):
        kept=[]
        for p in rows:
            assert p['kind'] in ('line','arc'),'Do not copy an old full spline middle'
            e=segment(p)
            if p['kind']=='line' and e.Length>=9:
                q=e.valueAt(e.FirstParameter)+9*e.tangentAt(e.FirstParameter);kept.append(dict(kind='line',start=p['start'],end=list(q),length_mm=9));return kept
            kept.append(copy.deepcopy(p))
        raise AssertionError('No complete9mm source grip in inherited local prefix')
    terminals={t['ref']:t for t in carrier['terminals']}
    for wire,doc,terminal in (('XS13',head,'B1.out'),('XS23',head,'B2.out'),('XS33',tail,'B3.out')):
        r=doc['routes'][wire];bare=doc['routes'][wire+'_bare'];p=terminals[terminal]
        pad=[11.59+p['x'],2+p['y'],board.BoundBox.ZMax]
        bp=moved(bare['parts']);assert abs(bp[-1]['end'][0]-pad[0])<1e-5 and abs(bp[-1]['end'][1]-pad[1])<1e-5
        store(wire+'/extra/start',moved(prefix(r['parts'])),bp,r['radius'],bare['radius'],
            'Selected local underside head/tail departure only; no old middle inherited',pad,terminal)
    ef=BASE/'pwm-branch-checkpoint/selection.json';e2=json.loads(ef.read_text())
    for wire,route,terminal,lower in (('XP02.module','XP02_module','XP02.board',0),('XP03.module','XP03_module','XP03.board',1)):
        r=e2['routes'][route];bare=e2['routes'][route+'_bare'];p=terminals[terminal]
        pad=A.Vector(11.59+p['x'],2+p['y'],board.BoundBox.ZMax)
        oldtip=A.Vector(*bare['parts'][-1]['end']);shift=pad+A.Vector(0,0,1.5)-oldtip
        bp=[dict(v,**{k:list(A.Vector(*v[k])+shift) for k in ('start','mid','end') if k in v}) for v in bare['parts']]
        # The two new named pads share Y; a3mm jacket layer pitch is required,
        # not the old2mm Z pitch (.15mm gap for two1.85mm jackets).
        if lower:
            for k in ('start','mid','end'):bp[0][k][2]-=lower
            bp[1]['start'][2]-=lower
        q=A.Vector(*bp[0]['start']);parts=[dict(kind='line',start=list(q),end=list(q+A.Vector(9,0,0)),length_mm=9)]
        store(wire+'/extra/end',parts,bp,r['radius'],bare['radius'],
            'Selected E2 local formed bare geometry aligned to actual XP02/03 carrier pad, not old IC pin; ground bare+1mm project budget',
            list(pad),terminal)
    assert len(specs)==14 and len(actors)==28
    return actors,specs,updates,dict(source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (rf,cf,hf,tf,ef,Path(__file__))},
        PCB_bottom_mm=board.BoundBox.ZMin,PCB_top_mm=board.BoundBox.ZMax,mirror_plane_Z_mm=zsum/2,
        selected_parts_changed=False,electrical_identities_changed=False,whole225mm_Molex_corridors_NOT_received=True,
        grip_common_combs_roots_tools_and_world_OPEN=True,N01_complete=False,native_changed=False,physical_pass=False,
        construction_worker_seconds=round(time.monotonic()-tick,3))


def save(board):
    actors,specs,updates,r=construct(board);dest=OUT/'n01-U1-whole14-underside-plan.json';assert not dest.exists()
    bundle=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in actors.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=n,wire=n.split(':')[1],kind=n.rsplit(':',1)[1].replace('jacket','wire'),entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    r.update(status='ONE_WHOLE14_UNDERSIDE_SOURCE_PROPOSAL_WORLD_OPEN',specs=specs,updates=updates,
        geometry=geometry,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle))
    save_json(dest,r);print(r['status'],len(actors),r['construction_worker_seconds'],flush=True)
    return r


def vertical_unit(fixed):
    """Whole-unit alternative after BOTH complete escape families failed.

    No scalar shifting of a wire. Move all145 U1 parts and6 mounting items
    by one proper rigid transform, preserving every selected internal part.
    Original lower carrier arms are explicitly replaced, not hidden blockers.
    Native bracket design and exact factory-middle routes are NOT claimed.
    """
    import Part
    from receive_feline_rrp_shared_height import load
    source=OUT/'n01-U1-whole14-underside-plan.json';r=json.loads(source.read_text());wires=load(r)
    names=[n for n in fixed if n.startswith('Ref_Material_U1_') or n.startswith('Ref_Material_PWM1608')]
    assert len(names)==151,('Whole unit ownership changed',len(names))
    board=fixed['Ref_Material_PWM1608NominalPCB_0_0'];pivot=board.BoundBox.Center
    rotation=A.Rotation(A.Vector(0,1,0),90);target=A.Vector(5,0,36)
    tf=A.Placement(target-rotation.multVec(pivot),rotation);actors={};metadata={};identity={};updates={}
    for n in names:
        old=fixed[n];s=old.copy();s.Placement=tf*s.Placement
        assert old.isValid() and s.isValid() and len(old.Solids)==len(s.Solids),n
        actors[n]=s;metadata[n]=dict(kind='unchanged_rigid_unit',unit='U1_complete',original=n)
        identity[n]=dict(original_BRep_sha256=hashlib.sha256(old.exportBrepToString().encode()).hexdigest(),
            source_volume_mm3=old.Volume,target_volume_mm3=s.Volume,one_common_proper_rigid_transform=True)
    for n,s in wires.items():
        wire=n.split(':')[1];q=s.copy();local=A.Placement()
        if wire.startswith('XP'):
            # Clock BOTH physical E2 terminations together to the Y-side of
            # their own named carrier holes: after the whole-module turn
            # these escape sideways, not down into the preserved P0 plate.
            eid=wire+'/extra/end';p=A.Vector(*r['specs'][eid]['pad_world_mm']);rot=A.Rotation(A.Vector(0,0,1),90)
            local=A.Placement(p-rot.multVec(p),rot)
        q.Placement=tf*local*q.Placement;assert q.isValid() and len(q.Solids)==1,n
        actors[n]=q;metadata[n]=dict(kind='bare' if n.endswith(':bare') else 'wire',wire=wire,unit='U1_complete')
        eid=next(k for k,v in r['specs'].items() if v['wire']==wire)
        if eid not in updates:
            u=copy.deepcopy(r['updates'][eid]);combined=tf*local
            for field in ('jacket_routing_point_mm','routing_exit_mm'):u[field]=list(combined.multVec(A.Vector(*u[field])))
            u['jacket_grip9_mm']=[list(combined.multVec(A.Vector(*p))) for p in u['jacket_grip9_mm']]
            u['routing_exit_axis']=list(combined.Rotation.multVec(A.Vector(*u['routing_exit_axis'])))
            u['point_mm']=list(tf.multVec(A.Vector(*r['specs'][eid]['pad_world_mm'])))
            u['routing_boundary_status']='WHOLE_U1_VERTICAL_JOINT_CANDIDATE_NOT_RECEIVED';updates[eid]=u
    assert len(actors)==179 and len(updates)==14
    result=dict(status='WHOLE151_U1_PLUS14ESCAPES_VERTICAL_SHARED_SPACE_PROPOSAL',
        body_ownership=names,rigid_identity=identity,body_transform_matrix=list(tf.toMatrix().A),
        source=source.relative_to(ROOT).as_posix(),source_sha256={source.relative_to(ROOT).as_posix():sha(source),
            (ROOT/r['bundle']).relative_to(ROOT).as_posix():sha(ROOT/r['bundle']),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        retired=['StructureReserve:U1CarrierArm0','StructureReserve:U1CarrierArm1'],
        retained_old_root_material='StructureReserve:U1CarrierRoot1 stays integral floor rib, not a qualified new module support',
        body_PCB_centre_mm=list(target),updates=updates,selected_parts_changed=False,internal_copper_graph_rigidly_unchanged=True,
        P0_R47_MAIN_Pi_and_JPWM_not_moved=True,bookstand_to_actual_PCB_holes_roots_tools_factory_corridors_OPEN=True,
        N01_complete=False,native_changed=False,physical_pass=False)
    return actors,metadata,result


def save_vertical(fixed):
    tick=time.monotonic();actors,metadata,r=vertical_unit(fixed);dest=OUT/'n01-U1-whole-vertical-plan.json';assert not dest.exists()
    bundle=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in actors.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(metadata[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    box=A.BoundBox()
    for n in r['body_ownership']:box.add(actors[n].BoundBox)
    r.update(bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),geometry=geometry,
        whole_rigid_unit_bounds_mm=[[box.XMin,box.YMin,box.ZMin],[box.XMax,box.YMax,box.ZMax]],
        construction_worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,r);print(r['status'],len(actors),r['construction_worker_seconds'],flush=True)
    return r


def remaining_five(fixed):
    """Keep the proven nine UPPER seats; allocate the whole other five.

    XS13 leaves north before any west bend: the former immediate west arc
    met the actual W044 cap. The E2 pair gets ONE coupled layer interval
    between actual PCB bottom and carrier-arm top, not arbitrary Z trials.
    These are local space allocations; no complete225mm route is implied.
    """
    tick=time.monotonic();f=OUT/'n01-U1-whole14-underside-plan.json';r=json.loads(f.read_text())
    dest=OUT/'n01-U1-remaining-five-coupled-plan.json';assert not dest.exists()
    pcb=fixed['Ref_Material_PWM1608NominalPCB_0_0'];arm=fixed['StructureReserve:U1CarrierArm1']
    radius=.925;bare_radius=r['specs']['XP02.module/extra/end']['bare_radius_mm']
    # The previous pair included PCB/arm and jacket/jacket but missed the
    # opposite bare fillet. Include ALL three coupled bounds, analytically.
    min_pitch=max(2*radius+.2,radius+bare_radius+1.25)
    max_pitch=pcb.BoundBox.ZMin-.2-radius-(arm.BoundBox.ZMax+1.25+radius)
    assert min_pitch<max_pitch,('No full bare/jacket/PCB/arm interval',min_pitch,max_pitch)
    pitch=(min_pitch+max_pitch)/2
    lo=arm.BoundBox.ZMax+1.25+radius+pitch
    hi=pcb.BoundBox.ZMin-.2-radius
    assert lo<hi,('No coupled E2 jacket layer interval',lo,hi)
    top=(lo+hi)/2;actors={};specs={};updates={}
    for eid in ('XS13/extra/start','XS23/extra/start','XS33/extra/start','XP02.module/extra/end','XP03.module/extra/end'):
        old=r['specs'][eid];s=copy.deepcopy(old);parts=s['parts'];bare=s['bare_parts'];wire=s['wire']
        if wire=='XS13':
            q=A.Vector(*parts[0]['start']);parts=[dict(kind='line',start=list(q),end=list(q+A.Vector(0,9,0)),length_mm=9)]
        elif wire.startswith('XP'):
            level=top if wire=='XP02.module' else top-pitch
            dz=level-parts[0]['start'][2]
            for p in parts:
                for k in ('start','mid','end'):
                    if k in p:p[k][2]+=dz
            for k in ('start','mid','end'):bare[0][k][2]+=dz
            bare[1]['start'][2]+=dz
            s['source_basis']='Same named carrier pad and formed R1 tail; coupled PCB/arm clearance interval, project strip length, not supplier tolerance'
        s['parts']=parts;s['bare_parts']=bare;specs[eid]=s
        for kind,recipe,rad in (('jacket',parts,s['radius_mm']),('bare',bare,s['bare_radius_mm'])):
            name='U1Five:'+wire+':'+kind;shape=pipe(recipe,rad)
            assert shape.isValid() and len(shape.Solids)==1;actors[name]=shape
        last=segment(parts[-1]);assert last.Length>=9-1e-6
        q=last.valueAt(last.LastParameter);d=last.tangentAt(last.LastParameter)
        updates[eid]=dict(r['updates'][eid],prefix_geometry_owner='U1Five:'+wire+':jacket',
            jacket_routing_point_mm=parts[0]['start'],routing_exit_mm=list(q),routing_exit_axis=list(d),
            jacket_grip9_mm=[list(q-9*d),list(q)],source_prefix_length_mm=sum(segment(p).Length for p in parts),
            routing_boundary_status='REMAINING_FIVE_WITH_PROVEN_UPPER_NINE_SHARED_PLAN_PENDING')
    bundle=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in actors.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=n,wire=n.split(':')[1],kind='bare' if n.endswith(':bare') else 'wire',entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result=dict(status='U1_NINE_ORIGINAL_PLUS_FIVE_COUPLED_LOCAL_SPACE_PLAN_NOT_RECEIVED',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (f,Path(__file__),OUT/'n01-U1-intrinsic-mates-reconciled.json')},
        specs=specs,updates=updates,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),geometry=geometry,
        coupled_E2_upper_centre_interval_mm=[lo,hi],E2_jacket_centres_Z_mm=[top,top-pitch],E2_layer_pitch_mm=pitch,
        coupled_E2_pitch_interval_mm=[min_pitch,max_pitch],
        prior_rejected_pair='U1Five:XP03.module:jacket|U1Five:XP02.module:bare gap1.1689402494<1.25; no gap waiver',
        unchanged_upper_prefixes=9,selected_parts_or_pad_identities_changed=False,full_factory_corridors_grips_roots_assembly_motion_OPEN=True,
        N01_complete=False,native_changed=False,physical_pass=False,construction_worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],len(actors),result['construction_worker_seconds'],flush=True)
    return result
