import time,json,hashlib,zipfile,os
t224=time.monotonic();c224=time.process_time();first224=None;rows224=[];covers224={};guards224=[]
parts224={k:Current35['Ref_Material_F_R4_CP2_'+k+'_0_0'] for k in ['Housing','ATO','IN','OUT']}
fixed224={'D5_CURRENT_FIXED_LOWER':lower221,'D5_CURRENT_WIDE_KEEPER_UPPER':upper221,'D5_SAME_SELECTED_CASE':case216,**{n:s for n,s in kit199.items() if n.startswith('Hardware:')},'D5_WHOLE145_LOOP':band181,'D5_FULL_HEAD':head181,'D5_FULL_TAIL_NECK':neck181,'D5_FULL66p001640_TAIL_CAPACITY':tailfield181}
for n,s in parts224.items():
    bb=s.BoundBox;sourcebox=Part.makeBox(bb.XLength+2e-6,bb.YLength+2e-6,bb.ZLength+2e-6,A.Vector(bb.XMin-1e-6,bb.YMin-1e-6,bb.ZMin-1e-6));mis=s.cut(sourcebox);assert mis.isValid() and mis.Volume<1e-7
    cover=Part.makeBox(bb.XLength+2e-6,bb.YLength+2e-6,bb.ZLength+12+2e-6,A.Vector(bb.XMin-1e-6,bb.YMin-1e-6,bb.ZMin-1e-6));covers224[n]=cover;guards224.append(dict(part=n,actual_current_name='Ref_Material_F_R4_CP2_'+n+'_0_0',current_valid=s.isValid(),unchanged_current_source=True,source_outside_used_bound_valid=mis.isValid(),source_outside_used_bound_mm3=mis.Volume,actual_source_bounds_mm=saved_bounds(s),continuous_translation_mm=[0,12],cover_bounds_mm=saved_bounds(cover)))
    for fn,f in fixed224.items():
        lo=bbox_lower_bound(cover.BoundBox,f.BoundBox)
        if lo>=1.25-1e-7:rows224.append(dict(bank_part=n,fixture=fn,required_mm=1.25,lower_mm=lo,status='CONTINUOUS_CONSERVATIVE_SEPARATED'));continue
        ga=cover.distToShape(f)[0];co=cover.common(f);row=dict(bank_part=n,fixture=fn,required_mm=1.25,valid_common=co.isValid(),cover_common_mm3=co.Volume,actual_cover_gap_mm=ga,status='CONTINUOUS_CONSERVATIVE_SEPARATED' if ga>=1.25-1e-7 else 'ALLOCATED_SWEEP_HOLD_NOT_ACTUAL_CONTACT');rows224.append(row)
        if not co.isValid() or ga<1.25-1e-7:first224=dict(stage='WHOLE_FOUR_PART_BANK_RECIPROCAL_NECESSARY_GATE',row=row,not_all_routes_impossible=True);break
    if first224:break
separate224=None
if first224 is None:
    # Actual distinct printed halves must not penetrate in the assembled state before any new lift/closure proof.
    co=lower221.common(upper221);separate224=dict(actual_same_operating_parts_common_valid=co.isValid(),common_mm3=co.Volume,lower_solids=len(lower221.Solids),upper_solids=len(upper221.Solids),not_from_union_identity_alone=True)
    if not co.isValid() or co.Volume>1e-7:first224=dict(stage='DISTINCT_NEW_LOWER_UPPER_ASSEMBLED_NONPENETRATION_REQUIRED_BEFORE_CLOSURE',row=separate224,not_wire_or_bought_contact=True)
ar224=OUT/'day07-whole-FR4-late-bank-reciprocal-and-D5-separate-half-first.breps.zip';assert not ar224.exists();ge224=[]
with zipfile.ZipFile(ar224,'w',zipfile.ZIP_DEFLATED) as z:
    ss=list(parts224.items())+[('FR4_'+n+'_CONTINUOUS_ENTRY12_COVER',s) for n,s in covers224.items()]
    if separate224:ss += [('ACTUAL_NEW_D5_FIXED_LOWER',lower221),('ACTUAL_NEW_D5_KEEPER_UPPER',upper221),('ACTUAL_LOWER_UPPER_COMMON_WITNESS',co)]
    for i,(n,s) in enumerate(ss):
        f=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat90-first-'+str(i)+'.brep');s.exportBrep(str(f));raw=f.read_bytes();en=str(i)+'.brep';z.writestr(en,raw);ge224.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge224),indent=2)+'\n').encode())
p224=OUT/'day07-whole-FR4-late-bank-reciprocal-and-D5-separate-half-first.json';r224=dict(id=p224.stem,status='WHOLE_LATE_BANK_RECIPROCAL_OR_D5_SEPARATE_ASSEMBLY_FIRST_HOLD' if first224 else 'WHOLE_FOUR_BANK_RECIPROCAL_SCOPED_CLEAR_DISTINCT_D5_HALVES_VALID_MORE_ORDER_AND_CLOSURE_OPEN',continuous_bank_part_guards=guards224,rows=rows224,received=len(rows224),total=4*len(fixed224),remaining=4*len(fixed224)-len(rows224),distinct_actual_print_halves=separate224,first_falsifier=first224,actual_bank_case_retaining_and_full_two_stock_bindings_OPEN=True,new_wide_upper_continuous_closure_NOT_claimed=True,no_second_order_family_built=True,source_and_factory_parts_unchanged=True,selected=False,N01_complete=False,archive=ar224.name,archive_sha256=hashlib.sha256(ar224.read_bytes()).hexdigest(),geometry=ge224,operation_seconds=time.monotonic()-t224,process_cpu_seconds=time.process_time()-c224,pid=os.getpid(),session_id=46493);p224.write_bytes((json.dumps(r224,indent=2)+'\n').encode());print('LATEBANK224_FIRST',r224['status'],first224,'bankrows',len(rows224),'of',r224['total'],'separate',separate224,'seconds',r224['operation_seconds'],r224['process_cpu_seconds'],'OWNER90_SAVED_IDLE',os.getpid(),flush=True)
