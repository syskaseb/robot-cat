from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,subprocess,os
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=out/'day07-whole-FR4-late-bank-initial-order-parting-boundary-bounded-disposition.json';r=json.loads(p.read_bytes());assert r['continuous_reciprocal_bank']['received']==44 and r['inherited_actual_source_diagnosis']['prior_current_overlap_two_way_missing_mm3']==[0,0]
r['view'].update(visually_inspected=True,inspection='Actual XZ atY-31 andYZ atX58 inspected: red shared material occurs at BOTH downward case face stops and permanent pressure beam below full5source channels. Geometry samebefore/after real keeper transfer; projection not contact evidence, valid BOP is witness.')
r['stopped_at_first_missing_functional_gate']=True;r['distinct_print_overlap_NOT_accepted_as_intentional_fit']=True
lesson_path='hardware/cad/DESIGN_LESSONS.md';lesson=root/lesson_path;lesson_raw=lesson.read_bytes()
addition=('\n- Przy odbiorze osobnego korpusu i zdejmowanego docisku sprawdzić\n  poprawne lower.common(upper) == 0 przed montażem; zamierzony wcisk\n  wymaga osobnego uzasadnienia. Zerowe różnice sumy i valid+1Solid\n  każdej części nie wykluczają wspólnego materiału. D5: dwa stopery\n  dzieliły 6.673236 mm3 z belką, mimo niezmienionej sumy.\n').encode()
assert addition not in lesson_raw
def git(args,data=None,custom=False):return subprocess.run(['git',*args],cwd=root,env=env if custom else None,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
env=os.environ.copy();env['GIT_INDEX_FILE']=str(temp/'robot-cat90-late-bank-parting-exact.index');assert not Path(env['GIT_INDEX_FILE']).exists()
base=git(['rev-parse','HEAD']).decode().strip();lesson_head=git(['show',base+':'+lesson_path]);lesson_index=git(['show',':'+lesson_path]);assert lesson_index==lesson_head,'Preserve already-staged foreign lesson changes: do not overwrite their index.'
lh=lesson_head.index(b'\n')+1;lw=lesson_raw.index(b'\n')+1;new_lesson_head=lesson_head[:lh]+addition+lesson_head[lh:];new_lesson_work=lesson_raw[:lw]+addition+lesson_raw[lw:]
r['own_lesson_change']=dict(path=lesson_path,inserted_UTF8_bytes_sha256=hashlib.sha256(addition).hexdigest(),added_lines=len(addition.splitlines()),committed_from_HEAD_plus_ONLY_this_insert=True,foreign_working_bytes_preserved=True,not_whole_working_lesson_exactbyte_claim=True)
n='day07-late-bank-order-finalize-bank-order-parting-boundary.recipe.py';assert not(out/n).exists();(out/n).write_bytes(Path(__file__).read_bytes());r['packet_pins'].append(dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size));p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());names=[q['path'] for q in r['packet_pins']]+[p.name];assert len(names)==len(set(names))
for q in r['packet_pins']:assert sha(out/q['path'])==q['sha256']
for q in r['source_pins']:assert sha(out/q['path'])==q['sha256']
for q in r['external_source_pins']:assert sha(Path(q['path']))==q['sha256']
for q in r['archive_checks']:
 with zipfile.ZipFile(out/q['path']) as z:
  assert z.testzip() is None;gg=json.loads(z.read('manifest.json'))['geometry'];assert len(gg)==q['member_sha_verified']
  for v in gg:assert hashlib.sha256(z.read(v['entry'])).hexdigest()==v['sha256']
files=[str((out/n).relative_to(root)).replace('\\','/') for n in names];entries=[];hashes={};git(['read-tree',base],custom=True)
for n in files:
 raw=(root/n).read_bytes();blob=git(['hash-object','-w','--stdin','--no-filters'],data=raw).decode().strip();entries.append('100644 '+blob+'\t'+n+'\0');hashes[n]=hashlib.sha256(raw).hexdigest()
lesson_blob=git(['hash-object','-w','--stdin','--no-filters'],data=new_lesson_head).decode().strip();entries.append('100644 '+lesson_blob+'\t'+lesson_path+'\0');git(['update-index','-z','--index-info'],data=''.join(entries).encode(),custom=True)
assert set(git(['diff','--cached','--name-only','-z'],custom=True).decode().strip('\0').split('\0'))==set(files+[lesson_path])
assert lesson.read_bytes()==lesson_raw;q=lesson.with_suffix('.owner90.tmp');q.write_bytes(new_lesson_work);os.replace(q,lesson)
tree=git(['write-tree'],custom=True).decode().strip();commit=git(['commit-tree',tree,'-p',base],data=b'Preserve late whole-bank reciprocal clearance and inherited D5 parting defect\n').decode().strip();git(['update-ref','-m','commit: whole late bank and actual D5 parting defect','HEAD',commit,base])
raw=git(['cat-file','--batch'],data=''.join(commit+':'+n+'\n' for n in files).encode());at=0
for n in files:
 end=raw.index(b'\n',at);size=int(raw[at:end].split()[2]);body=raw[end+1:end+1+size];at=end+size+2;assert hashlib.sha256(body).hexdigest()==hashes[n] and sha(root/n)==hashes[n]
assert git(['show',commit+':'+lesson_path])==new_lesson_head and lesson.read_bytes()==new_lesson_work
assert new_lesson_work[:lw]+new_lesson_work[lw+len(addition):]==lesson_raw
git(['update-index','-z','--index-info'],data=''.join(entries).encode())
lesson_numstat=git(['diff','--numstat',base,commit,'--',lesson_path]).decode().strip()
card=root/'hardware/HOBBY_COMPLETION_PLAN.md';raw=card.read_bytes();i=raw.index(b'## Historia poprzednich okien');pre=raw[:i].decode();tail=raw[i:];j=pre.index('\n',pre.index('## Bieżąca'))+1
fact='\nWHOLE_FR4_LATE_BANK_RECIPROCAL_RECEIVED_INHERITED_D5_PARTING_DEFECT: '+p.name+' SHA'+sha(p)+' /owncommit'+commit[:8]+'/'+str(len(files))+'exactARTIFACTfiles+ONLYownlesson'+str(len(addition.splitlines()))+'lines(foreignworkinglessonbytespreserved). SourceWHOLEFR4MTA0300330+ATO+TE4-520448-2IN/W054LAPPandTE2-520184-2OUT/W055SOURCE_RR1, notINalone/4protectedfactoryMTA/U1MODULEunplug. NEW4continuous+Z0..12covers actualsource0outside/44of44necessaryreciprocalpairs vswholeD5keeper/case/4steel/full145stock CLEARmin3.825019 (43bounds+1actualcover). Notwholebankretention/otherneighbors/stocktailsPASS. FIRSTmissingupperFUNCTIONactuallower.common(upper) VALID6.673236HOLD. SAMEPRIORnewframe209/up2026.673236/overlapidentity0/0=>inheritedconstructionpartingdefect, NOTneworderstrategyfailure. ExactPressureLoadBeamvsSouthCaseFaceStop3.673236+North3.000000; unchangedC1full9upper/web0. No geometryrepair/secondorderfamily afterfirstfalsifier. NeedgenuineDISJOINTsamefunctionalprintpartition retainingbeam/root/full9/uppercapture/loadjoints/145; operatingunion0/0 and1solideachdidNOTprovepartseparability. Newwideupperentry/closure+wholebankkitcaseholding/stockbindingsOPEN; historicalconstructorflagsNOTcurrentnegative. Oldallcounts/static/motion22575/31605/27k36k155451548USB preserved/no replay; source9Li-delta55/850900MAX3/AUfitslackNULL/actualcutNULL/whole123246N010. 2ZIP15BRepSHA/actual2sectionsviewed. Same26064/46493IDLE pendingnull unsavedfalse/windowACTIVE.\n'
pre=pre[:j]+fact+pre[j:]
for label,value in [('NEXT:',r['next']),('CURRENT_OWNER_CHUNK:','Same26064/46493 bounded90complete: whole4F_R4reciprocal44scopedCLEAR; sourcecorrectIN/OUT+W054/W055roles pinned. Newnecessarydistinct-print gate exposesINHERITED6.673236permanentbeam/twoface-stop overlap, old/newwitnessidentity0/0. No repair/secondfamilybuilt. Needactualsamefunctionaldisjointpartition beforeupperentryclosure, thenwholeSOURCE. PreviousqueuedNEXTs historical; currentbaseunchanged/N010.')]:
 if '\n'+label in pre:
  a=pre.index('\n'+label)+1;e=pre.find('\n\n',a);e=len(pre) if e<0 else e;pre=pre[:a]+label+' '+value+pre[e:]
 else:pre+='\n'+label+' '+value+'\n'
assert card.read_bytes()==raw;q=card.with_suffix('.owner90final.tmp');q.write_bytes(pre.encode()+tail);os.replace(q,card)
rt=Path('C:/Users/Sysq/PycharmProjects/robot-cat/.codex/hooks/robot-cat-work-window.json');raw=rt.read_bytes();d=json.loads(raw);d['active_worker'].update(pid=26064,session_id=46493,state='IDLE_WHOLE_LATE_FR4_RECIPROCAL_CLEAR_INHERITED_D5_DISTINCT_PRINT_DEFECT',receive=r['status'],latest_receipt=str(p),latest_receipt_sha256=sha(p),latest_local_commit=commit,latest_commit_exact_byte_files=len(files),latest_commit_additional_own_lesson_hunk=lesson_numstat,pending_operation=None,pendingoperation=None,unsaved_geometry=False,agent_turn_state='bounded_complete_native_idle',confirmation='Same26064/directTTY46493 actualprompt following226source-member save. Wholebank44reciprocalclear; inheritedseparateprintcommon6.673236 withtwofaceStops pinned andsaved; no geometryrepair/newprocess/oldchecks. Allnewgeometry/source/witness/actualsections saved.',confirmed_utc=datetime.now(timezone.utc).isoformat(),next=r['next']);assert rt.read_bytes()==raw;q=rt.with_suffix('.owner90final.tmp');q.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode());os.replace(q,rt)
print(json.dumps(dict(receipt=p.name,sha256=sha(p),commit=commit,exact_artifact_files=len(files),additional_lesson_own_hunk_numstat=lesson_numstat,packetpins=len(r['packet_pins']),sourcepins=len(r['source_pins']),externalpins=len(r['external_source_pins']),members=sum(q['member_sha_verified'] for q in r['archive_checks']),wall=r['measured_native_wall_seconds'],CPU=r['measured_native_CPU_seconds'],viewSHA=sha(out/r['view']['path']),native='26064/46493 IDLE pendingnull unsavedfalse',enabled=d['enabled'],N01='0/10'),indent=2))
