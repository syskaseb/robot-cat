from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,subprocess,os,html
from PIL import Image,ImageDraw,ImageFont
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rs=['day07-SOURCE-pad-conforming-passive9-whole-first-gate.json','day07-SOURCE-new-moving-module-region-first-gate.json','day07-SOURCE-new-motion-reuse-relations.json'];a,b,c=[json.loads((out/n).read_bytes()) for n in rs]
assert a['actual_root']['contact_mm2']==105 and a['unreceived']==0 and b['received_complete_poses']==3 and len(b['actual_candidate_rows'])==19
im=Image.new('RGB',(1400,920),'#f5f6f8');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24);svg=[]
def txt(x,y,t,color='#152238',f=None):
 dr.text((x,y),t,font=f or font,fill=color);svg.append(f'<text x="{x}" y="{y+20}" fill="{color}" font-family="Arial" font-size="19">{html.escape(t)}</text>')
txt(25,12,'SOURCE: actual pad-conforming support received / whole approach OPEN',f=bold)
txt(25,49,'Contact105mm2 / embed26.25mm3; full parent9members +7positive joints; N01=0/10.')
colors={'actual_BankBed':'#77818f','actual_U1carrier':'#bd655a','actual_BankPortal2':'#985ca1','new_source_pad_passive_guide':'#2371b6','full9_capacity':'#d59100'}
for k,yval in enumerate([42.75,72]):
 x0=35+690*k;txt(x0,96,f'Actual section Y={yval}: X / Z [mm]')
 def xy(v):return(x0+25+(v[0]+59)/43*595,580-(v[1]-34)/24*410)
 for sec in a['sections']:
  if sec['axis']!='Y' or abs(sec['value_mm']-yval)>1e-6:continue
  for line in sec['curves_xz']:
   pts=[xy(q) for q in line]
   if len(pts)>1:
    col=colors.get(sec['name'],'#222222');dr.line(pts,fill=col,width=3);svg.append('<polyline fill="none" stroke="'+col+'" stroke-width="2" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+'"/>')
for i,(n,col) in enumerate(colors.items()):txt(35+i*275,600,n.replace('actual_','').replace('new_source_pad_',''),col,f=small)
for j,t in enumerate([
 'Portal2 >=2.4999999; SideLeft6.286542; PWM screw1.550806; unchanged U1>=2.291mm.',
 'Motion:3/36 complete, pose3 partial;19 strict pairs separated. Remaining33 pose blocks OPEN.',
 'Ground lower91.334809mm ONLY poses0..3; no all36/whole outline acceptance.',
 'Short toward-target C/S:22/36 target-inside cases; neutral25.531366 < R35.1.',
 'This rejects that approach family ONLY. External-loop group bay/R/fan/length/slack remain OPEN.',
 'Passive capture mouth3.9/full3.1+.4each side; real end strain-reliefs and four moving ties retained.',
 'No physical wire contact/shortage claim; A/U/min/fit/slack NULL; R6 tool and BodyOuter3.25 OPEN.'
]):txt(25,650+34*j,t,'#b32030' if j in [1,3,4] else '#152238')
png='day07-SOURCE-pad-conforming-guide-and-region-received-view.png';svgn=png.replace('.png','.svg');im.save(out/png);(out/svgn).write_bytes(('<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="920"><rect width="1400" height="920" fill="#f5f6f8"/>'+''.join(svg)+'</svg>').encode())
names=['day07-SOURCE-pad-conforming-passive9-whole-proposal.json',rs[0],a['archive'],'day07-SOURCE-new-moving-module-and-region-gate-scope.json',rs[1],b['archive'],rs[2],'day07-SOURCE-new-motion-frozen-input-projection.json',png,svgn]
for src in ['robot-cat55-start-source-pad-conforming-guide.py','robot-cat55-pad-conforming-guide-whole-first-gate.py','robot-cat55-start-new-source-motion-region-gate.py','robot-cat55-new-source-motion-and-region-first-gate.py','robot-cat55-source-motion-reuse-relations.py','robot-cat55-render-and-close-source-pad-guide.py']:
 n='day07-'+src.removeprefix('robot-cat55-').removesuffix('.py')+'.recipe.py';assert not(out/n).exists();(out/n).write_bytes((temp/src).read_bytes());names.append(n)
checks=[]
for n in names:
 if n.endswith('.zip'):
  with zipfile.ZipFile(out/n) as z:
   assert z.testzip() is None;ge=json.loads(z.read('manifest.json'))['geometry']
   for q in ge:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
   checks.append(dict(path=n,crc_ok=True,member_sha_verified=len(ge)))
p=out/'day07-SOURCE-pad-conforming-guide-bounded-disposition.json';assert not p.exists()
nextstep='Finish ONLY new21 motion cursor: pose3 skip alreadyreceived exact19keys, then4..35; no oldtests. Choose ONE external-loop shared Knee6/Hip3 -> merge9DGV accessible occupied bay/R35.1/actualguide-Y entryfan/roll/localcurrentneighbors/explicitmovingreserve. CurrentshorttowardC/Sfamily falsified22/36, NOTall3Dloops. Full9IDs12portions4physicalMAX3 original+donor percoreupperlength/fit/slack only after qualified group path; no oldprefix/chordcredit/V3detail/guideposeoffset/shorterR.'
r=dict(id=p.stem,status='FIXED_PASSIVE9_LOAD_INTERFACE_CLOSED_SCOPED_NEW_SOURCE_MOTION_PENDING_SHORT_CS_FAMILY_FALSIFIED',selected=False,N01_complete=False,
 local_closed=dict(actual_root=a['actual_root'],foreign_rows=a['actual_foreign_rows'],underdeck_true_unchanged=a['Underdeck_true_unchanged_reuse'],BankPad_actual_subvolume=a['same_print_actual_subset_aliases'],valid=a['whole_parent_valid'],solids=a['whole_parent_solids'],member_coverage=a['intended9_member_coverage'],positive_junctions=a['positive7_junctions'],whole9_profile_fit=a['whole9_profile_fit'],full_capacity_material_common_mm3=a['full_capacity_material_common_mm3'],new_part_strict_reopen=a['new_part_strict_reopen'],useful_sections=a['useful_sections'],print_bounds=a['proposed_part_print_bounds'],local_installation=a['local_installation']),
 proposed_fixed_override=dict(replaces='CurrentFoundation:BankBedCurrent:1',archive=a['archive'],archive_sha256=a['archive_sha256'],geometry=a['geometry'][-1],coordinate_frame='AlreadyWORLD BRep applyONCE/noXML',exclude_old_parent_and_proved_duplicate_BankPad_aliases=True,not_officially_selected=True),
 proposed_moving_context=dict(path='day07-SOURCE-body-approach-proposed-moving-context.json',sha256=sha(out/'day07-SOURCE-body-approach-proposed-moving-context.json'),operating=21,temporary_pull=4,attachment='Motion_RL_Knee',not_ignored_in_body_neighbors=True),
 new_motion=dict(status=b['status'],required_poses=36,received_complete_poses=b['received_complete_poses'],received_pose_rows=b['received_pose_rows'],received_strict_pairs=len(b['actual_candidate_rows']),received_pair_keys=[{k:q[k] for k in ['pose','part','other','name','target'] if k in q} for q in b['actual_candidate_rows']],exact_rows_reference=rs[1],new_floor_properties=len(b['new_floor_rows']),ground_rest_z_mm=b['ground_rest_z_mm'],minimum_floor_lower_mm=b['minimum_new_conservative_floor_lower_mm'],floor_scope='poses0..3 ONLY; not36floorPASS',first_physical_falsifier=b['first_falsifier'],remaining_complete_blocks=33,resume='pose3 skip19alreadyreceived exactkeys then4..35; preserve rawpartial',full63_109_rotation_symmetry_proved=False,reuse_relation_reference=rs[2],invalid_symmetry_inference_is_not_designfailure=True),
 group_approach=dict(neutral=b['neutral_group_premise'],short_toward_CS_falsified_pose_count=b['short_toward_CS_falsified_pose_count'],all36_port_frames_ref=rs[1],guide_end_tangent_fan=b['guide_end_tangent_fan'],meaning='Reject ONLY shorttoward-target singleC/straight family; notall3Dloops, physicalcontact, shortage, or receivedroutedlength. external-loop/twoarc sharedbay remains designwork.',all_A_U_minimum_fit_slack=None),
 retention='Passive leading/capture9.4x10.5 mouth3.9/full3.1+.4eachside; doesNOTreplace realmoving/source/bodyendstrainreliefs. Only neverselected optionalextra fixed100 retired; SOURCE4movingties/MODULE2/selectedSKUs unchanged. Sequentiallateralbodylay beforeclosures, no factorycase threading/virtualunsolder/newterminal/extra9.',
 source_invariants='9IDs12portions4physicalMAX3/SOURCEFL1FL2continuousFL3original+DONOR. source14/terminal11/full9/lap4once/3x8laps/3x20sleeves/stagger/2x9lands/factoryplug/850project/ceil5(min+20)<=900perunitMAX3/actualcutNULLphase2/fourindependent220/both4MTA. No old181205225197534614prefix/Gdelta/chordcredit/pool.',
 current_composition='Current1292/effective1311/rest108 unchanged; fixedoverride+moving25 are PROPOSED qualifiedscopes only. Oldrejects notcurrent. No wholeSOURCE/N01selection.',
 R6_scope=a['R6'],global_open='WholeSOURCEapproach/R/fan/movingreserve/lengthslack; actualR6withdraw25/tool12x41x25/continuousmanualspace; BodyOuteractual3.25; wholeinitialassembly;123246/U1far/headNorth/4MTA/four220/Pimates/invalid3/motionoutline. N01=0/10.',
 next=nextstep,source_pins=[dict(path=n,sha256=sha(out/n)) for n in ['day07-SOURCE-Ymin-open9-guide-bounded-disposition.json','day07-S0-C1-current-candidate-composition.json','day07-coordinator-SOURCE-splice-layout-authority-receipt.json','n01-selected-piece-profile-contract.json']],
 packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=checks,view=dict(path=png,source=rs[0],actual_sections_y_mm=[42.75,72],projection_not_contact_proof=True,visual_inspection='PENDING separate ownerview; geometryevidence inreceipts'),timings=[dict(receipt=n,operation_seconds=q['operation_seconds'],process_cpu_seconds=q['process_cpu_seconds']) for n,q in zip(rs,[a,b,c])],native=dict(pid=26064,session_id=46493,state='IDLE',identity_received='OWNER55_FINAL_IDLE 26064 1292 1311 108 True',pending_operation=None,unsaved_geometry=False),written_utc=datetime.now(timezone.utc).isoformat())
p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());names.append(p.name)
print(json.dumps(dict(receipt=p.name,sha256=sha(p),files=len(names),archive_checks=checks,view=png),indent=2))
