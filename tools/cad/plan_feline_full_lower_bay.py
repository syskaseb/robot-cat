"""One shared lower-bay cause change against the complete805part scene.

Retain U1/F0/AUX/rails. Restore four original separated MTA source cases;
allocate ALL8joints to one -34plane and inward full-grip return lanes.
No upper cassette, guessed extra electrical part, native build or selection.
"""
import copy
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,BASE,MODEL,STAGES
from plan_feline_factory_links import routes
from plan_feline_endpoints import transfer_port,source_port_frames
from plan_feline_n01_shared import pipe
from check_feline_leg_body import placement


def main():
    tick=time.monotonic();reader=SavedShapes();dest=OUT/'n01-full-lower-bay-plan.json'
    assert not dest.exists(),'Receive existing complete/partial result first'
    paths={k:OUT/n for k,n in dict(scene='n01-full-material-scene.json',
        modules='n01-module-plan-r5.json',rear='n01-shared-preflight-r5.json',
        cassette='n01-cassette-world-probe.json',motion='motion-layout.json').items()}
    p={k:json.loads(path.read_text()) for k,path in paths.items()}
    assert p['scene']['status']=='FULL_CURRENT_MODULE_DEPENDENCY_REJECTED'
    assert {r['b_role'] for r in p['scene']['contacts']}=={'F0','PWM1608_U1'}
    assert sha(ROOT/p['scene']['bundle'])==p['scene']['bundle_sha256']
    native=OUT/'FelineInteriorMotion.FCStd';effective=copy.deepcopy(p['modules'])
    groups={g['role']:g for g in effective['groups']}
    targets={'W026_Joint':[-97,15,-34],'W037_Joint':[-97,-15,-34],
        'W045_Joint':[121,15,-34],'W053_Joint':[121,-15,-34],
        'W041_Joint':[48,33.25,-34],'W042_Joint':[48,-33.25,-34],
        'W044_Joint':[-22,33.25,-34],'W052_Joint':[-22,-33.25,-34]}
    deltas={}
    for role,target in targets.items():
        g=groups[role];delta=np.array(target)-np.mean(g['candidate_bounds_mm'],axis=0)
        g['translation_mm']=(np.array(g['translation_mm'])+delta).tolist();deltas[role]=delta.tolist()
        g['candidate_bounds_mm']=(np.array(g['candidate_bounds_mm'])+delta).tolist()
    report=dict(status='RUNNING_FULL_SHARED_LOWER_BAY',selected=False,N01_complete=False,physical_pass=False,
        native_changed=False,contacts=[],reservation_contacts=[],planned_material_unions=[],errors=[],
        outside=[],wall_failures=[],poses=[],pairs=0,wire_seats=[],factory_routes=[],custom_ends=[],parts=[],
        changed_cause='Complete scene invalidated central cassette against retained U1/F0. Keep those modules; four original separated MTA sources plus ALL8whole joints at common-34plane, full9mm grips and inboard returns allocated together.',
        source_cases='Retained R5 four purchased MTA positions/orientations, not old transverse-column or two-tier cassette',
        joint_centres_mm=targets,
        lane_basis_mm=dict(retained_U1_maxY=27.4,full_wire_seat_R=4.35,required_gap=1.25,chosen_absY=33.25,conservative_gap=1.5),
        print_plan='Two independent lower panels splitX20 with1.25gap; each owns its front/rear four existing M2axes. No thin lap joint or added panel-coupling hardware.',
        quantities_candidate=dict(factory_usable100mm_is_assumption=True,wire_ties_T18I=24,case_ties_T18I=12,
            M2x10_delta=-8,M2x12_delta=8,new_electrical_parts=0,stock_selected=False),
        actual_joint_seats_root_bearings_native_material_and_whole_removal_open=True,
        source_sha256={path.relative_to(ROOT).as_posix():sha(path) for path in paths.values()})
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s stage cap, retain partial result')
    def box(a,b):return Part.makeBox(*(v-u for u,v in zip(a,b)),A.Vector(*a))
    fixed={};fixedrows={};new={};kind={};owner={}
    with zipfile.ZipFile(ROOT/p['scene']['bundle']) as z:
        for r in p['scene']['parts']:
            if r['role']=='CurrentCassette':continue
            s=Part.Shape();s.importBrepFromString(z.read(r['entry']).decode('utf-8'))
            fixed[r['name']]=s;fixedrows[r['name']]=r
    # Retain the passing lower-root and hardware geometry, not its upper tray.
    assert sha(ROOT/p['cassette']['bundle'])==p['cassette']['bundle_sha256']
    with zipfile.ZipFile(ROOT/p['cassette']['bundle']) as z:
        for r in p['cassette']['parts']:
            n=r['name']
            if not n.startswith(('RootPlateReserve','RootWebReserve','FootHardwareCandidate')):continue
            s=Part.Shape();s.importBrepFromString(z.read(r['entry']).decode('utf-8'))
            new[n]=s;kind[n]=r['kind'];owner[n]='ForePanel' if s.BoundBox.Center.x<20 else 'RearPanel'
    moved=p['rear']['changed_complete_receiving_groups'];rr=p['rear']['relative_rotations']
    for role in ['MTA_'+c for c in ('FL','FR','RL','RR')]+list(targets):
        g=groups[role]
        for n in g['objects']:
            s=reader.shape(native,n)
            if role in moved:
                m=A.Matrix();R=rr.get(role,[[1,0,0],[0,1,0],[0,0,1]])
                for i in range(3):
                    for j in range(3):setattr(m,f'A{i+1}{j+1}',R[i][j])
                s.Placement=A.Placement(A.Vector(*moved[role]),A.Rotation(m))*s.Placement
            if role in deltas:s.translate(A.Vector(*deltas[role]))
            assert s.isValid() and s.Solids,n
            expected=np.mean(g['candidate_bounds_mm'],axis=0)
            assert np.linalg.norm(np.array(list(s.BoundBox.Center))-expected)<1e-4,(role,expected,list(s.BoundBox.Center))
            new[n]=s;kind[n]='actual_case';owner[n]=role
    report['effective_factory_groups']={r:groups[r] for r in targets if r in groups}
    factory=routes(effective);report['factory_routes']=factory
    for r in factory:
        n='Factory:'+r['wire'];new[n]=pipe(r['parts'],r['radius_mm']);kind[n]='actual_wire'
        owner[n]=[r['source_group'],r['joint_group']]
    source=BASE/'body-harness-checkpoint/remaining25-interface-allocation.json'
    ends={e['id']:e for e in json.loads(source.read_text())['ends']};frames=source_port_frames(effective)
    for r in factory:
        w=r['wire'];e=ends[w+'/custom/start']
        role,pt,_=transfer_port(effective,e['role'],e['point_world_mm'],frames=frames)
        # Legacy custom land may be AFTER an old bend. It is not a port axis.
        # Whole inline221-412 custom exit opposes its declared factory exit.
        d=-np.array(groups[role]['factory_exit_axis'])
        assert abs(abs(d[0])-1)<1e-6 and abs(d[1])+abs(d[2])<1e-6
        n='CustomPrefix:'+w;new[n]=Part.makeCylinder(2.1,9.25,A.Vector(*pt),A.Vector(*d));kind[n]='actual_wire';owner[n]=[role]
        report['custom_ends'].append(dict(wire=w,id=w+'/custom/start',role=role,point_mm=pt.tolist(),departure_axis=d.tolist(),prefix_mm=9.25,nominal_CAD_port_not_delivered_measurement=True))
    def seat(name,w,start,d):
        q=np.array(start)+9*np.array(d);x=min(start[0],q[0]);y,z=start[1:]
        outer=Part.makeCylinder(4.35,9,A.Vector(x,y,z),A.Vector(1,0,0))
        cavity=Part.makeCylinder(2.35,11,A.Vector(x-1,y,z),A.Vector(1,0,0))
        s=outer.cut(cavity).cut(box([x-1,y-5,z],[x+10,y+5,z+5]))
        s=s.fuse(box([x,y-3,-42.2],[x+9,y+3,z-3.8])).cut(cavity)
        s=s.cut(box([x+3.1,y-5,-40.5],[x+5.9,y+5,-39.1])).removeSplitter()
        assert s.isValid() and len(s.Solids)==1,name
        new[name]=s;kind[name]='seat_reservation';owner[name]='ForePanel' if (x+4.5)<20 else 'RearPanel'
        report['wire_seats'].append(dict(name=name,wire=w,land_start_mm=list(start),land_end_mm=q.tolist(),length_mm=9,wall_mm=2,delivered_wire_and_tie_fit_gate=True))
    for r in factory:
        w=r['wire'];first,last=r['parts'][0],r['parts'][-1]
        for i,(line,end) in enumerate(((first,False),(last,True))):
            a,b=np.array(line['start']),np.array(line['end']);d=(b-a)/np.linalg.norm(b-a)
            start=b-9.25*d if end else a+.25*d
            seat('Seat:'+w+':factory:'+str(i),w,start,d)
    for e in report['custom_ends']:
        d=np.array(e['departure_axis']);start=np.array(e['point_mm'])+.25*d
        seat('Seat:'+e['wire']+':custom',e['wire'],start,d)
    assert len(report['wire_seats'])==24
    for label,lo,hi in (('ForePanel',-117.5,19.375),('RearPanel',20.625,129.5)):
        s=box([lo,-28,-44.3],[hi,28,-42])
        if label=='RearPanel':
            # Leave the actual central XT60 (-43.2bottom) and its mating lane
            # free. Rear joint paddles are two side branches, not a full slab.
            for ya,yb in ((-21.75,-8.25),(8.25,21.75)):
                s=s.fuse(box([125,ya,-44.3],[142.5,yb,-42]))
        for x in (-80,-70,112,122):
            for y in (-22.5,22.5):s=s.cut(Part.makeCylinder(3.25,5,A.Vector(x,y,-45)))
        for y0,y1 in ((-28,-26),(26,28)):s=s.fuse(box([lo,y0,-42.1],[hi,y1,-38]))
        for a,b in ((-51.25,-1.75),(28,77.5)):
            for ya,yb in ((-40,-26.5),(26.5,40)):
                aa,bb=max(lo,a),min(hi,b)
                if bb>aa:s=s.fuse(box([aa,ya,-44.3],[bb,yb,-42]))
        s=s.removeSplitter();assert s.isValid() and len(s.Solids)==1
        n='LowerBay:'+label;new[n]=s;kind[n]='frame_reservation';owner[n]=label
    bounds={n:s.BoundBox for n,s in {**fixed,**new}.items()}
    valid={n:s.isValid() and bool(s.Solids) for n,s in {**fixed,**new}.items()}
    def check(n,s,m,t,pose=None):
        gate();b=t.BoundBox if pose is not None else bounds[m]
        if not bounds[n].intersect(b):return
        report['pairs']+=1
        if not valid[n] or not (t.isValid() and t.Solids):
            report['errors'].append(dict(a=n,b=m,error='Invalid actual candidate pair'));return
        c=s.common(t);assert c.isNull() or c.isValid(),(n,m)
        if c.Volume<=1e-5:return
        row=dict(a=n,b=m,pose=pose,volume_mm3=c.Volume)
        # Explicit ownership of planned unions, not dropped purchased contacts.
        if pose is None and m.startswith('StructureReserve:') and kind[n] in ('frame_reservation','load_root_reservation'):
            if any(k in m for k in ('AUX','U1','LowerDeckRoot')):
                report['planned_material_unions'].append(row);return
        reservation='reservation' in kind[n] or m in kind and 'reservation' in kind[m] or m in fixedrows and 'reservation' in fixedrows[m]['kind']
        report['reservation_contacts' if reservation else 'contacts'].append(row)
    try:
        save()
        for n,s in new.items():
            for m,t in fixed.items():
                if fixedrows[m]['role'].startswith('leg:'):continue
                check(n,s,m,t)
        for i,(n,s) in enumerate(new.items()):
            for m,t in list(new.items())[i+1:]:
                if kind[n].endswith('reservation') and kind[m].endswith('reservation') and owner[n]==owner[m]:continue
                if kind[n]=='actual_wire' and owner.get(m) in owner[n] or kind[m]=='actual_wire' and owner.get(n) in owner[m]:continue
                check(n,s,m,t)
        outer=reader.shape(OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd','TorsoEnvelope');shell=Part.makeCompound(outer.Shells)
        for n,s in new.items():
            gate();diff=s.cut(outer);assert diff.isNull() or diff.isValid(),n
            if diff.Volume>1e-5:report['outside'].append(dict(object=n,volume_mm3=diff.Volume))
            else:
                gap=s.distToShape(shell)[0]
                if gap<3.65-1e-5:report['wall_failures'].append(dict(object=n,gap_mm=gap))
            b=bounds[n];report['parts'].append(dict(name=n,kind=kind[n],owner=owner[n],bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],volume_mm3=s.Volume))
        save();print('Whole static',report['pairs'],len(report['contacts']),len(report['reservation_contacts']),len(report['outside']),len(report['wall_failures']),flush=True)
        if any(report[k] for k in ('contacts','reservation_contacts','errors','outside','wall_failures')):
            report['status']='FULL_LOWER_BAY_STATIC_REJECTED_NO_MOTION_RERUN'
        else:
            axespath=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axespath.read_text())['axes'];motion=p['motion']
            moving={n:s for n,s in fixed.items() if fixedrows[n]['role'].startswith('leg:')}
            corners={n:[A.Vector(x,y,z) for x in (s.BoundBox.XMin,s.BoundBox.XMax) for y in (s.BoundBox.YMin,s.BoundBox.YMax) for z in (s.BoundBox.ZMin,s.BoundBox.ZMax)] for n,s in moving.items()}
            for index,sample in enumerate(motion['poses'][:36]):
                for code,group in motion['membership'].items():
                    aa=[next(a for a in axes if a['code']==code and a['stage']==st) for st in STAGES];tf=placement(aa,sample['legs'][code]['angles_delta_degrees'])
                    for st,names in group.items():
                        for n in names:
                            gate();B=A.BoundBox()
                            for v in corners[n]:B.add(tf[st].multVec(v))
                            near=[m for m in new if B.intersect(bounds[m])]
                            if not near:continue
                            s=moving[n].copy();s.Placement=tf[st]*s.Placement
                            for m in near:check(m,new[m],n,s,index)
                floor=motion['ground_rest_z_mm']+sample['body_drop_mm']
                report['poses'].append(dict(index=index,floor_z_mm=floor,below_floor=[n for n in new if bounds[n].ZMin<floor]));save()
            report['status']='FULL_LOWER_BAY_MOTION_REJECTED' if report['contacts'] or report['reservation_contacts'] else 'FULL_LOWER_BAY_SCOPED_CLEAR_FULL_HARNESS_JOINT_SEATS_TOOLS_NATIVE_OPEN'
    except Exception as exc:
        report['errors'].append(repr(exc));report['status']='FULL_LOWER_BAY_INCOMPLETE'
    report['source_sha256'].update(reader.hashes)
    for pp in (source,Path(__file__)):report['source_sha256'][pp.relative_to(ROOT).as_posix()]=sha(pp)
    save();print(json.dumps({k:report[k] for k in ('status','pairs','worker_seconds','errors')})+' contacts='+str(len(report['contacts']))+' reservations='+str(len(report['reservation_contacts'])),flush=True)


if __name__=='__main__':main()
