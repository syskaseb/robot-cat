"""One bounded all-orientation F_PI space/lead-budget search, no native CAD.

Disjoint real-part bounds prove separation; overlap only rejects a conservative
search cell, NEVER proves real collision or physical infeasibility. Both source
leads, initial wire lands, receiver relief and E6 pre-fuse50mm budget participate.
No candidate is selectable without full curves, roots, tools and motion.
"""
import itertools,json,time
from datetime import datetime,timezone
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT


def main():
    tick=time.monotonic();dest=OUT/'n01-pi-fuse-bay-search.json';assert not dest.exists(),'Receive existing bounded search'
    native=OUT/'FelineInteriorMotion.FCStd';files=[OUT/n for n in ('n01-module-plan-r5.json',
        'n01-shared-preflight-r5.json','n01-compact-bank-plan-r2.json','n01-complete-end-allocation.json',
        'n01-common-backbone-preflight-r4.json','motion-layout.json')]
    plan,lower,bank,ledger,frame,motion=[json.loads(p.read_text()) for p in files]
    files.extend([OUT.parent/'body-harness-checkpoint/source-receiving-plan.json',
        OUT.parent/'body-harness-checkpoint/main-pi-plan.json',ROOT/'hardware/electronics/power-platform/MAIN-INPUT-P0.md'])
    assert sha(native)==bank['source_native_sha256']
    result=dict(status='RUNNING',selected=False,N01_complete=False,physical_pass=False,native_changed=False,
        grid_step_mm=5,orientations=24,orientation_results=[],candidates=[],
        input_first_wire_land_mm=6.5,output_first_wire_land_mm=3,
        receiver_full_intact_grips_mm=9,output_bare_overlap_mm=8,
        factory_shortest_raw_mm=84.5,E6_input_project_raw_limit_mm=50,
        enclosure_search_box_mm=[[-160,-95.6,-45.6],[181.1,95.6,109.6]],
        basis='Existing source-receiving recipe6.5mm input thenR6/downstream9mm relief; main-pi recipe3mm output thenR6. Not manufacturer bend guarantees.',
        conservative_search_not_actual_collision=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files+[native,Path(__file__)]})
    def save():
        result.update(worker_seconds=round(time.monotonic()-tick,3),updated_utc=datetime.now(timezone.utc).isoformat())
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>120:
            result['status']='BOUNDED_SEARCH_PARTIAL_NOT_SELECTED';save();raise TimeoutError('120s search cap')
    save();reader=SavedShapes();boxes=[];names=[]
    def add(n,s):
        b=s.BoundBox;boxes.append([[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]);names.append(n)
    for g in plan['groups']:
        role=g['role']
        if role=='F_PI' or role.startswith('Bank'):continue
        for n in g['objects']:
            gate();s=reader.shape(native,n)
            if role in lower['changed_complete_receiving_groups']:
                rot=A.Rotation(A.Vector(1,0,0),90) if role in lower['relative_rotations'] else A.Rotation()
                s.Placement=A.Placement(A.Vector(*lower['changed_complete_receiving_groups'][role]),rot)*s.Placement
            d={'JPWM':[-90,44,30],'W041_Joint':[0,15,3],'W042_Joint':[0,-15,3]}.get(role)
            if d:s.translate(A.Vector(*d))
            add(n,s)
    for key,p in bank['relative_holder_poses'].items():
        m=A.Matrix()
        for i in range(3):
            for j in range(3):setattr(m,f'A{i+1}{j+1}',p['rotation_rows'][i][j])
        pose=A.Placement(A.Vector(*p['translation_mm']),A.Rotation(m))
        for kind in ('Housing','IN','OUT','ATO'):
            n=f'Ref_Material_F_{key}_CP2_{kind}_0_0';s=reader.shape(native,n);s.Placement=pose*s.Placement;add(n,s)
    moving={n for g in motion['membership'].values() for ns in g.values() for n in ns}
    for row in motion['inventory']:
        n=row['object']
        if n in names or n in moving or row['kind']!='surface':continue
        if n.startswith(('Print_P0_','Ref_Material_P0_','Battery','Print_CP2_TailRiser')):
            if not n.startswith('BatteryFrameHardware'):add(n,reader.shape(native,n))
    for i in range(1,5):add(f'BellyFoot{i}',reader.shape(native,f'BellyFoot{i}'))
    for row in frame['recipes']:
        if row['name'].startswith(('PiFuseCradle','PiFuseRiser')):continue
        if 'low_mm' in row:boxes.append([row['low_mm'],row['high_mm']]);names.append('Reservation:'+row['name'])
    obstacles=np.array(boxes);olo,ohi=obstacles[:,0],obstacles[:,1]
    points=np.array(list(itertools.product(range(-145,151,5),range(-80,81,5),range(-30,101,5))),dtype=float)
    ends={r['role']:r for r in ledger['endpoints']};receiver_in=np.array(ends['P_SYS.5']['point_mm'])
    in_axis=np.array(ends['P_SYS.5']['departure_axis']);in_free=receiver_in+9*in_axis
    receiver_out=np.array(ends['SPLICE_PI.16']['point_mm'])
    # Existing horizontal splice:16AWG approaches +X; intact land is17mm
    # behind its bare tip (8mm overlap then9mm jacket), not9mm bare wire.
    out_free=receiver_out+np.array([-17,0,0])
    innerlo,innerhi=np.array(result['enclosure_search_box_mm'])
    def clear(lows,highs):
        keep=np.ones(len(lows),bool)
        for start in range(0,len(lows),1000):
            gate();lo=lows[start:start+1000,None,:];hi=highs[start:start+1000,None,:]
            overlap=np.all((lo<ohi[None,:,:]+1.25)&(hi>olo[None,:,:]-1.25),axis=2)
            keep[start:start+1000]=~np.any(overlap,axis=1)
        return keep
    for order in itertools.permutations(range(3)):
        for signs in itertools.product((-1,1),repeat=3):
            rr=np.zeros((3,3))
            for i,j in enumerate(order):rr[i,j]=signs[i]
            if np.linalg.det(rr)<0:continue
            axis=rr@np.array([1,0,0]);half=np.abs(rr)@np.array([25.5,11,10.125])
            pin=points+25.5*axis;pout=points-25.5*axis
            input_lower=6.5+np.linalg.norm(pin+6.5*axis-in_free,axis=1)+9+12
            output_lower=3+np.linalg.norm(pout-3*axis-out_free,axis=1)+17
            select=(input_lower<=50)&(output_lower<=84.5)&np.all(points-half>=innerlo,axis=1)&np.all(points+half<=innerhi,axis=1)
            ps=points[select];lin=input_lower[select];lout=output_lower[select]
            count=len(ps)
            if count:
                keep=clear(ps-half,ps+half);ps,lin,lout=ps[keep],lin[keep],lout[keep]
            cases=len(ps)
            if cases:
                pin=ps+25.5*axis;pout=ps-25.5*axis
                lo=np.minimum(pin,pin+6.5*axis)-2;hi=np.maximum(pin,pin+6.5*axis)+2
                keep=clear(lo,hi);ps,lin,lout=ps[keep],lin[keep],lout[keep]
            if len(ps):
                pout=ps-25.5*axis;lo=np.minimum(pout,pout-3*axis)-2;hi=np.maximum(pout,pout-3*axis)+2
                keep=clear(lo,hi);ps,lin,lout=ps[keep],lin[keep],lout[keep]
            result['orientation_results'].append(dict(rotation_rows=rr.tolist(),necessary_length_cells=count,
                conservative_case_clear_cells=cases,case_and_initial_wire_clear_cells=len(ps)))
            for i in np.argsort(lin+lout)[:3]:
                result['candidates'].append(dict(centre_mm=ps[i].tolist(),rotation_relative_current=rr.tolist(),
                    input_raw_lower_bound_mm=float(lin[i]),output_raw_lower_bound_mm=float(lout[i]),
                    complete_curves=False,downstream_grips_tools_and_motion=False,selected=False))
            save()
    result['candidates']=sorted(result['candidates'],key=lambda r:r['input_raw_lower_bound_mm']+r['output_raw_lower_bound_mm'])[:10]
    result['fixed_obstacle_count']=len(boxes);result['source_sha256'].update(reader.hashes)
    result['status']='NECESSARY_SPACE_AND_LEAD_CANDIDATES_FOUND_FULL_PATHS_OPEN' if result['candidates'] else 'NO_CONSERVATIVE_GRID_CANDIDATE_NOT_PROOF_OF_PHYSICAL_INFEASIBILITY'
    result['next']='No case-only selection. If no candidate, change F_PI/P_SYS/splice architecture together; do not retry scalar holder nudges. All proposed support boxes treated conservatively; overlap is not actual contact.'
    save();print(json.dumps(dict(status=result['status'],candidates=len(result['candidates']),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
