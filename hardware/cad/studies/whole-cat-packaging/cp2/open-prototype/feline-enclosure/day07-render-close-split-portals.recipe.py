from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,math,os,subprocess,html
from PIL import Image,ImageDraw,ImageFont
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
propname='day07-SOURCE-split-Knee6-Hip3-portals-whole-proposal.json';gn='day07-SOURCE-split-portals-capacity-outline-first-gate.json';sn='day07-SOURCE-split-portals-actual-blocker-source-read.json';prop,g,s=[json.loads((out/n).read_bytes()) for n in [propname,gn,sn]]
assert g['Knee6_full_region']['cursor']==3 and g['Knee6_full_region']['unreceived']==30 and s['isSame_Current1292'];assert abs(g['Knee6_full_region']['rows'][0]['gap_mm']-1.591)<1e-6;assert abs(g['Hip3_north_outline']['excess_past_margin_mm']-20.05)<1e-6
im=Image.new('RGB',(1450,1010),'#f5f6f8');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24);svg=[]
def txt(x,y,t,col='#152238',f=None):
 dr.text((x,y),t,font=f or font,fill=col);svg.append(f'<text x="{x}" y="{y+20}" fill="{col}" font-family="Arial" font-size="19">{html.escape(t)}</text>')
txt(25,13,'SOURCE split Knee6 / Hip3: U1 layer cleared locally; whole allocation HOLD',f=bold)
txt(25,50,'Existing guide/root/pose and fullprofiles unchanged. No new holders, old motion, wire cuts or selected overlay.')
colors={'actual_retained_P0_MountFrontL':'#8950a1','actual_current_U1carrier':'#b65257','allocated_Knee6_south_region':'#d59100','actual_BankBedguide':'#2371b6'}
for k,y in enumerate([37.394595088058644,55]):
 x0=25+475*k;txt(x0,96,'Actual section Y'+('37.394595 (witness)' if k==0 else '55 / U1 layer'),f=small);panel=Image.new('RGB',(450,340),'white');pd=ImageDraw.Draw(panel)
 def xy(v):return((v[0]+92)/56*450,340-(v[1]-31)/34*340)
 svg.append(f'<defs><clipPath id="p{k}"><rect x="{x0}" y="135" width="450" height="340"/></clipPath></defs><g clip-path="url(#p{k})">')
 for sec in s['sections']:
  if abs(sec['value_mm']-y)>1e-6:continue
  for line in sec['curves_xz']:
   pts=[xy(q) for q in line]
   if len(pts)>1:
    col=colors[sec['name']];pd.line(pts,fill=col,width=3);svg.append('<polyline fill="none" stroke="'+col+'" stroke-width="2" points="'+' '.join(f'{x+x0:.2f},{z+135:.2f}' for x,z in pts)+'"/>')
 svg.append('</g>');im.paste(panel,(x0,135))
x0=975;txt(x0,96,'Plan XY / fields, not contact proof',f=small)
def plan(x,y):return(x0+(x+90)/52*435,475-(y-20)/105*340)
for cy,zcol,start,end in [(67,'#d59100',-90,0),(77,'#25855b',0,90)]:
 for rr in [30.4,39.8]:
  pts=[plan(-84.1+rr*math.cos(math.radians(a)),cy+rr*math.sin(math.radians(a))) for a in range(start,end+1,2)]
  dr.line(pts,fill=zcol,width=3);svg.append('<polyline fill="none" stroke="'+zcol+'" stroke-width="2" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+'"/>')
 for a in [start,end]:
  p1=plan(-84.1+30.4*math.cos(math.radians(a)),cy+30.4*math.sin(math.radians(a)));p2=plan(-84.1+39.8*math.cos(math.radians(a)),cy+39.8*math.sin(math.radians(a)));dr.line([p1,p2],fill=zcol,width=3)
for yy,col in [(100,'#b65257'),(96.75,'#b65257')]:
 p1=plan(-90,yy);p2=plan(-38,yy);dr.line([p1,p2],fill=col,width=2);svg.append(f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="{col}"/>')
txt(980,140,'Hip3 full Ymax116.8',col='#25855b',f=small);txt(980,468,'BodyYmax100 / limit96.75',col='#b65257',f=small)
for i,(n,col) in enumerate([('Actual P0mount','#8950a1'),('Actual U1carrier','#b65257'),('Knee6 allocated region','#d59100'),('Hip3 allocated region','#25855b')]):txt(25+i*350,505,n,col,f=small)
lines=[
 'Knee6 full9.4x7.2/R35.1: U1 gap1.591 >=1.25; C30 gap14.271609; first P0mount capacity HOLD.',
 'Actual MountFrontL / allocated Knee6 common402.079000mm3;3/33 received +30 UNRECEIVED.',
 'Source actor isSame current1292 TRUE; real bounds[-84,27.5,35.92]..[-57.5,37.8,61]. No own-by-name.',
 'Hip3 full9.4x3.9/R35.1 north quarter Ymax116.8 vs fixedbody margin limit96.75: exceeds20.05mm.',
 'Both are THIS ALLOCATION failures; NOT actual flexible wire contact or all3D approach impossibility.',
 'Planned motion allowance Knee6=55 / Hip3=10mm; stored capacity and all whole-wire fit/slack UNQUALIFIED.',
 'Existing passive guide is not an electrical port/extra9 terminal. New portal seam NOT received after stop.',
 'NEXT: actual retained P0 frame passage + whole entryfan topology before another turn or printed detail.',
 'No third quarter offset/guide height/PCB pose/shorterR. All9IDs12portions4MAX3 current A/U/fit/slack NULL.',
 'Previous new21 motion36/root105/embed26.25 unchanged SCOPED. Full flex/BodyOuter/R6 still OPEN.',
 'Native26064/46493 IDLE / pendingnull / unsavedfalse. N01=0/10; active24h window retained.'
]
for i,t in enumerate(lines):txt(25,550+i*38,t,'#b32030' if i in [1,3,4,8] else '#152238')
png='day07-SOURCE-split-portals-capacity-outline-received-view.png';svgn=png.replace('.png','.svg');im.save(out/png);(out/svgn).write_bytes(('<svg xmlns="http://www.w3.org/2000/svg" width="1450" height="1010"><rect width="1450" height="1010" fill="#f5f6f8"/>'+''.join(svg)+'</svg>').encode())
names=[propname,gn,g['archive'],sn,s['archive'],png,svgn]
for src in ['robot-cat57-save-split-portals-whole-proposal.py','robot-cat57-split-portals-first-capacity-gate.py','robot-cat57-save-actual-frame-blocker-read.py','robot-cat57-render-close-split-portals.py']:
 n='day07-'+src.removeprefix('robot-cat57-').removesuffix('.py')+'.recipe.py';(out/n).write_bytes((temp/src).read_bytes());names.append(n)
checks=[]
for n in names:
 if n.endswith('.zip'):
  with zipfile.ZipFile(out/n) as z:
   assert z.testzip() is None;ge=json.loads(z.read('manifest.json'))['geometry']
   for q in ge:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
   checks.append(dict(path=n,crc_ok=True,member_sha_verified=len(ge)))
p=out/'day07-SOURCE-split-portals-bounded-disposition.json'
nextstep='ACTUAL_P0_FRAME_PASSAGE_BEFORE_PASSIVE_GUIDE_ENTRY_FAN: PreserveMountFrontLactualmaterial/currentU1realfunctions, fixed105root/guide/new21motion evidence. Two body-end quarter templates(full9south andsplit6south3north) faileddifferentactualconstraints; NO third scalarquarter/guideheight/PCBoffset/shorterR. ChoosewholeexternalKnee6/Hip3 passage/layorder fromactualretainedframeopening andcurrentneighbors BEFOREimposingaY-tangentquarterataNONTERMINALpassiveaccountingguide. FullR35.1/fullprofiles/functionalrealendreliefs/assembly/55and10plannedreserve mustfitaccessibleconnectedspace; ifguide/loadinterface trulyneedswholechange proveactualmaterial/functions andinvalidateonlychangedinterfaces. No new material orV3details beforecredibleactualsource/bodyapproach andall9ID12portion4physicalMAX3 budgets. No oldprefix/chordcredits/all3Dshortageclaim.'
r=dict(id=p.stem,status='SPLIT6_3_ALLOCATION_REJECTED_P0_MATERIAL_AND_NORTH_FIXED_OUTLINE_NO_THIRD_QUARTER',selected=False,N01_complete=False,
 new_fact=dict(Knee6_current_U1_gap_mm=g['Knee6_full_region']['rows'][0]['gap_mm'],Knee6_C30_gap_mm=g['Knee6_full_region']['rows'][1]['gap_mm'],Knee6_first_falsifier=g['Knee6_full_region']['first_falsifier'],cursor=3,total=33,unreceived=30,whole_Knee6_path_NOT_qualified=True,guide_entry_own_seam_NOT_qualified=True,actual_source_identity=s['isSame_Current1292'],actual_source_actor=s['source_actor'],actual_source_bounds_mm=s['actual_source_world_bounds_mm'],actual_source_export=s['geometry'][0],cached_allocated_common=s['cached_common_mm3']),
 independent_outline_falsifier=g['Hip3_north_outline'],classification='Botharecapacity/allocatedgroupplanfailures, NOTactualinstalledwirecontact/allmanualfreeflexpaths impossible/physicalshortage. Northfixedfieldnotmovinglegexposure. CurrentMountFrontL retainedmaterialreal; no manufacturingmaterial/ownstatusfromname. StopatfirstKnee6falsifier/no30replay/northotherpairs0.',
 whole_hypothesis=dict(proposal=propname,actual_guide_two_portals=True,upper6_south_and_lower3_north=True,guide_root_pose_material_unchanged=True,all9ID12physicalportions=prop['physical_portion_rows'],planned_moving_reserve=prop['planned_motion_reserve'],actual_A_U_minimum_fit_slack=None,assembly_received=False,full_external_bay_capacity_received=False),
 historical_negatives='Oldfull9southquarter78.3508221of34/33unreceived,shortCS22of36,oldV3/SOURCE/S0/Pi45/vertical/counts remainfrozen. Newsplitplan isnotnewwirecontact/wirestockshortage; no sourceworld/reopen/static/root/guide/new21motion36replay. No resettingoldreview1of1/no thirdquarter.',
 unchanged_context='Current1292/effective1311/rest108a9f78e06/2d1d8cfa/def3e56a unchanged; proposedBankBedoverrideef81a623/d42f3671ONCE excludesoldparent/provedpadaliases andproposedmoving21+4temp retained. OldrejectsNOTcurrent. Root105/embed26.25/9members7joints/source4ties/MODULE2/fourindependent220/both4MTA unchanged.',
 source_invariants='R47/P0/E6/15drives/MG92B/MAIN46.52/325x200x160/max200/256cube/foreign1.25/BodyOuter3.25. Source14terminal11full9lap4once/3x8laps3x20sleeves/stagger2x9lands/850project/900ceil5(min+20)MAX3perphysicalunit/factoryplug/actualcutNULLphase2. No pool/oldprefix/chordlength/20fittrimasslack.',
 next=nextstep,global_open='WholeSOURCEexternalapproach+entryfan/R/roll/movingreserve/storage/ALL9/12/4sourcebudgets;123246/U1far/headNorth/Pimates/R6/invalid3/changedoutline/fullinitialassembly/wholeN01.',source_pins=[dict(path=n,sha256=sha(out/n)) for n in ['day07-SOURCE-motion36-and-group-return-bounded-disposition.json','day07-SOURCE-pad-conforming-guide-bounded-disposition.json','day07-S0-C1-current-candidate-composition.json','day07-SOURCE-body-approach-proposed-moving-context.json','n01-selected-piece-profile-contract.json','day07-coordinator-SOURCE-splice-layout-authority-receipt.json']],packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=checks,
 timings=[dict(receipt=n,operation_seconds=q['operation_seconds'],process_cpu_seconds=q['process_cpu_seconds']) for n,q in [(gn,g),(sn,s)]],view=dict(path=png,source=sn,actual_section_y_mm=[37.394595088058644,55],outline_plan='Analyticprojectionofnewfullregion; BodyOuterbboxnecessaryrejectionNOTcontact',visual_inspection='PENDING_OWNER_VIEW'),native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False,identity_received='OWNER57_IDLE26064 1292 1311 108 pendingnull unsavedfalse'),written_utc=datetime.now(timezone.utc).isoformat())
p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(dict(receipt=p.name,sha256=sha(p),files=len(names)+1,archive_checks=checks,view=png),indent=2))
