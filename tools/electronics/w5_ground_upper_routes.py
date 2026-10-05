"""Joint complete ground recipe after facing bridge and upper-rail planning."""
from pathlib import Path
import json,math
from w5_ground_joint_layout_r4 import ROOT
from w5_ground_bridge_plan import ports
from w5_ground_network_plan import profile
from w5_central_ground_routes_r2 import recipes as central_recipes
from w5_leg_ground_upper_rail import layout
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add,mul
from w5_rounded_path import corner_offsets

def prefix(wire,end,roll=0,datum=None):
    p=datum or ports()[end];c=CentreLine(p['point_mm'],p['outward_axis']);r=profile(wire)['radius_mm']
    c.line(add(c.p,mul(c.t,6)))
    if roll:
        c.arc([0,roll/math.sqrt(2),1/math.sqrt(2)],radius=r)
        c.arc([0,-roll/math.sqrt(2),1/math.sqrt(2)],math.pi/4,radius=r)
    else:c.arc([0,0,1],radius=r)
    c.line(add(c.p,mul(c.t,6)))
    return dict(edges=c.edges,tip=c.p,tangent=c.t)

def recipes():
    _,legends=layout();lookup={r['wire']:r for r in legends}
    result=central_recipes()
    for wire,end,roll,level in [('W025','G1.3',0,218),('W036','G1.4',-1,223),
                              ('W062','G2.2',-1,228),('W063','G2.3',1,233)]:
        a=prefix(wire,end,roll);b=lookup[wire];pa,pb=a['tip'],b['tip']
        result.append(dict(wire=wire,a=a,b=b,middle=[pa,[pa[0],pa[1],level],[pb[0],pb[1],level],pb],radius_mm=21))
    raw=json.loads((ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json').read_text(encoding='utf-8'))['routes']
    for old in raw:
        if old['role']!='G':continue
        wire=old['wire'];a=lookup[wire];pa,pb=a['tip'],old['waypoints_mm'][-1]
        level=196+(int(old['loom'][-1])-1)*4
        result.append(dict(wire=wire,a=a,b=None,middle=[pa,[pa[0],pa[1],level],[pb[0],pa[1],level],
            [pb[0],pb[1],level],pb],radius_mm=10,loom=old['loom'],retained_moving_candidate_mm=old['moving_candidate_length_mm']))
    a=prefix('W060','G1.2');p=a['tip']
    result.append(dict(wire='W060',a=a,b=None,middle=[p,[p[0],p[1],170],[132.5,0,170],[132.5,0,95]],
        radius_mm=10,retained_MAIN_tail=True,retained_tail_radius_bound_mm=6))
    a=prefix('XA05','G2.5');b=prefix('XA05','G_AUX.1',datum=dict(point_mm=[110.5,-57,113.5],outward_axis=[-1,0,0]))
    pa,pb=a['tip'],b['tip']
    result.append(dict(wire='XA05',a=a,b=b,middle=[pa,[pa[0],pa[1],170],[pb[0],pb[1],170],pb],radius_mm=15))
    assert len(result)==20 and len({r['wire'] for r in result})==20
    for row in result:corner_offsets(row['middle'],row['radius_mm'])
    return result

if __name__=='__main__':print('Analytical bend constraints:',len(recipes()),'routes plus retained straight W061')
