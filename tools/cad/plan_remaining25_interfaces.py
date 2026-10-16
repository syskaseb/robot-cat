"""Bind all remaining fixed guides to physical ends before any new detail CAD.

Current eight opposed MTA joints are TWO cuts each, not continuous wires.
This is an interface allocation, not collision, retention or W5 acceptance.
"""
import json
import math
import time
from pathlib import Path
from plan_current_harness_interfaces import ROOT, OUT, SHA


def endpoint_land(parts, side, minimum):
    """Nearest sufficiently long straight; report intervening bend explicitly."""
    distance = 0
    indices = range(len(parts)) if side == 'start' else range(len(parts)-1, -1, -1)
    for i in indices:
        p = parts[i]
        if p['kind'] == 'line' and p['length_mm'] >= minimum-1e-6:
            axis = [(b-a)/p['length_mm'] for a,b in zip(p['start'],p['end'])]
            centre = [a+u*minimum/2 for a,u in zip(p['start'],axis)] if side=='start' else [
                b-u*minimum/2 for b,u in zip(p['end'],axis)]
            return dict(part_index=i, land_mm=minimum, centre_world_mm=centre,
                        axis=axis, intervening_guide_mm=distance,
                        entire_straight_mm=p['length_mm'],
                        offset_on_part_mm=0 if side=='start' else p['length_mm']-minimum)
        distance += p['length_mm']
    raise AssertionError(('No insulation land', side, minimum))


def allocate(register, plans):
    rows = [r for r in register['body_conductors'] if r['route_status']=='SCOPED_NOMINAL_GUIDE_QUALIFIED_NATIVE_OPEN']
    assert len(rows) == 25
    ends=[];segments=[]
    already={'W043':'P_SYS.5','W067':'P_SYS.2','W068':'P_SYS.3'}
    for row in rows:
        wid=row['id']; g=row['guide']; source=plans[g['plan']]
        route=source.get('routes',{}).get(g['route']) or source['factory_routes'][g['route']]
        cuts=[('custom' if row.get('factory_segment') else 'single',g['plan'],g['route'],route)]
        factory=row.get('factory_segment')
        if factory:
            plan=plans[factory['plan']]
            r=plan['factory_override'] if factory['route']=='factory_override' else plan['factory_routes'][factory['route']]
            cuts.insert(0,('factory',factory['plan'],factory['route'],r))
        outer={e['role']:e['point_mm'] for e in row['current_ends']}
        bound_outer=[]
        for kind,file,key,r in cuts:
            parts=r['parts']; radius=r['radius_mm']
            segment_id=wid+'/'+kind
            segments.append(dict(id=segment_id,wire=wid,kind=kind,recipe_file=file,recipe_key=key,
                radius_mm=radius,guide_mm=sum(p['length_mm'] for p in parts),actual_cut_mm=None))
            for side,point in (('start',parts[0]['start']),('end',parts[-1]['end'])):
                closest=min(outer,key=lambda n:math.dist(point,outer[n]))
                if math.dist(point,outer[closest])<1e-5:
                    role=closest;bound_outer.append(role)
                else:
                    assert factory, (wid,point,outer)
                    assert (kind,side) in (('factory','end'),('custom','start'))
                    role=wid+'_Joint.'+('factory' if kind=='factory' else 'custom')
                done=already.get(wid)==role
                # Preserve explicit former9mm independent grip contracts. Short
                # W041/W052 departures use a downstream straight, NOT the lever.
                minimum=3 if done or role=='F_PI.in' else 10 if role.startswith('F_') and role.endswith('.in') and not factory else 9
                land=endpoint_land(parts,side,minimum)
                ends.append(dict(id=segment_id+'/'+side,wire=wid,segment=kind,side=side,role=role,
                    point_world_mm=point,project_radius_mm=radius,recipe_file=file,recipe_key=key,
                    land=land,already_native_source_group=wid+'_P_SYS' if done else None,
                    root=None,normal=None,qualified=False,
                    caution='Downstream insulation land: support intervening bend/terminal during assembly' if land['intervening_guide_mm'] else None))
        assert sorted(bound_outer)==sorted(outer),(wid,bound_outer,outer)
    assert len(segments)==33 and len(ends)==66
    assert len({e['id'] for e in ends})==66
    assert sum(bool(e['already_native_source_group']) for e in ends)==3
    # Three equal branch jackets can share one loop. The larger incoming feed
    # must have its own axial level and binding; a loose mixed-OD loop is NOT
    # accepted as retention. Whole band, closure and roots still need a gate.
    groups=[];grouped=set()
    for leg in ('FL','FR','RL','RR'):
        thin=[e for e in ends if e['role'] in [leg+'_P.'+str(i) for i in (2,3,4)]]
        assert len(thin)==3 and all(e['project_radius_mm']==1.55 for e in thin)
        points=[e['point_world_mm'] for e in thin]
        assert all(abs(p[1]-points[0][1])<1e-6 and abs(p[2]-19.5)<1e-6 for p in points)
        # CentreZ24: the whole3mm axial cradle lies on all existing UP stems.
        groups.append(dict(id=leg+'_P_BRANCH3',ends=[e['id'] for e in thin],
            architecture='Three equal-radius jackets, common loop on one independent saddle',
            common_axis=[0,0,1],centre_world_mm=[sum(p[0] for p in points)/3,points[0][1],24],
            project_radius_mm=1.55,land_mm=3,lateral_half_span_mm=4.75+1.55,
            qualified=False,root=None,normal=None))
        grouped.update(e['id'] for e in thin)
    for e in ends:
        if e['id'] in grouped or e['already_native_source_group']:continue
        groups.append(dict(id=e['id'],ends=[e['id']],architecture='Independent insulation saddle/lacing',
                           qualified=False,root=None,normal=None,**e['land'],
                           project_radius_mm=e['project_radius_mm']))
    assert len(groups)==55
    assert len({i for g in groups for i in g['ends']})==63
    return ends,segments,groups


def run():
    tick=time.monotonic();files={OUT/'harness-interfaces-plan.json',Path(__file__),
                                OUT/'current-body-source-native-set.json'}
    register=json.loads((OUT/'harness-interfaces-plan.json').read_text())
    names={r['guide']['plan'] for r in register['body_conductors'] if r['route_status']=='SCOPED_NOMINAL_GUIDE_QUALIFIED_NATIVE_OPEN'}
    names.update(r['factory_segment']['plan'] for r in register['body_conductors'] if r.get('factory_segment'))
    plans={n:json.loads((OUT/n).read_text()) for n in names};files.update(OUT/n for n in names)
    ends,segments,groups=allocate(register,plans)
    result=dict(status='REMAINING25_SIXTY_SIX_ENDS_SHARED_ALLOCATION_NOT_MATERIAL_ACCEPTANCE',
        ends=ends,segments=segments,groups=groups,body_nets=25,physical_cuts=33,
        physical_ends=66,already_native_ends=3,new_candidate_saddle_groups=55,
        bank_binding=dict(preserve='12 purchased MTA0300330 holders/24 TE interfaces and current electrical roles',
            superseded_prints=['BankLeft','BankRight','Deck','Cover'],
            actual_current_holder_load_paths='OPEN: no native support inferred from holder reservation or old R47 stock',
            access='ATO extraction from installed assembly without routine WAGO disconnection; no independent old cover lift'),
        station_cases='Twelve D/G/P cases already have native low shoes rooted in actual P0/ Foundation. Reuse, do not duplicate.',
        source_cases='S0/S1/BAT/F0/F_PI/P_SYS/8 opposed joints require explicit current mechanical retention; wire lacing alone is not case mounting.',
        assembly=['No power: fit structural parents and cases before wire loads.',
                  'Prepare each factory/custom MTA pair as two cuts at its opposed221-2411 ports.',
                  'Fit bank inputs through the recorded Foundation passages before TE seating; support holder and crimp while fitting.',
                  'Lace equal-radius branch triplets separately from the larger incoming feed; do not bind levers.',
                  'Confirm installed ATO/tool access, then reverse this assembly for deep repair; no hot-swap requirement.'],
        open=['Simultaneous band/saddle/root material allocation with current36/19 and native13 source lands',
              'Current bank and source case M4 mounting, installed routine access',
              'Native changed parts/whole assembly/stock/final current selection'],
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in files},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
    (OUT/'remaining25-interface-allocation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('body_nets','physical_cuts','physical_ends','already_native_ends','new_candidate_saddle_groups','worker_seconds')}))


if __name__=='__main__':run()
