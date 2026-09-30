"""Move the failed loop to the outside of the head, using saved part cache.

An integral low-load wire outrigger is a candidate only until native export.
The lower cover may need a specific demonstrated cable passage, not a waiver.
"""
import json,math
from pathlib import Path
import xb11_upstream_route as R
from head_external_yaw_loop_r1 import mv
A,Part,ROOT=R.A,R.Part,R.ROOT
P=ROOT/'hardware/electronics/full-cat/head-external-yaw-loop-r1'
OUT=ROOT/'hardware/electronics/full-cat/head-external-yaw-loop-r2'
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def path(yaw):
    start=mv(Part.Vertex(A.Vector(-133,65.5,119)),yaw).Vertexes[0].Point;end=A.Vector(-90,65.5,119)
    d=end-start;u=d/d.Length;lo=.001;hi=2*math.pi-.001;length=180
    for _ in range(70):
        phi=(lo+hi)/2
        if phi/(2*math.sin(phi/2))>length/d.Length:hi=phi
        else:lo=phi
    phi=(lo+hi)/2;r=length/phi;n=A.Vector(-u.y,u.x,0)
    arc=Part.Arc(start,(start+end)/2+n*r*(1-math.cos(phi/2)),end).toShape()
    wire=Part.Wire([arc]);assert abs(wire.Length-180)<1e-5
    tube=wire.makePipeShell([Part.Wire([Part.makeCircle(2.5,start,arc.tangentAt(arc.FirstParameter))])],True,False)
    assert tube.isValid() and len(tube.Solids)==1
    return wire,tube,r
def main():
    assert not (OUT/'checks.json').exists();OUT.mkdir(exist_ok=True)
    old=read(P/'checks.json');plan=read(P/'plan.json')
    plan.update(status='SOURCE_BEFORE_OUTSIDE_HEAD_LOOP',loop_length_mm=180,plane='Horizontal XY atZ119; bow towards+Y outside the head',
      moving_anchor_rest_mm=[-133,65.5,119],fixed_anchor_mm=[-90,65.5,119],
      proposed_integral_wire_outrigger_bbox_mm=[-136,8,117,-130,63,121],
      rationale='r1 entered Fork, pitch front and Deck. r2 moves the supported moving end outside the shell; newwire arm must be checked against changed shell poses before it is selected.',
      fixed_anchor_basis='Outside+Y of fixed tie postYmax63, not cable through strap slot. Wire may require lower cover passage.',
      parent_checks_sha256=R.sha(P/'checks.json'));dump('plan.json',plan)
    def load(n):s=Part.Shape();s.read(str(P/(n+'_REST.brep')));return s
    shells={n:load(n) for n in ('FrontLeft','FrontRightPorted','Rear','Nose','EarL','EarR','CageBase','CageRetainerLeft','CageRetainerRight')}
    yawparts={n:load(n) for n in ('UpperFork','PitchRetainer','Pitch_Carrier','Pitch_ServoReference')}
    fixed={n:load(n) for n in ('CoverMountHole4','Deck','FixedDeckTie')}
    arm=R.box(plan['proposed_integral_wire_outrigger_bbox_mm']);slot=R.box([-136,58.35,118.05,-130,61.65,119.95]);arm=arm.cut(slot)
    joined=yawparts['UpperFork'].fuse(arm).removeSplitter();assert joined.isValid() and len(joined.Solids)==1
    rows=[];summ=[]
    for yaw in plan['sampled_yaw_deg']:
        p,w,r=path(yaw);w.exportBrep(str(OUT/f'loop_yaw{yaw:+}.brep'))
        summ.append(dict(yaw=yaw,radius_mm=r,length_mm=p.Length,samples=[[v.x,v.y,v.z] for v in p.Edges[0].discretize(Deflection=.1)]))
        for name,s in {**fixed,**{k:mv(v,yaw) for k,v in {**yawparts,'UpperFork':joined}.items()}}.items():
            for i,t in enumerate(s.Solids):
                if R.overlap(t.BoundBox,w.BoundBox):
                    hit=t.common(w);vol=R.volume(hit);rows.append(dict(target='loop',yaw=yaw,pitch=None,owner=name,solid=i,positive_mm3=vol,centers=[list(s.CenterOfMass) for s in hit.Solids] if vol>1e-5 else []))
        for pitch in plan['sampled_pitch_deg']:
            for name,s in shells.items():
                for target,v in [('loop',w),('new_arm_only',mv(arm,yaw))]:
                    for i,t in enumerate(mv(s,yaw,pitch).Solids):
                        if R.overlap(t.BoundBox,v.BoundBox):
                            hit=t.common(v);vol=R.volume(hit);rows.append(dict(target=target,yaw=yaw,pitch=pitch,owner=name,solid=i,positive_mm3=vol,centers=[list(t.CenterOfMass) for t in hit.Solids] if vol>1e-5 else []))
    hits=[r for r in rows if r['positive_mm3']>1e-5];joined.exportBrep(str(OUT/'UpperFork_ARM_DIAGNOSTIC.brep'))
    dump('checks.json',dict(status='REJECTED' if hits else 'SAMPLED_OUTSIDE_LOOP_CANDIDATE',source_sha256=old['source_sha256'],parent_checks_sha256=R.sha(P/'checks.json'),
      script_sha256=R.sha(Path(__file__)),plan_sha256=R.sha(OUT/'plan.json'),exact_pairs=rows,hits=hits,loop_poses=summ,new_stls=0,physical_pass=False,phase1_complete=False))
    print(json.dumps(dict(hits=hits,pairs=len(rows),radii=[s['radius_mm'] for s in summ])),flush=True)
if __name__=='__main__':main()
