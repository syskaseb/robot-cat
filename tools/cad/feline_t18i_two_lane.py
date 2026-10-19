"""Two whole first-land rows, not scalar movement of purchased WAGO cases.

Every actual mouth is unchanged. Both rows keep full9mm grooves and complete
selected T18I heads. The second straight land is12mm farther along its wire,
so adjacent PETG combs no longer cover each other's head. No R reduction.
"""
import numpy as np
import FreeCAD as A
import Part
from feline_t18i_selected_head import unit as one_lane

LANE_PITCH_MM=12. # 9mm full clamp +2*1.25mm nominal separation, rounded UP.


def unit(st,slot,lane):
    assert lane in (0,1)
    result=one_lane(st,slot)
    if lane:
        d=np.array([0.,-slot['side'],0.]);delta=LANE_PITCH_MM*d
        for w in result['wires']:
            q=np.asarray(w['point_mm']);r=w['radius_mm']
            result['parts']['wire:'+w['endpoint']]=Part.makeCylinder(r,12.25+LANE_PITCH_MM,A.Vector(*q),A.Vector(*d))
            w['grip_start_mm']=(np.asarray(w['grip_start_mm'])+delta).tolist()
            w['straight_tip_mm']=(np.asarray(w['straight_tip_mm'])+delta).tolist()
        for n in ('split_common_comb','band_budget','head_budget'):
            result['parts'][n].translate(A.Vector(*delta))
    result['grip_lane']=lane
    result['whole_extra_straight_mm']=lane*LANE_PITCH_MM
    result['bought_case_all_ports_R_insulation_and_full_grip_unchanged']=True
    result['source_length_capacity_and_roots_still_required']=True
    return result
