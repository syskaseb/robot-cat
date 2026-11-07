import json,time,hashlib,os,zipfile
t203=time.monotonic();c203=time.process_time();assert first202['row']['actor']=='CurrentFoundation:FoundationFlange:-1'
flange203=Current35['CurrentFoundation:FoundationFlange:-1'];rootco203=newdelta201.common(flange203);ex203=rootco203.cut(kit199['Neck'])
assert rootco203.isValid() and ex203.isValid() and ex203.Volume<1e-7
# ActualdesignedNECKonly inactualcurrentdownflange; no purchased/wireOWNwaiver.
# Sourcefeline_shared_frame.py43..75 creates sideRail/downFlange/neck ascommon
# printedframefunctions. Complete retainedparents stay MATERIAL, not deletedparts.
wholeframe203=base201.multiFuse([rootpart199,flange203]);assert wholeframe203.isValid()
member203=[]
for n,s in [('Newcasecarriercomplete',base201),('ACTUALcurrentcommonRail',rootpart199),('ACTUALcurrentDownFlange',flange203)]:
    m=s.cut(wholeframe203);member203.append(dict(member=n,missing_valid=m.isValid(),missing_mm3=m.Volume if m.isValid() else None,bounds_mm=saved_bounds(s)))
rootrule203=dict(raw_receipt=p202.name,raw_sha256=hashlib.sha256(p202.read_bytes()).hexdigest(),raw_foreign_required125_preserved=True,actual_newNeck_to_actualDownFlange_common_mm3=rootco203.Volume,common_outside_actualNewNeck_mm3=ex203.Volume,criterion='Actualsource-commonframe positivefunctionaljoint LIMITED to newlydesignedNeck; wholecasecarrier+ACTUALretainedRail+Flange nowexplicitONEprintedparent withall3membercoverage andoneconnectedsolid. NotnameOWN/no generalforeignmetalwireexception.',whole_frame_parent_solids=len(wholeframe203.Solids),whole_frame_parent_bounds_mm=saved_bounds(wholeframe203),all3complete_parent_coverage=member203,print_prototype_256cube=all(b-a<=256+1e-7 for a,b in zip(saved_bounds(wholeframe203)[0],saved_bounds(wholeframe203)[1])),unchanged_named_max200_carriers_not_redefined=True,no_virtual_detach_or_delete_retained_frame=True)
first203=None
if len(wholeframe203.Solids)!=1 or any(not q['missing_valid'] or q['missing_mm3']>1e-7 for q in member203) or not rootrule203['print_prototype_256cube']:first203=dict(stage='EXPLICIT_ACTUAL_WHOLE_PRINT_FRAME_ROOT_GUARD',row=rootrule203)
rows203=[];wita203=None;witb203=None
# OnlypreviouslyUNRECEIVEDnewmaterialpairs afterfunction-disposedrow8.
remaining203=newtasks202[len(newforeign202):]
if first203 is None:
    for _,kn,n,a,b,lo,req in remaining203:
        ga,ww,_=a.distToShape(b);row=dict(new_part=kn,actor=n,actual_gap_mm=ga,required_mm=req,source_valid=b.isValid(),witnesses=[[list(x),list(y)] for x,y in ww[:1]])
        if n in ['CurrentFoundation:FoundationRail:-1','CurrentFoundation:FoundationFlange:-1']:
            co=a.common(b);ex=co.cut(kit199['Neck']);row.update(function='LIMITEDactualNECKjoinedcompletePRINTparent',common_valid=co.isValid(),common_mm3=co.Volume,extra_outside_designed_neck_mm3=ex.Volume);fail=not co.isValid() or not ex.isValid() or ex.Volume>1e-7
        else:
            if ga<1e-7:
                co=a.common(b);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
            fail=not row['source_valid'] or ga<req-1e-7 or (req==0 and ga<1e-7 and (not row.get('common_valid') or row.get('common_mm3',0)>1e-7))
        row['status']='NEW_CARRIER_ACTUAL_CURRENT_INTERFACE_HOLD' if fail else 'NEW_CARRIER_CLEAR_OR_EXACT_DESIGNED_ROOT';rows203.append(row)
        if fail:first203=dict(stage='NEW_CARRIER_MISSING_CURRENT_INTERFACE',row=row);wita203=a;witb203=b;break
        if time.monotonic()-t203>10:break
ar203=OUT/'day07-five-D-caseback-explicit-whole-frame-and-last-static.breps.zip';assert not ar203.exists();ge203=[]
exp203={'NEW_ONE_COMPLETE_FRAME_AND_CASE_CARRIER':wholeframe203,'NEW_CONNECTED_REMOVABLE_UPPER':up202,'ACTUAL_NEW_NECK_TO_DOWNFLANGE_JOIN':rootco203}
if witb203 is not None:exp203['FIRST_ACTUAL_MISSING_INTERFACE_WITNESS']=witb203
with zipfile.ZipFile(ar203,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(exp203.items()):
        raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge203.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge203),indent=2))
p203=OUT/'day07-five-D-caseback-explicit-frame-root-and-missing-static.json';assert not p203.exists()
r203=dict(id=p203.stem,status='CASEBACK_WHOLE_FRAME_FIRST_NEW_INTERFACE_HOLD' if first203 else 'CASEBACK_EXPLICIT_PRINT_ROOT_AND_NEW_STATIC_CURSOR_RECEIVED',root_function_disposition=rootrule203,prior8_newmaterial_pairs_not_replayed=True,new_rows=rows203,new_missing_cursor=len(rows203),new_missing_total=len(remaining203),new_missing_unreceived=[[kn,n] for _,kn,n,a,b,lo,req in remaining203[len(rows203):]],first_falsifier=first203,PROPOSED_effectivity=dict(replace_whole_actors=['CurrentFoundation:FoundationRail:-1','CurrentFoundation:FoundationFlange:-1','CurrentDFL:permanent'],retire_old_clamp3_pose=list(old199),retain_all_other_source_function_material=True,new_whole_permanent_archive_entry='0.brep',removable_upper_entry='1.brep',no_duplicate_old_frame_parents=True,currentbase_not_changed=True),new_motion_and_bodyoutline_and_initial_case_lay_OPEN=True,selected=False,N01_complete=False,actualcut=None,archive=ar203.name,archive_sha256=hashlib.sha256(ar203.read_bytes()).hexdigest(),geometry=ge203,operation_seconds=time.monotonic()-t203,process_cpu_seconds=time.process_time()-c203,pid=os.getpid(),session_id=46493)
p203.write_bytes((json.dumps(r203,indent=2)+'\n').encode());print('CASEBACK_EXACT_FRAME_LAST_STATIC',r203['status'],'root',rootco203.Volume,'outsideNeck',ex203.Volume,'solids',len(wholeframe203.Solids),'newrows',len(rows203),'of',len(remaining203),'first',first203,'wall',r203['operation_seconds'],'CPU',r203['process_cpu_seconds'],hashlib.sha256(p203.read_bytes()).hexdigest(),flush=True)
