import json,time,hashlib,os,zipfile
t204=time.monotonic();c204=time.process_time();assert first203['row']['actor']=='SharedRetention:lower_common_flange_base'
src204=ROOT/'tools/cad/prototype_shared_retention_20261025.py'
shared204={n:s for n,s in neigh199.items() if n=='SharedRetention:lower_common_flange_base' or n.endswith(':shared_near_root')}
assert set(shared204)=={'SharedRetention:lower_common_flange_base','Station:FR_G:shared_near_root','Station:P_AUX:shared_near_root'}
co204=newdelta201.common(shared204['SharedRetention:lower_common_flange_base']);outside204=co204.cut(kit199['Neck']);assert outside204.Volume<1e-7
frame204=wholeframe203.multiFuse(list(shared204.values()));assert frame204.isValid()
coverage204=[]
for n,s in {'PreviouscompleteFrameAndCaseCarrier':wholeframe203,**shared204}.items():
    m=s.cut(frame204);coverage204.append(dict(member=n,missing_valid=m.isValid(),missing_mm3=m.Volume if m.isValid() else None))
first204=None
if len(frame204.Solids)!=1 or any(not q['missing_valid'] or q['missing_mm3']>1e-7 for q in coverage204):first204=dict(stage='ACTUAL_CURRENT_SHARED_PRINT_FUNCTION_PARENT',solids=len(frame204.Solids),coverage=coverage204)
rows204=[];remaining204=remaining203[len(rows203):];wita204=None;witb204=None
for _,kn,n,a,b,lo,req in (remaining204 if first204 is None else []):
    ga,ww,_=a.distToShape(b);row=dict(new_part=kn,actor=n,actual_gap_mm=ga,required_mm=req,source_valid=b.isValid(),witnesses=[[list(x),list(y)] for x,y in ww[:1]])
    if n in shared204 or n in ['CurrentFoundation:FoundationRail:-1','CurrentFoundation:FoundationFlange:-1']:
        co=a.common(b);ex=co.cut(kit199['Neck']);row.update(function='Actualcommonprintparent+LIMITEDnewNeckcontactonly',common_valid=co.isValid(),common_mm3=co.Volume,outside_designed_neck_mm3=ex.Volume);fail=not co.isValid() or not ex.isValid() or ex.Volume>1e-7
    else:
        if ga<1e-7:
            co=a.common(b);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
        fail=not row['source_valid'] or ga<req-1e-7 or (req==0 and ga<1e-7 and (not row.get('common_valid') or row.get('common_mm3',0)>1e-7))
    row['status']='NEW_CASEBACK_CURRENT_INTERFACE_HOLD' if fail else 'NEW_CASEBACK_CLEAR_OR_EXACT_PRINTEDROOT';rows204.append(row)
    if fail:first204=dict(stage='NEW_CASEBACK_MISSING_CURRENT_INTERFACE',row=row);wita204=a;witb204=b;break
ar204=OUT/'day07-five-D-caseback-current-complete-print-parent.breps.zip';assert not ar204.exists();ge204=[]
exps204={'NEW_ONE_COMPLETE_CURRENT_FRAME_AND_D_CARRIER':frame204,'NEW_ONE_COMPLETE_REMOVABLE_CASE_CAPTURE':up202}
if witb204 is not None:exps204['FIRST_ACTUAL_CURRENT_NEIGHBOR']=witb204
with zipfile.ZipFile(ar204,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(exps204.items()):
        raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge204.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge204),indent=2))
p204=OUT/'day07-five-D-caseback-shared-root-function-and-last-pairs.json';assert not p204.exists()
r204=dict(id=p204.stem,status='CASEBACK_WHOLE_FUNCTIONAL_PRINT_STATIC_FIRST_HOLD' if first204 else 'CASEBACK_WHOLE_FUNCTIONAL_PRINT_STATIC_SCOPED_RECEIVED',source_pin=dict(path=str(src204),sha256=hashlib.sha256(src204.read_bytes()).hexdigest(),lines='71..85 explicitbase_parent=currentFoundationFlange/whole=parent.fuse(base).fuse(actualroots), all13jacketsunchanged'),raw_required125_root_row_preserved=p203.name,actual_limited_newNeck_sharedbase_common_mm3=co204.Volume,actual_common_outside_newNeck_mm3=outside204.Volume,ownroot_classification='SourceexplicitSAMEcommonpermanentprintloadpath + actualcurrentonlynewNeckoverlap and ALLcurrentmaterialretained inONEconnectedparent. NotnameOWN, no wiremetalwaiver; no absenthistoricalDFRroot recreated.',actual_current_shared_members=coverage204,whole_connected_parent_solids=len(frame204.Solids),previous10newmaterialpairs_not_replayed=True,new_rows=rows204,new_cursor=len(rows204),new_total=len(remaining204),new_unreceived=[[kn,n] for _,kn,n,a,b,lo,req in remaining204[len(rows204):]],combined_new_material_cursor=8+len(rows203)+len(rows204),combined_new_material_total=len(newtasks202),first_falsifier=first204,wholeparent_PROPOSED_effectivity=dict(replace_current_frames=['CurrentFoundation:FoundationRail:-1','CurrentFoundation:FoundationFlange:-1',*shared204],replace_proposed_Dpermanent=True,replace_proposed_Dupper=True,old_clamp3_completepose_retired_onlywhenwholeaccepted=True,no_duplicate_old_parents=True,currentbase_unchanged=True),new_motion_and_outline_initial_lay_OPEN=True,selected=False,N01_complete=False,actualcut=None,archive=ar204.name,archive_sha256=hashlib.sha256(ar204.read_bytes()).hexdigest(),geometry=ge204,operation_seconds=time.monotonic()-t204,process_cpu_seconds=time.process_time()-c204,pid=os.getpid(),session_id=46493)
p204.write_bytes((json.dumps(r204,indent=2)+'\n').encode());print('CASEBACK_SHAREDROOT_LAST_STATIC',r204['status'],'solids',len(frame204.Solids),'missingzero',all(q['missing_mm3']<1e-7 for q in coverage204),'pairs',r204['combined_new_material_cursor'],'of',r204['combined_new_material_total'],'first',first204,'wall',r204['operation_seconds'],'CPU',r204['process_cpu_seconds'],hashlib.sha256(p204.read_bytes()).hexdigest(),flush=True)
