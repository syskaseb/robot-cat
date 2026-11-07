from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,html,os,subprocess
from PIL import Image,ImageDraw,ImageFont
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pn='day07-W068-whole-rooted-pressure-leading-interface-proposal.json';gn='day07-W068-actual-frame-root-first-gate.json';nn='day07-W068-root-independent-neighbor-and-window-read.json';vn='day07-W068-root-RR-source-section.json';pr,g,n,v=[json.loads((out/q).read_bytes()) for q in [pn,gn,nn,vn]];assert n['first_falsifier']['common_valid'] and v['current_motion_owner']==['RR',0]
im=Image.new('RGB',(1450,1050),'#f5f6f8');dr=ImageDraw.Draw(im);ff=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);sm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);bd=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24);sv=[]
def txt(x,y,s,col='#152238',font=None):
 dr.text((x,y),s,font=font or ff,fill=col);sv.append(f'<text x="{x}" y="{y+19}" fill="{col}" font-family="Arial" font-size="18">{html.escape(s)}</text>')
def line(pp,col,width=2):
 if len(pp)>1:dr.line(pp,fill=col,width=width);sv.append('<polyline fill="none" stroke="'+col+'" stroke-width="'+str(width)+'" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pp)+'"/>')
txt(25,18,'W068 whole mechanical retention: west-frame-root preflight HOLD',font=bd)
txt(25,55,'Oldfloating9saddle function is NOT a mounted loadpath. Newwholepressure/root/stock hypothesis tested before details.',col='#b32030')
txt(25,103,'Actual frame YZ section / proposed contact footprint and tie-feed field',font=sm)
yz=lambda p:(30+(p[0]+55)*5.6,475-p[1]*8)
for curve in v['actual_frame_face16_YZ_boundary_curves']:line([yz(p) for p in curve],'#687b8b',1)
line([yz(p) for p in [[-30,18],[-20,18],[-20,28],[-30,28],[-30,18]]],'#1973a5',3);line([yz(p) for p in [[-16,23],[-14,23],[-14,26.3],[-16,26.3],[-16,23]]],'#c08512',3)
txt(25,510,'Actual contact88.771555mm2 / positive substrate8.877156mm3',font=sm)
txt(25,540,'Fullfeed allocated box / actual frame common7.548396mm3: HOLD',col='#b32030',font=sm)
txt(745,103,f"Actual XZ section Y{v['actual_section_Y_mm']:.6f}: root / RR0 part / common",font=sm)
xz=lambda p:(755+(p[0]+101)*22,540-p[1]*11)
for s in v['sections']:
 col='#b32030' if 'COMMON' in s['name'] else '#c08512' if 'BACKPAD' in s['name'] else '#687b8b'
 for curve in s['curves_xz']:line([xz(p) for p in curve],col,3)
txt(745,550,'Valid actual planned-root / retained RRstage0 common33.295211mm3',col='#b32030',font=sm)
lines=[
 'CurrentW068saddle bbox contact candidates: ownbandONLY. No actualframe/bodymaterial root proved; do not call it mounted.',
 '100mm2was a proposed rectangle, NOT a strength threshold:88.771555usable source-conforming contact is retained as fact.',
 'Rootbackpad actualRR0 overlap is separate decisive negative:1/4neighborpairs received,3UNRECEIVED; no detail after rejection.',
 'FullrootT18I145feedbox also crosses frame7.548396; notproofallflexiblebandroutes/otherframeinterfacesimpossible.',
 'Selected4905 is case-loadsONLY and was explicitly NOT used as strain-load root. No supplier/load waiver/FEM gate added.',
 'Wholeplan: unchangedW068wire/R25.2/9land, lower+removableupper pressure, full6head, twoT18I145roles incl1additionalrootDEMAND.',
 'Wholeuncuttails/rootfeed25once/stock/head/access not received; quantity availability not claimed; SOURCE4/MODULE2/BUS retained.',
 'NEXT one causal correction: inboard face99 bearing + over-frame loadlayer + realapertureloop + inboardtailpark; NOT BUILT.',
 'No root-thickness/head/curve nudge. ExistingSOURCE9packing closedscoped; outsideDGV/55each/lengthslack/wholeN01 remain OPEN.',
 'Native26064/46493IDLE pendingnull unsavedfalse / N01=0/10 / activewindow. No pressurearm/guide/V3 built or selected.'
]
for i,s in enumerate(lines):txt(25,620+i*36,s,'#b32030' if i in [1,2,3,7,8] else '#152238',sm)
png='day07-W068-root-and-RR-first-falsifier-received-view.png';svg=png.replace('.png','.svg');im.save(out/png);(out/svg).write_bytes(('<svg xmlns="http://www.w3.org/2000/svg" width="1450" height="1050"><rect width="1450" height="1050" fill="#f5f6f8"/>'+''.join(sv)+'</svg>').encode())
names=[pn,gn,g['archive'],nn,n['archive'],vn,png,svg]
for src in ['robot-cat66-save-W068-whole-mechanical-interface.py','robot-cat66-W068-actual-root-full-neighbor-first.py','robot-cat66-W068-root-independent-neighbor-and-window-read.py','robot-cat66-root-RR-source-section.py','robot-cat66-render-close-W068-root.py']:
 q='day07-'+src.removeprefix('robot-cat66-').removesuffix('.py')+'.recipe.py';assert not(out/q).exists();(out/q).write_bytes((temp/src).read_bytes());names.append(q)
checks=[]
for d in [g,n]:
 with zipfile.ZipFile(out/d['archive']) as z:
  assert z.testzip() is None
  for row in d['geometry']:assert hashlib.sha256(z.read(row['entry'])).hexdigest()==row['sha256']
 checks.append(dict(path=d['archive'],crc_ok=True,member_sha_verified=len(d['geometry'])))
nextstep='W068_ONE_INBOARD_CAPTURE_OVERFRAME_CORRECTION: currentwestrootbackpadoccupiesretainedRR/stage0part33.295211, whileowncontact88.771555isactualusablematerialnot100strengthcriterion; rootfeedfieldframecommon7.548396 alsoHOLD. Preservebothnegativefacts/rawreceipt0tasks/not0of0PASS. OnewholeC1: actualinboardFrameFront20face99source-conformingbearing(notrect100), mechanicalclosedselectedT18I145rootloopthroughREALnativeaperture, loadbridgeOVERframe andunderS0 ratherthanwestRRservo; full9W068splitpressure/full6head/tailstock/inboardpark/access together. ExistingFrameTop37.02 andS0min44.92003 withforeign1.25 givecoarseoverframeZ38.27..43.67003 (5.40003), NOTfree-spaceproof; chooseuseful4mmloadsectiononlyafteractualroot/head/feed/fullneighbors first. Eastrootface99actualcontact/rootloop/allneighbors NOTTESTED, correctionNOTBUILT; no sourcehead/curve/pad scalarretry and no caseadhesivetoloadwaiver. SameW068wire/R25.2/terminal5ring/full9, source9lanes/3branches/R35.1/four220/MTA/BUS/SOURCE4/MODULE2 preserved. No printing/wholemount untilpressurematerialjoins/stock145wholeheads/25once/uncuttails/currentroot/access/motionoutline qualified. C0onewholeattempt withmultipleHOLD, C1onecorrectionpending; olddesignreviewclosed1/1 no newround. GlobalSOURCEleg+body/R/55each/9ID12portion4MAX3/850/900/AUminfit_slackNULL/N010.'
sources=[dict(path=q,sha256=sha(out/q)) for q in ['day07-SOURCE-ninecore-entry-lane-roll-bounded-disposition.json','day07-SOURCE-ninecore-entry-physical-roles-and-W068-function.json','day07-SOURCE-current-BUS-DG-alias-stock-and-entry-function.json','day07-SOURCE-new-motion-frozen-input-projection.json']]
sources += [dict(path='tools/cad/'+q,sha256=sha(root/'tools/cad'/q)) for q in ['feline_s1_flexible_fans.py','feline_shared_power_backplane.py']]
stock=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint/w5-nominal-material-selection.json';sources.append(dict(path=stock.relative_to(root).as_posix(),sha256=sha(stock)))
p=out/'day07-W068-whole-retention-root-bounded-disposition.json';assert not p.exists()
r=dict(id=p.stem,status='W068_WEST_ROOT_C0_ACTUAL_RR_INTERFERENCE_AND_FEED_HOLD_FULL_INTERFACE_UNBUILT',selected=False,N01_complete=False,closed_problem='OldW068saddlehasnoactualrigidrootcontactotherthanownband. NewwholemechanicalframeclampalternativewasfalsifiedBEFOREpressure/stockdetail byactualRRstage0geometry, notlackofanexact100rectangle. Mechanicaltiefulldemand/wholeunit/phase2scopeexplicit; case-onlyadhesivenotmisused.',whole_hypothesis=pn,old_retention_function=dict(standalone_actor='W068/single/end:0:saddle',bbox_contact_candidates=g['old_W068_saddle_material_contact_bbox_candidates'],no_nonown_root_candidate=True,do_not_delete_actualwire_or_stock=True),actual_source_bearing=dict(actor='Ref_Material_P0_FrameFront20_0_0',face=16,contact_area_mm2=g['actual_patch_area_mm2'],positive_substrate_mm3=g['actual_substrate_common_mm3'],nominal_100_rect_not_strength_requirement=True,raw100receipt_preserved=True,source_conforming_useful_material_NOT_mountPASS=True),first_decisive_falsifier=n['first_falsifier'],source_obstacle_role=dict(actor=n['first_falsifier']['other'],frozen_current_motion_owner=v['current_motion_owner'],retained_rigid_geometry=True,notloosewire_or_ownframe=True,new_motion_tests=0),root_neighbor_counter=dict(cursor=1,total=4,unreceived=3,first_falsifier_stop=True),feed_failure=dict(actual_frame_common_mm3=g['full_frame_feed_material_common_mm3'],full3p3x2field=True,allocated_stock_feed_HOLD_not_all_band_paths_impossible=True),raw_receipt_area_HOLD_disposition=n['material_criterion_disposition'],whole_stock_plan=pr['pressure']['W068_pressure_tie'],additional_root_stock_plan=dict(selected_existing_SKU='111-02370/T18I145',nominal_additional_demand=1,source_stock_available_UNKNOWN=True,notpurchased=True),all_full_uncuttails_head_pull25_root_loop_install_access_OPEN=True,material_implementation=dict(actualpressure_upper_lower_not_built=True,actualarm_tray_not_built=True,onlyrootfunctional_envelope_and_sourcecontact_read=True,nomodel_parent_replaced=True),correction_scope=dict(C0_whole_attempts=1,C0_multiple_hold_not_multiple_strategies=True,C1_remaining=1,C1_inboard_capture_overframe_NOT_BUILT=True,no_new_designreview=True),initialassembly_scope=pr['assembly'],unchanged=pr['guards'],all_outside_SOURCE_DGV_fan_R_legvariation_usable55_each_lengths_stock_root_motion_outline_OPEN=True,current_A_U_minfit_slack=None,negative_history='SOURCE9fixedpackingclosedscopedreuse; DcentreS1metal4/5+1,outerW068head2/2.915103,U5/35+30,S8/127+119,floors303+21/321+3/allolderrejectionsretained. No oldproofreplay/newSOURCEcurve/V3.',next=nextstep,global_open='WholeN01constructivelayout/actualSOURCEtransport/lengthslack/123246/headNorth/U1far/fourMTA/four220/Pimates/R6/invalid3/motionoutline/N010.',source_pins=sources,packet_pins=[dict(path=q,sha256=sha(out/q),bytes=(out/q).stat().st_size) for q in names],archive_checks=checks,timings=[dict(receipt=q,operation_seconds=d['operation_seconds'],process_cpu_seconds=d['process_cpu_seconds']) for q,d in [(gn,g),(nn,n),(vn,v)]],view=dict(path=png,actual_frame_YZ_source=nn,actual_RR_XZ_source=vn,visual_inspection='PENDING_OWNER_VIEW',projection_not_collision_proof=True),native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False),written_utc=datetime.now(timezone.utc).isoformat());p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());names.append(p.name)
print(json.dumps(dict(receipt=p.name,sha256=sha(p),files=len(names),packet_pins=len(r['packet_pins']),source_pins=len(sources),archive_checks=checks,view=png),indent=2))
