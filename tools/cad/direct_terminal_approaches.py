"""Simplify only optional wire approaches, never physical ports or grips.

W004/W069 pressure lands are their LAST9mm terminal segment. The preceding
Uturn/return is not a mount or manufacturer requirement. Remove it as a new
whole-route proposal; W022's middle pressure land must NOT be shortened.
"""
import copy,math


def simplify(rows, pending):
    result=copy.deepcopy(rows)
    for name in ('W004','W069'):
        if name not in pending:continue
        row=result[name];parts=row['receiving_parts'];land=row['receiving_land']
        assert parts[-1]==land and row['receiving_grip_part_index']==len(parts)-1,name
        assert land['kind']=='line' and abs(land['length_mm']-9)<1e-6,name
        assert math.dist(land['end'],row['receiver_point_mm'])<1e-6,name
        row['removed_optional_pregrip_parts']=copy.deepcopy(parts[:-1])
        row['receiving_parts']=[copy.deepcopy(land)]
        row['receiving_grip_part_index']=0;row['free_end']=copy.deepcopy(land['start'])
        row['receiver_outward_axis']=[(a-b)/land['length_mm'] for a,b in zip(land['start'],land['end'])]
        row['receiving_approach_basis']='Direct to unchanged9mm terminal pressure land; optional pregrip loop removed, not yet whole-route qualified'
    return result
