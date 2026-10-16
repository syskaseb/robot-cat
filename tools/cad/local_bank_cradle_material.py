"""Four local three-holder combs, no continuous plate across current wiring.

Two T18I loops retain each flange outside its ATO. Same12 holders/24 ends.
All aperture/strap dimensions are explicit prototype fit envelopes, not a
manufacturer clamp or pull-force specification. Four parent roots stay OPEN.
"""
import FreeCAD as A
import Part
from loom_land_port import box


GROUPS=[('FL',58,[-53,-23,7],'FrontLeftFixedCarrier'),
        ('RL',58,[37,67,97],'RearLeftFixedCarrier'),
        ('FR',-58,[-53,-21,11],'FrontRightFixedCarrier'),
        ('RR',-58,[43,75,107],'RearRightFixedCarrier')]


def material(leg,side,head_pattern=1):
    _,y,centres,owner=next(r for r in GROUPS if r[0]==leg)
    def B(x,a,z,X,b,Z):
        lo,hi=sorted((y+side*a,y+side*b));return [x,lo,z,X,hi,Z]
    # Different fixed Frames may not overlap at the FL/RL or FR/RR split.
    # Keep0.4mm between their adjacent combs; same-parent bridges may merge.
    boundary=22 if y>0 else 27
    xmin,xmax=centres[0]-16.5,centres[-1]+16.5
    if leg.startswith('F'):xmax=boundary-.2
    else:xmin=boundary+.2
    pads=[dict(name='OutsideTerminalBridge',bounds_mm=B(xmin,10,118,xmax,18,122))]
    ties={};lands=[]
    for i,x in enumerate(centres):
        for sign in (-1,1):
            lo,hi=sorted((x+sign*11.6,x+sign*15.5))
            lo=max(lo,xmin);hi=min(hi,xmax)
            pads.append(dict(name=f'Holder{i+1}FlangeLedge{sign}',bounds_mm=B(lo,-8,120,hi,18,124)))
            cx=x+sign*13
            inner_y=sorted((y-side*8,y+side*18))
            outer=[cx-1.25,inner_y[0]-1.2,116.7,cx+1.25,inner_y[1]+1.2,127.3]
            inner=[cx-2,inner_y[0],117.9,cx+2,inner_y[1],126.1]
            # Adjacent straps are4mm apart inX; their6mm heads must close
            # on opposite sides, not overlap between two holders.
            # Historical T18I head6x4x5 has5mm ACROSS its2.5mm strap.
            # Old strap axisZ maps to newX: head world dimensions5x4x6.
            close_at_root=sign*head_pattern==1
            head=B(cx-2.5,18 if close_at_root else -12,117.3,cx+2.5,22 if close_at_root else -8,123.3)
            tie=box(outer).cut(box(inner)).fuse(box(head)).removeSplitter()
            assert tie.isValid() and len(tie.Solids)==1 and not tie.check(True)
            name=f'{leg}_Holder{i+1}_FlangeTie{sign}'
            ties[name]=tie
            lands.append(dict(id=name,holder_centre_mm=[x,y],outer=outer,inner=inner,head=head,
                project_width_mm=2.5,project_thickness_mm=1.2,head_envelope_mm=[5,4,6],
                head_basis='Retained6x4x5 prototype envelope, strap-axisZ mapped toX; not a changed supplier dimension',
                SKU_family='T18I retained prototype envelope',quantity=1,
                project_loop_perimeter_mm=68.4,nominal_supplied_length_mm=100,
                actual_retention_verified=False))
    s=box(pads[0]['bounds_mm'])
    for p in pads[1:]:s=s.fuse(box(p['bounds_mm'])).removeSplitter()
    assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    assert all(s.common(t).Volume<1e-6 for t in ties.values())
    root=[centres[1],y+side*14,116]
    return dict(body=s,ties=ties,owner=owner,root_goal_mm=root,
        recipe=dict(id=leg,side=side,head_pattern=head_pattern,owner=owner,holder_centres_mm=[[x,y] for x in centres],pads=pads,
            ties=lands,root_goal_mm=root,root_beam_half_widths_mm=[4,4,4],root_path=None,
            aperture_basis='Prototype body22.2x11.3 below supplied28x15x2 flange; ledges beginX+/-11.6. Delivered holder/terminal engagement and printed fit coupon mandatory.',
            load_path='Holder flange -> two cuttable T18I loops/individual ledges -> shared bridge OUTSIDE terminal/body corridor -> one actual fixed Frame root OPEN.',
            routine_service='ATO pulls between strapsX+/-13, without cutting straps or disconnecting WAGO. Check installed nominal35mm sweep and project jaws; actual tool/engagement fit phase2.',
            deep_repair='No power; support holder, label/remove its two TE ends if required, cut only its two replaceable case straps, lift holder from ledges. Whole robot reverse assembly remains A2 OPEN.',
            prototype_mechanical_gate='No strength, creep or extraction-force rating assigned. Support holder during the delivered unpowered ATO trial; case ties are NOT wire strain relief.',
            nominal_hardware={'T18I':6,'new_metal_fasteners':0},new_separate_prints=0,
            selected=False,W5_complete=False,M4_complete=False,physical_pass=False))


def families():
    return {leg:{f'{side}/{pattern}':material(leg,side,pattern) for side in (-1,1) for pattern in (-1,1)}
            for leg,_,_,_ in GROUPS}


def placed_families(rows):
    """Correct the origin/centre confusion using placed world solids.

    This is not a geometric offset search or movement of purchased parts.
    The prior+/-58 template origin was NOT their current+/-62 centre.
    """
    result=families()
    for leg,old_y,xs,owner in GROUPS:
        side='L' if old_y>0 else 'R';indices=range(1,4) if leg.startswith('F') else range(4,7)
        placed=[next(r for r in rows if r['side']==side and r['index']==i) for i in indices]
        assert [r['centre_xy_mm'][0] for r in placed]==xs,'Changed X layout needs a new shared plan'
        ys={r['centre_xy_mm'][1] for r in placed};assert len(ys)==1
        current_y=ys.pop();dy=current_y-old_y
        for key,q in result[leg].items():
            for shape in [q['body'],*q['ties'].values()]:shape.translate(A.Vector(0,dy,0))
            rec=q['recipe'];rec['holder_centres_mm']=[[x,current_y] for x in xs]
            for pad in rec['pads']:
                pad['bounds_mm'][1]+=dy;pad['bounds_mm'][4]+=dy
            for tie in rec['ties']:
                tie['holder_centre_mm'][1]+=dy
                for name in ('outer','inner','head'):tie[name][1]+=dy;tie[name][4]+=dy
            q['root_goal_mm'][1]+=dy
            # Shared list in old recipe; do not translate the root a second time.
            assert rec['root_goal_mm']==q['root_goal_mm']
            rec['world_datum_correction']=dict(template_origin_y_mm=old_y,
                current_placed_centre_y_mm=current_y,translation_y_mm=dy,
                purchased_components_moved=False,basis=placed[0]['placement_basis'])
            rec['catalog_panel_cutout']=dict(a_mm=22.2,b_mm=11.3,
                b_tolerance_mm=[0,.3],panel_d_mm=2,
                source='hardware/reference/servo-holder-p0-2026-09-24/0300330.png, MTA B0-100.E10A table')
            rec['aperture_basis']='Drawing table22.2x11.3(+0.3/-0) for2mm panel; nominal body taper/terminal engagement still require delivered fit. Cradle is not a full panel cutout.'
    return result
