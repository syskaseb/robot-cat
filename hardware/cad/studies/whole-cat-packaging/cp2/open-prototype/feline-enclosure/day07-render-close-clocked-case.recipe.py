from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,html,os
from PIL import Image,ImageDraw,ImageFont
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pn='day07-FPI-W068-whole-clocked-case-layer-proposal.json';gn='day07-FPI-whole-clocked-case-first-preflight.json';sn='day07-FPI-clocked-case-supported-housing-source-witness.json';pr,g,s=[json.loads((out/n).read_bytes()) for n in [pn,gn,sn]];assert s['common_valid'] and s['full_case_allocation_common_mm3']>250
viewsec=json.loads((out/'day07-FPI-clocked-case-full-source-section.json').read_bytes())
im=Image.new('RGB',(1460,1050),'#f7f8fa');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);sm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);bd=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24);sv=[]
def txt(x,y,t,c='#17314b',f=None):
 dr.text((x,y),t,font=f or font,fill=c);sv.append(f'<text x="{x}" y="{y+18}" font-family="Arial" font-size="17" fill="{c}">{html.escape(t)}</text>')
def line(pp,c,w=2):
 if len(pp)>1:dr.line(pp,fill=c,width=w);sv.append('<polyline fill="none" stroke="'+c+'" stroke-width="'+str(w)+'" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pp)+'"/>')
def box2(bb,axes,proj,c,w=2):
 a,b=axes;lo,hi=bb;pts=[[lo[a],lo[b]],[hi[a],lo[b]],[hi[a],hi[b]],[lo[a],hi[b]],[lo[a],lo[b]]];line([proj(q) for q in pts],c,w)
txt(25,17,'ONE whole F_PI/W068 clocked layer — case allocation rejected BEFORE new support',f=bd)
txt(25,57,'Selected FHAC0001ZXJ +0287003.PXCN3A preserved. Full51x22x20.25 case box rotated ONCE; no actual PCB/MTA moved.',f=sm)
txt(25,105,'PLAN XY — source-bound whole candidate / no contact inferred from projection',f=sm)
xy=lambda p:(560+p[0]*4.0,285-p[1]*4.0)
box2([[-78.449996,-11,30.975],[-27.450004,11,51.225]],(0,1),xy,'#a7adb5')
box2(pr['case_pose']['bounds_mm'],(0,1),xy,'#2375ac',3)
box2(s['actual_owner_bounds_mm'],(0,1),xy,'#9a6b37',3)
box2([[4.55,-1.5,43],[26.55,35.5,54]],(0,1),xy,'#6b7785')
box2([[-127,-25,33.5],[-80.8,4.5,41.02]],(0,1),xy,'#b49b47')
line([xy(p) for p in [[-20,-9.5],[-20,-2],[-14,4],[4.55,4]]],'#319267',2)
line([xy(p) for p in [[-20,-60.5],[-20,-70.75],[-32.4,-83.15],[-44.8,-70.75],[-44.8,-45.75]]],'#9e69b2',2)
txt(25,618,'Blue full FHAC candidate | Brown retained F_R1 | Grey old unqualified F_PI/P_SYS | Yellow unchanged newcrown',f=sm)
txt(755,105,'Actual XZ section Y=-50 — supported housing, pad and valid common',f=sm)
xz=lambda p:(770+(p[0]+48)*17,615-(p[1]-30)*7.5)
for q in viewsec['sections']:
 col={'PROPOSED_FULL_FHAC_CASE_BOX':'#2375ac','ACTUAL_F_R1_HOUSING':'#9a6b37','ACTUAL_F_R1_BEARING_PAD':'#778592','CASE_ALLOCATION_WITH_HOUSING_COMMON':'#c32036'}[q['name']]
 for curve in q['curves_xz']:line([xz(p) for p in curve],col,4 if 'COMMON' in q['name'] else 2)
lines=[
 ('First gate1/29,28UNRECEIVED: full FHAC allocation / real selected-housing BankPad common167.343720 mm3.', '#b02032'),
 ('Independent source-owner1/1: full FHAC allocation / ACTUAL F_R1 housing common251.015580 mm3, both operands valid.', '#b02032'),
 ('BankPad is required bottom bearing extruded3mm from actual selected F_R1 bottom face; not an arbitrary free guide or own F_PI.', '#183048'),
 ('This rejects THIS complete case/lid/lead-layer allocation, not delivered hardware contact/all F_PI orientations or a stock shortage.', '#183048'),
 ('New W043 nominal route+strip12=47.474778; raw+tip8.35=55.824778 <=84.5 source. W077+tip8.35=82.555749 <=84.5.', '#183048'),
 ('Those positive LENGTH BOUNDS are NOT received routes/current stock fit. W078 input210 remains a separate same-K1474 debit, NULL.', '#183048'),
 ('Whole cradle/root extension/full large case-tie/head/uncut tails/strainlands/lid access/assembly unbuilt and OPEN. No detail after stop.', '#183048'),
 ('Unchanged W068 crown roots and SOURCE9 packing kept; old W0683/4+1 and S0cowl/PWMwasher negatives remain scoped/open.', '#183048'),
 ('Native26064/session46493 IDLE pendingnull unsavedfalse; current1292/effective1311 unchanged; N01=0/10; active window.', '#183048')]
for i,(t,col) in enumerate(lines):txt(25,667+i*38,t,col,sm)
png='day07-FPI-clocked-case-and-real-F_R1-first-falsifier-view.png';svg=png.replace('.png','.svg');im.save(out/png);(out/svg).write_bytes(('<svg xmlns="http://www.w3.org/2000/svg" width="1460" height="1050"><rect width="1460" height="1050" fill="#f7f8fa"/>'+''.join(sv)+'</svg>').encode())
names=[pn,gn,g['archive'],sn,s['archive'],'day07-FPI-W068-clocked-layer-pregate-whole-proposal.svg',png,svg]
for src in ['robot-cat69-clocked-case-source-first-gate.py','robot-cat69-actual-supported-housing-source-witness.py','robot-cat69-render-close-clocked-case.py']:
 n='day07-'+src.removeprefix('robot-cat69-').removesuffix('.py')+'.recipe.py';assert not(out/n).exists();(out/n).write_bytes((temp/src).read_bytes());names.append(n)
checks=[]
for d in [g,s]:
 with zipfile.ZipFile(out/d['archive']) as z:
  assert z.testzip() is None
  for row in d['geometry']:assert hashlib.sha256(z.read(row['entry'])).hexdigest()==row['sha256']
 checks.append(dict(path=d['archive'],crc_ok=True,member_sha_verified=len(d['geometry'])))
sources=list(pr['source_pins'])
for rel in ['tools/cad/feline_channelled_foundation.py','hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/n01-module-plan-r5.json','hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day07-S0-complete-oblique-entry-profile.json','hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/n01-shared-routing-boundaries.json']:
 sources.append(dict(path=rel,sha256=sha(root/rel)))
nextstep='WHOLE_FPI_SOURCE_FHAC_CASE_AND_SHORT_TWO_LEAD_SPACE_FROM_ACTUAL_BOUGHT_OCCUPANCY: currentcentralspineFPIhomewasunqualified, butNEWfullclockedcase20.25x51x22at[-20,-35,48.5] isallocatedintoactualselectedF_R1housing251.015580anditsrequiredBankPad167.343720. DoNOTcutbearingoredit/moveR47case/factoryends orscalarcase/bandnudge; no cradle detail/28remainingchecks forrejectedinput. NeedoneWHOLEavailablecase+lid/strain/splice/shortW043tofixedP_SYSallocation fromactualF_R1/fullneighborlayers, beforechooseanotherpose. RootFramecrown5/4/localcontactsunchangedpositiveONLYscoped; no newrootacceptancebyname. W043new47.474778+tip8.35<=84.5 andW07782.555749<=84.5 areconditionalnominalbounds/notacceptedpaths; W078210inputsameK1474/newwholedebitNULL (notPi350), existingowned8lap/20sleeve/2full9 preserved. MAINphysicalinterface/receivedfull12notmoved; no oldmiddle/nominalblankcredit. FPIactualcaseomittedfromDay26/currentctxonlyprojectbox, conservative51case+FHAC0001ZXJ/3Afuse/2supplier84.5tails andcase-no-wirepullfunction retained. W068pressure9/heads/full2uncut145/1S0pair/parking/access andS0shield/PWMwashernegative remainOPEN; source9lanes/four220/MTA/55EACHFL2/9ID12portion4MAX3/AUfit_slackNULL/globalN010 unchanged.'
times=[dict(receipt=n,operation_seconds=d['operation_seconds'],process_cpu_seconds=d['process_cpu_seconds']) for n,d in [(gn,g),(sn,s)]]
r=dict(id='day07-FPI-W068-clocked-layer-bounded-disposition',status='WHOLE_CLOCKED_CASE_ALLOCATION_REJECTED_BY_SELECTED_F_R1_HOUSING_BEFORE_SUPPORT',selected=False,N01_complete=False,one_whole_strategy_attempt=1,no_second_case_pose_or_detail_built=True,proposal=pn,physical_source_resolution=pr['physical_source'],pose=pr['case_pose'],first_gate=dict(receipt=gn,first_falsifier=g['first_falsifier'],counter=dict(received=1,total=29,unreceived=28,first_stop=True)),independent_supported_housing_fact=dict(receipt=sn,owner=s['actual_pad_owner'],owner_bounds=s['actual_owner_bounds_mm'],source_role=s['actual_pad_role'],common_valid=s['common_valid'],housing_allocated_common_mm3=s['full_case_allocation_common_mm3'],gap_mm=s['gap_mm'],counter=dict(received=1,total=1),not_resume_of28=True),classification='NewFHACfullconservativecaseallocation intersects validcurrentboughtF_R1housingmodel anditsactualbearing; notjustmovableguide/stockcurve. Thisiscurrentallocationrejection, NOTdeliveredphysicalcontact orallavailablecasearrangements/stockimpossibility. No sourcehousing/pad/foreign1.25 waiver.',case_mapping=dict(currentctx_only_registered_reservation=True,missing_Day26_native_case_previously_received_not_retested=True,source_registered_size_retained=True,whole_case_rotation_applied_ONCE=g['new_rigid_transform'],contents='FHAC0001ZXJ+0287003.PXCN3A / same two included16AWGleads; no movedMTA/MAIN/PiPCBs'),source_length_bounds=dict(W043=pr['W043'],W077=pr['W077'],W078=pr['W078'],new_whole_routes_received=False,old_nominal_blanks_not_delivered_cuts=True,factory_trim_after_dryfit_SOURCE_only_no_physical_cut=True,currentMAIN_full12_unchanged_notinvalidated_by_reference_bbox=True,no_doubleXML_or_virtual_solder_detach=True),case_mount=dict(attachment_hypothesis=pr['support'],built=False,actual_added_root_or_cradle_received=False,manufacturer_note7_case_must_not_take_wirepull=True,case_tie_selected_existing_large_role_only_no_new_SKU_inventoryUNKNOWN=True),initialassembly=dict(proposed=pr['assembly'],whole_sequence_unreceived=True,rare_partial_disassembly_allowed=True,routine_upward_lid_field_unreceived=True,no_full_N08_gate_added=True),remaining_stock_and_functions=dict(W068=pr['W068'],replacement_roles_only=['W068/single/end:0:saddle','W068/single/end:0:band_budget','W068/single/end:0:head_budget'],replace_only_after_futurekit_received=True,W068wire_and_terminalring_otherends_preserved=True,oldroot_foreign3of4_1S0pair_unreceived_frozen=True,S0cowl_PWMwasher_common_mm3=0.252442229,S0cowl_PWMwasher_negative_retained=True,new_source_bbox_proofs=g['new_bounding_scope_only']),currentcomposition=dict(base_source_count=1292,effective_context_count=1311,changed=False,oldFPIregisteredcase_still_retained=True,new_candidate_not_selected=True),negative_history='OldriserC0/C1 andS0cowl/V3/SOURCEU/S/floors/physical4independent220/bothMTA/currentR47P0E6MAIN46.52 held; no replay/waiver/newreview.',source_pins=sources,packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=checks,timings=times,actual_native_total_wall_seconds=sum(q['operation_seconds'] for q in times),actual_native_total_process_cpu_seconds=sum(q['process_cpu_seconds'] for q in times),view=dict(path=png,actualsection=sn,visual_inspection='PENDING_OWNER_VIEW',planlines_are_proposed_not_qualifiedwirecurves=True),next=nextstep,native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False),global_open='Whole123246/currentoutsideDGV/55EACHphysicalFL2/independentdeltaL/9ID12portion4MAX3/850+900ceil5minplus20/AUfit_slackNULL/actualcutNULL/U1far/headNorth/four220/both4MTA/Pimates/R6/invalid3/motionoutline/N010.',written_utc=datetime.now(timezone.utc).isoformat())
p=out/(r['id']+'.json');assert not p.exists();p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(dict(receipt=p.name,sha256=sha(p),packet_pins=len(names),source_pins=len(sources),archives=checks,wall=r['actual_native_total_wall_seconds'],CPU=r['actual_native_total_process_cpu_seconds'],view=png),indent=2))
