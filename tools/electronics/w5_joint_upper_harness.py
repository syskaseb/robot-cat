"""Check one complete45-conductor body scope before native support changes.

Twenty-one ground paths plus the retained24 D/V candidate paths, all four
new upper ground reservations, and the preserved source/bank/other harness.
Printed parts are explicit pending native interfaces, never a claimed PASS.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,re,math
from servo_fuse_inputs_r1 import save,sha
from w5_ground_upper_routes import ROOT,recipes
from w5_ground_network_plan import profile

OUT=ROOT/'hardware/electronics/full-cat/w5-joint-upper-harness-r1'

def main():
    import FreeCAD as A,Part
    from w5_ground_network_r1 import from_recipe
    from w5_ground_entries_r1 import owners,RECEIVED
    from w5_exact_separation import separated
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    fixed,pins=owners(A,Part,json.loads(RECEIVED.read_text(encoding='utf-8')))
    upper=ROOT/'hardware/electronics/full-cat/w5-leg-ground-upper-rail-r1'
    upper_receipt=json.loads((upper/'checks.json').read_text(encoding='utf-8'))
    assert not upper_receipt['hits'] and not upper_receipt['errors']
    for name in upper_receipt['bodies']:
        del fixed[name+'_NEW_BODY'];p=upper/(name+'_BODY_WORLD.brep');fixed[name+'_UPPER_BODY']=Part.read(str(p));pins.append(p)
    built={};lengths=[];files=[];errors=[];roles={}
    for row in recipes():
        key=row['wire']
        try:
            path,shape=from_recipe(A,Part,row);built[key]=shape;roles[key]='G'
            for suffix,s in [('WORLD',shape),('CENTERLINE_WORLD',path)]:
                p=OUT/(key+'_'+suffix+'.brep');s.exportBrep(str(p));files.append(p)
            strip=19 if key=='W001' else 17 if key=='W060' else 25 if key in ('W025','W036') else 22 if key in ('W062','W063','XA05') else 11
            moving=row.get('retained_moving_candidate_mm',0);nominal=path.Length+moving+strip;reserve=10 if key=='W001' else 30
            lengths.append(dict(wire=key,body_mm=path.Length,moving_candidate_mm=moving,nominal_mm=nominal,
                trial_blank_mm=math.ceil((nominal+reserve)/10)*10,
                fits_limit=nominal<=150 if key=='W001' else nominal+reserve<=300 if key=='W003' else nominal+reserve<=900 if moving else None))
            print('JOINT_BUILT',key,round(nominal,2),flush=True)
        except Exception as exc:errors.append(dict(wire=key,stage='build',error=str(exc)))
    p=ROOT/'hardware/electronics/full-cat/w5-ground-facing-plan-r1/W061_BRIDGE_WORLD.brep'
    built['W061']=Part.read(str(p));roles['W061']='G';pins.append(p)
    lengths.append(dict(wire='W061',body_mm=24.5,nominal_mm=49.5,trial_blank_mm=80))
    folder=ROOT/'hardware/electronics/full-cat/w5-leg-joint-source-layout-r1'
    receipt=json.loads((folder/'checks.json').read_text(encoding='utf-8'))
    shapes=Part.read(str(folder/'FANOUTS_WORLD.brep')).childShapes()
    assert len(shapes)==len(receipt['routes'])==36
    for row,shape in zip(receipt['routes'],shapes):
        if row['role'] in ('D','V'):built[row['wire']]=shape;roles[row['wire']]=row['role']
    pins.extend((folder/'checks.json',folder/'FANOUTS_WORLD.brep',upper/'checks.json'))
    obligations=[]
    for key in list(fixed):
        if key.startswith(('ReceivedD/','ReceivedV/','R53BUS/G2shared/')) or any(re.search(r'(?<![A-Za-z0-9])'+re.escape(w)+r'(?![A-Za-z0-9])',key) for w in built):
            obligations.append(key);del fixed[key]
    printed={'SourceDeck','SourceCarrier','SourceCover','SourcePlatform','SourceBankLeft','BankRight','SourceWestHood','SourceEastHood'}
    hits=[];native=[];pairs=0
    for i,(key,shape) in enumerate(built.items()):
        for owner,other in [*fixed.items(),*list(built.items())[:i]]:
            if not shape.BoundBox.intersect(other.BoundBox):continue
            if owner in printed:
                native.append(dict(wire=key,owner=owner,bounds_overlap_only=True));continue
            try:
                vol=0
                for a in shape.Solids:
                    for b in other.Solids:
                        if a.BoundBox.intersect(b.BoundBox) and not separated(a,b):
                            pairs+=1;vol+=a.common(b).Volume
                if vol>1e-6:hits.append(dict(wire=key,role=roles[key],owner=owner,volume_mm3=vol))
            except Exception as exc:errors.append(dict(wire=key,owner=owner,stage='common',error=str(exc)))
        save(OUT/'progress.json',dict(checked=i+1,total=len(built),hits=hits,errors=errors,pairs=pairs))
        print('JOINT_CHECKED',key,len(hits),len(errors),flush=True)
    finish=datetime.now(timezone.utc)
    pins.extend([Path(__file__),RECEIVED,*[ROOT/'tools/electronics'/name for name in ('w5_ground_upper_routes.py','w5_ground_bridge_plan.py','w5_central_ground_routes_r2.py','w5_central_ground_routes.py','w5_leg_ground_upper_rail.py','w5_ground_network_plan.py','w5_ground_network_r1.py')]])
    save(OUT/'checks.json',dict(status='JOINT45_ROUTING_CANDIDATE_NOT_SELECTED',required_conductors=45,built_conductors=len(built),roles=roles,
        lengths=lengths,hits=hits,errors=errors,pairs=pairs,native_interfaces_pending=native,replacement_obligations=obligations,
        upper_return_max_centre_Z=233,existing_hood_top_Z=226.5,hood_height_change_pending=True,
        full_moving_qualification=False,native_supports_complete=False,stock_selected=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},files={p.relative_to(ROOT).as_posix():sha(p) for p in files},
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds()))
    print('JOINT_COMPLETE',len(built),len(hits),len(errors),flush=True)

if __name__=='__main__':main()
