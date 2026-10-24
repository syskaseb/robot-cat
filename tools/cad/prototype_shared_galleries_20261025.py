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
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(name,s) in enumerate(shapes.items()):
            s.check(True);raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
            t=Part.Shape();t.importBrepFromString(raw.decode());t.check(True)
            members[name]=dict(member=entry,sha256=hashlib.sha256(raw).hexdigest(),strict_reopen=True,
                solids=len(t.Solids),volume_mm3=t.Volume,bounds_mm=[[t.BoundBox.XMin,t.BoundBox.YMin,t.BoundBox.ZMin],[t.BoundBox.XMax,t.BoundBox.YMax,t.BoundBox.ZMax]])
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
