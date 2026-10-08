"""Shared three-wire trunks: exact circular offsets with transported packing.

These are route reservations, NOT finished source fanouts or manufactured parts.
Retain the accepted input/output fixtures; never rebuild the old rejected feeds.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import sys
import time
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds

sys.path.insert(0, str(ROOT/'tools/electronics'))
from w5_rounded_path import corner_offsets

OUT = BASE/'wiring-checkpoint'
SOURCE = OUT/'OutputReliefsAssembly.FCStd'
RADIUS = 15.1
N = 1.05/math.sqrt(3)


def add(a,b): return [x+y for x,y in zip(a,b)]
def sub(a,b): return [x-y for x,y in zip(a,b)]
def mul(a,k): return [x*k for x in a]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def unit(a): return mul(a,1/math.sqrt(dot(a,a)))


def rotate(v,axis,angle):
    """Rodrigues; no Frenet flip at a straight/arc junction."""
    c,s=math.cos(angle),math.sin(angle)
    return add(add(mul(v,c),mul(cross(axis,v),s)),mul(axis,dot(axis,v)*(1-c)))


def segments(points,radius=RADIUS):
    cuts,tangents=corner_offsets(points,radius)
    result=[];current=points[0]
    for i,p in enumerate(points[1:-1],1):
        u,v=tangents[i-1:i+1]
        if cuts[i]<1e-8: continue
        before=sub(p,mul(u,cuts[i]));after=add(p,mul(v,cuts[i]))
        axis=unit(cross(u,v));angle=math.acos(max(-1,min(1,dot(u,v))))
        center=add(before,mul(unit(sub(v,mul(u,dot(u,v)))),radius))
        mid=add(center,rotate(sub(before,center),axis,angle/2))
        result.append(dict(kind='line',start=current,end=before,t0=u,t1=u))
        result.append(dict(kind='arc',start=before,mid=mid,end=after,
                           t0=u,t1=v,axis=axis,angle=angle))
        current=after
    result.append(dict(kind='line',start=current,end=points[-1],t0=tangents[-1],t1=tangents[-1]))
    return result


def offsets(parts,end_side,side,normal):
    """Preserve the required terminal packing; transport backwards, then forwards."""
    b=end_side[:]
    for e in reversed(parts):
        if e['kind']=='arc': b=rotate(b,e['axis'],-e['angle'])
    result=[]
    for e in parts:
        def point(p,t,frame):
            return add(p,add(mul(frame,side),mul(cross(frame,t),normal)))
        assert abs(dot(b,e['t0']))<1e-8
        row=dict(kind=e['kind'],start=point(e['start'],e['t0'],b))
        if e['kind']=='arc':
            halfway=rotate(b,e['axis'],e['angle']/2)
            row['mid']=point(e['mid'],rotate(e['t0'],e['axis'],e['angle']/2),halfway)
            b=rotate(b,e['axis'],e['angle'])
        row['end']=point(e['end'],e['t1'],b)
        result.append(row)
    assert math.dist(b,end_side)<1e-8
    return result


def build_plan():
    specs=[('HY',[[-8,-10,178],[-8,20,178],[-76,20,178],[-76,-56.8,178],[-76,-56.8,85.2],[-112,-56.8,85.2]],
            [0,1,0],[('XB12',-1.05,-N),('XB13',1.05,-N),('XS13',0,2*N)]),
           ('HP',[[20,0,186],[-52,0,186],[-52,0,149],[-52,26,149]],
            [1,0,0],[('XB22',-1.05,-N),('XB23',1.05,-N),('XS23',0,2*N)]),
           ('TY',[[120,10,194],[32,10,194],[32,-45,194],[32,-45,118],[68,-45,118]],
            [0,1,0],[('XB32',0,2*N),('XB33',1.05,-N),('XS33',-1.05,-N)])]
    groups=[]
    for name,points,b,packing in specs:
        cuts,_=corner_offsets(points,RADIUS);parts=segments(points)
        assert math.dist(points[0],points[1])-cuts[1]>=9
        assert math.dist(points[-2],points[-1])-cuts[-2]>=9
        rows=[dict(wire=n,side_mm=s,normal_mm=h,segments=offsets(parts,b,s,h)) for n,s,h in packing]
        groups.append(dict(group=name,centre_points_mm=points,centre_segments=parts,rows=rows,
                           first_free_mm=math.dist(points[0],points[1])-cuts[1],
                           last_free_mm=math.dist(points[-2],points[-1])-cuts[-2]))
    files=[SOURCE,OUT/'TailLocalCurrent.FCStd',BASE/'OpenPrototypePlan.FCStd',
           OUT/'local-boundary-plan.json',Path(__file__),ROOT/'tools/electronics/w5_rounded_path.py']
    return dict(status='THREE_SHARED_TRUNK_RESERVATIONS_NOT_COMPLETE_FEEDS',groups=groups,
        wire_OD_mm=2.1,centre_radius_mm=RADIUS,
        guaranteed_individual_radius_lower_bound_mm=RADIUS-2*N,
        required_fixed_radius_mm=12.6,bundle_outer_radius_mm=1.05+2*N,
        exact_transported_triangular_packing=True,
        current_fixture_shapes_unchanged=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files},
        open_interfaces=['All nine actual source fanouts and covered factory joins',
            'Common PWM outlet after carrier lip Y29; no guessed U1 map',
            'New fixed pitch anchor Y86/Z166 and moving loop to retained fork',
            'Raised tail insulation station and local continuations, not point-only approval',
            'Two WAGO footprints/occupied port frames if fanouts need the proposed rotations',
            'Independent trunk restraints, whole body/legs/source920mm and stock'],
        selected=False,stage_completed=False,physical_pass=False,new_printed_parts=0)


def main():
    import FreeCAD as A
    import Part
    tick=time.monotonic();plan=build_plan()
    (OUT/'bundle-spines-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    if '--plan-only' in sys.argv:
        print(json.dumps(dict(groups=3,rows=9,status=plan['status'])));return
    docs=[A.openDocument(str(p)) for p in (SOURCE,BASE/'OpenPrototypePlan.FCStd',OUT/'TailLocalCurrent.FCStd')]
    doc,ctx,tail=docs
    result=dict(status='PENDING',contacts=[],errors=[],tested_pairs=0,wire_rows=[],
                source_sha256=plan['source_sha256'],selected=False,stage_completed=False,physical_pass=False)
    try:
        targets={}
        for o in doc.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name=='BUS_CP2':continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith(('_CurrentReference','NominalPCB','_CP2')) or o.Name.startswith('BUSsupplier'):
                targets['mount/'+o.Name]=o.Shape
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','Head_','TailBridge')) and o.Name!='P0_MG92BMount29':
                targets['context/'+o.Name]=o.Shape
        targets['tail/CurrentTailSupport']=tail.CurrentTailSupport.Shape
        pipes={};paths={}
        for group in plan['groups']:
            for row in group['rows']:
                edges=[]
                for e in row['segments']:
                    p,q=A.Vector(*e['start']),A.Vector(*e['end'])
                    edge=Part.makeLine(p,q) if e['kind']=='line' else Part.Arc(p,A.Vector(*e['mid']),q).toShape()
                    if e['kind']=='arc':assert edge.Curve.Radius>=12.6-1e-7
                    edges.append(edge)
                for a,b in zip(edges,edges[1:]):
                    assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
                    assert a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))>1-1e-7
                path=Part.Wire(edges);first=edges[0]
                profile=Part.Wire([Part.makeCircle(1.05,first.valueAt(first.FirstParameter),first.tangentAt(first.FirstParameter))])
                shape=path.makePipeShell([profile],True,False)
                assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
                pipes[row['wire']]=shape;paths[row['wire']]=path
                result['wire_rows'].append(dict(wire=row['wire'],group=group['group'],trunk_length_mm=path.Length,
                    start_mm=row['segments'][0]['start'],end_mm=row['segments'][-1]['end'],
                    smallest_actual_arc_radius_mm=min(e.Curve.Radius for e in edges if isinstance(e.Curve,Part.Circle))))
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            result['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid(),'Invalid BRep cannot establish clearance'
                hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
            except Exception as exc:result['errors'].append(dict(a=n,b=m,error=str(exc)))
        for i,(n,s) in enumerate(pipes.items()):
            for m,t in targets.items():check(n,s,m,t)
            for m,t in list(pipes.items())[i+1:]:check(n,s,m,t)
        result['same_bundle_minimum_separation_mm']=[]
        for group in plan['groups']:
            names=[r['wire'] for r in group['rows']]
            for i,n in enumerate(names):
                for m in names[i+1:]:
                    distance=paths[n].distToShape(paths[m])[0]
                    assert distance>=2.1-1e-6,(n,m,distance)
                    result['same_bundle_minimum_separation_mm'].append(dict(a=n,b=m,minimum_mm=distance))
        clear=not result['contacts'] and not result['errors']
        result['status']='SHARED_TRUNKS_STATICALLY_CLEAR_SOURCE_FANOUTS_AND_MOUNTS_OPEN' if clear else 'SHARED_TRUNKS_CHANGE_REQUIRED'
        if clear:
            for n,s in pipes.items():
                o=doc.addObject('Part::Feature',n+'_SharedTrunkReservation');o.Shape=s
                o.addProperty('App::PropertyString','Qualification');o.Qualification='Exact fixed trunk only; fanouts, restraints, moving loop and native mount changes OPEN'
            doc.saveAs(str(OUT/'BundleSpinesPreflight.FCStd'))
            result['preview_sha256']=sha(OUT/'BundleSpinesPreflight.FCStd')
        result['route_reference_not_native_printed_part']=True
    finally:
        for d in docs:A.closeDocument(d.Name)
    result.update(worker_wall_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'bundle-spines-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
