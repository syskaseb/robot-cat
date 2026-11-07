from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,math,os,subprocess,html
from PIL import Image,ImageDraw,ImageFont
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pn='day07-SOURCE-left-entry-adaptive-long-loop-whole-proposal.json';gn='day07-SOURCE-adaptive-loop-ground-first-falsifier.json';ln='day07-SOURCE-adaptive-loop-ground-local-proof.json';prop,g,r=[json.loads((out/n).read_bytes()) for n in [pn,gn,ln]];f=r['first'];route=prop['groups'][f['group_index']]['states'][f['pose']]['route'];assert f['pose']==33 and f['core']=='G' and g['cursor']==303 and g['unreceived']==21;assert r['full_reserved_G_below_floor_mm3']>0 and r['minimum_profile_point_actual_BRep_gap_mm']<1e-6
im=Image.new('RGB',(1450,1050),'#f5f6f8');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24);sv=[]
def txt(x,y,t,col='#152238',ff=None):
 dr.text((x,y),t,font=ff or font,fill=col);sv.append(f'<text x="{x}" y="{y+20}" fill="{col}" font-family="Arial" font-size="19">{html.escape(t)}</text>')
txt(25,14,'SOURCE adaptive long-loop: chosen radius-storage topology HOLD',ff=bold)
txt(25,52,'Pose33 / SOURCE-FL2 G=W021 full reserved profile3.1; NOT delivered-wire contact or all manual loops impossible.')
# ContextprojectionfromnativecurrentposedBReps; centrelineisthiscandidatefamily ONLY.
pts=[]
for j in range(81):
 t=route['theta_radians']*j/80;pts.append([route['P'][i]+route['R_mm']*(math.sin(t)*route['T'][i]+(1-math.cos(t))*route['N'][i]) for i in range(3)])
pts.append(route['Q']);cols={'D':'#2371b6','V':'#6c798a','G':'#b32030','Ref_Material_P0_Part__Feature056_0_0':'#65828b','Ref_Material_P0_Part__Feature123_0_0_0':'#8b8e96'}
txt(25,96,'XZ projection / actual posed case+Foot context, candidate group path',ff=small)
xy=lambda p:(25+(p[0]+155)/180*660,490-(p[1]+100)/170*350)
for s in r['context_projections']:
 for line in s['curves_xz']:
  pp=[xy(v) for v in line]
  if len(pp)>1:dr.line(pp,fill=cols[s['name']],width=1);sv.append('<polyline fill="none" stroke="'+cols[s['name']]+'" points="'+' '.join(f'{x:.2f},{z:.2f}' for x,z in pp)+'"/>')
pp=[xy([p[0],p[2]]) for p in pts];dr.line(pp,fill='#d59100',width=3);sv.append('<polyline fill="none" stroke="#d59100" stroke-width="2" points="'+' '.join(f'{x:.2f},{z:.2f}' for x,z in pp)+'"/>')
floor=r['new_reference_floor_bodyrelative_Z_mm'];aa=xy([-155,floor]);bb=xy([25,floor]);dr.line([aa,bb],fill='#b32030',width=2);sv.append(f'<line x1="{aa[0]}" y1="{aa[1]}" x2="{bb[0]}" y2="{bb[1]}" stroke="#b32030"/>')
txt(740,96,f'Actual XZ section at Y={r["sections"][0]["Y_mm"]:.6f} / local floor hazard',ff=small)
xy2=lambda v:(745+(v[0]+40)/13*660,490-(v[1]+82)/10*350)
for s in r['sections']:
 if s['name'] not in ['D','V','G']:continue
 for line in s['curves_xz']:
  pp=[xy2(v) for v in line]
  if len(pp)>1:dr.line(pp,fill=cols[s['name']],width=3);sv.append('<polyline fill="none" stroke="'+cols[s['name']]+'" stroke-width="2" points="'+' '.join(f'{x:.2f},{z:.2f}' for x,z in pp)+'"/>')
aa=xy2([-40,floor]);bb=xy2([-27,floor]);dr.line([aa,bb],fill='#b32030',width=2);sv.append(f'<line x1="{aa[0]}" y1="{aa[1]}" x2="{bb[0]}" y2="{bb[1]}" stroke="#b32030"/>');point=xy2([r['minimum_profile_point_mm'][0],r['minimum_profile_point_mm'][2]]);dr.ellipse((point[0]-5,point[1]-5,point[0]+5,point[1]+5),fill='#b32030')
txt(25,510,'Actual case / Foot outlines are context only: case and Ankle clearance pairs remain UNRECEIVED.',ff=small)
lines=[
 'Loop family: real nominal source frames -> long C/S -> left passage; perpose shape changes, R >=35.1.',
 '55/10 planning allowance placed into radius growth; SOURCE-FL2 loop axial allocation318.676960mm.',
 'First reserved-profile ground HOLD: pose33/G, R44.678427, lower -0.599916mm vs required +1.25mm.',
 'Native local3short profiles valid; G below-floor volume9.106753mm3; actual surface point corroborates minimum.',
 'Ground gate303/324 rows +21 UNRECEIVED; case/Ankle/entryfan/roll/coallocation/whole stock remain OPEN.',
 'At R35.1 samefamily ground-only lower: Hip14.591541 / KneeFL2 7.598338 / donorFL3 8.435519mm.',
 'Those are ground diagnostics, NOT accepted whole paths. This rejects radius-storage, not minR35.1.',
 'NEXT: retain R35.1 and move stored length into separate axial/lateral return bay, not scalar radius/pose retry.',
 'Left body passage/contour/moving-interface evidence unchanged; no new leading material or V3 detail.',
 'Default torus bbox metric rejected; optimal bounds + on-BRep witness + below-floor common used.',
 'All9IDs12portions4MAX3 A/U/minfit/slack NULL; source14/11/9/lap4/850/900/factory units preserved.',
 'Native26064/46493 IDLE / pendingnull / unsavedfalse. N01=0/10; active24h window retained.'
]
for i,t in enumerate(lines):txt(25,550+i*37,t,'#b32030' if i in [2,4,6,10] else '#152238')
png='day07-SOURCE-adaptive-loop-ground-received-view.png';svg=png.replace('.png','.svg');im.save(out/png);(out/svg).write_bytes(('<svg xmlns="http://www.w3.org/2000/svg" width="1450" height="1050"><rect width="1450" height="1050" fill="#f5f6f8"/>'+''.join(sv)+'</svg>').encode())
names=[pn,gn,ln,r['archive'],png,svg]
for src in ['robot-cat59-save-adaptive-loop-whole-proposal.py','robot-cat59-full-profile-ground-first-falsifier.py','robot-cat59-ground-local-profile-proof.py','robot-cat59-render-close-adaptive-ground.py']:
 n='day07-'+src.removeprefix('robot-cat59-').removesuffix('.py')+'.recipe.py';assert not(out/n).exists();(out/n).write_bytes((temp/src).read_bytes());names.append(n)
checks=[]
with zipfile.ZipFile(out/r['archive']) as z:
 assert z.testzip() is None;ge=json.loads(z.read('manifest.json'))['geometry'];assert len(ge)==7
 for q in ge:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
 checks.append(dict(path=r['archive'],crc_ok=True,member_sha_verified=7))
p=out/'day07-SOURCE-adaptive-entry-storage-bounded-disposition.json';assert not p.exists()
nextstep='CONSTANT_RADIUS_AXIAL_OR_LATERAL_RETURN_STORAGE: leftbodypassageclosed andsourceholder21unchanged. ThisONEfamily failedbecauseentire55/10planningallowancewasstoredbyradiusgrowthdirecteddownward; R35.1ground-onlybaselinepositiveNOTwholecasefit. ChooseONEactualaccessibleexternalKnee6/Hip3returnbay withR>=35.1fixedarcs+variableSTRAIGHT/3Dreturnleglength (store55/10outsidefloor-limitedarc), fullprofiles/currentcase/Ankle/stock/movingreserve beforematerial. No loweringR/slack/margins/55waiver/sourceportpose/PCBscalarretry or allmanualpaths/shortageclaim. Sourceconnectoraxis remainsprojectprovisional, notmanufacturerimmutable; preservefullfactoryend/source14 andcurrentselectedpointuntilsource-backedwholeinterfaceproof. Actualnewentryfan/roll/bodyDGV/enddebits/all9ID12portion4MAX3/A/U/minfit/slack stillOPEN; no oldprefix/chordcredit/V3detail/newreview.'
sources=[dict(path=n,sha256=sha(out/n)) for n in ['day07-SOURCE-left-end-body-passage-bounded-disposition.json','day07-SOURCE-motion36-and-group-return-bounded-disposition.json','day07-SOURCE-new-moving-module-region-first-gate.json','day07-SOURCE-new-motion-frozen-input-projection.json','day07-SOURCE-slot-bearing-retention-bounded-disposition.json','n01-selected-piece-profile-contract.json','day07-whole-physical-SOURCE-approach-Knee-link-proposal.json']];sourcepath=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint/leg-source-near-member-plan.json';sources.append(dict(path=str(sourcepath.relative_to(root)).replace('\\','/'),root='MECH',sha256=sha(sourcepath)))
x=dict(id=p.stem,status='ADAPTIVE_LONG_RETURN_RADIUS_STORAGE_FULL_RESERVED_PROFILE_FLOOR_HOLD_NO_SOURCE_SELECTION',selected=False,N01_complete=False,whole_hypothesis=dict(proposal=pn,groups=[dict(name=q['spec']['name'],IDs=q['spec']['ids'],full_triplet_cross_mm=q['full_triplet_cross_mm'],min_R_mm=35.1,allocated_axial_loop_mm=q['loop_axial_allocation_mm'],planned_extra_mm=q['spec']['reserve']) for q in prop['groups']],meaning='Oneadaptiveregionfamily, distinctperposesameconstantloopaxialallocation; scalarinverseONLYlengthidentitynotclearancetuning/newvariant. Allsource/currentfullprofiles/factorysource14unchanged; bodyentryisaccountingnotY-terminal. Knee6branchcoallocationNOTreceived.'),
 first_falsifier=g['first_falsifier'],source_wire_at_first_falsifier='W021/SOURCE_FL2/G',ground_counter=dict(cursor=303,total=324,unreceived=21,stop_after_first_full_profile_HOLD=True),native_local_proof=dict(profile_rows=r['profile_rows'],below_floor_reserved_volume_mm3=r['full_reserved_G_below_floor_mm3'],minpoint_mm=r['minimum_profile_point_mm'],minpoint_on_BRep_gap_mm=r['minimum_profile_point_actual_BRep_gap_mm'],profile_BRep_min_vs_analytic_delta_mm=r['analytic_vs_BRep_Zmin_delta_mm'],only_short_critical_arc=True),
 classification='Chosenstorageallocationfails FULLreservedprofile/floor1.25, NOTdeliveredwirecontact, allmanualfreefleximpossibility, actualrequiredphysicalreserve55orstockshortage. R35.1notrejected; no loweringOD/R/floor/margins. 55/10plannedreservesNOTacceptedstoredslack/minfit; groupcentreline318etcNOTwholefactorydebit.',
 baseline_samefamily_R35p1_ground_diagnostic=g['baseline_minR_ground_diagnostic'],unreceived=dict(case_and_Ankle_collision_pairs=0,context_BRep_exports_are_not_collisionproof=True,entryfan_roll=False,three_branch_coallocation=False,source_external_envelope_and_movingreserve_space=False,bodyDGVfans_and_enddebits=False,all_A_U_minimum_fit_slack=None,initial_assembly=False),input_quality=r['input_quality_disposition'],geometry_metric_repair_NOT_design_failure=True,
 source_endpoint_function=dict(connector_datums_provisional=True,pin_cavity_order_known=False,factory_plugs_installed_per_source=1,project_connector_choice=0,current_chosen_source14_points_axes_preserved=True,source_axis_NOT_called_manufacturerimmutable=True,no_pinout_or_cut_inferred=True),
 unchanged='Actualleftbodypassage9.4x10.5/37.75/all1443min2.05/BodyOuter3.25/new35x129min3.163420 remainsclosedSCOPED. Current1292/effective1311/rest108a9f78e06/2d1d8cfa/def3e56a unchanged/newSource21+4tempPROPOSED. OriginalBankBedretained, oldunselectedguide8notreactivated/root105nottransferred. SOURCE4ties/MODULE2/fourindependent220/both4MTA preserved; no material/holderbuilt.',
 guards='R47/P0/E6/15drives/MG92B/MAIN46.52/325x200x160/max200/256cube/foreign1.25/BodyOuter3.25. 9IDs12portions4physicalMAX3original+donor/source14terminal11full9lap4once/3x8laps3x20sleeves/stagger2x9/850project/900ceil5(min+20)perunit/no pool/oldprefix/chordcredit/actualcutNULLphase2. AlloldSOURCE/V3/S0/quarters/Pi45/vertical/reviewcounts retained.',next=nextstep,global_open='WholeSOURCEadaptiveaccessibleR/loopstorage/entryfan/root/physicalstock/initialassembly;whole123246/U1far/headNorth/4MTA/Pimates/R6/invalid3/lengthslack/motionoutline. No N01point/fullN03N08N09N10.',source_pins=sources,packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=checks,
 timings=dict(successful_native_local_proof_operation_seconds=r['operation_seconds'],successful_native_local_proof_process_CPU_seconds=r['process_cpu_seconds'],scope='ONLYtimedfinalnativegroundproof; notwholechunkCPU. Initialdefault-bboxdiagnosticattemptandmetadataanalyticsNOTtimed/no inventedCPU or wall-as-CPU.'),view=dict(path=png,source=ln,actual_section_Y_mm=r['sections'][0]['Y_mm'],visual_inspection='PENDING_OWNER_VIEW',projection_not_contact_proof=True),native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False,identity_received='OWNER59_IDLE26064 1292/1311/108 pendingnull unsavedfalse'),written_utc=datetime.now(timezone.utc).isoformat());p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(dict(receipt=p.name,sha256=sha(p),files=len(names)+1,archive_checks=checks,view=png),indent=2))
