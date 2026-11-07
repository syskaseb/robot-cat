from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,math,os,subprocess,html
from PIL import Image,ImageDraw,ImageFont
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pn='day07-SOURCE-constant-radius-axial-return-whole-proposal.json';gn='day07-SOURCE-constant-radius-axial-storage-ground-gate.json';ln='day07-SOURCE-constant-radius-axial-ground-local-proof.json';prop,g,r=[json.loads((out/n).read_bytes()) for n in [pn,gn,ln]];f=g['first_falsifier'];st=prop['groups'][f['group_index']]['states'][f['pose']];q=st['route'];d=st['extension_mm'];cap=next(c for c in g['conditional_storage_capacity'] if c['group']=='KNEE3_CONTINUOUS_FL2');assert f['pose']==35 and f['R_mm']==35.1 and g['cursor']==321 and g['unreceived']==3;assert r['full_reserved_G_below_floor_mm3']>0 and cap['minimum_extra_must_move_OUT_OF_THIS_BAY_mm']>14
im=Image.new('RGB',(1450,1080),'#f5f6f8');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24);sv=[]
def txt(x,y,t,col='#152238',ff=None):
 dr.text((x,y),t,font=ff or font,fill=col);sv.append(f'<text x="{x}" y="{y+20}" fill="{col}" font-family="Arial" font-size="19">{html.escape(t)}</text>')
txt(25,14,'SOURCE fixedR35.1 axial return: selected planar storage HOLD',ff=bold)
txt(25,52,'Full reserved profiles / unchanged floor; NOT delivered-wire contact, stock shortage or all3D loop impossibility.')
pts=[q['P'],[q['P'][i]+d*q['T'][i] for i in range(3)]]
for j in range(41):
 t=math.pi*j/40;pts.append([q['P'][i]+d*q['T'][i]+35.1*(math.sin(t)*q['T'][i]+(1-math.cos(t))*q['N'][i]) for i in range(3)])
pts.append([q['P'][i]+70.2*q['N'][i] for i in range(3)])
for j in range(41):
 t=math.pi+(q['theta_radians']-math.pi)*j/40;pts.append([q['P'][i]+35.1*(math.sin(t)*q['T'][i]+(1-math.cos(t))*q['N'][i]) for i in range(3)])
pts.append(q['Q']);cols={'D':'#2371b6','V':'#6c798a','G':'#b32030','Ref_Material_P0_Part__Feature056_0_0':'#65828b','Ref_Material_P0_Part__Feature123_0_0_0':'#8b8e96'};txt(25,96,'XZ projection / actual posed case+Foot / candidate group path',ff=small);xy=lambda v:(25+(v[0]+155)/180*660,490-(v[1]+100)/170*350)
for ss in r['context_projections']:
 for line in ss['curves_xz']:
  pp=[xy(v) for v in line]
  if len(pp)>1:dr.line(pp,fill=cols[ss['name']],width=1);sv.append('<polyline fill="none" stroke="'+cols[ss['name']]+'" points="'+' '.join(f'{x:.2f},{z:.2f}' for x,z in pp)+'"/>')
pp=[xy([p[0],p[2]]) for p in pts];dr.line(pp,fill='#d59100',width=3);sv.append('<polyline fill="none" stroke="#d59100" stroke-width="2" points="'+' '.join(f'{x:.2f},{z:.2f}' for x,z in pp)+'"/>');floor=r['new_reference_floor_bodyrelative_Z_mm'];aa=xy([-155,floor]);bb=xy([25,floor]);dr.line([aa,bb],fill='#b32030',width=2);sv.append(f'<line x1="{aa[0]}" y1="{aa[1]}" x2="{bb[0]}" y2="{bb[1]}" stroke="#b32030"/>')
txt(740,96,f'Actual local XZ section Y={r["sections"][0]["Y_mm"]:.6f}',ff=small);xc=r['minimum_profile_point_mm'][0];xy2=lambda v:(745+(v[0]-(xc-6))/13*660,490-(v[1]-(floor-3))/10*350)
for ss in r['sections']:
 if ss['name'] not in ['D','V','G']:continue
 for line in ss['curves_xz']:
  pp=[xy2(v) for v in line]
  if len(pp)>1:dr.line(pp,fill=cols[ss['name']],width=3);sv.append('<polyline fill="none" stroke="'+cols[ss['name']]+'" stroke-width="2" points="'+' '.join(f'{x:.2f},{z:.2f}' for x,z in pp)+'"/>')
aa=xy2([xc-6,floor]);bb=xy2([xc+7,floor]);dr.line([aa,bb],fill='#b32030',width=2);sv.append(f'<line x1="{aa[0]}" y1="{aa[1]}" x2="{bb[0]}" y2="{bb[1]}" stroke="#b32030"/>');pt=xy2([xc,r['minimum_profile_point_mm'][2]]);dr.ellipse((pt[0]-5,pt[1]-5,pt[0]+5,pt[1]+5),fill='#b32030')
txt(25,510,'Case / Foot geometry is context only; case/Ankle/coallocation checks remain UNRECEIVED.',ff=small)
lines=[
 'R35.1 FIXED; first semicircle moves+dT, two straight legs2d; material allocation unchanged, no radius growth.',
 'Pose35 / W021-G / SOURCE-FL2: d27.5mm gives full reserved profile ground lower -0.944077mm.',
 'Native local3profiles valid; below-floor reserved G volume15.171042mm3; on-BRep minimum corroborated.',
 'Ground321/324 +3 UNRECEIVED; source case/Ankle/entryfan/roll/wholewire stock still OPEN.',
 'This chosen plane+flat-B roll: floor-only extra capacity <=40.873522mm versus planned55mm.',
 'Therefore >=14.126478mm must leave THIS bay if this plane/roll retained; NOT a wire-stock shortage.',
 'Upper bound is NOT available storage: cases/packing may reduce it. Other3D orientations are unqualified.',
 'NEXT: whole perphysical SOURCE-FL2 leg+body-DGV reserve allocation, keep total55; do not borrow donor slack.',
 'No third local loop/offset/shorterR/margin waiver. Left body passage and oldrigid21 proof unchanged.',
 'All9IDs12portions4MAX3 A/U/minfit/slack NULL; source14/11/9/lap4/850/900/phase2cutNULL preserved.',
 'Prospective U1 leading root/material NOT accepted or built; old105root not transferred. N01=0/10.',
 'Native26064/46493 IDLE / pendingnull / unsavedfalse; active24h window retained.'
]
for i,t in enumerate(lines):txt(25,550+i*38,t,'#b32030' if i in [1,3,4,5,9] else '#152238')
png='day07-SOURCE-constant-radius-axial-ground-received-view.png';svg=png.replace('.png','.svg');im.save(out/png);(out/svg).write_bytes(('<svg xmlns="http://www.w3.org/2000/svg" width="1450" height="1080"><rect width="1450" height="1080" fill="#f5f6f8"/>'+''.join(sv)+'</svg>').encode())
names=[pn,gn,ln,r['archive'],png,svg]
# Existing published analytic definitions, not an ephemeralTemp dependency.
sp=temp/'robot-cat60-save-constant-radius-whole-proposal.py';ss=sp.read_text(encoding='utf-8-sig');ss=ss.replace("src=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat59-save-adaptive-loop-whole-proposal.py').read_text(encoding='utf-8-sig')","src=(out/'day07-save-adaptive-loop-whole-proposal.recipe.py').read_text(encoding='utf-8-sig')");sp.write_bytes(ss.encode())
for source in ['robot-cat60-save-constant-radius-whole-proposal.py','robot-cat60-constant-radius-ground-and-capacity.py','robot-cat60-constant-R-local-ground-proof.py','robot-cat60-render-close-constant-radius.py']:
 n='day07-'+source.removeprefix('robot-cat60-').removesuffix('.py')+'.recipe.py';assert not(out/n).exists();(out/n).write_bytes((temp/source).read_bytes());names.append(n)
checks=[]
with zipfile.ZipFile(out/r['archive']) as z:
 assert z.testzip() is None;ge=json.loads(z.read('manifest.json'))['geometry'];assert len(ge)==7
 for qq in ge:assert hashlib.sha256(z.read(qq['entry'])).hexdigest()==qq['sha256']
 checks.append(dict(path=r['archive'],crc_ok=True,member_sha_verified=7))
p=out/'day07-SOURCE-constant-radius-storage-bounded-disposition.json';assert not p.exists()
nextstep='WHOLE_PER_PHYSICAL_LEG_AND_BODY_DGV_RESERVE_ALLOCATION: twochosenlocalstorageforms(radiusgrowthandfixedRsource-forwardstadium)failfloorwithfull55inthisplane/flatBroll. No thirdlocalcurve/scalaroffset/shorterR/55waiver. Thisplane/roll SOURCEFL2 floor-only ceiling40.873522 extra, so >=14.126478 ofplanned55mustmoveoutsideTHISbay ifsameplane/rollretained; othercase/packingconstraints maylowerceiling. ChooseactualconnectedbodyD3/G3/V3regions+legspace andreservepercoreofSAMEphysicalSOURCEFL2, total55unchanged; no donor/Hip/spare/20fittrim pooling. Other3D/rollsolutionsnotruledoutbut requirewhole source/currentcase/Ankle/ground/space/stockproof, notthirdlegnudge. Actualleftbodypassageclosed/rigid21unchanged. Perphysical900MAX3/850/ends/source14terminal11full9lap4once/3x8/3x20/stagger2x9/fullfactory/sourceoriginal+donor/all9ID12portions actualA/U/minfit/slackNULL untilqualifiedgrouptransport/bodyDGVends. ProspectiveU1leadingroot/functions/accessbeforematerial/V3, no old105transfer/newreview.'
x=dict(id=p.stem,status='CONSTANT_R_AXIAL_STORAGE_FLOOR_HOLD_CONDITIONAL_CAPACITY_IDENTIFIED_NO_THIRD_LOCAL_RETURN',selected=False,N01_complete=False,whole_hypothesis=dict(proposal=pn,R_mm=35.1,extra_length_method='TwoaxialSTRAIGHTlegs2d+translatedfirstsemicircle; tangentcontinuous, allR35.1, no radius/pose/sourcepointtuning.',groups=[dict(name=qq['spec']['name'],ids=qq['spec']['ids'],R_mm=35.1,loop_axial_allocation_mm=qq['loop_axial_allocation_mm'],extra_planned_mm=qq['spec']['reserve']) for qq in prop['groups']],three_branch_coallocation=False,source_case_stock_fullneighborhood_NOT_qualified=True),
 first_falsifier=f,first_wire='W021/G/SOURCE_FL2 inproposedpackingnotmanufacturerpincavity',ground_counter=dict(cursor=321,total=324,unreceived=3,first_falsifier_stop=True),native_local_confirmation=dict(profile_rows=r['profile_rows'],full_reserved_G_below_floor_mm3=r['full_reserved_G_below_floor_mm3'],point_on_BRep_gap_mm=r['minimum_profile_point_actual_BRep_gap_mm'],minimum_profile_point_mm=r['minimum_profile_point_mm'],analytic_vs_optimal_bound_delta_mm=r['analytic_vs_BRep_Zmin_delta_mm'],short_profile_span_mm=35.1*.24,scope='ReservedfullprofileONLYnotdeliveredwirecontact/wholefreewiremodel.'),
 conditional_capacity=cap,capacity_classification=g['capacity_scope'],required_redistribution_is_not_physical_stock_shortage=True,shared_allocation_counterexample='No capacityborrowfromDONOR_FL3/Hip/no physicalextra55minimumclaim. SOURCEFL2globalpercoreboughtstock/cut/wholeminfitunknown; groupcentreline318.67696isNOTwholeunitwiredebit.',
 unresolved=dict(current_sourcecase_and_Ankle_clearance_pairs=0,context_export_not_contact_proof=True,fullexternalbay_and_exposure=False,entryfan_roll=False,three_branch_coallocation=False,bodyDGVregiontransport_and_ends=False,percore_upperlength_and_actualstoredslack=None,initial_assembly=False,new_U1_leading_root=False),input_quality='NEWpartialtorususesanalytic/optimalbounds+actualonshapeproof+validbelowfloorcommon, rawdefaultBBoxNOTminimum. No olderacceptedsourceboundaudit/replay.',
 historical_negatives='Preservepriorradiusstoragepose33W021G/R44.678427/lower-.599916/303of324/21unreceived; priorquarters402.0793of33/30unreceived,78.3508221of34/33unreceived,Hipnorth20.05outline,shortCS22of36/alloldSOURCE/V3/S0/Pi45/reviewcounts. ThisisONEdistinctaxialfunctionalstorageplan, notC2radius/poseoffset/wholeR35impossibility.',
 unchanged='Actualleftbodypassage1697b075/37.75/full9.4x10.5/BodyOuter3.25/all1443min2.05/new4515coversmin3.163420 retained. Current1292/effective1311/rest108a9f78e06/2d1d8cfa/def3e56a/newSource21+4tempunchanged. No oldrigid21motion155/sourceworld/static/root/quarterreplay/newmaterial. OriginalBankBedretained/oldunselected8guideoverlaynotreactivated/old105rootnottransferred. SOURCE4ties/MODULE2/fourindependent220/both4MTA unchanged.',
 guards='R47/P0/E6/15drives/MG92B/MAIN46.52/325x200x160/max200/256cube/foreign1.25/BodyOuter3.25; source14terminal11full9lap4once/3x8laps3x20sleeves/stagger2x9/850/900ceil5(min+20)MAX3/actualcutNULLphase2/no oldprefix/chordcredit/pool/20trimdouble slack. Group35.1projectcapacitynotmanufacturerminimum, selected12.4percoreunchanged/no shorterRwaiver.',
 next=nextstep,global_open='WholeSOURCE/bodyDGV/currentlengthslack/mount/entryfan/initialassembly;global123246/U1far/headNorth/four220/4MTA/Pimates/R6/invalid3/motionoutline/wholeN01.',source_pins=[dict(path=n,sha256=sha(out/n)) for n in ['day07-SOURCE-adaptive-entry-storage-bounded-disposition.json','day07-SOURCE-left-end-body-passage-bounded-disposition.json','day07-SOURCE-new-motion-frozen-input-projection.json','day07-SOURCE-new-moving-module-region-first-gate.json','day07-SOURCE-slot-bearing-retention-bounded-disposition.json','n01-selected-piece-profile-contract.json','day07-whole-physical-SOURCE-approach-Knee-link-proposal.json','day07-S0-C1-current-candidate-composition.json']],packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=checks,timings=dict(native_local_proof_operation_seconds=r['operation_seconds'],native_local_proof_process_CPU_seconds=r['process_cpu_seconds'],scope='Onlymeasurednativechangedlocalproof; metadataanalytics/render notCADCPU orwall-as-CPU.'),view=dict(path=png,source=ln,actual_sectionY_mm=r['sections'][0]['Y_mm'],visual_inspection='PENDING_OWNER_VIEW',projection_not_contact_proof=True),native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False),written_utc=datetime.now(timezone.utc).isoformat());p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(dict(receipt=p.name,sha256=sha(p),files=len(names)+1,archive_checks=checks,view=png),indent=2))
