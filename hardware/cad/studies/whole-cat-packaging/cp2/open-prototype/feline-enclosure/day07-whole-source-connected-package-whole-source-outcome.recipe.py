from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,html,math,csv
from PIL import Image,ImageDraw
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rd=lambda n:json.loads((out/n).read_bytes())
names=['day07-WHOLE_SOURCE-receiver-anchored-returns-and-concentric-underbody-entry-proposal.json','day07-WHOLE_SOURCE-ninecore-connected-entry-first-gate.json','day07-WHOLE_SOURCE-ninecore-connected-entry-first-gate.breps.zip','day07-WHOLE_SOURCE-current-context-and-first-gap-view-data.json'];a=rd(names[0]);b=rd(names[1]);c=rd(names[3]);assert len(a['rows'])==9 and len(a['all12_portions'])==12 and len(a['physical_units'])==4 and b['first_falsifier']
with zipfile.ZipFile(out/names[2]) as z:
 assert z.testzip() is None;gg=json.loads(z.read('manifest.json'))['geometry']
 for q in gg:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
csvpath=out/'day07-WHOLE_SOURCE-twelve-physical-portions-conditional-debit.csv';assert not csvpath.exists()
with csvpath.open('w',encoding='utf8',newline='') as f:
 w=csv.writer(f);w.writerow(['wire','piece_id','physical_unit','passes_body','known_CONDITIONAL_components_mm','remaining_until850_before_unknown_path_mm','unknown_required_path','actual_installed_minimum_mm','actual_fit_mm','actual_cut_mm'])
 for q in a['all12_portions']:w.writerow([q['wire'],q['piece_id'],q['physical_unit'],q['passes_body_section'],q['known_conditional_component_mm'],q['remaining_before_850_project_mm'],q['unknown_actual_path'],'NULL','NULL','NULL'])
names.append(csvpath.name)
im=Image.new('RGB',(1600,1160),'white');dr=ImageDraw.Draw(im);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1160"><rect width="1600" height="1160" fill="white"/>']
def txt(x,y,t,col='#222'):
 dr.text((x,y),t,fill=col);svg.append(f'<text x="{x}" y="{y+13}" fill="{col}" font-family="sans-serif" font-size="13">{html.escape(t)}</text>')
def line(pts,col,width=2,dash=False):
 if len(pts)<2:return
 if dash:
  for i in range(0,len(pts)-1,2):dr.line(pts[i:i+2],fill=col,width=width)
 else:dr.line(pts,fill=col,width=width)
 svg.append('<polyline fill="none" stroke="'+col+'" stroke-width="'+str(width)+'"'+(' stroke-dasharray="5 4"' if dash else '')+' points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+'"/>')
txt(15,12,'WHOLE SOURCE: 9 IDs / 12 PHYSICAL PORTIONS / 4 MAX3 UNITS / ONE CONNECTED PROPOSAL / FIRST ENTRY ALLOCATION HOLD / N01 0/10')
txt(15,38,'BLUE D / ORANGE V / GREEN G. Solid paths proposed exact-R modules; DASHED links connectivity ONLY, NOT straight wire length or accepted free space.')
projectXY=lambda p:(18+(p[0]+165)*2.8,92+(105-p[1])*2.45)
projectXZ=lambda p:(18+(p[0]+165)*2.8,690+(110-p[2])*1.8)
for label,proj in [('XY whole interior and source passage',projectXY),('XZ levels + receiver-anchored returns',projectXZ)]:
 txt(18,65 if proj==projectXY else 663,label)
 for q in c['current_body_bounds']:
  bb=q['bounds_mm'];p=proj(bb[0]);Q=proj(bb[1]);rect=(min(p[0],Q[0]),min(p[1],Q[1]),max(p[0],Q[0]),max(p[1],Q[1]));col='#bf8e8e' if q['selected_FPI_unqualified_home_variable'] else '#ccc';dr.rectangle(rect,outline=col);svg.append(f'<rect x="{rect[0]:.2f}" y="{rect[1]:.2f}" width="{rect[2]-rect[0]:.2f}" height="{rect[3]-rect[1]:.2f}" fill="none" stroke="{col}"/>')
 for q in a['rows']:
  core=q['core'];col={'D':'#1764bc','V':'#cf8119','G':'#18864c'}[core];P=q['source_passage_P'];cx=q['XY_shared_centre'][0];R=q['XY_R_mm'];z=P[2];y=P[1];pts=[[P[0],77,z],P]+[[cx-R*math.cos(t),y-R*math.sin(t),z] for t in [i*math.pi/2/24 for i in range(25)]];r1=q['XZ_S_R1_mm'];r2=q['XZ_S_R2_mm'];yc=q['XY_Q'][1];zc=z-r1
  pts += [[cx+r1*math.sin(t),yc,zc+r1*math.cos(t)] for t in [i*math.pi/2/24 for i in range(1,25)]]
  c2=cx+r1+r2;pts += [[c2-r2*math.cos(t),yc,zc-r2*math.sin(t)] for t in [i*math.pi/2/24 for i in range(1,25)]];line([proj(p) for p in pts],col)
  Q=q['receiver_return_lower_port'];link=[q['post_S_end'],Q];line([proj(link[0]),proj([(link[0][k]+link[1][k])/2 for k in range(3)]),proj(link[1])],col,1,True)
  p=q['receiver_held9_end'];T=q['receiver_outward_T'];d=q['return_straights_mm'][0];R=35.1;upts=[p,[p[k]+d*T[k] for k in range(3)]]
  upts += [[p[k]+(d+R*math.sin(t))*T[k]-(R*(1-math.cos(t)) if k==2 else 0) for k in range(3)] for t in [i*math.pi/36 for i in range(1,37)]];upts.append(Q);line([proj(x) for x in upts],col)
txt(1010,80,'FIRST ACTUAL NAMED HAZARD: S0 BODY','#a92525')
txt(1010,104,'W005 fullallocated field gap1.137293 <1.25','#a92525');txt(1010,126,'Nominaljacket gap1.537293; validcommon0')
txt(1010,148,'Allocation reserve failure, NOT deliveredwirecontact.')
ox=1010
for q in c['sections']:
 col={'ACTUAL_RETAINED_S0_BODY':'#999','NEW_ENTRY_W005_FULL_CAPACITY':'#c22','NEW_ENTRY_W005_NOMINAL':'#1764bc'}[q['actor']]
 for curve in q['curves']:
  pts=[(ox+(x+140)*9,600-(z-30)*8) for x,z in curve]
  if pts and all(950<px<1590 and 170<py<640 for px,py in pts):line(pts,col,2)
txt(1010,628,'Actual XZ section / Y'+str(round(c['actual_local_section_Y_mm'],4)))
txt(1010,666,'PER-PHYSICAL DEBIT: CONDITIONAL ONLY')
for i,u in enumerate(a['physical_units']):
 mx=max(q['known_conditional_component_mm'] for q in u['core_rows']);txt(1010,691+i*42,u['unit']+' maxknown '+str(round(mx,3))+' mm');txt(1010,708+i*42,'unknownroute budget before850 >= '+str(round(850-mx,3)))
txt(1010,874,'All actualinstalled/fit/cut/slack NULL. MAX3 notSUM.')
for i,t in enumerate([
 'ONEwhole causal change: actualreceiver-anchoredreturns replacefloatingreservoirportals; common9concentricXYroll +pairedXZ-S, allR>=35.1.',
 'Actualcontext AABBs GREY orientation only; F_PIfull51x22x20.25 home RED isUNQUALIFIEDvariable/notdeleted or immutablemount. No contact from boxes.',
 'All9SOURCEIDs: FL1DVG/FL2DVG/FL3DVG;12physicalportions include originalFL3onlyatKnee+DONORbody. Sourceowned+8.5sidecar/3laps8/sleeves20/2x9retained.',
 'Newpacketentry first1of11/10UNRECEIVED HOLD atactualS0, fieldcommon0/jacketcommon0; doNOTresume10 or nudgeoneheight/radius/case.',
 'ReceiverUexact125.2..135.2 alreadyincludes55..65; eachFL2independentE=55+maxLi-Li. CurrentoutsideLi/delta<=10 NOTqualified. No sharedphi/trim20pool.',
 'FL1alsochooses55bodyexcess (extra45 overminimum10) charged in ownconditionalbudget, notuser/manufacturerrequirement. No actualwirefit/shortageclaim.',
 'D5OWNcontinuousclosure29/120technicalOPEN +F_R4casecapture/2fullstockGLOBALOPEN carry. Mainnewbody/legregionsR/Ankle/ground/stock/assembly remainOPEN.',
 'Consequence: constantheight foreturn reachesS0 allocatedshellbeforeverticaldrop. Need whole ENTRYLAYER/ORDER or realdifferentframepassage, notscalarretry.'
]):txt(15,945+i*24,t,'#a92525' if i in [3,7] else '#222')
png=out/'day07-WHOLE_SOURCE-connected-ninecore-first-entry-HOLD.png';assert not png.exists();im.save(png);svg.append('</svg>');png.with_suffix('.svg').write_bytes(('\n'.join(svg)+'\n').encode());names.extend([png.name,png.with_suffix('.svg').name])
for src in ['robot-cat92-whole-source-proposal.py','robot-cat92-whole9-entry-first-gate.py','robot-cat92-save-whole-source-context-and-view.py','robot-cat92-package-whole-source-outcome.py']:
 n='day07-whole-source-connected-'+src.removeprefix('robot-cat92-').removesuffix('.py')+'.recipe.py';assert not(out/n).exists();(out/n).write_bytes((temp/src).read_bytes());names.append(n)
nextstep='WHOLE_SOURCE_ENTRY_LAYER_ORDER_BEFORE_FORETURN: ONEwhole9receiveranchoredverticalreturns+concentricXYpacket/pairedXZ-S plan saved/all9rows12portions4MAX3/conditionalcomponentguides+unknownmoving/packing/Li explicit. FIRSTnewwholepacketentryW005 vsactualS0body allocatedgap1.137293<125/commonVALID0; namednominalr1.55gap1.537293/commonVALID0=>allocationreserveHOLD NOTwirecontact/shortage/all3Dspace. 1of11/10UNRECEIVED frozen/no resume. Constantheightfirstforeturn passesactualS0lowerbodylayer BEFORE the designedverticaldrop; need WHOLEentrylayer/order or actualdifferentretainedP0passage for full9/R35/packing/sourceground, notonewireheight/caseoffset/shorterR/55waiver/thirdlocalcurve. ReceiveranchoredUports/underbodyDGVlinks areproposednotaccepted. Allnewconditionalknowncomponentlengths incl12physicalrows areNOTactualminimum/fit/physicalshortage; actualsource14/holder+8.5/FL3properlap4/terminal11/full9/G15WITHINreturnonce/source3x8/3x20/stagger2x9/factoryplug/MAX3/850+900ceil5min+20/actualcutNULL retained. ActualmovingKnee6/Hip3+Ankle/ground andLi perpose/independentdeltaLi<=10forE55..65/usable55EACHFL2 remainOPEN. D1W002BUSW003mate/D5W007bothends/G1W025/four220/both4MTA preserved. No newmaterial/motionmatrix/oldfieldreplay/newreview. D5ownclosureface29technical/F_R4caseholding2stockGLOBALOPEN carry, no newlocalbankCAD. Currentbase1292effective1311 unchanged/G4D5PROPOSED/all123246N010.'
tim=[dict(receipt=names[1],operation_seconds=b['operation_seconds'],process_cpu_seconds=b['process_cpu_seconds']),dict(receipt=names[3],operation_seconds=c['operation_seconds'],process_cpu_seconds=c['process_cpu_seconds'])]
r=dict(id='day07-WHOLE_SOURCE-connected-ninecore-first-entry-bounded-disposition',status='ONE_WHOLE_SOURCE9_RECEIVER_ANCHORED_RESERVE_AND_ENTRY_PLAN_FIRST_ALLOCATED_S0_CLEARANCE_HOLD',selected=False,N01_complete=False,whole_proposal=names[0],whole_proposal_sha256=sha(out/names[0]),all9_plan_rows=a['rows'],all12_physical_debits=a['all12_portions'],all4_physical_MAX3=a['physical_units'],known_lengths_strict_scope='Exact lengths of PROPOSED component curves ONLY; conditional wholelinks not packed/cleared, movingpath absent. Neither routedminimum nor acceptedfeasibleupper/installedcut/slack/physicalshortage. Chordsketches NOTcountedasroutedlength.',first_falsifier=b['first_falsifier'],first_nominal_gap_mm=c['first_nominal_jacket_gap_mm'],received=b['cursor'],total=b['total'],unreceived=b['unreceived'],profile_quality=b['all9_profiles'],proposed_current_effectivity=b['proposed_effectivity'],source21_rest108_actual_identity=[b['source21_current_identity'],b['rest108_current_identity']],temporary4_scope=b['temporary4_source_assembly_fields'],all_source_functions_and_old_negatives_preserved=True,no_new_material_or_second_family=True,local_D5_and_bank_global_OPEN_carried=True,actual_A_U_fit_slack=None,actualcut=None,next=nextstep,timings=tim,measured_native_wall_seconds=sum(q['operation_seconds'] for q in tim),measured_native_CPU_seconds=sum(q['process_cpu_seconds'] for q in tim),view=dict(path=png.name,sha256=sha(png),actual_local_sections=True,whole_proposal_not_measured_geometry=True,visually_inspected=False),source_pins=a['source_pins']+[dict(path='day07-SOURCE-body-approach-proposed-moving-context.json',sha256=sha(out/'day07-SOURCE-body-approach-proposed-moving-context.json'))],packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=[dict(path=names[2],crc_ok=True,member_sha_verified=len(gg))],native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False,idle_prompt_received_utc=None),bounded_start_utc='2026-11-07T20:43:06Z',authorized_deadline_utc='2026-11-07T22:11:33Z',partial_final_not_windowclose=True,written_utc=datetime.now(timezone.utc).isoformat());p=out/(r['id']+'.json');assert not p.exists();p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());print(p.name,sha(p),'members',len(gg),'view',str(png))
