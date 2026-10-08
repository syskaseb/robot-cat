"""Shared PWM outlet, covered power joins and coordinated three-wire funnels.

Cubic source approaches are chosen by a curvature gate BEFORE FreeCAD. Every
curvature stationary point is checked, not only a sampled picture of a spline.
No new padmap, connector, mount or whole-stage acceptance is implied.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import time
import numpy as np
from numpy.polynomial import polynomial as P

import open_prototype_shared_space as S
import open_prototype_bundle_spines as B
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds

OUT=BASE/'wiring-checkpoint'
SOURCE=OUT/'LocalStationsAssembly.FCStd'


def curvature_gate(poles):
    a=np.asarray(poles,dtype=float)
    d=np.array([3*(a[1]-a[0]),6*(a[2]-2*a[1]+a[0]),
                3*(a[3]-3*a[2]+3*a[1]-a[0])])
    dd=np.array([d[1],2*d[2]])
    def norm2(cols):
        result=np.zeros(1)
        for c in cols:result=P.polyadd(result,P.polymul(c,c))
        return result
    speed=norm2(d.T)
    cross=[]
    for i,j in ((1,2),(2,0),(0,1)):
        cross.append(P.polysub(P.polymul(d[:,i],dd[:,j]),P.polymul(d[:,j],dd[:,i])))
    numerator=norm2(cross)
    stationary=P.polysub(P.polymul(P.polyder(numerator),speed),
                        3*P.polymul(numerator,P.polyder(speed)))
    def roots(poly):
        poly=np.trim_zeros(poly,'b')
        if len(poly)<2:return []
        return [float(t.real) for t in P.polyroots(poly)
                if abs(t.imag)<1e-7 and 0<t.real<1]
    speed_ts=[0.,1.]+roots(P.polyder(speed))
    if min(P.polyval(t,speed) for t in speed_ts)<1e-8:return None
    ts=[0.,1.]+roots(stationary)
    maximum=max(max(0.,P.polyval(t,numerator))/P.polyval(t,speed)**3 for t in ts)
    return dict(minimum_radius_mm=1/math.sqrt(maximum) if maximum>1e-20 else None,
                curvature_stationary_parameters=ts,method='Polynomial stationary roots plus endpoints; numerical1e-7 real-root tolerance, no physical claim')


def approach(start,t0,end,t1):
    candidates=[]
    for a in (12.6,18.,25.,35.,50.,65.):
        for b in (12.6,18.,25.,35.,50.,65.):
            poles=[start,B.add(start,B.mul(t0,a)),B.sub(end,B.mul(t1,b)),end]
            # A sufficient planning bound, NOT a contact test of the loft.
            if any(not(-120<=p[0]<=205 and -98<=p[1]<=98 and 75<=p[2]<=155.5) for p in poles):continue
            gate=curvature_gate(poles)
            if gate and (gate['minimum_radius_mm'] is None or gate['minimum_radius_mm']>=13):
                candidates.append((a+b,dict(kind='bezier',poles=poles,curvature=gate)))
    if not candidates:raise ValueError(('No curvature-qualified source approach',start,end))
    return [min(candidates,key=lambda c:c[0])[1]]


def parallel_approach(start,t0,end,t1):
    """Closed-form arcs for parallel/opposite outlet directions; no fit loop."""
    alignment=B.dot(t0,t1)
    if abs(alignment)<1-1e-8:return approach(start,t0,end,t1)
    delta=B.sub(end,start);along=B.dot(delta,t0)
    transverse=B.sub(delta,B.mul(t0,along));distance=math.sqrt(B.dot(transverse,transverse))
    if distance<1e-8 and alignment>0 and along>0:
        return [dict(kind='line',start=start,end=end)]
    u=B.unit(transverse)
    def half(a,t,r):
        c=B.add(a,B.mul(u,r));b=B.add(a,B.mul(u,2*r))
        axis=B.unit(B.cross(t,u))
        mid=B.add(c,B.mul(t,r))
        return dict(kind='arc',start=a,mid=mid,end=b),b
    if alignment<0:
        radius=distance/2
        if radius<13:return approach(start,t0,end,t1)
        first=max(0,along)+9
        a=B.add(start,B.mul(t0,first));arc,b=half(a,t0,radius)
        return [dict(kind='line',start=start,end=a),arc,dict(kind='line',start=b,end=end)]
    if along<0:
        # Two half-turns and one straight traverse. The complete transverse
        # distance sets BOTH radii, not per-wire scalar offset searches.
        radius=distance/4
        if radius<13:return approach(start,t0,end,t1)
        a1,b1=half(start,t0,radius)
        a2start=B.add(b1,B.mul(t0,along));a2,b2=half(a2start,B.mul(t0,-1),radius)
        assert math.dist(b2,end)<1e-7
        return [a1,dict(kind='line',start=b1,end=a2start),a2]
    if distance<1e-8:return [dict(kind='line',start=start,end=end)]
    radius=(along*along+distance*distance)/(4*distance)
    if radius<13:return approach(start,t0,end,t1)
    angle=2*math.atan(distance/along);axis=B.unit(B.cross(t0,u))
    c0=B.add(start,B.mul(u,radius))
    turn=B.add(c0,B.rotate(B.sub(start,c0),axis,angle))
    mid0=B.add(c0,B.rotate(B.sub(start,c0),axis,angle/2))
    c1=B.sub(turn,B.mul(B.rotate(u,axis,angle),radius))
    mid1=B.add(c1,B.rotate(B.sub(turn,c1),B.mul(axis,-1),angle/2))
    b=B.add(c1,B.rotate(B.sub(turn,c1),B.mul(axis,-1),angle))
    assert math.dist(b,end)<1e-7
    return [dict(kind='arc',start=start,mid=mid0,end=turn),dict(kind='arc',start=turn,mid=mid1,end=b)]


def convergence(centre,tangent,offset):
    """Two opposite exact arcs shrink a shared triangular section3:1."""
    front=B.sub(centre,B.mul(tangent,29))
    start=B.add(front,B.mul(offset,3))
    magnitude=math.sqrt(B.dot(offset,offset));u=B.unit(offset)
    shift=2*magnitude;length=20.
    r=(length*length+shift*shift)/(4*shift)
    angle=2*math.atan(shift/length)
    axis=B.unit(B.cross(tangent,B.mul(u,-1)))
    c0=B.sub(start,B.mul(u,r))
    mid0=B.add(c0,B.rotate(B.sub(start,c0),axis,angle/2))
    turn=B.add(c0,B.rotate(B.sub(start,c0),axis,angle))
    c1=B.add(turn,B.mul(B.rotate(u,axis,angle),r))
    mid1=B.add(c1,B.rotate(B.sub(turn,c1),B.mul(axis,-1),angle/2))
    end=B.add(c1,B.rotate(B.sub(turn,c1),B.mul(axis,-1),angle))
    expected=B.add(B.sub(centre,B.mul(tangent,9)),offset)
    assert math.dist(end,expected)<1e-7
    return start,[dict(kind='arc',start=start,mid=mid0,end=turn),
                  dict(kind='arc',start=turn,mid=mid1,end=end),
                  dict(kind='line',start=end,end=B.add(centre,offset))]


def build_plan():
    old=read(OUT/'shared-space-checks.json')
    assert not old['contacts'] and not old['errors']
    plan=S.build_plan()
    outputs={r['holder']:r for r in read(OUT/'branch-output-plan.json')['output_recipes']}
    groups=plan['groups']
    hy=next(g for g in groups if g['group']=='HY')
    # The old +Y mouth required a tight reversal from F_HY's +X cut end.
    # Reorient the whole unselected HY mouth to-X, not individual wire nudges.
    hy['centre_points_mm']=[[50,-15,134],[-76,-15,134],[-76,-56.8,134],
                           [-76,-56.8,85.2],[-112,-56.8,85.2]]
    parts=B.segments(hy['centre_points_mm'])
    packing=[('XB12',-1.05,-B.N),('XB13',1.05,-B.N),('XS13',0,2*B.N)]
    hy['rows']=[dict(wire=n,segments=B.offsets(parts,[0,1,0],s,h)) for n,s,h in packing]
    hp=next(g for g in groups if g['group']=='HP')
    # Trim40+6mm from the previously clear FIRST straight, no moving of the
    # turn/end/support. A subset cannot add contacts; first free is10.9mm.
    hp['centre_points_mm'][0][0]=-26
    for row in hp['rows']:row['segments'][0]['start'][0]=-26
    hp['first_free_mm']=10.9
    rows=[]
    ground={'HY':([67.5,-84.75,99.99],[1,0,0]),
            'HP':([67.5,-89.5,99.99],[1,0,0]),
            'TY':([101.5,-80,99.99],[1,0,0])}
    signal_x={'HY':81.43,'HP':83.97,'TY':86.51}
    pwm_common=[]
    for group in groups:
        centre=group['centre_points_mm'][0]
        tangent=B.unit(B.sub(group['rows'][0]['segments'][0]['end'],group['rows'][0]['segments'][0]['start']))
        for row in group['rows']:
            name=row['wire'];offset=B.sub(row['segments'][0]['start'],centre)
            wide,funnel=convergence(centre,tangent,offset)
            end=B.sub(wide,B.mul(tangent,9))
            if name.startswith('XB') and name.endswith('2'):
                output=outputs['F_'+group['group']]
                origin=output['end_mm'];direction=output['end_departure']
                # Sleeve ends6mm past factory cut. Independent9mm insulation
                # grip starts there. Factory lap8mm, intact factory cover6mm.
                start=B.add(origin,B.mul(direction,15))
                prefix=[dict(kind='line',start=origin,end=start)]
                basis='Known holder factory cut; lap8/sleeve20 and last6mm intact cover are project recipe, delivered copper/strength/heat-shrink SKU OPEN'
            elif name.startswith('XB'):
                origin,direction=ground[group['group']]
                start=B.add(origin,B.mul(direction,9))
                prefix=[dict(kind='line',start=origin,end=start)]
                basis='Rigid rotation of entire same WAGO casing/port frame; new underside footprints/retention not built'
            else:
                x=signal_x[group['group']];origin=[x,65,105];direction=[0,0,1]
                start=B.add(origin,[0,0,9])
                prefix=[dict(kind='line',start=origin,end=start)]
                source=[[x,30.5,85.3702],[x,65,85.3702],[x,65,105]]
                pwm_common.append(dict(wire=name,points_mm=source,centre_radius_mm=12.6,
                    known_copper_landing={'HY':'B1.out','HP':'B2.out','TY':'B3.out'}[group['group']],
                    pad_to_insulation_covered_transition_and_carrier_relief_open=True))
                basis='Known1608 net, not U1 padmap; common parallel3wire outlet precedes branches'
            if name=='XS33':
                # Exact R13 quarter-turn followed by two space-defined arcs:
                # avoid a single cubic with zero net climb and a+Z tangent.
                before=B.add(start,[0,0,7]);centre=B.add(before,[13,0,0])
                after=B.add(centre,[0,0,13])
                quarter=dict(kind='arc',start=before,
                    mid=B.add(centre,B.rotate(B.sub(before,centre),[0,1,0],math.pi/4)),end=after)
                via=[150,45,start[2]]
                curve=[dict(kind='line',start=start,end=before),quarter]
                curve+=parallel_approach(after,[1,0,0],via,[1,0,0])
                curve+=parallel_approach(via,[1,0,0],end,tangent)
            else:curve=parallel_approach(start,direction,end,tangent)
            pieces=prefix+curve+[dict(kind='line',start=end,end=wide)]+funnel
            rows.append(dict(wire=name,group=group['group'],segments=pieces,
                core_segments=row['segments'],source_basis=basis,
                independent_insulation_grip_mm=9,final_wide_spacing_mm=6.3,
                material_OD_mm=2.1,required_fixed_radius_mm=12.6,
                bare_factory_lap_mm=8 if name.endswith('2') else 0,
                whole_route_qualified=False,nominal_fit_blank_mm=None))
    inputs=(SOURCE,OUT/'shared-space-checks.json',OUT/'branch-output-plan.json',
            OUT/'endpoint-plan.json',OUT/'TailLocalCurrent.FCStd',BASE/'OpenPrototypePlan.FCStd',
            Path(__file__),Path(S.__file__),Path(B.__file__))
    return dict(status='NINE_SOURCE_APPROACHES_COMMON_PWM_AND_CONVERGENCE_PLAN',rows=rows,
        common_PWM_outlet=pwm_common,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in inputs},
        WAGO_rotations_proposed=[dict(native='G_AUX_CP2',old=[50,-84.75],new=[58,-84.75],angle=-90),
                                dict(native='G_TAIL_CP2',old=[92,-84.75],new=[92,-84.75],angle=-90)],
        other18_WAGO_retained=True,trimmed_HP_core_first_line_is_same_path_subset=True,
        HY_mouth_direction_changed_together_not_inherited_clearance=True,
        source_grips_sleeve_SKU_PWM_carrier_relief_and_rotated_WAGO_native_OPEN=True,
        unknown_U1_not_connected=True,selected=False,stage_completed=False,physical_pass=False)


def main():
    import FreeCAD as A
    import Part
    from w5_rounded_path import rounded
    tick=time.monotonic();plan=build_plan()
    (OUT/'source-fanouts-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    docs=[A.openDocument(str(p)) for p in (SOURCE,BASE/'OpenPrototypePlan.FCStd',OUT/'TailLocalCurrent.FCStd')]
    doc,ctx,tail=docs
    result=dict(status='PENDING',contacts=[],errors=[],outside_torso=[],rows=[],tested_pairs=0,
        source_sha256=plan['source_sha256'],selected=False,stage_completed=False,physical_pass=False)
    try:
        targets={}
        for o in doc.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name=='BUS_CP2':continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith(('_CurrentReference','NominalPCB','_CP2')) or o.Name.startswith('BUSsupplier'):
                targets['mount/'+o.Name]=o.Shape
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','Head_','TailBridge')) and o.Name!='P0_MG92BMount29':targets['context/'+o.Name]=o.Shape
        targets['tail/CurrentTailSupport']=tail.CurrentTailSupport.Shape
        for r in plan['WAGO_rotations_proposed']:
            s=targets['mount/'+r['native']].copy()
            s.rotate(A.Vector(*r['old'],0),A.Vector(0,0,1),r['angle'])
            s.translate(A.Vector(r['new'][0]-r['old'][0],r['new'][1]-r['old'][1],0))
            targets['mount/'+r['native']]=s
        def edges(parts):
            result=[]
            for e in parts:
                if e['kind']=='line':edge=Part.makeLine(A.Vector(*e['start']),A.Vector(*e['end']))
                elif e['kind']=='arc':edge=Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
                else:
                    curve=Part.BezierCurve();curve.setPoles([A.Vector(*p) for p in e['poles']]);edge=curve.toShape()
                result.append(edge)
            return result
        def sweep(parts):
            if isinstance(parts,Part.Wire):path=parts
            else:path=Part.Wire(edges(parts))
            for a,b in zip(path.Edges,path.Edges[1:]):
                assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
                assert a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))>1-1e-6
            first=path.Edges[0];section=Part.Wire([Part.makeCircle(1.05,first.valueAt(first.FirstParameter),first.tangentAt(first.FirstParameter))])
            s=path.makePipeShell([section],True,False)
            assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            return path,s
        core={};new={}
        for row in plan['rows']:
            path,shape=sweep(row['core_segments']);core[row['wire']]=shape
            path,shape=sweep(row['segments']);new[row['wire']]=shape
            out=shape.cut(ctx.TorsoEnvelope.Shape);assert out.isValid()
            if out.Volume>1e-5:result['outside_torso'].append(dict(wire=row['wire'],volume_mm3=out.Volume,bounds_mm=bounds(out)))
            result['rows'].append(dict(wire=row['wire'],fanout_length_mm=path.Length,
                minimum_source_Bezier_radius_mm=min([e['curvature']['minimum_radius_mm'] for e in row['segments'] if e['kind']=='bezier'],default=None)))
        for r in plan['common_PWM_outlet']:
            path=rounded(A,Part,[A.Vector(*p) for p in r['points_mm']],12.6)
            _,shape=sweep(path);new[r['wire']+'_CommonPWM']=shape
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            result['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid()
                hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
            except Exception as e:result['errors'].append(dict(a=n,b=m,error=str(e)))
        for i,(n,s) in enumerate(new.items()):
            for m,t in targets.items():check(n,s,m,t)
            for m,t in core.items():check(n,s,m+'_Core',t)
            for m,t in list(new.items())[i+1:]:check(n,s,m,t)
        # HY new mouth is not covered by the previous core clearance report.
        for n,s in core.items():
            if n[2]!='1':continue
            for m,t in targets.items():check(n+'_Core',s,m,t)
            for m,t in core.items():
                if m[2]!='1':check(n+'_Core',s,m+'_Core',t)
        result['status']='SOURCE_APPROACH_PREFLIGHT_CLEAR_NATIVE_RESTRAINTS_OPEN' if not result['contacts'] and not result['errors'] and not result['outside_torso'] else 'SOURCE_APPROACH_COMMON_LAYOUT_CHANGE_REQUIRED'
    finally:
        for d in docs:A.closeDocument(d.Name)
    result.update(worker_wall_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'source-fanouts-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],contacts=result['contacts'],errors=result['errors'],
        outside_torso=result['outside_torso'],rows=result['rows'],pairs=result['tested_pairs'],
        seconds=result['worker_wall_seconds'])),flush=True)


if __name__=='__main__':main()
