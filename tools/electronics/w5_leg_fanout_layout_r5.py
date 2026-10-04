"""Keep ground footprints; separate inner D and outer G height bands.

R4's shifted G blocks overlap bought auxiliaries. Its X shifts of Y-running
DATA restraints miss the wire. Retain all DATA grips and bought footprints,
rotate only G orientation, and lift D vertically before travelling in X.
"""
GROUND_DX=0.0
GROUND_DY=0.0


def changed_plan(rows):
    result=[]
    for old in rows:
        r=dict(old)
        if r['role']=='V':result.append(r);continue
        points=r['waypoints_mm'];end=list(points[0]);tail=list(points[-1])
        leg=r['loom'][:2];side=1 if leg.endswith('L') else -1
        outward=-1 if leg.startswith('F') else 1
        peers=sorted((q for q in rows if q['loom'][:2]==leg and q['role']==r['role']),key=lambda q:q['waypoints_mm'][0][0])
        index=next(i for i,q in enumerate(peers) if q['wire']==r['wire'])
        rank=index if outward<0 else 2-index
        if r['role']=='G':
            # The uncut moving ends are mapped as project-labelled cages;
            # catalogue marks are not inferred from primitive block boxes.
            end[1]=side*49.5;lane=side*83.5;level=141.1+2.5*rank
            r['body_entry_tangent']=[0,side,0]
        else:
            lane=side*20.49;level=133.6+2.5*rank
        r['waypoints_mm']=[end,[end[0],lane,end[2]],[end[0],lane,level],
            [tail[0],lane,level],[tail[0],tail[1],level],tail]
        r['candidate_ground_relocation']=False
        r['ground_orientation_180_same_footprint']=r['role']=='G'
        r['new_mounts_selected']=False
        result.append(r)
    assert len(result)==36
    return result
