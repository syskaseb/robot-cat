import json,time,hashlib,os
t194=time.monotonic();c194=time.process_time();assert first193 is None
padname194='CurrentFoundation:BankPad:Ref_Material_F_R5_CP2_Housing_0_0:0';housingname194='Ref_Material_F_R5_CP2_Housing_0_0';ledge194=Current35['CurrentFoundation:BankLedge:3'];bank194=Current35['Underdeck:RestoredBank'];pad194=Current35[padname194];housing194=Current35[housingname194]
path194=[]
for n,a,b in [('C1containsFULLcurrentLedge3',ledge194,base193),('CURRENTLedge3_to_actualRestoredBank',ledge194,bank194),('CURRENTactualRestoredBank_to_R5pad',bank194,pad194),('C1protectedClampNeck3',base193,Current35['CurrentFoundation:ClampNeck:3'])]:
    co=a.common(b);path194.append(dict(interface=n,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None))
bearing194=pad194.common(housing194);contact194=0.
if bearing194.isValid() and bearing194.Volume<1e-7:
    # One missingCURRENT bearinglink read, no oldwholefoundation replay.
    for f in pad194.Faces:
        if abs(f.BoundBox.ZMin-55)<1e-6 and abs(f.BoundBox.ZMax-55)<1e-6:
            contact194+=sum(f.common(g).Area for g in housing194.Faces if abs(g.BoundBox.ZMin-55)<1e-6 and abs(g.BoundBox.ZMax-55)<1e-6)
pathok194=all(q['common_valid'] and q['common_mm3']>1e-7 for q in path194) and bearing194.isValid() and bearing194.Volume<1e-7 and contact194>=427.5-1e-5
tasks194=[];covers194=0
for i,(r,a) in enumerate(zip(routes193,voids193)):
    for n,b in ctx182.items():
        bb=bounds126[n] if n in bounds126 else b.BoundBox;lo=bbox_lower_bound(a.BoundBox,bb)
        if lo>=1.25-1e-7:covers194+=1;continue
        priority=0 if ('Housing' in n or '_ATO_' in n or n.endswith(':case') or n.startswith('Ref_Material_P0_')) else 1 if n.startswith('CurrentFoundation:') else 2
        tasks194.append((priority,i,n,a,b,lo))
tasks194.sort(key=lambda q:(q[0],q[1],q[2]));rows194=[];first194=None;lastfield194=None;lastpart194=None
for _,i,n,a,b,lo in tasks194:
    row=dict(wire=routes193[i]['wire'],actor=n,bbox_lower_mm=lo,required_foreign_mm=1.25,source_valid=b.isValid())
    if not row['source_valid']:row['status']='SOURCE_INTEGRITY_OPEN_NOT_CONTACT'
    else:
        ga,ww,_=a.distToShape(b);row.update(gap_mm=ga,witnesses=[[list(x),list(y)] for x,y in ww[:1]],status='NEW_CONTINUOUS_EXIT_FOREIGN_SEPARATED125' if ga>=1.25-1e-7 else 'NEW_FULL_EXIT_ALLOCATED_FOREIGN_HOLD_NOT_DELIVERED_CONTACT')
        if ga<1e-7:
            co=a.common(b);row.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
    rows194.append(row)
    if row['status']!='NEW_CONTINUOUS_EXIT_FOREIGN_SEPARATED125':first194=row;lastfield194=a;lastpart194=b;break
    if time.monotonic()-t194>12:break
p194=OUT/'day07-five-D-continuous-C1-current-bankpath-and-exit-foreign.json';assert not p194.exists();r194=dict(id=p194.stem,status='C1_CONTINUOUS_EXIT_FIRST_FOREIGN_HOLD' if first194 else ('C1_CONTINUOUS_EXIT_FOREIGN_SCOPED_RECEIVED' if len(rows194)==len(tasks194) else 'C1_CONTINUOUS_EXIT_FOREIGN_CURSOR_PENDING'),C1material_first_receipt=p193.name,C1material_first_sha256=hashlib.sha256(p193.read_bytes()).hexdigest(),legacy_current_revision_effectivity=dict(historical_BankBed_minus1_named_actor_present=False,actual_current_mapped_parent='Underdeck:RestoredBank',mapping_source='day05-Pi45-local-preflight-scope.json material_lineage/current_bank: copiesBankBed-1 thenopen-support-bankoverride, no assumedoldunchangedbed.',CURRENTactual_links=path194,CURRENT_R5_pad_case_common_valid=bearing194.isValid(),CURRENT_R5_pad_case_common_mm3=bearing194.Volume if bearing194.isValid() else None,CURRENT_R5_bottom_actual_bearing_mm2=contact194,source_required_bearing_mm2=427.5,historical_path_transfer_qualified=pathok194,legacy_halfmm_GLOBAL_OPEN=not pathok194,no_printOwnership_fromname=True),rows=rows194,cursor=len(rows194),total=len(tasks194),unreceived_keys=[[routes193[i]['wire'],n] for _,i,n,a,b,lo in tasks194[len(rows194):]],fullbounds_separated=covers194,first_falsifier=first194,all5continuous_actual_own_voidproof_already10of10=True,whole_SOURCE_Li_55_850900_OPEN=True,selected=False,N01_complete=False,actualcut=None,operation_seconds=time.monotonic()-t194,process_cpu_seconds=time.process_time()-c194,pid=os.getpid(),session_id=46493);p194.write_bytes((json.dumps(r194,indent=2)+'\n').encode());print('C1_CURRENT_PATH_EXIT',r194['status'],'path',path194,'bearing',contact194,'foreign',len(rows194),'of',len(tasks194),first194,r194['operation_seconds'],r194['process_cpu_seconds'],hashlib.sha256(p194.read_bytes()).hexdigest(),flush=True)
