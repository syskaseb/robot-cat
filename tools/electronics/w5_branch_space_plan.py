"""Allocate all leg departures together before rerouting crossing flights.

Reservations are planning volumes, not selected wires or collision evidence.
Actual material intersections qualify each departure against retained solids.
Reopen only accepted routes intersecting the jointly chosen reservations.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, re, time, math
import w5_coupled_corridors_r3 as prior
from servo_fuse_inputs_r1 import save, sha

ROOT=prior.base.ROOT
OUT=ROOT/'hardware/electronics/full-cat/w5-branch-space-plan-r1'
RECEIPT=ROOT/'hardware/electronics/full-cat/w5-coupled-corridors-r3/checks.json'


def main():
    import FreeCAD as A, Part
    from w5_ground_entries_r1 import owners, RECEIVED
    from w5_exact_separation import separated
    start=datetime.now(timezone.utc);tic=time.monotonic()
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    bodies,rows,preserved,pins=prior.contract()
    legs=[r for r in rows if 'retained_moving_candidate_mm' in r]
    assert len(legs)==24
    fixed,pp=owners(A,Part,json.loads(RECEIVED.read_text(encoding='utf-8')));pins+=pp
    changed={r['wire'] for r in rows}|{'W001','W003','W061'}
    obligations=[]
    for k in list(fixed):
        if k in {n+'_NEW_BODY' for n in bodies}|{n+'_design' for n in bodies} or k.startswith('R53BUS/G2shared/') or any(re.search(r'(?<![A-Za-z0-9])'+w+r'(?![A-Za-z0-9])',k) for w in changed):
            obligations.append(k);del fixed[k]
    printed={k:fixed.pop(k) for k in prior.base.PRINTED if k in fixed}
    for w in ('W001','W003'):
        p=ROOT/f'hardware/electronics/full-cat/w5-central-ground-routes-r2/{w}_WORLD.brep'
        fixed[w]=Part.read(str(p));pins.append(p)
    p=ROOT/'hardware/electronics/full-cat/w5-ground-facing-plan-r1/W061_BRIDGE_WORLD.brep'
    fixed['W061']=Part.read(str(p));pins.append(p)
    for n,b in bodies.items():fixed[n+'_BODY']=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    previous=json.loads(RECEIPT.read_text(encoding='utf-8'))
    accepted={}
    for r in previous['accepted']:
        p=RECEIPT.parent/(r['wire']+'_WORLD.brep');accepted[r['wire']]=Part.read(str(p));pins.append(p)
    pairs=0
    def touch(a,b):
        nonlocal pairs
        if not a.BoundBox.intersect(b.BoundBox):return False
        for x in a.Solids:
            for y in b.Solids:
                if x.BoundBox.intersect(y.BoundBox) and not separated(x,y):
                    pairs+=1
                    if x.common(y).Volume>1e-6:return True
        return False
    def solid(pre,w):
        bits=[]
        for e in pre['edges']:
            edge=Part.makeLine(A.Vector(*e['start']),A.Vector(*e['end'])) if e['kind']=='line' else Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
            section=Part.Wire([Part.makeCircle(prior.base.spec(w)['OD_mm']/2,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])
            bits.append(Part.Wire([edge]).makePipeShell([section],True,False))
        return Part.makeCompound(bits)
    options={};rejected={};errors=[]
    for row in legs:
        w=row['wire'];options[w]=[];rejected[w]=[]
        for mode in ('up','left','right'):
            pre=prior.base.prefix(row['a_datum'],w,mode)
            s=solid(pre,w)
            hits=[k for k,b in fixed.items() if touch(s,b)]
            if hits:rejected[w].append(dict(option=mode,material_contacts=hits));continue
            # Same straight departure envelope through all allowed flight heights.
            # This reserves space; it does not invent a physical 250mm wire.
            p=pre['tip'];height=250-p[2]
            assert height>0 and math.dist(pre['tangent'],[0,0,1])<1e-8
            tube=Part.makeCylinder(prior.base.spec(w)['OD_mm']/2,height,A.Vector(*p))
            reservation=Part.makeCompound([s,tube])
            blockers=[k for k,b in fixed.items() if touch(tube,b)]
            if blockers:rejected[w].append(dict(option=mode,reservation_obstacles=blockers));continue
            reopen=[k for k,b in accepted.items() if k!=w and touch(reservation,b)]
            options[w].append((dict(prefix=pre,reopen=reopen,flight_reservation_top_mm=250),reservation))
        options[w].sort(key=lambda v:(len(v[0]['reopen']),v[0]['prefix']['option']!='up'))
        print('DEPARTURE',w,len(options[w]),flush=True)
        save(OUT/'progress.json',dict(completed=list(options),rejected=rejected))
    missing=[w for w,v in options.items() if not v]
    chosen={};nodes=0;bound=False
    order=sorted(options,key=lambda w:len(options[w]))
    def joint(i):
        nonlocal nodes,bound
        nodes+=1
        if nodes>4096 or time.monotonic()-tic>480:bound=True;return False
        if i==len(order):return True
        w=order[i]
        for q,s in options[w]:
            if any(touch(s,t) for _,t in chosen.values()):continue
            chosen[w]=(q,s)
            if joint(i+1):return True
            del chosen[w]
        return False
    success=not missing and joint(0)
    reopened=sorted({k for q,s in chosen.values() for k in q['reopen']}) if success else []
    files=[]
    if success:
        for w,(q,s) in chosen.items():
            p=OUT/(w+'_RESERVATION.brep');s.exportBrep(str(p));files.append(p)
    finish=datetime.now(timezone.utc)
    pins += [Path(__file__),Path(prior.__file__),Path(prior.base.__file__),RECEIPT,RECEIVED]
    save(OUT/'checks.json',dict(status='JOINT_BRANCH_SPACE_PLAN_NOT_SELECTED',success=success,
        declared_total_network_count=49,leg_departure_count=24,choices={w:q for w,(q,s) in chosen.items()} if success else {},
        unresolved_departures=missing,rejected=rejected,reopen_accepted_routes=reopened,
        retained_accepted_routes=sorted(set(accepted)-set(reopened)) if success else [],
        reservation_obstacles_are_not_material_collision_claims=True,search_nodes=nodes,search_bound_reached=bound,
        exact_pairs=pairs,errors=errors,replacement_obligations=obligations,printed_pending=sorted(printed),
        selected=False,full_routes_complete=False,native_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in files}))
    print('BRANCH_PLAN_DONE',success,missing,reopened,flush=True)


if __name__=='__main__':main()
