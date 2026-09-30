"""One full uncut factory-lead reservation, including the external slack loop.

Uses a provisional flat section, not a claimed measurement of MG92B wiring.
Does not silently waive a shell or bearing collision.
"""
import json,math
from pathlib import Path
import xb11_upstream_route as R
from head_external_yaw_loop_r1 import mv
A,Part,ROOT=R.A,R.Part,R.ROOT
C=ROOT/'hardware/electronics/full-cat/head-external-yaw-loop-r1'
P=ROOT/'hardware/cad/studies/head-external-wire-support-r1'
J=ROOT/'hardware/cad/studies/head-jr-support-r2'
OUT=ROOT/'hardware/electronics/full-cat/head-factory-lead-storage-r1'
def load(p):s=Part.Shape();s.read(str(p));return s
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def pt(y,z):return A.Vector(-152,y,z)
def arc(cy,cz,lo,hi):
    def v(a):return pt(cy+25*math.cos(math.radians(a)),cz+25*math.sin(math.radians(a)))
    return Part.Arc(v(lo),v((lo+hi)/2),v(hi)).toShape()
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    plan=dict(status='SOURCE_BEFORE_FACTORY_LEAD_STORAGE',owner='same rigid yaw frame as pitch servo and JR holder',
      factory_wire_length_mm=250,profile_mm=[3.5,1.8],profile_basis='provisional flat3-wire section, not actual manufacturer wire/exit dimensions',
      bend_radius_mm=25,service='Do not cut factory lead. Loose external loop away from pitch shell, not through journal. Actual factory exit/pinout and residual slack verified after delivery.',
      new_stls=0,physical_pass=False,phase1_complete=False)
    dump('plan.json',plan)
    edges=[Part.makeLine(pt(8.8,128.5),pt(68,128.5)),arc(68,153.5,-90,0),
      Part.makeLine(pt(93,153.5),pt(93,166)),arc(118,166,180,0),arc(118,166,0,-90),Part.makeLine(pt(118,141),pt(112,141))]
    path=Part.Wire(edges)
    vs=[A.Vector(x,8.8,z) for x,z in [(-153.75,127.6),(-150.25,127.6),(-150.25,129.4),(-153.75,129.4),(-153.75,127.6)]]
    lead=path.makePipeShell([Part.makePolygon(vs)],True,False)
    assert lead.isValid() and len(lead.Solids)==1 and not lead.check(True)
    path.exportBrep(str(OUT/'FactoryLeadCenterline.brep'));lead.exportBrep(str(OUT/'FactoryLeadReservation.brep'))
    rows=[];pins={}
    yawparts={'Fork':J/'ForkJRHolder.brep','Carrier':J/'PitchCarrierThroughLeadExit.brep',
      'Retainer':C/'PitchRetainer_REST.brep','Servo':C/'Pitch_ServoReference_REST.brep'}
    shells={'FrontRight':P/'FrontRightWirePassage.brep',**{n:C/(n+'_REST.brep') for n in ('FrontLeft','Rear','Nose','EarL','EarR','CageBase','CageRetainerLeft','CageRetainerRight')}}
    def check(name,file,shape,pose):
        pins[file.relative_to(ROOT).as_posix()]=R.sha(file)
        for i,s in enumerate(shape.Solids):
            if R.overlap(s.BoundBox,lead.BoundBox):
                hit=s.common(lead);v=R.volume(hit)
                rows.append(dict(owner=name,solid=i,pose=pose,hit_mm3=v,witness_centers=[list(t.CenterOfMass) for t in hit.Solids] if v>1e-5 else []))
    for n,p in yawparts.items():check(n,p,load(p),'same yaw frame')
    for pitch in (-10,0,5):
        for n,p in shells.items():check(n,p,mv(load(p),0,pitch),dict(pitch=pitch))
    # Transform fixed obstacles into the moving yaw frame, avoiding duplicate lead construction.
    for yaw in (-15,0,15):
        for n,p in [('Cover',P/'CoverHeadWirePassage.brep'),('Deck',C/'Deck_REST.brep')]:check(n,p,mv(load(p),-yaw),dict(yaw=yaw))
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    dump('checks.json',dict(status='REJECTED' if hits else 'FACTORY_LEAD_RESERVATION_CANDIDATE',length_mm=path.Length,
      nominal_length_budget_mm=250-path.Length,minimum_bend_mm=25,profile_provisional=True,source_sha256=pins,
      script_sha256=R.sha(Path(__file__)),rows=rows,hits=hits,new_stls=0,physical_pass=False,phase1_complete=False,
      open=['Actual exit and wire profile','Factory length measurement and internal exit allowance','Loop retention and guarding','Complete custom side transition and fixed yaw feed']))
    print(json.dumps(dict(length_mm=path.Length,hits=hits)),flush=True)
if __name__=='__main__':main()
