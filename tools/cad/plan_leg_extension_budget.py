"""Current endpoints and real cable blanks BEFORE selecting any extension.

Lower bounds are not routed lengths or a shopping list. A splice cannot be
invented on the short RL3 body tail or on a free joint flex. A full900mm
donor at one long SOURCE-OWNED straight land is the shared candidate.
"""
import hashlib,json,math,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    tick=time.monotonic();fp=OUT/'leg-source-near-member-plan.json';df=OUT/'current-leg-receiver-datums.json'
    ef=OUT/'harness-interfaces-plan.json';facts=ROOT/'hardware/reference/leg-cable-2026-10-04/facts.json'
    family,datums,ends,supplier=[json.loads(f.read_text()) for f in (fp,df,ef,facts)]
    assert supplier['manufacturer_nominal_length_mm']==900 and supplier['factory_cables_per_pack']==6
    body={r['id']:r for r in ends['body_conductors']};rows=[];joins=[]
    for route in family['routes']:
        name=route['loom'];root=next(r for r in family['hips'] if r['loom']==name)['fixed_anchor_world_mm']
        remaining=850-route['guide_to_body_grip_mm'];cores=[]
        for core,entry in route['source']['electrical'].items():
            role=entry['body_end'];wire=entry['wire']
            end=datums['ports'][role] if role in datums['ports'] else next(e for e in body[wire]['current_ends'] if e['role']==role)
            # The9mm receiving straight and stripped insertion are explicit
            # lower-bound bookkeeping, not a curved full fanout.
            point=end['point_mm'];axis=end['departure'];land=[x+9*u for x,u in zip(point,axis)]
            insertion=body[wire].get('insertion_strip_max_mm',11)
            geometric_lower=math.dist(root,land)+9
            cores.append(dict(core=core,wire=wire,role=role,point_mm=point,departure=axis,
                route_lower_bound_mm=geometric_lower,terminal_allowance_project_mm=insertion,
                unextended_budget_after_lower_bound_mm=remaining-geometric_lower-insertion))
        row=dict(loom=name,guide_to_body_grip_mm=route['guide_to_body_grip_mm'],
            project_usable_factory_mm=850,remaining_after_guide_mm=remaining,body_cores=cores,
            unextended_lower_bound_fits=all(c['unextended_budget_after_lower_bound_mm']>=0 for c in cores))
        if name.endswith('3'):
            # Reverse stored root->socket parts: this length is measured from
            # the real socket's outer reservation, NOT from an old flex end.
            source=list(reversed(route['source_parts']));straight=max((q for q in source if q['kind']=='line'),key=lambda q:q['length_mm'])
            index=source.index(straight);prefix=sum(q['length_mm'] for q in source[:index])+straight['length_mm']/2
            centre=[(a+b)/2 for a,b in zip(straight['start'],straight['end'])]
            # Stagger the three individually insulated joints longitudinally.
            # Three20mm sleeves at22mm pitch occupy64mm, plus two2mm gaps
            # and two9mm jacket lands =86mm, all on this source-owned line.
            # This is a cut/space candidate, not supplier insulation data.
            offsets=(-22,0,22);required=86
            assert straight['length_mm']>=required
            axis=[(a-b)/straight['length_mm'] for a,b in zip(straight['start'],straight['end'])]
            primary_blank=math.ceil((prefix+max(offsets)+14+4+20)/5)*5
            donor_guide_to_root=route['guide_to_body_grip_mm']-prefix
            core_capacity=850-donor_guide_to_root-4
            join=dict(loom=name,owner=route['source']['moving_saved_stage'],centre_world_mm=centre,
                straight_available_mm=straight['length_mm'],source_to_join_guide_mm=prefix,
                original_factory_blank_project_mm=primary_blank,real_donor_sku=supplier['manufacturer_part'],
                donor_nominal_mm=900,donor_usable_project_mm=850,donor_guide_to_body_root_mm=donor_guide_to_root,
                body_core_capacity_before_terminal_mm=core_capacity,three_eight_mm_laps=3,
                individual_insulation_sleeves=3,sleeve_length_project_mm=20,independent_nine_mm_lands=2,
                sleeve_centre_pitch_project_mm=22,sleeve_zone_project_mm=64,
                required_straight_total_project_mm=required,source_owned_not_free_flex=True,
                independent_land_centres_world_mm=[[c+sign*38.5*u for c,u in zip(centre,axis)] for sign in (-1,1)],
                holder_and_material_qualified=False,splice_geometry_not_yet_added_to_material_gate=True)
            schedule=[]
            for c,offset in zip(cores,offsets):
                capacity=core_capacity+offset
                c['donor_budget_after_lower_bound_mm']=capacity-c['route_lower_bound_mm']-c['terminal_allowance_project_mm']
                schedule.append(dict(core=c['core'],wire=c['wire'],source_to_joint_guide_mm=prefix+offset,
                    joint_centre_world_mm=[v+offset*u for v,u in zip(centre,axis)],
                    original_core_cut_from_plug_face_project_mm=prefix+offset+14+4,
                    donor_core_capacity_before_terminal_mm=capacity))
            join['staggered_core_schedule']=schedule
            assert all(c['donor_budget_after_lower_bound_mm']>0 for c in cores)
            row['extension_candidate']=join;joins.append(join)
        rows.append(row)
    report=dict(status='CURRENT_36_ENDS_CABLE_EXTENSION_LOWER_BOUNDS_ONLY',rows=rows,
        four_source_owned_extension_candidates=joins,selected=False,W5_complete=False,physical_pass=False,
        candidate_stock=dict(sku=supplier['manufacturer_part'],packs=3,cables_per_pack=6,total_cables=18,
            original_source_plugs=12,whole_900mm_donors=4,whole_cables_spare=2,
            source3_trim_offcuts_not_counted_as_spare=True,additional_sleeves=12,
            sleeve_total_project_mm=240,source_join_independent_lands=8),
        rejected='A static splice20mm above RL3 bodyroot cannot be promised with15.16mm remaining. No imaginary longer900mm source or join on dynamic flex.',
        open=['All36actualbodyfanout lengths, bends, sources and independent support roots',
            'Four source-owned splice holders,12insulatedlaps,8independentlands and changed motion gate',
            'Delivered usable lead length/pin cavity mapping/Cu/OD/flex rating/TE and WAGO termination compatibility',
            'Sleeve SKU/expanded/recovered OD selected only after real insulation data; no guessed supplier dimensions',
            'Three packs are a candidate only, not selected stock or an authorized purchase'],
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (fp,df,ef,facts,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'leg-extension-budget-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],unextended_fail=[r['loom'] for r in rows if not r['unextended_lower_bound_fits']],
        joins=[dict(loom=j['loom'],prefix=round(j['source_to_join_guide_mm'],2),body_capacity=round(j['body_core_capacity_before_terminal_mm'],2)) for j in joins],worker_seconds=report['worker_seconds'])))


if __name__=='__main__':run()
