"""One whole pitch feed: JR exit, tangent-clamped yaw loop, fixed transition.

Save the proposed interfaces before geometry. Separate segment solids avoid
the demonstrated Compound Boolean false-zero. Nothing is selected on a hit.
"""
import json, math
from pathlib import Path
import xb11_upstream_route as R
from head_external_yaw_loop_r1 import mv
A, Part, ROOT = R.A, R.Part, R.ROOT
OUT = ROOT/'hardware/electronics/full-cat/head-complete-yaw-transitions-r1'
CACHE = ROOT/'hardware/electronics/full-cat/head-external-yaw-loop-r1'
CAD = ROOT/'hardware/cad/studies/head-jr-support-r5'
PORTS = ROOT/'hardware/cad/studies/head-external-wire-support-r1'
END_X, END_Y, MOVING_Y, FLEX_LENGTH = -50, 124, 90, 230

def dump(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')

def load(p):
    s=Part.Shape(); s.read(str(p)); return s

def vec(p): return A.Vector(*p)
def xyz(p): return [p.x,p.y,p.z]

def arc(center, start, end):
    c,s,e=map(vec,(center,start,end)); r=(s-c).Length
    assert abs((e-c).Length-r)<1e-7
    middle=c+((s-c)+(e-c)).normalize()*r
    return Part.Arc(s,middle,e).toShape()

def moving_edges():
    # JR front insulation station, rigidly moves with yaw, not pitch.
    return [arc([-164.6,76,141],[-152,76,141],[-164.6,63.4,141]),
            arc([-164.6,76,141],[-164.6,63.4,141],[-177.2,76,141]),
            Part.makeLine(vec([-177.2,76,141]),vec([-177.2,MOVING_Y,141]))]

def fixed_edges():
    # Two 45degree bends preserve the loop's -Y tangent at both ends.
    r=12.6; q=math.sqrt(.5); dz=17; straight=(dz-2*r*(1-q))/q
    p0=vec([END_X,124,141]); p1=p0+vec([0,-r*q,-r*(1-q)])
    p2=p1+vec([0,-straight*q,-straight*q])
    p3=p2+vec([0,-r*q,-r*(1-q)])
    return ([Part.makeLine(vec([END_X,END_Y,141]),p0)] if END_Y!=124 else [])+[arc(xyz(p0+vec([0,0,-r])),xyz(p0),xyz(p1)),
            Part.makeLine(p1,p2),
            arc(xyz(p3+vec([0,0,r])),xyz(p2),xyz(p3)),
            Part.makeLine(p3,vec([END_X,76,124]))]

def flex(yaw, length=230, end_x=-50):
    start=mv(Part.Vertex(vec([-177.2,MOVING_Y,141])),yaw).Vertexes[0].Point
    direction=vec([0,1,0]); direction=A.Rotation(vec([0,0,1]),yaw).multVec(direction)
    end=vec([end_x,END_Y,141])
    def curve(a,b):
        c=Part.BezierCurve(); c.setPoles([start,start+direction*a,end+vec([0,b,0]),end]); return c.toShape()
    candidates=[]
    for a in range(20,181,4):
        lo,hi=1.,300.
        if not curve(a,lo).Length<length<curve(a,hi).Length: continue
        for _ in range(32):
            mid=(lo+hi)/2
            if curve(a,mid).Length>length: hi=mid
            else: lo=mid
        edge=curve(a,(lo+hi)/2)
        k=max(edge.curvatureAt(i/100) for i in range(101))
        candidates.append((1/k,edge))
    assert candidates
    _,edge=max(candidates,key=lambda x:x[0])
    radii=[1/edge.curvatureAt(edge.FirstParameter+(edge.LastParameter-edge.FirstParameter)*i/500)
           for i in range(501)]
    return edge,min(radii),xyz(start),xyz(direction)

def tube(edge):
    p=Part.Wire([edge]); t=edge.tangentAt(edge.FirstParameter)
    s=p.makePipeShell([Part.Wire([Part.makeCircle(2.5,edge.valueAt(edge.FirstParameter),t)])],True,False)
    assert s.isValid() and len(s.Solids)==1
    return s

def main():
    OUT.mkdir(exist_ok=True); assert not (OUT/'checks.json').exists()
    plan=dict(status='SOURCE_BEFORE_FULL_END_TRANSITIONS',new_stls=0,
        wires=['XB22 F_HP.out -> C_HP.V+ HELU23302 0.5mm2 OD2.1 AUX6V/F_HP1A',
               'XB23 G_AUX.4 -> C_HP.GND HELU23301 0.5mm2 OD2.1 power return',
               'XS23 U1/R2.2 -> C_HP.PWM provisional silicone26AWG0.12mm2 OD1.25'],
        bundle_OD_mm=5, fixed_radius_mm=12.6, moving_min_radius_mm=31.5,
        moving_anchor_rest_mm=[-177.2,MOVING_Y,141], fixed_anchor_mm=[END_X,END_Y,141],
        flexible_length_mm=FLEX_LENGTH, rigid_moving_start_mm=[-152,76,141],
        rationale='Replace incomplete180mm arc with a constant-length clamped-tangent loop. Both complete end transitions included; anchors must be constructed only after the full changed route clears.',
        JR='R22 provisional mating pair; retained factory250mm and independent insulation stationY76',
        physical_pass=False, selected=False, phase1_complete=False,
        scope='Changed whole pitch feed geometry, sampled poses. Fixed yaw-servo feed still separate; no old repeated matrix.')
    dump('plan.json',plan)
    shapes={n:load(CACHE/(n+'_REST.brep')) for n in ('FrontLeft','Rear','Nose','EarL','EarR','CageBase','CageRetainerLeft','CageRetainerRight','PitchRetainer','Pitch_ServoReference','Deck','FixedDeckTie')}
    shapes.update(Fork=load(CAD/'ForkJRHolder.brep'),Carrier=load(CAD/'PitchCarrierThroughLeadExit.brep'),
                  FrontRight=load(PORTS/'FrontRightWirePassage.brep'),Cover=load(PORTS/'CoverHeadWirePassage.brep'))
    recovery=OUT/'partial-rows.json'
    rows=json.loads(recovery.read_text())['rows'] if recovery.exists() else []
    completed={(x['yaw'],x['segment']) for x in rows}
    poses=[]
    for yaw in (-15,0,15):
        e,r,start,direction=flex(yaw,FLEX_LENGTH,END_X); moving=moving_edges()
        edges=[('rigid_moving'+str(i),mv(x,yaw)) for i,x in enumerate(moving)]
        edges += [('flexible'+str(i),e.Curve.toShape(i/8,(i+1)/8)) for i in range(8)]
        edges += [('rigid_fixed'+str(i),x) for i,x in enumerate(fixed_edges())]
        # Check explicit tangent continuity across the yaw boundary.
        ta=edges[2][1].tangentAt(edges[2][1].LastParameter); tb=e.tangentAt(e.FirstParameter)
        tc=e.tangentAt(e.LastParameter); fixed_first=fixed_edges()[0]; td=fixed_first.tangentAt(fixed_first.FirstParameter)
        assert ta.dot(tb)>1-1e-7 and tc.dot(td)>1-1e-7
        poses.append(dict(yaw=yaw,length_mm=e.Length,min_sampled_radius_mm=r,start=start,
                          moving_tangent=direction,end_tangent=xyz(tc),tangent_continuity=True,
                          flexible_samples=[xyz(p) for p in e.discretize(Number=150)]))
        for name,edge in edges:
            if (yaw,name) in completed: continue
            dump('partial-rows.json',dict(poses=poses,rows=rows,next_segment=name,yaw=yaw))
            s=tube(edge); s.exportBrep(str(OUT/f'{name}_yaw{yaw:+}.brep'))
            dump('progress.json',dict(yaw=yaw,segment=name,rows=len(rows)))
            for owner,base in shapes.items():
                shell=owner in ('FrontLeft','FrontRight','Rear','Nose','EarL','EarR','CageBase','CageRetainerLeft','CageRetainerRight')
                for pitch in ((-10,0,5) if shell else (0,)):
                    obstacle=mv(base,yaw,pitch) if shell else (mv(base,yaw) if owner in ('Fork','Carrier','PitchRetainer','Pitch_ServoReference') else base)
                    for i,solid in enumerate(obstacle.Solids):
                        separated=not R.overlap(s.BoundBox,solid.BoundBox)
                        v=0 if separated else R.volume(s.common(solid))
                        rows.append(dict(yaw=yaw,pitch=pitch,segment=name,owner=owner,solid=i,
                                         bounded_bbox=separated,hit_mm3=v))
            dump('partial-rows.json',dict(poses=poses,rows=rows,completed_segment=name,yaw=yaw))
    hits=[x for x in rows if x['hit_mm3']>1e-5]
    radius_ok=min(x['min_sampled_radius_mm'] for x in poses)>=31.5
    inputs=globals().get('INPUTS',list(CACHE.glob('*_REST.brep'))+[CAD/'ForkJRHolder.brep',CAD/'PitchCarrierThroughLeadExit.brep',PORTS/'FrontRightWirePassage.brep',PORTS/'CoverHeadWirePassage.brep'])
    dump('checks.json',dict(status='REJECTED' if hits or not radius_ok else 'FULL_END_TRANSITIONS_GEOMETRY_CANDIDATE',
        poses=poses,rows=rows,hits=hits,moving_radius_sample_bound_met=radius_ok,
        rigid_moving_length_mm=sum(x.Length for x in moving_edges()),rigid_fixed_length_mm=sum(x.Length for x in fixed_edges()),
        input_sha256={p.relative_to(ROOT).as_posix():R.sha(p) for p in inputs},script_sha256=R.sha(Path(__file__)),
        anchors_complete=False,new_stls=0,physical_pass=False,phase1_complete=False))
    print(json.dumps(dict(hits=hits,min_radii=[x['min_sampled_radius_mm'] for x in poses],pairs=len(rows))),flush=True)
if __name__=='__main__': main()
