"""Bounded whole-network corridor allocation using actual saved obstacles.

All 49 nets are declared before routing. Reserve the three central grounds
and twelve V routes, jointly move the four DATA blocks above the crowded
lower wiring, then allocate all remaining D/G routes. Candidate ordering is
shortest first; failed candidates are counted, not exported as new parts.
PETG changes remain explicit obligations, not material collision exemptions
in a selected assembly. No route or block here is selected for manufacture.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import json, math, re, time
from w5_ground_joint_layout_r4 import ROOT
from w5_ground_bridge_plan import ports as ground_ports
from w5_leg_ground_upper_rail import layout as ground_layout
from w5_leg_fanouts_r1 import CAGE_ORDER
from w5_ground_network_plan import profile as ground_profile
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add, mul
from w5_rounded_path import corner_offsets
from servo_fuse_inputs_r1 import save, sha

OUT = ROOT/'hardware/electronics/full-cat/w5-coupled-corridors-r1'
PRINTED = {'SourceDeck','SourceCarrier','SourceCover','SourcePlatform',
           'SourceBankLeft','BankRight','SourceWestHood','SourceEastHood','FixedGuard'}


def spec(wire):
    if wire == 'W002': return dict(OD_mm=2, radius_mm=10)
    return ground_profile(wire)


def prefix(datum, wire, option='up'):
    c = CentreLine(datum['point_mm'], datum['outward_axis']); r = spec(wire)['radius_mm']
    c.line(add(c.p, mul(c.t, 6)))
    if option in ('up','down'):
        c.arc([0,0,1 if option=='up' else -1], radius=r)
    else:
        side = [-c.t[1], c.t[0], 0]
        if option == 'right': side = mul(side,-1)
        c.arc(side, radius=r); c.arc([0,0,1], radius=r)
    c.line(add(c.p, mul(c.t, 6)))
    return dict(edges=c.edges,tip=c.p,tangent=c.t,option=option)


def contract():
    graph_path = ROOT/'hardware/electronics/power-platform/wiring-p0.json'
    graph = json.loads(graph_path.read_text(encoding='utf-8'))['wires']
    raw_path = ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json'
    raw = json.loads(raw_path.read_text(encoding='utf-8'))['routes']
    gb, ge = ground_layout(); datums = ground_ports(); bodies = dict(gb)
    for e in ge: datums[e['end']] = e
    for leg in ('FL','FR','RL','RR'):
        cx = -65 if leg.startswith('F') else 115
        cy = 35 if leg.endswith('L') else -35; u = -1 if leg.startswith('F') else 1
        bodies['D_'+leg] = [cx-9.5,cy-15,175,cx+9.5,cy+15,184]
        for slot,label in enumerate(CAGE_ORDER['D_'+leg]):
            datums[f'D_{leg}.{label}'] = dict(point_mm=[cx+u*9.5,cy+(slot-2)*6.75,179.5],outward_axis=[u,0,0])
    datums['G_AUX.1'] = dict(point_mm=[110.5,-57,113.5],outward_axis=[-1,0,0])
    nodes = {w['id']:w for w in graph}
    aux_path=ROOT/'hardware/electronics/full-cat/aux-power-r1/circuit.json'
    aux=next(w for w in json.loads(aux_path.read_text(encoding='utf-8'))['feeds'] if w['id']=='XA05')
    assert {aux['from'],aux['to']}=={'P0 G2.5','G_AUX.1'}
    nodes['XA05']=dict(a='G2.5',b='G_AUX.1')
    raw_by_wire = {r['wire']:r for r in raw}
    bus_path = ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
    bus_src = json.loads(bus_path.read_text(encoding='utf-8'))['source_lead_datums']['W002']
    # Difficult finite-radius returns first, then DATA backbone, then whole looms.
    order = ['W025','W036','W062','W063','XA05','W060','W002','W007','W011','W012']
    order += [r['wire'] for r in raw if r['role'] in ('D','G')]
    assert len(order)==34 and len(set(order))==34
    rows=[]
    for wire in order:
        w=nodes[wire]
        a_end,b_end=w['a'],w['b']
        if a_end not in datums: a_end,b_end=b_end,a_end
        assert a_end in datums,(wire,a_end)
        row=dict(wire=wire,a_end=a_end,b_end=b_end,a_datum=datums[a_end],radius_mm=spec(wire)['radius_mm'])
        if b_end in datums: row['b_datum']=datums[b_end]
        elif wire=='W002': row.update(target=bus_src,lead_in=True)
        elif wire=='W060': row.update(target=[132.5,0,95],retained_MAIN_tail=True,retained_tail_radius_bound_mm=6)
        else:
            old=raw_by_wire[wire]
            row.update(target=old['waypoints_mm'][-1],retained_moving_candidate_mm=old['moving_candidate_length_mm'])
        rows.append(row)
    preserved=['W001','W003','W061']+[r['wire'] for r in raw if r['role']=='V']
    assert len(preserved)==15 and len(set(order+preserved))==49
    return bodies,rows,preserved,[graph_path,raw_path,bus_path,aux_path]


def variants(row):
    r=row['radius_mm']; upper=row['a_datum']['point_mm'][2]>160
    aa=[prefix(row['a_datum'],row['wire'],o) for o in (['up'] if upper else ['up','down','left','right'])]
    bb=[prefix(row['b_datum'],row['wire'],'up')] if 'b_datum' in row else [None]
    for a in aa:
        for b in bb:
            p=a['tip']; q=b['tip'] if b else row['target']
            candidates=[]
            for h in (202,214,226,238,250):
                if h-max(p[2],q[2])<=r+1: continue
                # Downward departures need a genuine low elbow, not a U-turn.
                exits=[None] if a['tangent'][2]>0 else [('x',-1),('x',1),('y',-1),('y',1)]
                for escape in exits:
                    lead=[p]
                    if escape:
                        low=[p[0],p[1],p[2]-r-4]; outer=list(low)
                        outer[0 if escape[0]=='x' else 1]+=escape[1]*(2*r+12)
                        lead += [low,outer]; top=[outer[0],outer[1],h]
                    else: top=[p[0],p[1],h]
                    lead.append(top); dest=[q[0],q[1],h]
                    for turn in ('direct','x-first','y-first'):
                        bridge=[] if turn=='direct' else [[dest[0],top[1],h]] if turn=='x-first' else [[top[0],dest[1],h]]
                        points=lead+bridge+[dest,q]
                        clean=[]
                        for v in points:
                            if not clean or math.dist(v,clean[-1])>1e-6:clean.append(v)
                        try:corner_offsets(clean,r)
                        except AssertionError:continue
                        recipe=dict(row,a=a,b=b,middle=clean)
                        if row.get('lead_in'):
                            # The BUS lead starts at the source and ends at the cage.
                            recipe['middle']=list(reversed(clean))
                        cost=sum(math.dist(x,y) for x,y in zip(clean,clean[1:]))
                        candidates.append((cost,recipe))
            for _,recipe in sorted(candidates,key=lambda x:x[0]):yield recipe


def main():
    import FreeCAD as A,Part
    import w5_ground_network_r1 as sweep
    from w5_ground_entries_r1 import owners,RECEIVED
    from w5_exact_separation import separated
    begin=datetime.now(timezone.utc); tic=time.monotonic()
    assert not (OUT/'checks.json').exists(); OUT.mkdir(parents=True,exist_ok=True)
    bodies,rows,preserved,pins=contract(); changed={r['wire'] for r in rows}
    fixed,source_pins=owners(A,Part,json.loads(RECEIVED.read_text(encoding='utf-8'))); pins+=source_pins
    replaced=changed|{'W001','W003','W061'}; obligations=[]
    for key in list(fixed):
        if key in {n+'_NEW_BODY' for n in bodies} or key in {n+'_design' for n in bodies} or key.startswith('R53BUS/G2shared/') or any(re.search(r'(?<![A-Za-z0-9])'+re.escape(w)+r'(?![A-Za-z0-9])',key) for w in replaced):
            obligations.append(key);del fixed[key]
    central=ROOT/'hardware/electronics/full-cat/w5-central-ground-routes-r2'
    for w in ('W001','W003'):
        p=central/(w+'_WORLD.brep');fixed[w]=Part.read(str(p));pins.append(p)
    p=ROOT/'hardware/electronics/full-cat/w5-ground-facing-plan-r1/W061_BRIDGE_WORLD.brep'
    fixed['W061']=Part.read(str(p));pins.append(p)
    printed={k:fixed.pop(k) for k in PRINTED if k in fixed}
    checks=0
    def contact(shape, skip=()):
        nonlocal checks
        for key,other in fixed.items():
            if key in skip or not shape.BoundBox.intersect(other.BoundBox):continue
            for a in shape.Solids:
                for b in other.Solids:
                    if a.BoundBox.intersect(b.BoundBox) and not separated(a,b):
                        checks+=1
                        if a.common(b).Volume>1e-6:return key
        return None
    body_hits=[];files=[]
    for name,box in bodies.items():
        shape=Part.makeBox(box[3]-box[0],box[4]-box[1],box[5]-box[2],A.Vector(*box[:3]))
        hit=contact(shape)
        if hit:body_hits.append(dict(body=name,owner=hit))
        fixed[name+'_RESERVATION']=shape
    save(OUT/'intent.json',dict(bodies=bodies,routes=rows,preserved=preserved,scope_count=49,
        body_hits=body_hits,printed_rework_owners=sorted(printed),replacement_obligations=obligations,
        native_parts_complete=False,selected=False,physical_pass=False))
    sweep.profile=spec
    accepted=[]; unresolved=[]; errors=[]
    for row in ([] if body_hits else rows):
        if time.monotonic()-tic>480:break
        rejected=Counter();attempted=0;winner=None
        for candidate in variants(row):
            if time.monotonic()-tic>480:break
            attempted+=1
            try:path,shape=sweep.from_recipe(A,Part,candidate)
            except Exception as exc:
                rejected['bend_or_sweep:'+str(exc)]+=1;continue
            # Keep one factory BUS lead; never silently turn 300mm into an extension.
            if row['wire']=='W002' and path.Length+11+30>300:
                rejected['factory300mm_budget']+=1;continue
            if row.get('retained_moving_candidate_mm') and path.Length+row['retained_moving_candidate_mm']+11+30>900:
                rejected['loom900mm_budget']+=1;continue
            try:hit=contact(shape)
            except Exception as exc:
                errors.append(dict(wire=row['wire'],error=str(exc)));break
            if hit:rejected[hit]+=1;continue
            winner=dict(candidate,body_mm=path.Length,attempted=attempted,
                native_pending=[k for k,s in printed.items() if s.BoundBox.intersect(shape.BoundBox)])
            fixed[row['wire']]=shape
            for suffix,s in [('WORLD',shape),('CENTERLINE_WORLD',path)]:
                p=OUT/(row['wire']+'_'+suffix+'.brep');s.exportBrep(str(p));files.append(p)
            accepted.append(winner);break
        if winner is None:unresolved.append(dict(wire=row['wire'],attempted=attempted,rejection_counts=dict(rejected)))
        save(OUT/'progress.json',dict(accepted=accepted,unresolved=unresolved,errors=errors,exact_pairs=checks))
        print('CORRIDOR',row['wire'],'accepted' if winner else 'UNRESOLVED',attempted,dict(rejected),flush=True)
    finish=datetime.now(timezone.utc)
    pins += [Path(__file__),RECEIVED,ROOT/'tools/electronics/w5_ground_network_r1.py',
        ROOT/'tools/electronics/w5_ground_bridge_plan.py',ROOT/'tools/electronics/w5_leg_ground_upper_rail.py',
        ROOT/'tools/electronics/w5_ground_network_plan.py',ROOT/'tools/electronics/w5_leg_fanouts_r1.py']
    save(OUT/'checks.json',dict(status='COUPLED49_CORRIDOR_PLANNING_NOT_SELECTED',bodies=bodies,body_hits=body_hits,
        accepted=accepted,unresolved=unresolved,not_attempted=[r['wire'] for r in rows if r['wire'] not in {a['wire'] for a in accepted+unresolved}],
        preserved=preserved,errors=errors,exact_pairs=checks,printed_pending=sorted(printed),
        mutual_checked_only_among_accepted=True,all_native_and_motion_open=True,selected=False,W5_complete=False,physical_pass=False,
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in files}))
    print('COUPLED_DONE',len(accepted),len(unresolved),len(body_hits),len(errors),flush=True)


if __name__=='__main__':main()
