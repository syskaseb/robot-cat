"""Receive roof R2 and check nut loading, driver reserve and staged hood lift.

Only changed roof interfaces. Lift poses are explicitly sampled, not a
continuous collision or cable-motion certification. No source re-routing.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math
from servo_fuse_inputs_r1 import save,sha
ROOT=Path(__file__).resolve().parents[2]
NATIVE=ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r3/checks.json'
OUT=ROOT/'hardware/electronics/full-cat/w5-source-roof-service-r1'

def hull(points):
    points=sorted(set(points))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower=[]
    for q in points:
        while len(lower)>=2 and cross(lower[-2],lower[-1],q)<=0:lower.pop()
        lower.append(q)
    upper=[]
    for q in reversed(points):
        while len(upper)>=2 and cross(upper[-2],upper[-1],q)<=0:upper.pop()
        upper.append(q)
    return lower[:-1]+upper[:-1]

def main():
    import FreeCAD as A,Part
    from w5_source_grips_native_r1 import current_owners
    begin=datetime.now(timezone.utc);assert not (OUT/'assembly.json').exists()
    r=json.loads(NATIVE.read_text(encoding='utf-8'))
    assert r['status']=='SOURCE_ROOF_NATIVE_STATIC_COMPLETE_SERVICE_OPEN' and not r['hits'] and not r['errors']
    assert r['closed_STLs'] and r['parameter_recompute'] and r['relocated_reopen']
    assert all(sha(ROOT/k)==v for k,v in {**r['source_sha256'],**r['files']}.items())
    owners,pins=current_owners(A,Part)
    owners.pop('SourceCover')
    folder=ROOT/'hardware/cad/studies/w5-source-roof-native-r3'
    for label,path in [('FinishedCover',folder/'Cover_WORLD.brep'),
                       ('SourceCarrier',ROOT/'hardware/cad/studies/w5-source-grips-native-r2/Carrier_WORLD.brep')]:
        owners[label]=Part.read(str(path));pins.append(path)
    for wire in ('W064','W065','W067','W068'):
        path=ROOT/f'hardware/electronics/full-cat/w5-source-grips-native-r2/{wire}_T18I_WORLD.brep'
        owners[wire+'_band']=Part.read(str(path));pins.append(path)
    hoods={}
    for label in ('WestHood','EastHood'):
        path=folder/(label+'_WORLD.brep');hoods[label]=Part.read(str(path));pins.append(path)
    OUT.mkdir(parents=True,exist_ok=True)
    hits=[];errors=[];pairs=0;checks=[]
    def check(label,s,obstacles):
        nonlocal pairs
        assert s.isValid()
        for key,t in obstacles.items():
            for a in s.Solids:
                for b in t.Solids:
                    if not a.BoundBox.intersect(b.BoundBox):continue
                    pairs+=1
                    try:
                        common=a.common(b)
                        if common.Volume>1e-5:hits.append(dict(check=label,owner=key,mm3=common.Volume))
                    except Exception as exc:errors.append(dict(check=label,owner=key,error=str(exc)))
        checks.append(label)
    for i,m in enumerate(r['mounts']):
        x,y,z,top=m['x'],m['y'],m['bearing_z'],m['pad_top_z']
        vertices=[(x+3.175*math.cos(math.pi/6+k*math.pi/3),y+3.175*math.sin(math.pi/6+k*math.pi/3)+dy)
                  for k in range(6) for dy in (0,12)]
        vv=[A.Vector(a,b,z-2.9) for a,b in hull(vertices)]
        sweep=Part.Face(Part.makePolygon(vv+[vv[0]])).extrude(A.Vector(0,0,2.4))
        check('Nut'+str(i)+'_continuous_side_load',sweep,owners)
        sweep.exportBrep(str(OUT/('Nut'+str(i)+'_LOAD_SWEEP.brep')))
        driver=Part.makeCylinder(4,35,A.Vector(x,y,top+3.5))
        check('Bolt'+str(i)+'_driver_reserve',driver,{**owners,**hoods})
        driver.exportBrep(str(OUT/('Bolt'+str(i)+'_DRIVER_ALLOWANCE.brep')))
    # Both bolts/upper washers removed from the lifted half. Other half may stay.
    for label,s in hoods.items():
        obstacles={**owners,**{k:t for k,t in hoods.items() if k!=label}}
        for dz in (0,10,30,60):
            q=s.copy();q.translate(A.Vector(0,0,dz))
            check(label+'_lift_'+str(dz),q,obstacles)
        assert s.BoundBox.ZMin+60>max(t.BoundBox.ZMax for k,t in owners.items() if k in ('FinishedCover','W064','W065','W067','W068'))
    allocations=[]
    cart=ROOT/'hardware/manufacturing/one-batch-prototype-r53/fixed-fastener-cart.json'
    rows=json.loads(cart.read_text(encoding='utf-8'))['rows']
    for sku,qty,role in [('SKL000625',4,'sourceRoof:M3x16'),('SKL000383',4,'sourceRoof:M3nut'),('SKL001158',8,'sourceRoof:M3washer')]:
        row=next(q for q in rows if q['supplier_sku']==sku)
        allocations.append(dict(role=role,quantity=qty,supplier_id=row['id'],dimensions_mm=row['dimensions_mm'],url=row['url']))
    pins.extend([Path(__file__),NATIVE,cart]);end=datetime.now(timezone.utc)
    save(OUT/'assembly.json',dict(status='SOURCE_ROOF_LOCAL_ASSEMBLY_CLEAR_UNSELECTED' if not hits and not errors else 'SOURCE_ROOF_LOCAL_ASSEMBLY_REJECTED',
        pairs=pairs,hits=hits,errors=errors,checks=checks,allocations=allocations,
        nut_loading=dict(distance_mm=12,continuous_convex_outer_hex_sweep=True,hole_filled_conservative=True),
        driver=dict(key_across_flats_mm=2.5,project_reserve_diameter_mm=8,height_mm=35,actual_tool_verified=False),
        hood_lift=dict(poses_mm=[0,10,30,60],sampled_not_continuous=True,bolts_and_upper_washers_removed=True,other_half_may_remain=True),
        assembly=['With both hoods absent slide each M3nut12mm from positive Y into its side-open post, then place the lower washer.',
                  'Complete source wiring and four insulation straps before fitting the hoods. Do not tighten PETG against excessive torque.',
                  'Fit either hood with two M3x16 and upper washers; its top faces give straight access for a2.5mm hex key.',
                  'For access remove that half\'s two bolts and upper washers, lift60mm, then place it aside. The other half may stay.',
                  'Whole Cover/Carrier/source removal still needs its separate staged sequence; this hood result does not waive that requirement.'],
        stock_rule='Four new M3x16/four nuts/eight washers and two additional prints; replace Cover once. Candidate only, no R53 stock/selection change.',
        whole_source_assembly_complete=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in dict.fromkeys(pins)},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in OUT.glob('*.brep')},
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print('SOURCE_ROOF_SERVICE',pairs,len(hits),len(errors),flush=True)

if __name__=='__main__':main()
