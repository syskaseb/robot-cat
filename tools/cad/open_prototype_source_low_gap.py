"""One constraint-derived low corridor, preserving six clear full profiles.

F0 top and G_AUX bottom bound the whole4.2mm tube, not just its axis.
Do not rerun the other six or treat the nominal0.15mm gap as delivered fit.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,time
import open_prototype_source_south_ato as Prior
import open_prototype_rear_face as F
import open_prototype_source_bypass as G
B=G.B;ROOT=G.ROOT;OUT=G.OUT
PLAN=OUT/'source-low-gap-plan.json'
# Unchanged complete cases/positive-point evidence only. The new full-radius
# gate checks the changed W068, with all current profiles and W001 as peers.
PROOF=Prior.PROOF
SIX_PROOF=OUT/'source-south-ato-radius.json'

def build_geometry():
    p=Prior.build();proof=B.read(SIX_PROOF)
    assert not proof['outside'] and not proof['errors']
    assert proof['conflicts']==[dict(a='W068',b='G_AUX',distance_mm=2.0,required_mm=2.1,basis='nominal module reservation')]
    assert all(B.sha(ROOT/n)==h for n,h in proof['source_sha256'].items())
    row=next(r for r in p['s1_routes'] if r['wire']=='W068')
    g=next(r for r in p['stations'] if r['role']=='G_AUX')
    f0=next(r for r in B.read(OUT/'obstacle-map-current.json')['objects'] if r['name']=='F0_CP2')
    radius=row['OD_mm']/2;margin=.1
    lo=f0['bounds_mm'][5]+radius+margin
    hi=g['centre_mm'][2]-g['size_mm'][2]/2-radius-margin
    assert hi>lo,'No allocated tube corridor; change shared layout'
    level=(lo+hi)/2
    end=p['ports'][row['target']]['point_mm']
    r=G.Route('W068',row['barrel_mm'],row['barrel_direction'],4.2,25.2,28.452,[]);lands=[]
    def land(n,label):
        a=r.p[:];r.line(n);lands.append(dict(label=label,start_mm=a,end_mm=r.p[:]))
    land(9,'S1 upstream');r.turn(B.WEST,25.2);land(9,'Low-gallery upstream insulation')
    r.shift([0,0,level-r.p[2]],25.2)
    land(r.p[0]-(-72+25.2),'Low gallery before bank; no clamp in narrow gap')
    r.turn(B.UP,25.2);r.line(end[2]-25.2-r.p[2]);r.turn(B.EAST,25.2)
    r.line(end[0]-25.2-r.p[0]);r.turn(B.NORTH,25.2)
    land(end[1]-r.p[1],'P_SYS incoming');r.finish(end,B.NORTH)
    seg=F.parts(r);length=B.check_path(seg,row['barrel_mm'],end,25.2)
    row.update(segments=seg,centreline_mm=length,nominal_fit_blank_mm=math.ceil(length+28.452),insulation_grip_lands=lands)
    p.update(changed_path_names=['W068'],
        low_tube_corridor=dict(centre_level_mm=level,permitted_centre_levels_mm=[lo,hi],
            bottom_reservation='F0_CP2',top_reservation='G_AUX',minimum_project_margin_mm=margin,
            nominal_each_side_gap_mm=(g['centre_mm'][2]-g['size_mm'][2]/2-f0['bounds_mm'][5]-row['OD_mm'])/2,
            no_grip_in_narrow_corridor=True,delivered_fit_not_qualified=True),
        six_unchanged_radius_profiles_reused=dict(proof=SIX_PROOF.name,worker_seconds=proof['worker_seconds'],
            profiles=['W064','W065','W067','W044','W052','F_AUX/input'],
            scope='Same current pinned cases/routes only; modified W068 and its interactions checked anew'),
        source_topology='Preserved south-of-ATO family; W068 full tube allocated between F0 top and G_AUX bottom')
    return p

def build():
    q=B.read(PLAN)
    for n,h in q['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    return q['family']

def main():
    assert not PLAN.exists(),'No unchanged repeat'
    tick=time.monotonic();p=build_geometry();screen=G.S.F.F.proximity(p)
    bad=[r for r in screen['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY']
    files=[Path(__file__),Path(Prior.__file__),Path(F.__file__),Path(G.__file__),Prior.PLAN,Prior.PROOF,SIX_PROOF,
        OUT/'obstacle-map-current.json',OUT/'endpoint-plan.json']
    q=dict(family=p,geometry_digest=G.T.R.geometry_digest(p),mutual_preflight=screen,known_mutual_conflicts=bad,
        status='REJECTED_MUTUAL_PREFLIGHT' if bad else 'LOW_TUBE_GAP_REQUIRES_SCOPED_RADIUS_GATE',
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat(),
        selected=False,stage_completed=False,physical_pass=False)
    PLAN.write_text(json.dumps(q,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:q[k] for k in ('status','known_mutual_conflicts','worker_seconds')}),flush=True)

if __name__=='__main__':main()
