"""Constructive cross-sections, not area-density guesses or route approval.

Parallel transport without twist through a circular arc gives each centre
radius at least R-centre_offset. This bound remains valid for every bend
plane. Endpoint fan-in, branch space, self-intersections and paths stay OPEN.
"""
import json,math


def certificate(points,radii,minimums,corridor_radius,bend_radius,gap=.2):
    assert len(points)==len(radii)==len(minimums)>0 and min(radii)>0
    offsets=[math.hypot(*p) for p in points]
    spacing=min((math.dist(a,b)-radii[i]-radii[j] for i,a in enumerate(points) for j,b in enumerate(points) if i<j),default=math.inf)
    enclosing=max(o+r for o,r in zip(offsets,radii))
    bend=[bend_radius-o for o in offsets]
    ok=spacing>=gap-1e-8 and enclosing<=corridor_radius+1e-8 and all(a>=b-1e-8 for a,b in zip(bend,minimums))
    return dict(centres_mm=points,jacket_radii_mm=radii,required_project_bends_mm=minimums,
        minimum_jacket_gap_mm=spacing if math.isfinite(spacing) else None,enclosing_radius_mm=enclosing,
        guaranteed_minimum_wire_bend_mm=min(bend),corridor_radius_mm=corridor_radius,
        corridor_centre_bend_mm=bend_radius,section_and_turn_fit=ok,
        frame_rule='Continuous no-twist parallel transport; no wire permutation or local twist added',
        actual_shared_route_branches_roots_access_not_qualified=True)


def triangle(radius):
    R=(2*radius+.2)/math.sqrt(3)
    return [[R*math.cos(a*2*math.pi/3),R*math.sin(a*2*math.pi/3)] for a in range(3)]


def square(radius):
    d=radius+.1;return [[x*d,y*d] for x,y in ((-1,-1),(-1,1),(1,1),(1,-1))]


def main():
    from check_main_p0_placement import ROOT,sha
    from plan_feline_layout import OUT
    from feline_atomic_save import save_json
    from pathlib import Path
    nf=OUT/'n01-current-corridor-topology.json';network=json.loads(nf.read_text())
    cases={}
    for name,key,centres,radius,required in (
        ('single_medium','2.1-R16',[[0,0]],2.1,12.4),
        ('three_small','4.0-R16',triangle(1.55),1.55,12.4),
        ('four_medium','6.0-R16',square(2.1),2.1,12.4),
        ('three_small_large_bend','3.5-R28',triangle(1.55),1.55,25.2),
        ('single_medium_large_bend','2.1-R28',[[0,0]],2.1,25.2)):
        row=network['classes'][key];cases[name]=dict(corridor_class=key,**certificate(centres,[radius]*len(centres),[required]*len(centres),row['radius_mm'],row['bend_mm']))
        assert cases[name]['section_and_turn_fit'],name
    negative=certificate(square(2.1),[2.1]*4,[25.2]*4,6,28)
    assert not negative['section_and_turn_fit'],'Do not accept four large-bend wires just because their section fits'
    save_json(OUT/'n01-constructive-bundle-sections.json',dict(status='FIVE_SECTION_AND_TURN_CONSTRUCTIONS_RECEIVED_NOT_ALLOCATED',
        sections=cases,rejected_four_medium_R28=negative,all123_wires_not_yet_assigned_to_shared_trunks=True,
        N01_complete=False,physical_pass=False,source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (nf,Path(__file__))}))
    print(json.dumps({k:dict(enclosing_mm=v['enclosing_radius_mm'],bend_lower_mm=v['guaranteed_minimum_wire_bend_mm']) for k,v in cases.items()}))


if __name__=='__main__':main()
