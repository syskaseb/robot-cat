from common import *
d=rd(H19/'whole-termination-plan.json');rr={r['wire']:r for r in d['wires']};assert len(rr)==160
g=rd(P/'lower-unit-lengths.json');gg=rd(P/'lower-approaches.json');bl=rd(P/'changed-branch-lays.json');bk=rd(P/'fl-hand-space.json')
d['endpoints'].update(g['endpoints']);d['endpoints'].update(bl['endpoints']);regions=rd(P/'fl-region.json')
for k,q in gg.items():
 if k.startswith('pack'):continue
 p=q['points'];s=g['rows'][k];rr[k].update(regional_transport_mm=s['developed'],length_to_station_faces_mm=s['developed'],shared_approach=p[::25]+[p[-1]],jacket_or_section_mm=q['diameter'],project_stock=s['project_blank_mm'],termination_mm=s['end_mm'],dressing_mm=s['dress'],source_unit=s['own_unit'],allocation='two-tier deck, G1 upper shelf; actual wire mouth and typed ends')
for k,l in bl['rows'].items():
 q=bk.get(k,l)[0];p=q['points'];r=rr[k];r.update(regional_transport_mm=q['developed'],length_to_station_faces_mm=q['developed'],shared_approach=p[::25]+[p[-1]],jacket_or_section_mm=q['diameter'],section_basis='project packing - measure MTA tails' if k.endswith('factory') else 'source jacket',material_role=q['material'],termination_mm=q['ends_outside_lay_mm'],dressing_mm=q['project_dress'],project_blank_mm=q['planned_blank_mm'],minimum_inner_R=q['minimum_centre_radius']-q['diameter']/2,allocation='P_AUX lower shelf / two independent levels of open FL inline rack')
 if k.startswith('W0'):r['connected_fl_bay']=regions[k]
 if k.endswith('factory'):r.update(project_blank_mm=None,delivered_length_mm=None,minimum_required_for_lay_mm=q['developed']+q['ends_outside_lay_mm'],actual_cut_fit_slack=None)
 if len(l)>1:r['stock_variants']=[dict(FHAC_factory_mm=x['stock_mm'],extension_transport_mm=x['developed'],extension_blank_mm=x['planned_blank_mm']) for x in l]
h=rd(P/'shared-fuse-transfer.json')['routes'];d['FHAC']['F_HP.in'].update(minimum_lay=h[0]['points'],end_or_overlap=h[0]['end_or_overlap'],variants=h)
pu=rd(P/'remote-pulldown-lay.json')
for role,q in d['JR'].items():
 q.update(first_static_mm=50,remaining_transport_and_reserve_mm=196,local_tap=dict(method='PROPOSED_CONDITIONAL continuous JR, PWM and GND insulated window taps; both factory crimps preserved',centres=[15,35],grips=[5,45],guide='ELECTRICAL_ASSEMBLY.md'),poses=(pu['stations'] if role=='pitch' else pu['fixed'][role]))
d['units']['K1474'].update(W060_separate_black_allowance=300,W060_required=g['rows']['W060']['project_blank_mm'],gross_parent_debits_per_core_mm=[460,558])
a=d['units']['battery'];a.pop('W001_remaining_obstacle',None);bb=g['rows']['pack'];a.update(pack_approach={k:round(bb[k+'_mm'],3) for k in ['-1','1']},minimum_pack_jacket_to_mate_excluding_delivered_end_mm={k:round(bb[k+'_mm']+82.4070751,3) for k in ['-1','1']},park_head_yaw_deg=0,terminal_grip='both plug shells; lower F0 W075 and BAT.minus/W001 before installed plug')
d['physical_checks']=[d['H19_terminal_limitations'][0],d['H19_terminal_limitations'][-1],'Full MTA0100335 geometry and both independent tail lengths. Fit largest keyed leg end before closure.','Delivered USB overmolds, mic audio cable length, cooler and acoustic openings, pack leads / extraction; G-Tech cavity identity before energising.','R7/R8/R9 insulation, measured joint section and strain relief per electrical guide.']
d.pop('H19_terminal_limitations');d['shared_region_update']='For changed stations the row-specific allocated approaches supersede 19H group spines. Fit before covers. Actual cuts and stock slack unmeasured.'
p=rd(P/'W075-seated.json');a['F0_lead_with_termination']=round(p['project_free_mm']+p['source_end_debit'],2)
rr['W075'].update(shared_approach=p['points'][::-20],regional_transport_mm=p['project_free_mm'],length_to_station_faces_mm=p['project_free_mm'],termination_mm=5,source_unit='W075_continuous',maximum_mm=50,jacket_or_section_mm=4.8,achieved_inner_radius_mm=p['achieved_inner_radius'],section_basis='4.8 mm project jacket, final axial entry under installed XT60; measure supplied part')
wr('whole-termination-plan.json',d)
