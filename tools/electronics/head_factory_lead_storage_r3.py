"""Componentwise conservative sweep of the saved S route, no compound-zero waiver."""
import json,math
from pathlib import Path
import head_factory_lead_storage_r1 as B
from head_factory_lead_storage_r2 import centerline_edges
A,Part=B.A,B.Part
OUT=B.ROOT/'hardware/electronics/full-cat/head-factory-lead-storage-r3'
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    edges=centerline_edges();path=Part.Wire(edges);path.exportBrep(str(OUT/'FactoryLeadCenterline.brep'))
    radius=math.hypot(3.5/2,1.8/2)
    dump('plan.json',dict(status='SOURCE_BEFORE_COMPONENT_SWEEPS',profile_provisional_mm=[3.5,1.8],
      circular_envelope_radius_mm=radius,basis='circumscribed circle contains every orientation of the provisional flat profile; not actual round wire or a new minimum bending rule',
      centerline_min_radius_mm=22,factory_length_mm=250,new_stls=0,physical_pass=False,
      previous_operation='Full flat-profile multi-plane sweep interrupted after extended CPU work without result; no collision PASS inferred.'))
    tubes=[]
    for i,e in enumerate(edges):
        print(f'Build component {i}',flush=True)
        start=e.Vertexes[0].Point
        # Parameter start is authoritative for reversed edges.
        start=e.valueAt(e.FirstParameter);tangent=e.tangentAt(e.FirstParameter)
        t=Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(radius,start,tangent)])],True,False)
        assert t.isValid() and len(t.Solids)==1 and not t.check(True)
        t.exportBrep(str(OUT/f'LeadEnvelope{i}.brep'));tubes.append(t)
    Part.makeCompound(tubes).exportBrep(str(OUT/'LeadEnvelopes_DISPLAY_ONLY.brep'))
    rows=[];pins={}
    def check(n,p,shape,pose):
        pins[p.relative_to(B.ROOT).as_posix()]=B.R.sha(p)
        for i,s in enumerate(shape.Solids):
            for j,t in enumerate(tubes):
                if B.R.overlap(s.BoundBox,t.BoundBox):
                    hit=s.common(t);v=B.R.volume(hit)
                    rows.append(dict(owner=n,solid=i,segment=j,pose=pose,hit_mm3=v,
                      witness_centers=[list(v.CenterOfMass) for v in hit.Solids] if v>1e-5 else []))
    for n,p in {'Fork':B.J/'ForkJRHolder.brep','Carrier':B.J/'PitchCarrierThroughLeadExit.brep','Retainer':B.C/'PitchRetainer_REST.brep','Servo':B.C/'Pitch_ServoReference_REST.brep'}.items():check(n,p,B.load(p),'same yaw frame')
    for pitch in (-10,0,5):
        for n,p in {'FrontRight':B.P/'FrontRightWirePassage.brep',**{n:B.C/(n+'_REST.brep') for n in ('FrontLeft','Rear','Nose','EarL','EarR','CageBase','CageRetainerLeft','CageRetainerRight')}}.items():check(n,p,B.mv(B.load(p),0,pitch),dict(pitch=pitch))
    for yaw in (-15,0,15):
        for n,p in [('Cover',B.P/'CoverHeadWirePassage.brep'),('Deck',B.C/'Deck_REST.brep')]:check(n,p,B.mv(B.load(p),-yaw),dict(yaw=yaw))
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    dump('checks.json',dict(status='CONSERVATIVE_HITS_REQUIRE_LOCAL_RESOLUTION' if hits else 'FACTORY_LEAD_RESERVATION_CANDIDATE',
      centerline_length_mm=path.Length,nominal_residual_mm=250-path.Length,source_sha256=pins,script_sha256=B.R.sha(Path(__file__)),
      exact_component_rows=rows,hits=hits,new_stls=0,physical_pass=False,phase1_complete=False,
      remaining=['Resolve affected conservative hits without treating them as actual cable collisions','Actual exit/profile/length','Slack restraint and both custom loop end transitions','Fixed yaw feed']))
    print(json.dumps(dict(length_mm=path.Length,hits=hits)),flush=True)
if __name__=='__main__':main()
