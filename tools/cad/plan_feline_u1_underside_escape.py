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
