"""Separate W047 lane beside retained W069; never share its graph centreline."""
import json
import numpy as np
import feline_tangent_routes as ft
from plan_feline_layout import OUT
from plan_feline_FL_three_core_shared_trunk import transport


def construct(count=3):
    base=json.loads((OUT/'n01-current-W069-complete-body-plan.json').read_text())['middle_recipe']['parts']
    assert 3<=count<=23
    # Down-clock the companion cross-section below W058's complete tie head.
    # This changes no source cap, W069 route, insulation or bought part.
    lane,end_offset=transport(base[2:count],[-3,0,-2])
    start=[97.9,24,66.4]
    prefix=ft.biarc(start,[0,-1,0],lane[0]['start'],[0,-1,0])
    parts=prefix+lane
    assert ft.min_radius(parts)>=12.4-1e-6
    assert np.allclose(parts[0]['start'],start)
    return parts,end_offset
