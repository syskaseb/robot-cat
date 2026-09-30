"""One new S-exit and tilted slack loop; unchanged factory cable, no cuts yet."""
import math
from pathlib import Path
import head_factory_lead_storage_r1 as B
A,Part=B.A,B.Part
B.OUT=B.ROOT/'hardware/electronics/full-cat/head-factory-lead-storage-r2'
def centerline_edges():
    angle=math.acos(1-18/50);dy=25*math.sin(angle);end_y=8.8+2*dy
    def xy(cx,cy,t):return A.Vector(cx+25*math.cos(t),cy+25*math.sin(t),128.5)
    a=Part.Arc(xy(-127,8.8,math.pi),xy(-127,8.8,math.pi-angle/2),xy(-127,8.8,math.pi-angle)).toShape()
    b=Part.Arc(xy(-159,end_y,-angle),xy(-159,end_y,-angle/2),xy(-159,end_y,0)).toShape()
    def yz(cy,cz,lo,hi):
        def v(t):return A.Vector(-134,cy+22*math.cos(math.radians(t)),cz+22*math.sin(math.radians(t)))
        return Part.Arc(v(lo),v((lo+hi)/2),v(hi)).toShape()
    coil_r=math.hypot(9,22)
    edges=[a,b,Part.makeLine(A.Vector(-134,end_y,128.5),A.Vector(-134,70,128.5)),yz(70,150.5,-90,0),
      Part.makeLine(A.Vector(-134,92,150.5),A.Vector(-134,92,163)),
      Part.Arc(A.Vector(-134,92,163),A.Vector(-143,114,163+coil_r),A.Vector(-152,136,163)).toShape()]
    def v(t):return A.Vector(-152,114+22*math.cos(math.radians(t)),163+22*math.sin(math.radians(t)))
    edges += [Part.Arc(v(0),v(-45),v(-90)).toShape(),Part.makeLine(v(-90),A.Vector(-152,112,141))]
    return edges
def main():
    B.OUT.mkdir(exist_ok=True);assert not (B.OUT/'checks.json').exists()
    path=Part.Wire(centerline_edges())
    vs=[A.Vector(x,8.8,z) for x,z in [(-153.75,127.6),(-150.25,127.6),(-150.25,129.4),(-153.75,129.4),(-153.75,127.6)]]
    lead=path.makePipeShell([Part.makePolygon(vs)],True,False)
    assert lead.isValid() and len(lead.Solids)==1 and not lead.check(True)
    path.exportBrep(str(B.OUT/'FactoryLeadCenterline.brep'));lead.exportBrep(str(B.OUT/'FactoryLeadReservation.brep'))
    plan=dict(status='SOURCE_BEFORE_NEW_FULL_FACTORY_LEAD_ROUTE',profile_provisional_mm=[3.5,1.8],factory_length_mm=250,minimum_radius_mm=22,
      ownership='rigid yaw frame; S exit avoids the passive journal rather than drilling it',source_before_check=True,new_stls=0,physical_pass=False)
    B.dump('plan.json',plan)
    rows=[];pins={}
    def check(n,p,s,pose):
        pins[p.relative_to(B.ROOT).as_posix()]=B.R.sha(p)
        for i,t in enumerate(s.Solids):
            if B.R.overlap(t.BoundBox,lead.BoundBox):
                q=t.common(lead);volume=B.R.volume(q)
                rows.append(dict(owner=n,solid=i,pose=pose,hit_mm3=volume,witness_centers=[list(v.CenterOfMass) for v in q.Solids] if volume>1e-5 else []))
    for n,p in {'Fork':B.J/'ForkJRHolder.brep','Carrier':B.J/'PitchCarrierThroughLeadExit.brep','Retainer':B.C/'PitchRetainer_REST.brep','Servo':B.C/'Pitch_ServoReference_REST.brep'}.items():check(n,p,B.load(p),'same yaw frame')
    for pitch in (-10,0,5):
        for n,p in {'FrontRight':B.P/'FrontRightWirePassage.brep',**{n:B.C/(n+'_REST.brep') for n in ('FrontLeft','Rear','Nose','EarL','EarR','CageBase','CageRetainerLeft','CageRetainerRight')}}.items():check(n,p,B.mv(B.load(p),0,pitch),dict(pitch=pitch))
    for yaw in (-15,0,15):
        for n,p in [('Cover',B.P/'CoverHeadWirePassage.brep'),('Deck',B.C/'Deck_REST.brep')]:check(n,p,B.mv(B.load(p),-yaw),dict(yaw=yaw))
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    B.dump('checks.json',dict(status='REJECTED' if hits else 'FULL_FACTORY_ROUTE_CANDIDATE',length_mm=path.Length,nominal_residual_mm=250-path.Length,
      source_sha256=pins,script_sha256=B.R.sha(Path(__file__)),rows=rows,hits=hits,new_stls=0,physical_pass=False,
      profile_provisional=True,phase1_complete=False,remaining=['Shown collisions if any','Actual exit profile/length','Retain slack without strain','Custom end transitions and yaw feed']))
    print(__import__('json').dumps(dict(length_mm=path.Length,hits=hits)),flush=True)
if __name__=='__main__':main()
