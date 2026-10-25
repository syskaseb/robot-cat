"""GAL25-A: one shared side-cell layout hypothesis, no production export."""
import FreeCAD as A
import prototype_joint_endpoints_20261024 as prior

def side_groups(scene,out,targets=None):
    groups,grips=prior.early_groups(scene,out)
    for group,rz,target in [('D_RR',-90,(55,-92.5,57)),('G_AUX',90,(10,-92.5,57))]:
        target=(targets or {}).get(group,target)
        pivot=groups['Station:'+group+':case'].BoundBox.Center
        for name,shape in groups.items():
            if name.startswith('Station:'+group+':'):
                shape.rotate(pivot,A.Vector(0,0,1),rz)
                shape.rotate(pivot,A.Vector(1,0,0),90)
                shape.translate(A.Vector(*target)-pivot)
        grips[group].update(case_centre_mm=target,proper_rotation_degrees=[rz,90],
            levers_and_open_comb_face='negativeY exterior after proper90X',
            source_rows='stackedZ; preserve wire/slot identity',
            full_source_grip_mm=9,case_is_allocated_simplified_geometry=True)
    return groups,grips


def staged_rr3(endpoints,fan_run=20):
    """Jointly separate rows before rising over the retained XP02 support."""
    import math
    from plan_feline_FL_three_core_shared_trunk import transport
    import prototype_layout_review_20261024 as base
    shapes={};recipes={}
    for w,y in [('W016',-90.15),('W017',-93.45),('W018',-96.75)]:
        row=endpoints['rows'][w];p=row['local']['point_mm'];q=row['remote']['point_mm']
        a=[p[0]+fan_run,y,p[2]];parts=base.tr.biarc(p,(1,0,0),a,(1,0,0));R=12.4
        dz=q[2]-p[2]
        if dz>=2*R:
            b=[a[0]+R,y,a[2]+R];c=[a[0]+R,y,q[2]-R];d=[a[0]+2*R,y,q[2]]
            parts += [base.tr.arc(a,(1,0,0),b),base.tr.line(b,c),base.tr.arc(c,(0,0,1),d)]
        else:
            theta=math.acos(1-dz/(2*R));b=[a[0]+R*math.sin(theta),y,a[2]+dz/2]
            d=[a[0]+2*R*math.sin(theta),y,q[2]];first=base.tr.arc(a,(1,0,0),b)
            parts += [first,base.tr.arc(b,first['end_tangent'],d)]
        common_x=p[0]+fan_run+2*R
        if common_x-d[0]>1e-8:
            parts.append(base.tr.line(d,[common_x,y,q[2]]))
        centre=base.tr.biarc([common_x,-93.45,q[2]],(1,0,0),[q[0],-88.25,q[2]],(1,0,0))
        fan,normal=transport(centre,[0,y+93.45,0]);parts += fan
        assert (A.Vector(*parts[-1]['end'])-A.Vector(*q)).Length<1e-6
        minimum=min(r.get('radius',math.inf) for r in parts);assert minimum>=R-1e-6,(w,minimum)
        shapes[w]=base.solid(parts,row['radius_mm']);shapes[w].check(True)
        recipes[w]=dict(parts=parts,body_length_mm=base.tr.length(parts),minimum_R_mm=minimum,
            radius_mm=row['radius_mm'],source=row['local'],receiver=row['remote'],
            stages='20mm lateralfan with retainedZ rows; independentearlyrise on3separateYlanes; Bishop parallel-normal finalfan aboveXP02root',
            factory900_whole_length_NOT_received=True)
    return shapes,recipes


def rooted_side_cradle(scene,groups):
    """Add only to the selected printed rail; keep all original rail material."""
    import Part
    def box(lo,hi):return Part.makeBox(*(hi[i]-lo[i] for i in range(3)),A.Vector(*lo))
    original=scene['CurrentFoundation:FoundationRail:-1'];cells=[]
    for group in ['D_RR','G_AUX']:
        case=groups['Station:'+group+':case'].optimalBoundingBox(False,False);x=(case.XMin+case.XMax)/2
        cells += [box((x-3,-98.5,35.5),(x+3,-53,38.5)),
                  box((x-3,-59,35.5),(x+3,-55,40.52)),
                  box((case.XMin-1,-99,38.3),(case.XMax+1,-87.5,41.5))]
        comb=groups['Station:'+group+':split_common_comb'];b=comb.optimalBoundingBox(False,False)
        lo_x=b.XMin if b.XMin>=case.XMax else b.XMin-.5
        hi_x=b.XMax if b.XMax<=case.XMin else b.XMax+.5
        wall=box((lo_x,b.YMax-.2,38.3),(hi_x,b.YMax+1.2,b.ZMax))
        # Clearance slots in NEW wall only, never delete any of the full9mm comb.
        for role in ['band_budget','head_budget']:
            k=groups['Station:'+group+':'+role].optimalBoundingBox(False,False)
            wall=wall.cut(box((k.XMin-.25,k.YMin-.25,k.ZMin-.25),(k.XMax+.25,k.YMax+.25,k.ZMax+.25)))
        cells += [wall,comb]
    body=original.multiFuse(cells);body.check(True);assert len(body.Solids)==1
    assert original.cut(body).Volume<1e-7
    added=body.cut(original);added.check(True)
    return body,added,dict(original_rail_preserved_mm3=original.Volume,
        construction_cell_bounds_mm=[[c.BoundBox.XMin,c.BoundBox.YMin,c.BoundBox.ZMin,c.BoundBox.XMax,c.BoundBox.YMax,c.BoundBox.ZMax] for c in cells],
        adhesive_seat_gap_mm=.5,case_bottom_Z_mm=42.,printed_toe_top_Z_mm=41.5,
        new_arm_top_Z_mm=38.5,old_lower_station_case_bottom_Z_mm=40.76,
        no_purchased_parts_or_P0_holes_changed=True,
        fixed_rail_assembly_versus_removable_case_service_OPEN=True,
        geometry_positive_loadpath_NOT_physical_strength=True)



def rejected_front_ground_group(endpoints):
    """Three actual cores follow one frame; cross below existing FL3 trunk."""
    import math
    from plan_feline_FL_three_core_shared_trunk import transport
    import prototype_layout_review_20261024 as base
    shapes={};recipes={}
    centre_turn=[base.tr.arc([-32.25,-92.5,54.35],(-1,0,0),[-49.25,-75.5,54.35])]
    for w,offset in [('XA05',[0,1.25,-.55]),('XB23',[0,-1.25,.55]),('XB13',[0,0,9.85])]:
        row=endpoints['rows'][w];p=row['local']['point_mm'];q=row['remote']['point_mm']
        turn,last_offset=transport(centre_turn,offset);a=turn[0]['start'];b=turn[-1]['end'];x,z=b[0],b[2]
        parts=base.tr.biarc(p,(-1,0,0),a,(-1,0,0))+turn
        if w=='XB13':
            c=[x,-46.35,z];d=[x-15,-31.35,z];k=[-120,-31.35,q[2]]
            parts += [base.tr.line(b,c),base.tr.arc(c,(0,1,0),d),
                *base.tr.biarc(d,(-1,0,0),k,(-1,0,0)),
                *base.tr.biarc(k,(-1,0,0),q,[-v for v in row['remote']['outward']])]
        elif w=='XA05':
            c=[x,0,z];parts += [base.tr.line(b,c),*base.tr.biarc(c,(0,1,0),q,(0,1,0))]
        else:
            # HP finish(-35) was an arbitrary flexible split, not a connector.
            # Preserve actual head source and moving portion, reassign final straight.
            q=[-92.6,36.4,103.]
            c=[x,46.,z];d=[x-14,60.,z];f=[x-26.6,60.,z+12.6]
            g=[x-26.6,60.,81.]
            parts += [base.tr.line(b,c),base.tr.arc(c,(0,1,0),d),
                base.tr.arc(d,(-1,0,0),f),base.tr.line(f,g),
                *base.tr.biarc(g,(0,0,1),q,(-1,0,0))]
        minimum=min(p.get('radius',math.inf) for p in parts)
        assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        shapes[w]=base.solid(parts,row['radius_mm']);shapes[w].check(True)
        recipes[w]=dict(parts=parts,body_length_mm=base.tr.length(parts),minimum_R_mm=minimum,
            radius_mm=row['radius_mm'],source=row['local'],receiver=row['remote'],
            common_frame_offset_mm=offset,
            common_group='Parallel-normal17mm turn to paired lower lanesXA05[-48,Z53.8]/XB23[-50.5,Z54.9] below received FL3torus; XB13upperZ64.2 branches early through wholeS0/S1gapY-31.35',
            source_and_receiver_grips_unchanged_except_authorized_whole_sidecell_pose=True,
            revised_flexible_split_mm=q if w=='XB23' else None,
            not_a_new_cut_or_connector=w=='XB23')
    return shapes,recipes


def removable_side_cradle(scene,groups):
    """One fixed rail, two lift-off carriers. Assembly concept, not print release."""
    import Part
    def box(lo,hi):return Part.makeBox(*(hi[i]-lo[i] for i in range(3)),A.Vector(*lo))
    arms={-1:[],1:[]};carriers={};receipts={}
    def sidebox(lo,hi,side):
        if side<0:return box(lo,hi)
        return box((lo[0],-hi[1],lo[2]),(hi[0],-lo[1],hi[2]))
    for group in ['D_RR','G_AUX']:
        cb=groups['Station:'+group+':case'].optimalBoundingBox(False,False);x=(cb.XMin+cb.XMax)/2;side=1 if cb.YMin>0 else -1
        arm=sidebox((x-3,-98.5,35.5),(x+3,-53,38.5),side);post=sidebox((x-3,-59,35.5),(x+3,-55,40.52),side)
        arms[side] += [arm,post]
        foot=sidebox((cb.XMin-1,-99,38.5),(cb.XMax+1,-87.5,41.5),side)
        # Horizontal threading windows through carrier, above the fixed arm.
        # Ties retain removable PETG, independently of the wire strain relief.
        for y in [-95.5,-90.]:
            foot=foot.cut(sidebox((cb.XMin-2,y-1.4,39.),(cb.XMax+2,y+1.4,40.5),side))
        comb=groups['Station:'+group+':split_common_comb'];b=comb.optimalBoundingBox(False,False)
        lo_x=b.XMin if b.XMin>=cb.XMax else b.XMin-.5
        hi_x=b.XMax if b.XMax<=cb.XMin else b.XMax+.5
        wy=(b.YMin-1.2,b.YMin+.2) if side>0 else (b.YMax-.2,b.YMax+1.2)
        wall=box((lo_x,wy[0],38.5),(hi_x,wy[1],b.ZMax))
        for role in ['band_budget','head_budget']:
            k=groups['Station:'+group+':'+role].optimalBoundingBox(False,False)
            wall=wall.cut(box((k.XMin-.25,k.YMin-.25,k.ZMin-.25),(k.XMax+.25,k.YMax+.25,k.ZMax+.25)))
        carrier=foot.fuse(wall).fuse(comb);carrier.check(True);assert len(carrier.Solids)==1
        contact=carrier.common(arm);assert contact.Volume<1e-7
        distance=carrier.distToShape(arm)[0];assert distance<1e-7
        carriers[group]=carrier
        receipts[group]=dict(carrier_one_solid=True,arm_top_mm=38.5,carrier_bottom_mm=38.5,
            assembly_contact_gap_mm=distance,wire_comb_preserved_mm3=comb.cut(carrier).Volume,
            case_tape_gap_mm=.5,retention='2 selected T18I100 through horizontal windows; no tie across WAGO levers',
            nominal_tie_length_budget_mm=2*(21+5)+7+20,
            tie_qty=2,physical_fit_strength_and_cut_tie_service_phase2_OPEN=True,
            service='Remove side panel, release gallery ties, cut only two carrier fixing ties; lift carrier with all five wires attached. Open wire comb separately if needed. Parking/whole-factory slack still OPEN.')
        assert receipts[group]['wire_comb_preserved_mm3']<1e-7
    fixed={}
    for side,cells in arms.items():
        if not cells:continue
        name='CurrentFoundation:FoundationRail:'+str(side);original=scene[name]
        body=original.multiFuse(cells);body.check(True)
        assert len(body.Solids)<=len(original.Solids)
        assert original.cut(body).Volume<1e-7
        assert all(body.common(c).Volume>0 for c in cells);fixed[name]=body
    return fixed,carriers,dict(carriers=receipts,selected_tie_total_added=4,
        historical_selected_pack_capacity=200,historical_installed=143,historical_service_spares=36,
        historical_unallocated_before_change=21,actual_owned_inventory_unknown=True,
        no_new_SKU_or_purchase=True,old_rail_bolt_geometry_preserved=True,
        fixed_rail_is_revision_of_existing_print_owner_not_second_physical_rail=True)


def preserve_current(out,shapes,receipt):
    """Keep the one current GAL25 witness, preserving the historical JOINT24 pack."""
    import hashlib,json,time,zipfile
    import Part
    tick=time.monotonic();archive=out/'prototype-shared-galleries-20261025.breps.zip';members={}
    prior_json={}
    if archive.exists():
        with zipfile.ZipFile(archive) as z:prior_json={n:z.read(n) for n in z.namelist() if n.endswith('.json')}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(name,s) in enumerate(shapes.items()):
            s.check(True);raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
            t=Part.Shape();t.importBrepFromString(raw.decode());t.check(True)
            members[name]=dict(member=entry,sha256=hashlib.sha256(raw).hexdigest(),strict_reopen=True,
                solids=len(t.Solids),volume_mm3=t.Volume,bounds_mm=[[t.BoundBox.XMin,t.BoundBox.YMin,t.BoundBox.ZMin],[t.BoundBox.XMax,t.BoundBox.YMax,t.BoundBox.ZMax]])
        for n,raw in prior_json.items():z.writestr(n,raw)
    receipt['generator_sha256']=hashlib.sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest()
    receipt.update(geometry_archive=dict(path=str(archive),sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),members=members),
        preserve_and_reopen_seconds=time.monotonic()-tick,selected=False,N01_complete=False,physical_pass=False)
    (out/'prototype-shared-galleries-20261025-result.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return receipt


def opposite_side_groups(scene,out):
    """Current G layout: whole GAUX faces +Y near its three +Y receivers."""
    groups,grips=side_groups(scene,out,{'D_RR':(35,-92.5,57),'G_AUX':(10,-92.5,57)})
    for name,s in groups.items():
        if name.startswith('Station:G_AUX:'):
            s.rotate(A.Vector(10,-92.5,57),A.Vector(1,0,0),180)
            s.translate(A.Vector(0,185,0))
    grips['G_AUX'].update(case_centre_mm=[10,92.5,57],additional_proper_rotation_X_degrees=180,
        levers_and_open_comb_face='positiveY exterior',source_rows='reversed Z after whole proper rotation; identities unchanged')
    return groups,grips


def main_inputs_shared_lane(endpoints):
    """Joint source fan and XZ folds, dimensioned from actual cap tangents."""
    import math
    import prototype_layout_review_20261024 as base
    shapes={};recipes={};R=12.4;lanes={'W060':-82.8,'W078':-85.1}
    for w,y in lanes.items():
        row=endpoints['rows'][w];p=row['local']['point_mm'];q=row['remote']['point_mm']
        a=[17.6,y,96.55];b=[30,y,84.15]
        parts=base.tr.biarc(p,(1,0,0),a,(1,0,0))+[base.tr.arc(a,(1,0,0),b)]
        if w=='W078':
            c=[30,y,60.5];d=[17.6,y,48.1];e=[-21.5,y,48.1]
            f=[-33.9,y+R,48.1];g=[-33.9,-36.4,48.1]
            parts += [base.tr.line(b,c),base.tr.arc(c,(0,0,-1),d),base.tr.line(d,e),
                base.tr.arc(e,(-1,0,0),f),base.tr.line(f,g),base.tr.arc(g,(0,1,0),q)]
        else:
            qv=A.Vector(*q);h=qv-A.Vector(0,R*(1-math.cos(math.pi/6)),R*.5)
            # Prior fixed55.5X only worked at the old Y. Derive the whole turn,
            # keeping selected minimum R instead of reducing it for the new lane.
            turn_x=qv.x+math.sqrt(max(0.,(2*R)**2-(h.y-y)**2))
            c=A.Vector(turn_x,y,h.z);v=h-c;radius=v.Length/2;assert radius>=R-1e-7
            u=v.normalize();bend=dict(kind='arc',start=list(c),end=list(h),tangent=[0,0,-1],
                bend=list(u),radius=radius,angle=math.pi,length=math.pi*radius,end_tangent=[0,0,1])
            f=[30,y,45]
            parts += [base.tr.line(b,f),*base.tr.biarc(f,(0,0,-1),list(c),(0,0,-1)),
                bend,base.tr.arc(list(h),(0,0,1),q)]
        minimum=min(p.get('radius',math.inf) for p in parts);assert minimum>=row['minimum_R_mm']-1e-6
        body=base.solid(parts,row['radius_mm']);body.check(True);shapes[w]=body
        recipes[w]=dict(parts=parts,source=row['local'],receiver=row['remote'],length_mm=base.tr.length(parts),minimum_R_mm=minimum,
            common_lane_centres_mm=lanes,lane_occupied_Y_mm=[-86.15,-81.75],
            previous_4p3mm_allocation_corrected_to_4p4mm_for_retained_p2mm_pair_gap=True,
            source_grip_and_receiver_prefix_unchanged=True,W078_source_grip_not_received=w=='W078')
    return shapes,recipes


def gaux_shared_source_fan(endpoints):
    """All five lanes before bifurcation, then two nested rear turns, three front."""
    import math
    import prototype_layout_review_20261024 as base
    shapes={};recipes={}
    for w,z in [('XA05',70.),('XA04',67.),('XB23',63.),('XB13',57.),('XA06',51.)]:
        row=endpoints['rows'][w];p=row['local']['point_mm'];a=[-35.,92.5,z]
        parts=base.tr.biarc(p,(-1,0,0),a,(-1,0,0))
        if w in ['XA04','XA06']:
            R=31. if w=='XA04' else 15.;b=[-35.,92.5,z-2*R]
            parts.append(dict(kind='arc',start=a,end=b,tangent=[-1,0,0],bend=[0,0,-1],
                radius=R,angle=math.pi,length=math.pi*R,end_tangent=[1,0,0]))
            phase='nested common-centre rear reversal; radial gap12mm, no translated crossing turns'
        else:
            R=47. if w=='XA05' else 30.
            b=[a[0]-R,a[1]-R,z];parts.append(base.tr.arc(a,(-1,0,0),b))
            phase='three front lanes share R30 XY turn, clear outside actual F_L1 ATO'
        minimum=min(p.get('radius',math.inf) for p in parts);assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        body=base.solid(parts,row['radius_mm']);body.check(True);shapes[w]=body
        recipes[w]=dict(parts=parts,source=row['local'],end_mm=b,phase=phase,
            length_mm=base.tr.length(parts),minimum_R_mm=minimum,radius_mm=row['radius_mm'],
            partial_source_transition_only=True,whole_receiver_and_route_NOT_received=True)
    return shapes,recipes


def splice_saddle_and_root(scene,rail):
    """Replace filled end-cuff reservations by two open jacket saddles on one rail."""
    import Part
    def box(lo,hi):return Part.makeBox(*(hi[i]-lo[i] for i in range(3)),A.Vector(*lo))
    pads=[];full9={}
    for w,x,r in [('W077',-88.55,2.),('W078',-55.55,1.05)]:
        pad=box((x,-28.1,44.),(x+9,-19.9,48.1))
        bore=Part.makeCylinder(r+.15,11,A.Vector(x-1,-24,48.1),A.Vector(1,0,0))
        open_top=box((x-1,-24-r-.15,48.1),(x+10,-24+r+.15,53.2))
        pad=pad.cut(bore).cut(open_top);pad.check(True);assert len(pad.Solids)==1;pads.append(pad)
        full9[w]=Part.makeCylinder(r,9.25 if w=='W078' else 9,A.Vector(x,-24,48.1),A.Vector(1,0,0))
    spine=box((-88.55,-21.4,44.),(-46.55,-18.4,46.))
    clip=pads[0].fuse(pads[1]).fuse(spine);clip.check(True);assert len(clip.Solids)==1
    post=box((-51.6,-57,38.52),(-46.6,-53,44.5))
    arm=box((-51.6,-55,41.),(-46.6,-18.4,44.5))
    root=clip.fuse(post).fuse(arm)
    # The retained P0 mount has an inherited BOP error. Keep new PETG OUTSIDE
    # its complete conservative bounds+1.25, without inferring a real collision.
    mount=scene['Ref_Material_P0_MountFrontR_0_0'].optimalBoundingBox(False,False);margin=1.25
    exclusion=box((mount.XMin-margin,mount.YMin-margin,mount.ZMin-margin),
        (mount.XMax+margin,mount.YMax+margin,mount.ZMax+margin))
    root=root.cut(exclusion);bands={}
    for w,x,r in [('W077',-87.15,2.),('W078',-51.05,1.05)]:
        top=48.1+r
        outer=box((x-1.25,-29.3,42.6),(x+1.25,-18.7,top+1.2))
        inner=box((x-2,-28.1,43.8),(x+2,-19.9,top))
        band=outer.cut(inner);head=box((x-2.5,-18.9,top-2.65),(x+2.5,-14.4,top+2.65))
        band=band.fuse(head);band.check(True);assert len(band.Solids)==1;bands[w]=band
        clear_outer=box((x-1.4,-29.45,42.45),(x+1.4,-18.55,top+1.35))
        clear_inner=box((x-2,-27.95,43.95),(x+2,-20.05,top-.15))
        root=root.cut(clear_outer.cut(clear_inner))
    root.check(True);assert len(root.Solids)==1
    assert root.common(exclusion).Volume<1e-7
    assert all(root.common(b).Volume<1e-7 for b in bands.values())
    joined=rail.fuse(root);joined.check(True);assert len(joined.Solids)==1
    assert rail.cut(joined).Volume<1e-7
    assert all(clip.common(s).Volume<1e-6 for s in full9.values())
    return joined,root,full9,bands,dict(replaces='SpliceClip full rectangular cuff reservations, not a purchased clamp',
        source_constructor='check_feline_n01_coupled_pi_bus:clip_parts from n01-central-spine-power-plan-r4.json',
        full9_jacket_lands_mm={'W077':[-88.55,-79.55],'W078':[-55.55,-46.55]},
        channel_project_radius_mm={'W077':2.,'W078':1.05},channel_radial_assembly_clearance_mm=.15,
        W078_reference_jacket_length_mm=9.25,full_gripped_length_mm=9.,W078_body_cap_mm=[-46.3,-24,48.1],
        solder_sleeve_unchanged=True,sleeve_to_spine_nominal_gap_mm=.5,
        positive_root_to_retained_rail_mm3=root.common(rail).Volume,
        no_original_rail_material_removed_mm3=rail.cut(joined).Volume,
        independent_T18I100_per_jacket=1,tie_quantity=2,
        tie_nominal_budget_mm=2*(8.2+8.2)+27,
        tie_threading_windows_mm=dict(width=2.8,centres_X=[-87.15,-51.05],lower_Z=[42.45,43.95]),
        conservative_P0_exclusion_mm=[[mount.XMin-margin,mount.YMin-margin,mount.ZMin-margin],[mount.XMax+margin,mount.YMax+margin,mount.ZMax+margin]],
        retained_W077_full9_jacket_to_P0_bounds_Y_gap_mm=(-26.)-mount.YMax,
        W077_band_to_P0_bounds_X_gap_mm=mount.XMin-(-87.15+1.25),
        side_walls_stop_at_wire_centre_for_actual_band_contact=True,
        actual_pull_strength_and_threading_fit_phase2_OPEN=True,
        one_revision_of_negative_foundation_print_owner=True,not_physical_strength_PASS=True)


def complete_gaux_front(source_rec,endpoints,late_head_descent=False):
    """Critical G2/S0/HP approaches; open shared columns between interfaces."""
    import math
    import prototype_layout_review_20261024 as base
    shapes={};recipes={}
    for w in ['XA05','XB23','XB13']:
        row=endpoints['rows'][w];q=row['remote']['point_mm'];parts=list(source_rec[w]['parts']);p=parts[-1]['end']
        if w=='XA05':
            c=[p[0],43.,p[2]];d=[q[0],43.,q[2]];v=A.Vector(*d)-A.Vector(*c);R=v.Length/2
            bend=list(v.normalize())
            turn=dict(kind='arc',start=c,end=d,tangent=[0,-1,0],bend=bend,radius=R,
                angle=math.pi,length=math.pi*R,end_tangent=[0,1,0])
            parts += [base.tr.line(p,c),turn,base.tr.line(d,q)]
            reason='One tilted half-turn outside F_PI/S0 casing, above P0 beam; G2 last full9 kept. Wider47mm source corner allocates the whole fold.'
        elif w=='XB23':
            z=p[2];c=[-80.,47.5,z];d=[-92.6,47.5,z+12.6];e=[-92.6,47.5,81.];q=[-117.46,36.4,103.]
            parts += [base.tr.arc(p,(0,-1,0),c),base.tr.arc(c,(-1,0,0),d),base.tr.line(d,e),*base.tr.biarc(e,(0,0,1),q,(-1,0,0))]
            reason='Rise outside ForeFHAC and approach exposed +Y side of HP row; finish-35 was not a connector. Head/moving source and proper final source cylinder retained.'
        else:
            tier=61.+1.05+1.25
            entry=[-65.,39.5,tier];c=[-65.,-16.35,tier];d=[-80.,-31.35,tier];k=[-120.,-31.35,q[2]]
            parts += [*base.tr.biarc(p,(0,-1,0),entry,(0,-1,0)),base.tr.line(entry,c),base.tr.arc(c,(0,-1,0),d)]
            if late_head_descent:
                late=[-128.,-31.35,tier]
                parts += [base.tr.line(d,late),*base.tr.biarc(late,(-1,0,0),q,[-v for v in row['remote']['outward']])]
            else:
                parts += [*base.tr.biarc(d,(-1,0,0),k,(-1,0,0)),
                    *base.tr.biarc(k,(-1,0,0),q,[-v for v in row['remote']['outward']])]
            reason='Lower shared front column passes above F_PI and below S0 key, then whole S0/S1 gap. Final yaw approach reused from D trial.'
        minimum=min(p.get('radius',math.inf) for p in parts);assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        body=base.solid(parts,row['radius_mm']);body.check(True);shapes[w]=body
        recipes[w]=dict(parts=parts,reason=reason,length_mm=base.tr.length(parts),minimum_R_mm=minimum,
            radius_mm=row['radius_mm'],source=row['local'],receiver_nominal=row['remote'],final_mm=q,
            source_profile_assumptions_and_motion_fit_not_supplier_certification=True)
    return shapes,recipes


def regroup_common_ground(groups,endpoints,front_destination_order=False):
    """One common-rail physical permutation, not a changed electrical pinout."""
    import copy,Part
    new={n:s.copy() for n,s in groups.items()};ends=copy.deepcopy(endpoints)
    mapping=[('XA04',2),('XA06',5),('XA05',1),('XB23',3),('XB13',4)]
    if front_destination_order:mapping=[('XA04',2),('XA06',5),('XB13',4),('XB23',3),('XA05',1)]
    rows=[]
    pad=Part.makeBox(9,3.25,25.5,A.Vector(-8.75,89.25,44.25))
    for physical,(w,logical) in enumerate(mapping,1):
        z=66.5-(physical-1)*4.75;r=ends['rows'][w]['radius_mm']
        actor=f'Station:G_AUX:wire:G_AUX.{logical}'
        new[actor]=Part.makeCylinder(r,9.25,A.Vector(.5,92.5,z),A.Vector(-1,0,0))
        bore=Part.makeCylinder(r+.15,11,A.Vector(-9.75,92.5,z),A.Vector(1,0,0))
        pad=pad.cut(bore)
        ends['rows'][w]['local'].update(point_mm=[-8.75,92.5,z],radius_mm=r,
            physical_slot=physical,logical_common_rail_endpoint=f'G_AUX.{logical}')
        rows.append(dict(wire=w,logical_endpoint=f'G_AUX.{logical}',physical_slot=physical,
            source_cap_mm=[-8.75,92.5,z],radius_mm=r))
    pad.check(True);assert len(pad.Solids)==1
    new['Station:G_AUX:split_common_comb']=pad
    return new,ends,dict(common_net_unchanged=True,purchased_part_unchanged=True,
        physical_slot_map=rows,full_grip_mm=9.,no_external_pinout_inferred=True,
        old_contract_not_overwritten=True)


def upper_ground_source_fan(endpoints):
    """Ordered front/rear bifurcation above the measured folding-knee sweep."""
    import math
    import prototype_layout_review_20261024 as base
    shapes={};recipes={}
    targets={'XA04':74.21,'XA06':69.46,'XA05':66.,'XB23':62.,'XB13':58.}
    for w,z in targets.items():
        row=endpoints['rows'][w];p=row['local']['point_mm'];a=[-35.,92.5,z]
        parts=base.tr.biarc(p,(-1,0,0),a,(-1,0,0))
        if w in ('XA04','XA06'):
            R=15. if w=='XA04' else 19.75;b=[-35.,92.5,z+2*R]
            parts.append(dict(kind='arc',start=a,end=b,tangent=[-1,0,0],bend=[0,0,1],
                radius=R,angle=math.pi,length=math.pi*R,end_tangent=[1,0,0]))
        else:
            R=47. if w=='XA05' else 30.;b=[-35.-R,92.5-R,z]
            parts.append(base.tr.arc(a,(-1,0,0),b))
        minimum=min(p.get('radius',math.inf) for p in parts)
        assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        s=base.solid(parts,row['radius_mm']);s.check(True);shapes[w]=s
        recipes[w]=dict(parts=parts,source=row['local'],end_mm=b,
            length_mm=base.tr.length(parts),minimum_R_mm=minimum,radius_mm=row['radius_mm'],
            shared_upper_reverse_centre_Z_mm=89.21 if w in ('XA04','XA06') else None,
            partial_source_transition_only=True,whole_receiver_and_route_NOT_received=True)
    return shapes,recipes


def top_exit_ground_station(groups,endpoints,scene):
    """M: orient the entire common-ground station above the folded front leg."""
    import copy,Part
    def box(lo,hi):return Part.makeBox(*(hi[i]-lo[i] for i in range(3)),A.Vector(*lo))
    mat=A.Matrix();mat.A11=0;mat.A12=1;mat.A13=0
    mat.A21=0;mat.A22=0;mat.A23=-1;mat.A31=-1;mat.A32=0;mat.A33=0
    rot=A.Rotation(mat);assert abs(rot.multVec(A.Vector(-1,0,0)).z-1)<1e-8
    tf=A.Placement(A.Vector(10,84,61.35),rot)*A.Placement(A.Vector(-10,-92.5,-57),A.Rotation())
    result={n:s.copy() for n,s in groups.items()};ends=copy.deepcopy(endpoints)
    for n,s in result.items():
        if n.startswith('Station:G_AUX:'):s.Placement=tf*s.Placement
    band=result['Station:G_AUX:band_budget'].optimalBoundingBox(False,False)
    result['Station:G_AUX:head_budget']=box((band.XMax,81.35,band.Center.z-2.5),
        (band.XMax+4.3,86.65,band.Center.z+2.5))
    for w in ('XA04','XA06','XA05','XB23','XB13'):
        p=ends['rows'][w]['local'];p['point_mm']=list(tf.multVec(A.Vector(*p['point_mm'])))
        p['outward']=[0,0,1]
    foot=box((3.,68.,48.35),(15.5,99.,51.35))
    for y in (74.,94.):foot=foot.cut(box((2.,y-1.4,48.85),(16.5,y+1.4,50.35)))
    comb=result['Station:G_AUX:split_common_comb'];b=comb.optimalBoundingBox(False,False)
    wall=box((3.,b.YMin,48.35),(4.25,b.YMax,b.ZMax))
    bridge=box((3.,b.YMin,b.ZMin),(6.95,b.YMax,b.ZMin+2.))
    carrier=foot.fuse(wall).fuse(bridge).fuse(comb);carrier.check(True);assert len(carrier.Solids)==1
    arm=box((7.,55.,45.35),(13.,98.5,48.35));post=box((7.,55.,38.52),(13.,59.,48.35))
    old=scene['CurrentFoundation:FoundationRail:1'];rail=old.fuse(post).fuse(arm);rail.check(True)
    assert old.cut(rail).Volume<1e-7 and len(rail.Solids)<=len(old.Solids)
    assert carrier.common(rail).Volume<1e-7 and carrier.distToShape(rail)[0]<1e-7
    assert comb.cut(carrier).Volume<1e-7
    return result,ends,rail,carrier,dict(case_centre_mm=[10,84,61.35],source_direction=[0,0,1],
        case_bounds_mm=[[5.5,69.,51.85],[14.5,99.,70.85]],full_source_grip_mm=9.,
        cap_Z_mm=80.10,same_common_ground_map=True,purchased_parts_unchanged=True,
        wire_tie_head_repositioned_to_free_positive_X_side=True,
        carrier_one_solid=True,positive_rail_original_material_removed_mm3=old.cut(rail).Volume,
        carrier_rail_positive_post_union_mm3=old.common(post).Volume,
        carrier_fixing_ties=2,wire_relief_tie=1,case_tape_gap_mm=.5,
        assembly='Open side/top; place case on carrier with source comb and band on bench; lower complete carrier onto fixed arm, thread two fixing ties through horizontal windows. Free ends routed before closing skin. Parking/full factory slack OPEN.',
        arm_and_post_bounds_mm=[[[7,55,45.35],[13,98.5,48.35]],[[7,55,38.52],[13,59,48.35]]],
        provisional_not_strength_or_physical_PASS=True)


def top_exit_ground_branches(endpoints,roof_lane_Z=None,all_positive_X=False):
    """All five lanes together: separate Y rows, no reversed low source fan."""
    import math
    import prototype_layout_review_20261024 as base
    shapes={};recipes={}
    for w in ('XA04','XA06','XA05','XB23','XB13'):
        row=endpoints['rows'][w];p=row['local']['point_mm'];y=p[1]
        z=p[2]+15 if roof_lane_Z is None else (roof_lane_Z[w] if isinstance(roof_lane_Z,dict) else roof_lane_Z)
        rear=w in ('XA04','XA06') or all_positive_X;sign=1 if rear else -1
        start=[p[0],y,z-15];a=[p[0]+sign*15,y,z]
        parts=([base.tr.line(p,start)] if start[2]>p[2]+1e-7 else [])+[base.tr.arc(start,(0,0,1),a)]
        if roof_lane_Z is not None and not rear:
            parts.append(base.tr.line(a,[-20.,y,z]))
        if not rear:
            if roof_lane_Z is not None:
                minimum=min(p.get('radius',math.inf) for p in parts)
                s=base.solid(parts,row['radius_mm']);s.check(True);shapes[w]=s
                recipes[w]=dict(parts=parts,source=row['local'],end_mm=parts[-1]['end'],length_mm=base.tr.length(parts),
                    minimum_R_mm=minimum,radius_mm=row['radius_mm'],whole_receiver_and_route_NOT_received=True)
                continue
            b=[-20.,y,z];c=[-35.,y,z-15];d=[-50.,y,z-30]
            parts += [base.tr.line(a,b),base.tr.arc(b,(-1,0,0),c),base.tr.arc(c,(0,0,-1),d)]
            R=32. if w=='XA05' else 15.;e=[d[0]-R,y-R,d[2]]
            parts += [base.tr.arc(d,(-1,0,0),e)]
            if w=='XB23':parts.append(base.tr.line(e,[-65.,62.5,d[2]]))
        minimum=min(p.get('radius',math.inf) for p in parts);assert minimum>=row['minimum_R_mm']-1e-6
        s=base.solid(parts,row['radius_mm']);s.check(True);shapes[w]=s
        recipes[w]=dict(parts=parts,source=row['local'],end_mm=parts[-1]['end'],
            length_mm=base.tr.length(parts),minimum_R_mm=minimum,radius_mm=row['radius_mm'],
            source_bifurcation='two rear +X / three front -X, separate Y rows',
            whole_receiver_and_route_NOT_received=True)
    return shapes,recipes


def raised_top_station(groups,endpoints,scene,centre_X=11.8):
    """M2: seat on the existing bank bed, independently rooted outer ledge."""
    import copy,Part
    dx=centre_X-11.8
    def box(lo,hi):return Part.makeBox(*(hi[i]-lo[i] for i in range(3)),A.Vector(lo[0]+dx,lo[1],lo[2]))
    result={n:s.copy() for n,s in groups.items()};ends=copy.deepcopy(endpoints);delta=A.Vector(1.8+dx,0,6.65)
    for n,s in result.items():
        if n.startswith('Station:G_AUX:'):s.translate(delta)
    for w in ('XA04','XA06','XA05','XB23','XB13'):
        local=ends['rows'][w]['local'];local['point_mm']=list(A.Vector(*local['point_mm'])+delta)
    foot=box((4.8,69.,55.),(17.3,99.,58.))
    for y in (74.,94.):foot=foot.cut(box((3.8,y-1.4,55.5),(18.3,y+1.4,57.)))
    comb=result['Station:G_AUX:split_common_comb'];b=comb.optimalBoundingBox(False,False)
    wall=box((4.8,b.YMin,55.),(6.05,b.YMax,b.ZMax))
    bridge=box((4.8,b.YMin,b.ZMin),(8.75,b.YMax,b.ZMin+2))
    carrier=foot.fuse(wall).fuse(bridge).fuse(comb);carrier.check(True);assert len(carrier.Solids)==1
    arm=box((8.8,55.,47.75),(14.8,98.5,50.75));post=box((8.8,55.,38.52),(14.8,59.,50.75))
    seat=box((8.8,81.25,50.5),(14.8,98.5,55.))
    old=scene['CurrentFoundation:FoundationRail:1'];rail=old.fuse(post).fuse(arm).fuse(seat);rail.check(True)
    assert old.cut(rail).Volume<1e-7 and len(rail.Solids)<=len(old.Solids)
    bed=scene['CurrentFoundation:BankBedCurrent:1']
    assert carrier.common(bed).Volume<1e-7 and carrier.distToShape(bed)[0]<1e-7
    assert carrier.common(rail).Volume<1e-7 and carrier.distToShape(rail)[0]<1e-7
    cells={'arm':[[8.8,55,47.75],[14.8,98.5,50.75]],'post':[[8.8,55,38.52],[14.8,59,50.75]],'seat':[[8.8,81.25,50.5],[14.8,98.5,55.]]}
    for lo,hi in cells.values():lo[0]+=dx;hi[0]+=dx
    return result,ends,rail,carrier,dict(case_centre_mm=[centre_X,84,68.],cap_Z_mm=86.75,
        physical_rows_Y_mm=[74.5,79.25,84,88.75,93.5],case_tape_gap_mm=.5,
        carrier_one_solid=True,unchanged_bed_face_bearing_Z_mm=55.,
        carrier_rail_positive_post_union_mm3=old.common(post).Volume,
        no_old_rail_material_removed_mm3=old.cut(rail).Volume,
        arm_clearance_below_existing_bed_mm=1.25,outer_seat_clearance_to_bed_Y_mm=1.25,
        fixing_ties=2,wire_relief_tie=1,assembly_method='Bench module; open top/side; lower onto retained bed face and separate rail-rooted outer seat; two fixing ties. Full attached-end assembly parking still OPEN.',
        new_fixed_cells=cells,
        source_common_ground_map_unchanged=True,not_physical_PASS=True)


def bed_edge_retained_carrier(carrier,scene):
    """Two short removable ties through the shoe, using the retained bed load path."""
    import Part
    def box(lo,hi):return Part.makeBox(*(hi[i]-lo[i] for i in range(3)),A.Vector(*lo))
    body=carrier.copy();ties={};heads={};bed=scene['CurrentFoundation:BankBedCurrent:1'];revised_bed=bed.copy()
    for i,x in enumerate((59.5,64.),1):
        # The upper strap is recessed below the case, never over its levers.
        top=box((x-1.4,72.65,55.65),(x+1.4,84.35,57.15))
        slots=[box((x-1.4,y0,54.9),(x+1.4,y1,57.15)) for y0,y1 in ((72.65,74.15),(82.85,84.35))]
        body=body.cut(top).cut(slots[0]).cut(slots[1])
        # Two tie slots in NEW revision of the printed bed, outside all
        # housing bearing strips (Y<=67.75); never cut purchased hardware.
        revised_bed=revised_bed.cut(box((x-1.4,72.65,51.),(x+1.4,74.15,56.)))
        revised_bed=revised_bed.cut(box((x-1.4,72.65,51.9),(x+1.4,80.1,53.35)))
        outer=box((x-1.25,72.8,52.),(x+1.25,84.2,57.))
        inner=box((x-2.,74.,53.2),(x+2.,83.,55.8))
        ties[str(i)]=outer.cut(inner)
        heads[str(i)]=box((x-2.5,84.2,51.95),(x+2.5,88.5,57.25))
        ties[str(i)].check(True);heads[str(i)].check(True)
    body.check(True);assert len(body.Solids)==1
    revised_bed.check(True);assert len(revised_bed.Solids)==len(bed.Solids)
    protected=box((-100,39.25,51.),(150,67.75,56.))
    assert bed.cut(revised_bed).common(protected).Volume<1e-7
    assert body.common(revised_bed).Volume<1e-7
    assert body.distToShape(revised_bed)[0]<1e-7
    for t in ties.values():
        assert t.common(revised_bed).Volume<1e-7
        assert t.common(body).Volume<1e-7
    return body,ties,heads,revised_bed,dict(load_path='Case -> adhesive bearing -> PETG shoe -> BankBed face/root network -> frame; two independent shoe ties resist lift/overhang',
        added_fixed_rail_arm_and_post_retired=True,purchased_parts_unchanged=True,
        printed_bed_revision_two_tie_slots_only=True,bed_material_removed_mm3=bed.cut(revised_bed).Volume,
        housing_bearing_material_removed_mm3=0.,
        shoe_tie_centres_X_mm=[59.5,64.],shoe_slots_Y_mm=[[72.65,74.15],[82.85,84.35]],
        upper_strap_recess_Z_mm=[55.65,57.15],case_bottom_Z_mm=58.5,
        selected_fixing_tie_qty=2,nominal_length_budget_each_mm=2*(11.4+5.)+27.,
        full_1p2mm_lower_strap_recessed_into_printed_bed=True,bed_understrap_recess_Z_mm=[52.,53.35],
        minimum_remaining_bed_web_above_recess_mm=1.65,
        source_wire_tie_separate=True,physical_pull_threading_and_strength_phase2_OPEN=True,
        planned_lowering_with_top_side_panels_removed=True,
        five_attached_ends_service_parking_NOT_received=True)


def constant_torso_section_bounds(shapes):
    """Conservative exact-parametric rounded-section check in the flat-width span.

    The saved outer BRep fails strict BOP; never use its failed Boolean as
    containment. This only uses the unchanged pinned200-wide section recipe,
    valid for the complete X[-128,145] interval, radius12, Z[-48,112].
    """
    import itertools,math
    result=[]
    for n,s in shapes.items():
        b=s.optimalBoundingBox(False,False)
        if b.XMin < -128 or b.XMax>145:
            result.append(dict(owner=n,status='OUTSIDE_CONSTANT_SECTION_DOMAIN_NOT_QUALIFIED'));continue
        gaps=[]
        for y,z in itertools.product((b.YMin,b.YMax),(b.ZMin,b.ZMax)):
            qy=abs(y)-88.;qz=abs(z-32.)-68.
            signed=math.hypot(max(qy,0),max(qz,0))+min(max(qy,qz),0)-12
            gaps.append(-signed)
        gap=min(gaps)
        result.append(dict(owner=n,conservative_box_boundary_gap_mm=gap,
            conservative_box_inside=gap>=-1e-7,default_skin_air_budget_mm=3.25,
            conservative_default_budget_received=gap>=3.25-1e-7,
            negative_bound_not_actual_contact=True))
    return result


def ground_service_bight():
    """One nine-ish by eight bundle budget for five CUSTOM leads, no factory slack."""
    import math
    import prototype_layout_review_20261024 as base
    R=20.;p=[140.,91.,55.];a=[130.,91.,55.];b=[130.,91.,95.];q=[140.,91.,95.]
    parts=[base.tr.line(p,a),dict(kind='arc',start=a,end=b,tangent=[-1,0,0],bend=[0,0,1],
        radius=R,angle=math.pi,length=math.pi*R,end_tangent=[1,0,0]),base.tr.line(b,q)]
    envelope=base.solid(parts,4.);envelope.check(True)
    return envelope,dict(parts=parts,bundle_envelope_radius_mm=4.,
        five_custom_wires=['XA04','XA06','XA05','XB23','XB13'],
        transverse_pack_mm={'power_row_Y':[-2.7,0,2.7],'power_radius':1.25,
            'signal_row_Y':[-1.35,1.35],'signal_row_normal':-2.3382685902,'signal_radius':1.05},
        maximum_nominal_packed_radius_mm=3.95,retained_wire_gap_mm=.2,
        common_centreline_length_mm=base.tr.length(parts),minimum_possible_inner_radius_mm=16.,
        provisional_custom_service_allowance_each_mm=100.,factory900_or_4MTA_allowance_added_mm=0.,
        no_source_or_receiver_branches_yet=True,not_entire_length_or_parking_PASS=True)


def packed_ground_service_bight():
    """One transported five-core pack; the prior round envelope was overbroad."""
    import math
    import prototype_layout_review_20261024 as base
    from plan_feline_FL_three_core_shared_trunk import transport
    _,rec=ground_service_bight();parts=rec['parts']
    for p in parts:
        p['start'][1]=92.;p['end'][1]=92.
    pack=[('XA04',[0,0,-2.7],1.25),('XA06',[0,0,0],1.25),('XA05',[0,0,2.7],1.25),
          ('XB23',[0,2.3382685902,-1.35],1.05),('XB13',[0,2.3382685902,1.35],1.05)]
    shapes={};rows={}
    for w,offset,r in pack:
        path,_=transport(parts,offset);s=base.solid(path,r);s.check(True);shapes[w]=s
        minimum=min(p.get('radius',math.inf) for p in path)
        assert minimum>=(15. if r==1.25 else 12.6)-1e-6
        rows[w]=dict(parts=path,offset_mm=offset,radius_mm=r,minimum_R_mm=minimum,
            bight_path_length_mm=base.tr.length(path),custom_design_allowance_mm=100.,
            factory_allowance_added_mm=0.)
    return shapes,dict(whole_pack=rows,nominal_Y_extent_mm=[90.75,95.3882685902],
        source_and_receiver_branches_OPEN=True,not_full_service_parking=True,
        same_shared_U_frame=True,round_envelope_overlap_not_actual_wire_contact=True,
        no_manufacturer_stock_or_factory_length_change=True)


def common_positive_bundle_passage(scene,carrier):
    """Dogleg our printed U1 upper cross, instead of five cable detours.

    Keep the accepted46.6mm beam tier, complete clamp and lower U1 root.
    One shared clearance box also opens the new shoe's overhanging underside.
    """
    import Part
    def box(lo,hi):return Part.makeBox(*(hi[i]-lo[i] for i in range(3)),A.Vector(*lo))
    old=scene['U1Carrier:Fore:Base'];old.check(True)
    passage=box((20.,89.5,46.4),(84.,96.6382685902,56.8))
    cells={'cross':box((24.,85.5,46.6),(44.,89.5,50.6)),
        'inner_pillar':box((40.,85.5,42.4),(44.,89.5,50.6)),
        'lower_elbow':box((40.,85.5,42.4),(44.,95.2,46.4))}
    revised=old.cut(passage).multiFuse(list(cells.values()));revised.check(True);assert len(revised.Solids)==1
    revised_carrier=carrier.cut(passage);revised_carrier.check(True);assert len(revised_carrier.Solids)==1
    # Coincident cut-plane COMMON leaves nonvolumetric BOP-error faces in
    # this kernel. Never qualify clearance from that result. The valid full
    # solids require actual profile/primitive-distance checks separately.
    root=scene['U1Relief:ForeRoot'];before=old.common(root);after=revised.common(root)
    assert before.Volume>0 and abs(before.Volume-after.Volume)<1e-7
    whole=revised.fuse(root);whole.check(True);assert len(whole.Solids)==1
    added=revised.cut(old);added.check(True)
    return revised,revised_carrier,cells,dict(source_constructor='plan_feline_u1_common_carrier.construct:Fore',
        shared_occupied_Y_mm=[90.75,95.3882685902],shared_occupied_Z_mm=[47.65,55.55],
        rigid_clearance_mm=1.25,passage_bounds_mm=[[20,89.5,46.4],[84,96.6382685902,56.8]],
        source_beam_lower_Z_unchanged_mm=46.6,complete_clamp_and_purchased_hardware_unchanged=True,
        original_fore_root_union_mm3=before.Volume,new_fore_root_union_mm3=after.Volume,
        new_U1_base_one_solid=True,new_base_and_root_one_solid=True,new_shoe_one_solid=True,
        shoe_roof_above_shared_passage_mm=1.2,
        removed_printed_U1_mm3=old.cut(revised).Volume,added_printed_U1_mm3=added.Volume,
        no_purchased_part_or_P0_cut=True,physical_strength_and_print_fit_OPEN=True)


def whole_ground_common_service(endpoints):
    """All five custom leads use one rear U and the same lower gallery.

    This ends at the shared X80 split. Neither remote branches nor factory
    lengths are certified merely by receiving this common source assembly.
    """
    import math
    import prototype_layout_review_20261024 as base
    from plan_feline_FL_three_core_shared_trunk import transport
    levels={w:101.75 if w=='XA05' else 107.1 for w in endpoints['rows']}
    _,source_rec=top_exit_ground_branches(endpoints,levels,all_positive_X=True)
    p=[110.,92.,95.];a=[120.,92.,95.];b=[120.,92.,55.];c=[110.,92.,55.];q=[80.,92.,51.6]
    common=[base.tr.line(p,a),dict(kind='arc',start=a,end=b,tangent=[1,0,0],bend=[0,0,-1],
        radius=20.,angle=math.pi,length=math.pi*20.,end_tangent=[-1,0,0]),base.tr.line(b,c),
        *base.tr.biarc(c,(-1,0,0),q,(-1,0,0))]
    offsets={'XA04':[0,0,2.7],'XA06':[0,0,0],'XA05':[0,0,-2.7],
        'XB23':[0,2.3382685902,-1.35],'XB13':[0,2.3382685902,1.35]}
    shapes={};recipes={}
    for w,offset in offsets.items():
        row=endpoints['rows'][w];shared,last_offset=transport(common,offset)
        prefix=source_rec[w]['parts'];end=prefix[-1]['end'];target=shared[0]['start']
        fan=base.tr.biarc(end,(1,0,0),target,(1,0,0));parts=prefix+fan+shared
        minimum=min(p.get('radius',math.inf) for p in parts);assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        s=base.solid(parts,row['radius_mm']);s.check(True);shapes[w]=s
        recipes[w]=dict(parts=parts,source=row['local'],split_mm=shared[-1]['end'],split_tangent=[-1,0,0],
            partial_length_mm=base.tr.length(parts),radius_mm=row['radius_mm'],minimum_R_mm=minimum,
            fan_minimum_R_mm=min(p.get('radius',math.inf) for p in fan),
            packed_offset_start_mm=offset,packed_offset_finish_mm=list(last_offset),
            included_service_U_and_legs_mm=base.tr.length(shared[:3]),
            source_grip_extra_to_add_mm=9.25,service_loop_already_included_not_added_twice=True,
            factory_length_added_mm=0.,receiver_branch_NOT_received=True)
    return shapes,recipes


def complete_destination_ordered_front(source_rec,endpoints,fore_detour=False):
    """Three whole constructive front branches, no added tethered-service U."""
    import math
    import prototype_layout_review_20261024 as base
    shapes={};recipes={}
    for w in ('XA05','XB23','XB13'):
        row=endpoints['rows'][w];q=row['remote']['point_mm'];parts=list(source_rec[w]['parts'])
        p=parts[-1]['end'];dropR=17. if fore_detour and w=='XB13' else 15.
        if fore_detour:
            start=[-33.,p[1],p[2]];parts.append(base.tr.line(p,start));p=start
        a=[p[0]-dropR,p[1],p[2]-dropR];b=[p[0]-2*dropR,p[1],p[2]-2*dropR]
        parts += [base.tr.arc(p,(-1,0,0),a),base.tr.arc(a,(0,0,-1),b)]
        R=12.6 if fore_detour and w=='XB23' else p[1]-69.
        c=[b[0]-R,p[1]-R,b[2]];parts.append(base.tr.arc(b,(-1,0,0),c))
        if w=='XA05':
            d=[-82.,43.,c[2]];e=[q[0],43.,q[2]]
            parts += base.tr.biarc(c,(0,-1,0),d,(0,-1,0))
            v=A.Vector(*e)-A.Vector(*d);radius=v.Length/2
            parts += [dict(kind='arc',start=d,end=e,tangent=[0,-1,0],bend=list(v.normalize()),
                radius=radius,angle=math.pi,length=math.pi*radius,end_tangent=[0,1,0]),base.tr.line(e,q)]
            boundary='Current G2 fixed full9 cap; existing printed portal received separately'
        elif w=='XB23':
            turnY=62.5 if fore_detour else 60.1
            d=[c[0],turnY,c[2]];e=[c[0]-15,turnY-15,c[2]];q=[-117.46,36.4,103.]
            parts += [base.tr.line(c,d),base.tr.arc(d,(0,-1,0),e),*base.tr.biarc(e,(-1,0,0),q,(-1,0,0))]
            boundary='Protected head source cap at-117.46; retire only the old arbitrary straight accounting tail to-35, no purchased lead cut'
        else:
            if fore_detour:
                d=[-141.,43.,c[2]];e=[-141.,-17.95,c[2]];f=[-141.,-30.55,c[2]-12.6]
                low=[-141.,-30.55,30.];g=[-139.4,-30.55,q[2]+12.6];h=[-139.4,-43.15,q[2]]
                parts += [*base.tr.biarc(c,(0,-1,0),d,(0,-1,0)),base.tr.line(d,e),
                    base.tr.arc(e,(0,-1,0),f),base.tr.line(f,low),*base.tr.biarc(low,(0,0,-1),g,(0,0,-1)),
                    base.tr.arc(g,(0,0,-1),h),base.tr.arc(h,(0,-1,0),q)]
            else:
                d=[-65.,-16.35,c[2]];e=[-80.,-31.35,c[2]];late=[-126.8,-30.55,c[2]]
                f=[-139.4,-30.55,c[2]-12.6];g=[-139.4,-30.55,q[2]+12.6];h=[-139.4,-43.15,q[2]]
                parts += [base.tr.line(c,d),base.tr.arc(d,(0,-1,0),e),
                    *base.tr.biarc(e,(-1,0,0),late,(-1,0,0)),base.tr.arc(late,(-1,0,0),f),
                    base.tr.line(f,g),base.tr.arc(g,(0,0,-1),h),base.tr.arc(h,(0,-1,0),q)]
            boundary='Same SelectedYaw/JR/factory250 cap; descend beyond complete hip and S1, approach from the existing cap tangent'
        minimum=min(p.get('radius',math.inf) for p in parts);assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        s=base.solid(parts,row['radius_mm']);s.check(True);shapes[w]=s
        recipes[w]=dict(parts=parts,source=row['local'],receiver_nominal=row['remote'],actual_final_mm=q,
            body_length_mm=base.tr.length(parts),minimum_R_mm=minimum,radius_mm=row['radius_mm'],
            receiver_boundary=boundary,nominal_source_grip_extra_mm=9.25,
            added_factory_length_mm=0.,added_unordered_service_loop_mm=0.,
            whole_fore_S0_detour=fore_detour,
            assembly='Install carrier/case first, route free custom ends, terminate receiver ends afterward; rare carrier removal may disconnect its5localWAGO ends. No74routine disconnections or rapidPi repair requirement.',
            physical_fit_motion_and_whole_N01_NOT_automatically_received=True)
    return shapes,recipes


def complete_destination_rear(source_rec,endpoints):
    """Two rear receivers using their existing whole prefixes, no new U-loop."""
    import math
    import prototype_layout_review_20261024 as base
    shapes={};recipes={}
    for w in ('XA04','XA06'):
        row=endpoints['rows'][w];parts=list(source_rec[w]['parts']);p=parts[-1]['end']
        q=row['remote']['point_mm'];incoming=[-v for v in row['remote']['outward']]
        if w=='XA04':
            # Cross above the BUS from its west side. The old aft crossing
            # approached AuxEscape against its tangent and forced R11.05.
            a=[100.,p[1],p[2]];b=[115.,p[1]-15,p[2]];c=[115.,-25.,p[2]]
            parts += [base.tr.line(p,a),base.tr.arc(a,(1,0,0),b),base.tr.line(b,c),
                *base.tr.biarc(c,(0,-1,0),q,incoming)]
        else:parts += base.tr.biarc(p,(1,0,0),q,incoming)
        minimum=min(p.get('radius',math.inf) for p in parts);assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        s=base.solid(parts,row['radius_mm']);s.check(True);shapes[w]=s
        recipes[w]=dict(parts=parts,source=row['local'],receiver=row['remote'],
            body_length_mm=base.tr.length(parts),minimum_R_mm=minimum,radius_mm=row['radius_mm'],
            unchanged_remote_prefix_owner=row['remote']['actor'],added_factory_length_mm=0.,
            added_unordered_service_loop_mm=0.,whole_motion_and_assembly_NOT_automatically_received=True)
    return shapes,recipes


def load_saved_gal25(resume=None):
    """One explicit hash-bound restart; no archive searches or source rebuild."""
    import json,zipfile,hashlib,Part
    from check_feline_harness_proposal import load_recovered_context
    from restore_feline_bound_service_actors import restore,restore_provider_receipt
    from check_main_p0_placement import ROOT
    from plan_feline_layout import OUT
    if resume is None:
        scene,meta,base=load_recovered_context()
        extra,restoration=restore(scene,base['unrecovered']);scene.update(extra)
    else:scene,meta,base,restoration=resume
    providers=json.loads((OUT/'n01-service-provider-actors-restored-20261024.json').read_text())
    # Some explicit current-provider owners were added after the old pin map.
    # Record fresh file pins honestly; the loader also verifies each selected
    # geometry entry and its whole archive hash. This is recovery, not reuse
    # of a nonexistent old source-validation receipt.
    fresh_pins={};resolved=dict(providers['source_sha256'])
    for relative in set(providers['owners'].values()):
        path=OUT/relative;key=path.relative_to(ROOT).as_posix()
        if key not in resolved:
            digest=hashlib.sha256(path.read_bytes()).hexdigest();resolved[key]=digest;fresh_pins[key]=digest
    providers=dict(providers,source_sha256=resolved)
    scene.update(restore_provider_receipt(scene,providers))
    # Add metadata only from the same explicitly bound provider receipts.
    for relative in set(providers['owners'].values()):
        doc=json.loads((OUT/relative).read_text());rows=doc.get('geometry',[])
        if isinstance(rows,dict):rows=[dict(v,name=k) for k,v in rows.items()]
        for row in rows:
            if row['name'] in scene:
                meta[row['name']]={**row,**row.get('metadata',{}),**meta.get(row['name'],{})}
    local_sources=json.loads((OUT/'n01-selected-local-head-tail-sources.json').read_text())
    for row in local_sources['parts']:
        n=row['name']
        if n in scene and not scene[n].Solids and not isinstance(meta.get(n,{}).get('nominal_profile_radius_mm'),(int,float)):
            meta[n]={**meta.get(n,{}), 'kind':row['kind'],'nominal_profile_radius_mm':row['nominal_profile_radius_mm'],
                'profile_basis':'Same selected physical wire/insulation identity from source builder; current geometry is independently recovered',
                'profile_only_NOT_old_geometry_or_clearance_receipt':True}
    def archived(packet,wanted=None):
        spec=packet['geometry_archive'];path=__import__('pathlib').Path(spec['path'])
        assert hashlib.sha256(path.read_bytes()).hexdigest()==spec['sha256']
        values={}
        with zipfile.ZipFile(path) as z:
            for n,r in spec['members'].items():
                if wanted is not None and n not in wanted:continue
                raw=z.read(r['member'])
                if 'sha256' in r:assert hashlib.sha256(raw).hexdigest()==r['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode());values[n]=s
        return values
    packet=json.loads((OUT/'prototype-shared-galleries-20261025-result.json').read_text(encoding='utf-8'))
    shapes=archived(packet)
    prior_packet=json.loads((OUT/'prototype-joint-endpoints-20261024-result.json').read_text(encoding='utf-8'))
    main=archived(prior_packet,{'Reference:MainSupportUnchanged'})['Reference:MainSupportUnchanged']
    pas=archived(json.loads((OUT/'n01-power-axial-saddle-20261024.json').read_text()))
    retired=('Station:D_RR:','Station:G_AUX:','MainSupported:')
    current={n:s for n,s in scene.items() if not n.startswith(retired) and n not in
        {'SharedPi:Carrier','SpliceClip','CurrentMiddle:W022','CurrentMiddle:W024','BankPortal2:Carrier',
         *('RRFlatResource:'+w+'/body/start' for w in ('W016','W017','W018'))}}
    current.update({n:s for n,s in shapes.items() if not n.startswith('UnconnectedServiceBight:')});current['MAINassembly']=main
    current.update({'PAS:'+n:s for n,s in pas.items()})
    current['BankPortal2:Carrier']=current.pop('BankPortal2:XA05_open')
    return scene,meta,current,packet,shapes,dict(restoration=restoration,
        missing_current=[n for n in base['unrecovered'] if n not in scene],
        explicit_provider_replay=True,no_archive_search=True,
        provider_file_pins_newly_recorded_NOT_old_validation=fresh_pins)


def swap_rear_common_ports(groups,endpoints):
    """Put the near G_TAIL return inside the far AUX return on the same GND rail."""
    import copy
    result={n:s.copy() for n,s in groups.items()};ends=copy.deepcopy(endpoints)
    a=ends['rows']['XA04']['local'];b=ends['rows']['XA06']['local']
    assert abs(a['radius_mm']-b['radius_mm'])<1e-8
    aa,bb=a['actor'],b['actor'];result[aa],result[bb]=result[bb],result[aa]
    a['point_mm'],b['point_mm']=b['point_mm'],a['point_mm']
    a['physical_slot'],b['physical_slot']=b['physical_slot'],a['physical_slot']
    return result,ends,dict(same_common_ground_rail=True,same_purchased_part=True,
        same_physical_geometry_union_and_profiles=True,
        near_GTAIL_XA06_physical_slot=b['physical_slot'],far_AUX_XA04_physical_slot=a['physical_slot'],
        reason='Order two rear departures by destination; remove early Y crossing, no individual micro-offset',
        external_pinout_unchanged=True)


def bounded_changed_checks(changed,current,metadata,state,known_invalid=(),budget_seconds=40.,live_file=None,covers=None):
    """Changed pairs only, robust empty errors and a saved state before source work."""
    import time,json,os
    from feline_solid_distance import bbox_lower_bound,distance
    from receive_feline_jpwm_whole_pose import solid_profile_target
    tick=time.monotonic()
    def save():
        if live_file is not None:
            tmp=live_file.with_suffix('.tmp');tmp.write_text(json.dumps(state,ensure_ascii=False),encoding='utf-8');os.replace(tmp,live_file)
    for a,s in changed.items():
        if a in state['done']:continue
        s.check(True)
        for b,other in current.items():
            if a==b or [a,b] in state['visited']:continue
            m=metadata.get(b,{});reserve=m.get('nominal_profile_radius_mm',0) if not other.Solids else 0
            if not isinstance(reserve,(int,float)) or reserve<0 or (not other.Solids and reserve<=0):
                state['errors'].append(dict(new=a,actor=b,error='Unbound curve profile; no clearance inferred'))
                state['visited'].append([a,b]);continue
            pieces=(covers or {}).get(a,[s]);piece_bounds=[bbox_lower_bound(p.BoundBox,other.BoundBox) for p in pieces]
            local=[p for p,d in zip(pieces,piece_bounds) if d<=1.25+reserve]
            if not local:continue
            if time.monotonic()-tick>=budget_seconds:
                state['seconds']+=time.monotonic()-tick;save();return state
            state['last_pair']=[a,b];save()
            try:
                if b in known_invalid:raise ValueError('Known invalid source, not revalidated or accepted')
                if len(other.Faces)>250:raise ValueError('Complex unqualified source; bounded check does not run unbounded BOP')
                target=other.copy() if other.Solids else solid_profile_target(other,m)
                target.check(True)
                exact_near=min(distance(p.copy(),target) for p in local)
                far_bounds=[max(0.,d-reserve) for d in piece_bounds if d>1.25+reserve]
                gap=min([exact_near,*far_bounds])
                kind=m.get('kind','UNKNOWN_RETAINED_ACTOR')
                if b.startswith(('Service:','ATOAccess:')):kind='access_reservation'
                state['rows'].append(dict(new=a,existing=b,kind=kind,gap_mm=gap,
                    volume_not_inferred_from_touch=True,recipe_segment_cover_count=len(pieces),
                    exact_near_piece_count=len(local),gap_is_conservative_lower_bound=bool(covers) and exact_near>=1.25))
            except Exception as exc:
                message=str(exc).splitlines()
                state['errors'].append(dict(new=a,actor=b,error=message[0] if message else type(exc).__name__))
            state['visited'].append([a,b]);save()
        state['done'].append(a);save()
        print('GAL25_STATIC_PART',a,'rows',len(state['rows']),'errors',len(state['errors']),flush=True)
    state['seconds']+=time.monotonic()-tick;save();return state


def repack_front_middle_pair(out,vertical_transfer_mm=-5.):
    """Constant-length shared U-fold, no source move or new factory slack."""
    import copy,json,math
    import prototype_layout_review_20261024 as base
    from plan_feline_FL_three_core_shared_trunk import transport
    a=json.loads((out/'n01-current-W022-complete-body-plan.json').read_text(encoding='utf-8'))
    b=json.loads((out/'n01-current-W024-shared-complete-body-plan.json').read_text(encoding='utf-8'))
    parts=copy.deepcopy(a['middle_recipe']['parts']);delta=vertical_transfer_mm
    assert min(8-delta,8+delta)>=0.
    # Keep both external endpoints and the full lower loop. Redistribute the
    # two existing8mm vertical runs; all four quarter-circle radii unchanged.
    parts[6]['end'][2]+=delta;parts[6]['length']-=delta
    for i in [7,8,9]:
        parts[i]['start'][2]+=delta;parts[i]['end'][2]+=delta
    parts[10]['start'][2]+=delta;parts[10]['length']+=delta
    shifted,_=transport(parts[:13],[0,0,2.2]);other=shifted+copy.deepcopy(b['middle_recipe']['parts'][13:])
    shapes={};recipes={}
    for w,new,parent in [('W022',parts,a),('W024',other,b)]:
        old=parent['middle_recipe'];length=base.tr.length(new)
        assert abs(length-base.tr.length(parent['middle_recipe']['parts']))<1e-7
        assert (A.Vector(*new[0]['start'])-A.Vector(*old['parts'][0]['start'])).Length<1e-6
        assert (A.Vector(*new[-1]['end'])-A.Vector(*old['parts'][-1]['end'])).Length<1e-6
        minimum=min(p.get('radius',math.inf) for p in new);assert minimum>=12.4-1e-6
        body=base.solid(new,old['radius_mm']);body.check(True);shapes[w]=body
        recipes[w]=dict(parts=new,radius_mm=old['radius_mm'],minimum_R_mm=minimum,
            middle_length_mm=length,previous_middle_recipe_length_mm=base.tr.length(old['parts']),
            inherited_saved_BRep_length_mm=parent['middle_length_mm'],
            inherited_BRep_vs_recipe_difference_mm=parent['middle_length_mm']-base.tr.length(old['parts']),
            complete_body_length_mm=parent['complete_body_length_mm'],
            source_prefix_owners=parent['source_prefix_owners'],current_boundaries=parent['current_boundaries'],
            vertical_length_reallocation_mm={'before':[8,8],'after':[8-delta,8+delta]},
            stock_length_added_mm=0.,source_and_receiver_moved=False,
            unchanged_lower_vertical_tie_station_mm=[[-40.,-22.,43.5],[-42.2,-22.,43.5]],
            common_simple_anchor_owner='GAL25 SpliceRoot arm; N03 shared tie eyelet/detail pending',
            whole900_NOT_received=True,not_physical_PASS=True)
    return shapes,recipes


def load_existing_leg_motion(start_pose=0,stop_pose=36,rest=None):
    """Pinned original leg shapes and chosen existing poses; reuse rest shapes, no scene replay."""
    import itertools,json,numpy as np
    from check_main_p0_placement import ROOT,SavedShapes,sha
    from plan_feline_layout import OUT,MODEL,STAGES,transforms
    motionfile=OUT/'motion-layout.json';axesfile=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    data=json.loads(motionfile.read_text(encoding='utf-8'));axes=json.loads(axesfile.read_text(encoding='utf-8'))['axes']
    reader=SavedShapes();rest={} if rest is None else rest;actors=[]
    for code,groups in data['membership'].items():
        aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
        pose_rows=data['poses'][start_pose:stop_pose]
        tfs=[transforms(aa,p['legs'][code]['angles_delta_degrees']) for p in pose_rows]
        for stage,names in groups.items():
            for name in names:
                source=rest[name] if name in rest else reader.shape(MODEL,name);rest[name]=source;bb=source.BoundBox
                corners=np.array(list(itertools.product((bb.XMin,bb.XMax),(bb.YMin,bb.YMax),(bb.ZMin,bb.ZMax))))
                for i in range(len(pose_rows)):
                    r,t=tfs[i][STAGES.index(stage)];v=corners@r.T+t
                    actors.append(dict(name=name,code=code,stage=stage,pose=start_pose+i,r=r,t=t,bounds=[v.min(0),v.max(0)]))
    return rest,actors,{**reader.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in [MODEL,motionfile,axesfile]}}


def check_existing_motion_step(shapes,rest,actors,state=None,budget_seconds=100.,covers=None):
    """One bounded pass over changed owners; preserve exact-pose cache in RAM."""
    import time
    from feline_solid_distance import bbox_lower_bound,distance
    from receive_feline_global_case_candidates import placement
    if state is None:state=dict(done=[],rows=[],errors=[],cache={},validated={},seconds=0.)
    tick=time.monotonic()
    for n,s in shapes.items():
        if n in state['done']:continue
        s.check(True)
        pieces=(covers or {}).get(n,[s]);piece_bounds=[p.BoundBox for p in pieces]
        for a in actors:
            key=(n,a['name'],a['pose'])
            if any(row['key']==key for row in state['rows']):continue
            bb=A.BoundBox(*a['bounds'][0],*a['bounds'][1])
            bounds=[bbox_lower_bound(b,bb) for b in piece_bounds]
            near=[p for p,d in zip(pieces,bounds) if d<1.25]
            if not near:continue
            if time.monotonic()-tick>=budget_seconds:
                state['seconds']+=time.monotonic()-tick
                return state
            signature=(n,a['name'],tuple(a['r'].reshape(-1)),tuple(a['t']))
            if a['name'] not in state['validated']:
                # A complex unqualified supplier/source shape is HOLD. Do not
                # block the entire bounded pass on another expensive BOP scan.
                if len(rest[a['name']].Faces)>250:
                    state['validated'][a['name']]=False
                    state['errors'].append(dict(source=a['name'],error='Complex unqualified source; no repeated unbounded BOP validation or clearance claim'))
                else:
                    try:rest[a['name']].check(True);state['validated'][a['name']]=True
                    except Exception as exc:
                        message=str(exc).splitlines();state['validated'][a['name']]=False
                        state['errors'].append(dict(source=a['name'],error=message[0] if message else type(exc).__name__))
            if not state['validated'][a['name']]:
                state.setdefault('unqualified_near_pairs',[]).append(dict(owner=n,source=a['name'],pose=a['pose'],status='HOLD_invalid_or_unqualified_source_not_clearance'))
                continue
            if signature not in state['cache']:
                inv=placement(a['r'],a['t']).inverse();gaps=[]
                for piece in near:
                    q=piece.copy();q.Placement=inv*q.Placement
                    gaps.append(distance(q,rest[a['name']].copy()))
                gaps.extend(d for d in bounds if d>=1.25)
                state['cache'][signature]=min(gaps)
            gap=state['cache'][signature];state['rows'].append(dict(key=key,owner=n,source=a['name'],pose=a['pose'],gap_mm=gap,minimum_mm=1.25,ok=gap>=1.25-1e-6))
        state['done'].append(n)
        print('GAL25_MOTION_PART',n,'done',len(state['done']),'of',len(shapes),'queries',len(state['rows']),'failures',sum(not r['ok'] for r in state['rows']),'errors',len(state['errors']),flush=True)
        if time.monotonic()-tick>=budget_seconds:break
    state['seconds']+=time.monotonic()-tick
    return state


def transverse_whole_ground_plan(groups,endpoints):
    """U: three front wires cross before the fore fuse; rear avoids the Pi strap.

    Same common-GND purchased rail, no external pinout change. Only the AUX
    custom R15 exit changes clock about its retained full9 axial cap. Factory
    leads and module poses stay. These are nominal proposal bodies, not prints.
    """
    import copy,math,Part
    import prototype_layout_review_20261024 as base
    g={n:s.copy() for n,s in groups.items()};e=copy.deepcopy(endpoints)
    order=('XA04','XA05','XB13','XB23','XA06')
    originals={r['local']['physical_slot']:copy.deepcopy(r['local']) for w,r in endpoints['rows'].items() if w in order}
    for slot,w in enumerate(order,1):
        local=e['rows'][w]['local'];target=originals[slot]
        assert abs(local['radius_mm']-target['radius_mm'])<1e-8,(w,slot)
        g[local['actor']]=groups[target['actor']].copy()
        local['point_mm']=target['point_mm'];local['physical_slot']=slot
    levels={w:101.75 if w=='XA06' else 107.1 for w in order}
    _,sr=top_exit_ground_branches(e,levels)
    shapes={};recipes={}
    # Rotate the existing complete custom exit, not its purchased pad or grip.
    old=e['rows']['XA04']['remote'];a=A.Vector(*old['point_mm'])-A.Vector(*old['outward'])*15-A.Vector(0,0,15)
    q=a+A.Vector(-15/math.sqrt(2),-15/math.sqrt(2),15)
    escape=[base.tr.arc(list(a),(0,0,1),list(q))]
    aux=base.solid(escape,1.25);aux.check(True)
    for w in order:
        row=e['rows'][w];parts=list(sr[w]['parts'])
        # Discard only the uncommitted front straight continuation to X-20.
        if w not in ('XA04','XA06'):parts=parts[:2]
        p=parts[-1]['end'];dest=list(row['remote']['point_mm'])
        if w in ('XA05','XB13','XB23'):
            R={'XA05':15.,'XB13':18.,'XB23':21.}[w]
            c=[p[0]-R,p[1]-R,p[2]];parts.append(base.tr.arc(p,(-1,0,0),c))
            if w=='XA05':
                d=[c[0],40.,c[2]];f=[c[0],25.,c[2]-15]
                h=[c[0],25.,dest[2]+15];j=[c[0]-15,25.,dest[2]]
                parts += [base.tr.line(c,d),base.tr.arc(d,(0,-1,0),f),base.tr.line(f,h),
                    base.tr.arc(h,(0,0,-1),j),*base.tr.biarc(j,(-1,0,0),dest,tuple(-v for v in row['remote']['outward']))]
            elif w=='XB23':
                d=[c[0],51.4,c[2]];f=[c[0]-15,36.4,c[2]];h=[-90.46,36.4,c[2]]
                dest=[-117.46,36.4,103.]
                parts += [base.tr.line(c,d),base.tr.arc(d,(0,-1,0),f),base.tr.line(f,h),*base.tr.biarc(h,(-1,0,0),dest,(-1,0,0))]
            else:
                d=[c[0],-30.,c[2]];f=[c[0]-15,-45.,c[2]];h=[-126.,-45.,c[2]]
                j=[-141.,-45.,c[2]-15];k=[-141.,-45.,50.]
                m=[-139.4,-30.55,dest[2]+12.6];n=[-139.4,-43.15,dest[2]]
                parts += [base.tr.line(c,d),base.tr.arc(d,(0,-1,0),f),base.tr.line(f,h),base.tr.arc(h,(-1,0,0),j),
                    base.tr.line(j,k),*base.tr.biarc(k,(0,0,-1),m,(0,0,-1)),base.tr.arc(m,(0,0,-1),n),base.tr.arc(n,(0,-1,0),dest)]
        elif w=='XA04':
            # West of Pi/AUX, then turn below the full AUX case/carrier.
            c=[p[0]+15,p[1]-15,p[2]];d=[c[0],40.,c[2]];f=[c[0],-10.,q.z]
            last=[q.x-15/math.sqrt(2),q.y-15*(1-1/math.sqrt(2)),q.z]
            h=[c[0],last[1]+15,q.z];j=[c[0]+15,last[1],q.z]
            parts += [base.tr.arc(p,(1,0,0),c),base.tr.line(c,d),*base.tr.biarc(d,(0,-1,0),f,(0,-1,0)),
                base.tr.line(f,h),base.tr.arc(h,(0,-1,0),j),base.tr.line(j,last),base.tr.arc(last,(1,0,0),list(q))]
            dest=list(q)
        else:
            d=[100.,p[1],p[2]]
            parts += [base.tr.line(p,d),*base.tr.biarc(d,(1,0,0),dest,(0,0,-1))]
        minimum=min(p.get('radius',math.inf) for p in parts)
        assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        body=base.solid(parts,row['radius_mm']);body.check(True);shapes[w]=body
        recipes[w]=dict(parts=parts,source=row['local'],actual_receiver_mm=dest,radius_mm=row['radius_mm'],
            minimum_R_mm=minimum,body_length_mm=base.tr.length(parts),source9_extra_mm=9.25,
            factory_length_added_mm=0,full_wire_stock_motion_assembly_NOT_received=True)
    return g,e,shapes,recipes,aux,dict(common_ground_order=list(order),purchased_rail_unchanged=True,
        front_crossing_X_mm=[25.5,31.5],both_FHY97_factory_leads_and_grips_unchanged=True,
        AUX_same_axial_cap_mm=list(a),AUX_exit_clock_change_deg=90,AUX_new_R15_parts=escape,
        whole_layout_static_motion_and_outline_NOT_received=True)


def horizontal_ground_module(groups,endpoints,bed):
    """V: lever-up common rail, full inboard9 grips and one rooted open comb.

    Module first. Planar body layer90 is above83 bank cases and below97.6
    power boot. Those source bounds motivate the layer, not a clearance PASS.
    Two equal-OD tie zones avoid a flat band bridging smaller jackets.
    """
    import copy,Part
    def box(a,b):return Part.makeBox(*(b[i]-a[i] for i in range(3)),A.Vector(*a))
    old=groups['Station:G_AUX:case'];origin=old.BoundBox.Center
    rot=A.Rotation(A.Vector(1,0,0),90)*A.Rotation(A.Vector(0,0,1),-90)
    tf=A.Placement(A.Vector(61.5,84,90)-rot.multVec(origin),rot)
    case=old.copy();case.Placement=tf*case.Placement
    actors={'Station:G_AUX:case':case};e=copy.deepcopy(endpoints)
    order=('XB13','XB23','XA05','XA04','XA06');xs=(52.,56.75,61.5,66.25,71.)
    for slot,(w,x) in enumerate(zip(order,xs),1):
        row=e['rows'][w];n=row['local']['actor'];r=row['radius_mm'];start=[x,74.5,90.]
        actors[n]=Part.makeCylinder(r,9.25,A.Vector(*start),A.Vector(0,-1,0))
        row['local'].update(point_mm=[x,65.25,90.],outward=[0,-1,0],physical_slot=slot,
            original_same_rail_logical_id_retained=True,full9_grip_start_mm=[x,74.25,90.])
    pad=box([49.05,65.25,90.15],[73.95,74.25,93.4])
    for w,x in zip(order,xs):
        pad=pad.cut(Part.makeCylinder(e['rows'][w]['radius_mm']+.15,13,A.Vector(x,76,90),A.Vector(0,-1,0)))
    # One carrier: broad floor, two posts inside actual bank-bed bounds and
    # one front comb riser. Nothing passes over purchased WAGO lever tops.
    floor=box([44,73,81.5+1.25],[82.5,95.25,85])
    wall=box([47,73,82.75],[50,74.25,93.4])
    lip1=box([44,77,85],[46,93,87]);lip2=box([77,77,85],[79,93,87])
    lip3=box([48,94,85],[75,95.25,87])
    posts=[box([x,75.25,53.5],[x+4,79.25,82.95]) for x in (56.5,61.5)]
    carrier=floor.multiFuse([wall,pad,lip1,lip2,lip3,*posts]).removeSplitter();carrier.check(True)
    assert len(carrier.Solids)==1
    joints=[]
    for p in posts:
        common=bed.copy().common(p);common.check(True);assert common.Volume>1e-5
        joints.append(common.Volume)
    whole=bed.fuse(carrier);whole.check(True);assert len(whole.Solids)==1
    actors['Carrier:G_AUX:horizontal']=carrier
    for tag,lo,hi,r,y,side in [('front2',49.25,58.75,1.05,67.5,-1),('rear3',59.5,73.95,1.25,74.25-5/2,1)]:
        outer=box([lo-1.2,y-1.25,90-r-1.2],[hi+1.2,y+1.25,94.6])
        inner=box([lo,y-1.35,90-r],[hi,y+1.35,93.4])
        band=outer.cut(inner);band.check(True)
        head=box([lo-5.5,y-2.5,87.35],[lo-1.2,y+2.5,92.65]) if side<0 else box([hi+1.2,y-2.5,87.35],[hi+5.5,y+2.5,92.65])
        actors['Station:G_AUX:band_'+tag]=band;actors['Station:G_AUX:head_'+tag]=head
        # Real side straps pass through the common roof BETWEEN jackets.
        # Axially staggered zones fit in the2.45mm inter-jacket gap. Cut only
        # their .15-clearance CSG envelope, never a whole band bounding box.
        slot_outer=box([lo-1.35,y-1.4,90-r-1.35],[hi+1.35,y+1.4,94.75])
        slot_inner=box([lo+.15,y-1.5,90-r+.15],[hi-.15,y+1.5,93.25])
        carrier=carrier.cut(slot_outer.cut(slot_inner))
    carrier.check(True);assert len(carrier.Solids)==1
    actors['Carrier:G_AUX:horizontal']=carrier
    for n,a in actors.items():a.check(True)
    c=case.BoundBox;b=carrier.BoundBox
    return actors,e,dict(proposal_id='GAL25-V',module_first=True,centre_mm=[61.5,84,90],
        same_purchased_common_ground_rail=True,external_pinout_unchanged=True,
        physical_port_order=list(order),nominal_jacket_radius_mm={w:e['rows'][w]['radius_mm'] for w in order},
        source_outward=[0,-1,0],full9_after_case_transition_mm=.25,
        changed_common_comb_not_purchased_bores=True,tie_zone_core_counts=[2,3],
        tie_zone_selected_T18I100_qty=2,independent_equal_OD_zone_relief=True,
        case_bounds_mm=[[c.XMin,c.YMin,c.ZMin],[c.XMax,c.YMax,c.ZMax]],
        lever_direction_project='+Z from retained flat case orientation; confirm delivered WAGO',
        case_floor_tape_gap_mm=.5,lateral_case_stop_gap_mm=.5,
        body_layer_Z_mm=90,bank_case_top_reference_mm=83,power_boot_bottom_reference_mm=97.6,
        positive_post_bed_common_mm3=joints,bed_material_removed_mm3=0,
        ATO_whole_fuses_point_positive_Y_not_up=True,ATO_tool_top_reference_mm=81.5,
        floor_bottom_mm=82.75,floor_thickness_mm=2.25,posts_between_both_real_fuses_and_tool_X_budgets=True,
        bed_carrier_union_one_solid=True,carrier_bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],
        load_path='WAGO -> .5tape/floor/stops -> two PETGposts -> unchanged BankBed -> retained frame roots',
        assembly='Install full bed/carrier, seat case, operate lever-up ends before upper cover and before securing the adjacent Pi power loom. Route free custom ends then close two equal-OD grip bands. Reverse partial assembly for rare rework; no rapid service demand.',
        bought_parts_or_P0_cut=False,all_factory_lengths_unchanged=True,
        source_OD_pull_fit_lever_access_strength_and_whole_routes_OPEN=True,
        native_N03_NOT_started=True,N01_complete=False,physical_pass=False)


def east_exit_ground_module(groups,endpoints,bed):
    """W: same lever-up rail between the two retained USB runs; east exits.

    Whole bought-case pose, full9 lands, shared comb and load path move as one
    plan. Keep USB/Pi/FHY and both horizontal ATO extraction spaces unchanged.
    """
    import copy,Part
    def box(a,b):return Part.makeBox(*(b[i]-a[i] for i in range(3)),A.Vector(*a))
    v,e,previous=horizontal_ground_module(groups,endpoints,bed)
    rot=A.Rotation(A.Vector(0,0,1),90)
    tf=A.Placement(A.Vector(46,71.75,91.5)-rot.multVec(A.Vector(61.5,84,90)),rot)
    actors={n:s.copy() for n,s in v.items() if n!='Carrier:G_AUX:horizontal'}
    for a in actors.values():a.Placement=tf*a.Placement
    for w in ('XA04','XA05','XA06','XB13','XB23'):
        local=e['rows'][w]['local'];local['point_mm']=list(tf.multVec(A.Vector(*local['point_mm'])))
        local['full9_grip_start_mm']=list(tf.multVec(A.Vector(*local['full9_grip_start_mm'])))
        local['outward']=[1,0,0]
    # The upper ratchet head goes ABOVE the retained USB main run, outside
    # the case/electrical lands. Its material joins its own strap budget.
    actors['Station:G_AUX:head_rear3']=box([55.75,84.2,95],[60.75,88.5,100.3])
    # The smaller-zone ratchet closes ABOVE its comb, away from the retained
    # BUS-USB side head. Full stock head dimensions5x4.3x5.3 are preserved.
    actors['Station:G_AUX:head_front2']=box([60,62.475,95],[65,66.775,100.3])
    comb=v['Carrier:G_AUX:horizontal'].common(box([0,0,90],[150,150,100]));comb.check(True)
    comb.Placement=tf*comb.Placement
    floor=box([34.5,54.75,84.25],[58,88,86.5]);riser=box([56,54.75,84.25],[58,59.5,95])
    posts=[box([x,75.25,53.5],[x+4,79.25,84.45]) for x in (33.5,38.5)]
    stops=[box([35,58,86.5],[36,85,88.5]),box([38,54.75,86.5],[54,56.25,88.5]),
           box([38,87.25,86.5],[54,88,88.5])]
    carrier=floor.multiFuse([riser,comb,*posts,*stops]).removeSplitter();carrier.check(True)
    assert len(carrier.Solids)==1
    whole=bed.fuse(carrier);whole.check(True);assert len(whole.Solids)==1
    actors['Carrier:G_AUX:east']=carrier
    joints=[]
    for p in posts:
        c=bed.copy().common(p);c.check(True);assert c.Volume>1e-6;joints.append(c.Volume)
    # Head and strap are the SAME physical T18I item, not two colliding parts.
    for zone in ('front2','rear3'):
        tie=actors.pop('Station:G_AUX:band_'+zone).fuse(actors.pop('Station:G_AUX:head_'+zone))
        tie.check(True);assert len(tie.Solids)==1
        actors['Station:G_AUX:tie_'+zone]=tie
    for a in actors.values():a.check(True)
    cb=actors['Station:G_AUX:case'].BoundBox
    return actors,e,dict(proposal_id='GAL25-W',same_purchased_common_ground_rail=True,
        centre_mm=[46,71.75,91.5],case_bounds_mm=[[cb.XMin,cb.YMin,cb.ZMin],[cb.XMax,cb.YMax,cb.ZMax]],
        port_order_low_to_high_Y=['XB13','XB23','XA05','XA04','XA06'],source_outward=[1,0,0],
        lever_project_direction='+Z; delivered lever fit gate',full9_mm=9,case_transition_mm=.25,
        selected_T18I100_wire_ties=2,equal_OD_zone_core_counts=[2,3],upper_head_above_retained_USB=True,
        case_tape_gap_mm=.5,case_stop_gap_mm=.5,floor_thickness_mm=2.25,
        positive_post_bed_common_mm3=joints,unchanged_bed_material_removed_mm3=0,
        carrier_bed_union_one_solid=True,ATO_fuses_slide_positive_Y=True,
        bank_case_top_reference_mm=83,ATO_tool_top_reference_mm=81.5,floor_bottom_mm=84.25,
        USB_main_axis_YZ_mm=[91.85810963471377,89],USB_return_axis_YZ_mm=[46,89],
        assembly='Same bench-free ends and lever-up sequence as V; operate WAGO before securing adjacent power loom. Two OD-zone ties on the shared9 comb; no tie over case levers. Rare work reverses partial assembly.',
        native_N03_NOT_started=True,whole_body_routes_motion_and_stock_OPEN=True,
        selected=False,N01_complete=False,physical_pass=False)


def low_gallery_ground_module(groups,endpoints,bed,west=False,avoid_west_max_X_mm=None,west_bay=False):
    """Keep W46 bought-case/root; one three-zone comb frees the low front gallery.

    Equal-OD zones bear on every jacket. Port permutation is inside the SAME
    common ground rail. No manufacturer's pinout or delivered OD is inferred.
    """
    import copy,Part
    def box(a,b):return Part.makeBox(*(b[i]-a[i] for i in range(3)),A.Vector(*a))
    old,e,plan=east_exit_ground_module(groups,endpoints,bed)
    actors={'Station:G_AUX:case':old['Station:G_AUX:case']}
    order=('XA04','XA06','XA05','XB23','XB13') if west_bay else ('XA04','XA06','XB13','XB23','XA05')
    pad=box([55.75,59.3,91.65],[64.75,84.2,95])
    for slot,w in enumerate(order,1):
        row=e['rows'][w];r=row['radius_mm'];y=62.25+(slot-1)*4.75
        actors[row['local']['actor']]=Part.makeCylinder(r,9.25,A.Vector(55.5,y,91.5),A.Vector(1,0,0))
        row['local'].update(point_mm=[64.75,y,91.5],full9_grip_start_mm=[55.75,y,91.5],
            outward=[1,0,0],physical_slot=slot)
        pad=pad.cut(Part.makeCylinder(r+.15,11,A.Vector(54.75,y,91.5),A.Vector(1,0,0)))
    # Three2.5mm straps fit on the9mm land with .5mm axial separation.
    # The north single-core head stays north of the neighbouring side strap.
    zones=[('rear2',59.3,69.2,1.25,57,62.475),
           ('front2',69.8,78.5,1.05,60,71.975),('front1',79.25,84.2,1.25,63,80)]
    if west_bay:
        assert west
        zones=[('rear3',59.3,73.75,1.25,58,62.475),('front2',74.5,84.2,1.05,62.5,77.3)]
    tie_slots=[]
    for tag,lo,hi,r,x,hy in zones:
        outer=box([x-1.25,lo-1.2,91.5-r-1.2],[x+1.25,hi+1.2,96.2])
        inner=box([x-1.35,lo,91.5-r],[x+1.35,hi,95])
        band=outer.cut(inner)
        hx=max(55.75,x-2.5)  # entire stock head outside the case's X55.5 face
        head=box([hx,hy,95],[hx+5,hy+4.3,100.3])
        tie=band.fuse(head);tie.check(True);assert len(tie.Solids)==1
        actors['Station:G_AUX:tie_'+tag]=tie
        slot_outer=box([x-1.4,lo-1.35,91.5-r-1.35],[x+1.4,hi+1.35,96.35])
        slot_inner=box([x-1.5,lo+.15,91.5-r+.15],[x+1.5,hi-.15,94.85])
        tie_slots.append(slot_outer.cut(slot_inner))
    # A broad common spine survives the rear strap window. Reusing the
    # W46 two-mm upright here severed the comb when its real strap was cut.
    floor=box([34.5,54.75,84.25],[58,88,86.5]);riser=box([56,54.75,84.25],[64.75,59.5,95])
    posts=[box([x,75.25,53.5],[x+4,79.25,84.45]) for x in (33.5,38.5)]
    stops=[box([35,58,86.5],[36,85,88.5]),box([38,54.75,86.5],[54,56.25,88.5]),box([38,87.25,86.5],[54,88,88.5])]
    if west:
        # Rotate the actual module/source/comb family, retaining the bank's
        # floor, posts and stops. A west comb avoids three front U detours.
        rot=A.Rotation(A.Vector(0,0,1),180);origin=A.Vector(46,71.75,91.5)
        tf=A.Placement(origin-rot.multVec(origin),rot)
        for s in [*actors.values(),pad,riser,*tie_slots]:s.Placement=tf*s.Placement
        for w in order:
            local=e['rows'][w]['local']
            for key in ('point_mm','full9_grip_start_mm'):local[key]=list(tf.multVec(A.Vector(*local[key])))
            local['outward']=[-1,0,0]
        shift=34. if west_bay else (0. if avoid_west_max_X_mm is None else max(0.,avoid_west_max_X_mm+1.25-27.25))
        if shift:
            # Joint inequality from the complete RR_P case, not an offset scan:
            # west comb Xmin >= RR_P Xmax + rigid1.25. Keep the qualified posts.
            delta=A.Vector(shift,0,0)
            for s in [*actors.values(),pad,riser,*tie_slots,*stops]:s.translate(delta)
            for w in order:
                for key in ('point_mm','full9_grip_start_mm'):e['rows'][w]['local'][key][0]+=shift
            floor=box([34.5,54.75,84.25],[58+shift,88,86.5])
        # The reflected upright stops at the floor's north edge. Extending
        # it .75 further was unnecessary and infringed the retained USB gap.
        riser=box([27.25+shift,84.,84.25],[36.+shift,88.,95.])
        if west_bay:
            # Ymin of the case is USB ratchet's Ymax56 + rigid1.25.
            # Keep the two X stops and tape; no north/south lip in the USB lane.
            delta=A.Vector(0,.5,0)
            for s in [*actors.values(),pad,riser,*tie_slots]:s.translate(delta)
            for w in order:
                for key in ('point_mm','full9_grip_start_mm'):e['rows'][w]['local'][key][1]+=.5
            riser=box([61.25,84.5,84.25],[70.,88.,95.])
            # The complete BUS USB ratchet is at Y<=56, not just its band.
            # Leave the south edge open; retain the case on its two X sides
            # and north side, with tape on the broad floor and a third post.
            # Support the case locally; the old long floor lay across the
            # west cable egress. Both roots are between actual ATO6/7 tools.
            floor=box([68.5,57.25,84.25],[91.5,88,86.5])
            stops=[box([69.,58,86.5],[70.,85,88.5]),box([90.,58,86.5],[91.5,85,88.5])]
            posts=[box([x,75.25,53.5],[x+4,79.25,84.45]) for x in (80.25,85.25)]
    carrier=floor.multiFuse([riser,pad,*posts,*stops]).removeSplitter()
    # Side straps also pass through the common riser, not just its pad.
    for slot in tie_slots:carrier=carrier.cut(slot)
    carrier.check(True);assert len(carrier.Solids)==1
    whole=bed.fuse(carrier);whole.check(True);assert len(whole.Solids)==1
    actual_joints=[bed.common(p).Volume for p in posts];assert min(actual_joints)>1e-6
    actors['Carrier:G_AUX:low_gallery']=carrier
    for s in actors.values():s.check(True)
    plan.update(proposal_id='GAL25-X-low-gallery',port_order_low_to_high_Y=list(order),
        selected_T18I100_wire_ties=3,equal_OD_zone_core_counts=[2,2,1],
        unchanged_W46_case_floor_posts_not_newly_qualified=True,
        actual_tie_threading_pull_and_delivered_fit_OPEN=True,
        assembly='Bench install grounded bed/carrier, seat lever-up case, terminate same-net ends, lay full9 jackets into one comb and secure three equal-OD zones before closing accessible bundle gallery; reverse partial assembly for rework.')
    if west:plan.update(proposal_id='GAL25-Z-west-exit',source_outward=[-1,0,0],
        port_order_low_to_high_Y=list(reversed(order)),west_comb_on_same_rooted_floor=True,
        centre_mm=[46+shift,71.75,91.5],case_bounds_mm=[[actors['Station:G_AUX:case'].BoundBox.XMin,56.75,87.],[actors['Station:G_AUX:case'].BoundBox.XMax,86.75,96.]],
        west_RR_P_max_X_constraint_mm=avoid_west_max_X_mm,derived_whole_module_shift_X_mm=shift,
        original_two_post_positions_unchanged=True)
    if west_bay:plan.update(proposal_id='GAL25-AD-local-case-floor-two-roots',
        centre_mm=[80,72.25,91.5],case_bounds_mm=[[70.5,57.25,87.],[89.5,87.25,96.]],
        selected_T18I100_wire_ties=2,equal_OD_zone_core_counts=[2,3],
        nominal_T18I100_wrap_plus_head_thread_allowance_mm=[75.,65.1],
        tie_stock_mm=100,head_thread_allowance_is_project_assumption_mm=27.,
        positive_post_bed_common_mm3=actual_joints,
        original_two_post_positions_unchanged=False,
        current_post_XY_bounds_mm=[[[x,75.25],[x+4,79.25]] for x in (80.25,85.25)],
        post_constraint='Between ATO6/7; first Xmin=tool6.Xmax79+rigid1.25; second Xmax89.25<tool7.Xmin91-1.25',
        cable_egress_west_of_local_case_floor_min_X_mm=68.5,
        south_floor_Y_mm=57.25,complete_USB_head_max_Y_mm=56.,
        case_south_overhang_mm=0,case_retained_two_X_sides_and_tape=True,
        north_and_south_edges_open_for_retained_USB=True)
    if west_bay:
        plan.pop('unchanged_W46_case_floor_posts_not_newly_qualified',None)
        plan['assembly']='Install local floor/two posts on the retained bank bed, tape and seat the lever-up rail between the two X stops. Terminate same-net ends, close the two equal-OD jacket ties on the shared west comb, then lay the accessible bundle corridors. North/south case edges stay open for retained USB. Reverse partial assembly for rare work; no rapid service assumption.'
    return actors,e,plan


def west_exit_ground_branches(endpoints,old_front_recipes,west_bay=False):
    """Three direct front branches; only the two rear leads use the lower gallery."""
    import math
    import prototype_layout_review_20261024 as base
    bodies={};recipes={}
    for w in ('XB13','XB23','XA05','XA04','XA06'):
        row=endpoints['rows'][w];p=row['local']['point_mm'];dest=list(row['remote']['point_mm'])
        if w in ('XB13','XB23','XA05'):
            d=[-35.,92.5,{'XB13':57.,'XB23':63.,'XA05':70.}[w]]
            # Joint staged fan: first Z with source Ypitch preserved, then Y
            # with six/seven-mm Zpitch preserved. Independent spatial biarcs
            # collided despite separated endpoints; do not reuse that family.
            level=[0.,92.5,{'XB13':78.45,'XB23':81.65,'XA05':84.6}[w]] if west_bay else [-3.,p[1],d[2]]
            parts=[*base.tr.biarc(p,(-1,0,0),level,(-1,0,0)),
                   *base.tr.biarc(level,(-1,0,0),d,(-1,0,0))]
            old=old_front_recipes[w]['parts'];index=next(i for i,t in enumerate(old) if all(abs(t['start'][j]-d[j])<1e-7 for j in range(3)))
            parts+=old[index:];dest=list(parts[-1]['end'])
        else:
            if west_bay and w=='XA06':
                # Separate the rear return before the front convergence.
                # One tilted half-turn starts at the full9 cap; it avoids
                # the vertical curtain that cut Head in the two old folds.
                finish=[p[0],92.5,50.7];delta=A.Vector(*finish)-A.Vector(*p);R=delta.Length/2
                turn=dict(kind='arc',start=p,end=finish,tangent=[-1,0,0],bend=list(delta.normalize()),
                    radius=R,angle=math.pi,length=math.pi*R,end_tangent=[1,0,0])
                c=[85.,92.5,50.7];d=[113.,86.5,95.595];f=[128.,71.5,95.595]
                # Rise immediately after the tilted turn. The unnecessary
                # low straight crossed AUX's later XY branch at X78.5.
                parts=[turn,*base.tr.biarc(finish,(1,0,0),d,(1,0,0)),
                    base.tr.arc(d,(1,0,0),f),base.tr.arc(f,(0,-1,0),dest)]
                minimum=min(t.get('radius',math.inf) for t in parts);assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
                body=base.solid(parts,row['radius_mm']);body.check(True);bodies[w]=body
                recipes[w]=dict(parts=parts,radius_mm=row['radius_mm'],source=row['local'],actual_receiver_mm=dest,
                    minimum_R_mm=minimum,body_length_mm=base.tr.length(parts),factory_length_added_mm=0,
                    whole_current_clearance_motion_stock_OPEN=True)
                continue
            y,R={'XA04':(95.5,16.2 if west_bay else 17.),'XA06':(92.5,15.3)}[w]
            # Branch order: finish the rear folds east of X0, BEFORE the
            # front group descends. A fold at X-10 cut all three front lanes.
            turn_X=20. if west_bay else -10.
            centre_Z=65.2 if west_bay and w=='XA04' else 66.
            a=[turn_X,y,centre_Z+R];b=[turn_X,y,centre_Z-R]
            turn=dict(kind='arc',start=a,end=b,tangent=[-1,0,0],bend=[0,0,-1],radius=R,
                angle=math.pi,length=math.pi*R,end_tangent=[1,0,0])
            parts=[*base.tr.biarc(p,(-1,0,0),a,(-1,0,0)),turn]
            if w=='XA04':
                c=[126.43,y,b[2]];d=[146.43,y-20,b[2]];f=[146.43,-5.,97.21];dest=[146.43,-50.27,97.21]
                if west_bay:
                    # Restore the ACTUAL retained45-degree AUX cap, not the
                    # provisional +Y clock that intersected P_REAR's case.
                    dest=list(row['remote']['point_mm']);assert abs(dest[0]-135.82339828220188)<1e-6
                    c=[68.,y,b[2]];d=[88.,y-20,b[2]];low=[88.,20.,b[2]]
                    rise=[88.,5.,b[2]+15];up=[88.,5.,82.21];high=[88.,-10.,97.21]
                    j=[88.,-35.27,97.21];k=[103.,-50.27,97.21]
                    s=[dest[0]-15/math.sqrt(2),dest[1]+15*(1-1/math.sqrt(2)),dest[2]]
                    parts += [base.tr.line(b,c),base.tr.arc(c,(1,0,0),d),base.tr.line(d,low),
                        base.tr.arc(low,(0,-1,0),rise),base.tr.line(rise,up),base.tr.arc(up,(0,0,1),high),
                        base.tr.line(high,j),base.tr.arc(j,(0,-1,0),k),base.tr.line(k,s),base.tr.arc(s,(1,0,0),dest)]
                else:parts += [base.tr.line(b,c),base.tr.arc(c,(1,0,0),d),*base.tr.biarc(d,(0,-1,0),f,(0,-1,0)),base.tr.line(f,dest)]
            else:
                c=[80.,92.5,b[2]];d=[113.,86.5,95.595];f=[128.,71.5,95.595]
                parts += [base.tr.line(b,c),*base.tr.biarc(c,(1,0,0),d,(1,0,0)),base.tr.arc(d,(1,0,0),f),base.tr.arc(f,(0,-1,0),dest)]
        minimum=min(t.get('radius',math.inf) for t in parts);assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        body=base.solid(parts,row['radius_mm']);body.check(True);bodies[w]=body
        recipes[w]=dict(parts=parts,radius_mm=row['radius_mm'],source=row['local'],actual_receiver_mm=dest,
            minimum_R_mm=minimum,body_length_mm=base.tr.length(parts),factory_length_added_mm=0,
            receiver_continuation_reused=w in ('XB13','XB23','XA05'),whole_current_clearance_motion_stock_OPEN=True)
    return bodies,recipes,dict(proposal_id='GAL25-Z-west-direct-front-lower-rear',
        direct_front_count=3,lower_rear_count=2,rear_gallery_YZ_mm=[[95.5,49.],[92.5,50.7]],
        requires_shared_U1_printed_cross_revision=True,N01_complete=False,physical_pass=False)


def outer_aux_gallery(row,rear_X):
    """One exterior rear/south passage avoids the occupied electronics stack.

    Same vertical full9 AUX land, larger R17 south-west escape, custom HELU
    only. Rear_X comes from the actual retained AUX screw's outermost X plus
    jacket1.25 and rigid1.25, not a position search. Leg/outline proof is OPEN.
    """
    import math
    import prototype_layout_review_20261024 as base
    p=row['local']['point_mm'];a=[20.,95.5,81.4];b=[20.,95.5,49.]
    parts=[*base.tr.biarc(p,(-1,0,0),a,(-1,0,0)),
        dict(kind='arc',start=a,end=b,tangent=[-1,0,0],bend=[0,0,-1],radius=16.2,
             angle=math.pi,length=16.2*math.pi,end_tangent=[1,0,0])]
    c=[rear_X-20,95.5,49.];d=[rear_X,75.5,49.];s=[rear_X,-75.,49.]
    # R17 keeps the selected axial land, gives a south-west free cap and
    # headroom for the body's R15 final approach without exceeding200wide.
    axial=[146.43,-65.27,82.21];q=[138.43,-80.27,99.21]
    direction=[8/17,15/17,0];up=[q[0]-15*direction[0],q[1]-15*direction[1],q[2]-15]
    parts += [base.tr.line(b,c),base.tr.arc(c,(1,0,0),d),base.tr.line(d,s),
        *base.tr.biarc(s,(0,-1,0),up,(0,0,1)),base.tr.arc(up,(0,0,1),q)]
    escape_parts=[base.tr.arc(axial,(0,0,1),q)]
    minimum=min(t.get('radius',math.inf) for t in parts)
    assert minimum>=row['minimum_R_mm']-1e-6,minimum
    body=base.solid(parts,row['radius_mm']);escape=base.solid(escape_parts,row['radius_mm'])
    body.check(True);escape.check(True)
    return body,dict(parts=parts,radius_mm=row['radius_mm'],source=row['local'],actual_receiver_mm=q,
        minimum_R_mm=minimum,body_length_mm=base.tr.length(parts),factory_length_added_mm=0,
        custom_HELU_not_factory_extension=True),escape,dict(source_axial_cap_mm=axial,
        source_R_mm=17,source_free_cap_mm=q,source_outward=[-v for v in direction],
        source_parts=escape_parts,rear_plane_X_mm=rear_X,
        unchanged_axial9_grip_bare_and_electrical_lands=True,
        whole_outline_leg_motion_stock_service_and_receiver_fit_OPEN=True,N01_complete=False,physical_pass=False)


def low_outboard_branches(endpoints,old_front_recipes):
    """Critical source U turns only; reuse the exact I receiver continuations.

    The named risk is source/factory USB and whole front/rear mutual occupancy.
    Concentric U turns at outboard Y92.5 replace the obstructed high return.
    No claims about the old I service tool checks or whole motion are inherited.
    """
    import math
    import prototype_layout_review_20261024 as base
    bodies={};recipes={}
    # The inside-USB gallery is BELOW the real ATOs/tools on the return,
    # outside the bed's Ymax80. The earlier outboard Y92.5 vertical U cut
    # the retained USB main tube; this changes the whole fold's topology.
    lanes={'XB13':(92.5,23.5,57.),'XB23':(88.4,19.4,63.),'XA05':(84.3,15.3,70.)}
    for w in ('XB13','XB23','XA05','XA04','XA06'):
        row=endpoints['rows'][w];p=row['local']['point_mm'];dest=list(row['remote']['point_mm'])
        if w in lanes:
            # One jointly ordered spatial fan, not two serial planar fans.
            # With Xrun32.25 its smallest bend is17mm; the outer U ends at
            # X120.5, leaving4.5 to the retained USB spline's Xmin125.
            # The old serial fan required X110 and crossed that USB surface.
            z,R,tier=lanes[w];b=[97.,87.5,z];c=[97.,87.5,z-2*R]
            d=[-35.,92.5,tier]
            turn=dict(kind='arc',start=b,end=c,tangent=[1,0,0],bend=[0,0,-1],radius=R,
                angle=math.pi,length=math.pi*R,end_tangent=[-1,0,0])
            parts=[*base.tr.biarc(p,(1,0,0),b,(1,0,0)),turn,
                *base.tr.biarc(c,(-1,0,0),d,(-1,0,0))]
            old=old_front_recipes[w]['parts'];index=next(i for i,t in enumerate(old) if all(abs(t['start'][j]-d[j])<1e-7 for j in range(3)))
            parts+=old[index:];dest=list(parts[-1]['end'])
        elif w=='XA04':
            a=[95.,p[1],86.5];b=[131.43,p[1],86.5];c=[146.43,p[1]-15,86.5];d=[146.43,-5.,97.21];dest=[146.43,-50.27,97.21]
            parts=[*base.tr.biarc(p,(1,0,0),a,(1,0,0)),base.tr.line(a,b),base.tr.arc(b,(1,0,0),c),*base.tr.biarc(c,(0,-1,0),d,(0,-1,0)),base.tr.line(d,dest)]
        else:
            a=[113.,86.5,95.595];b=[128.,71.5,95.595]
            parts=[*base.tr.biarc(p,(1,0,0),a,(1,0,0)),base.tr.arc(a,(1,0,0),b),base.tr.arc(b,(0,-1,0),dest)]
        minimum=min(t.get('radius',math.inf) for t in parts);assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        body=base.solid(parts,row['radius_mm']);body.check(True);bodies[w]=body
        recipes[w]=dict(parts=parts,radius_mm=row['radius_mm'],source=row['local'],actual_receiver_mm=dest,
            minimum_R_mm=minimum,body_length_mm=base.tr.length(parts),factory_length_added_mm=0,
            receiver_continuation_reused=w in lanes,whole_current_clearance_motion_stock_OPEN=True)
    return bodies,recipes,dict(proposal_id='GAL25-Y-inner-USB-under-ATO-gallery',fold_Y_mm=87.5,
        front_concentric_U_R_mm=[23.5,19.4,15.3],common_centre_Z_mm=69.,
        source_joint_3D_fan=True,USB_spline_min_X_mm=125,outer_U_max_X_mm=120.5,
        not_whole_scene_received=True,N01_complete=False,physical_pass=False)


def saved_round_USB_cells(shape):
    """Specific9-face saved USB tube cover; never repairs the invalid full BRep.

    Full cylindrical/toroidal faces yield valid isolated round-tube cells.
    The one COMPLETE periodic circumferential spline face covers a round
    swept section; its face bounds contain the discs' convex hulls. Keep it
    as a conservative box, with no Boolean or source-validity claim.
    """
    import math,Part
    from receive_feline_W024_shared_body import solid
    from feline_tangent_routes import arc
    cells={};facts=[]
    for i,f in enumerate(shape.Faces):
        kind=type(f.Surface).__name__;u0,u1,v0,v1=f.ParameterRange
        if kind=='Plane':continue
        if kind=='Cylinder':
            assert abs((u1-u0)-2*math.pi)<1e-6
            radius=f.Surface.Radius;assert abs(radius-2.5)<1e-6
            a=(f.valueAt(u0,v0)+f.valueAt(u0+math.pi,v0))*.5
            b=(f.valueAt(u0,v1)+f.valueAt(u0+math.pi,v1))*.5
            cell=Part.makeCylinder(radius,(b-a).Length,a,b-a)
        elif kind=='Toroid':
            assert abs((v1-v0)-2*math.pi)<1e-6 and abs(f.Surface.MinorRadius-2.5)<1e-6
            centre=lambda u:(f.valueAt(u,v0)+f.valueAt(u,v0+math.pi))*.5
            a=centre(u0);b=centre((u0+u1)/2);c=centre(u1)
            edge=Part.Arc(a,b,c).toShape();t=edge.tangentAt(edge.FirstParameter)
            cell=solid([arc(list(a),list(t),list(c))],2.5)
        elif kind=='BSplineSurface':
            assert f.Surface.isUPeriodic() and abs((u1-u0)-2*math.pi)<1e-6
            bb=f.BoundBox;cell=Part.makeBox(bb.XLength,bb.YLength,bb.ZLength,A.Vector(bb.XMin,bb.YMin,bb.ZMin))
        else:raise ValueError('Unclassified USB face '+kind)
        cell.check(True);cells['USB500:facecell:'+str(i)]=cell
        facts.append(dict(face=i,surface=kind,cover='full-periodic-tube conservative box' if kind=='BSplineSurface' else 'valid isolated analytic tube cell',
            full_source_BRep_NOT_revalidated_or_repaired=True))
    assert len(cells)==7
    return cells,facts


def east_ground_whole_branches(endpoints,only_wires=None):
    """One joint W five-body hypothesis; unchanged full9 source cylinders.

    The three front U bends share XY axes with separated Z lanes; source and
    return fans use enough perpendicular separation before flattening. Rear
    AUX passes below them; Tail uses the north side and retained two R15 ends.
    """
    import math,Part
    import prototype_layout_review_20261024 as base
    shapes={};recipes={};target_Y={'XB13':45.6,'XB23':42.95,'XA05':40.25}
    for w in ('XB13','XB23','XA05','XA04','XA06'):
        if only_wires is not None and w not in only_wires:continue
        row=endpoints['rows'][w];p=row['local']['point_mm'];dest=list(row['remote']['point_mm'])
        if w in target_Y:
            lane={'XB13':89.8,'XB23':93.,'XA05':96.2}[w]
            flat_Y={'XB13':52.5,'XB23':47.75,'XA05':43.}[w]
            level=[81.,p[1],lane];a=[106.,82.5,lane];b=[106.,52.5,lane]
            spread=[78.,flat_Y,lane];c=[51.,flat_Y,93.2];d=[-5. if w=='XA05' else -20.,target_Y[w],93.2]
            U=dict(kind='arc',start=a,end=b,tangent=[1,0,0],bend=[0,-1,0],radius=15.,
                angle=math.pi,length=15*math.pi,end_tangent=[-1,0,0])
            parts=[*base.tr.biarc(p,(1,0,0),level,(1,0,0)),*base.tr.biarc(level,(1,0,0),a,(1,0,0)),U,
                *base.tr.biarc(b,(-1,0,0),spread,(-1,0,0)),*base.tr.biarc(spread,(-1,0,0),c,(-1,0,0)),
                *base.tr.biarc(c,(-1,0,0),d,(-1,0,0))]
            if w=='XA05':
                f=[-20.,25.25,93.2];g=[-20.,-15.,93.2];h=[-20.,-30.,78.2]
                j=[-20.,-30.,60.26];k=[-20.,-15.,45.26];m=[-37.375,30.,45.26]
                parts += [base.tr.arc(d,(-1,0,0),f),base.tr.line(f,g),base.tr.arc(g,(0,-1,0),h),
                    base.tr.line(h,j),base.tr.arc(j,(0,0,-1),k),*base.tr.biarc(k,(0,1,0),m,(0,1,0)),base.tr.line(m,dest)]
            elif w=='XB23':
                f=[-67.46,42.95,93.2];dest=[-117.46,36.4,103.]
                parts += [base.tr.line(d,f),*base.tr.biarc(f,(-1,0,0),dest,(-1,0,0))]
            else:
                climb=[-60.,45.6,93.2];above=[-115.,45.6,106.2]
                parts += [base.tr.line(d,climb),*base.tr.biarc(climb,(-1,0,0),above,(-1,0,0))]
                d=above
                f=[-126.,45.6,106.2];g=[-141.,30.6,106.2];h=[-141.,-17.95,106.2]
                j=[-141.,-30.55,93.6];k=[-141.,-30.55,30.]
                m=[-139.4,-30.55,dest[2]+12.6];n=[-139.4,-43.15,dest[2]]
                parts += [base.tr.line(d,f),base.tr.arc(f,(-1,0,0),g),base.tr.line(g,h),base.tr.arc(h,(0,-1,0),j),
                    base.tr.line(j,k),*base.tr.biarc(k,(0,0,-1),m,(0,0,-1)),base.tr.arc(m,(0,0,-1),n),base.tr.arc(n,(0,-1,0),dest)]
        elif w=='XA04':
            a=[95.,p[1],86.5];b=[131.43,p[1],86.5];c=[146.43,p[1]-15,86.5]
            d=[146.43,-5.,97.21];dest=[146.43,-50.27,97.21]
            parts=[*base.tr.biarc(p,(1,0,0),a,(1,0,0)),base.tr.line(a,b),base.tr.arc(b,(1,0,0),c),
                *base.tr.biarc(c,(0,-1,0),d,(0,-1,0)),base.tr.line(d,dest)]
        else:
            a=[113.,86.5,95.595];b=[128.,71.5,95.595]
            parts=[*base.tr.biarc(p,(1,0,0),a,(1,0,0)),base.tr.arc(a,(1,0,0),b),base.tr.arc(b,(0,-1,0),dest)]
        minimum=min(t.get('radius',math.inf) for t in parts);assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        body=base.solid(parts,row['radius_mm']);body.check(True);shapes[w]=body
        recipes[w]=dict(parts=parts,source=row['local'],actual_receiver_mm=dest,radius_mm=row['radius_mm'],
            body_length_mm=base.tr.length(parts),minimum_R_mm=minimum,factory_length_added_mm=0,
            full_factory_OD_fit_motion_stock_and_ATO_parking_NOT_received=True)
    # AUX quarter is rotated as a WHOLE about its retained full9 axial cap.
    a=[146.43,-65.27,82.21];q=[146.43,-50.27,97.21]
    aux_parts=[base.tr.arc(a,(0,0,1),q)];aux=base.solid(aux_parts,1.25);aux.check(True)
    return shapes,recipes,aux,dict(AUX_same_axial_cap_mm=a,AUX_R15_parts=aux_parts,
        required_changed_printed_neighbor='PowerGripRoot:XA01; inspect load path before any return-channel change',
        front_Pi_boot_flatten_finish_X_mm=51,front_U_max_X_mm=121,front_U_Z_lanes_mm=[89.8,93,96.2],
        rigid_case_and_factory_leads_unchanged=True,N01_complete=False,physical_pass=False)


def round_recipe_covers(recipes,prefix='FullBody:'):
    """Exact per-segment round sweeps for a long wire's sparse broad phase.

    The union covers the same circular-profile spine as its full pipe. These
    cells only avoid treating the wire's whole bounding box as occupied space.
    No valid or invalid retained neighbor is omitted when its bound is near.
    """
    import prototype_layout_review_20261024 as base
    result={}
    for wire,row in recipes.items():
        parts=[]
        for p in row['parts']:
            s=base.solid([p],row['radius_mm']);s.check(True);parts.append(s)
        result[prefix+wire]=parts
    return result
