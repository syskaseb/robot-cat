"""Allocate BOTH central blocks, bridge and eight departures as one family.

Bounded deterministic placement search, not successive manual wire nudges.
Actual saved obstacle intersections decide occupancy; bounding boxes only
prune pairs. Keep all22 unaffected accepted routes from the coupled proof.
Purchased block envelopes and cage registration remain provisional. Native
mounts, full routes and motion are NOT qualified by this planning result.
"""
from datetime import datetime,timezone
from pathlib import Path
from itertools import product
import json,math,re,time
from w5_coupled_corridors import ROOT,PRINTED,prefix,spec
from w5_coupled_corridors_r3 import contract
from w5_ground_bridge_plan import ports
from servo_fuse_inputs_r1 import save,sha

OUT=ROOT/'hardware/electronics/full-cat/w5-central-space-solver-r1'
ENDS={'W001':'G1.1','W025':'G1.3','W036':'G1.4','W060':'G1.2',
      'W003':'G2.4','W062':'G2.2','W063':'G2.3','XA05':'G2.5'}


def placements(targets):
    result=[];datum=ports()
    for x,y,z,gap in product(range(-70,71,20),range(-65,116,20),(109,129,149),(70,90)):
        gx=x+gap
        if gx+9.5>140:continue
        shift={'G1':[x-66,y-5.5,z-109],'G2':[gx-111,y-5.5,z-109]}
        points={w:[p+d for p,d in zip(datum[e]['point_mm'],shift[e.split('.')[0]])] for w,e in ENDS.items()}
        if math.dist(points['W001'],targets['W001'])+19>150:continue
        if math.dist(points['W003'],targets['W003'])+41>300:continue
        cost=sum(math.dist(points[w],targets[w]) for w in ENDS)
        result.append(dict(g1_centre=[x,y],g2_centre=[gx,y],floor=z,shift=shift,
            lower_bound_cost_mm=cost,bridge_mm=gx-9.5-(x+11)))
    return sorted(result,key=lambda p:(p['lower_bound_cost_mm'],p['floor'],p['g1_centre']))


def main():
    import FreeCAD as A,Part
    from w5_ground_entries_r1 import owners,RECEIVED
    from w5_exact_separation import separated
    begin=datetime.now(timezone.utc);tic=time.monotonic()
    assert not (OUT/'checks.json').exists();OUT.mkdir(parents=True,exist_ok=True)
    bodies,rows,preserved,pins=contract();changed={r['wire'] for r in rows}|{'W001','W003','W061'}
    fixed,oldpins=owners(A,Part,json.loads(RECEIVED.read_text(encoding='utf-8')));pins+=oldpins
    obligations=[]
    for k in list(fixed):
        if k in {'G1_NEW_BODY','G2_NEW_BODY'} or k in {n+'_NEW_BODY' for n in bodies} or k in {n+'_design' for n in bodies} or k.startswith('R53BUS/G2shared/') or any(re.search(r'(?<![A-Za-z0-9])'+re.escape(w)+r'(?![A-Za-z0-9])',k) for w in changed):
            obligations.append(k);del fixed[k]
    for name,b in bodies.items():fixed[name+'_CURRENT_RESERVATION']=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    received=ROOT/'hardware/electronics/full-cat/w5-coupled-corridors-r3/checks.json'
    proof=json.loads(received.read_text(encoding='utf-8'));assert not proof['body_hits'] and not proof['errors']
    reused=[]
    for r in proof['accepted']:
        if r['wire'] in ENDS:continue
        p=received.parent/(r['wire']+'_WORLD.brep');fixed[r['wire']]=Part.read(str(p));pins.append(p);reused.append(r['wire'])
    assert len(reused)==22
    printed={k:fixed.pop(k) for k in PRINTED if k in fixed}
    targets={r['wire']:r['b_datum']['point_mm'] for r in rows if r['wire'] in ENDS and 'b_datum' in r}
    targets.update(W001=[55.5,75,70],W060=[132.5,0,95])
    bus=ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
    targets['W003']=json.loads(bus.read_text(encoding='utf-8'))['source_lead_datums']['W003']
    pairs=0
    def hit(s,obstacles):
        nonlocal pairs
        for name,t in obstacles.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            for a in s.Solids:
                for b in t.Solids:
                    if a.BoundBox.intersect(b.BoundBox) and not separated(a,b):
                        pairs+=1
                        if a.common(b).Volume>1e-6:return name
        return None
    templates={};datums=ports()
    for w,end in ENDS.items():
        templates[w]=[]
        for option in ('up','down','left','right'):
            r=prefix(datums[end],w,option);bits=[]
            for edge in r['edges']:
                e=Part.makeLine(A.Vector(*edge['start']),A.Vector(*edge['end'])) if edge['kind']=='line' else Part.Arc(A.Vector(*edge['start']),A.Vector(*edge['mid']),A.Vector(*edge['end'])).toShape()
                bits.append(Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(spec(w)['OD_mm']/2,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False))
            templates[w].append((r,Part.makeCompound(bits)))
    candidates=placements(targets);attempts=[];solution=None;solution_shapes={};errors=[]
    for c in candidates:
        if time.monotonic()-tic>480:break
        x,y=c['g1_centre'];gx,_=c['g2_centre'];z=c['floor']
        family={'G1':Part.makeBox(22,37,11,A.Vector(x-11,y-18.5,z)),
                'G2':Part.makeBox(19,30,9,A.Vector(gx-9.5,y-15,z))}
        edge=Part.makeLine(A.Vector(x+11,y,z+4.5),A.Vector(gx-9.5,y,z+4.5))
        family['W061']=Part.Wire([edge]).makePipeShell([Part.Wire([Part.makeCircle(2.1,A.Vector(x+11,y,z+4.5),A.Vector(1,0,0))])],True,False)
        blocked=None
        try:
            for name,s in family.items():
                owner=hit(s,fixed)
                if owner:blocked=dict(part=name,owner=owner);break
            if blocked:
                attempts.append(dict(placement=c,blocked=blocked));continue
            options={};rejected={}
            for w,variants in templates.items():
                delta=c['shift'][ENDS[w].split('.')[0]];options[w]=[];rejected[w]=[]
                for recipe,s in variants:
                    moved=s.copy();moved.translate(A.Vector(*delta))
                    q=json.loads(json.dumps(recipe))
                    for e in q['edges']:
                        for field in ('start','mid','end'):
                            if field in e:e[field]=[v+d for v,d in zip(e[field],delta)]
                    q['tip']=[v+d for v,d in zip(q['tip'],delta)]
                    lower=sum(e['length_mm'] for e in q['edges'])+math.dist(q['tip'],targets[w])
                    if (w=='W001' and lower+19>150) or (w=='W003' and lower+41>300):
                        rejected[w].append(dict(option=q['option'],owner='factory_length_lower_bound'));continue
                    owner=hit(moved,{**fixed,**family})
                    if owner:rejected[w].append(dict(option=q['option'],owner=owner));continue
                    options[w].append((q,moved))
            missing=[w for w in options if not options[w]]
            if missing:
                attempts.append(dict(placement=c,blocked_ends=missing,rejections={w:rejected[w] for w in missing}));continue
            ordered=sorted(options,key=lambda w:len(options[w]));chosen={}
            def joint(i):
                if i==len(ordered):return True
                w=ordered[i]
                for q,s in options[w]:
                    if hit(s,{k:v[1] for k,v in chosen.items()}):continue
                    chosen[w]=(q,s)
                    if joint(i+1):return True
                    del chosen[w]
                return False
            if not joint(0):
                attempts.append(dict(placement=c,blocked='no_mutually_clear_end_assignment'));continue
            solution=dict(placement=c,ends={w:q for w,(q,s) in chosen.items()},
                native_pending={name:[k for k,s in printed.items() if shape.BoundBox.intersect(s.BoundBox)] for name,shape in family.items()})
            solution_shapes={**family,**{w:s for w,(q,s) in chosen.items()}}
            attempts.append(dict(placement=c,complete_family_departures_clear=True));break
        except Exception as exc:
            errors.append(dict(placement=c,error=str(exc)));break
        finally:
            if len(attempts)%10==0:print('SPACE',len(attempts),'of',len(candidates),'pairs',pairs,flush=True)
            save(OUT/'progress.json',dict(attempts=attempts,solution=solution,errors=errors,exact_pairs=pairs))
    files=[]
    for name,s in solution_shapes.items():
        p=OUT/(name+'_WORLD.brep');s.exportBrep(str(p));files.append(p)
    finish=datetime.now(timezone.utc)
    pins += [Path(__file__),RECEIVED,received,bus,ROOT/'tools/electronics/w5_coupled_corridors.py',
        ROOT/'tools/electronics/w5_coupled_corridors_r2.py',ROOT/'tools/electronics/w5_coupled_corridors_r3.py',
        ROOT/'tools/electronics/w5_ground_bridge_plan.py',ROOT/'tools/electronics/w5_ground_network_plan.py']
    save(OUT/'checks.json',dict(status='CENTRAL_FAMILY_SPACE_PLAN_ONLY',solution=solution,
        candidate_count=len(candidates),attempts=attempts,errors=errors,exact_pairs=pairs,reused=reused,
        printed_pending=sorted(printed),replacement_obligations=obligations,
        body_envelopes_and_cage_registration_provisional=True,full_routes_complete=False,native_complete=False,
        selected=False,W5_complete=False,physical_pass=False,
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in files}))
    print('SPACE_DONE',len(attempts),bool(solution),len(errors),flush=True)


if __name__=='__main__':main()
