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
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import BASE, OUT, STAGES
from build_feline_layout_envelope import STATIONS


def inside(points,center,margin=2):
    x=points[:,0]
    valid=(x>=STATIONS[0][0]+margin)&(x<=STATIONS[-1][0]-margin)
    widths=np.interp(x,[s[0] for s in STATIONS],[s[1] for s in STATIONS])-2*margin
    heights=np.interp(x,[s[0] for s in STATIONS],[s[2] for s in STATIONS])-2*margin
    a=(np.arange(16)+.5)*2*np.pi/16
    c=np.sign(np.cos(a))*abs(np.cos(a))**(2/2.6);c/=abs(c).max()
    s=np.sign(np.sin(a))*abs(np.sin(a))**(2/2.6);s/=abs(s).max()
    for i in range(16):
        j=(i+1)%16
        py, pz=c[i]*widths/2,s[i]*heights/2
        dy, dz=(c[j]-c[i])*widths/2,(s[j]-s[i])*heights/2
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
    groups=[];assigned=set()
    def add(name,names,delta=(0,0,0),rotation=None,new_center=None):
        names=sorted(names);assert names,name
        assert not assigned.intersection(names),(name,assigned.intersection(names))
        assigned.update(names)
        rotation=np.eye(3) if rotation is None else rotation
        points=np.concatenate([meshes[n][0].reshape(-1,3) for n in names])
        old_center=(points.min(0)+points.max(0))/2
        translation=np.asarray(delta) if new_center is None else np.asarray(new_center)-rotation@old_center
        moved=points@rotation.T+translation
        contained=inside(moved,layout['native']['center_z_mm'])
        witnesses=moved[~contained]
        outside_objects=[]
        for obj in names:
            moved_object=meshes[obj][0].reshape(-1,3)@rotation.T+translation
            count=int((~inside(moved_object,layout['native']['center_z_mm'])).sum())
            if count:outside_objects.append(dict(object=obj,points=count))
        groups.append(dict(role=name,objects=names,rotation_rows=rotation.tolist(),translation_mm=translation.tolist(),
            current_bounds_mm=[points.min(0).tolist(),points.max(0).tolist()],
            candidate_bounds_mm=[moved.min(0).tolist(),moved.max(0).tolist()],
            sampled_points=len(points),sampled_outside_inner_reservation=int((~contained).sum()),
            outside_objects=outside_objects,
            outside_witnesses_mm=witnesses[np.linspace(0,len(witnesses)-1,min(8,len(witnesses)),dtype=int)].tolist() if len(witnesses) else [],
            selected=False,rigid_internal_geometry_retained=True))
    surfaces={n:r for n,r in records.items() if r['kind']=='surface'}
    labels={n:r['label'] for n,r in surfaces.items()}
    select=lambda *prefixes:[n for n,label in labels.items() if label.startswith(prefixes)]
    add('Pi4',select('Pi4'))
    add('BUS',select('BUSsupplier'))
    add('MAIN',select('MAIN/','MAIN_','Power/MAIN'),delta=(0,0,0))
    add('PWM9685',select('PWM9685'),delta=(-50,0,-12))
    add('PWM1608_U1',select('PWM1608','U1_'),delta=(-80,0,-21))
    add('AUX4092',select('AUX4092'),delta=(40,0,-15))
    # Full TE ends span71.43mm in Z, not just the28.5mm casing.
    add('Bank12Oprawek24Koncow',select('F_L','F_R'),delta=(-10,0,-95))
    rx=np.array([[1,0,0],[0,0,-1],[0,1,0]])
    rz=np.array([[0,-1,0],[1,0,0],[0,0,1]])
    add('S0',select('S0_'),rotation=rx,new_center=(-75,2,48))
    add('S1',select('current/S1_'),rotation=rz,new_center=(137,28,34))
    for code,x,y in (('FL',-45,40),('FR',-45,-40),('RL',65,40),('RR',65,-40)):
        add('MTA_'+code,select('MTA/'+code+'/'),new_center=(x,y,56))
    n=select('F_PI_new/');assert len(n)==1
    ry=np.array([[0,0,1],[0,1,0],[-1,0,0]])
    add('F_PI',n,rotation=ry,new_center=(-110,0,-10))
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
    large_slots=[(i,1) for i in range(4)]
    small_slots=[slot for slot in slots if slot not in large_slots]
    for (n,dims),(col,row) in list(zip(large,large_slots))+list(zip(small,small_slots)):
        # Largest -> X, smallest -> Y, middle -> Z; preserve orientation parity.
        order=np.argsort(dims)
        rotation=np.eye(3)[[order[2],order[0],order[1]]]
        if np.linalg.det(rotation)<0:rotation[1]*=-1
        height=sorted(dims)[1]
        add('WAGO:'+records[n]['label'].split('/')[0],[n],rotation=rotation,
            new_center=([-64,-23,18,59,100][col],[-24,-8,8,24][row],-52+height/2))
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
        reservation_native_sha256=layout['native']['sha256'],
        proposed_cross_section_exponent=2.6,native_envelope_matches_this_proposal=False,
        native_update_condition='After the36pose worker releases the old pad/envelope source and this whole layout passes its coarse/exact space gates.',
        main_world_z46_52_retained=True,
        complete_conductor_paths=False,connector_entry_direction_verified=False,
        corridors=[dict(id='left',y_mm=58,z_mm=-15,x_mm=[-90,125],nominal_diameter_mm=30),
                   dict(id='right',y_mm=-58,z_mm=-15,x_mm=[-90,125],nominal_diameter_mm=30)],
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
    (OUT/'module-layout.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],groups=len(groups),parts=sum(len(g['objects']) for g in groups),
        outside_groups=[(g['role'],g['sampled_outside_inner_reservation']) for g in groups if g['sampled_outside_inner_reservation']],
        potential_pairs=potential,seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()
