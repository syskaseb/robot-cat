"""Shared REV3 query scene, not a full snapshot or native assembly.

Whole source cases and first profiles, while missing interfaces are explicit.
Retains world-posed BReps unchanged; repairs no imported supplier shapes.
"""
import json
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT
from feline_current_scene import load
from plan_feline_central_pi_wedge import packed
from check_feline_shared_space import tube_prefix
from plan_feline_front_service_split import line_tube
from plan_feline_front_bulkhead_architecture import tube


def build():
    files={k:OUT/n for k,n in dict(plan='n01-coupled-allocation-plan.json',
        clocked='n01-coupled-clocked-joints.json',bus='n01-bus-both-plugs-plan-r3.json',
        boundary='n01-solder-boundary-allocation.json',extra='n01-all-extra-interface-contract.json').items()}
    docs={k:json.loads(p.read_text()) for k,p in files.items()};plan=docs['plan'];assert plan['profile_revision']==3
    scene,meta,templates,data,pins,_=load();pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),__import__('pathlib').Path(__file__))})
    stations={r['ref']:r for r in data['ports']['stations']};moved={s['current_group'] for s in stations.values() if s['ref']!='P_SYS'}
    invalidated={e['id'] for e in data['packet']['endpoints'] if e['group'] in moved or e['group'] in ('Pi4','PWM9685')}
    oldcases={n:s.copy() for n,s in scene.items() if meta[n].get('role') in moved or meta[n].get('role')=='PWM9685'}
    oldmeta=dict(meta)
    for n in list(scene):
        role=meta[n].get('role','')
        if role in moved or role in ('Pi4','PWM9685') or (n.startswith('End:') and n[4:] in invalidated) or n.startswith(('StructureReserve:PCBrootPi4','StructureReserve:PCBrailPi4','StructureReserve:PCBrootPWM9685','StructureReserve:PCBrailPWM9685','StructureReserve:PWMForeBranch')) or (n.startswith('CurrentBUS:USB') and 'Overmould' not in n):
            scene.pop(n);meta.pop(n)
    _,clocked,crows=packed(files['clocked'])
    for n,s in clocked.items():
        if crows[n]['group']=='PiCoupled' and not n.startswith('PiUSBData'):
            scene[n]=s;meta[n]=crows[n]
    pwm=plan['PWM9685'];rot=A.Rotation(A.Vector(0,1,0),90)
    tf=A.Placement(A.Vector(*pwm['target_PCB_bottom_datum_mm'])-rot.multVec(A.Vector(*pwm['source_PCB_bottom_datum_mm'])),rot)
    for n,s in oldcases.items():
        if oldmeta[n].get('role')=='PWM9685':s.Placement=tf*s.Placement;scene[n]=s;meta[n]=oldmeta[n]
    for row in plan['WAGO_station_rows']:
        for ref,x,sign in zip(row['refs'],row['centres_X_mm'],row['departure_X_signs']):
            st=stations[ref];n=next(n for n in oldcases if oldmeta[n].get('role')==st['current_group']);s=oldcases[n]
            p=A.Vector(*st['prototype']['port_pitch_vector_mm']);p.normalize();d=A.Vector(*st['prototype']['departure_axis']);d.normalize();h=1 if p.cross(d).z>0 else -1
            targets=[A.Vector(0,0,h*sign*row['side']),A.Vector(sign,0,0),A.Vector(0,row['side'],0)];basis=[p,d,A.Vector(0,0,1)];m=A.Matrix()
            for i in range(3):
                for j in range(3):setattr(m,f'A{i+1}{j+1}',sum(t[i]*v[j] for t,v in zip(targets,basis)))
            r=A.Rotation(m);s0=s.copy();s0.Placement=A.Placement(A.Vector(),r)*s0.Placement;bb=s0.BoundBox
            centre=A.Vector(x,row['side']*(plan['WAGO_case_inner_face_abs_Y_mm']+bb.YLength/2),row['case_top_Z_mm']-bb.ZLength/2)
            t=A.Placement(centre-r.multVec(s.BoundBox.Center),r);s.Placement=t*s.Placement;scene[n]=s;meta[n]=dict(kind='actual_source_case')
            for e in st['occupied_ports']:
                q=t.multVec(A.Vector(*e['point_mm']));d=r.multVec(A.Vector(*e['departure_axis']));b=A.Vector(*row['bend_unit_mm']);R=12.4
                en='REV3Station:'+e['endpoint'];scene[en]=tube_prefix(list(q),list(d),2.1,list(b),R,3);meta[en]=dict(kind='wire')
                tip=q+d*(3+R)+b*R;scene[en+':after9']=line_tube(list(tip),list(tip+b*9),2.1);meta[en+':after9']=dict(kind='wire')
    for spec in plan['FHAC']+[dict(role='Monitor5015',**plan['Monitor5015'])]:
        n,s,r=templates[spec['role']];s=s.copy();rot=A.Rotation(A.Vector(0,1,0),-90) if spec['role']!='Monitor5015' else A.Rotation(A.Vector(1,0,0),-90)
        s.Placement=A.Placement(A.Vector(*spec['centre_mm'])-rot.multVec(s.BoundBox.Center),rot)*s.Placement
        scene['REV3:'+spec['role']]=s;meta['REV3:'+spec['role']]=dict(kind='actual_source_case')
        if spec['role']=='Monitor5015':continue
        local={e['endpoint']:e for sec in docs['extra']['sections'] for e in sec['ends'] if e.get('local_point_mm') is not None}
        for side in ('in','out'):
            e=local[spec['role']+'.'+side];q=A.Vector(*spec['centre_mm'])+rot.multVec(A.Vector(*e['local_point_mm']));d=rot.multVec(A.Vector(*e['departure_axis']));b=A.Vector(*spec['bend_unit_mm'])
            a=q+d*9;mid=a+d*(12.4/2**.5)+b*(12.4*(1-1/2**.5));end=a+d*12.4+b*12.4;tip=end+b*14
            curve=Part.Wire([Part.makeLine(q,a),Part.Arc(a,mid,end).toShape(),Part.makeLine(end,tip)])
            en='REV3:'+spec['role']+'.'+side
            scene[en+':factory']=tube(curve,2);meta[en+':factory']=dict(kind='wire')
            scene[en+':sleeve']=line_tube(list(tip-b*14),list(tip+b*6),2.4);meta[en+':sleeve']=dict(kind='insulation_reservation')
            scene[en+':custom']=line_tube(list(tip-b*8),list(tip+b*18),1.55);meta[en+':custom']=dict(kind='wire')
    for e in docs['boundary']['ends']:
        en='REV3:PCA:'+e['wire'];q=A.Vector(*e['jacket_mouth_world_mm']);d=A.Vector(*e['jacket_departure_axis']);b=A.Vector(0,-1,0) if e['wire'].startswith('XS') else A.Vector(0,0,-1)
        first=1.5 if e['wire'].startswith('XS') else 9;R=e['minimum_fixed_project_R_mm'];radius=e['first_jacket_radius_mm'];tip=q+d*(first+R)+b*R
        scene[en]=tube_prefix(list(q),list(d),radius,list(b),R,first);meta[en]=dict(kind='wire')
        scene[en+':after9']=line_tube(list(tip),list(tip+b*9),radius);meta[en+':after9']=dict(kind='wire')
        for i,seg in enumerate(e['bare_segments']):
            assert seg['kind']=='line';scene[en+':bare'+str(i)]=line_tube(seg['start'],seg['end'],e['bare_radius_project_mm']);meta[en+':bare'+str(i)]=dict(kind='wire')
    # Invalid transformed BUS shape is not healed. Query its ORIGINAL valid
    # saved shape in the inverse rigid frame. Exact distances are invariant.
    reader=SavedShapes();name='Ref_Material_BUSsupplier25_0_0';original=reader.shape(OUT/'FelineInteriorMotion.FCStd',name)
    assert original.isValid() and original.Solids,'Invalid original BUS source: leave HOLD'
    bus=docs['bus']['relative_BUS_pose'];m=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(m,f'A{i+1}{j+1}',bus['rotation_rows'][i][j])
    rot=A.Rotation(m);tf=A.Placement(A.Vector(*bus['translation_mm']),rot)
    posed=original.copy();posed.Placement=tf*posed.Placement
    assert (posed.BoundBox.Center-scene[name].BoundBox.Center).Length<1e-6
    assert max(abs(getattr(posed.BoundBox,k)-getattr(scene[name].BoundBox,k)) for k in ('XMin','XMax','YMin','YMax','ZMin','ZMax'))<1e-5
    pins.update(reader.hashes)
    return scene,meta,pins,dict(name=name,original=original,inverse=tf.inverse(),
        method='Exact inverse rigid query against original valid BRep; no healing; bounds datum checked')
