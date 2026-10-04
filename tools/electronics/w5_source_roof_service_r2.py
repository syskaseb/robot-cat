"""Qualify the changed outboard curtain removal; inherit R1 nut/tool access."""
from pathlib import Path
from datetime import datetime,timezone
import json
from servo_fuse_inputs_r1 import save,sha
ROOT=Path(__file__).resolve().parents[2]
NATIVE=ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r5/checks.json'
PRIOR=ROOT/'hardware/electronics/full-cat/w5-source-roof-service-r1/assembly.json'
OUT=ROOT/'hardware/electronics/full-cat/w5-source-roof-service-r2'

def main():
    import FreeCAD as A,Part
    from w5_source_grips_native_r1 import current_owners
    begin=datetime.now(timezone.utc);assert not (OUT/'assembly.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    r=json.loads(NATIVE.read_text(encoding='utf-8'));prior=json.loads(PRIOR.read_text(encoding='utf-8'))
    assert r['closed_STLs'] and r['relocated_reopen'] and not r['hits'] and not r['errors']
    assert not prior['hits'] and not prior['errors']
    for record in (r,prior):assert all(sha(ROOT/k)==v for k,v in {**record['source_sha256'],**record['files']}.items())
    owners,pins=current_owners(A,Part);owners.pop('SourceCover')
    folder=ROOT/'hardware/cad/studies/w5-source-roof-native-r5'
    for label,path in [('FinishedCover',folder/'Cover_WORLD.brep'),('WestHood',folder/'WestHood_WORLD.brep'),
                       ('SourceCarrier',ROOT/'hardware/cad/studies/w5-source-grips-native-r2/Carrier_WORLD.brep')]:
        owners[label]=Part.read(str(path));pins.append(path)
    for wire in ('W064','W065','W067','W068'):
        path=ROOT/f'hardware/electronics/full-cat/w5-source-grips-native-r2/{wire}_T18I_WORLD.brep'
        owners[wire+'_band']=Part.read(str(path));pins.append(path)
    path=folder/'EastHood_WORLD.brep';east=Part.read(str(path));pins.append(path)
    pairs=0;hits=[];errors=[]
    for dz in (0,40,100,160):
        s=east.copy();s.translate(A.Vector(0,0,dz))
        for name,t in owners.items():
            for a in s.Solids:
                for b in t.Solids:
                    if not a.BoundBox.intersect(b.BoundBox):continue
                    pairs+=1
                    try:
                        common=a.common(b)
                        if common.Volume>1e-5:hits.append(dict(lift_mm=dz,owner=name,mm3=common.Volume))
                    except Exception as exc:errors.append(dict(lift_mm=dz,owner=name,error=str(exc)))
    assert east.BoundBox.ZMin+160>max(owners[k].BoundBox.ZMax for k in ('FinishedCover','W064','W065','W067','W068'))
    # Added material lies atX191.6..194,Z62..185.5. All four loading/driver
    # reserves are atX-72 or44.5 with half-width <=4: their unchanged proofs
    # cannot gain an intersection with this addition. West lift also disjointX.
    assert r['outer_east_curtain']['X_mm']==[191.6,194]
    assert all(m['x']+4<191.6 for m in r['mounts'])
    end=datetime.now(timezone.utc);pins.extend([Path(__file__),NATIVE,PRIOR])
    save(OUT/'assembly.json',dict(status='SOURCE_ROOF_LOCAL_ASSEMBLY_CLEAR_UNSELECTED' if not hits and not errors else 'SOURCE_CURTAIN_LIFT_REJECTED',
        pairs=pairs,hits=hits,errors=errors,east_lift_poses_mm=[0,40,100,160],sampled_not_continuous=True,
        inherited_nut_driver_and_west_access=PRIOR.relative_to(ROOT).as_posix(),inheritance_reason='Added curtain material disjoint inX from all inherited tooling and west half; source/axes unchanged.',
        assembly=prior['assembly'][:3]+['For east-side access remove its two bolts/upper washers, lift160mm and place aside. West half may stay. West-only access retains60mm sampled lift.',prior['assembly'][-1]],
        allocations=prior['allocations'],stock_rule=prior['stock_rule'],
        whole_source_assembly_complete=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in dict.fromkeys(pins)},
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print('SOURCE_CURTAIN_SERVICE',pairs,len(hits),len(errors),flush=True)

if __name__=='__main__':main()
