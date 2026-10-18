"""ONE shared macro snapshot, source-pinned before exact checks. Not native.

Consumes the approved-scope all-station plan; leaves all unresolved interface,
tool, corridor and stack holds visible. Does not save any historical CAD.
"""
import hashlib
import json
import math
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_current_scene import load,box
from plan_feline_central_pi_wedge import packed
from plan_feline_front_service_split import line_tube
from plan_feline_front_bulkhead_architecture import tube
from check_feline_shared_space import tube_prefix


def main():
    tick=time.monotonic();dest=OUT/'n01-coupled-allocation-snapshot.json';assert not dest.exists()
    planpath=OUT/'n01-coupled-allocation-plan.json';plan=json.loads(planpath.read_text())
    scene,meta,templates,data,pins,_=load();proposal={};rows={};retired={};ends={};factory=[]
    files={k:OUT/n for k,n in dict(pi='n01-pi-carrier-portal.json',
        source='n01-front-service-split-plan.json',extra='n01-all-extra-interface-contract.json',
        local='n01-selected-local-head-tail-sources.json',map='n01-whole-constraint-map.json').items()}
    docs={k:json.loads(f.read_text()) for k,f in files.items()}
    def put(n,s,group,kind='proposal_material',wire_owner=None):
        assert s.isValid(),n
        proposal[n]=s;rows[n]=dict(name=n,group=group,kind=kind,wire_owner=wire_owner)
    def remove(n):
        retired[n]=meta.pop(n);scene.pop(n)
    def first_profile(n,q,d,b,r,R,first,group,owner):
        finish=q+d*(first+R)+b*R;tip=finish+b*9
        put(n,tube_prefix(list(q),list(d),r,list(b),R,first),group,'proposal_wire',owner)
        put(n+':grip',line_tube(list(finish),list(tip),r),group,'proposal_wire',owner)
        return dict(point_mm=list(q),departure_axis=list(d),bend_unit=list(b),R_mm=R,
            first_mm=first,after_grip_line_mm=[list(finish),list(tip)])
    _,oldpi,oldpirows=packed(files['pi'])
    for n,s in oldpi.items():
        if n.startswith('PiPortal:'):continue
        s.translate(A.Vector(0,0,1));r=oldpirows[n]
        owner=n.removesuffix(':grip') if r['kind']=='proposal_wire' else None
        put(n,s,'PiCoupled',r['kind'],owner)
    for n,s in list(scene.items()):
        role=meta[n].get('role','')
        if role=='Pi4' or n.startswith(('StructureReserve:PCBrootPi4','StructureReserve:PCBrailPi4')):
            remove(n)
        elif role=='PWM9685':
            s=s.copy();s.translate(A.Vector(*plan['PWM9685']['whole_current_group_delta_mm']))
            remove(n);put(n,s,'PWMLower')
        elif n.startswith(('StructureReserve:PCBrootPWM9685','StructureReserve:PCBrailPWM9685','StructureReserve:PWMForeBranch')):
            remove(n)
        elif role=='HeadMechanism':
            s=s.copy();s.translate(A.Vector(0,0,35));remove(n);put(n,s,'HeadRaised')
    # Keep the ACTUAL existing MAIN channel, not a reconstructed solid cap.
    n='StructureReserve:UpperStrip-1';cap=scene[n].common(box([-84,-32,70],[-27.5,-9,90]))
    assert cap.Solids and cap.isValid();remove(n);put('RetainedMAINCutForeCap',cap,'MAINStructure','reservation')
    remove('StructureReserve:UpperStrip1')
    _,old,oldrows=packed(files['source'])
    for n,s in old.items():
        if oldrows[n]['group'] in ('F_PWM','Monitor5015'):
            r=oldrows[n];put(n,s,r['group'],r['kind'],n.split(':')[0] if r['kind']=='proposal_wire' else None)
    # All19 relocated station cases; P_SYS is deliberately source-fixed.
    stations={r['ref']:r for r in data['ports']['stations']};changed_groups=set()
    for row in plan['WAGO_station_rows']:
        for ref,x,sign in zip(row['refs'],row['centres_X_mm'],row['departure_X_signs']):
            st=stations[ref];matches=[n for n,r in meta.items() if r.get('role')==st['current_group']]
            assert len(matches)==1,(ref,matches)
            n=matches[0];s=scene[n].copy();proto=st['prototype']
            p=A.Vector(*proto['port_pitch_vector_mm']);p.normalize();d=A.Vector(*proto['departure_axis']);d.normalize()
            assert abs(p.z)<1e-6 and abs(d.z)<1e-6 and abs(p.dot(d))<1e-5
            h=1 if p.cross(d).z>0 else -1;targetp=A.Vector(0,-h*sign,0);targetd=A.Vector(sign,0,0)
            m=A.Matrix()
            for i in range(3):
                for j in range(3):setattr(m,f'A{i+1}{j+1}',targetp[i]*p[j]+targetd[i]*d[j]+(1 if i==2 and j==2 else 0))
            rot=A.Rotation(m);assert abs(rot.multVec(A.Vector(0,0,1)).z-1)<1e-6
            tf=A.Placement(A.Vector(x,row['Y_mm'],row['Z_mm'])-rot.multVec(s.BoundBox.Center),rot)
            s.Placement=tf*s.Placement;remove(n);put(n,s,'WG:'+ref);changed_groups.add(st['current_group'])
            for e in st['occupied_ports']:
                q=tf.multVec(A.Vector(*e['point_mm']));axis=rot.multVec(A.Vector(*e['departure_axis']))
                radius=2.1 if ref=='P_AUX' else 1.55
                ends[e['endpoint']]=first_profile('Station:'+e['endpoint'],q,axis,A.Vector(*row['bend_unit_mm']),
                    radius,12.4,3,'WG:'+ref,e['endpoint'])
    assert len(changed_groups)==19 and len(ends)==82
    # Retire only affected old endpoint profiles; retain MAIN and3Pi SOURCE paths.
    invalidated={e['id'] for e in data['packet']['endpoints'] if e['group'] in changed_groups or e['group'] in ('Pi4','PWM9685')}
    for n in list(scene):
        if n.startswith('End:') and n[4:] in invalidated:remove(n)
    # Current PCA occupied exits; no inferred external U1 pinout.
    pwm_ends=[e for sec in docs['extra']['sections'] for e in sec['ends'] if e['group']=='PWM9685']
    assert len(pwm_ends)==7;delta=A.Vector(*plan['PWM9685']['whole_current_group_delta_mm'])
    for e in pwm_ends:
        q=A.Vector(*e['point_mm'])+delta;d=A.Vector(*e['departure_axis'])
        b=A.Vector(-.6,-.8,0) if '.CH' in e['endpoint'] else A.Vector(-.8,.6,0)
        ends[e['endpoint']]=first_profile('PWMEnd:'+e['endpoint'],q,d,b,.7,10,3,'PWMLower',e['endpoint'])
    pcbs=[s for n,s in proposal.items() if rows[n]['group']=='PWMLower' and 'PCB' in n]
    assert len(pcbs)==1;bb=pcbs[0].BoundBox
    put('PWMFullOccupiedHeaderBudget',box([bb.XMin,bb.YMin,bb.ZMax],[bb.XMax,bb.YMax,26.1]),'PWMLower','reservation')
    local_ports={e['endpoint']:e for sec in docs['extra']['sections'] for e in sec['ends'] if e.get('local_point_mm') is not None}
    for spec in plan['FHAC']:
        role=spec['role'];centre=A.Vector(*spec['centre_mm']);_,case,_=templates[role];case=case.copy()
        rot=A.Rotation(A.Vector(0,1,0),-90) if spec['source_axis_X_rotated_to']=='-Z' else A.Rotation(A.Vector(0,0,1),90)
        case.Placement=A.Placement(centre-rot.multVec(case.BoundBox.Center),rot)*case.Placement;put(role+':case',case,role)
        for side in ('in','out'):
            e=local_ports[role+'.'+side];q=centre+rot.multVec(A.Vector(*e['local_point_mm']));d=rot.multVec(A.Vector(*e['departure_axis']))
            upper=d.z>.99
            if 'both_factory_first_mm' in spec:
                first=spec['both_factory_first_mm'];b=A.Vector(*spec['outward_bend_unit' if d.y<0 else 'inward_bend_unit']);after=14
                grip=[q,q+d*9]
            else:
                first=spec['upper_factory_first_mm' if upper else 'lower_factory_first_mm']
                b=A.Vector(*spec['upper_bend_unit' if upper else 'lower_bend_unit'])
                after=spec.get('upper_factory_after_arc_mm',14) if upper else 14
                grip=None if upper else [q,q+d*9]
            a=q+d*first;mid=a+d*(12.4/2**.5)+b*(12.4*(1-1/2**.5));end=a+d*12.4+b*12.4;tip=end+b*after
            curve=Part.Wire([Part.makeLine(q,a),Part.Arc(a,mid,end).toShape(),Part.makeLine(end,tip)])
            nominal=curve.Length+3;assert nominal<100,(role,side,nominal)
            if grip is None:grip=[end,end+b*9]
            owner=role+'.'+side
            put(owner+':factory',tube(curve,2),role,'proposal_wire',owner)
            put(owner+':sleeve',line_tube(list(tip-b*14),list(tip+b*6),2.4),role,'reservation',owner)
            put(owner+':custom',line_tube(list(tip-b*8),list(tip+b*18),1.55),role,'proposal_wire',owner)
            ends[owner]=dict(point_mm=list(q),departure_axis=list(d),factory_grip_line_mm=[list(p) for p in grip],
                custom_grip_line_mm=[list(tip+b*9),list(tip+b*18)],factory_nominal_mm=nominal,
                lap_mm=8,sleeve_mm=20,after_arc_factory_mm=after,factory100mm_is_assumption=True)
            factory.append(dict(interface=owner,nominal_mm=nominal))
    _,locals_,localrows=packed(files['local'])
    for n,s in locals_.items():
        r=localrows[n]
        if r['role']=='HeadElectricalYaw':s.translate(A.Vector(0,0,35))
        put(n,s,'HeadRaised' if r['role']=='HeadElectricalYaw' else 'TailElectrical',
            'curve_NOT_full_jacket' if not s.Solids else r.get('kind','source_material'))
    bundle=dest.with_suffix('.zip');outrows=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in proposal.items():
            entry=f'{len(outrows):04}.brep';raw=s.exportBrepToString().encode();z.writestr(entry,raw)
            outrows.append(dict(rows[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest(),
                solids=len(s.Solids),bounds_mm=[[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin],[s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]]))
    result=dict(status='ONE_COUPLED_ALL_STATION_SNAPSHOT_SAVED_EXACT_GATE_PENDING',selected=False,N01_complete=False,
        physical_pass=False,parts=outrows,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),
        retired_parts=retired,retained_base_part_count=len(scene),changed_end_overrides=ends,
        six_complete_factory_budget=factory,WAGO_moved=19,WAGO_retained=['P_SYS'],
        source_sha256={**pins,planpath.relative_to(ROOT).as_posix():sha(planpath),
            **{f.relative_to(ROOT).as_posix():sha(f) for f in files.values()},Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        holds=['Exact common geometry gate BEFORE further native details',
            'No root/stack/tool/outline/motion/corridor capacity or full-middle approval yet',
            'Pi source same hardware flipped needs explicit6.2/1mm interposers, not floating nut approval',
            'PWM entire header budget is provisional; source JPWM power mate and full port housing still requires capture',
            '22local source curves are accounting geometry, not qualified full-jacket solids',
            'Known invalid BUS supplier shape remains HOLD; never count it clear'],
        worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],changed_parts=len(outrows),retained_parts=len(scene),
        ends=len(ends),factory_count=len(factory),factory_nominal_range_mm=[min(r['nominal_mm'] for r in factory),max(r['nominal_mm'] for r in factory)],
        seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
