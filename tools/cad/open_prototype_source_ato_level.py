"""Allocate the entire rear arrival plane above the retained ATO, not housing.

Reuse the prior unchanged ring/case proof only; all changed wire recipes and
the raised bus are new. Native grips, fuse removal and other wiring stay OPEN.
"""
from pathlib import Path
from datetime import datetime,timezone
import json, math, time
import open_prototype_rear_face as F
import open_prototype_source_bypass as G

B=F.B;ROOT=F.ROOT;OUT=F.OUT
PLAN=OUT/'source-ato-level-plan.json';PROOF=OUT/'source-ato-level-space.json'
PRIOR_PLAN=OUT/'source-rear-ordered-columns-plan.json'
PRIOR_PROOF=OUT/'source-rear-ordered-columns-space.json'
REUSE_PROOF=None

def build_geometry():
    p=F.build_geometry(ordered_columns=True)
    records=B.read(OUT/'obstacle-map-current.json')['objects']
    ato=next(r for r in records if r['name']=='F_L6_CP2_ATO')
    level=ato['bounds_mm'][5]+2.1+.1
    case=next(s for s in p['stations'] if s['role']=='P_REAR')
    dz=level-case['centre_mm'][2];case['centre_mm'][2]=level
    for i in range(1,6):p['ports'][f'P_REAR.{i}']['point_mm'][2]=level
    for e in p['body_ends']:e['datum']=p['ports'].get(e['current_role'])
    def source_row(row,route,lands):
        seg=F.parts(route);end=p['ports'][row['target']]['point_mm']
        route.finish(end,B.mul(p['ports'][row['target']]['departure'],-1))
        length=B.check_path(seg,route.row['segments'][0]['start_mm'],end,25.2)
        row.update(segments=seg,centreline_mm=length,nominal_fit_blank_mm=math.ceil(length+28.452),insulation_grip_lands=lands)
    for row in p['s1_routes']:
        if row['wire']=='W065':
            # Translating the last turn alone would kink its vertical land.
            r=G.Route(row['wire'],row['barrel_mm'],row['barrel_direction'],4.2,25.2,28.452,[])
            lands=[]
            def land(n,label):
                a=r.p[:];r.line(n);lands.append(dict(label=label,start_mm=a,end_mm=r.p[:]))
            end=p['ports'][row['target']]['point_mm']
            land(9,'S1 upstream');r.turn(B.UP,25.2)
            land(level-25.2-r.p[2],'Rear vertical before above-ATO transfer')
            r.turn(B.WEST,25.2);r.turn(B.SOUTH,25.2)
            land(r.p[1]-end[1],'P_REAR incoming insulation')
            source_row(row,r,lands)
        elif row['wire']=='W067':
            f0=next(q for q in records if q['name']=='F0_CP2')
            y=f0['bounds_mm'][4]+row['OD_mm']/2+1
            r=G.Route(row['wire'],row['barrel_mm'],row['barrel_direction'],4.2,25.2,28.452,[])
            lands=[]
            def land(n,label):
                a=r.p[:];r.line(n);lands.append(dict(label=label,start_mm=a,end_mm=r.p[:]))
            end=p['ports'][row['target']]['point_mm']
            G.short_line(r,2);r.turn(B.WEST,25.2);land(9,'Low-gallery insulation')
            r.shift([0,0,62.25-r.p[2]],25.2);r.line(r.p[0]-40)
            r.shift([0,y-r.p[1],0],25.2)
            land(r.p[0]-(end[0]-25.2-11),'F0-separated low gallery')
            r.turn(B.UP,25.2)
            # F0 determines only the low gallery. Shift the vertical column
            # SOUTH before the upper receiving bend so its tangent entry is
            # bound to SYS.3 instead of inheriting the low-gallery Y level.
            r.shift([0,end[1]-25.2-2-r.p[1],0],25.2)
            r.line(end[2]-25.2-r.p[2]);r.turn(B.EAST,25.2)
            land(11,'P_SYS upstream insulation');r.turn(B.NORTH,25.2)
            G.short_line(r,end[1]-r.p[1]);source_row(row,r,lands)
    for row in p['tails']:
        if row['wire'] not in ('W044','W052'):continue
        # Keep the receiving column / lateral shift, extend its straight
        # vertical insulation, and move its final UP->SOUTH quarter together.
        seg=row['segments'];v=next(i for i,s in enumerate(seg) if s['kind']=='line' and B.segment_geometry(s)[1]==B.UP)
        seg[v]['end']=B.add(seg[v]['end'],[0,0,dz])
        for s in seg[v+1:]:
            for k in ('start','mid','end'):
                if k in s:s[k]=B.add(s[k],[0,0,dz])
        length=B.check_path(seg,seg[0]['start'],p['ports'][row['target']]['point_mm'],6)
        assert length+14<=row['assumed_factory_limit_mm']
        row.update(centreline_mm=length,required_blank_mm=length+14,
            independent_grip_lands=[dict(start_mm=s['start'],end_mm=s['end']) for s in seg if s['kind']=='line' and B.segment_geometry(s)[0]>=9-1e-7])
    h=next(h for h in p['holders'] if h['role']=='F_AUX');end=p['ports'][h['input_target']]['point_mm']
    r=G.Route('F_AUX/input',h['input_mm'],B.EAST,4,6,11,[])
    # Use a3mm ungripped source land; independent retention is on the long
    # vertical and final incoming straight, not on this short bend lead-in.
    G.short_line(r,3);r.turn(B.UP,6);r.line(level-6-r.p[2]);r.turn(B.WEST,6)
    G.short_line(r,r.p[0]-(end[0]+6));r.turn(B.SOUTH,6)
    r.line(r.p[1]-end[1]);r.finish(end,B.SOUTH)
    seg=F.parts(r);length=B.check_path(seg,h['input_mm'],end,6)
    assert length+11<=h['factory_minimum_mm']
    h.update(input_segments=seg,input_blank_mm=length+11,
        input_grip_lands=[dict(start_mm=s['start'],end_mm=s['end']) for s in seg if s['kind']=='line' and B.segment_geometry(s)[0]>=9-1e-7])
    # The saved ring geometry is identical to the valid part of a97c50e.
    prior=B.read(PRIOR_PLAN)['family'];proof=B.read(PRIOR_PROOF)
    assert p['s1_module']==prior['s1_module']
    assert not proof['contacts'] and not proof['outside'] and not proof['errors']
    assert all(row['a']=='W065' and row['b']=='F_L6_CP2_ATO' for row in proof['input_point_intrusions'])
    p.update(s1_geometry_changed=False,
        reused_ring_case_proof=dict(proof=PRIOR_PROOF.name,producer_snapshot='a97c50e',
            scope='Identical transformed S1 material and all unchanged cases only; no route clearance reused'),
        rear_level_allocation=dict(ATO_name=ato['name'],ATO_top_mm=ato['bounds_mm'][5],
            conductor_radius_mm=2.1,project_margin_mm=.1,entry_level_mm=level),
        source_topology='All four rear arrivals above retained ATO top; ordered receiving columns, short AUX lead-in with upstream grips')
    return p

def build():
    q=B.read(PLAN)
    for n,h in q['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    return q['family']

def main():
    assert not PLAN.exists(),'Do not repeat unchanged allocation'
    tick=time.monotonic();p=build_geometry();screen=G.S.F.F.proximity(p)
    bad=[r for r in screen['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY']
    files=[Path(__file__),Path(F.__file__),Path(G.__file__),Path(G.T.__file__),Path(G.S.__file__),G.T.PLAN,
        OUT/'obstacle-map-current.json',OUT/'endpoint-plan.json',PRIOR_PLAN,PRIOR_PROOF]
    q=dict(family=p,geometry_digest=G.T.R.geometry_digest(p),mutual_preflight=screen,known_mutual_conflicts=bad,
        status='REJECTED_MUTUAL_PREFLIGHT' if bad else 'ABOVE_ATO_COMMON_REAR_FAMILY_REQUIRES_MATERIAL_GATE',
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat(),
        selected=False,stage_completed=False,physical_pass=False)
    PLAN.write_text(json.dumps(q,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:q[k] for k in ('status','known_mutual_conflicts','worker_seconds')}),flush=True)

if __name__=='__main__':main()
