from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,subprocess,os
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
proofpath=out/'day11-GUI-same-path-normal9-P0-proof.json';b=json.loads(proofpath.read_bytes())
assert len(b['rows'])==9 and b['new_pair_received']==1 and abs(b['allocated_gap_mm']-.3844891445638857)<1e-8
assert b['allocated_common_valid'] and b['allocated_common_mm3']==0 and b['nominal_common_valid'] and b['nominal_common_mm3']==0
assert b['normalpacking_min_gap_mm']>=.2-1e-8 and b['qualified_subset']['old_circle_outside_volume_mm3']<1e-6
snap=out/'day11-WORKING_UNSELECTED_N01_0of10.FCStd';idxp=out/'day11-GUI-working-snapshot-source-index.json';idx=json.loads(idxp.read_bytes())
assert idx['current_actor_count']==1311 and len(idx['actor_names_to_objects'])==1455
idx['snapshot_initial_creation_sha256']=idx['snapshot_sha256'];idx['snapshot_sha256']=sha(snap)
idx['GUI_current_document']='day11_WORKING_UNSELECTED_N01_0of10';idx['GUI_current_object_count']=1470
idx['GUI_diagnostic_effectivity']='4 diagnostic shapes + group added, same retained1311 material unchanged; correctedfield not selectedroute.'
idx['GUI_final_visibility']='retained1311 + neutral108 + proposedSOURCE21; alternativeG4/D5/temp4/steelreferences/boundary/diagnosticfield hidden, separatelyaddressable; no additive oldparents.'
write(idxp,idx)
obs=out/'day11-GUI-current-model-save-observation.json';s=json.loads(obs.read_bytes());s.update(label='WORKING_UNSELECTED_N01_0of10 / retained1311 + neutral108 + proposedSOURCE21',modified=False,save_confirmation='NativeMCP list_documents after observed-window Ctrl+S: one active document,1470objects,modified=False. No CAD code after final UI save.',confirmed_utc='2026-11-11T00:36:53Z',GUI_left_open=True,geometry_owner='Banach GUI_MCP PID26044',auxiliary_source_cache=dict(pid=11476,session_id=70789,state='IDLE_NO_PENDING_NO_WRITES_AFTER_GUI_HANDOFF'),snapshot_sha256=sha(snap));assert (s['retained'],s['moving108'],s['SOURCE21'],s['visible_moving'],s['visible_source'])==(1311,108,21,108,21);write(obs,s)
names=[snap.name,idxp.name,obs.name,proofpath.name,b['archive'],'day11-GUI-normal9-P0-local-isolated.png','day11-GUI-WORKING-1311-with-neutral108-SOURCE21.png']
for src,dst in [('robot-cat11-GUI-data-snapshot.py','day11-GUI-data-snapshot.recipe.py'),('robot-cat11-GUI-normal-field-P0-correction.py','day11-GUI-normal-field-P0-correction.recipe.py'),('robot-cat11-finish-GUI-normal9.py','day11-GUI-normal9-packet-finalize.recipe.py')]:
 (out/dst).write_bytes((temp/src).read_bytes());names.append(dst)
checks=[]
with zipfile.ZipFile(out/b['archive']) as z:
 assert z.testzip() is None
 for q in b['geometry']:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
 checks.append(dict(path=b['archive'],CRC=True,exact_BRep_member_SHAs=len(b['geometry'])))
with zipfile.ZipFile(snap) as z:
 assert z.testzip() is None
 assert 'Document.xml' in z.namelist()
 checks.append(dict(path=snap.name,CRC=True,DocumentXML_sha256=hashlib.sha256(z.read('Document.xml')).hexdigest(),scope='NEWdisplay-snapshot file integrity; not replay of oldsource/currentgeometrytests.'))
pins=['day07-final-window-current-base-and-proposed-resume-manifest.json','day07-removable-Pi-carrier-current-candidate-composition.json','day07-MODULE-V3-capacity-current-candidate-composition.json','day07-S0-C1-current-candidate-composition.json','day11-P0-connected-space-bounded-disposition.json','day11-P0-connected-space-and-load-interface-read.json','day11-WHOLE_N01-architecture-bounded-disposition.json','day11-WHOLE_N01-layout-architecture-and-closure-plan.json','day11-whole-source-group-first-gate.json','day07-SOURCE-actual-frame-passage-source-inputs.json','n01-selected-piece-profile-contract.json']
external=[root/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd',root/'tools/freecad/skorupa/build20.py']
pp=out/'day11-GUI-current-model-and-normal9-bounded-disposition.json'
nextstep='The same path fails even with all9 actual nominal profiles and unchanged margins. End this evidence correction; no secondroll/height/pitch/quarter/stock variant. Next whole architecture decision must replace the conflicting separate PETG chassis-shell load/entry interface OR choose a causally different connected transport/order based on actual source->A->B->C->trueDGV space. Preserve M2.5anchor/NutShoe, solid indexingdowel, M3axis/steel/nutfeed/tool/shellbearing/verticalshelllift, realframe, factoryends and fullstock. No local trim/newMount detail before wholepath/R/roll/assembly/usable55/perphysical length premise. Four links remainUNKNOWN; no geometryGO from GUI.'
r=dict(id=pp.stem,status='GUI_OPERATIONAL_SAVED_ACTUAL_NORMAL9_SAME_PATH_P0_HOLD_STOP_CORRECTION',N01='0/10',selected=False,whole_feasible=False,
 decision='Removing only excess circular-cover area does not close this path: actual nominalall9 still fail foreign1.25. No newroute/roll/pose/support or counterreset.',
 measured=dict(allocated_gap_mm=b['allocated_gap_mm'],allocated_common_valid=True,allocated_common_mm3=0,nominal_gap_mm=b['nominal_gap_mm'],nominal_common_valid=True,nominal_common_mm3=0,required_foreign_mm=1.25,witnesses=b['witnesses'],new_local_pair_received=1,meaning='Allocated clearance HOLD, no deliveredwire contact; only exact same chosen Bishop field/path falsified, not allpacking/allspace/stock.'),
 coverage=dict(all9_profiles=b['rows'],normalpacking_min_gap_mm=b['normalpacking_min_gap_mm'],margin_mm=.4,nominalfullprofiles_mm=[3.1,2,3.1],normalframe=b['normalfield'],unchanged_path=b['path_parameters_unchanged'],old_circle_subset=b['qualified_subset'],critical_scope='Full9 over actual P0 upper-wall straight interval X[-69.5,-57.5], same analyticentry/helix/crest/exit. Local BRep is not a newterminal/debit nor fullglobal123axes. Nonlocaloverlap notaccepted; firstactualP0falsifier stopsdependentneighbors.',all_full_neighbors_NOT_accepted=True),
 raw_frozen=dict(circle_common_mm3=17.140621176002977,circle_received=2,circle_total=154,circle_UNRECEIVED=152,old_iterator_NOT_resumed=True,worldZ_axes_diagnostic_min_gap_mm=3.148785,worldZ_diagnostic_NOT_physical_counter=True,all_older_negative_counts_preserved=True),
 GUI=dict(**s,connection='ExistingFreeCADAI0.23.1-alpha nativeMCP at127.0.0.1:3000/mcp; structuredlistdocs/measurebbox/setview/zoom/capture used. Minimalexecute_code only unsupported existing-data import, namedsourcebind, normalfield geometry and documentmetadata/save.',data_snapshot_operation_seconds=idx['operation_seconds'],data_snapshot_process_CPU_seconds=idx['process_cpu_seconds'],source1292_unchanged=True,current_effective1311='def->2d1->a9f',reference_effectivity='G4/D5 alternatives hidden, not selected/not additive oldparent; SOURCE21+temp4 separately proposed; neutral108 reference not newBOM. Original1292 not recreated as duplicate visible group.',technical_errata=['First blankwhite capture and later occludedlocal screenshot rejected as visual evidence; finalwhole and isolatedP0 capture visuallyinspected.','MCP AttributeError Document.Modified occurred AFTER successfulsave; representationunchanged. Corrected by actual structuredlist_documents after ordinary UI save; finalmodifiedFalse.','An earlierMCP NoneType.success recovery changedlabel to .ai-backup; finalcorrectlabel and namedFCStd saved. No sourcegeometry/designfailure from interface errors.']),
 source_hardware=dict(original4_confirmed=True,current_actor_alias='UNKNOWN_NOT_ABSENT',source_relativepose='CurrentMountFrontL andNutShoe two-way materialdifference0/0 from previous910ff7a1/0c728e6f; source4steel worldrelativepose qualified to those matchedparents. WorldONCE/no secondXML.',reference_only_group='SourceSteelReference in GUI; qualifiedsourcekeepouts, NOT additivephysicalBOM/importedextra4parts.',dependent_clearance_NOT_accepted=True,no_new_hardware_binding_scan_after_first_P0_HOLD=True,Mount_function='SeparatePETGchassis-shellmount, not boughtimmutable module. SolidR1.2indexdowel isnotfreehole. Actual M2.5anchor/M3axis/nutfeed/tool/shellbearing/lift preserved.'),
 retained=dict(base=1292,effective=1311,MAIN_mm=46.52,base_manifest_sha256=sha(out/pins[0]),no_new_selected_layout=True,G4_D5_SOURCE='PROPOSED only',source21_moving_and4temp='data-only neutral references/currentpinnedsourcecontext',rest108='data-only neutralreference; no oldmotionreplay'),
 all_four_connected_links='UNKNOWN moving->A / A->B / B->C / C->trueDGV; selected criticalpath allocation HOLD, sections notwholefreeway.',
 global_OPEN=['SOURCE actual connectedspace/KneeHipmovingR/actualpercoreLi-delta/usable55EACHFL2+Hip10/perunit850project900ceil5(min+20)MAX3/A-U-fit-slack-cutNULL','D5OWNcontinuousclosureface29/120 technicalinvalidderivedToroid,204validchecks preserved; not sourceinvalid/contact/newdesignfailure','F_R4housingcapture+2stockbindings','S0routineoperatorportal/cowlPWM','wholeFPIfore-neck/loadlayer+shortfactoryW043/W077/W078/MAINinputbinding+V3support','R6/Pimates/U1far/headNorth/123246/lengthslack/changedmotion-outline'],
 USB3='a1422d04/96eb8a6e three gates CLOSED_SCOPED; no staleinvalid3GLOBALOPEN/no replay',
 physical_invariants='9IDs/12portions/4physicalMAX3/sourceFL1FL2continuous/FL2NOlap4/FL3properexistingjoint/source14terminal11full9properprefixONCE/3laps8+3sleeves20/stagger2x9/factoryplugs/850project900ceil5(min+20)/fittrim20notoperatingslack/Knee55EACHFL2Hip10/E_i=55+maxLi-Li(p),delta<=10 IF55..65, U125..135alreadycontainsE/no pooling/no cut/newsplice/purchase. Fourindependent220/both4MTA/MODULEsoldered/selectedR47P0E6MAIN46.52/15MG92B/envelope325x200x160/max200namedcarrier/256cube/foreign1.25/BodyOuter3.25 unchanged.',
 initialassembly='Reuse received partialorder only, not wholeN08: benchMODULE/MTA/FPIlap+MAINinput -> P0nuts/S0fasteners -> connectedSOURCE beforeE6 -> D5keeper+FRGkey/full83.3 -> WHOLEF_R4IN+OUT once afterclamp/D5 -> FPIcaseband/strains/DGVpressure afterlay -> MAIN/Pimates/headNorth/R6access -> batterystrap/skins. Linkedkitopening, F_R4capture2stock, simultaneousFPI-S0V3PWMaccess remainUNKNOWN.',
 timing=dict(bounded_start_UTC='2026-11-11T00:12:29Z',correction_operation_seconds=b['operation_seconds'],correction_process_CPU_seconds=b['process_cpu_seconds'],save_confirmed_UTC='2026-11-11T00:36:53Z',written_utc=datetime.now(timezone.utc).isoformat()),
 views=[dict(path=n,sha256=sha(out/n),visually_inspected=True,not_geometry_GO=True) for n in names if n.endswith('.png')],
 source_pins=[dict(path=n,sha256=sha(out/n)) for n in pins]+[dict(path=str(p),sha256=sha(p)) for p in external],
 packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=checks,
 next=nextstep,authorization='Resultstage remains enabled/no deadline/no percentthreshold; partialfinal not close/newpermission.',pending_operation=None,unsaved_geometry=False)
write(pp,r);names.append(pp.name)
# Exact whitelist commit, preserve foreign staged/working hunks.
files=[str((out/n).relative_to(root)).replace('\\','/') for n in names];env=os.environ.copy();env['GIT_INDEX_FILE']=str(temp/'robot-cat11-GUI-normal9-exact.index');assert not Path(env['GIT_INDEX_FILE']).exists()
def git(args,data=None,custom=False):return subprocess.run(['git',*args],cwd=root,env=env if custom else None,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
base=git(['rev-parse','HEAD']).decode().strip();git(['read-tree',base],custom=True);entries=[];hashes={}
for n in files:
 raw=(root/n).read_bytes();blob=git(['hash-object','-w','--stdin','--no-filters'],data=raw).decode().strip();entries.append('100644 '+blob+'\t'+n+'\0');hashes[n]=hashlib.sha256(raw).hexdigest()
git(['update-index','-z','--index-info'],data=''.join(entries).encode(),custom=True)
assert set(git(['diff','--cached','--name-only','-z'],custom=True).decode().strip('\0').split('\0'))==set(files)
tree=git(['write-tree'],custom=True).decode().strip();commit=git(['commit-tree',tree,'-p',base],data=b'Save current N01 GUI model and same-path complete normal9 P0 clearance HOLD\n').decode().strip();git(['update-ref','-m','commit: current GUI and adequate normal9 evidence','HEAD',commit,base])
raw=git(['cat-file','--batch'],data=''.join(commit+':'+n+'\n' for n in files).encode());at=0
for n in files:
 end=raw.index(b'\n',at);size=int(raw[at:end].split()[2]);body=raw[end+1:end+1+size];at=end+size+2;assert hashlib.sha256(body).hexdigest()==hashes[n] and sha(root/n)==hashes[n]
git(['update-index','-z','--index-info'],data=''.join(entries).encode())
card=root/'hardware/HOBBY_COMPLETION_PLAN.md'
fact='OWNER_RESULT_RECEIVED: '+pp.name+' SHA'+sha(pp)+' /owncommit'+commit[:8]+'/'+str(len(files))+'exactfiles. GUI26044/MCP one WORKING_UNSELECTED_N01_0of10 document/1470objects/retained1311+separate refs/MAIN46.52/worldONCE; savedmodifiedFALSE, whole+isolatedlocalview inspected. Aux11476/70789IDLE cacheonly. SAMEpath/Bishop actual9 fullprofiles/.2gap/.4margin stillP0gap.384489145<1.25 validcommon0; nominalgap.784489145/common0. HELIXcoreRlower37.837425/crest>=35.1; actualfield outsideoldcircle0. NEW1localpair, rawcircle17.140621 2/154+152frozen, no counterreset/replay/newpath/roll/support. Source4steelqualifiedrelativepose keepouts/currentaliasesUNKNOWNnotabsence/no duplicateBOM. FourlinksUNKNOWN/AUfit-slack-cutNULL/N010.\n\nNEXT: '+nextstep+'\n\n'
for _ in range(4):
 raw=card.read_bytes();txt=raw.decode('utf-8');a=txt.index('CURRENT_OWNER_INPUT:');e=txt.index('ODEBRANE I ZWERYFIKOWANE:',a);new=(txt[:a]+fact+txt[e:]).encode('utf-8')
 if card.read_bytes()!=raw:continue
 q=card.with_suffix('.owner-GUI-final.tmp');q.write_bytes(new);os.replace(q,card);break
else:raise RuntimeError('Concurrent card edit: result saved/committed, card merge not applied')
rt=Path('C:/Users/Sysq/PycharmProjects/robot-cat/.codex/hooks/robot-cat-work-window.json')
for _ in range(4):
 raw=rt.read_bytes();d=json.loads(raw);w=d['active_worker'];w.update(state='IDLE_GUI_SAVED_NORMAL9_P0_HOLD_CORRECTION_COMPLETE',receive=r['status'],latest_receipt=str(pp),latest_receipt_sha256=sha(pp),latest_local_commit=commit,latest_commit_exact_byte_files=len(files),active_gui_pid=26044,gui_transport='nativeMCP port3000 soleCADwriter',gui_document=s['document'],gui_document_label=s['label'],gui_snapshot=str(snap),gui_snapshot_sha256=sha(snap),gui_model_modified=False,headless_source_cache_pid=11476,headless_source_cache_session_id=70789,headless_source_cache_state='IDLE_NO_COMPETING_WRITES',pending_operation=None,pendingoperation=None,unsaved_geometry=False,agent_turn_state='bounded_complete_GUI_open_headless_idle',confirmed_utc=datetime.now(timezone.utc).isoformat(),next=nextstep)
 if rt.read_bytes()!=raw:continue
 q=rt.with_suffix('.owner-GUI-final.tmp');write(q,d);os.replace(q,rt);break
else:raise RuntimeError('Concurrent runtime edit: packet committed, metadata not applied')
print(json.dumps(dict(receipt=pp.name,sha256=sha(pp),commit=commit,exact_files=len(files),packetpins=len(r['packet_pins']),sourcepins=len(r['source_pins']),archives=checks,GUI=s['label'],objects=1470,GUI_modified=False,GUI_pid=26044,sourcecache='11476/70789 IDLE',pending=None,unsaved=False,N01='0/10',enabled=d['enabled']),indent=2))
