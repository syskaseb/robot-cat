"""Changed15end contracts plus actual S0 throats; no unchanged full rerun.

Also check the complete rotated POST_F0 and nominal K-1474 mould against
the retained whole scene. Unfinished owned restraint channels remain OPEN.
"""
import json
import time
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT
from check_feline_all_current_lands import near


def main():
    tick=time.monotonic();dest=OUT/'n01-reconciled-port-contracts-gate.json';assert not dest.exists()
    paths={k:OUT/n for k,n in dict(packet='n01-current-endpoint-packet-r3.json',
        prior='n01-all-current-first-lands.json',scene='n01-full-material-scene.json',lower='n01-lower-bay-world-probe.json').items()}
    p={k:json.loads(f.read_text()) for k,f in paths.items()};packet=p['packet']
    ends={e['id']:e for e in packet['endpoints']};recipes={r['id']:r for r in p['prior']['land_recipes']}
    changed={r['id'] for r in packet['contract_changes']};assert len(changed)==15
    report=dict(status='RUNNING_COUPLED_CONTRACT_CHANGES',selected=False,N01_complete=False,physical_pass=False,
        contacts=[],reservation_contacts=[],errors=[],jacket_conflicts=[],pairs=0,wire_pairs=0,
        changed_end_ids=sorted(changed),source_crimp_jacket_lands=[],component_mating_pairs=[],
        outside=[],wall_failures=[],full178first_land_or_middle_or_motion_acceptance=False,
        retained_open=['Owned cuff/arm and MAIN/P_SYS groove material','MAIN existing insulating band0.75mm air vs1.25general budget','Full middle routes/independent grips/stock/tools/motion'],
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (*paths.values(),Path(__file__))})
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s coupled-contract budget')
    scene={};meta={}
    for key in ('scene','lower'):
        bundle=ROOT/p[key]['bundle'];assert sha(bundle)==p[key]['bundle_sha256']
        report['source_sha256'][bundle.relative_to(ROOT).as_posix()]=sha(bundle)
        with zipfile.ZipFile(bundle) as z:
            for row in p[key]['parts']:
                if row.get('role')=='CurrentCassette' or row.get('role','').startswith('leg:'):continue
                s=Part.Shape();s.importBrepFromString(z.read(row['entry']).decode('utf-8'))
                scene[row['name']]=s;meta[row['name']]=row
    changedparts=set()
    pose=packet['changed_scene_groups']['POST_F0'];R=pose['relative_rotation_rows'];m=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(m,f'A{i+1}{j+1}',R[i][j])
    c=A.Vector(*pose['centre_mm']);rot=A.Rotation(m);tf=A.Placement(c-rot.multVec(c),rot)
    for n,s in scene.items():
        if meta[n].get('role')=='POST_F0':s.Placement=tf*s.Placement;changedparts.add(n)
    lo,hi=packet['nominal_Pi_USB_C_mould']['bounds_mm'];name='NominalPiUSBCPowerMould'
    scene[name]=Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))
    meta[name]=dict(role='Pi4',kind='project_mating_reservation');changedparts.add(name)
    boxes={n:s.BoundBox for n,s in scene.items()};valid={n:s.isValid() and bool(s.Solids) for n,s in scene.items()}
    def matched_restraint(n,e):
        return n.startswith(('Seat:'+e['wire']+':','TieLoop:Seat:'+e['wire']+':'))
    def mate(n,e):return meta[n].get('role')==e['group'] or meta[n].get('owner')==e['group'] and meta[n]['kind']=='actual_case'
    def samewire(n,e):return n in (e['wire'],'Factory:'+e['wire'],'CustomPrefix:'+e['wire'],'End:'+e['id']) or (e['wire']=='W002' and n=='CurrentBUS:BUS.D') or (e['wire']=='W003' and n=='CurrentBUS:BUS.G')
    lands={};landrows={}
    def record(a,s,n,t,gap_budget=1.25,own=False):
        gate()
        if not near(s.BoundBox,t.BoundBox,gap_budget):return
        report['pairs']+=1
        assert s.isValid() and t.isValid(),(a,n,'Invalid candidate')
        x=s.common(t);assert x.isNull() or x.isValid(),(a,n)
        volume=x.Volume;gap=s.distToShape(t)[0] if volume<=1e-5 else 0
        if volume>1e-5 or gap<gap_budget-1e-5:
            row=dict(a=a,b=n,volume_mm3=volume,gap_mm=gap,required_gap_mm=gap_budget,nominal_mate_trim=own)
            report['reservation_contacts' if 'reservation' in meta[n]['kind'] else 'contacts'].append(row)
    try:
        save()
        for n in changedparts:
            assert valid[n],n
            for other,s in scene.items():
                if other==n:continue
                # Nominal plug mates the PCB edge. Only zero-volume contact
                # to that particular PCB is allowed, not an entire Pi group.
                if n==name and other=='Ref_Material_Pi4NominalPCB_0_0':
                    x=scene[n].common(s);assert x.isNull() or x.isValid()
                    assert x.Volume<=1e-5
                    report['component_mating_pairs'].append(dict(a=n,b=other,volume_mm3=x.Volume));continue
                record(n,scene[n],other,s)
        for key,r in recipes.items():
            e=ends[key];a=np.array(e['point_mm']);d=np.array(e['departure_axis']);radius=e.get('nominal_project_wire_radius_mm',r['radius_mm']);length=r['straight_mm']
            if e['group']=='S0':
                ring='Ref_Material_S0_ring_OUT_0_0' if e['wire']=='W066' else 'Ref_Material_S0_ring_IN_0_0'
                probe=Part.makeCylinder(radius,20,A.Vector(*a),A.Vector(*d));common=probe.common(scene[ring]);assert common.isValid() and common.Volume>0
                local=common.copy();frame=A.Placement(A.Vector(*a),A.Rotation(A.Vector(0,0,1),A.Vector(*d)))
                local.Placement=frame.inverse()*local.Placement
                allowance=local.optimalBoundingBox().ZMax+.25;assert 0<allowance<9
                report['source_crimp_jacket_lands'].append(dict(id=key,actual_reference_ring=ring,
                    source_throat_allowance_mm=allowance,jacket_land_mm=9,
                    basis='Nominal source metal-barrel extent plus0.25project clearance, not producer insertion depth'))
                a=a+allowance*d;length=9;changed.add(key)
            s=Part.makeCylinder(radius,length,A.Vector(*a),A.Vector(*d));lands[key]=s
            landrows[key]=dict(id=key,start_mm=a.tolist(),axis=d.tolist(),radius_mm=radius,straight_mm=length)
            if key not in changed:continue
            for n,t in scene.items():
                if samewire(n,e):continue
                tested=Part.makeCylinder(radius,length-2.5,A.Vector(*(a+2.5*d)),A.Vector(*d)) if mate(n,e) else s
                record(key,tested,n,t,.2 if matched_restraint(n,e) else 1.25,mate(n,e))
        for key,s in lands.items():
            if key in changed:continue
            for n in changedparts:record(key,s,n,scene[n])
        keys=list(lands)
        for i,a in enumerate(keys):
            for b in keys[i+1:]:
                gate()
                if a not in changed and b not in changed:continue
                if not near(lands[a].BoundBox,lands[b].BoundBox,.2):continue
                report['wire_pairs']+=1;gap=lands[a].distToShape(lands[b])[0]
                if gap<.2-1e-5:report['jacket_conflicts'].append(dict(a=a,b=b,gap_mm=gap))
        reader=SavedShapes();outer=reader.shape(OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd','TorsoEnvelope')
        shell=Part.makeCompound(outer.Shells)
        for n,s in {**{n:scene[n] for n in changedparts},**{n:lands[n] for n in changed}}.items():
            gate();diff=s.cut(outer);assert diff.isNull() or diff.isValid(),n
            if diff.Volume>1e-5:report['outside'].append(dict(name=n,volume_mm3=diff.Volume))
            elif s.distToShape(shell)[0]<3.65:report['wall_failures'].append(n)
        report['source_sha256'].update(reader.hashes)
        report['status']='CHANGED_CURRENT_PORT_CONTRACTS_CLEAR_RESTRAINT_CHANNELS_FULL_WIRING_OPEN' if not any(report[k] for k in ('contacts','reservation_contacts','jacket_conflicts','errors','outside','wall_failures')) else 'COUPLED_CHANGED_CONTRACTS_REJECTED'
    except Exception as exc:report['errors'].append(repr(exc));report['status']='COUPLED_CHANGED_CONTRACTS_PARTIAL'
    report['changed_end_ids']=sorted(changed);report['changed_scene_parts']=sorted(changedparts)
    report['land_recipes']=list(landrows.values())
    save();print(json.dumps({k:report[k] for k in ('status','worker_seconds','pairs','wire_pairs','errors')})+
        f" contacts={len(report['contacts'])} reserves={len(report['reservation_contacts'])} jackets={len(report['jacket_conflicts'])}",flush=True)


if __name__=='__main__':main()
