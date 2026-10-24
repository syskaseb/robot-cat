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


def complete_gaux_front(source_rec,endpoints):
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
            c=[-80.,47.5,63.];d=[-92.6,47.5,75.6];e=[-92.6,47.5,81.];q=[-117.46,36.4,103.]
            parts += [base.tr.arc(p,(0,-1,0),c),base.tr.arc(c,(-1,0,0),d),base.tr.line(d,e),*base.tr.biarc(e,(0,0,1),q,(-1,0,0))]
            reason='Rise outside ForeFHAC and approach exposed +Y side of HP row; finish-35 was not a connector. Head/moving source and proper final source cylinder retained.'
        else:
            tier=61.+1.05+1.25
            entry=[-65.,39.5,tier];c=[-65.,-16.35,tier];d=[-80.,-31.35,tier];k=[-120.,-31.35,q[2]]
            parts += [*base.tr.biarc(p,(0,-1,0),entry,(0,-1,0)),base.tr.line(entry,c),base.tr.arc(c,(0,-1,0),d),
                *base.tr.biarc(d,(-1,0,0),k,(-1,0,0)),
                *base.tr.biarc(k,(-1,0,0),q,[-v for v in row['remote']['outward']])]
            reason='Lower shared front column passes above F_PI and below S0 key, then whole S0/S1 gap. Final yaw approach reused from D trial.'
        minimum=min(p.get('radius',math.inf) for p in parts);assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        body=base.solid(parts,row['radius_mm']);body.check(True);shapes[w]=body
        recipes[w]=dict(parts=parts,reason=reason,length_mm=base.tr.length(parts),minimum_R_mm=minimum,
            radius_mm=row['radius_mm'],source=row['local'],receiver_nominal=row['remote'],final_mm=q,
            source_profile_assumptions_and_motion_fit_not_supplier_certification=True)
    return shapes,recipes


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
