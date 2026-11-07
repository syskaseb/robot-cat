from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,math,os,subprocess,html
from PIL import Image,ImageDraw,ImageFont
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((out/'day07-SOURCE-new-moving-module-region-first-gate.json').read_bytes());m=json.loads((out/'day07-SOURCE-new21-motion36-complete-scoped.json').read_bytes());g=json.loads((out/'day07-SOURCE-external-loop-return-capacity-first-gate.json').read_bytes());prop=json.loads((out/g['proposal']).read_bytes())
assert m['complete_pose_indices']==list(range(36)) and m['first_falsifier'] is None and len(m['actual_candidate_rows'])==155 and m['actual_candidate_rows'][:19]==old['actual_candidate_rows'];assert len({(q['pose'],q['new_actor'],q['other']) for q in m['actual_candidate_rows']})==155
assert len(m['new_floor_rows'])==len({(q['pose'],q['actor']) for q in m['new_floor_rows']})==756 and m['new_floor_rows'][:84]==old['new_floor_rows'];assert all(q['status']=='NEW_SOURCE_MOTION_SEPARATED125' for q in m['actual_candidate_rows'])
assert g['cursor']==1 and g['total']==34 and g['unreceived']==33 and g['first_falsifier']['common_valid'] and abs(g['first_falsifier']['allocated_capacity_common_mm3']-78.35082226377095)<1e-6
im=Image.new('RGB',(1400,960),'#f5f6f8');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);svg=[]
def txt(x,y,t,color='#152238',f=None):
 dr.text((x,y),t,font=f or font,fill=color);svg.append(f'<text x="{x}" y="{y+20}" fill="{color}" font-family="Arial" font-size="19">{html.escape(t)}</text>')
txt(25,14,'SOURCE new21 motion36 RECEIVED / full9 south-return capacity HOLD',f=bold)
txt(25,53,'155/155 strict pairs separated (136 NEW;19 reused),756 floor properties; no whole harness/outline PASS.')
colors={'full9_R35p1_return_capacity':'#d59100','actual_current_U1carrier':'#b65257','new_complete_BankBed_guide':'#2371b6'}
for k,y in enumerate([55,60]):
 x0=30+690*k;txt(x0,100,f'Actual source-derived section Y={y}: X / Z [mm]')
 panel=Image.new('RGB',(650,365),'#ffffff');pd=ImageDraw.Draw(panel)
 def xy(v):return((v[0]+92)/55*650,365-(v[1]-32)/23*365)
 svg.append(f'<defs><clipPath id="p{k}"><rect x="{x0}" y="145" width="650" height="365"/></clipPath></defs><g clip-path="url(#p{k})">')
 for sec in g['sections']:
  if abs(sec['value_mm']-y)>1e-6:continue
  for line in sec['curves_xz']:
   pts=[xy(q) for q in line]
   if len(pts)>1:
    col=colors[sec['name']];pd.line(pts,fill=col,width=3);svg.append('<polyline fill="none" stroke="'+col+'" stroke-width="2" points="'+' '.join(f'{x+x0:.2f},{yy+145:.2f}' for x,yy in pts)+'"/>')
 svg.append('</g>');im.paste(panel,(x0,145))
for i,(name,col) in enumerate(colors.items()):txt(35+i*455,530,name.replace('actual_current_',''),col,f=small)
lines=[
 'Full9 turn: R35.1 / radial9.4 / depth10.5; neutral-axis arc55.134951mm (NOT whole wire debit).',
 'Actual U1carrier / allocated turn common78.350822mm3; valid operands;1/34 +33 UNRECEIVED.',
 'This is ALLOCATED CAPACITY HOLD, NOT physical installed wire contact or all handroutes impossible.',
 'Existing guide seam matches Y67, X[-53.7,-44.3], Z[38.75,49.25]; no terminal or extra9.',
 'Guide root105mm2/embed26.25 and9members/7joints remain received unchanged SCOPED.',
 'New21 body/floor motion:36/36 complete, minimum ground lower60.581157mm; no old matrix replay.',
 'BodyOuter3.25 / full R6 routine tool space / whole loop moving reserve & lengths remain OPEN.',
 'NEXT: separate Knee6 / Hip3 approaches across actual U1 load layer before accounting merge9.',
 'No scalar turn/guide offset, no shorter R, no V3 detail. All9IDs/12portions/4MAX3 fit/slack NULL.',
 'Native26064/46493 IDLE / pendingnull / unsavedfalse. N01=0/10; active window retained.'
]
for i,t in enumerate(lines):txt(25,578+i*35,t,'#b32030' if i in [1,2,6,8] else '#152238')
png='day07-SOURCE-motion36-and-south-return-capacity-view.png';svgn=png.replace('.png','.svg');im.save(out/png);(out/svgn).write_bytes(('<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="960"><rect width="1400" height="960" fill="#f5f6f8"/>'+''.join(svg)+'</svg>').encode())
names=['day07-SOURCE-new-motion-continuation-current.json','day07-SOURCE-new21-motion36-complete-scoped.json','day07-SOURCE-external-loop-current-neighborhood-inputs.json',g['proposal'],'day07-SOURCE-external-loop-return-capacity-first-gate.json',g['archive'],png,svgn]
for src in ['robot-cat56-source-new-motion-continuation.py','robot-cat56-external-loop-current-inputs.py','robot-cat56-save-external-loop-whole-proposal.py','robot-cat56-external-loop-capacity-first-gate.py','robot-cat56-render-close-motion-group.py']:
 n='day07-'+src.removeprefix('robot-cat56-').removesuffix('.py')+'.recipe.py';(out/n).write_bytes((temp/src).read_bytes());names.append(n)
checks=[]
with zipfile.ZipFile(out/g['archive']) as z:
 assert z.testzip() is None;ge=json.loads(z.read('manifest.json'))['geometry']
 for q in ge:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
 checks.append(dict(path=g['archive'],crc_ok=True,member_sha_verified=len(ge)))
# Current portion chains are explicit. Proposal's copied old core_rows contribute ID/unit identity ONLY;
# their old region_chain arrays are historical baseline, not current connected-path acceptance.
portion_rows=[]
for q in prop['all9_rows']:
 core=q['core'];dest={'D':'D3_underframe','V':'V3_outerbank','G':'G3_underbank'}[core]
 tail=['SOUTH_MERGE9','FIXED_RETURN_QUARTER9','EXISTING_PASSIVE9','DGV_SPLIT',dest,q['body_receiver']]
 if q['loom']=='FL3':
  portion_rows.append(dict(wire=q['wire'],physical_unit='SOURCE/FL3',role='ORIGINAL',chain=['factory_source14','Knee_static_approach','received_holder_ENTRY9','source_owned_joint_'+core],minimum_mm=None,fit_blank_mm=None,actual_cut_mm=None))
  portion_rows.append(dict(wire=q['wire'],physical_unit='DONOR/FL3',role='DONOR',chain=['source_owned_joint_'+core,'received_holder_EXIT9','KNEE6_EXTERNAL_LOOP']+tail,minimum_mm=None,fit_blank_mm=None,actual_cut_mm=None))
 else:portion_rows.append(dict(wire=q['wire'],physical_unit=q['physical_units'][0],role='CONTINUOUS',chain=['factory_source14','HIP3_EXTERNAL_APPROACH' if q['loom']=='FL1' else 'Knee_static_approach','KNEE6_EXTERNAL_LOOP']+tail if q['loom']=='FL2' else ['factory_source14','HIP3_EXTERNAL_APPROACH']+tail,minimum_mm=None,fit_blank_mm=None,actual_cut_mm=None))
assert len(portion_rows)==12 and len({q['wire'] for q in portion_rows})==9
p=out/'day07-SOURCE-motion36-and-group-return-bounded-disposition.json';assert not p.exists()
nextstep='SPLIT_KNEE6_HIP3_APPROACH_BEFORE_ACCOUNTING_MERGE: actualU1lowercrossbeam blocksTHISfull9southquarter lowercapacitylayer78.350822, notall3Dloops/actualwire. Retain105root/guidepose andreceivednew21motion; beforeanynewmaterial choosewholeKnee6/Hip3entry/layer/assembly order usingtwoexistingguideportals/realU1functions andcurrentfullprofiles/R35.1. Firstactualusablecrosssection/connectedturncapacity+sourceportframes andfullneighbors; no third scalar9turn/guideheight/PCBoffset/shorterR. Then explicitmovingreserve/percoreRoffsetlength/ALL9ID12portion4MAX3sourceoriginal+donor/850/ceil5(min+20)<=900, realsource14terminal11full9lap4once, no oldprefix/chordcredit/V3detail. Allfit/slackNULL until qualified.'
r=dict(id=p.stem,status='NEW21_MOTION36_CLOSED_SCOPED_EXTERNAL_LOOP_FULL9_RETURN_ALLOCATED_CAPACITY_HOLD',selected=False,N01_complete=False,
 closed_problem=dict(new_operating_parts=21,required_current_poses=36,complete=36,strict_pairs_total=155,strict_pairs_NEW=136,previous19_not_replayed=True,new_floor_properties_total=756,previous84_not_replayed=True,ground_rest_z_mm=old['ground_rest_z_mm'],minimum_conservative_ground_lower_mm=m['minimum_new_floor_lower_mm'],first_physical_falsifier=None,raw_motion_receipt='day07-SOURCE-new21-motion36-complete-scoped.json',source_same_Knee_relative_pairs_reused=True,scope='OnlyNEWoperating21body/currentfixedincludingnewBankBedguide+posedrest108 exceptcommonKneeunchangedrelativepairs. Excludes4temporarybenchpullfieldsoperation. NOTwholeflexharness, BodyOuter, R6, orN09.'),
 whole_group_decision=dict(proposal=g['proposal'],source_identity_rows_from_old_recipe_ONLY=True,old_core_rows_regionchains_NOT_current_pathproof=True,current_physical_portion_chains=portion_rows,all_chains_unqualified_after_first_capacity_HOLD=True,fixed_turn=g['capacity'],first_falsifier=g['first_falsifier'],cursor=g['cursor'],total=g['total'],unreceived=g['unreceived'],classification=g['meaning'],stopped_before_remaining_pairs=True,actual_A_U_minimum_fit_slack=None,unknowns=['ExternalKnee6/Hip3continuousR/roll/firstactualsourceapproach','Movingreserve+actualstoredslack','BodyDGVtransport/endfans','PerphysicalMAX3fit/minimum','Fullinitiallay/R6tool/BodyOuter3.25']),
 unchanged_received='Root26.25/contact105/sourcepad15x7/9members0missing/7joints/newpartstrictreopen/source4movingties/MODULE2/unchanged4independent220/both4MTA. ProposedBankBedoverride10.brep/d42f3671 replacesoldparent/provedpadaliases; newKnee21+4tempcontext13e527c8; current1292/effective1311/rest108a9f78e06/2d1d8cfa/def3e56a unchanged. No rejectedS0cowl/V3/oldholdersadded.',
 source_invariants='Selectedparts/R47/P0/E6/15drives/MG92B/MAIN46.52/325x200x160/max200/256cube/foreign1.25/BodyOuter3.25. Allnegativecounts unchanged. 850project+900/MAX3perphysicalunit,source14terminal11full9lap4once/3x8laps/3x20sleeves/stagger/2x9lands/factoryplug/actualcutNULL. No oldprefix/Gdelta/pool/purchasedoffcutasslack.',
 next=nextstep,global_open='WholeSOURCEconnectedoccupiedregions/lengthslack/assembly/changedoutline; R6actualwithdraw/tool/parking;3USBinvalidcurrentgates;Pimates/U1far/headNorth/123246/both4MTA/four220. Newmotion36 isscopedprototypefeasibility notwholeN09, no point.',
 source_pins=[dict(path=n,sha256=sha(out/n)) for n in ['day07-SOURCE-pad-conforming-guide-bounded-disposition.json','day07-SOURCE-body-approach-proposed-moving-context.json','day07-SOURCE-new-moving-module-region-first-gate.json','day07-SOURCE-new-motion-frozen-input-projection.json','day07-coordinator-SOURCE-splice-layout-authority-receipt.json','n01-selected-piece-profile-contract.json']],packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=checks,
 timings=dict(new_motion_chunks=m['chunks'],new_motion_operation_seconds=sum(q['operation_seconds'] for q in m['chunks']),new_motion_process_cpu_seconds=sum(q['process_cpu_seconds'] for q in m['chunks']),new_capacity_operation_seconds=g['operation_seconds'],new_capacity_process_cpu_seconds=g['process_cpu_seconds'],old_received_operation_not_added=True,wall_is_not_CPU=True),view=dict(path=png,source='day07-SOURCE-external-loop-return-capacity-first-gate.json',actual_sections_y_mm=[55,60],visual_inspection='PENDING_OWNER_VIEW',no_image_contact_inference=True),native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False,identity_received='OWNER56_FINAL_IDLE26064 36 36 155 756 None Underdeck:PositiveFoundation 1292 1311 108'),written_utc=datetime.now(timezone.utc).isoformat())
p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(dict(receipt=p.name,sha256=sha(p),files=len(names)+1,archive_checks=checks,view=png,native=r['native']),indent=2))
