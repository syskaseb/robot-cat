"""One C1 R10 spatial S-approach; retained terminal/parallel9mm clamp land."""
import copy,math
from plan_current_moving_looms import add,mul,exact_quarter,exact_turn_to
from plan_current_mta_interfaces import line
from plan_body_fanout_layout import reverse_part


def build(original):
    row=copy.deepcopy(original);end=row['receiver_point_mm'];down=[0,0,-1];away=[0,-1,0]
    # A45deg descent clears W024 but ends inside LowerCarrier. Its actual
    # maximum Z is49.87. A15deg plane ends at53.473, above that material
    # plus1.25mm cable radius/margin, while passing below the saved W024.
    diagonal=[math.cos(math.pi/12),0,-math.sin(math.pi/12)]
    entry=line(end,add(end,mul(down,9)))
    first=exact_quarter(entry['end'],down,away,10)
    land=line(first['end'],add(first['end'],mul(away,9)))
    lateral=exact_quarter(land['end'],away,diagonal,10)
    restore=exact_turn_to(lateral['end'],diagonal,[1,0,0],10)
    parts=[reverse_part(p) for p in reversed([entry,first,land,lateral,restore])]
    assert all(math.dist(a['end'],b['start'])<1e-7 for a,b in zip(parts,parts[1:]))
    row.update(receiving_parts=parts,receiving_land=parts[2],receiving_grip_part_index=2,
        free_end=parts[0]['start'],receiver_outward_axis=[1,0,0],
        receiver_profile='parallel9mm_land_spatial_S_R10',entry_straight_project_mm=9,
        approach_basis='SharedMAIN/Spacer2/W024 avoidance; terminals and9mm Y40.5 land retained')
    assert abs(row['receiving_land']['length_mm']-9)<1e-7
    assert row['receiving_parts'][-1]['end']==original['receiver_point_mm']
    return row
