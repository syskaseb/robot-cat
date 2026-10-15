"""Check unchanged source straights once, before repeating body-root searches."""
import json,time
import check_near_axis_hip_sources as C
P=C.P

if __name__=='__main__':
    tick=time.monotonic();plan=json.loads((P.OUT/'body-axial-hip-plan.json').read_text())
    family=json.loads((P.OUT/'leg-source-near-member-plan.json').read_text())
    axes=json.loads((P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    bounds=C.ImmutableBounds();rows=[]
    for row in plan['hips']:
        segments=[('moving_land',row['moving_lands'][0]['parts']),('factory_straight',row['source_parts'])]
        for other in family['routes']:
            if other['loom']==row['loom'] or other['source']['cad_code']!=row['cad_code']:continue
            old=P.wire(C.B.parts_for_loom(family,other['loom'],0,0,axes)+C.B.moved_parts(other['source_parts'],other['source'],0,0,axes))
            for kind,parts in segments:
                new=P.wire(parts)
                if not bounds.near(new,old,6.25):continue
                gap,points,_=new.distToShape(old)
                witness=dict(loom=row['loom'],segment=kind,other=other['loom'],gap_mm=gap,required_mm=6.25,
                    violates=gap<6.25-1e-6,nearest_world_mm=[[list(a),list(b)] for a,b in points[:1]])
                rows.append(witness);print(json.dumps(witness),flush=True)
    result=dict(status='AXIAL_NOMINAL_INVARIANT_CORRIDOR_WITNESSES_ONLY',rows=rows,worker_seconds=round(time.monotonic()-tick,3),
        scope='Four unchanged moving9mm/factory9mm straights vs other two sameleg sourcefamilies at rest; not wholewire or physical approval.',selected=False,physical_pass=False)
    (P.OUT/'axial-invariant-corridors.json').write_text(json.dumps(result,indent=2)+'\n')
