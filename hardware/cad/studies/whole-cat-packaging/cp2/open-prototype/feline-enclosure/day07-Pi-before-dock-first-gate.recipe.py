import json,time,hashlib,zipfile,os
t42=time.monotonic();c42=time.process_time()
meta42=json.loads((OUT/'day07-microSD-partial-repair-input-and-first-gate.json').read_bytes())
src42=json.loads((OUT/'day07-JPWM-source13-release-and-park-proposal.json').read_bytes())
pi36={r['name'] for r in json.loads((OUT/'day05-Pi45-complete-local-source-inputs.json').read_bytes())['rows']}
moving42=[r['name'] for r in meta42['moving_board_with_card_actors']]
dock_later42={r['actor'] for r in src42['roles13'] if r['actor'] not in src42['permanent_not_removed']}
notlaid42={n for n in Current35 if n.startswith(('Underdeck:SOURCE:','Flat:MODULE:'))}
fixed42={n:s for n,s in Current35.items() if n not in pi36|dock_later42|notlaid42}
fixed42.update({'C1:'+n:s for n,s in W37parts.items()})
assert len(moving42)==14 and len(pi36)==36 and len(dock_later42)==11
plan42=dict(id='day07-Pi-before-dock-initial-assembly-scope',status='ONE_ASSEMBLY_ORDER_HYPOTHESIS',N01_complete=False,selected=False,
 cause_changed='Do not park an already wired MODULE half in the rejected northwest bay. Initial construction installs Pi/card before seating dock and before board-end final solder/restraints; rare repair is a separate documented dependency, not a new permanent service sling.',
 sequence=['Build/retain complete permanent CommonSupport, both open saddles, west C1 frame and source Pi rails. Case not seated, 3 dock one-way ties not installed yet.',
 'Fit microSD to Pi on bench. Install bare Pi with its 13 onboard components via proposed left entry at Z-5, then raise5 into unchanged rails; retain all four sourceM2/metal and full original access.',
 'Lay four complete factory225+/-5/min220 units in received open regions. Dryfit both bought MicroFit halves; seat mated dock using reverse of received7mm lateral body release; no supplier-latch shrink or stroke inference.',
 'Preserve preformed full prefixes/9/R/OD and all current installed whole-unit debits. Source endpoint insertion, final board-end solder to named U_PWM terminals and final restraint closure occur only after routing/dryfit; no physical solder or cut here.',
 'Close 3 full100 dock ties and any separately counted source/Pi restraint units after tool and mating access. Tie replacement is a future consumable requirement, not a releasable fastener.',
 'Rare repair: source endpoints P_REAR.4/G_TAIL.3 must be freed with their actual release functions; F_PWM/pigtail handling whole. MODULE remains soldered to U_PWM; manually support freed housing in available open-cover space rather than adding a sling. Actual connected storage/endpoint access must be received before accepting that reverse.'],
 stock=src42['stock'],
 first_falsifier='All14 valid onboard operands at proposed left-entry final lower Z-5 against all current fixed hardware/material plus7C1cells, excluding ONLY36Pi assembly and11not-yet-installed dock actors and declared unlaid flexible middles. Purchased contact/foreign gap<1.25 rejects this endpoint; own Pi mounting interface only by source function. No complete left99 trajectory or reverse-wire parking PASS.',
 moving=moving42,not_yet_installed=sorted(dock_later42),not_yet_laid_flexible=sorted(notlaid42),permanent_retained=src42['permanent_not_removed'],fixed_count=len(fixed42),
 source_scope='Legacy E2 selectedfalse supports bench solder-after-dryfit and cut-ties-not-wires lifecycle only; obsolete module150 not imported. All four currentfactory225 retained.',
 source_pins=[dict(file=n,sha256=hashlib.sha256((OUT/n).read_bytes()).hexdigest()) for n in ['day07-microSD-partial-repair-input-and-first-gate.json','day07-JPWM-source13-release-and-park-proposal.json','day07-JPWM-release-assembly-dependency-disposition.json']],
 no_new_print_or_pose=True,old_4_body_3_park_pairs_repeated=False)
pp42=OUT/'day07-Pi-before-dock-initial-assembly-scope.json';assert not pp42.exists();pp42.write_bytes((json.dumps(plan42,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
order42=sorted(moving42,key=lambda n:(0 if n=='PiBudget:DSI' else 1 if 'PCB' in n else 2,n))
tasks42=[];poses42={}
for n in order42:
 s=Current35[n].copy();s.translate(A.Vector(0,0,-5));poses42[n]=s
 for b,q in fixed42.items():
  if bbox_lower_bound(s.BoundBox,q.BoundBox)<=1.25:tasks42.append((n,b))
rows42=[];stop42=None
for n,b in tasks42:
 s,q=poses42[n],fixed42[b]
 r=dict(moving=n,fixed=b,moving_valid=s.isValid(),fixed_valid=q.isValid())
 if not r['moving_valid'] or not r['fixed_valid']:r['status']='INVALID_SOURCE_UNRESOLVED_NOT_CONTACT'
 else:
  try:
   g,w,_=s.distToShape(q);r.update(gap_mm=g,witnesses=[[list(a),list(z)] for a,z in w[:1]])
   if g<1e-7:
    co=s.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
   r['status']='SEPARATED125' if g>=1.25-1e-7 else 'INITIAL_ENTRY_ENDPOINT_HOLD'
  except Exception as ex:r.update(status='KERNEL_ERROR_UNRESOLVED_NOT_CONTACT',error=str(ex))
 rows42.append(r)
 if r['status']=='INITIAL_ENTRY_ENDPOINT_HOLD':stop42=r;break
ar42=OUT/'day07-Pi-before-dock-first-gate-inputs.breps.zip';assert not ar42.exists();gg42=[]
with zipfile.ZipFile(ar42,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate([(n,s) for n,s in poses42.items()]+[(b,fixed42[b]) for b in sorted({r['fixed'] for r in rows42})]):
  raw=s.exportBrepToString().encode('utf-8');e=str(i)+'.brep';z.writestr(e,raw);gg42.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=gg42,scope='Transient initial-entry endpoint only; installed Current35 unchanged'),indent=2)+'\n').encode())
r42=dict(id='day07-Pi-before-dock-first-initial-entry-gate',status='INITIAL_ORDER_REJECTED_AT_LOWER_ENTRY_ENDPOINT' if stop42 else 'LOWER_ENTRY_ENDPOINT_RECEIVED_ONLY',rows=rows42,cursor=len(rows42),total=len(tasks42),unreceived=len(tasks42)-len(rows42),stop=stop42,
 planned_moving_onboard_count=14,complete_fixed_count=len(fixed42),source_scope=pp42.name,source_scope_sha256=hashlib.sha256(pp42.read_bytes()).hexdigest(),archive=ar42.name,archive_sha256=hashlib.sha256(ar42.read_bytes()).hexdigest(),geometry=gg42,
 left99_continuous_entry_NOT_received=True,whole_reverse_module_source_park_NOT_received=True,current_installed_actors=1292,installed_geometry_unchanged=True,operation_seconds=time.monotonic()-t42,process_cpu_seconds=time.process_time()-c42,pid=os.getpid(),session_id=46493,N01_complete=False,selected=False)
rp42=OUT/'day07-Pi-before-dock-first-initial-entry-gate.json';assert not rp42.exists();rp42.write_bytes((json.dumps(r42,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print('PI_BEFORE_DOCK_FIRST',r42['status'],len(rows42),len(tasks42),stop42,r42['operation_seconds'],r42['process_cpu_seconds'],hashlib.sha256(rp42.read_bytes()).hexdigest(),flush=True)
