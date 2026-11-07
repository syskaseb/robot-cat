from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,math,csv,html
from PIL import Image,ImageDraw,ImageFont
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rd=lambda n:json.loads((out/n).read_bytes())
pn='day07-SPLIT_HIP3_DIRECT10_KNEE6_LOWER55-whole-proposal.json';gn='day07-SPLIT3plus6-Hip-upper-north-first-gate.json';sn='day07-SPLIT3plus6-current-U1-R4-local-actual-section.json';a=rd(pn);b=rd(gn);c=rd(sn);space=rd('day07-SPLIT3plus6-current-upper-north-and-lower-case-layer-read.json');assert b['received']==84 and b['total']==153 and b['first_falsifier']['allocated_common_mm3']==0 and len(c['sections'])==2 and all(q['curves_YZ'] for q in c['sections'])
names=[pn,gn,sn,'day07-SPLIT3plus6-current-upper-north-and-lower-case-layer-read.json','day07-SPLIT3plus6-Hip-upper-north-first-gate-cursor.json',b['archive']]
cp=out/'day07-SPLIT3plus6-twelve-physical-debit-status.csv'
with cp.open('w',encoding='utf8',newline='') as f:
 w=csv.writer(f);w.writerow(['wire','piece_id','physical_unit','group','new_routed_length','actual_installed','actualfit','actualcut','phase2','reason'])
 for q in a['all12_portions']:w.writerow([q['wire'],q['piece_id'],q['physical_unit'],q['group'],'NULL','NULL','NULL','NULL','actualcutNULL','NewcompleteRpath/movingLi/bodyfans/reserve notqualified; previousconditionalcomponent RETIRED NOTcredit'])
names.append(cp.name)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n);F=font(17);H=font(22);im=Image.new('RGB',(1600,1350),'white');dr=ImageDraw.Draw(im);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1350"><rect width="1600" height="1350" fill="white"/>']
def text(x,y,t,col='#222',big=False):
 dr.text((x,y),t,fill=col,font=H if big else F);svg.append(f'<text x="{x}" y="{y+18}" fill="{col}" font-family="Arial" font-size="{22 if big else 17}">{html.escape(t)}</text>')
def line(p,col='#777',width=2,dash=False):
 if len(p)<2:return
 for j,(u,v) in enumerate(zip(p,p[1:])):
  if dash:
   N=max(2,int(math.dist(u,v)/6))
   for k in range(0,N,2):dr.line([(u[0]+(v[0]-u[0])*z/N,u[1]+(v[1]-u[1])*z/N) for z in [k,min(k+1,N)]],fill=col,width=width)
  else:dr.line([u,v],fill=col,width=width)
 svg.append(f'<polyline fill="none" stroke="{col}" stroke-width="{width}"'+(' stroke-dasharray="6 6"' if dash else '')+' points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in p)+'"/>')
def rect(p,q,col):line([(p[0],p[1]),(q[0],p[1]),(q[0],q[1]),(p[0],q[1]),(p[0],p[1])],col,1)
text(20,12,'ONE PHYSICAL SPLIT: HIP3 DIRECT10 / KNEE6 SEPARATE55 — FIRST U1_R4 CLEARANCE HOLD',big=True)
text(20,45,'PROPOSAL ONLY / all9 IDs,12 portions,4 physicalMAX3 / current1292 effective1311 unchanged / N01 0/10')
xy=lambda p:(25+(p[0]+155)*3.2,90+(105-p[1])*3.1);xz=lambda p:(25+(p[0]+155)*3.2,690+(110-p[2])*1.8)
ctx=rd('day07-WHOLE_SOURCE-current-context-and-first-gap-view-data.json')['current_body_bounds'];src=rd('day07-whole-physical-SOURCE-approach-Knee-link-proposal.json')
for title,proj,Y in [('XY whole currentcontext / Hip upper-north local branch / lowerKnee dashed PLAN',xy,80),('XZ split layers / dashed connections UNKNOWN / current+8.5 Knee source retained',xz,672)]:
 text(20,Y,title)
 for q in ctx:
  lo,hi=q['bounds_mm'];p=proj(lo);v=proj(hi);rect(p,v,'#cf9c9c' if q.get('selected_FPI_unqualified_home_variable') else '#c8c8c8')
 for q in a['rows']:
  col={'D':'#1764bc','V':'#bd7716','G':'#18864c'}[q['core']]
  if q['row']==0:
   P=q['upper_passage_P'];R=q['north_turn_R_mm'];pts=[[-94.9-R*math.cos(t),77-R*math.sin(t),47.3] for t in [i*math.pi/2/35 for i in range(36)]]+[q['leading_end']];line([proj(p) for p in pts],col,2)
   origin=src['source_origins'][0]['source_outer_reservation_world_mm'];line([proj(origin),proj(P)],col,1,True);branchX={'D':65.98,'V':-40.,'G':28.125}[q['core']];B=[branchX,q['north_turn_end'][1],47.3];line([proj(B),proj(q['receiver_held9_end'])],col,1,True)
  else:
   P=q['lower_region_bounds_mm'][0];Q=q['lower_region_bounds_mm'][1];rect(proj(P),proj(Q),'#bb8c50');E=a.get('current_moving_holder',{})
   origin=src['source_origins'][1]['source_outer_reservation_world_mm'] if q['row']==1 else [-90.89770358114208,97.19404052910949,5.106513693400942];M=[-126,10,-34.6];line([proj(origin),proj(M),proj(q['receiver_held9_end'])],col,1,True)
text(1090,100,'FIRST ACTUAL LOCAL YZ SECTION',big=True)
text(1090,132,'X=-70.55 mm; both real section curves')
yz=lambda p:(1090+(p[0]-38)*35,470-(p[1]-43)*42)
for q in c['sections']:
 col='#18864c' if q['actor']=='HIP_W019_ALLOCATED' else '#555555'
 for cv in q['curves_YZ']:line([yz(p) for p in cv],col,2)
text(1090,500,'W019 allocated field / retained U1_R4')
text(1090,530,'Actual gap1.072333536 <1.25', '#ae2525')
text(1090,558,'VALID common0: clearanceHOLD, notcontact')
text(1090,586,'84/153 received;69 NOT RECEIVED')
text(1090,614,'No second family / no remaining scan')
text(1090,674,'HIP3 direct10: NOT blind minus45',big=True)
text(1090,707,'All3 R-constrained receiver fans OPEN')
text(1090,735,'10 usable reserve/moving Li still OPEN')
text(1090,780,'KNEE6 lower18.2 x3.9 plan',big=True)
text(1090,813,'Whole6 roll/dilation, R35.1, floor OPEN')
text(1090,841,'0 AABB candidates is NOT bay acceptance')
text(1090,869,'55 EACH FL2/donor not waived or pooled')
for i,t in enumerate(['ALL9 receiver roles retained: D3 atD2..4; G3 atG2..4 plus fourthW025; V3 atactual9 ends. D1BUSmate andD5W007bothends unchanged.','SOURCE/FL1 continuous3 HIP cores; SOURCE/FL2 continuous3 KNEE cores; SOURCE/FL3original3 atKnee plusDONOR3 independently tobody.','All12 actual routes/debits/fit/cuts NULL. Hip displacement-only sums250.236/152.411/210.822 are NECESSARY ONLY, not R-route, upper fit or shortage.','Separate group fan/layer/10-vs55 allocation is new topology; no old9quarter/S-height/Rsum nudge. Whole plan rejected atfirst Hip north entry field.','Preserve all9 ends/fullprofiles/R35.1/four220/both4MTA/source14/terminal11/full9properonce/FL2NOlap4/FL3properjoint/laps8+sleeves20/stagger2x9.','D5 own closure face29/120 and F_R4casecapture2stock remainGLOBALOPEN. W037wholefactory/custom case/root/bothends/full220 stay.','True fixedclamps terminate loose length transfer; allusable55/percoreindependentdeltaLi<=10IF55..65/850project900ceil5(min+20)MAX3 remainOPEN.','Grey boxes orient currentnativecontext; dashed links are UNKNOWN regions, not routed wires/debits. FPIfullselectedcase/unqualifiedhome remainspresent.','Stopgeometry afterthisONEfalsifier; no new material/pose/stock/terminal/cut/purchase. Nativeidle retained for authorizedfinalsave/exit before22:11:33Z.']):text(20,1040+i*31,t)
png=out/'day07-SPLIT3plus6-whole-topology-and-actual-U1R4-section.png';im.save(png);sv=png.with_suffix('.svg');sv.write_bytes(('\n'.join(svg)+ '</svg>\n').encode());names += [png.name,sv.name]
for srcn in ['robot-cat94-actual-split-layer-available-read.py','robot-cat94-save-split3plus6-whole-proposal.py','robot-cat94-hip3-north-first-falsifier.py','robot-cat94-receive-only-new-hip-north-keys.py','robot-cat94-save-actual-Hip-north-section.py','robot-cat94-package-split-result.py']:
 n='day07-split3plus6-'+srcn.removeprefix('robot-cat94-').removesuffix('.py')+'.recipe.py';assert not(out/n).exists();(out/n).write_bytes((temp/srcn).read_bytes());names.append(n)
checks=[]
with zipfile.ZipFile(out/b['archive']) as z:
 assert z.testzip() is None;gg=json.loads(z.read('manifest.json'))['geometry']
 for q in gg:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
 checks.append(dict(path=b['archive'],member_sha_verified=len(gg),crc_ok=True))
p=out/'day07-SPLIT3plus6-Hip-direct10-Knee55-first-layer-bounded-disposition.json';r=dict(id=p.stem,status='ONE_WHOLE_PHYSICAL_SPLIT_FIRST_HIP_NORTH_LAYER_CLEARANCE_HOLD_STOP_NO_SECOND_FAMILY',selected=False,N01_complete=False,proposal=pn,proposal_sha256=sha(out/pn),actual_source_layers=space,first_falsifier=b['first_falsifier'],received=b['received'],total=b['total'],unreceived=b['unreceived'],source9ID12portion4MAX3_mapping_preserved=True,all_actual_A_U_minimum_fit_slack_cut_NULL=True,Hip10_chosen_instead_optional55_not_subtraction=True,Knee55each_FL2_and_donor_preserved=True,no_whole_body_fit_storage_motion_or_stock_claim=True,source_physical_unit_rows=a['all12_portions'],hip_displacement_necessary_NOT_actual_route=a['hip_necessary_displacement_only'],native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False,idle_prompt='OWNER94_NATIVE_IDLE26064 after savedactualnonemptyYZsection'),remaining=['wholeHip3differentavailableconnectedR35approach/receiverfans/usable10','wholeKnee6packingroll/bodylayer/sourcecaseAnkle/ground/currentLi/usable55','all9 independent percorelengthvariation andall12physical850900MAX3 fits','D5OWNcontinuousclosureface29technical+F_R4capture2stock','entire123246/HEAD/U1far/Pimates/R6/stock/currentcomposition/motionoutline integration'],next='LAST_GEOMETRY_CHUNK_COMPLETE_SAVE_AND_END_OWNED_COMPUTE_BEFORE_22:11:33Z: no secondgeometryfamily/newCAD/review/extension. Preserve source1292/effective1311 and allproposedG4/D5/movingSOURCE21+4temp/rest108 sourcechain/currentoverrides/negatives; prepareactualstopreceipt/ZIP-SHA/currentcomposition/resume. Gracefulsave/exit OWN26064/session46493 only underfinalclosure coordination; no replacement. Currentwhole3+6 rejected atW019/U1_R4 gap1.072333536<1.25 VALIDcommon0,84/153+69unreceived frozen. Wholefuturearchitecture needsactualavailable connectedHip3direct10 andKnee6separate55/sourcecase/ground/percoreLi/MAX3 evidence, not scalarquarter/Z/head/case/R/55 change or oldfailedscan. No N01point/mail untilwholeaccepted.',view=dict(path=png.name,sha256=sha(png),visually_inspected=False,actual_nonempty_local_YZ_source=sn,projections_not_contactproof=True,dashed_regions_UNKNOWN=True),timings=[dict(receipt=n,wall=q['operation_seconds'],CPU=q['process_cpu_seconds']) for n,q in [(space['id']+'.json',space),(gn,b),(sn,c)]],measured_native_wall_seconds=space['operation_seconds']+b['operation_seconds']+c['operation_seconds'],measured_native_CPU_seconds=space['process_cpu_seconds']+b['process_cpu_seconds']+c['process_cpu_seconds'],archive_checks=checks,source_pins=a['source_pins'],packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],all_old_counters_and_negative_geometry_frozen=True,no_material_new_parts_or_secondfamily=True,authorized_deadline_utc='2026-11-07T22:11:33Z',partial_final_not_windowclose=True,written_utc=datetime.now(timezone.utc).isoformat());p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());print(p.name,sha(p),'packet',len(names),'source',len(r['source_pins']),'BRep',len(gg),'wallCPU',r['measured_native_wall_seconds'],r['measured_native_CPU_seconds'])
