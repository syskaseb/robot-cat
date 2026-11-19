from common import *
q=rd(P/'whole-termination-plan.json');units=q['units'];l=rd(P/'lower-unit-lengths.json')['rows']
b=rd(P/'changed-branch-lays.json')['rows'];b.update(rd(P/'fl-hand-space.json'))
bulk={}
for n,r in l.items():
 if n=='pack' or n=='W060':continue
 bulk[n]=dict(parent=r['own_unit'],sku_and_color=r['material'],project_blank_mm=r['project_blank_mm'],ends_once=r['end_mm'],dress=r['dress'])
for n,v in b.items():
 r=max(v,key=lambda p:p['planned_blank_mm']);bulk[n]=dict(parent=n,sku_and_color=r['material'],project_blank_mm=None if n.endswith('factory') else r['planned_blank_mm'],project_reach_including_ends_mm=round(r['developed']+r['ends_outside_lay_mm'],2),physical_measured=None)
for r in units['ToF']:bulk[r['wire']]=dict(parent=r['wire'],sku_and_color=str(r['sku'])+' '+r['color'],project_blank_mm=r['planned'],ends_once=r['ends_once'])
totals={}
for r in bulk.values():
 if r['project_blank_mm'] is not None:
    k=r['sku_and_color'];totals[k]=totals.get(k,0)+r['project_blank_mm']
legs=rd(H19/'leg-mouths.json');legs[0]['centre']=[-51,-102,93]
service=rd(F/'service-lay.json');stock={k:{n:q[n] for n in ['unit','owner','stock','free','ends_and_free','analytic_lengths','centre_radius','inner_R'] if n in q} for k,q in service['fixed'].items()}
wr('source-units.json',dict(graph_rows=160,selected_rows=57,additions=7,unchanged_units=units,MG_JR_pairs=q['JR'],fixed_factory_routes=stock,changed_and_ToF_bulk_by_independent_parent=bulk,subtotal_of_these_project_blanks_by_stock=totals,available_bulk_length=None,other_connections='whole-termination-plan.json and source/MATERIALY.csv; no pooling between physical parents',leg_openings=legs,FFC='190 free + 10 both ends = 200',battery='each delivered pigtail must reach from its own pack exit, through a 125.72 mm allocated lower passage and 82.41 mm accessible upper service loop; delivered ends additional per sample',FHAC='5 full holders; original FHAC lead 84.5–94.5 incl bare end, P_REAR–F_AUX and P_SYS–F_PI pairs intact',MTA='4 separately purchased unknown full units, each two body-side leads; compare F_FL.in and F_FL.out separately, do not credit a hypothetical 140 mm per lead.',USB_AUDIO='independent USB-A/C data unit; measure delivered usable length and two simultaneous Pi boots',R7_windows='12+50+196+25+9+8=300; each spool end/sleeve accounted only once',actual_cut_fit_slack=None))
