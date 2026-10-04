"""Single joint D/G layout, with outward-facing ground blocks.

Keep each complete cable continuous and each original electrical endpoint.
The four G blocks are moved outboard, NOT on top of the DATA blocks.
CAD positions and wire diameters remain prototype assumptions.
"""
import math

GROUND_DX = 40.0
GROUND_DY = 22.0
D_LANE = 20.49


def changed_plan(rows):
    result = []
    dg = [r for r in rows if r['role'] != 'V']
    for old in rows:
        r = dict(old)
        if r['role'] == 'V':
            result.append(r)
            continue
        old_points = r['waypoints_mm']
        end = list(old_points[0]); tail = list(old_points[-1])
        leg = r['loom'][:2]; side = 1 if leg.endswith('L') else -1
        outward = -1 if leg.startswith('F') else 1
        # Sort by the real cage X, not servo number: RR cages are permuted.
        peers = sorted((q for q in dg if q['loom'][:2] == leg and q['role'] == r['role']),
                       key=lambda q:q['waypoints_mm'][0][0])
        index = next(i for i,q in enumerate(peers) if q['wire'] == r['wire'])
        rank = index if outward < 0 else 2-index
        level = 133.6 + 2.5*rank
        if r['role'] == 'G':
            end[0] += GROUND_DX
            end[1] = side*(49.5+GROUND_DY)
            lane = side*(49.5+GROUND_DY+12)
            level += 2.5
            points = [end, [end[0],lane,end[2]], [end[0],lane,level],
                      [tail[0],lane,level], [tail[0],tail[1],level], tail]
            r['body_entry_tangent'] = [0,side,0]
        else:
            # R10 turn lifts and moves away from the crowded existing mouths.
            # No reduced bend radius or abrupt elbow is introduced.
            lane = side*D_LANE
            dx = outward*(level-end[2])*.9/math.sqrt(1-.9**2)
            points = [end, [end[0],lane,end[2]], [end[0]+dx,lane,level],
                      [tail[0],lane,level], [tail[0],tail[1],level], tail]
        r['waypoints_mm'] = points
        r['candidate_ground_relocation'] = r['role'] == 'G'
        result.append(r)
    assert len(result) == 36 and len({r['wire'] for r in result}) == 36
    return result
