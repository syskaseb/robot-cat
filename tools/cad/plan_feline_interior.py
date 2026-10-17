"""One coarse whole-interior proposal using actual current component meshes.

No geometry or circuit is selected here. Positive mesh-outside witnesses and
potential pairs drive the next native check. Cases retain role/port identities;
two identical contextual aliases are not two additional purchased connectors.
"""
import json
import pickle
import time
from pathlib import Path
import numpy as np
from check_main_p0_placement import ROOT, SavedShapes, sha
from plan_feline_layout import BASE, OUT, STAGES
from build_feline_layout_envelope import STATIONS, PROFILE_EXPONENT, PROFILE_FAMILY,section_coefficients


def inside(points,center,margin=2):
    x=points[:,0]
    valid=(x>=STATIONS[0][0]+margin)&(x<=STATIONS[-1][0]-margin)
    widths=np.interp(x,[s[0] for s in STATIONS],[s[1] for s in STATIONS])-2*margin
    heights=np.interp(x,[s[0] for s in STATIONS],[s[2] for s in STATIONS])-2*margin
    sections=[np.column_stack(section_coefficients(w,h))*[w/2,h/2] for _,w,h in STATIONS]
    # Ruled loft interpolates actual corresponding vertices, not a local
    # exponent guessed independently of the native station geometry.
    count=len(sections[0])
    yy=[np.interp(x,[s[0] for s in STATIONS],[p[i,0] for p in sections])*(widths/(widths+2*margin)) for i in range(count)]
    zz=[np.interp(x,[s[0] for s in STATIONS],[p[i,1] for p in sections])*(heights/(heights+2*margin)) for i in range(count)]
    for i in range(count):
        j=(i+1)%count
        py,pz=yy[i],zz[i]
        dy,dz=yy[j]-py,zz[j]-pz
        valid &= dy*(points[:,2]-center-pz)-dz*(points[:,1]-py)>=-1e-5
    return valid


def main():
    tick=time.monotonic()
    motion=json.loads((OUT/'motion-layout.json').read_text())
    layout=json.loads((OUT/'layout-checkpoint.json').read_text())
    assert all(sha(ROOT/n)==h for n,h in motion['source_sha256'].items())
    records={p['object']:p for p in motion['inventory']}
    meshes={}
    with (BASE/'phase1-prototype-final/preview/triangulation-cache.pkl').open('rb') as f:
        pickle.load(f)
        while True:
            try:n,m=pickle.load(f)
            except EOFError:break
            meshes[n]=m
    # Reuse the original native mechanical carrier, before the large W3 arms.
    # Its supplier servo matches the current datum after the known CP2 shift.
    yaw_file=ROOT/'hardware/cad/studies/head-p7/yaw-r1/YawCarrier.FCStd'
    yaw_reader=SavedShapes();core=yaw_reader.shape(yaw_file,'Carrier')
    import FreeCAD as A
    core.translate(A.Vector(-42,0,25))
    vertices,faces=core.tessellate(.8)
    yaw_name='Ref_Material_head_0_0_YawCarrier_0_0'
    old_carrier_bounds=records[yaw_name]['bounds_mm']
    meshes[yaw_name]=(np.array([list(v) for v in vertices])[np.array(faces)],meshes[yaw_name][1],'surface')
    replacement=dict(source=yaw_file.relative_to(ROOT).as_posix(),object='Carrier',
        world_shift_before_head_drop_mm=[-42,0,25],original_current_bounds_mm=old_carrier_bounds,
        reason='Retain original editable servo carrier core; supersede long W3 wire-support arms in the new wiring architecture.')
    # Clock only unkeyed ring lugs around their ACTUAL saved cylindrical axes.
    # The mounting bolts atX-96/-58 are different features, not these axes.
    overrides={}
    for suffix,x,degrees in [('IN',-89,90),('OUT',-65,-90)]:
        n='Ref_Material_S0_ring_'+suffix+'_0_0';r=A.Rotation(A.Vector(0,0,1),degrees)
        p=A.Vector(x,16,78.85);t=A.Placement(p-r.multVec(p),r);m=t.toMatrix()
        rot=np.array([[getattr(m,f'A{i+1}{j+1}') for j in range(3)] for i in range(3)])
        shift=np.array(list(t.Base));v,c,kind=meshes[n];meshes[n]=(v@rot.T+shift,c,kind)
        overrides[n]=dict(rotation_rows=rot.tolist(),translation_mm=shift.tolist(),
            actual_cylinder_axis_point_mm=list(p),axis=[0,0,1],clock_degrees=degrees,
            basis='Saved ring cylinderR5.02 onselectedsource; unchanged bore and lug. Not newmanufacturerfastener data.')
    for k,y,z,degrees in [(2,41.5,105,90),(3,41.5,93,90),(5,29.5,105,-90),(6,29.5,93,-90)]:
        n=f'Ref_Material_current_S1_ring_{k}_0_0';p=A.Vector(122.558,y,z);r=A.Rotation(A.Vector(1,0,0),degrees)
        t=A.Placement(p-r.multVec(p),r);m=t.toMatrix()
        rot=np.array([[getattr(m,f'A{i+1}{j+1}') for j in range(3)] for i in range(3)])
        shift=np.array(list(t.Base));v,c,kind=meshes[n];meshes[n]=(v@rot.T+shift,c,kind)
        overrides[n]=dict(rotation_rows=rot.tolist(),translation_mm=shift.tolist(),
            actual_cylinder_axis_point_mm=list(p),axis=[1,0,0],clock_degrees=degrees,
            basis='Saved S1ring cylinderR2.667; clock lug upward about actual bore, not casing or signalpin.')
    # Preserve all catalogue housings/ATO/TE instances. The R47 right support
    # needs a new native30mm pitch instead of32mm in this enclosure extension.
    # This is NOT the old selected right support or its wiring qualification.
    for n in records:
        if not n.startswith('Ref_Material_F_R'):continue
        i=int(n.split('F_R',1)[1][0]);shift=np.array([-2*(i-1),0,0])
        v,c,kind=meshes[n];meshes[n]=(v+shift,c,kind)
        overrides[n]=dict(rotation_rows=np.eye(3).tolist(),translation_mm=shift.tolist(),
            basis='New common right6holder pitch30; catalogue subparts unchanged. Supersedes R47rightmount pose/stock in new scope.')
    tail_file=ROOT/'hardware/cad/modules/tail/TailSupport.FCStd'
    tail=SavedShapes();s=tail.shape(tail_file,'ServoSupport34');s.translate(A.Vector(0,0,15))
    v,f=s.tessellate(.8);tn='Ref_Material_tail_MG92BMount29_0_0'
    meshes[tn]=(np.array([list(p) for p in v])[np.array(f)],meshes[tn][1],'surface')
    tail_replacement=dict(source=tail_file.relative_to(ROOT).as_posix(),object='ServoSupport34',
        world_shift_before_head_drop_mm=[0,0,15],reason='Original native structuralcore proven subset; obsolete W4arms retired. Newstationarywiregrip required.')
    groups=[];assigned=set()
    def add(name,names,delta=(0,0,0),rotation=None,new_center=None,region='torso',datum=None):
        names=sorted(names);assert names,name
        assert not assigned.intersection(names),(name,assigned.intersection(names))
        assigned.update(names)
        rotation=np.eye(3) if rotation is None else rotation
        points=np.concatenate([meshes[n][0].reshape(-1,3) for n in names])
        datum_points=points if datum is None else meshes[datum][0].reshape(-1,3)
        old_center=(datum_points.min(0)+datum_points.max(0))/2
        translation=np.asarray(delta) if new_center is None else np.asarray(new_center)-rotation@old_center
        moved=points@rotation.T+translation
        contained=inside(moved,layout['native']['center_z_mm']) if region=='torso' else np.ones(len(moved),dtype=bool)
        witnesses=moved[~contained]
        outside_objects=[]
        for obj in names:
            moved_object=meshes[obj][0].reshape(-1,3)@rotation.T+translation
            count=int((~inside(moved_object,layout['native']['center_z_mm'])).sum()) if region=='torso' else 0
            if count:outside_objects.append(dict(object=obj,points=count))
        groups.append(dict(role=name,region=region,objects=names,rotation_rows=rotation.tolist(),translation_mm=translation.tolist(),
            current_bounds_mm=[points.min(0).tolist(),points.max(0).tolist()],
            candidate_bounds_mm=[moved.min(0).tolist(),moved.max(0).tolist()],
            sampled_points=len(points),sampled_outside_inner_reservation=int((~contained).sum()),
            outside_objects=outside_objects,
            outside_witnesses_mm=witnesses[np.linspace(0,len(witnesses)-1,min(8,len(witnesses)),dtype=int)].tolist() if len(witnesses) else [],
            placement_datum_object=datum,selected=False,rigid_internal_geometry_retained=True))
    surfaces={n:r for n,r in records.items() if r['kind']=='surface'}
    labels={n:r['label'] for n,r in surfaces.items()}
    select=lambda *prefixes:[n for n,label in labels.items() if label.startswith(prefixes)]
    add('HeadMechanism',select('head/0/0/','headref/0/'),delta=(-40,0,-90),region='head_neck')
    add('TailMechanicalCore',[tn],region='tail_root')
    add('Pi4',select('Pi4'),delta=(0,0,50.38))
    add('BUS',select('BUSsupplier'),delta=(0,0,42))
    add('MAIN',select('MAIN/','MAIN_','Power/MAIN'),delta=(0,-23,50))
    add('PWM9685',select('PWM9685'),delta=(-63,22,21.28))
    add('PWM1608_U1',select('PWM1608','U1_'),delta=(-80,2,-107.75))
    add('AUX4092',select('AUX4092'),delta=(-115,6,-91))
    # Full TE ends span71.43mm in Z, not just the28.5mm casing.
    rx=np.array([[1,0,0],[0,0,-1],[0,1,0]])
    rz=np.array([[0,-1,0],[1,0,0],[0,0,1]])
    ang=np.radians(60)
    rx60=np.array([[1,0,0],[0,np.cos(ang),-np.sin(ang)],[0,np.sin(ang),np.cos(ang)]])
    add('BankLeft6Oprawek12Koncow',select('F_L'),rotation=rx60.T,new_center=(4,30,70))
    add('BankRight6Oprawek12Koncow',select('F_R'),rotation=rx60,new_center=(16,-30,70))
    add('S0',select('S0_'),rotation=rx,new_center=(-115,-6,78),datum='Ref_Material_S0_body_CP2_0_0')
    add('S1',select('current/S1_'),rotation=rz,new_center=(-105,45,65),datum='Ref_Material_current_S1_body_CP2_0_0')
    for code,x,y,z in (('FL',-40,15,-34),('FR',-40,-15,-34),('RL',65,15,-34),('RR',65,-15,-34)):
        add('MTA_'+code,select('MTA/'+code+'/'),new_center=(x,y,z))
    n=select('F_PI_new/');assert len(n)==1
    ry=np.array([[0,0,1],[0,1,0],[-1,0,0]])
    add('F_PI',n,rotation=rx,new_center=(-105,0,-32))
    rz45=np.array([[2**-.5,-2**-.5,0],[2**-.5,2**-.5,0],[0,0,1]])
    for role,prefix,rotation,centre in [
        ('F0','F0_CP2/',rz45,(68,0,-13.75)),
        ('F_AUX','F_AUX_candidate_case/',rz,(143,0,-15)),
        ('XT60','XT60_CP2/',None,(143,0,-35)),
        ('POST_F0','PostF0Splice_CP2/',None,(143,-35,42)),
        ('JPWM','JPWM/',None,(25,-44,50))]:
        add(role,select(prefix),rotation=rotation,new_center=centre)
    for code,x,y in [('W026',-45,35),('W041',5,47),('W037',-45,-35),('W042',5,-47),
                     ('W045',30,35),('W044',89,47),('W053',30,-35),('W052',89,-47)]:
        n=select(code+'_Joint/');assert len(n)==1
        dims=np.array(records[n[0]]['bounds_mm'][1])-records[n[0]]['bounds_mm'][0]
        order=np.argsort(dims);rotation=np.eye(3)[[order[2],order[0],order[1]]]
        if np.linalg.det(rotation)<0:rotation[1]*=-1
        add(code+'_Joint',n,rotation=rotation,new_center=(x,y,-35.75))
    aliases=select('W1Ref_P_AUX_CP2/','W1Ref_G2_CP2/')
    cases=[]
    for n,r in surfaces.items():
        if n in aliases:continue
        d=np.array(r['bounds_mm'][1])-r['bounds_mm'][0]
        dims=sorted(d)
        if np.max(np.abs(np.array(dims)-[9,19,30]))<.15 or np.max(np.abs(np.array(dims)-[11,22,37]))<.15:
            cases.append((n,d))
    assert len(cases)==20,len(cases)
    large=[item for item in cases if item[1].max()>35]
    small=[item for item in cases if item[1].max()<35]
    assert len(large)==4 and len(small)==16
    slots=[(column,row) for row in (0,3,1,2) for column in range(5)]
    large_slots=[(i,row) for row in (1,2) for i in (0,4)]
    small_slots=[slot for slot in slots if slot not in large_slots]
    coverage_path=BASE/'body-harness-checkpoint/w5-current-end-coverage.json'
    coverage=json.loads(coverage_path.read_text())
    from plan_feline_endpoints import owner
    for (n,dims),(col,row) in list(zip(large,large_slots))+list(zip(small,small_slots)):
        # Flat cases: largest -> X, middle -> Y, smallest -> Z.
        order=np.argsort(dims)
        outer=row in (0,3)
        rotation=np.eye(3)[[order[2],order[1],order[0]]] if outer else np.eye(3)[[order[2],order[0],order[1]]]
        if np.linalg.det(rotation)<0:rotation[1]*=-1
        height=sorted(dims)[0] if outer else sorted(dims)[1]
        xs=[-50,-15,20,55,90] if outer else [-46.5,-12,19,50,84.5]
        y=[-67,-40.5,40.5,67][row]
        base=35.5 if outer else -4-height
        role='WAGO:'+records[n]['label'].split('/')[0]
        old_centre=np.mean(records[n]['bounds_mm'],axis=0)
        source_points=[r['point_world_mm'] for r in coverage['fixed_physical_guide_ends']+coverage['body_fixed_boundary_ends']
            if owner(r['role'],{role:None})==role]
        source_face=None
        if source_points:
            source_face=np.sign(np.median(np.array(source_points)[:,order[1]]-old_centre[order[1]]))
            original_axis=np.eye(3)[order[1]]*source_face
            desired=np.array([0,-np.sign(y),0]) if outer else np.array([0,0,1])
            if np.dot(rotation@original_axis,desired)<0:
                rotation=(np.diag([-1,-1,1]) if outer else np.diag([1,-1,-1]))@rotation
        add('WAGO:'+records[n]['label'].split('/')[0],[n],rotation=rotation,
            new_center=(xs[col],y,base+height/2))
        groups[-1]['entry_face_verified_by_source_ends']=source_face is not None
        groups[-1]['source_entry_axis']=None if source_face is None else original_axis.tolist()
        groups[-1]['source_entry_basis']='Current nominal guide-end roles on source case, not a new manufacturer datum.'
    # Bounding overlaps are only candidates for exact checks, never collisions.
    potential=[]
    for i,a in enumerate(groups):
        alo,ahi=np.array(a['candidate_bounds_mm'])
        for b in groups[i+1:]:
            blo,bhi=np.array(b['candidate_bounds_mm'])
            if np.all(np.minimum(ahi,bhi)-np.maximum(alo,blo)>.01):
                potential.append([a['role'],b['role']])
    report=dict(status='ONE_COMMON_INTERIOR_PROPOSAL_NOT_SELECTED',groups=groups,
        connector_count=20,large_connector_count=4,small_connector_count=16,
        contextual_aliases_not_added_to_physical_count=aliases,
        potential_group_pairs_NOT_collisions=potential,
        source_sha256={},
        geometry_source_sha256=motion['source_sha256'],
        reference_substitutions={yaw_name:replacement,tn:tail_replacement},part_pose_overrides=overrides,
        role_pose_overrides={'S0.in':'Ref_Material_S0_ring_IN_0_0','S0.out':'Ref_Material_S0_ring_OUT_0_0',
            **{f'S1.{k}':f'Ref_Material_current_S1_ring_{k}_0_0' for k in (2,3,5,6)},
            **{f'F_{code}{j}.{side}':f'Ref_Material_F_R{j+offset}_CP2_{"IN" if side=="in" else "OUT"}_0_0'
                for code,offset in [('FR',0),('RR',3)] for j in (1,2,3) for side in ('in','out')}},
        superseded_wire_insulation_not_rigid_modules=select('XP01/','XP02_source/','XP03_source/','XP02_module_','XP03_module_'),
        superseded_insulation_basis='build_current_pwm_fixture.py/build_e2_tail_insulation.py: wraps of obsolete routed leads, not connector bodies or board geometry. Must rebuild on complete newW4paths, never rigidly relocate as modules.',
        head_drop_mm=90,head_yaw_axis_mm=[-192,-5.25,-65],head_pitch_axis_mm=[-234,0,71],
        head_new_root_mount_required=True,
        reservation_native_sha256=layout['native']['sha256'],
        proposed_cross_section_exponent=PROFILE_EXPONENT,proposed_profile_family=PROFILE_FAMILY,
        native_envelope_matches_this_proposal=layout['native'].get('profile_family')==PROFILE_FAMILY,
        native_update_condition='Quarterturned whole bank, all8inlinejoins andsourcecases; actual prefixes/sideATOtool andlowerWAGO12mmservice mustpass before details.',
        main_world_z46_52_retained=False,main_new_world_z_mm=96.52,
        old_MAIN_P0_adapter_not_reselected=True,
        wago_entry_policy='Inner rails upright portsUP: mouthZ-4. Outer railsflat portsINWARD: mouthZ40. Source face/slotidentities must be reconstructed, not guessed frombbox.',
        lower_negative_WAGO_service_drop_mm=0,
        complete_conductor_paths=False,connector_entry_direction_verified=False,
        operating_apertures_required=[dict(object='Ref_Material_current_S1_control_CP2_0_0',
            scope='Operating control face, actual cap/access still open and must keep totalwidth<=200.'),
            dict(object='Ref_Material_S0_key_CP2_0_0',scope='Full shaft/key sweep and shaped service flap; local cover must stay within totalwidth200. Not a waiver for exposed electrical parts.')],
        corridors=[dict(id='left',y_mm=12,z_mm=-12,x_mm=[-90,125],width_y_mm=20,height_z_mm=10),
                   dict(id='right',y_mm=-12,z_mm=-12,x_mm=[-90,125],width_y_mm=20,height_z_mm=10)],
        corridor_basis='Provisional shared reservation; derive actual occupied conductor area/packing/bend transitions from selected W5 before selecting.',
        new_mounts_required=['Two lower removable WAGO rails, independent wire restraints',
            'Compact bank core mounts retaining12holders/24ends and ATO access',
            'Both factory MTA exits with full leads/strain relief',
            'Shifted PWM/U1/AUX/S0/S1/F_PI mounts, matching hole stacks; replace legacy BUS long fasteners',
            'Replace outboard gallery arms and high UpperCarrier branches, retain actual frame anchors'],
        physical_pass=False,full_native_layout_complete=False,
        worker_seconds=round(time.monotonic()-tick,3))
    report['source_sha256']={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
        (OUT/'layout-checkpoint.json').relative_to(ROOT).as_posix():sha(OUT/'layout-checkpoint.json')}
    report['source_sha256'].update(yaw_reader.hashes)
    report['source_sha256'].update(tail.hashes)
    report['source_sha256'][coverage_path.relative_to(ROOT).as_posix()]=sha(coverage_path)
    report['source_sha256'][Path(__file__).with_name('build_feline_layout_envelope.py').relative_to(ROOT).as_posix()]=sha(Path(__file__).with_name('build_feline_layout_envelope.py'))
    (OUT/'module-layout.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],groups=len(groups),parts=sum(len(g['objects']) for g in groups),
        outside_groups=[(g['role'],g['sampled_outside_inner_reservation']) for g in groups if g['sampled_outside_inner_reservation']],
        potential_pairs=potential,seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()
