"""Close extra-circuit source coverage before another placement experiment.

134schematic sections are NOT134external cable pieces. Eleven sections are
inside the retained populated U1 carrier. Read actual named saved guide ends,
not endpoints from an unselected study. Transfer11known external interfaces.
"""
import hashlib
import json
import math
import re
import time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,BASE,MODEL
from compose_feline_n01_allocation import tangent,mv,plus

INTERNAL={'XP04A','XP04B','XP04C','XS12','XS22','XS32','XL03','XL04','XL11','XL12','XL13'}


def main():
    tick=time.monotonic();dest=OUT/'n01-extra-circuit-source-ends.json';assert not dest.exists()
    files={k:p for k,p in dict(motion=OUT/'motion-layout.json',modules=OUT/'n01-module-plan-r5.json',
        ecad=ROOT/'hardware/electronics/kicad-current/design.json',
        e1=BASE/'body-harness-checkpoint/e1-selection.json',
        common=BASE/'body-harness-checkpoint/u1-common-wiring-plan.json',
        service=BASE/'body-harness-checkpoint/u1-service-departures-plan.json',
        wago=OUT/'n01-twenty-wago-port-contract.json').items()}
    p={k:json.loads(f.read_text()) for k,f in files.items()};reader=SavedShapes()
    groups={r['role']:r for r in p['modules']['groups']};extra=[w for w in p['ecad']['wires'] if not w['id'].startswith('W0')]
    assert len(extra)==45 and INTERNAL<={w['id'] for w in extra}
    assert p['e1']['selected'] and p['e1']['E1_complete'] and len(p['e1']['local_links'])>0
    rows=[];errors=[];endrows=[]
    for r in p['motion']['inventory']:
        label=r['label']
        if r['kind']!='curve' or not (label.startswith('wire/') and not label.startswith('wire/W0') or label.startswith('headwire/')):continue
        s=reader.shape(MODEL,r['object']);vertices={};edges={}
        for edge in s.Edges:
            for vertex in edge.Vertexes:
                q=vertex.Point;key=tuple(round(x,5) for x in q)
                vertices[key]=q;edges.setdefault(key,[]).append(edge)
        ends=[]
        for key,ee in edges.items():
            if len(ee)!=1:continue
            edge=ee[0];q=vertices[key];u,v=edge.FirstParameter,edge.LastParameter
            first=(edge.valueAt(u)-q).Length < (edge.valueAt(v)-q).Length
            d=edge.tangentAt(u if first else v)
            if not first:d=-d
            ends.append(dict(source_point_mm=list(q),source_departure_into_guide=list(d)))
        raw=s.exportBrepToString().encode('utf-8')
        rows.append(dict(object=r['object'],label=label,source_guide_sha256=hashlib.sha256(raw).hexdigest(),
            source_centreline_length_mm=s.Length,source_ends=ends,
            guide_end_is_not_automatically_pin_or_mouth=True,current_port_transfer_qualified=False))
    full={**p['common']['complete_routes'],**p['service']['replacements']}
    full={k:v for k,v in full.items() if not k.startswith('W0')};assert len(full)==11
    bywg={r['wire']:r for st in p['wago']['stations'] for r in st['occupied_ports'] if r['wire']=='XL09'}
    for wire,route in full.items():
        for side,index,sgn in (('a',0,1),('b',-1,-1)):
            source=route['source'][side];kind=source['kind'];ref=source['ref']
            group=('Pi4' if ref.startswith('PI.') else 'PWM9685' if ref.startswith('PCA.') else
                'WAGO:G_TAIL' if ref.startswith('G_TAIL.') else 'PWM1608_U1')
            if group=='WAGO:G_TAIL':
                q=bywg[wire]['point_mm'];d=bywg[wire]['departure_axis'];basis='Current all20WAGO contract; source guide not used as casing pad'
            else:
                g=groups[group];q=plus(mv(g['rotation_rows'],source['world_mm']),g['translation_mm'])
                d=tangent(route['parts'][index],side=='a');d=[sgn*x for x in d];d=mv(g['rotation_rows'],d)
                basis='Selected E1 source datum + current module transform ONCE; old full middle NOT retained'
            endrows.append(dict(wire=wire,side=side,schematic_endpoint=next(w for w in extra if w['id']==wire)[side],
                named_physical_interface=ref,source_kind=kind,current_group=group,point_mm=q,
                departure_axis=d,nominal_OD_mm=route['source'].get('OD_project_upper_mm'),
                minimum_fixed_radius_mm=route.get('min_fixed_radius_mm',route['source'].get('project_radius_mm')),
                source_point_mm=source['world_mm'],basis=basis,
                current_route_and_grip_not_qualified=True,above_torso_roof_112=q[2]>112))
    assert len(endrows)==22
    report=dict(status='EXTRA_CIRCUIT_SOURCE_COVERAGE_AND_11EXTERNAL_DATUMS_NOT_COMPLETE_N01',
        selected=False,N01_complete=False,physical_pass=False,schematic_extra_sections=45,
        retained_U1_internal_sections=sorted(INTERNAL),external_schematic_sections=34,
        these_are_not_counts_of_physical_factory_custom_pieces=True,
        retained_internal_basis='Selected E1 circuit/population/copper graph and84formed leads move together in PWM1608_U1. Do not add eleven duplicate external cables or invent an unknown board pinout.',
        source_guides=rows,current_external_ends=endrows,
        remaining_external_sections_without_current_full_end_pair=[w['id'] for w in extra if w['id'] not in INTERNAL and w['id'] not in full],
        Pi_GPIO_roof_conflicts=[r['wire']+'/'+r['side'] for r in endrows if r['above_torso_roof_112']],
        complete134schematic_graph_unchanged=True,errors=errors,
        source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():sha(f) for f in (*files.values(),Path(__file__))}},
        worker_seconds=round(time.monotonic()-tick,3))
    assert len(report['remaining_external_sections_without_current_full_end_pair'])==23
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(report['status'],'guides',len(rows),'ends',len(endrows),'Pi roofs',report['Pi_GPIO_roof_conflicts'],report['worker_seconds'],flush=True)


if __name__=='__main__':main()
