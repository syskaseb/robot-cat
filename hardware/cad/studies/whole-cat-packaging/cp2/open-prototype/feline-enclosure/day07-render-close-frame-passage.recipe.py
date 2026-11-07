from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,math,os,subprocess,html
from PIL import Image,ImageDraw,ImageFont
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
n0='day07-SOURCE-actual-frame-passage-source-inputs.json';pn='day07-SOURCE-left-end-frame-bypass-whole-proposal.json';gn='day07-SOURCE-left-end-body-passage-first-gate.json';mn='day07-SOURCE-left-end-body-passage-new-moving-delta.json';a,p0,g,m=[json.loads((out/n).read_bytes()) for n in [n0,pn,gn,mn]]
assert g['first_falsifier'] is None and g['current_whole_neighbor_count']==1443 and g['cursor']==g['total']==0 and g['all_other_full_sources_bbox_positive'];assert g['outline']['received_margin'] and g['outline']['expanded_cover_outside_mm3']==0;assert m['received_complete_poses']==35 and m['conservative_pairs_computed']==4515 and m['actual_new_pairs']==0 and m['first_falsifier'] is None
assert abs(g['whole_full_field']['volume_mm3']-9.4*37.75*10.5)<1e-6
im=Image.new('RGB',(1450,1010),'#f5f6f8');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24);sv=[]
def txt(x,y,t,col='#152238',f=None):
 dr.text((x,y),t,font=f or font,fill=col);sv.append(f'<text x="{x}" y="{y+20}" fill="{col}" font-family="Arial" font-size="19">{html.escape(t)}</text>')
txt(25,14,'SOURCE actual frame bypass: whole9 straight body passage RECEIVED SCOPED',f=bold)
txt(25,52,'LEFT END of real U1 carrier; no P0 cutting, no new print, no quarter retry. Full loop / root / wire budgets OPEN.')
colors={'full9_left_end_passage_capacity':'#d59100','actual_U1carrier':'#b65257','actual_P0_MountFrontL':'#8950a1','actual_BodyOuter':'#222222'}
for k,y in enumerate([55,70]):
 x0=25+715*k;txt(x0,96,f'Actual current section Y{y}: X / Z [mm]')
 panel=Image.new('RGB',(685,365),'white');pd=ImageDraw.Draw(panel)
 def xy(v):return((v[0]+145)/40*685,365-(v[1]-25)/45*365)
 sv.append(f'<defs><clipPath id="p{k}"><rect x="{x0}" y="135" width="685" height="365"/></clipPath></defs><g clip-path="url(#p{k})">')
 for sec in g['sections']:
  if abs(sec['value_mm']-y)>1e-6:continue
  for line in sec['curves_xz']:
   pts=[xy(q) for q in line]
   if len(pts)>1:
    col=colors[sec['name']];pd.line(pts,fill=col,width=3);sv.append('<polyline fill="none" stroke="'+col+'" stroke-width="2" points="'+' '.join(f'{x+x0:.2f},{z+135:.2f}' for x,z in pts)+'"/>')
 # Conservative3.25expandedcover shown from actual savedgeometrybounds.
 pts=[xy(q) for q in [(-140.7,35.5),(-124.8,35.5),(-124.8,52.5),(-140.7,52.5),(-140.7,35.5)]];pd.line(pts,fill='#5ca0bc',width=2);sv.append('<polyline fill="none" stroke="#5ca0bc" stroke-width="2" points="'+' '.join(f'{x+x0:.2f},{z+135:.2f}' for x,z in pts)+'"/>');sv.append('</g>');im.paste(panel,(x0,135))
for i,(n,col) in enumerate([('Actual BodyOuter','#222222'),('Full9 capacity','#d59100'),('Actual U1 carrier','#b65257'),('3.25 expanded cover','#5ca0bc')]):txt(25+i*355,520,n,col,f=small)
lines=[
 'Full9.4x10.5 field: X[-137.45,-128.05], Y[39.25,77], Z[38.75,49.25]; straight length37.75mm.',
 'All1443 complete source bounds separated; closest U1 lower2.05mm. Zero strict candidates is NOT omission.',
 'ACTUAL BodyOuter: expanded3.25 cover outside volume0; actual contour margin received, not BBox-only.',
 'NEW field / moving interface ONLY:35poses x129actors=4515 complete covers; min3.163420mm; no exact pairs.',
 'Neutral reused; old new21 motion36/155pairs/root/guide/sourceworld checks NOT repeated.',
 'Open-lay9 packing3rows: D/G3.1, V2 / gaps.2 / margin.4. No new terminal or universal9 allowance.',
 'U1 end material faces0/2/11/12 recorded ONLY; new leading support/root/access is NOT accepted or built.',
 'Unselected old8-member guide overlay withdrawable; real originalBankBed retained,105root facts not transferred.',
 'NEXT: actual external Knee6/Hip3 entryfan/R35.1/roll + usable55/10reserve capacity and all9/12/4 stock bounds.',
 'No percore fit/slack claims, oldprefix credit, physicalcut or V3 detail. R6/head/global123246 remain OPEN.',
 'Native26064/46493 IDLE / pendingnull / unsavedfalse. N01=0/10; active24h window retained.'
]
for i,t in enumerate(lines):txt(25,558+37*i,t,'#b32030' if i in [6,8,9] else '#152238')
png='day07-SOURCE-left-end-body-passage-received-view.png';svg=png.replace('.png','.svg');im.save(out/png);(out/svg).write_bytes(('<svg xmlns="http://www.w3.org/2000/svg" width="1450" height="1010"><rect width="1450" height="1010" fill="#f5f6f8"/>'+''.join(sv)+'</svg>').encode())
names=[n0,pn,gn,g['archive'],'day07-SOURCE-left-end-body-passage-new-moving-delta-scope.json',mn,png,svg]
for src in ['robot-cat58-actual-frame-passage-source-read.py','robot-cat58-save-left-end-whole-proposal.py','robot-cat58-left-end-body-passage-first-gate.py','robot-cat58-new-body-passage-moving-delta.py','robot-cat58-render-close-frame-passage.py']:
 n='day07-'+src.removeprefix('robot-cat58-').removesuffix('.py')+'.recipe.py';assert not(out/n).exists();(out/n).write_bytes((temp/src).read_bytes());names.append(n)
checks=[]
with zipfile.ZipFile(out/g['archive']) as z:
 assert z.testzip() is None;ge=json.loads(z.read('manifest.json'))['geometry'];assert len(ge)==3
 for q in ge:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
 checks.append(dict(path=g['archive'],crc_ok=True,member_sha_verified=len(ge),empty_outside_result_has_no_world_bounds=ge[2]['bounds_mm'] is None))
p=out/'day07-SOURCE-left-end-body-passage-bounded-disposition.json';assert not p.exists()
nextstep='LEFT_END_GROUP_ENTRY_FAN_BEFORE_NEW_LEADING_MATERIAL: useactualclosedbodypassageX[-137.45,-128.05]/Y39.25..77/Z38.75..49.25. ONEadaptiveexternalKnee6/Hip3 sharedspace/entryfan/roll atR35.1 fromactualsource36portframes; guideispassiveNOTforcedY-tangentterminal. Resolvefirstfullactualsourcecase/edge/ground/Anklelocalhazardonlywhereregioncannotdecide; notall123axes/oneunchangingcurveforallposes/new21motionbodyreplay. Explicit55/10planningreserve stillneedsaccessiblecapacity/lengthupper. ALL9ID12portions4physicalMAX3original+donor currentA/U/minfit/slackNULL untilqualifiedgrouptransport+currentbodyDGVfan/enddebits/850/900ceil5(min+20). ProspectivepassiveleadingonactualU1leftendmaterialfaces0/2/11/12 mustpreserveU1functions/root/accessandqualifiedsourceentirekit beforebuild; no old105root transfer/newstockclaim/materialdetail/V3 before wholeSOURCEcredible.'
r=dict(id=p.stem,status='ACTUAL_LEFT_END_FRAME_BODY_PASSAGE_CURRENT_OCCUPANCY_CONTOUR_AND_NEW_MOVING_INTERFACE_CLOSED_SCOPED',selected=False,N01_complete=False,
 closed_problem=dict(body_passage=g['whole_full_field'],full_neutral_context_actors=1443,actor_count_basis='Effective1311+rest108+proposednewSource21+4temp minus1provedduplicateBankPadalias =1443; currentoriginalBankBed replacesunselectedoldguideoverlayONCE.',all_full_source_bbox_separated=True,closest_neutral_full_source_lower_mm=g['nearest_full_actor_bounds'][0]['conservative_full_source_bbox_lower_mm'],closest_actor=g['nearest_full_actor_bounds'][0]['actor'],strict_candidates=0,no_parts_omitted_by_name=True,actual_contour_proof=g['outline'],new_field_vs_moving=dict(required_new_poses=35,actors=129,full_conservative_covers=4515,minimum_full_cover_lower_mm=m['minimum_full_cover_lower_mm'],new_exact_pairs=0,neutral_reused=True,source_data=mn,bodyfixed_field_ground_lower_mm=m['bodyfixed_field_ground_lower_over_required36_mm'],old21motion_matrix_not_replayed=True,external_freeflex_NOT_qualified=True)),
 source_frame_function=dict(MountFrontL_actual_source=n0,small_bores_not_assumed_wireportals=True,actual_frame_near_parts=g['actual_P0_mount_neighbors'],actual_U1_deep_bar_bottom_z_mm=30.52,no_P0_cutting_or_hardware_removal=True),packing=dict(full9_source_cross_mm=[9.4,10.5],profile_D_G_mm=3.1,profile_V_mm=2,interprofile_gap_mm=.2,each_edge_packing_margin_mm=.4,triplet_row_Z_mm=[40.7,44,47.3],profile_X_centres_mm=[-135.5,-132.75,-130],source='Samealreadyreceived2Dpacking, newstraightfullfieldcontainsentirepack+currentactorsclear. Notnewwireaxes/wholecurve/wholefit. SourceFL1/FL2/DONORFL3threebodytriplets; SOURCEFL3originaljointportionstaysKnee.',group_R35p1_unmodified=True),
 whole_new_plan=dict(proposal=pn,physical_portion_rows=p0['physical_portion_rows'],planned_motion_reserve=p0['planned_moving_reserve'],all_current_A_U_minimum_fit_slack=None,external_group_R_entryfan_roll_storage_assembly_NOT_qualified=True,source_stock='Source14terminal11full9lap4once/3x8laps3x20sleeves/stagger2x9lands/850project/900ceil5(min+20)MAX3perphysicalunit/factoryplug/actualcutNULLphase2. No purchasedremainderpool/oldprefix/chord-as-route/20fittrimasslack/universal37.75debit.'),
 guide_load_interface=dict(old_added8_only_unselected_overlay_withdrawal=True,original_actual_BankBed_retained=True,old105root_geometry_evidence_TRUE_but_not_transferred=True,original_parent_subset_of_whole105_already_received_membercoverage=True,new_source21_motion_clearances_reuse_on_material_subset_deletion=True,actual_potential_U1_left_end_material_faces=g['actual_U1_left_end_material_faces'],new_root_contact_loadpath_received=False,new_material_or_holder_built=False,new_fastener_or_tie_demand_claimed=False,required_retained_functions='ActualU1feet/holes/lowerbranch/understep/foamC/metal/FHYsupport/screwaccess; SOURCE4movingties/MODULE2; no parentownershipwaiver fromname.'),
 historical_HOLDs='Keep402.079splitKnee6allocation3of33/30unreceived;Hip3northY116.8limit96.75excess20.05;oldfull9U178.3508221of34/33unreceived;shortCS22of36;alloldSOURCE/V3/S0/Pi45/vertical/reviewcounts frozen. NewpassagepositiveNOTwholealternativewirecontact/shortageproof; no thirdquarter oroldpairreplay.',
 current_scene='Current1292/effective1311/rest108a9f78e06/2d1d8cfa/def3e56aunchanged; newSource21+4tempPROPOSEDbodycontext. No officialwholeN01selection. NewfieldisreservedspaceNOTinstalledpart; originalBankBedsourcebf0311used, no duplicateparent/old8guide currentadd.',
 next=nextstep,global_open='ActualexternalSOURCEconnectedR/movingreserve/storage/lengthslack/entryfan/newleadingroot/initialassembly;all123246/U1far/headNorth/4MTA/four220/Pimates/R6actualwithdrawtool/3invalidUSB/globalchangedoutline/wholeN01.',guards='R47/P0/E6/15drives/MG92B/MAIN46.52/325x200x160/max200/256cube/foreign1.25/BodyOuter3.25/fourindependent220/both4MTA. Group35.1isprojectcapacitynotmanufacturerdatum; selectedpercore12.4unchanged/no shorterRwaiver.',
 source_pins=[dict(path=n,sha256=sha(out/n)) for n in ['day07-SOURCE-split-portals-bounded-disposition.json','day07-SOURCE-pad-conforming-guide-bounded-disposition.json','day07-SOURCE-motion36-and-group-return-bounded-disposition.json','day07-coordinator-fixed-print-source-functions.json','day07-SOURCE-body-approach-proposed-moving-context.json','n01-selected-piece-profile-contract.json','day07-S0-C1-current-candidate-composition.json']],packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=checks,geometry_metadata_repair=g.get('empty_outside_metadata_disposition'),timings=[dict(receipt=n,operation_seconds=q['operation_seconds'],process_cpu_seconds=q['process_cpu_seconds']) for n,q in [(n0,a),(gn,g),(mn,m)]],view=dict(path=png,source=gn,actual_sections_Y_mm=[55,70],visual_inspection='PENDING_OWNER_VIEW',no_projection_contact_inference=True),native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False,identity_received='OWNER58_FINAL_IDLE26064 1292/1311/108 pendingnull unsavedfalse'),written_utc=datetime.now(timezone.utc).isoformat())
p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(dict(receipt=p.name,sha256=sha(p),files=len(names)+1,archive_checks=checks,view=png),indent=2))
