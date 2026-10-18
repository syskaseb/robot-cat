"""One complete horizontal PWM board owner beside the fore S1 bay.

N01 planning solids, not native manufacturing release. Preserve all15 purchased
parts, actual7 bare ends and four complete fastener stacks. One top-hung frame
and two shared channelled restraints replace individual cylindrical clamps.
No selected source/master save, no altered supplier pinout or purchased SKU.
"""
import hashlib
import itertools
import json
import math
import sys
import time
import zipfile
from pathlib import Path

import FreeCAD as A
import Part
import numpy as np

from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from plan_feline_front_bulkhead_architecture import tube
from feline_solid_distance import distance, bbox_lower_bound


def box(lo, hi):
    assert all(b > a for a, b in zip(lo, hi)), (lo, hi)
    return Part.makeBox(*(b-a for a, b in zip(lo, hi)), A.Vector(*lo))


def route(q, d, b, first, radius, jacket, run=0):
    q, d, b = (A.Vector(*p) for p in (q, d, b))
    a = q+d*first
    mid = a+d*(radius/math.sqrt(2))+b*(radius*(1-1/math.sqrt(2)))
    end = a+d*radius+b*radius
    edges = [Part.makeLine(q, a), Part.Arc(a, mid, end).toShape()]
    if run:
        edges.append(Part.makeLine(end, end+b*run))
    grip = end+b*run
    edges.append(Part.makeLine(grip, grip+b*9))
    return tube(Part.Wire(edges), jacket), list(grip), list(grip+b*9)


def comb(parts, kinds, prefix, rows, axis):
    """Separate lower saddle/lid, full wrap budget and head; own grooves.

    0.15mm channel clearance and2mm wall are provisional PETG-fit assumptions.
    One common band retains the lid; each conductor has its own9mm groove.
    """
    qs = np.array([r['grip_start_mm'] for r in rows]); rr = np.array([r['jacket_radius_mm'] for r in rows])
    tips = np.array([r['grip_end_mm'] for r in rows]); allp = np.vstack((qs-rr[:, None], tips+rr[:, None]))
    lo, hi = allp.min(0), allp.max(0)
    lo[axis] = min(qs[:, axis].min(), tips[:, axis].min())
    hi[axis] = max(qs[:, axis].max(), tips[:, axis].max())
    # Width is transverse XY; height Z. Keep full axial9mm land, not11mm.
    transverse = 1-axis
    lo[transverse] -= 2; hi[transverse] += 2
    lo[2] -= 2; hi[2] += 2
    z = float(qs[0, 2]); assert np.max(np.abs(qs[:, 2]-z)) < 1e-6
    lower = box(lo, [hi[0], hi[1], z]); upper = box([lo[0], lo[1], z], hi)
    for row in rows:
        q = A.Vector(*row['grip_start_mm']); tip = A.Vector(*row['grip_end_mm'])
        d = tip-q; d.normalize()
        channel = Part.makeCylinder(row['jacket_radius_mm']+.15, 9.02, q-d*.01, d)
        lower = lower.cut(channel); upper = upper.cut(channel)
    lowband, highband = lo.copy(), hi.copy()
    lowband[axis] = (lo[axis]+hi[axis])/2-1.25
    highband[axis] = lowband[axis]+2.5
    lowband[transverse] -= 1.2; highband[transverse] += 1.2
    lowband[2] -= 1.2; highband[2] += 1.2
    outer = box(lowband, highband)
    holelo, holehi = lo.copy(), hi.copy()
    holelo[axis] -= .1; holehi[axis] += .1
    band = outer.cut(box(holelo, holehi))
    h = (lo+hi)/2
    h[transverse] = highband[transverse]+3
    for n, s in (('lower', lower), ('lid', upper), ('band_budget', band), ('head_budget', box(h-3, h+3))):
        name = prefix+':'+n
        assert s.isValid() and s.Solids, name
        parts[name] = s; kinds[name] = dict(kind='restraint', owner=prefix, intended_wires=[r['wire'] for r in rows])
    return lo, hi


def source_inputs():
    """Fast source-only constructor test, before the complete scene is loaded."""
    from plan_feline_front_service_split import line_tube
    path=OUT/'n01-full-material-scene.json'; doc=json.loads(path.read_text())
    bundle=ROOT/doc['bundle']; assert sha(bundle)==doc['bundle_sha256']
    p=json.loads((OUT/'n01-coupled-allocation-plan.json').read_text())['PWM9685']
    rot=A.Rotation(A.Vector(0,1,0),90)
    tf=A.Placement(A.Vector(*p['target_PCB_bottom_datum_mm'])-rot.multVec(A.Vector(*p['source_PCB_bottom_datum_mm'])),rot)
    scene={};meta={}
    with zipfile.ZipFile(bundle) as archive:
        for row in doc['parts']:
            if row.get('role')!='PWM9685' and row['name']!='Ref_Material_S0_key_CP2_0_0':continue
            blob=archive.read(row['entry']);assert hashlib.sha256(blob).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(blob.decode())
            if row.get('role')=='PWM9685':s.Placement=tf*s.Placement
            scene[row['name']]=s;meta[row['name']]=row
    boundary=json.loads((OUT/'n01-solder-boundary-allocation.json').read_text())
    for row in boundary['ends']:
        for i,seg in enumerate(row['bare_segments']):
            n='REV3:PCA:'+row['wire']+':bare'+str(i)
            scene[n]=line_tube(seg['start'],seg['end'],row['bare_radius_project_mm']);meta[n]=dict(kind='bare')
    return scene,meta


def build(scene, meta):
    source = json.loads((OUT/'n01-source-saddles-whole-joint.json').read_text())
    receipt = source['hard_source_motion_receiver']
    assert len(receipt['completed_sources']) == 10 and receipt['first_failure'] is None
    # The S1 snapshot belongs to the nested hard-motion receipt, not the parent.
    sourceparts = {}
    with zipfile.ZipFile(ROOT/receipt['bundle']) as z:
        assert sha(ROOT/receipt['bundle']) == receipt['bundle_sha256']
        for row in receipt['parts']:
            blob = z.read(row['entry']); assert hashlib.sha256(blob).hexdigest() == row['sha256']
            s = Part.Shape(); s.importBrepFromString(blob.decode()); sourceparts[row['name']] = s
    z = sourceparts['Ref_Material_current_S1_body_CP2_0_0'].BoundBox.ZMax+1.25
    planpath = OUT/'n01-coupled-allocation-plan.json'; plan = json.loads(planpath.read_text())['PWM9685']
    oldrot = A.Rotation(A.Vector(0, 1, 0), 90)
    old = A.Placement(A.Vector(*plan['target_PCB_bottom_datum_mm'])-oldrot.multVec(A.Vector(*plan['source_PCB_bottom_datum_mm'])), oldrot)
    # Entire PCB clear of the actual S0 key; NOT a wire/nut offset retry.
    key=scene['Ref_Material_S0_key_CP2_0_0']
    target = A.Vector(key.BoundBox.XMax+1.25+62.23/2, -51, z)
    new = A.Placement(target-A.Vector(*plan['source_PCB_bottom_datum_mm']), A.Rotation())
    relative = new*old.inverse()
    oldnames = [n for n in scene if meta[n].get('role') == 'PWM9685']
    # Four screws+nuts+bottom washers, TWO top washers, one PCB =15, not17.
    assert len(oldnames) == 15, oldnames
    holes = [target+A.Vector(x, y, 0) for x, y in itertools.product((-27.94, 27.94), (-9.525, 9.525))]
    parts = {}; kinds = {}; hwgroups = [[] for _ in holes]
    for n in oldnames:
        s = scene[n].copy(); s.Placement = relative*s.Placement
        board = 'PCB' in n
        if not board:
            h = min(range(4), key=lambda i: math.hypot(s.BoundBox.Center.x-holes[i].x, s.BoundBox.Center.y-holes[i].y))
            assert math.hypot(s.BoundBox.Center.x-holes[h].x, s.BoundBox.Center.y-holes[h].y) < .01, n
            cr = A.Rotation(A.Vector(1, 0, 0), 180); pivot = holes[h]+A.Vector(0, 0, .8)
            s.Placement = A.Placement(pivot-cr.multVec(pivot), cr)*s.Placement
            hwgroups[h].append(n)
        assert s.isValid() and s.Solids, n
        parts[n] = s; kinds[n] = dict(kind='board' if board else 'fastener', owner='PWM9685')
    assert sum(k['kind'] == 'board' for k in kinds.values()) == 1
    assert all(len(g) >= 3 for g in hwgroups)
    # Full underside hardware, not just PCB, sets the shelf datum. Derive
    # once from selected screws; never chase their local collision by offsets.
    underside=min(s.BoundBox.ZMin for s in parts.values())
    lift=max(0,sourceparts['Ref_Material_current_S1_body_CP2_0_0'].BoundBox.ZMax+1.25-underside)
    if lift:
        for s in parts.values():s.translate(A.Vector(0,0,lift))
        relative.Base=relative.Base+A.Vector(0,0,lift)
        target.z+=lift;z+=lift
    assert min(s.BoundBox.ZMin for s in parts.values())>=sourceparts['Ref_Material_current_S1_body_CP2_0_0'].BoundBox.ZMax+1.25-1e-6
    boundarypath = OUT/'n01-solder-boundary-allocation.json'
    boundary = json.loads(boundarypath.read_text()); recipes = []
    for row in boundary['ends']:
        wire = row['wire']; q = relative.multVec(A.Vector(*row['jacket_mouth_world_mm']))
        d = relative.Rotation.multVec(A.Vector(*row['jacket_departure_axis']))
        assert (d-A.Vector(0, 0, 1)).Length < 1e-6
        small = wire.startswith('XS'); radius = row['minimum_fixed_project_R_mm'] if small else max(10, row['minimum_fixed_project_R_mm'])
        # Custom insulated mouth already2.6mm above PCB; 1.5mm transition
        # before R10 is project geometry, NOT a supplier first3/9mm rule.
        bend = (0, -1, 0) if small else (1, 0, 0); first = 1.5
        jacket, grip, tip = route(q, d, bend, first, radius, row['first_jacket_radius_mm'], 6.5 if small else 0)
        name = 'ShelfPWM:jacket:'+wire; parts[name] = jacket; kinds[name] = dict(kind='wire', owner=wire)
        for i, seg in enumerate(row['bare_segments']):
            n = 'REV3:PCA:'+wire+':bare'+str(i); s = scene[n].copy(); s.Placement = relative*s.Placement
            parts[n] = s; kinds[n] = dict(kind='bare', owner=wire)
        recipes.append(dict(wire=wire, jacket_mouth_world_mm=list(q), departure_axis=list(d), bend_unit=list(bend),
                            first_straight_project_mm=first, R_mm=radius, minimum_inherited_R_mm=row['minimum_fixed_project_R_mm'],
                            jacket_radius_mm=row['first_jacket_radius_mm'], grip_start_mm=grip, grip_end_mm=tip,
                            after_arc_extra_straight_mm=6.5 if small else 0, bare_segments_preserved=True))
    xl = [r for r in recipes if r['wire'].startswith('XL')]; xs = [r for r in recipes if r['wire'].startswith('XS')]
    assert len(xl) == 4 and len(xs) == 3
    xllo, xlhi = comb(parts, kinds, 'ShelfPWM:XLcomb', xl, 0)
    xslo, xshi = comb(parts, kinds, 'ShelfPWM:XScomb', xs, 1)
    pieces = []
    for h in holes:
        post = Part.makeCylinder(2, 8, h+A.Vector(0, 0, 1.6))
        post = post.cut(Part.makeCylinder(1.2, 8.02, h+A.Vector(0, 0, 1.59)))
        pieces.append(post)
    fore=min(h.x for h in holes);rear=max(h.x for h in holes)
    # First R1 nominal25mm tool at X[-47.5,-22.5]. Root remains BEFORE
    # this whole access lane, also behind MountFrontRight rearX-57.5.
    rootx=-47.5-1.25-3
    for y in (-60.525, -41.475):
        pieces.append(box([fore-2, y-2, z+6.6], [rear+2, y+2, z+9.6]))
    for x in (rootx, xllo[0]+1, xlhi[0]-1):
        pieces.append(box([x-2, -62.525, z+6.6], [x+2, -39.475, z+9.6]))
    pieces.append(box([fore-2, -65.525, z+9.5], [rear+2, -62.525, z+15.6]))
    # XL lower saddle directly rests on a bridge; lid remains removable.
    pieces.append(box([xllo[0], xllo[1], xllo[2]-1.9], [xlhi[0], xlhi[1], xllo[2]+.1]))
    for x in (xllo[0]+1, xlhi[0]-1):
        pieces.append(box([x-1, -52, min(z+9.5,xllo[2]-2)], [x+1, -48, max(z+9.7,xllo[2]-1.8)]))
    # XS bridge joins rear end of lower saddle to the outboard carrier rib.
    pieces.append(box([xslo[0], xslo[1], xslo[2]-2], [xshi[0]+2, xslo[1]+2, xslo[2]+.1]))
    pieces.append(box([xshi[0], xslo[1], xslo[2]-2], [xshi[0]+2, -62.4, z+10]))
    # Finite common rail load-path proposal, not a floating clamp.
    pieces.append(box([rootx-3, -60, 34.7], [rootx+3, -54, z+9.6]))
    carrier = pieces[0].multiFuse(pieces[1:]).removeSplitter()
    assert carrier.isValid() and len(carrier.Solids) == 1, ('Disconnected carrier', len(carrier.Solids))
    parts['ShelfPWM:carrier'] = carrier; kinds['ShelfPWM:carrier'] = dict(kind='carrier', owner='PWM9685')
    retired = [n for n in scene if n in oldnames or n.startswith('REV3:PCA:')]
    contract = dict(status='CONSTRUCTIVE_OWNER_PROPOSAL_NOT_N01', target_PCB_bottom_datum_mm=list(target),
                    purchased_parts=oldnames, reversed_complete_fastener_stacks=hwgroups,
                    source_endpoints=recipes, retired_whole_owner=retired, source_parts=len(sourceparts),
                    carrier_solid_count=len(carrier.Solids), carrier_rail_root_mm=[[rootx-3,-60,34.7],[rootx+3,-54,37.7]],
                    bay_from_actual_S0_key_maxX_mm=key.BoundBox.XMax,
                    root_from_full_R1_tool_lane_minX_mm=-47.5,
                    height_from_full_fastener_underside_mm=lift,
                    shared_backbone_join=dict(owner='StructureReserve:BankBed-1',root_bounds_mm=[[rootx-3,-60,34.7],[rootx+3,-54,z+9.6]],
                                              kind='UNITE_CONNECTED_PLANNING_STRUCTURE_NOT_CASE_OR_WIRE_WAIVER',native_join_still_N03=True),
                    fit_assumptions=dict(channel_clearance_mm=.15, wall_mm=2, first_XL_mm=1.5, post_OD_mm=4, post_bore_mm=2.4,
                                         PETG_pull_fit_and_supplier_revision_require_physical_check=True),
                    source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (planpath,boundarypath,Path(__file__))},
                    selected=False, N01_complete=False, physical_pass=False)
    return parts, kinds, sourceparts, contract


def receive():
    """All changed owner parts against full hard owners, source, service, motion.

    One named failure per changed part, not a whitelist deleting obstructing
    material. Shared variable47 kits require the subsequent coupled receiver.
    """
    from feline_candidate_collision_scene import Scene
    from receive_feline_global_case_candidates import placement
    tick=time.monotonic(); dest=OUT/'n01-pwm-board-shelf.json'
    previous=None
    if dest.exists():
        assert '--next-owner-bay' in sys.argv or '--full-stack-backbone' in sys.argv, 'Receive saved owner; do not duplicate construction'
        previous=json.loads(dest.read_text())
        assert previous['status']=='OWNER_FIXED_GATE_REJECTED' and not previous['errors']
        if previous.get('prior_rejected_owners'):
            assert '--full-stack-backbone' in sys.argv and len(previous['prior_rejected_owners'])==1, 'After2 failures reassess whole owner'
    world=Scene(); parts,kinds,s1,rec=build(world.parts,world.meta)
    proof=json.loads((OUT/'n01-flat20-field-modulejoint.json').read_text())
    for file,groups in (('n01-fore-service-macro.json', {'F_HP','F_TY'}), ('n01-fore-topology.json', {'ForeFHAC'})):
        _,extra,rows=packed(OUT/file)
        for n,s in extra.items():
            if rows[n]['group'] in groups:world.parts[n]=s;world.meta[n]=rows[n]
    fixed={r['source']:world.parts[r['source']] for r in proof['material_clouds']
           if r['category']!='S1_mating_context' and r['source'] not in rec['retired_whole_owner']}
    fixed.update(s1)
    service={}
    for side in ('L','R'):
        sign=1 if side=='L' else -1
        for i in range(1,7):
            key=side+str(i); s=world.parts[f'Ref_Material_F_{key}_CP2_ATO_0_0']; b=s.optimalBoundingBox()
            low=[b.XMin,b.YMin if sign>0 else b.YMin-60,b.ZMin]
            service['ATO_sweep:'+key]=Part.makeBox(b.XLength,b.YLength+60,b.ZLength,A.Vector(*low))
            y0=b.YMax-6 if sign>0 else b.YMin-60
            service['ATO_tool:'+key]=Part.makeBox(25,66,12,A.Vector(b.Center.x-12.5,y0,b.Center.z-6))
    rec.update(stage='actual_fixed',pairs=[],failures=[],errors=[],completed_parts=[],
               all_fixed_owner_count=len(fixed), tool_assumption='Inherited full ATO60mm side pull plus nominal25x12 tool, not actual tool fit',
               outer_refinement_required=[], worker_seconds=0, source_sha256={**world.pins,**rec['source_sha256']})
    if previous:
        prior=list(previous.get('prior_rejected_owners',[]));previous.pop('prior_rejected_owners',None)
        rec['prior_rejected_owners']=prior+[previous]
        rec['changed_cause_after_two_failures']='Complete hardware underside sets height; custom insulated first transition1.5, and root is joined into existing shared BankBed scaffold, not fixed air budget'
    def save():
        rec['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8',newline='\n')
    def query(n,s,other,t,minimum,scope):
        bound=bbox_lower_bound(s.BoundBox,t.BoundBox)
        if bound>=minimum-1e-6:return True
        if n=='ShelfPWM:carrier' and other==rec['shared_backbone_join']['owner']:
            # This named3mm-slab intersection is a load-path junction of one
            # scaffold. No purchased object, wire or unknown frame is waived.
            common=s.common(t);assert common.isValid()
            root=box(*rec['shared_backbone_join']['root_bounds_mm'])
            unexpected=common.cut(root);assert unexpected.isNull() or unexpected.isValid()
            assert unexpected.Volume<1e-6 and abs(common.Volume-108)<1e-5
            rec.setdefault('intended_structure_mates',[]).append(dict(part=n,other=other,overlap_mm3=common.Volume,
                proof='Only connected6x6 root through3mm shared BankBed slab; union required in N03'))
            return True
        q=s
        if other==world.bus['name']:
            q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
        assert t.isValid() and t.Solids, other
        gap=distance(q,t); volume=None
        if gap<1e-6:
            common=q.copy().common(t.copy());assert common.isValid();volume=common.Volume
        row=dict(part=n,other=other,scope=scope,gap_mm=gap,required_mm=minimum,positive_common_mm3=volume)
        rec['pairs'].append(row)
        if gap<minimum-1e-6:rec['failures'].append(row);return False
        return True
    save()
    try:
        for n,s in sorted(parts.items(),key=lambda p: ('carrier' not in p[0],p[0])):
            if time.monotonic()-tick>240:rec['status']='PARTIAL_OWNER_GATE';break
            ok=True
            for other,t in fixed.items():
                minimum=.2 if kinds[n]['kind'] in ('wire','bare') and other in world.meta and world.wire(other) else 1.25
                if not query(n,s,other,t,minimum,'full_fixed_and_S1'):ok=False;break
            if ok:
                for other,t in service.items():
                    if not query(n,s,other,t,0.01,'full_ATO_side_pull'):ok=False;break
            if ok:
                bb=s.BoundBox
                for p in world.motion:
                    bounds=p['bounds']; lower=A.BoundBox(*bounds[0],*bounds[1])
                    if bbox_lower_bound(bb,lower)>=1.25:continue
                    q=s; r=p['r'];t=p['t']
                    if np.linalg.norm(r-np.eye(3))>1e-12 or np.linalg.norm(t)>1e-7:
                        q=s.copy();q.Placement=placement(r,t).inverse()*q.Placement
                    if not query(n,q,p['name'],world.rest[p['name']],1.25,'actual_leg_pose_'+str(p['pose'])):ok=False;break
            rec['completed_parts'].append(n);save()
            print('PWM owner',n,'clear' if ok else rec['failures'][-1],flush=True)
        else:rec['status']='OWNER_FIXED_GATE_REJECTED' if rec['failures'] else 'OWNER_FIXED_GATE_CLEAR_INTERNAL_SHARED47_OUTER_PENDING'
    except Exception as e:rec['errors'].append(repr(e));rec['status']='OWNER_GATE_ERROR_NOT_CLEARANCE'
    save()
    print(json.dumps({k:rec[k] for k in ('status','worker_seconds','errors')}),flush=True)


if __name__=='__main__':
    import os
    print('WORKER_PID',os.getpid(),flush=True)
    receive()
