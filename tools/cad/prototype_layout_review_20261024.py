"""One prototype layout proposal, not production CAD or a full N01 receipt.

Keep board poses. Move D_RR/G_AUX together onto a shared shelf, retain RR_G,
and reserve a bundled power corridor above the fixed electronics.
"""
import math
import FreeCAD as A
import Part
import feline_tangent_routes as tr
from receive_feline_W024_shared_body import solid

GROUPS = ('D_RR', 'G_AUX')
STATION_SHIFT = (0, 24, 0)
Y_MAIN = (-76.8875-80.3875)/2
Y_PI = (46.618109634713775+50.118109634713775)/2


def corridor():
    p0 = (20.7, Y_MAIN, 96.55)
    crest = (62, Y_MAIN, 108)
    p1, p2 = (98, Y_MAIN, 108), (118, Y_MAIN+20, 108)
    p3, p4 = (118, -35, 108), (130.95, 15, 108)
    p5, p6 = (130.95, Y_PI-20, 108), (110.95, Y_PI, 108)
    p7 = (89.7, Y_PI, 101.6)
    parts = [*tr.biarc(p0, (1,0,0), crest, (1,0,0)), tr.line(crest,p1),
             tr.arc(p1,(1,0,0),p2), tr.line(p2,p3),
             *tr.biarc(p3,(0,1,0),p4,(0,1,0)), tr.line(p4,p5),
             tr.arc(p5,(0,1,0),p6),
             *tr.biarc(p6,(-1,0,0),p7,(-1,0,0))]
    shape = solid(parts, 2.6)
    shape.check(True)
    return shape, dict(parts=parts, radius_mm=2.6,
        centre_length_mm=tr.length(parts),
        minimum_centre_radius_mm=min(p.get('radius', math.inf) for p in parts),
        nominal_wire_OD_mm=2.1, nominal_two_touching_wires_enclosing_radius_mm=2.1,
        packing_allowance_radial_mm=.5,
        complete_individual_wire_paths_NOT_received=True,
        source_and_receiver_fans_OPEN=True)


def station_group(scene):
    moved = {n:s.copy() for n,s in scene.items()
             if any(n.startswith('Station:'+g+':') for g in GROUPS)}
    assert len(moved) == 18
    for s in moved.values():
        s.translate(A.Vector(*STATION_SHIFT))
    return moved


def rack(moved):
    def box(lo, hi):
        return Part.makeBox(*(hi[i]-lo[i] for i in range(3)), A.Vector(*lo))
    # Shelf under cases; the front porch joins the received independent combs.
    shelf = box((-10,-66,90),(66.5,-44,93))
    porch = box((-10,-45.5,91),(66.5,-21.5,95))
    for n,s in moved.items():
        b = s.optimalBoundingBox(False,False)
        if n.endswith(':case'):
            # Keep the .5mm project adhesive seat below the delivered-case gate.
            porch = porch.cut(box((b.XMin-.3,b.YMin-.3,93),
                                   (b.XMax+.3,b.YMax+.3,104)))
    body = shelf.fuse(porch)
    for lo,hi in [((-10,-35,90),(-6,-31,109.4)),
                  ((64,-35,90),(68,-31,109.4)),
                  ((-10,-34.5,106.2),(68,-31.5,109.4)),
                  ((15,-33,106.2),(35,-14,109.4))]:
        body = body.fuse(box(lo,hi))
    for x0,x1 in ((0,12),(45,58)):
        body = body.fuse(box((x0,-67,92.7),(x1,-65.5,96.5)))
    # Explicit conservative tie slots; bounding boxes are design keepouts,
    # not claims that the entire boxes are physical nylon.
    for n,s in moved.items():
        if n.endswith((':band_budget', ':head_budget')):
            b = s.optimalBoundingBox(False,False)
            body = body.cut(box((b.XMin-.25,b.YMin-.25,b.ZMin-.25),
                                (b.XMax+.25,b.YMax+.25,b.ZMax+.25)))
    body.check(True)
    assert body.isValid() and len(body.Solids) == 1
    return body, dict(material='PETG planning material; native features later',
        root_owner='received removable Pi upper U rail',
        root_patch_mm=[[15,-17.03,106.2],[35,-14,106.4]],
        case_retention='provisional .5mm 4905 seat plus open lateral stops; fit gate',
        no_straps_over_WAGO_levers=True,
        independently_restrained_wires='received two full common combs retained',
        rare_Pi_service='disconnect these two groups as documented reverse assembly',
        native_manufacturing_and_physical_load_fit_OPEN=True)


def main_exit():
    """All four occupied MAIN pads turn east together; no purchased PCB change."""
    from feline_shared_pi_carrier import saddle
    ys = (-76.8875,-80.3875,-83.8875,-87.3875)
    pad, kit, recipe = saddle([((-3.3,y,96.55),(1,0,0)) for y in ys],1.05)
    pts = [(-24.5,-82.1375,95),(-24.5,-93,86.5),
           (0,-93,86.5),(0,-93,98.5),(0,-90.1375,98.5)]
    body = pad
    for a,b in zip(pts,pts[1:]):
        a,b = A.Vector(*a),A.Vector(*b)
        body = body.fuse(Part.makeCylinder(1.5,(b-a).Length,a,b-a))
        body = body.fuse(Part.makeSphere(1.5,a)).fuse(Part.makeSphere(1.5,b))
    body = body.cut(kit['band'])
    body.check(True)
    assert body.isValid() and len(body.Solids)==1
    recipe.update(source_pads_unchanged=True,wire_ids=['W079','W080','W060','W078'],
        bare_project_form_R_mm=2.2,bare_neck_length_mm=.5+math.pi*2.2/2,
        sleeve_raw_mm=16,sleeve_min_recovered_mm=14.4,
        recovered_overlap_mm=14.4-(.5+math.pi*2.2/2),
        jacket_start_X_mm=-15.3,full_grip_X_mm=[-3.3,5.7],
        root_point_mm=pts[0],root_owner='new primitive MAIN fork at unchanged PCB axes',
        all_four_affected_remote_wire_paths_and_terminations_OPEN=True,
        delivered_solder_form_and_sleeve_fit_gate=True)
    return dict(body=body,**kit),recipe


def main_support(scene, anchor):
    """Replace the strict-invalid inherited fork using unchanged screw axes."""
    axes=[];pieces=[]
    for i,limit in ((0,-89.3875),(1,-74.8875)):
        b=scene[f'Ref_Material_MAIN_{i}_shaft_0_0'].BoundBox
        p=A.Vector(b.Center.x,b.Center.y,91.25);axes.append(list(p))
        post=Part.makeCylinder(3.5,8,p).cut(Part.makeCylinder(1.2,10,p-A.Vector(0,0,1)))
        # Open flats next to the first/last insulated pad; no tight wire tunnel.
        lo=(-40,limit,90) if i==0 else (-40,-120,90)
        hi=(0,-60,101) if i==0 else (0,limit,101)
        post=post.cut(Part.makeBox(*(hi[j]-lo[j] for j in range(3)),A.Vector(*lo)))
        pieces.append(post)
    spine=A.Vector(-24.5,-82.1375,95)
    links=[(A.Vector(*anchor),spine)]+[(spine,A.Vector(p[0]-2.5,p[1],95)) for p in axes]
    for a,b in links:
        pieces.extend([Part.makeCylinder(1.5,(b-a).Length,a,b-a),
                       Part.makeSphere(1.5,a),Part.makeSphere(1.5,b)])
    body=pieces[0]
    for s in pieces[1:]:body=body.fuse(s)
    for p in axes:body=body.cut(Part.makeCylinder(1.2,12,A.Vector(p[0],p[1],89.25)))
    body.check(True)
    assert body.isValid() and len(body.Solids)==1
    return body,dict(screw_axes_mm=axes,washer_bearing_Z_mm=91.25,
        PCB_bearing_Z_mm=99.25,root_anchor_mm=anchor,open_side_relief=True,
        original_board_fastener_poses_unchanged=True,
        old_strict_invalid_root_NOT_used_for_clearance=True,
        printed_strength_and_native_features_OPEN=True)


def changed_support_checks(scene, moved, shapes):
    """Only new printed supports versus neighbours; retain every contact witness."""
    import time
    started=time.monotonic();rows=[]
    retired=lambda n: n=='SharedPi:Carrier' or n.startswith('MainSupported:')
    current={n:s for n,s in scene.items() if not retired(n)}
    current.update(moved)
    for label,shape in shapes.items():
        b=shape.optimalBoundingBox(False,False)
        vicinity=Part.makeBox(b.XLength+2,b.YLength+2,b.ZLength+2,
                              A.Vector(b.XMin-1,b.YMin-1,b.ZMin-1)).BoundBox
        for name,other in current.items():
            if not vicinity.intersect(other.BoundBox):continue
            try:
                gap=shape.copy().distToShape(other.copy())[0]
                common=shape.copy().common(other.copy()).Volume if gap<1e-6 else 0
                rows.append(dict(support=label,name=name,gap_mm=gap,common_mm3=common))
            except Exception as exc:
                rows.append(dict(support=label,name=name,error=str(exc)))
    return dict(seconds=time.monotonic()-started,rows=rows,
                exclusions='retired SharedPi carrier and MAIN local root/comb/ends; remote paths OPEN')


def save_packet(out, scene, moved, shapes, recipes, evidence):
    """Freeze one bounded proposal with strict reopen, hashes and explicit gates."""
    import hashlib,json,zipfile
    from pathlib import Path
    def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    archive=out/'prototype-layout-review-20261024.breps.zip'
    geometry={}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(name,s) in enumerate({**shapes,**moved}.items()):
            raw=s.exportBrepToString();raw=raw.encode() if isinstance(raw,str) else raw
            clone=Part.Shape();clone.importBrepFromString(raw.decode())
            strict_error=None
            try:clone.check(True)
            except ValueError as exc:
                if not name.endswith((':band_budget',':head_budget')):raise
                strict_error=str(exc).splitlines()[0]
            assert clone.isValid() and len(clone.Solids)==len(s.Solids)
            z.writestr(f'{i}.brep',raw)
            b=clone.optimalBoundingBox(False,False)
            geometry[name]=dict(member=f'{i}.brep',sha256=hashlib.sha256(raw).hexdigest(),
                strict_reopen=strict_error is None,strict_error=strict_error,
                invalid_reservation_NOT_actual_material=bool(strict_error),
                solids=len(clone.Solids),volume_mm3=clone.Volume,
                bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]])
    roots=['W009-W069-harness-corridor/recovered-context.json','n01-service-provider-actors-restored-20261024.json',
           'n01-shared-Pi-carrier-r3-core-received.json','n01-Pi-split-service-space.json',
           'n01-power-axial-saddle-20261024.json','n01-USB-main-saddle-20261024.json']
    sources={str(out/n):digest(out/n) for n in roots}
    sources[str(Path(__file__).resolve())]=digest(__file__)
    names=['Ref_Material_Pi4NominalPCB_0_0','Ref_Material_PWM9685NominalPCB_0_0',
           'Ref_Material_MAIN_CurrentMainSupplierReference_0_0','BatterySelectedNominal']
    module_bounds={}
    for n in names:
        if n not in scene:continue
        b=scene[n].optimalBoundingBox(False,False)
        module_bounds[n]=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
    module_bounds.update({f'new_{n}':r['bounds_mm'] for n,r in geometry.items()
                         if n in ('rack','MAINfork','MAINexit') or n.endswith(':case')})
    packet=dict(package_id='LAYOUT24-C-01',
        scope='One prototype architecture proposal with changed-interface witnesses; NOT whole N01',
        status='FROZEN_FOR_INDEPENDENT_REVIEW',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=sources,geometry_archive=dict(path=str(archive),sha256=digest(archive),members=geometry),
        module_bounds_mm=module_bounds,corridor=recipes['corridor'],recipes=recipes,evidence=evidence,
        assembly=[
            'Keep battery, PCBs, all bought hardware and RR_G at received poses.',
            'Replace strict-invalid MAIN fork at the same two screw axes; retain lower washers/nuts and PCB bearing planes.',
            'Join MAIN fork to retained fixed Pi root; fit four insulated MAIN leads then common east saddle and tie. Actual solder/sleeve fit gate remains.',
            'Unplug/reconnect D_RR and G_AUX once for assembly; place them on shared shelf on removable Pi upper U rail. Keep existing full combs; no tie across levers.',
            'Install existing received USB saddle/side-bow and PAS power support, preserving fixed USB beam.',
            'Lay W079/W080 together in open reserved corridor, then close simple shared tie anchors. First/last fans and final remote lead curves require next evidence.',
            'Close access panels only after whole N01 motion, all endpoints and assembly are received; none received by this packet.'],
        open=[
            'Ten moved station wire remote transitions are not yet rejoined. Two local groups move as units; purchased case poses change.',
            'Four MAIN remote paths/terminations and two power packing fans are OPEN. Corridor clearance alone is not complete wire receipt.',
            'Full installed loom 123 portions/246 ends, factory4MTA lengths, whole movement/floor/outer shell remain N01 gates.',
            'Tie closure, physical source sleeve shape/fit, adhesive retention and print strength need physical fit; no physical PASS.',
            'Native editable manufacturing features/selected exports and final stock are later stages. Proposal archive is planning geometry.',
            'BUSsupplier25 invalid/missing source is explicit; only conservative separated bounds may be used, no invalid Boolean proof.'])
    dest=out/'prototype-layout-review-20261024.json'
    dest.write_text(json.dumps(packet,indent=2,ensure_ascii=False),encoding='utf-8')
    return packet,dict(path=str(dest),sha256=digest(dest))


def packing_fans():
    """Four local cubic transitions; exact detail only at the changed mouths."""
    result={}
    for end,x,y,z,sign in [('MAIN',5.7,Y_MAIN,96.55,1),('Pi',74.7,Y_PI,101.6,-1)]:
        for wire,sense in [('W079',sign),('W080',-sign)]:
            c=Part.BezierCurve()
            c.setPoles([A.Vector(x,y+sense*1.75,z),A.Vector(x+5,y+sense*1.75,z),
                        A.Vector(x+10,y+sense*1.05,z),A.Vector(x+15,y+sense*1.05,z)])
            spine=Part.Wire(c.toShape())
            profile=Part.Wire(Part.makeCircle(1.05,c.value(0),A.Vector(1,0,0)))
            shape=spine.makePipeShell([profile],True,False);shape.check(True)
            assert shape.isValid() and len(shape.Solids)==1
            result[f'{end}:{wire}']=shape
    return result,dict(span_mm=15,offset_change_mm=.7,
        curvature_upper_per_mm=6*.7/15**2,minimum_radius_bound_mm=15**2/(6*.7),
        per_fan_length_upper_mm=15+.7,
        derivation='Linear x and cubic smoothstep y; |y second derivative|<=6*.7/L^2; arc length<=L+total y variation',
        nominal_wire_radius_mm=1.05,actual_OD_and_clamp_fit_phase2_gate=True)


def pair_bounds(parts,prefix_lengths,source_bare_length):
    turn=sum(abs(p.get('angle',0)) for p in parts)
    normal=A.Vector(0,1,0)
    for p in parts:
        if p['kind']=='arc':
            axis=A.Vector(*p['tangent']).cross(A.Vector(*p['bend']))
            normal=A.Rotation(axis,math.degrees(p['angle'])).multVec(normal)
    assert (normal-A.Vector(0,-1,0)).Length<1e-8
    return dict(parallel_transport_normal_end=list(normal),total_turn_rad=turn,
        inner_wire_min_radius_mm=min(p.get('radius',math.inf) for p in parts)-1.05,
        derivation='Constant +/-1.05mm Bishop parallel transported offset: radius>=centre radius-1.05; length<=centre length+1.05*total absolute turning. Start+Y maps to end-Y; no polarity exchange.',
        length_upper_with40mm_trim_terminal_allowance={w:v+9+21+source_bare_length+
            tr.length(parts)+1.05*turn+2*(15+.7)+40 for w,v in prefix_lengths.items()},
        existing_350mm_plan_insufficient=True,new_provisional_allocation_per_colour_mm=460,
        red_1m_minus_existing210_and_new460_mm=330,black_1m_minus_existing220_and_new460_mm=320,
        entire_stock_ledger_and_as_cut_physical_lengths_NOT_received=True)


def diagram(packet):
    """Dimensioned XY/XZ planning projection, not a render or collision proof."""
    rows = packet['module_bounds_mm']
    paths = []
    for p in packet['corridor']['parts']:
        paths.extend(list(tr.samples(p, 2)))
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="850" viewBox="0 0 1200 850">',
           '<rect width="1200" height="850" fill="white"/>',
           '<style>text{font:14px sans-serif} .small{font-size:11px}</style>',
           '<text x="25" y="28">Prototype layout: fixed boards, shared shelf, power bundle corridor (mm)</text>',
           '<text x="25" y="50">PLANNING ONLY. Rectangles are projections of bounds; overlaps are not collision evidence.</text>']
    for view, axes, origin, label in [('XY',(0,1),(315,265),'TOP: X / Y'),
                                      ('XZ',(0,2),(315,700),'SIDE: X / Z')]:
        scale=2.8
        def xy(p): return origin[0]+p[axes[0]]*scale,origin[1]-p[axes[1]]*scale
        out.append(f'<text x="25" y="{85 if view=="XY" else 475}">{label}</text>')
        for name,b in rows.items():
            x,y=xy([b[0][i] if i!=axes[1] else b[1][i] for i in range(3)])
            w=(b[1][axes[0]]-b[0][axes[0]])*scale
            h=(b[1][axes[1]]-b[0][axes[1]])*scale
            colour='#d9edf7' if name.startswith('new_') else '#e4e7eb'
            out.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{colour}" stroke="#52606d"/>')
            out.append(f'<text class="small" x="{x+2:.2f}" y="{y+12:.2f}">{name}</text>')
        line=' '.join(f'{xy(p)[0]:.2f},{xy(p)[1]:.2f}' for p in paths)
        out.append(f'<polyline points="{line}" fill="none" stroke="#df6d00" stroke-width="{5.2*scale}" opacity=".65"/>')
        out.append(f'<text x="820" y="{220 if view=="XY" else 600}">orange: 5.2mm bundle reservation</text>')
    out.extend(['<text x="25" y="810">Boards and battery stay at received poses. Two station groups shift +24Y; RR_G remains.</text>',
                '<text x="25" y="832">No production export, individual wire routing or physical PASS claimed.</text></svg>'])
    return '\n'.join(out)
