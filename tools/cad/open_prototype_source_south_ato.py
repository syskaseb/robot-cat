"""Shared seven-profile topology goes SOUTH of ATO, under the actual roof.

The above-fuse hypothesis is rejected by torso geometry. Two tangent turns
and a derived oblique land replace that hypothesis, not another Z offset.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,time
import open_prototype_source_ato_level as Above
import open_prototype_rear_face as F
import open_prototype_source_bypass as G
B=G.B;ROOT=G.ROOT;OUT=G.OUT
PLAN=OUT/'source-south-ato-plan.json';PROOF=OUT/'source-south-ato-space.json'
REUSE_PROOF=None

def build_geometry():
    p=Above.build_geometry();level=138;face_y=22.5
    case=next(s for s in p['stations'] if s['role']=='P_REAR')
    case.update(centre_mm=[68.8,face_y-11,level],rotation='180',
        project_slot_order='World X ascending project labels, not supplier molded numbering')
    for i in range(1,6):
        d=p['ports'][f'P_REAR.{i}'];d['point_mm']=[68.8+(i-3)*6.5,face_y,level]
        d['rotated_model_cavity_index']=6-i
        d['basis']='180deg rotated envelope; project slots numbered world-X ascending; delivered cavity depth remains unmeasured'
    for e in p['body_ends']:e['datum']=p['ports'].get(e['current_role'])
    row=next(r for r in p['s1_routes'] if r['wire']=='W065')
    end=p['ports'][row['target']]['point_mm'];R=25.2
    r=G.Route('W065',row['barrel_mm'],B.NORTH,4.2,R,28.452,[]);lands=[]
    def land(n,label):
        a=r.p[:];r.line(n);lands.append(dict(label=label,start_mm=a,end_mm=r.p[:]))
    land(9,'S1 upstream');r.turn(B.UP,R)
    land(level-R-r.p[2],'Rear vertical before south-of-ATO bend')
    # 60deg from SOUTH: first arc ends EAST of the ATO and SOUTH of its
    # footprint. The following straight and turn never cross its Y59.45 edge.
    theta=math.radians(60);heading=[-math.sin(theta),-math.cos(theta),0]
    r.turn(heading,R)
    length=(r.p[0]-end[0]-R*(1-math.cos(theta)))/math.sin(theta)
    land(length,'Oblique insulation before receiver bend');r.turn(B.SOUTH,R)
    G.short_line(r,r.p[1]-end[1]);r.finish(end,B.SOUTH)
    seg=F.parts(r);length=B.check_path(seg,row['barrel_mm'],end,R)
    row.update(segments=seg,centreline_mm=length,nominal_fit_blank_mm=math.ceil(length+28.452),
        insulation_grip_lands=lands,short_entry_is_not_grip=True)
    for row in p['tails']:
        if row['wire'] not in ('W044','W052'):continue
        end=p['ports'][row['target']]['point_mm'];start=row['segments'][0]['start']
        r=G.Route(row['wire'],start,B.NORTH,4,6,14,[])
        if row['wire']=='W052':
            displacement=abs(end[0]-start[0]);shift_radius=10
            advance=math.sqrt(4*shift_radius*displacement-displacement**2)
            r.line(face_y+3-start[1]-advance)
            r.shift([end[0]-r.p[0],0,0],shift_radius)
        else:r.line(face_y+3-start[1])
        r.turn(B.UP,6);r.line(level-6-r.p[2]);r.turn(B.SOUTH,6)
        G.short_line(r,r.p[1]-end[1]);r.finish(end,B.SOUTH)
        seg=F.parts(r);length=B.check_path(seg,start,end,6)
        assert length+14<=row['assumed_factory_limit_mm']
        row.update(segments=seg,centreline_mm=length,required_blank_mm=length+14,
            independent_grip_lands=[dict(start_mm=s['start'],end_mm=s['end']) for s in seg if s['kind']=='line' and B.segment_geometry(s)[0]>=9-1e-7])
    h=next(h for h in p['holders'] if h['role']=='F_AUX');end=p['ports'][h['input_target']]['point_mm']
    r=G.Route('F_AUX/input',h['input_mm'],B.EAST,4,6,11,[])
    r.line(9);r.turn(B.UP,6);r.line(level-6-r.p[2]);r.turn(B.WEST,6)
    r.line(r.p[0]-(end[0]+6));r.turn(B.SOUTH,6);r.line(r.p[1]-end[1]);r.finish(end,B.SOUTH)
    seg=F.parts(r);length=B.check_path(seg,h['input_mm'],end,6)
    assert length+11<=h['factory_minimum_mm']
    h.update(input_segments=seg,input_blank_mm=length+11,
        input_grip_lands=[dict(start_mm=s['start'],end_mm=s['end']) for s in seg if s['kind']=='line' and B.segment_geometry(s)[0]>=9-1e-7])
    p.update(rear_level_allocation=dict(entry_level_mm=level,face_y_mm=face_y,
        rejected_above_ATO_level_mm=147,transfer_direction=heading,
        basis='Turn south of installed ATO before crossing its X span; roof excludes above-ATO hypothesis'),
        source_topology='South-of-ATO oblique full-radius transfer; all four current rear arrivals regenerated',
        native_grips_full_wiring_service_stock_open=True,selected=False,stage_completed=False)
    return p

def build():
    q=B.read(PLAN)
    for n,h in q['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    return q['family']

def main():
    assert not PLAN.exists(),'No unchanged repeat'
    tick=time.monotonic();p=build_geometry();screen=G.S.F.F.proximity(p)
    bad=[r for r in screen['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY']
    files=[Path(__file__),Path(Above.__file__),Path(F.__file__),Path(G.__file__),Path(G.T.__file__),Path(G.S.__file__),G.T.PLAN,
        OUT/'obstacle-map-current.json',OUT/'endpoint-plan.json',Above.PRIOR_PLAN,Above.PRIOR_PROOF,
        Above.PLAN,Above.PROOF]
    q=dict(family=p,geometry_digest=G.T.R.geometry_digest(p),mutual_preflight=screen,known_mutual_conflicts=bad,
        status='REJECTED_MUTUAL_PREFLIGHT' if bad else 'SOUTH_ATO_COMMON_FAMILY_REQUIRES_MATERIAL_GATE',
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat(),
        selected=False,stage_completed=False,physical_pass=False)
    PLAN.write_text(json.dumps(q,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:q[k] for k in ('status','known_mutual_conflicts','worker_seconds')}),flush=True)

if __name__=='__main__':main()
