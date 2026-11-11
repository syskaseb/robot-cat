from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,subprocess,os
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');rt=Path('C:/Users/Sysq/PycharmProjects/robot-cat/.codex/hooks/robot-cat-work-window.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();save=lambda p,d:p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
frozen={'day11-joint-bank-receiver-load-and-fore-neck-service-premise.json':'f830cd7647ca3b56ea809e7a860be8261b84ee3863dde28934707f965488ca4b','day11-joint-FPI-service-current-frame-relation.json':'381ff392e6b21a72b2a4ef77888fab65d96c12dd8c892e0a440f2368f715c7f7','day11-joint-FPI-service-current-frame-relation.breps.zip':'9cc00c2b6a4685c447a56cfa268ecefa08391aebcc97bc5a639daf7e216688c3','day11-joint-service-current-limiting-material-sections.json':'4a96167d631114a24f0e27349cc2aa6555783602c5c8a67a8f889e609a2c7e65'}
for n,h in frozen.items():assert sha(out/n)==h
P=json.loads((out/list(frozen)[0]).read_bytes());G=json.loads((out/list(frozen)[1]).read_bytes());S=json.loads((out/list(frozen)[3]).read_bytes());runtime=json.loads(rt.read_bytes());held=runtime['coordinator_three_core_held_exit_source_dispatch']
assert G['common_valid'] and abs(G['common_mm3']-25.92)<1e-7 and G['new_missing_pairs_received']==1
assert len(held['facts']['records'])==3
for q in held['source_pins']:assert sha(Path(q['path']))==q['sha256']
checks=[]
with zipfile.ZipFile(out/G['archive']) as z:
 assert z.testzip() is None
 for q in G['geometry']:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
 checks.append(dict(path=G['archive'],CRC=True,archive_entries=len(z.namelist()),exact_BRep_member_SHAs=len(G['geometry']),no_native_geometry_read_or_rerun=True))
names=list(frozen)+['day11-joint-service-recovered-source-view.png','day11-joint-service-recovered-source-view.svg']
for src,dst in [('robot-cat11-joint-service-premise.py','day11-joint-service-premise.recipe.py'),('robot-cat11-joint-FPI-service-frame-read.py','day11-joint-FPI-service-frame-read.recipe.py'),('robot-cat11-render-recovered-joint-service.py','day11-render-recovered-joint-service.recipe.py'),('robot-cat11-finish-interrupted-joint-service.py','day11-finish-interrupted-joint-service.recipe.py')]:
 (out/dst).write_bytes((temp/src).read_bytes());names.append(dst)
pins=[];seen=set()
for q in P['source_pins']+P['external_source_pins']+held['source_pins']:
 pp=Path(q['path']);pp=pp if pp.is_absolute() else out/pp;key=str(pp.resolve()).lower()
 if key in seen:continue
 seen.add(key);assert sha(pp)==q['sha256'];pins.append(dict(path=str(pp),sha256=q['sha256']))
snapshot=out/'day11-WORKING_UNSELECTED_N01_0of10.FCStd';observed_snapshot=sha(snapshot)
pp=out/'day11-joint-bank-service-interrupted-packet-recovery-receipt.json'
next_scope='This recovery only completed the interrupted source packet. After parent confirms restoredGUI/MCP handoff, next authorized wholeallocation/service-order decision must jointly resolve wholeFPIcase/lid/access/shortends plus bankD5/G4/V3 load-pressure and S0/PWM service. Recorded inplaceSIDEoperationfield is rejected at currentP0rail. Othercase/service/partialdemount options are NOTtested or ruledout; do not choose anothercaseoffset/localtrim/transport family in this recovery. No supportdetails before connectedwholephysicalspace/length/reserve premise.'
r=dict(id=pp.stem,status='INTERRUPTED_JOINT_SERVICE_SOURCE_PACKET_RECOVERED_SAVED_GEOMETRY_NOT_RERUN',N01='0/10',selected=False,whole_feasible=False,
 interruption=dict(original_input='01a1c82b-7c5b-7363-8c43-bcec43a46d20',recovery_input='01a1cc4b-d5a5-72f0-b87c-03d00a89098f',recovery_first_clock_utc='2026-11-11T20:28:32Z',last_original_native_evidence='Savedservicegate andmaterialsections producedbeforeinterruption byGUI26044; originalappturnINTERRUPTED/notLoaded, no laternativeprogressreceived.',approximately_19_hour_gap=True,continuous_compute_claim=False,actual_process_death_time=None),
 saved_result=dict(receipt=G['id']+'.json',sha256=sha(out/(G['id']+'.json')),field='SIDE_ROUTINE_OPENING',field_classification=G['field_classification'],target=G['target_actor'],gap_mm=G['gap_mm'],common_valid=True,common_mm3=G['common_mm3'],source_pose_unchanged=True,new_missing_pairs_received=1,actual_original_operation_seconds=G['operation_seconds'],actual_original_CPU_seconds=G['process_CPU_seconds'],meaning='Rejects this choseninplaceprojectserviceallocation/site. NOTactualdeliveredlidcontact/allservicepaths/allFPIlayouts/wholeN01feasibility. No changedpose/retry/newtrunk/print/physicalclaim.',old_CASE3rows_not_replayed=True,old_iterator_NOT_resumed=True),
 joint_interface_evidence=dict(premise=P['id']+'.json',premise_sha256=sha(out/(P['id']+'.json')),actual_material_sections='day11-joint-service-current-limiting-material-sections.json',actual_sections_sha256=sha(out/'day11-joint-service-current-limiting-material-sections.json'),planes_mm=[G['actual_section_x_mm']]+[q['x_mm'] for q in S['sections']],meaning='Savedlimitingmaterial/sourceaccess data only. FrameFronttop37.02, SideRighttop38.52, currentVboughtmetalZ63.8057, actualS0patches/PWMmetal retained. Whiteparts/boundsnotfreebay; no claimednewbankloadroot/guard/casecradle.'),
 received_source_supersession=dict(authority='runtime.coordinator_three_core_held_exit_source_dispatch',received_source_input=held['input'],status='THREE_DONOR_HELD_EXITS_SOURCE_RECEIVED_NOT_NEW_GEOMETRY',frame=held['facts']['frame'],records=held['facts']['records'],scope=held['facts']['scope'],source_pins=held['source_pins'],point_diameters_NOT_Li_variation=held['parent_scalar_derivation']['individual_exit36_diameters_mm'],effectivity='Supersedes individualDONORexitUNKNOWN in frozenpremise. Retainedjoint->exit65/43/21 includes9, lap4 onlyifnotalreadyincluded. NoDONOR14/originalFL3bank11. SOURCEFL2grip stillUNKNOWN; no originalpremisefilerewrite or geometrylookup.'),
 factory_lifecycle=P['factory_lifecycle_fact'],physical_units=dict(IDs=9,portions=12,physical_MAX3_units=4,conditional_max_L_full9_included_mm=P['length_rules']['conditional_max_L_mm'],meaning='815FL1/770FL2/780donor/832originalFL3 remain conditionalonly. MAX3 separate; ifM<=850 thenceil5(M+20)<=870<=900. No routedLi/variation/slack/fit accepted; originalFL3 remains onKnee, donorindependent. 55eachFL2/Knee+Hip10/FL2NOlap4/FL3properexistingjoint/source14terminal11full9once/laps8sleeves20/stagger2x9 preserved.'),
 process_state=dict(observed_utc='2026-11-11T20:28:44Z',former_GUI=dict(pid=26044,state='ABSENT',exit_code=None),former_source_cache=dict(pid=11476,session_id=70789,state='ABSENT',exit_code=None,old_TTY_RPC_not_called=True),replacement_GUI=dict(pid=19584,started_by='Parent service/UI restoration only',process_exists=True,responding=True,model_load_status='LOADING_OR_HANDOFF_NOT_YET_CONFIRMED',native_MCP_tools_currently_unavailable=True,MCP_ready_NOT_claimed=True,GUI_saved_current_restore_NOT_claimed=True,no_owner_geometry_operations=True,no_new_process_by_owner=True),owner_packet_pending_operation=None,owner_packet_unsaved=False,global_GUI_modified_status='UNKNOWN; preserve parent restorationmetadata, no false saved/idle claim.'),
 saved_snapshot_reference=dict(path=snapshot.name,parent_restore_input_sha256='d5c283cc67ee43d012c782f1deea731a9f3affffbd0b96243f880730e22bc2e1',read_only_observed_sha256=observed_snapshot,observation_scope='Savedinput file, not anewmodel/save or confirmedloadedGUI. No FCStd geometryedit/export/repack or oldsourceaudit; not part of this ownartifactcommit.'),
 base_scope='Source1292/effective1311/a9f over2d1 overdef unchanged. ProposedG4/D5/SOURCE21+4temporary/rest108 remainreferences, notselectedwhole. Allparts/factoryends/P0R47E6MAIN46.52/fourindependent220/both4MTA/MODULEsoldered andallnegativecounters preserved. OldthreeUSBcurrentCLOSEDscoped, not staleinvalid3GLOBALOPEN.',
 global_OPEN=['SOURCEconnectedspace/KneeHipR/actualpercoreLi-delta/usable55+Hip10/perphysical850900MAX3/A-U-fit-slack-cutNULL','JointFPI-S0PWM-V3 loadandservice, fullFPIstock/head/feed/tails and MAINcurrentinputbinding','D5ownclosureface29technical/F_R4capture+2stockbindings','R6/Pimates/U1far/headNorth/123246/lengthslack/changedmotion-outline'],
 views=[dict(path=n,sha256=sha(out/n),rendered_from_frozen_JSON_only=True,visually_inspected=True,actual_nonempty_sections=True,not_new_native_view_or_geometry_GO=True) for n in names if n.endswith(('.png','.svg'))],
 source_pins=pins,packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=checks,next_scope=next_scope,authorization='Resultstage enabledtrue/nohourdeadline/nopercentthreshold preserved; recoverypacketcompletion not wholewindowclose. No newphysicalhypothesis/CAD/native/helper/review or geometryrerun.',written_utc=datetime.now(timezone.utc).isoformat())
save(pp,r);names.append(pp.name)
# Exact whitelist commit: cards/runtime/currentGUI/snapshot excluded, foreignhunks untouched.
files=[str((out/n).relative_to(root)).replace('\\','/') for n in names];env=os.environ.copy();env['GIT_INDEX_FILE']=str(temp/'robot-cat11-joint-service-recovery-exact.index');assert not Path(env['GIT_INDEX_FILE']).exists()
def git(args,data=None,custom=False,check=True):return subprocess.run(['git',*args],cwd=root,env=env if custom else None,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=check)
entries=[];hashes={}
for n in files:
 raw=(root/n).read_bytes();blob=git(['hash-object','-w','--stdin','--no-filters'],data=raw).stdout.decode().strip();entries.append('100644 '+blob+'\t'+n+'\0');hashes[n]=hashlib.sha256(raw).hexdigest()
for attempt in range(3):
 base=git(['rev-parse','HEAD']).stdout.decode().strip();git(['read-tree',base],custom=True);git(['update-index','-z','--index-info'],data=''.join(entries).encode(),custom=True)
 assert set(git(['diff','--cached','--name-only','-z'],custom=True).stdout.decode().strip('\0').split('\0'))==set(files)
 tree=git(['write-tree'],custom=True).stdout.decode().strip();commit=git(['commit-tree',tree,'-p',base],data=b'Recover interrupted joint FPI service evidence and received donor exits without CAD rerun\n').stdout.decode().strip()
 if git(['update-ref','-m','commit: recover frozen jointservice packet','HEAD',commit,base],check=False).returncode==0:break
else:raise RuntimeError('ConcurrentHEAD: packetready, commitnotpublished')
raw=git(['cat-file','--batch'],data=''.join(commit+':'+n+'\n' for n in files).encode()).stdout;at=0
for n in files:
 end=raw.index(b'\n',at);size=int(raw[at:end].split()[2]);body=raw[end+1:end+1+size];at=end+size+2;assert hashlib.sha256(body).hexdigest()==hashes[n] and sha(root/n)==hashes[n]
git(['update-index','-z','--index-info'],data=''.join(entries).encode())
card=root/'hardware/HOBBY_COMPLETION_PLAN.md'
for attempt in range(4):
 raw=card.read_bytes();s=raw.decode('utf-8');marker='CURRENT_OWNER_JOINT_INTERFACE_READ:';a=s.index(marker);e=s.index('\n\n',a)
 fact='OWNER_RESULT_RECEIVED: '+pp.name+' SHA'+sha(pp)+' /owncommit'+commit[:8]+'/'+str(len(files))+'exactfiles. Interrupted01a1c82b recoveredONLYfrom4savedpinnedartifacts: SIDEserviceprojectfield/actualSideRight22 validcommon25.920mm3, onepreviouslymissingpair; choseninplaceallocationHOLD notdeliveredlidcontact/allFPIservice. No geometryrerun/newpose/trunk/print; source-frozenview seen. DONOR3exitrecords nowRECEIVED: F(43,5.65/8.5/11.35,4)/+U/65,43,21includes9; properlap4notdoublecounted, FL2gripstillOPEN. ActualLi-AU-fit-slack-cutNULL/N010. OldGUI26044+helper11476/70789ABSENT/unknownexit/no oldRPC. GUI19584parentrestore NOTownerconfirmedloaded/MCPready; no newGUI/saveclaim. ~19hinterruption, NOTcontinuouscompute.'
 s=s[:a]+fact+s[e:]
 oldnext='NEXT: Receive concretejointservice/frame relation BEFORE any load/guardmaterial or transport. No caseoffset/lidclock/trim/secondfamily.'
 s=s.replace(oldnext,'NEXT: '+next_scope,1)
 if 'USERGUI/MCP: FreeCADGUI26044 działa' in s:
  a=s.index('USERGUI/MCP:');e=s.index('OWNER_RESULT_RECEIVED:',a)
  s=s[:a]+'USERGUI/MCP CURRENT RECOVERY: 11.11 20:28UTC oldGUI26044 andhelper11476ABSENT; oldTTY70789historical/noRPC. ParentlaunchedONEGUI19584 fromsavedFCStd d5c283cc...bc2e1; loading/servicehandoff notownerconfirmed. MCPnamespace removed/no competingCAD/plugin/newhelper. ParentrestoresUI/service; Banach soleCADwriter afterconfirmedhandoff. Thisrecovery onlysavedartifact/view/commit, noCADgeometry. Resultstage remainsactive.\n\n'+s[e:]
 new=s.encode('utf-8')
 if card.read_bytes()!=raw:continue
 q=card.with_suffix('.ownerjointrecovery.tmp');q.write_bytes(new);os.replace(q,card);break
else:raise RuntimeError('Concurrentcard: packetcommitted, cardnotmerged')
for attempt in range(4):
 raw=rt.read_bytes();d=json.loads(raw);w=d['active_worker'];w.update(latest_receipt=str(pp),latest_receipt_sha256=sha(pp),latest_local_commit=commit,latest_commit_exact_byte_files=len(files),owner_packet_state='INTERRUPTED_SOURCE_PACKET_RECOVERED_NO_CAD',owner_packet_pending_operation=None,owner_packet_unsaved=False,owner_packet_completed_utc=datetime.now(timezone.utc).isoformat(),former_source_cache_pid=11476,former_source_cache_session_id=70789,former_source_cache_state='ABSENT_CONFIRMED_NO_OLD_RPC',former_GUI26044_state='ABSENT_CONFIRMED',owner_packet_next_scope=next_scope)
 # Parent owns current restoration/handshake fields: do NOT overwrite state, GUIpid,
 # GUI_saved/modified, globalpending/usage/enabled or a newer coordinatorNEXT.
 d['owner_joint_service_recovery_packet']=dict(receipt=str(pp),sha256=sha(pp),commit=commit,exact_files=len(files),N01='0/10',no_new_CAD=True,oldsourceprocesses_absent=True,gui_handoff_owned_by_parent=True)
 if rt.read_bytes()!=raw:continue
 q=rt.with_suffix('.ownerjointrecovery.tmp');save(q,d);os.replace(q,rt);break
else:raise RuntimeError('Concurrentruntime: packetcommitted, metadatanotmerged')
print(json.dumps(dict(receipt=pp.name,sha256=sha(pp),commit=commit,exact_files=len(files),packetpins=len(r['packet_pins']),sourcepins=len(pins),archive_checks=checks,oldnative='26044/11476 ABSENT, exitUNKNOWN',GUI='19584 parentrestoration/handoffNOTownerconfirmed',own_pending=None,own_unsaved=False,enabled=d['enabled'],N01='0/10'),indent=2))
