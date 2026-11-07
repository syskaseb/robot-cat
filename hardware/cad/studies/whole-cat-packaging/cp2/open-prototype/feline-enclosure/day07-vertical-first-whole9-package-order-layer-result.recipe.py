from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,html,math,csv
from PIL import Image,ImageDraw
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rd=lambda n:json.loads((out/n).read_bytes())
names=['day07-WHOLE9-before-S0-current-vertical-entry-space-read.json','day07-WHOLE9-north-entry-vertical-before-foreturn-whole-plan.json','day07-WHOLE9-vertical-before-S0-order-first-gate.json','day07-WHOLE9-vertical-before-S0-order-first-gate.breps.zip','day07-WHOLE9-conditional-Hip3-source850-necessary-material-bound.json','day07-WHOLE9-new-order-first-bought-case-nominal-and-ground.json','day07-WHOLE9-new-order-W037-named-local-hazard.breps.zip','day07-WHOLE9-entry-layer-cause-W037-source-binding-and-necessary-window.json','day07-WHOLE9-new-order-current-bought-case-context-and-actual-section.json'];a=rd(names[1]);b=rd(names[2]);bound=rd(names[4]);c=rd(names[5]);cause=rd(names[7]);v=rd(names[8]);assert c['S0_received']==9 and c['actual_contour_all_zero'] and c['nominal_LOCAL_valid_common_mm3']==0
checks=[]
for n in names:
 if n.endswith('.zip'):
  with zipfile.ZipFile(out/n) as z:
   assert z.testzip() is None;gg=json.loads(z.read('manifest.json'))['geometry']
   for q in gg:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
   checks.append(dict(path=n,crc_ok=True,member_sha_verified=len(gg)))
csvp=out/'day07-WHOLE9-before-foreturn-twelve-physical-conditional-debits.csv';assert not csvp.exists()
with csvp.open('w',encoding='utf8',newline='') as f:
 w=csv.writer(f);w.writerow(['wire','physical_unit','piece_id','known_CONDITIONAL_component_mm','remaining_before850_UNKNOWNapproach_mm','actual_minimum','actualfit','actualcut']);
 for q in a['all12_portions']:w.writerow([q['wire'],q['physical_unit'],q['piece_id'],q['known_conditional_component_mm'],q['remaining_before_850_project_mm'],'NULL','NULL','NULL'])
names.append(csvp.name);oldview=rd('day07-WHOLE_SOURCE-current-context-and-first-gap-view-data.json');ctx=oldview['current_body_bounds']+v['bought_case_bounds']
im=Image.new('RGB',(1600,1400),'white');dr=ImageDraw.Draw(im);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1400"><rect width="1600" height="1400" fill="white"/>']
def txt(x,y,t,col='#222'):
 dr.text((x,y),t,fill=col);svg.append(f'<text x="{x}" y="{y+13}" fill="{col}" font-family="sans-serif" font-size="13">{html.escape(t)}</text>')
def line(pts,col,width=2,dash=False):
 if len(pts)<2:return
 for p0,p1 in zip(pts,pts[1:]):
  if dash:
   N=max(2,int(math.dist(p0,p1)/5))
   for j in range(0,N,2):dr.line([(p0[0]+(p1[0]-p0[0])*k/N,p0[1]+(p1[1]-p0[1])*k/N) for k in [j,min(j+1,N)]],fill=col,width=width)
  else:dr.line([p0,p1],fill=col,width=width)
 svg.append('<polyline fill="none" stroke="'+col+'" stroke-width="'+str(width)+'"'+(' stroke-dasharray="5 4"' if dash else '')+' points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+'"/>')
txt(15,12,'WHOLE9 VERTICAL BEFORE FORETURN / S0 ALL9 + ACTUAL SKIN + BODY GROUND SCOPED CLEAR / W037 BOUGHT CASE CLEARANCE HOLD / N01 0/10')
txt(15,38,'BLUE D / ORANGE V / GREEN G. Wholeentry phase order changed, no parts/height nudge. Dashed links are UNQUALIFIEDconnectivity, not wirelength.')
XY=lambda p:(18+(p[0]+165)*2.8,92+(105-p[1])*2.45);XZ=lambda p:(18+(p[0]+165)*2.8,690+(110-p[2])*1.8)
for label,proj in [('XY currentbody + whole9 proposedregions',XY),('XZ early wholepacket descent before S0foreturn',XZ)]:
 txt(18,65 if proj==XY else 663,label)
 for q in ctx:
  lo,hi=q['bounds_mm'];P=proj(lo);Q=proj(hi);col='#b97777' if q.get('selected_FPI_unqualified_home_variable') else '#bcbcbc';box=[min(P[0],Q[0]),min(P[1],Q[1]),max(P[0],Q[0]),max(P[1],Q[1])];dr.rectangle(box,outline=col);svg.append(f'<rect x="{box[0]:.2f}" y="{box[1]:.2f}" width="{box[2]-box[0]:.2f}" height="{box[3]-box[1]:.2f}" fill="none" stroke="{col}"/>')
 for q in a['rows']:
  col={'D':'#1764bc','V':'#cf8119','G':'#18864c'}[q['core']];x,y,z=q['source_passage_P'];r1=q['XZ_S_R1_mm'];r2=q['XZ_S_R2_mm'];zc=5.6;yy=y-r1-r2;zl=zc-r2;cx=-94.9;rr=q['XY_R_mm'];angs=[i*math.pi/2/24 for i in range(25)];pts=[[x,y-r1*math.sin(t),zc+r1*math.cos(t)] for t in angs];pts += [[x,yy+r2*math.cos(t),zc-r2*math.sin(t)] for t in angs[1:]];pts += [[cx-rr*math.cos(t),yy-rr*math.sin(t),zl] for t in angs[1:]];line([proj(p) for p in pts],col)
  P=q['post_S_end'];Q=q['receiver_return_lower_port'];line([proj(P),proj(Q)],col,1,True);p=q['receiver_held9_end'];T=q['receiver_outward_T'];d=q['return_straights_mm'][0];R=35.1;up=[p,[p[k]+d*T[k] for k in range(3)]]+[[p[k]+(d+R*math.sin(t))*T[k]-(R*(1-math.cos(t)) if k==2 else 0) for k in range(3)] for t in [i*math.pi/36 for i in range(1,37)]]+[Q];line([proj(p) for p in up],col)
leg=rd('day07-whole-physical-SOURCE-approach-Knee-link-proposal.json');holder=a['current_moving_holder']
for q in a['rows']:
 i=q['row'];P=leg['source_origins'][i]['source_outer_reservation_world_mm'] if i<2 else holder['current_EXIT'];Q=q['source_passage_P'];col={'D':'#1764bc','V':'#cf8119','G':'#18864c'}[q['core']]
 for proj in [XY,XZ]:line([proj(P),proj(Q)],col,1,True)
for proj in [XY,XZ]:line([proj(leg['source_origins'][2]['source_outer_reservation_world_mm']),proj(holder['current_ENTRY'])],'#8d5ca6',1,True);line([proj(holder['current_ENTRY']),proj(holder['current_EXIT'])],'#8d5ca6',2)
txt(1010,80,'S0 ALL9 min gap '+str(round(c['S0_min_actual_fullfield_gap_mm'],6)))
txt(1010,103,'ActualBodyOuter 27/27 offset-cover checks0outside')
txt(1010,126,'Worstfrozenbodydrop groundlower '+str(round(c['bodyfixed_ground']['worst_required36_ground_lower_mm'],6)))
txt(1010,165,'NEW FIRST BOUGHT W037 CASE HOLD','#a92525');txt(1010,188,'Fullfieldcommon0.003572 / nominalgap0.326332','#a92525');txt(1010,210,'Nominalcommon0: clearancefailure, NOT contact.')
for q in v['sections']:
 col={'CURRENT_BOUGHT_W037_CASE':'#999','NEW_W006_ALLOCATED_FIELD':'#c22','ONLY_NAMED_NOMINAL_QUARTER':'#1764bc'}[q['actor']]
 for cv in q['curves_XY']:
  pts=[(1010+(x+132)*12,600-(y+24)*16) for x,y in cv]
  if pts and all(970<px<1590 and 240<py<640 for px,py in pts):line(pts,col)
txt(1010,662,'SOURCE/FL1 W020: CONDITIONAL850PROJECT FAIL','#a92525')
txt(1010,687,'Bodycomponents749.997 + necessaryfreeHip121.652')
txt(1010,711,'=871.649 >850. Lowerfitbound895 <=900.')
txt(1010,735,'Notphysical900shortage/notglobalroutedminimum.')
txt(1010,759,'OptionalHip55U isownerchoice; Hip10 needsWHOLE')
txt(1010,782,'differentdirectreceiver topology, notsubtract45.')
txt(1010,823,'W037factory MTA0100335 + customHELU23802')
txt(1010,847,'35.5x8.1x8.9 actualcase kept/full220/bothends.')
txt(1010,891,'Currentpairs243/474,231UNRECEIVED. No resume.')
txt(1010,915,'NecessarywholehighestrowZwindow -36.2..-33.15')
txt(1010,938,'NOTemptybayproof/newapprovedheight/newfamily.')
for i,t in enumerate([
 'WHOLEORDER: entryfromactualY77 boundary, concentricYZ-Sfirst(R35.1..41.7), THEN XYforeturn atLOWrows; all9packing retained/noold37.75line debit.',
 'ActualS0causeclosedscoped9/9,min30.368370. Complete9capacity3.25actualcontour27/27 +worstbody-ground35.477349. ExternalmovingKnee/HipstillOPEN.',
 'FIRSTnewlowerforeturn W006 vsretainedboughtW037: fieldcommon.003572/nominalgap.326332<1.25/common0. NOcornertrim/marginwaiver/caseoffset.',
 'Bodyheight/order change nowneedsactualwholeW037factory/custom+bothstrains/fullstock/entrylayer decision; 231unreceived frozen, no secondfamily.',
 'Independentmaterialbound rejectsONLYspecifiedoptionalHip55bodycurves+Y77/-Y/R35completion under850PROJECT. Notactualminimum/cut/global900shortage.',
 'ALL9IDs12portions4MAX3 originalFL3+DONOR, current+8.5joint/3laps8/sleeves20/stagger2x9/source14terminal11/full9properprefixonce retained.',
 'FL2required55each/independentLi-delta<=10IF55..65 remainOPEN; U125.2alreadyincludes55. Hipminimum10notwaived; extraHip45isnotimmutable.',
 'Greycurrentbounds anddashedmoving/transportlinks orientONLY, notclearance/routes. FPIunqualifiedfullcase remainsvisible/notdeleted. No newmaterial.',
 'D5OWNclosure29/120technical +F_R4casecapture2stockGLOBALOPEN carried; base1292/effective1311unchanged; alloldcounters/parts/four220/both4MTA/N010.'
]):txt(15,1140+i*25,t,'#a92525' if i in [2,4] else '#222')
png=out/'day07-WHOLE9-vertical-first-S0-closed-W037-HOLD.png';assert not png.exists();im.save(png);svg.append('</svg>');png.with_suffix('.svg').write_bytes(('\n'.join(svg)+'\n').encode());names.extend([png.name,png.with_suffix('.svg').name])
for src in ['robot-cat93-current-vertical-entry-space-read.py','robot-cat93-save-whole-entry-order-plan.py','robot-cat93-whole9-before-S0-first-gate.py','robot-cat93-conditional-Hip3-material-bound.py','robot-cat93-save-first-bought-case-and-ground.py','robot-cat93-entry-cause-and-source-case-binding.py','robot-cat93-save-bought-context-and-local-section.py','robot-cat93-package-order-layer-result.py']:
 n='day07-vertical-first-whole9-'+src.removeprefix('robot-cat93-').removesuffix('.py')+'.recipe.py';assert not(out/n).exists();(out/n).write_bytes((temp/src).read_bytes());names.append(n)
nextstep='WHOLE_ENTRY_LAYER_PLUS_BOUGHT_W037_AND_APPROPRIATE_HIP3_DIRECT_RECEIVER_TOPOLOGY: SAMEwhole9 nowYZverticalSdropBEFOREforeXY fromactualY77/Xcolumns. ActualS0ALL9min30.368370/CLOSEDscope, 27actualBodyOuter3.25offsetpieces0outside, worstrequired36bodydropfloor35.477349; no old9entry/source/matrixreplay. FIRSTNEWlowXYW006/caseCarrier:bought:W037:case VALIDallocatedcommon.003572, nominalLOCALquartergap.326332<125/common0; realclearanceHOLDnotdeliveredcontact. 243of474currentpairs/231UNRECEIVED frozen/no resume/secondfamily. W037factoryMTA0100335supplied4mm2 +HELU23802custom/full35.5x8.1x8.9boughtcase/bothends/full220/root/stock mustremain; no onecaseoffset/cornertrim/waiver. Need WHOLEavailablebodyentrylayer+carrier/sourceunit/coallocation order. Necessaryglobalcase/floor highestrowZwindow[-36.2,-33.15] isNOTfree-space/approvedheight; newwholeconcentricS Rsum/packing/connectedtransport/contour/currentparts wouldneedproof, no scalarnudge. Independentselected-bodycompletion bound: SOURCEFL1W020 knownconditionalbody749.997 +necessary3DfreeHip121.652=871.649>850PROJECT; fitLOWERbound895 doesNOTprove900shortage/actualfit/minimum. ThisrejectsONLYspecifiedconditionalbodycurves+Y77/-Y/R35family withunnecessaryownerHip55U. ChooseONEwholeappropriateHip10/directreceiver approach (lowerUportsareprojectchoices), notblindsubtract45, preservingmandatoryFL2each55/R35/perphysical850900MAX3. NewactualmovingKnee6/Hip3/Ankle/ground/Li perpose/independentdeltaLi<=10for55..65/all12source+donor actualfitslack remainNULL. Keep source14terminal11full9properprefixONCE/FL2NOlap4/FL3properjoint/3laps8/sleeves20/stagger2x9/factoryplug/four220/both4MTA. D5ownclosure29/120/F_R4capture2stockGLOBALOPEN carry; no localmount/V3/FPI/storagedetail/newreview. Currentbase1292effective1311/alloldcounts/123246N010 unchanged.'
tim=[dict(receipt=n,operation_seconds=q['operation_seconds'],process_cpu_seconds=q['process_cpu_seconds']) for n,q in [(names[0],rd(names[0])),(names[2],b),(names[5],c),(names[8],v)]]
r=dict(id='day07-WHOLE9-vertical-before-foreturn-layer-order-bounded-disposition',status='WHOLE9_S0_CLEARANCE_CONTOUR_BODYGROUND_CLOSED_SCOPED_NEW_W037_CLEARANCE_HOLD_CONDITIONAL_HIP850_PLAN_FAIL',selected=False,N01_complete=False,whole_proposal=names[1],whole_proposal_sha256=sha(out/names[1]),all9_rows=a['rows'],all12_physical_debits=a['all12_portions'],physical4_MAX3=a['physical_units'],S0_closed=dict(count=9,min_actual_fullfield_gap_mm=c['S0_min_actual_fullfield_gap_mm']),actual_BodyOuter27=dict(rows=b['actual_contour_rows'],all_zero=True),bodyfixed_required36_ground=c['bodyfixed_ground'],first_new_W037=b['first_falsifier'],nominal_local_gap_mm=c['nominal_LOCAL_gap_mm'],nominal_local_common_mm3=c['nominal_LOCAL_valid_common_mm3'],current_pairs_received=c['current_other_pairs_received'],current_pairs_total=c['total_current_candidates'],current_pairs_unreceived=c['remaining_unreceived'],whole_entry_and_new_motion_NOT_selected=True,W037_physical_binding=cause['W037_source_physical_roles'],necessary_packet_window=cause['necessary_new_whole_packet_layer_window'],conditional_Hip850=bound,conditional_bound_scope='Onlyspecifiedbodycurvesandchosenprojectsource14bundle-reference/Y77/-Y/R35family. No manufacturerpin/cavityendpoint orphysicalcut claimed; no globalshortage. Movingpaths/sourcecurveactualminimum remainNULL.',all_actual_A_U_fit_slack_and_cut_NULL=True,no_newmaterial_secondfamily_or_case_scalar=True,all_old_negative_counts_sourceparts_and_globalOPEN_preserved=True,next=nextstep,timings=tim,measured_native_wall_seconds=sum(q['operation_seconds'] for q in tim),measured_native_CPU_seconds=sum(q['process_cpu_seconds'] for q in tim),view=dict(path=png.name,sha256=sha(png),actual_local_sections=True,whole_plan_not_measured_acceptance=True,visually_inspected=False),source_pins=a['source_pins']+[dict(path='n01-selected-piece-profile-contract.json',sha256=sha(out/'n01-selected-piece-profile-contract.json'))],packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=checks,native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False,idle_prompt_received_utc=None),bounded_start_utc='2026-11-07T21:10:09Z',authorized_deadline_utc='2026-11-07T22:11:33Z',partial_final_not_windowclose=True,written_utc=datetime.now(timezone.utc).isoformat());p=out/(r['id']+'.json');assert not p.exists();p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());print(p.name,sha(p),'pins',len(r['packet_pins']),'members',sum(q['member_sha_verified'] for q in checks),'view',str(png))
