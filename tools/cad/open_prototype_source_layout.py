"""Shared low factory exits, covered joints and source-to-trunk preflight.

The four high factory return loops are replaced together. Old sources remain
unchanged; no native carrier is rebuilt by this route gate.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import time

import open_prototype_shared_space as S
import open_prototype_bundle_spines as B
import open_prototype_source_fanouts as F
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds

OUT=BASE/'wiring-checkpoint'
SOURCE=OUT/'LocalStationsAssembly.FCStd'


def factory_path(row, target):
    start=row['start_mm'];u=row['start_departure'];v=target['departure']
    a=B.add(start,B.mul(u,9));c=B.add(a,B.mul(v,6))
    b=B.add(c,B.mul(u,6))
    mid=B.add(c,B.mul(B.unit(B.sub(u,v)),6))
    end=B.add(b,B.mul(v,15))
    assert math.dist(end,target['point_mm'])<1e-7
    return [dict(kind='line',start=start,end=a),
            dict(kind='arc',start=a,mid=mid,end=b),
            dict(kind='line',start=b,end=end)]


def build_plan():
    recovery=read(OUT/'source-layout-recovery-plan.json')
    recipe=recovery['one_proposed_factory_exit_recipe']
    material=read(OUT/'covered-joint-material-plan.json')['project_recipe']
    outputs={r['holder']:r for r in read(OUT/'branch-output-plan.json')['output_recipes']}
    cuts={r['holder']:r for r in recipe['proposed_cut_datums']}
    groups=S.build_plan()['groups']
    head=next(g for g in groups if g['group']=='HY')
    # The previous north-facing intake forced signals below the rounded torso
    # corner to reverse. Change the whole intake to westwards, toward the head.
    head['centre_points_mm']=[[-45,-15,134],[-76,-15,134],[-76,-56.8,134],
                             [-76,-56.8,85.2],[-112,-56.8,85.2]]
    centre_parts=B.segments(head['centre_points_mm'])
    head['rows']=[dict(wire=n,segments=B.offsets(centre_parts,[0,1,0],s,h))
                  for n,s,h in [('XB12',-1.05,-B.N),('XB13',1.05,-B.N),('XS13',0,2*B.N)]]
    pitch=next(g for g in groups if g['group']=='HP')
    pitch['centre_points_mm']=[[20,-50,149],[-52,-50,149],[-52,26,149]]
    pitch['rows']=[dict(wire=n,segments=B.offsets(B.segments(pitch['centre_points_mm']),[1,0,0],s,h))
                  for n,s,h in [('XB22',-1.05,-B.N),('XB23',1.05,-B.N),('XS23',0,2*B.N)]]
    # Tail intake is a subset of the clear first straight, eliminating the
    # previous rearwards overrun. All three terminal packing frames stay fixed.
    tail=next(g for g in groups if g['group']=='TY')
    tail['centre_points_mm'][0][0]=40
    for row in tail['rows']:row['segments'][0]['start'][0]=40
    poses=[dict(native='G_AUX_CP2',old=[50,-84.75],new=[-45,-80],angle=90),
           dict(native='G_TAIL_CP2',old=[92,-84.75],new=[107,-75],angle=0)]
    ep=read(OUT/'endpoint-plan.json')
    endpoints=[e for r in ep['body_conductors'] for e in r['ends']]
    endpoints += [e for r in ep['distribution_boundary'] for e in r['resolved_datums'].values()]
    rebound={}
    for pose in poses:
        for e in endpoints:
            if e.get('native')!=pose['native']:continue
            xy=e['point_mm'][:2];local=[xy[i]-pose['old'][i] for i in (0,1)]
            a=math.radians(pose['angle']);c,s=math.cos(a),math.sin(a)
            point=[pose['new'][0]+c*local[0]-s*local[1],
                   pose['new'][1]+s*local[0]+c*local[1],e['point_mm'][2]]
            d=e['departure'];direction=[c*d[0]-s*d[1],s*d[0]+c*d[1],d[2]]
            rebound[e['role']]=dict(point_mm=point,departure=direction,
                supplier_pin_claim=False,native_mount_and_body_routes_requalification_open=True)
    assert len(rebound)==9,'All nine occupied/end roles of both5port casings must be rebound'
    rebound['G_TAIL.5']=dict(point_mm=[116.5,-65.5,99.99],departure=[0,1,0],
        status='NC_NO_WIRE',supplier_pin_claim=False,
        basis='Same provisional4.75mm pitch, whole-casing translation; not manufacturer pin datum')
    ground={g:rebound[r]['point_mm'] for g,r in [('HY','G_AUX.3'),('HP','G_AUX.4'),('TY','G_TAIL.2')]}
    signal={'HY':81.43,'HP':83.97,'TY':86.51}
    factory=[];sleeves=[];rows=[];pwm=[]
    for holder,cut in cuts.items():
        pieces=factory_path(outputs[holder],cut)
        factory.append(dict(name=holder+'_Factory',segments=pieces,OD_mm=4,
                            holder=holder,fit_blank_mm=34))
        start=B.add(cut['point_mm'],B.mul(cut['departure'],-14))
        end=B.add(cut['point_mm'],B.mul(cut['departure'],12.5))
        sleeves.append(dict(name=holder+'_Sleeve',segments=[dict(kind='line',start=start,end=end)],
                            OD_mm=6,holder=holder,clearance_budget_not_actual_recovered_tube=True))
    for group in groups:
        centre=group['centre_points_mm'][0]
        tangent=B.unit(B.sub(group['rows'][0]['segments'][0]['end'],group['rows'][0]['segments'][0]['start']))
        for core in group['rows']:
            name=core['wire'];offset=B.sub(core['segments'][0]['start'],centre)
            wide,funnel=F.convergence(centre,tangent,offset)
            end=B.sub(wide,B.mul(tangent,9))
            if name.startswith('XB') and name.endswith('2'):
                cut=cuts['F_'+group['group']]
                origin=cut['point_mm'];direction=cut['departure'];straight=material['minimum_new_wire_straight_after_cut_mm']
            elif name.startswith('XB'):
                role={'HY':'G_AUX.3','HP':'G_AUX.4','TY':'G_TAIL.2'}[group['group']]
                origin=ground[group['group']];direction=rebound[role]['departure'];straight=9
            else:
                x=signal[group['group']];origin=[x,65,105];direction=[0,0,1];straight=9
                pwm.append(dict(wire=name,points_mm=[[x,30.5,85.3702],[x,65,85.3702],origin],radius_mm=12.6))
            start=B.add(origin,B.mul(direction,straight))
            if name=='XB12':
                # Power begins west of the intake. One planned central-bay
                # traverse resolves both tangents; a single cubic cannot do so
                # with its curvature bound. Full corners are checked first.
                via_y=10
                curve=B.segments([start,[start[0],via_y,start[2]],
                    [15,via_y,end[2]],[15,end[1],end[2]],end],13)
            elif name=='XB13':
                # The low direct cross-bank traverse intersects the FHAC/ATO
                # volumes. Rise in the west bay, then traverse north of them.
                curve=B.segments([start,[-83,start[1],start[2]],
                    [-83,start[1],131],[-83,30,131],[15,30,end[2]],
                    [15,end[1],end[2]],end],13)
            elif name=='XB23':
                # A separate west lane keeps both ground approaches away from
                # holders and their access budgets, not merely above casings.
                curve=B.segments([start,[-88,start[1],start[2]],
                    [-88,0,start[2]],[-88,0,end[2]],[75,0,end[2]],
                    [75,end[1],end[2]],end],13)
            elif name=='XB22':
                curve=B.segments([start,[start[0],50,start[2]],
                    [130,50,end[2]],[130,end[1],end[2]],end],13)
            elif name=='XB32':
                curve=B.segments([start,[start[0],45,start[2]],
                    [100,45,end[2]],[100,end[1],end[2]],end],13)
            elif name=='XS23':
                # Signal climbs above the TY signal before heading south;
                # power ascends in the separate X130 bay, not through this path.
                curve=B.segments([start,[start[0],start[1],end[2]],
                    [start[0],end[1],end[2]],end],13)
            elif name=='XS33':
                # Rotate toward the central bay, not rearwards toward P0.
                # The remaining transverse span sets two exact R>=13 turns.
                before=B.add(start,[0,0,6]);c=B.add(before,[-13,0,0])
                after=B.add(c,[0,0,13])
                curve=[dict(kind='line',start=start,end=before),
                    dict(kind='arc',start=before,
                         mid=B.add(c,B.rotate(B.sub(before,c),[0,-1,0],math.pi/4)),end=after)]
                curve+=F.parallel_approach(after,[-1,0,0],end,tangent)
            else:curve=F.parallel_approach(start,direction,end,tangent)
            rows.append(dict(wire=name,group=group['group'],
                segments=[dict(kind='line',start=origin,end=start)]+curve+
                    [dict(kind='line',start=end,end=wide)]+funnel,
                core_segments=core['segments'],OD_mm=2.1,
                independent_source_grip_mm=9,source_straight_mm=straight,
                source_end_mm=origin,source_departure=direction,
                selected=False,nominal_fit_blank_mm=None))
    aux=cuts['F_AUX'];end=B.add(aux['point_mm'],B.mul(aux['departure'],21.5))
    sources=[SOURCE,BASE/'OpenPrototypePlan.FCStd',OUT/'TailLocalCurrent.FCStd',
        OUT/'source-layout-recovery-plan.json',OUT/'covered-joint-material-plan.json',
        OUT/'branch-output-plan.json',OUT/'shared-space-checks.json',OUT/'endpoint-plan.json',
        Path(__file__),Path(F.__file__),Path(S.__file__),Path(B.__file__)]
    return dict(status='LOW_FACTORY_EXITS_AND_SHARED_SOURCE_APPROACHES_NOT_SELECTED',
        rows=rows,groups=groups,factory_paths=factory,sleeves=sleeves,
        AUX_insulated_stub=dict(name='F_AUX_NewWireStub',OD_mm=2.1,
            segments=[dict(kind='line',start=aux['point_mm'],end=end)],
            unknown_U1_not_connected=True),common_PWM=pwm,
        ground_casing_frames_unchanged=False,ground_casing_poses=poses,
        all_changed_ground_port_frames=rebound,
        replacing_wire_reservations=[h+'_OutputGuide' for h in cuts],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},
        native_restraints_and_assembly_open=True,selected=False,
        stage_completed=False,physical_pass=False)


def main():
    import FreeCAD as A
    import Part
    from w5_rounded_path import rounded
    tick=time.monotonic();plan=build_plan()
    (OUT/'source-layout-plan-current.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    docs=[A.openDocument(str(p)) for p in (SOURCE,BASE/'OpenPrototypePlan.FCStd',OUT/'TailLocalCurrent.FCStd')]
    doc,ctx,tail=docs
    result=dict(status='PENDING',contacts=[],errors=[],outside_torso=[],rows=[],tested_pairs=0,
        source_sha256=plan['source_sha256'],selected=False,stage_completed=False,physical_pass=False)
    try:
        targets={}
        for o in doc.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name=='BUS_CP2' or o.Name in plan['replacing_wire_reservations']:continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith(('_CurrentReference','NominalPCB','_CP2')) or o.Name.startswith('BUSsupplier'):
                targets['mount/'+o.Name]=o.Shape
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','Head_','TailBridge')) and o.Name!='P0_MG92BMount29':targets['context/'+o.Name]=o.Shape
        targets['tail/CurrentTailSupport']=tail.CurrentTailSupport.Shape
        moved={}
        for pose in plan['ground_casing_poses']:
            shape=targets.pop('mount/'+pose['native']).copy()
            shape.rotate(A.Vector(*pose['old'],0),A.Vector(0,0,1),pose['angle'])
            shape.translate(A.Vector(pose['new'][0]-pose['old'][0],pose['new'][1]-pose['old'][1],0))
            assert shape.isValid() and not shape.check(True)
            moved[pose['native']+'_MovedCasing']=shape
        def sweep(parts,diameter):
            if isinstance(parts,Part.Wire):path=parts
            else:
                edges=[]
                for p in parts:
                    if p['kind']=='line':edge=Part.makeLine(A.Vector(*p['start']),A.Vector(*p['end']))
                    elif p['kind']=='arc':edge=Part.Arc(A.Vector(*p['start']),A.Vector(*p['mid']),A.Vector(*p['end'])).toShape()
                    else:
                        c=Part.BezierCurve();c.setPoles([A.Vector(*v) for v in p['poles']]);edge=c.toShape()
                    edges.append(edge)
                path=Part.Wire(edges)
            for a,b in zip(path.Edges,path.Edges[1:]):
                assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
                assert a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))>1-1e-6
            first=path.Edges[0]
            section=Part.Wire([Part.makeCircle(diameter/2,first.valueAt(first.FirstParameter),first.tangentAt(first.FirstParameter))])
            s=path.makePipeShell([section],True,False)
            assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            return path,s
        new={};core={}
        for row in plan['rows']:
            path,shape=sweep(row['segments'],2.1);new[row['wire']]=shape
            _,core[row['wire']]=sweep(row['core_segments'],2.1)
            result['rows'].append(dict(wire=row['wire'],fanout_length_mm=path.Length))
        for row in plan['factory_paths']+plan['sleeves']+[plan['AUX_insulated_stub']]:
            path,shape=sweep(row['segments'],row['OD_mm']);new[row['name']]=shape
            result['rows'].append(dict(wire=row['name'],length_mm=path.Length))
        for row in plan['common_PWM']:
            path=rounded(A,Part,[A.Vector(*p) for p in row['points_mm']],row['radius_mm'])
            _,shape=sweep(path,2.1);new[row['wire']+'_CommonPWM']=shape
        new.update(moved)
        # The whole HY intake changed, so it does not inherit the old core
        # clearance. HP is unchanged; TY first straight is only shortened.
        for n,s in core.items():
            if n[2] not in '12':continue
            for m,t in targets.items():
                if s.BoundBox.intersect(t.BoundBox):
                    result['tested_pairs']+=1
                    try:
                        hit=s.common(t);assert hit.isValid()
                        if hit.Volume>1e-5:result['contacts'].append(dict(a=n+'_Core',b=m,volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
                    except Exception as e:result['errors'].append(dict(a=n+'_Core',b=m,error=str(e)))
            for m,t in core.items():
                if m[2] not in '12' and s.BoundBox.intersect(t.BoundBox):
                    result['tested_pairs']+=1
                    hit=s.common(t);assert hit.isValid()
                    if hit.Volume>1e-5:result['contacts'].append(dict(a=n+'_Core',b=m+'_Core',volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            result['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid()
                hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
            except Exception as e:result['errors'].append(dict(a=n,b=m,error=str(e)))
        def intentional_joint(n,m):
            for holder,wire in [('F_HY','XB12'),('F_HP','XB22'),('F_TY','XB32'),('F_AUX','F_AUX_NewWireStub')]:
                members={holder+'_Factory',holder+'_Sleeve',wire}
                if n in members and m in members:return True
            return False
        for i,(n,s) in enumerate(new.items()):
            outside=s.cut(ctx.TorsoEnvelope.Shape);assert outside.isValid()
            if outside.Volume>1e-5:result['outside_torso'].append(dict(wire=n,volume_mm3=outside.Volume,bounds_mm=bounds(outside)))
            for m,t in targets.items():check(n,s,m,t)
            for m,t in core.items():check(n,s,m+'_Core',t)
            for m,t in list(new.items())[i+1:]:
                if not intentional_joint(n,m):check(n,s,m,t)
        result['intentional_joint_overlap_not_collision']='Only same power conductor, its factory lap and sleeve clearance budget; all other pairs tested.'
        result['status']='SHARED_SOURCE_PREFLIGHT_CLEAR_NATIVE_RESTRAINTS_OPEN' if not result['contacts'] and not result['errors'] and not result['outside_torso'] else 'SHARED_SOURCE_LAYOUT_CHANGE_REQUIRED'
    finally:
        for d in docs:A.closeDocument(d.Name)
    result.update(worker_wall_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'source-layout-checks-current.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],contacts=result['contacts'],errors=result['errors'],outside=result['outside_torso'],pairs=result['tested_pairs'],seconds=result['worker_wall_seconds'])),flush=True)


if __name__=='__main__':main()
