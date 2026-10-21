"""A shared two-tier open cuff: six bank cores below, three grounds above.

Do not force a single flat9 seam, another project-only constraint. The upper
three align with the whole rotated RR_G receiver and need straight returns,
not crossing spatial S bends. All actual electrical contacts stay selected.
"""
import copy
import numpy as np
import FreeCAD as A
import Part
from plan_feline_n01_shared import pipe


def clone(s):
    c=Part.Shape();c.importBrepFromString(s.exportBrepToString());return c


def rebuild_receiver(original,plan):
    assert set(original)==set(plan['original_receiver_names'])
    receiver={n:clone(s) for n,s in original.items()}
    for s in receiver.values():
        s.rotate(A.Vector(*plan['receiver_original_centre_mm']),A.Vector(0,0,1),plan['receiver_rigid_rotation_Z_deg'])
        s.translate(A.Vector(*plan['receiver_translation_mm']))
    def box(bounds):
        lo,hi=bounds;return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))
    root=[box(b) for b in plan['receiver_root_boxes_mm']]
    receiver['RRGJointRoot']=root[0].multiFuse(root[1:]).removeSplitter()
    receiver['RRGJointCase4905']=box(plan['receiver_case_4905_box_mm'])
    return receiver


def construct(flat_source,flat_resources,flat_plan,original_receiver,receiver_plan):
    source={n:clone(s) for n,s in flat_source.items()};source_rows=copy.deepcopy(flat_plan['recipes'])
    receiver=rebuild_receiver(original_receiver,receiver_plan)
    targets=receiver_plan['ground_targets'];assert set(targets)=={'W072','W073','W074'}
    # Target coordinates are the ACTUAL retained prefix cap, checked by
    # the previous whole-receiver constructor; not a guessed station index.
    target_caps={w:np.array(r['target_exit_mm']) for w,r in targets.items()}
    def box(lo,hi):return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))
    floor=box([121,-92.25,94.25],[130,-75.25,96.25])
    walls=[box([121,a,94.25],[130,b,101.75]) for a,b in ((-92.25,-90.25),(-77.25,-75.25))]
    wing=box([121,-95.3,94.25],[123,-91.5,96.25])
    column=box([119,-95.3,84.05],[123,-93.3,96.25])
    guide=source['RRFlatGuide'].multiFuse([floor,*walls,wing,column]).removeSplitter()
    assert guide.isValid() and len(guide.Solids)==1
    band=box([124.25,-93.45,93.05],[126.75,-74.05,102.95]).cut(
        box([124,-92.25,94.25],[127,-75.25,101.75]))
    head=box([123,-86.4,102.95],[128,-81.1,107.25])
    assert abs(head.Volume-5*5.3*4.3)<1e-6
    source.update(RRFlatGuide=guide,RRUpperBand=band,RRUpperHead=head)
    resources={};bodies={};recipes={};contacts=[]
    for name,row in source_rows.items():
        wire=row['wire']
        if wire not in target_caps:
            resources[row['resource']]=clone(flat_resources[row['resource']]);continue
        q=target_caps[wire];start=q.copy();start[0]=130;p=start+[-9,0,0]
        assert np.allclose(q[1:],start[1:]) and p[0]>q[0]
        first=[dict(kind='line',start=start.tolist(),end=p.tolist(),length_mm=9.)]
        parts=[dict(kind='line',start=p.tolist(),end=q.tolist(),length_mm=float(p[0]-q[0]))]
        source[name]=pipe(first,row['radius_mm']);key='RRDirectGround:'+wire;bodies[key]=pipe(parts,row['radius_mm'])
        target=targets[wire]['actual_target_prefix'];contacts.extend([(key,name),(key,target)])
        row.update(parts=first,proposed_seam_mm=start.tolist(),resource=key,resource_parts=parts,
                   resource_end_mm=q.tolist(),resource_end_axis=[-1,0,0],target_exit_mm=q.tolist(),
                   target_departure_axis=[1,0,0],upper_ground_tier=True)
        recipes[key]=dict(wire=wire,parts=parts,radius_mm=row['radius_mm'],target_prefix=target,
                          target_end_id=targets[wire]['target_end_id'],middle_length_mm=float(p[0]-q[0]),
                          source9_added_to_existing_middle_NOT_extra_factory_length=True)
    actors={**source,**resources,**bodies,**receiver};assert len(actors)==33
    return actors,dict(source_recipes=source_rows,recipes=recipes,
        receiver=receiver_plan,receiver_names=list(receiver),source_guide_parent='AuxGrip:CommonRoot',
        original_receiver_names=receiver_plan['original_receiver_names'],
        actual_face_mates=contacts+[(n,r['resource']) for n,r in source_rows.items() if r['wire'] not in target_caps],
        two_tiers_not_a_bought9pin_connector=True,upper_source_X_mm=130,upper_source_Z_mm=98,
        full9_all9_retained=True,common_open_cuff_and_two_full_stock_loops=True,
        upper_head_mm=[5,5.3,4.3],AUX_print_and_looms_UNMODIFIED=True,
        full_factory900_approaches_and_W063_reroute_OPEN=True,
        N01_complete=False,physical_pass=False,native_changed=False)


def package(actors,plan,receiver,scene,static,outer,motion):
    import hashlib,json,time,zipfile
    from pathlib import Path
    from check_main_p0_placement import ROOT,sha
    from plan_feline_layout import OUT
    from feline_atomic_save import save_json
    from plan_feline_usb_service_bight import outer_margin
    from feline_solid_distance import bbox_lower_bound
    tick=time.monotonic();assert len(actors)==33 and not static['failures'];checks=dict(static['checks'])
    root_pairs={('RRFlatGuide','AuxGrip:CommonRoot'),('RRGJointRoot','PowerMount:Trunk:PETG')}
    for parent in ('AuxGrip:CommonRoot','PowerMount:Trunk:PETG'):
        for n,s in actors.items():
            if (n,parent) in root_pairs:continue
            if bbox_lower_bound(s.BoundBox,scene[parent].BoundBox)>=1.25:continue
            gap=s.distToShape(scene[parent])[0];checks[n+'|'+parent]=dict(gap_mm=gap,minimum_mm=1.25,ok=gap>=1.25-1e-6)
    assert all(r['ok'] for r in checks.values())
    outside={n:outer_margin(s,outer) for n,s in actors.items()};assert all(r['ok'] for r in outside.values())
    zbound=min(s.BoundBox.ZMin for s in actors.values())-max(r['bounds'][1][2] for r in motion)
    assert zbound>1.25 and {r['pose'] for r in motion}==set(range(36))
    print_graph=[];print_envelopes={}
    for label,names in {'source':['RRFlatGuide','AuxGrip:CommonRoot'],
                        'receiver':['RRGJointRoot','Station:RR_G:split_common_comb','PowerMount:Trunk:PETG']}.items():
        shapes=[clone(actors[n] if n in actors else scene[n]) for n in names]
        for i in range(1,len(shapes)):
            v=clone(shapes[0]).common(clone(shapes[i])).Volume;assert v>1e-5
            print_graph.append(dict(a=names[0],b=names[i],common_mm3=v))
        whole=shapes[0].multiFuse(shapes[1:]);assert whole.isValid() and len(whole.Solids)==1
        envelope=[whole.BoundBox.XLength,whole.BoundBox.YLength,whole.BoundBox.ZLength]
        assert max(envelope)<250;print_envelopes[label]=envelope
    complete={};whole_wires={}
    for name,r in plan['recipes'].items():
        wire=r['wire'];source=next(v for v in plan['source_recipes'].values() if v['wire']==wire)
        target=actors[r['target_prefix']];q=np.array(r['parts'][-1]['end'])
        caps=[np.array(list(f.CenterOfMass)) for f in target.Faces if type(f.Surface).__name__=='Plane']
        assert len(caps)==2;mouth=next(p for p in caps if np.linalg.norm(p-q)>1e-6)
        start=np.array(source['parts'][0]['start']);length=float(np.linalg.norm(mouth-start))
        assert abs(length-42.375)<1e-6
        full=pipe([dict(kind='line',start=start.tolist(),end=mouth.tolist(),length_mm=length)],r['radius_mm'])
        segment_volume=actors[next(n for n,v in plan['source_recipes'].items() if v['wire']==wire)].Volume+actors[name].Volume+target.Volume
        assert abs(full.Volume-segment_volume)<1e-5
        whole_wires['WholeBody:'+wire]=full
        complete[wire+'/body']=dict(wire=wire,start_mm=start.tolist(),end_mm=mouth.tolist(),length_mm=length,
            owned_source9_mm=9.,middle_mm=r['middle_length_mm'],retained_receiver_prefix_mm=12.25,
            unchanged_electrical_contact_identity=True,entire_factory900_NOT_received=True)
    adhesive=actors['RRGJointCase4905'];case=actors['Station:RR_G:case']
    interface=clone(adhesive).common(clone(case));assert interface.Volume<1e-6
    # OCC solid/solid Common drops this coplanar rotated face. Intersect
    # the ACTUAL planar face polygons atZ0; do not inflate either solid.
    case_faces=[f for f in case.Faces if type(f.Surface).__name__=='Plane' and abs(f.CenterOfMass.z-93.5)<1e-7]
    glue_faces=[f for f in adhesive.Faces if type(f.Surface).__name__=='Plane' and abs(f.CenterOfMass.z-93.5)<1e-7]
    assert len(case_faces)==len(glue_faces)==1
    def projected(f):
        assert all(type(e.Curve).__name__=='Line' for e in f.OuterWire.Edges)
        points=[A.Vector(v.Point.x,v.Point.y,0) for v in f.OuterWire.OrderedVertexes]
        return Part.Face(Part.makePolygon(points+[points[0]]))
    contact_area=projected(case_faces[0]).common(projected(glue_faces[0])).Area
    assert contact_area>0 and adhesive.distToShape(case)[0]<1e-6
    flatfile=OUT/'n01-RR9-flat-common-bank-bridge.json';flat=json.loads(flatfile.read_text())
    assert sha(ROOT/flat['bundle'])==flat['bundle_sha256']
    path=OUT/'n01-RR33-two-tier-ground-space.json';archive=path.with_suffix('.breps.zip');geometry=[]
    inputs={**{'InputReceiver:'+n:s for n,s in receiver.items()},
            **{'OriginalReceiver:'+n:scene[n] for n in plan['original_receiver_names']},
            **{'InputParent:'+n:scene[n] for n in ('AuxGrip:CommonRoot','PowerMount:Trunk:PETG')}}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in {**actors,**whole_wires,**inputs}.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    rawfile=OUT/'n01-RR33-two-tier-whole-ground-static.json'
    result=dict(status='RR33_TWO_TIER_ROOTED_SOURCE_AND_THREE_WHOLE_BODY_GROUNDS_RECEIVED',
        plan=plan,checks=checks,outer=outside,complete_body_portions=complete,
        positive_print_graph=print_graph,print_envelopes_mm=print_envelopes,
        case_adhesive_contact_area_mm2=contact_area,case_contact_proof='Actual coplanar planar-face polygon intersection, not bbox or expanded solids',case_adhesion_strength_NOT_verified=True,
        sampled36_leg_vertical_separation_lower_bound_mm=zbound,
        full_moving900_and_head_tail_motion_NOT_received=True,
        input_flat_receipt=flatfile.relative_to(ROOT).as_posix(),
        raw_static_receipt=rawfile.relative_to(ROOT).as_posix(),raw_static_sha256=sha(rawfile),
        raw_static_metadata_reduced_to_receiver_only_caps_geometry_all33_equal=True,
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        source_sha256={**{n:h for n,h in static['source_sha256'].items() if n!='tools/cad/plan_feline_rr_joint_ground_return.py'},flatfile.relative_to(ROOT).as_posix():sha(flatfile),
                       Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        selected_constructor_does_not_execute_rejected_RR31_or_left_bay_builders=True,
        N01_complete=False,physical_pass=False,native_changed=False,whole123_not_received=True,
        remaining_six_RR_forks_and_W063_reroute_and_whole_factory900_OPEN=True,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(path,result);return result
