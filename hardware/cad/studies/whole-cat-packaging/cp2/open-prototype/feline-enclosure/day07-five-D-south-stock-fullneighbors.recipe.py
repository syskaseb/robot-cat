import json,time,hashlib,os
t182=time.monotonic();c182=time.process_time();assert first181 is None
retire182=['CurrentDFL:permanent','CurrentDFL:removable','CurrentDFL:DFL:cap','CurrentDFL:DFL:band','CurrentDFL:DFL:head','CurrentFoundation:BankPier:3','CurrentFoundation:BankLedge:3'];ctx182={n:s for n,s in ctx177.items() if n not in retire182};parts182=[('NEW_D5_PERMANENT',base181),('NEW_D5_UPPER',up181),('NEW_D5_FULL_LOOP',band181),('NEW_D5_FULL_HEAD',head181),('NEW_D5_FULL_TAIL_NECK_CAPACITY',neck181),('NEW_D5_REMAINING_UNCUT_TAIL_CAPACITY',tailfield181)]
own182=[];first182=None
for n,s in [('full_band_primary',base181),('full_band_upper',up181)]:
    gap,ww,_=band181.distToShape(s);cc=band181.common(s);own182.append(dict(interface=n,required_mm=.2,gap_mm=gap,common_valid=cc.isValid(),common_mm3=cc.Volume))
    if gap<.2-1e-7 or cc.Volume>1e-7:first182=dict(stage='TRUE_FULL_STOCK_SEAT',row=own182[-1]);break
gap182=up181.distToShape(base181)[0];cc182=up181.common(base181);own182.append(dict(interface='upper_lower_REMOVABLE_closure',required_mm=0,gap_mm=gap182,common_valid=cc182.isValid(),common_mm3=cc182.Volume))
if cc182.Volume>1e-7:first182=dict(stage='DETACHABLE_MATERIAL_INTERPENETRATION',row=own182[-1])
tasks182=[];fullbounds182={n:saved_bounds(s) for n,s in parts182};neutralcovers182=0
for n,a in parts182:
    ab=a.BoundBox
    for m,b in ctx182.items():
        bb=bounds126[m] if m in bounds126 else b.BoundBox;lo=bbox_lower_bound(ab,bb)
        req=.2 if m=='Station:D_FL:case' and n in ['NEW_D5_PERMANENT','NEW_D5_UPPER'] else 0 if n=='NEW_D5_PERMANENT' and (m in ['CurrentFoundation:ClampSeat:3','CurrentFoundation:ClampNeck:3'] or 'RailClamp3' in m or 'TopClampPad3' in m) else 1.25
        if lo>=req-1e-7 and lo>0:neutralcovers182+=1;continue
        role='same_actual_D5_case_grip_fit' if req==.2 else 'same_actual_clamp3_root_hardware_function' if req==0 else 'new_full_foreign_interface'
        tasks182.append((0 if req<1.25 else 1 if 'Housing' in m or m.endswith(':case') or m.startswith('Ref_Material_P0_') else 2,n,m,a,b,lo,req,role))
tasks182.sort(key=lambda q:(q[0],q[1],q[2]));rows182=[];cursor182=0
p182=OUT/'day07-five-D-south-launch-whole-stock-and-neighbors.json';assert not p182.exists()
def save182():
    global r182
    r182=dict(id=p182.stem,status='FIVE_D_WHOLE_STOCK_OR_FOREIGN_FIRST_HOLD' if first182 else ('FIVE_D_FULL_STOCK_AND_STATIC_NEIGHBORS_CLOSED_SCOPED' if cursor182==len(tasks182) else 'FIVE_D_WHOLE_STOCK_NEIGHBORS_PENDING'),functional_first_gate=p181.name,functional_first_gate_sha256=hashlib.sha256(p181.read_bytes()).hexdigest(),own_fullstock_and_removable_rows=own182,rows=rows182,cursor=cursor182,total=len(tasks182),unreceived_keys=[[n,m] for _,n,m,a,b,lo,req,role in tasks182[cursor182:]],first_falsifier=first182,exact_retirements_for_PROPOSED_context=retire182,full_bound_separated_pairs=neutralcovers182,new_fixed_bounds=fullbounds182,case_and_all5_actualports_kept=True,selected=False,N01_complete=False,full_stock_unit_mm=145,loop_Vdivwt_mm=loop181,remaining_uncut_tail_mm=tail181,plastic_R3_NECK_within_tail_once_mm=3*math.pi/2,remaining_straight_tail_capacity_mm=straighttail181,tail_head_pull25_WITHINremaining_ONCE=True,inventory=None,additional_qty=0,actualA_U_fit_slack=None,actualcut=None,operation_seconds=time.monotonic()-t182,process_cpu_seconds=time.process_time()-c182,pid=os.getpid(),session_id=46493)
    q=p182.with_suffix('.tmp');q.write_bytes((json.dumps(r182,indent=2)+'\n').encode());os.replace(q,p182)
save182()
if not first182:
    for _,n,m,a,b,lo,req,role in tasks182:
        row=dict(key=[n,m],source_role=role,required_mm=req,bbox_lower_mm=lo,source_valid=b.isValid())
        if not row['source_valid']:row['status']='SOURCE_INTEGRITY_OPEN_NOT_CONTACT'
        else:
            gap,ww,_=a.distToShape(b);row.update(gap_mm=gap,witnesses=[[list(x),list(y)] for x,y in ww[:1]],status='NEW_INTERFACE_SCOPED_SEPARATED' if gap>=req-1e-7 else 'NEW_D5_ALLOCATION_CLEARANCE_HOLD_NOT_DELIVERED_CONTACT')
            if gap<1e-7:
                co=a.common(b);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
                if not co.isValid() or co.Volume>1e-7 and req==0:row['status']='OWN_ACTUAL_MATERIAL_OR_INPUT_HOLD_NOT_WAIVED'
        rows182.append(row);cursor182+=1
        if row['status']!='NEW_INTERFACE_SCOPED_SEPARATED':first182=dict(stage='WHOLE_STOCK_OR_CURRENT_FOREIGN',row=row)
        save182()
        if first182 or time.monotonic()-t182>12:break
print('FIVE_D_STOCK_AND_CONTEXT',r182['status'],cursor182,'of',len(tasks182),first182,r182['operation_seconds'],r182['process_cpu_seconds'],hashlib.sha256(p182.read_bytes()).hexdigest(),flush=True)
