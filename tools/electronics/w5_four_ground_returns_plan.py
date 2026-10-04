"""One four-return family; unchanged ground blocks and existing W061.

Prepare only a plan while the 36-core worker runs. TKD2500125 OD4.2/R21
comes from the existing received power-wire specification. Geometry,
restraints, mutual clearance and stock are deliberately not certified here.
"""
from math import ceil
from pathlib import Path
import json
from w5_rounded_path import corner_offsets

RADIUS=21.0
OD=4.2
STRAIGHT=3.5
# Current received cage labels, not the old body-ground-r1 permutation.
# G1 +X [.1,.5,.3,.4,.2], G2 +X [.2,.3,.1,.4,.5].
# Original RR_G +X [.3,.2,.1,.4,.5], never the rejected rotated block.
SPECS=(
    ('W025','G1.3',(66,11,113.5),'FL_G.1',(-46.5,30.5,113.5),1),
    ('W036','G1.4',(73.5,11,113.5),'FR_G.1',(-39.75,-30.5,113.5),-1),
    ('W062','G2.2',(97.5,9.5,113.5),'RL_G.1',(61.5,30.5,113.5),1),
    ('W063','G2.3',(104.25,9.5,113.5),'RR_G.1',(75,-30.5,113.5),-1),
)


def plan():
    rows=[]
    for rank,(wire,a,source,b,leg,side) in enumerate(SPECS):
        top=source[2]+2*RADIUS
        # Source: two opposing quarter circles lift by42/run42, +Y tangent.
        pa=[source[0],source[1]+STRAIGHT+2*RADIUS,top]
        # Leg: genuine R21 half-turn, from inward to outward Y tangent.
        pb=[leg[0],leg[1]-side*STRAIGHT,leg[2]+2*RADIUS]
        outer_x=-108 if wire in ('W025','W036') else 168
        high=201+7*rank
        middle=[pa,[pa[0],112,top],[pa[0],112,high],
                [outer_x,112,high],[outer_x,side*50,high],
                [pb[0],side*50,high],[pb[0],side*50,top],pb]
        corner_offsets(middle,RADIUS)
        rows.append(dict(wire=wire,source_end=a,leg_end=b,
            source_entry_mm=list(source),leg_entry_mm=list(leg),leg_side=side,
            source_prefix='3.5mm straight + two opposing R21 quarter arcs in Y/Z',
            leg_prefix='3.5mm inward straight + true R21 upward half-turn in Y/Z',
            middle_mm=middle,static_radius_mm=RADIUS,core_OD_mm=OD,
            selected=False,restraints_complete=False,geometry_checked=False))
    return rows


def provisional_blank(external_mm,source_family='615'):
    # 615: reserve14 within received12..14; 415: strip11. Rework30 assumed.
    assert source_family in ('615','415')
    source_strip=14 if source_family=='615' else 11
    return ceil((external_mm+source_strip+11+30)/10)*10


def main():
    from servo_fuse_inputs_r1 import save,sha
    root=Path(__file__).resolve().parents[2]
    graph_path=root/'hardware/electronics/power-platform/wiring-p0.json'
    bridge_path=root/'hardware/electronics/full-cat/body-ground-bridge-finish-r5/interface.json'
    graph=json.loads(graph_path.read_text(encoding='utf-8'))
    bridge=json.loads(bridge_path.read_text(encoding='utf-8'))
    assert bridge['cage_labels']=={'G1':['.1','.5','.3','.4','.2'],
                                 'G2':['.2','.3','.1','.4','.5']}
    rows=plan()
    for row in rows:
        wire=next(w for w in graph['wires'] if w['id']==row['wire'])
        assert {wire['a'],wire['b']}=={row['source_end'],row['leg_end']}
    folder=root/'hardware/electronics/full-cat/w5-four-ground-returns-plan-r1'
    folder.mkdir(parents=True,exist_ok=True)
    save(folder/'intent.json',dict(status='FOUR_CURRENT_NETS_RADIUS_AND_TANGENT_PLAN_ONLY',
        routes=rows,existing_W061_unchanged=True,new_splices=0,
        stock_length_mm=None,stock_not_selected=True,physical_pass=False,W5_complete=False,
        source_sha256={p.relative_to(root).as_posix():sha(p) for p in
            (Path(__file__),graph_path,bridge_path,root/'tools/electronics/w5_rounded_path.py')}))
    print('GROUND_PLAN_ONLY',len(rows),'actual geometry/grips/stock open',flush=True)


if __name__=='__main__':main()
