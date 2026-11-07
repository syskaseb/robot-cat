from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,math,html,os,subprocess
from PIL import Image,ImageDraw,ImageFont
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pn='day07-SOURCE-FL2-body-reserve-and-DGV-whole-proposal.json';gn='day07-SOURCE-FL2-body-reserve-first-gate.json';cn='day07-SOURCE-FL2-body-reserve-continuation.json'
prop,g,c=[json.loads((out/n).read_bytes()) for n in [pn,gn,cn]];assert c['cursor']==4 and c['first_falsifier'] is None
im=Image.new('RGB',(1400,940),'#f5f6f8');dr=ImageDraw.Draw(im);ff=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24);sv=[]
def txt(x,y,s,col='#152238',font=None):
 dr.text((x,y),s,font=font or ff,fill=col);sv.append(f'<text x="{x}" y="{y+18}" fill="{col}" font-family="Arial" font-size="18">{html.escape(s)}</text>')
def line(pp,col,width=2):
 if len(pp)>1:dr.line(pp,fill=col,width=width);sv.append('<polyline fill="none" stroke="'+col+'" stroke-width="'+str(width)+'" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pp)+'"/>')
txt(24,15,'SOURCE FL2: whole body reserve proposal / STATIC BAY PENDING',font=bold)
txt(24,52,'55mm EACH D/W005, V/W022, G/W021; no pooling, no accepted stored slack or whole-wire debit.',col='#ad3030')
xy=lambda p:(35+(p[0]+145)*4.1,400-(p[1]+105)*1.7)
txt(24,92,'XY analytic proposal, fixed endpoints; input full allocated field 9.4 x 3.9, body Z42.05..45.95',font=small)
R=37.85
for E,col in [(55,'#176eab'),(65,'#ce8200')]:
 lo,hi=0,math.pi/2
 for _ in range(60):
  p=(lo+hi)/2
  if 4*R*(p-math.sin(p))<E:lo=p
  else:hi=p
 phi=(lo+hi)/2;points=[[-132.75,77],[-132.75,54]]
 points += [[-94.9+R*math.cos(math.pi+j*math.pi/80),54+R*math.sin(math.pi+j*math.pi/80)] for j in range(41)]
 p=[-94.9,16.15];theta=0
 for sign,angle in [(-1,phi),(1,2*phi),(-1,phi)]:
  normal=[-math.sin(theta),math.cos(theta)];center=[p[0]+sign*R*normal[0],p[1]+sign*R*normal[1]];start=math.atan2(p[1]-center[1],p[0]-center[0])
  for j in range(1,41):
   a=start+sign*angle*j/40;points.append([center[0]+R*math.cos(a),center[1]+R*math.sin(a)])
  p=points[-1];theta+=sign*angle
 points.append([55.1,16.15]);line([xy(p) for p in points],col,3)
txt(900,120,'Blue E55 / amber E65 per core',font=small)
txt(900,150,'Rgroup37.85 / coreR >=35.1',font=small)
txt(900,180,'Fixed P[-94.9,16.15,44]',font=small)
txt(900,210,'Fixed Q[55.1,16.15,44]',font=small)
txt(900,240,'No new material or leg shape',font=small)
txt(900,270,'Actual body fans / D entry OPEN',col='#ad3030',font=small)
for j,y in enumerate([16.15,-30.0]):
 base=25+j*690;txt(base,445,f'Actual native XZ section Y={y:g} / allocated field + S0',font=small)
 trans=lambda v:(base+10+(v[0]+145)*3.1,660-(v[1]-35)*2.3)
 for s in g['sections']:
  if abs(s['Y_mm']-y)>1e-7:continue
  for curve in s['curves_xz']:line([trans(v) for v in curve],'#bf8a19' if s['name'].startswith('proposed') else '#697684',1)
lines=['Received INPUT quarter: S0 5.189851 / FoundationRail 11.749618 / OutSharedRoot 4.640140 / foundation 2.412054mm.',
 '4/127 strict pairs received; 123 UNRECEIVED. No falsifier yet is NOT whole-bay acceptance. Expanded BodyOuter3.25 outside0.',
 '19 full adaptive capacity members retained. Region overlap, if found, is allocation HOLD, not delivered flexible-wire contact.',
 'Mechanical transfer proposed upstream of actual D/V/G body-end clamps; loose guides only before reserve; no extra terminal9.',
 'Ebody=55+maxLleg-Lleg CONDITIONAL: actual leg+fan variation, roll, coallocation, loose capture/root and assembly still OPEN.',
 'A/U/minfit/slack NULL; R/850/900MAX3/ends unchanged. Old two planar floor negatives remain; no third local-leg return.',
 'Native26064/46493 IDLE / pendingnull / unsavedfalse; N01=0/10. Projection is not contact or selected whole-layout proof.']
for i,s in enumerate(lines):txt(24,690+32*i,s,'#ad3030' if i in [1,4,5] else '#152238',small)
png='day07-SOURCE-FL2-body-reserve-received-view.png';svg=png.replace('.png','.svg');im.save(out/png);(out/svg).write_bytes(('<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="940"><rect width="1400" height="940" fill="#f5f6f8"/>'+''.join(sv)+'</svg>').encode())
names=[pn,gn,cn,g['archive'],png,svg]
for src in ['robot-cat61-save-body-DGV-reserve-whole-proposal.py','robot-cat61-body-reserve-first-gate.py','robot-cat61-body-reserve-continuation.py','robot-cat61-render-close-body-reserve.py']:
 n='day07-'+src.removeprefix('robot-cat61-').removesuffix('.py')+'.recipe.py';assert not(out/n).exists();(out/n).write_bytes((temp/src).read_bytes());names.append(n)
with zipfile.ZipFile(out/g['archive']) as z:
 assert z.testzip() is None;geo=json.loads(z.read('manifest.json'))['geometry']
 for q in geo:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
pins=['day07-SOURCE-constant-radius-storage-bounded-disposition.json','day07-SOURCE-left-end-body-passage-bounded-disposition.json','day07-SOURCE-new-moving-module-region-first-gate.json','day07-SOURCE-slot-bearing-retention-bounded-disposition.json','n01-selected-piece-profile-contract.json','day07-S0-C1-current-candidate-composition.json']
nextstep='BODY_RESERVE_STATIC_FAMILY_FIRST: continue only pending wholebodyregion keys from cursor4/127, next BODY_FIRST_ARC_ALLPHI vs actualS0, no inputquarter replay. Stop at first actual allocation falsifier; classify rigid versus coallocated flex. If bay passes, prove currentDentry/tangent and D/G/V transport/endfans, actual continuous loose lengthtransfer/root/access/packing and new legentry/movingreserve before any material/V3. E55..65 is eachSOURCEFL2core capacity proposal, not accepted storedslack or wholedebit; A/U/minfit/slackNULL. No thirdleglocalreturn/shorterR/55waiver/pooling/oldprefixcredit. Preserve old321/324+3 and303/324+21 floor negatives and unchanged passage/motion21 proofs.'
p=out/'day07-SOURCE-FL2-body-reserve-bounded-disposition.json';assert not p.exists()
r=dict(id=p.stem,status='WHOLE_PER_PHYSICAL_BODY_RESERVE_PROPOSED_INPUT_QUARTER_RECEIVED_BODY_BAY_PENDING',selected=False,N01_complete=False,new_fact='Eachcore55 can be represented by one continuous upstream bodyS-family with fixed P/Q and individually preserved signed-turn offsets, rather than a third floor-limited local legloop. Actual inputquarter separates from all4 candidate-neighbor strictpairs; whole adaptivebodybay not yet received.',physical_allocation=dict(physical='SOURCE/FL2',cores={'D':'W005','V':'W022','G':'W021'},extra_each_core_mm=[55,65],leg_planned_extra_mm=0,body_each_core_min_mm=55,qualified_stored_slack_mm=None,source_stock_not_pooled=True),functional_transfer=dict(reserve_before_real_end_strain_reliefs=True,new_fixed_clamp_before_reserve=False,passive_guides_not_terminal=True,actual_end_functions='CurrentDFLcap; StationBankW022bodyfull9; CurrentFLGsplitcombfull9',DFL_current_entry_tangent='OPEN; oldshared54entryNOTinherited',SOURCE4movingties_retained=True,body_source_end_reliefs_retained=True,full_loop_length_is_not_whole_wire_debit=True,assembly='Lay connected kit through accessible passage/bay before uppermodules/skin/endcaps; no virtual factory/solder disconnection; loose capture/root/actualfan/access still OPEN.'),adaptive_family=g['adaptive_family'],counter=dict(received=4,total=127,unreceived=123,first_falsifier=None),received_rows=g['rows']+c['new_rows'],BodyOuter3p25=g['BodyOuter3p25'],member_retention=dict(count=19,compound_solids=19,all_retained=True,printed_material=False),open=['Adaptivebodyfamilyremaining123pairs','Otherharnessflexcoallocation','ActualbodyDGVfan/fullends','Newlegentryandactuallengthvariation','Initialassembly/capture/root','PerphysicalA/U/minfit/slack','SOURCEother6IDs/donor/full4physicalMAX3','Global123246/headNorth/U1far/4MTA/four220/R6/invalid3/Pimates/motionoutline'],all_current_A_U_minfit_slack=None,unchanged='current1292/effective1311/rest108/newmoving21+4temp, sourcepassage1697b075/new21motion155 no replay; oldunselectedguide8overlay withdrawn originalBankBed retained/no105roottransfer.',historical_negatives='a33floor303of324+21;117floor321of324+3;flooronly40.873522NOTavailablecapacity/no physicalshortage; alloldSOURCE/V3/S0/Pi45counts frozen.',guards='fullR35.1 profiles/foreign1.25/BodyOuter3.25;9IDs12portions4physicalMAX3/source14terminal11full9lap4once/850project/900ceil5minplus20/3x8laps3x20sleeves/stagger2x9/factoryplug/actualcutNULL;nooldprefix/chordcredit/pool/20trimdouble slack/four220/both4MTA unchanged',next=nextstep,source_pins=[dict(path=n,sha256=sha(out/n)) for n in pins],packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=[dict(path=g['archive'],crc_ok=True,member_sha_verified=len(geo))],timings=[dict(receipt=n,operation_seconds=d['operation_seconds'],process_cpu_seconds=d['process_cpu_seconds']) for n,d in [(gn,g),(cn,c)]],view=dict(path=png,actual_sections_source=gn,projection_not_contact_proof=True,owner_visual_check='PENDING'),native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False),written_utc=datetime.now(timezone.utc).isoformat());p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());names.append(p.name)
# Reuse exact-byte scoped checkpoint procedure; no card or unrelated hunks staged.
src=(temp/'robot-cat51-close-functional-bay.py').read_text(encoding='utf-8-sig');block=src[src.index("files=[str((out/n).relative_to(root))"):src.index("card=root/'hardware/HOBBY_COMPLETION_PLAN.md'")];block=block.replace('robot-cat51-exact.index','robot-cat61-body-reserve-exact.index').replace('Preserve continuous SOURCE Ankle profile bay and actual strap-return blocker with native slot feed','Preserve per-core SOURCE body reserve proposal and four received input interfaces').replace('SOURCE functional bay and native retention window','SOURCE body reserve bounded checkpoint');exec(block)
card=root/'hardware/HOBBY_COMPLETION_PLAN.md';raw=card.read_bytes();i=raw.index(b'## Historia poprzednich okien');pre=raw[:i].decode();tail=raw[i:];j=pre.index('\n',pre.index('## Bieżąca'))+1
fact='\nSOURCE_BODY_RESERVE_RECEIVED: '+p.name+' SHA'+sha(p)+' /owncommit'+commit[:8]+'/'+str(len(files))+'exactfiles. EachSOURCEFL2D/W005,V/W022,G/W02155mm proposed bodyS-family55..65 percore/Rgroup37.85/mincore35.1; fixedP/Q/upstreamrealendclamps, NOTpooled/acceptedslack. Inputquarter4of4 strictgap5.189851/11.749618/4.640140/2.412054; WHOLEbodybay4of127+123UNRECEIVED/no falsifier/notPASS. BodyOuterexpanded3.25outside0;19capacitymembers retained/no print or newleg. Dcurrententry/bodyfans/lengthtransfer/root/coallocation/assembly/motionstillOPEN; allA/U/minfit/slackNULL/N010. Native26064/46493IDLE pendingnull unsavedfalse.\n';pre=pre[:j]+fact+pre[j:]
if '\nNEXT:' in pre:
 a=pre.index('\nNEXT:')+1;e=pre.find('\n\n',a);e=len(pre) if e<0 else e;pre=pre[:a]+'NEXT: '+nextstep+pre[e:]
else:pre+='\nNEXT: '+nextstep+'\n'
assert card.read_bytes()==raw;q=card.with_suffix('.owner61final.tmp');q.write_bytes(pre.encode()+tail);os.replace(q,card)
rt=Path('C:/Users/Sysq/PycharmProjects/robot-cat/.codex/hooks/robot-cat-work-window.json');raw=rt.read_bytes();d=json.loads(raw);d['active_worker'].update(state='IDLE_SOURCE_BODY_RESERVE_INPUT4_RECEIVED_FAMILY123_PENDING',receive=r['status'],latest_receipt=str(p),latest_receipt_sha256=sha(p),latest_local_commit=commit,latest_commit_exact_byte_files=len(files),pending_operation=None,pendingoperation=None,unsaved_geometry=False,agent_turn_state='bounded_complete_native_idle',confirmed_utc=r['written_utc'],next=nextstep);assert rt.read_bytes()==raw;q=rt.with_suffix('.owner61final.tmp');q.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode());os.replace(q,rt)
print(json.dumps(dict(receipt=p.name,sha256=sha(p),commit=commit,exact_files=len(files),view=png,native='26064/46493 IDLE pendingnull unsavedfalse',enabled=d['enabled']),indent=2))
