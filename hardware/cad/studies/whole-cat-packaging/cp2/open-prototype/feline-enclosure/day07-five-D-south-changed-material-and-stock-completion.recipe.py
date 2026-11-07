import json,time,hashlib,os
t185=time.monotonic();c185=time.process_time();assert gap184>=1.25 and cursor183==5
rows185=[];cursor185=cursor183;first185=None;newcovers185=0
for _,n,m,a,b,lo,req,role in tasks182[cursor185:]:
    changed=(n=='NEW_D5_PERMANENT' and req==1.25);s=newdelta184 if changed else a;lo=bbox_lower_bound(s.BoundBox,bounds126[m] if m in bounds126 else b.BoundBox);row=dict(key=[n,m],required_mm=req,scope='ONLYpositiveaddedmaterial_foreign_delta' if changed else 'whole_new_stock_or_upper',bbox_lower_mm=lo)
    if lo>=req-1e-7 and lo>0:row.update(status='NEW_INTERFACE_FULL_COVER_SEPARATED',certified_lower_mm=lo);newcovers185+=1
    else:
        row['source_valid']=b.isValid()
        if not row['source_valid']:row['status']='SOURCE_INPUT_OPEN_NOT_CONTACT'
        else:
            ga,ww,_=s.distToShape(b);row.update(gap_mm=ga,witnesses=[[list(x),list(y)] for x,y in ww[:1]],status='NEW_INTERFACE_SEPARATED' if ga>=req-1e-7 else 'NEW_D5_ALLOCATED_FOREIGN_HOLD_NOT_DELIVERED_CONTACT')
            if ga<1e-7:
                co=s.common(b);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
                if req==0 and (not co.isValid() or co.Volume>1e-7):row['status']='ACTUAL_HARDWARE_INTERPENETRATION_HOLD'
    rows185.append(row);cursor185+=1
    if row['status'] not in ['NEW_INTERFACE_FULL_COVER_SEPARATED','NEW_INTERFACE_SEPARATED']:first185=row;break
    if time.monotonic()-t185>12:break
own185=[]
if first185 is None and cursor185==len(tasks182):
    for n,s in [('full_head',head181),('full_tail_neck',neck181),('full_tail_parking',tailfield181)]:
        for m,b in [('new_primary',base181),('new_upper',up181)]:
            ga,ww,_=s.distToShape(b);row=dict(stock=n,print=m,required_mm=1.25,gap_mm=ga,status='FULLSTOCK_SEPARATED125' if ga>=1.25-1e-7 else 'ALLOCATED_FULLSTOCK_TO_OWNPRINT_HOLD_NOT_CONTACT');own185.append(row)
            if ga<1.25-1e-7:first185=row;break
        if first185:break
p185=OUT/'day07-five-D-south-positive-material-and-whole-stock-completion.json';assert not p185.exists();r185=dict(id=p185.stem,status='NEW_FIVE_D_CHANGED_MATERIAL_OR_FULLSTOCK_FIRST_HOLD' if first185 else ('NEW_FIVE_D_STATIC_DELTA_AND_FULLSTOCK_CLOSED_SCOPED_LEGACY_PAD_OPEN' if cursor185==len(tasks182) else 'NEW_FIVE_D_STATIC_CURSOR_PENDING'),source_first5=p183.name,source_first5_sha256=hashlib.sha256(p183.read_bytes()).hexdigest(),legacy_pad_causality=p184.name,legacy_pad_causality_sha256=hashlib.sha256(p184.read_bytes()).hexdigest(),new_rows=rows185,cursor=cursor185,total=len(tasks182),unreceived_keys=[[n,m] for _,n,m,a,b,lo,req,role in tasks182[cursor185:]],first_falsifier=first185,full_head_neck_tail_to_own_material=own185,positive_delta_notwhole_inheritedfoot_forforeign_pairs=True,legacy_pad_half_mm_still_GLOBAL_OPEN_no_waiver=True,all_other_previously_boundseparated=neutralcovers182,selected=False,N01_complete=False,fullunit145_loop=loop181,full_remaining_uncut_tail=tail181,all_actualA_U_fit_slack=None,actualcut=None,operation_seconds=time.monotonic()-t185,process_cpu_seconds=time.process_time()-c185,pid=os.getpid(),session_id=46493);p185.write_bytes((json.dumps(r185,indent=2)+'\n').encode());print('FIVE_D_COMPLETION',r185['status'],cursor185,'of',len(tasks182),first185,r185['operation_seconds'],r185['process_cpu_seconds'],hashlib.sha256(p185.read_bytes()).hexdigest(),flush=True)
