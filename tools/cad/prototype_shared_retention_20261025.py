"""N01 construction witness for one shared13-end retention bank; not N03 release."""
import FreeCAD as A
import Part


def relieve_inner_corridor(scene):
    """Relieve two printed beams together, preserving actual end bearings."""
    start=A.Vector(18.525,-35.25,50)
    axis=Part.makeLine(start,A.Vector(88.3,-35.25,50))
    cutter=Part.makeCylinder(2.8,69.775,start,A.Vector(1,0,0))
    names=['CurrentFoundation:BankPier:3','CurrentFoundation:BankLedge:3']
    changed={};proof={}
    for n in names:
        old=scene[n];old.check(True);new=old.cut(cutter);new.check(True)
        assert len(new.Solids)==1 and new.cut(old).Volume<1e-7
        b=old.BoundBox;kept={}
        # The ledge is relieved from underneath; its complete foot slice is
        # deliberately not invariant. Preserve its roof and actual end joints.
        regions=[('foot',b.ZMin),('roof',b.ZMax-1)] if n.endswith('BankPier:3') else [('roof',b.ZMax-1)]
        for role,z in regions:
            clip=Part.makeBox(b.XLength+2,b.YLength+2,1,A.Vector(b.XMin-1,b.YMin-1,z))
            before=old.common(clip);after=new.common(clip)
            assert before.Volume>1e-6 and before.cut(after).Volume<1e-7
            kept[role]=dict(unchanged=True,volume_mm3=before.Volume)
        gap=axis.distToShape(new)[0]-1.55
        assert gap>=1.25-1e-6
        changed[n]=new;proof[n]=dict(removed_mm3=old.Volume-new.Volume,subset=True,kept_1mm=kept,profile_gap_lower_bound_mm=gap)
    joints=[]
    pairs=[(names[0],'CurrentFoundation:ClampSeat:3'),(names[0],'CurrentFoundation:ClampNeck:3'),(names[0],names[1]),(names[1],'CurrentFoundation:BankBedCurrent:-1')]
    for a,b in pairs:
        old=scene[a].common(scene[b]);new=changed.get(a,scene[a]).common(changed.get(b,scene[b]))
        assert old.Volume>1e-6 and old.cut(new).Volume<1e-7,(a,b)
        joints.append(dict(a=a,b=b,positive_joint_mm3=new.Volume,original_joint_material_unchanged=True))
    return changed,dict(corridor_axis_mm=[[18.525,-35.25,50],[88.3,-35.25,50]],wire_radius_mm=1.55,foreign_air_mm=1.25,cutter_radius_mm=2.8,printed_only=proof,joints=joints,full_branch_received=False,strength_physical_gate=True)


def build(scene):
    actors={};plans={};roots={};ties={};slots=[];retired=set()
    for group,comb_dy,band_dy,fy in [('D_FR',-12,-8.75,(-56.25,-53.2)),('FR_G',0,-2,(-52.3,-48.3)),('P_AUX',-12,-12,(-56.25,-53.2))]:
        p='Station:'+group+':'
        assert abs(scene[p+'case'].BoundBox.YMax+56.5)<1e-6,'Current mouth datum changed'
        comb=scene[p+'split_common_comb'].copy();comb.translate(A.Vector(0,comb_dy,0));comb.check(True)
        assert abs(comb.BoundBox.YLength-9)<1e-6
        original=scene[p+'band_budget'];cells=list(original.Solids)
        assert len(cells)==4,'This witness only reuses the four recorded ribbon cells'
        for cell in cells:cell.check(True)
        band=cells[0].multiFuse(cells[1:]);band.check(True);assert len(band.Solids)==1
        head=scene[p+'head_budget'].copy();head.check(True)
        band.translate(A.Vector(0,band_dy,0));head.translate(A.Vector(0,band_dy,0))
        tie=band.fuse(head);tie.check(True);assert len(tie.Solids)==1
        bb=original.BoundBox
        slots.append(Part.makeBox(bb.XLength+.4,bb.YLength+.4,1.6,A.Vector(bb.XMin-.2,bb.YMin+band_dy-.2,bb.ZMin-.2)))
        wires=[n for n in scene if n.startswith(p+'wire:')]
        assert len(wires)==(5 if group=='D_FR' else 4)
        top=min(scene[n].BoundBox.ZMin for n in wires)-.2;b=comb.BoundBox
        foot=Part.makeBox(b.XLength,fy[1]-fy[0],top-40.32,A.Vector(b.XMin,fy[0],40.32))
        root=comb.fuse(foot);root.check(True);assert len(root.Solids)==1
        actors[p+'shared_near_root']=root;actors[p+'shared_near_tie']=tie;roots[group]=root;ties[group]=tie
        retired.update(p+k for k in ['split_common_comb','band_budget','head_budget'])
        plans[group]=dict(comb_translation_mm=[0,comb_dy,0],band_and_same_head_translation_mm=[0,band_dy,0],full9_Y_mm=[-56.25,-47.25],wire_owners_unchanged=wires,source_valid_band_cells=4,foot_Y_mm=list(fy),stock_qty_added=0)
    # Ratchet recess stays outside all jacket channels; no bought component cut.
    head=scene['Station:FR_G:head_budget'].copy();head.translate(A.Vector(0,-2,0));b=head.BoundBox
    pocket=Part.makeBox(b.XLength+.4,b.YLength+.4,b.ZLength+.4,A.Vector(b.XMin-.2,b.YMin-.2,b.ZMin-.2))
    roots['D_FR']=roots['D_FR'].cut(pocket);actors['Station:D_FR:shared_near_root']=roots['D_FR']
    frames={};subset={}
    for n,s in scene.items():
        if not n.startswith('CurrentFoundation:'):continue
        relevant=[c for c in slots if c.BoundBox.intersect(s.BoundBox)]
        if not relevant:continue
        q=s.copy()
        for c in relevant:q=q.cut(c)
        if s.Volume-q.Volume<1e-7:continue
        q.check(True);assert len(q.Solids)==len(s.Solids)
        assert q.cut(s).Volume<1e-7
        frames[n]=q;subset[n]=dict(removed_mm3=s.Volume-q.Volume,new_material_outside_original_mm3=0,source_solid_count=len(s.Solids),new_solid_count=len(q.Solids))
    base=Part.makeBox(41.5,3.05,2,A.Vector(26,-56.25,37.5)).fuse(Part.makeBox(21.35,5.65,2,A.Vector(33.825,-56.25,37.5)))
    base=base.multiFuse([Part.makeBox(2.5,3.05,2.6,A.Vector(26,-56.25,39.3)),Part.makeBox(2.125,3.05,2.6,A.Vector(65.375,-56.25,39.3)),Part.makeBox(21.35,1.7,1.22,A.Vector(33.825,-52.3,39.3))]);base.check(True);assert len(base.Solids)==1
    parent=frames.get('CurrentFoundation:FoundationFlange:-1',scene['CurrentFoundation:FoundationFlange:-1'])
    joint=base.common(parent).Volume;assert joint>1e-6
    whole=parent.fuse(base);contacts={}
    for group,root in roots.items():
        root.check(True);assert len(root.Solids)==1
        contacts[group]=root.common(base).Volume;assert contacts[group]>1e-6
        whole=whole.fuse(root)
        for n in plans[group]['wire_owners_unchanged']:assert root.common(scene[n]).Volume<1e-7
    whole.check(True);assert len(whole.Solids)==1
    actors.update(frames);actors['SharedRetention:lower_common_flange_base']=base
    mutual=[]
    for i,a in enumerate(ties):
        for b in list(ties)[i+1:]:
            gap=float(ties[a].distToShape(ties[b])[0]);assert gap>=.2-1e-6 and ties[a].common(ties[b]).Volume<1e-7
            mutual.append(dict(a=a,b=b,gap_mm=gap))
    for n,s in actors.items():
        s.check(True)
        for g,tie in ties.items():
            if n!='Station:'+g+':shared_near_tie':assert s.common(tie).Volume<1e-7,(n,g,'strap pinched')
    return actors,dict(proposal_id='GAL25-BL-shared-thirteen-end-retention',groups=plans,retired_source_actors=sorted(retired),frame_subset=subset,base_parent='CurrentFoundation:FoundationFlange:-1',base_parent_positive_common_mm3=joint,root_base_positive_common_mm3=contacts,whole_print_loadpath_one_solid=True,three_ties_mutual=mutual,all13_jacket_geometries_unchanged=True,selected=False,N01_complete=False,native_N03_started=False,physical_pass=False,open=['Whole fourteen branches and actual assembly/service sequence','Delivered case/OD/head fit, tie pull strength and PETG strength','Production native features/print exports/stock remain later stages'])
