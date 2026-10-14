"""Rigidly rotate the complete three-core breakout with its fixed land."""
import copy
from check_rail_hip_shared_space import fan as vertical_fan
from plan_current_moving_looms import add,sub,rotation


def fan(row,direction):
    result=copy.deepcopy(vertical_fan(row,direction));root=row['fixed_anchor_world_mm']
    angle=row.get('fixed_entry_tilt_degrees',0)
    for core in result:
        for key in ('parts','after_5mm'):
            for part in core[key]:
                for field in ('start','mid','end'):
                    if field in part:part[field]=add(root,rotation(sub(part[field],root),[1,0,0],angle))
    return result
