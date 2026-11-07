import json,time,hashlib,os,zipfile
t202=time.monotonic();c202=time.process_time()
# SAME intended removableCASEcapture lacked two actualconnections. Repairrepresentation
# of that function with ONE usefulportedweb; no case/wire/stock/rootpose change.
webspec202=[[57.75,-32.5,48.5],[61.0,0,52.05]]
web202=box153(webspec202).cut(channels181).cut(void193)
up202=up201.fuse(web202);assert up202.isValid()
newup202=up202.cut(up193);cover202=[]
for n,s in {**uppermembers201,'ActualPortedCaseCaptureWeb':web202}.items():
    m=s.cut(up202);cover202.append(dict(member=n,missing_valid=m.isValid(),missing_mm3=m.Volume if m.isValid() else None))
join202=[]
for n,s in uppermembers201.items():
    co=s.common(web202);join202.append(dict(member=n,common_valid=co.isValid(),positive_common_mm3=co.Volume if co.isValid() else None))
first202=None
if len(up202.Solids)!=1 or any(not q['missing_valid'] or q['missing_mm3']>1e-7 for q in cover202) or any(not q['common_valid'] or q['positive_common_mm3']<=1e-7 for q in join202):first202=dict(stage='SAME_INTENDED_UPPER_CASE_CAPTURE_CONNECTION_GUARD',upper_solids=len(up202.Solids),rows=join202)
nom202=[]
if first202 is None:
    for n,s in [('newpermanent',newdelta201),('newupper',newup202)]:
        for label,a in [('all5held9',Part.makeCompound(nom181)),('all5unchangedcontinuousexit',Part.makeCompound(nominal193)),('actualcase',case201)]:
            co=s.common(a);row=dict(new_part=n,target=label,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None);nom202.append(row)
            if not co.isValid() or co.Volume>1e-7:first202=dict(stage='NEW_MATERIAL_SOURCE_OR_CASE_NONPENETRATION',row=row);break
        if first202:break
stock202=[]
if first202 is None:
    for n,s in [('newpermanent',newdelta201),('newupper',newup202)]:
        for kn,b in [('whole145loop',band181),('whole145head',head181),('whole145neck',neck181),('whole145uncuttailcapacity',tailfield181)]:
            co=s.common(b);row=dict(new_part=n,stock=kn,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None);stock202.append(row)
            if not co.isValid() or co.Volume>1e-7:first202=dict(stage='NEW_CASE_CAPTURE_COMPLETE_STOCK_INTERFACE',row=row);break
        if first202:break
newtasks202=[];sepbounds202=0;newforeign202=[]
for kn,a in [('NEW_PRIMARY_DELTA',newdelta201),('NEW_UPPER_DELTA',newup202)]:
    for n,b in neigh199.items():
        if n=='Station:D_FL:case':continue
        lo=bbox_lower_bound(a.BoundBox,bounds126[n] if n in bounds126 else b.BoundBox);req=0 if n in ['Ref_Material_P0_SideRight22_0_0','CurrentFoundation:FoundationRail:-1'] else 1.25
        if lo>=req+1e-7:sepbounds202+=1;continue
        priority=0 if ('Housing' in n or n.startswith('Ref_Material_P0_') or n.endswith(':case') or n.startswith('Battery')) else 1
        newtasks202.append((priority,kn,n,a,b,lo,req))
newtasks202.sort(key=lambda q:(q[0],q[1],q[2]));wita202=None;witb202=None
if first202 is None:
    for _,kn,n,a,b,lo,req in newtasks202:
        ga,ww,_=a.distToShape(b);row=dict(new_part=kn,actor=n,actual_gap_mm=ga,required_mm=req,witnesses=[[list(x),list(y)] for x,y in ww[:1]],source_valid=b.isValid())
        if n=='CurrentFoundation:FoundationRail:-1':
            co=a.common(b);ex=co.cut(kit199['Neck']);row.update(actual_function='Onlydesignednewneckloadroot',common_valid=co.isValid(),common_mm3=co.Volume,new_neck_contact_outside_mm3=ex.Volume);fail=not co.isValid() or not ex.isValid() or ex.Volume>1e-7
        else:
            if ga<1e-7:
                co=a.common(b);row.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
            fail=not row['source_valid'] or ga<req-1e-7 or (req==0 and ga<1e-7 and (not row.get('common_valid') or row.get('common_mm3',0)>1e-7))
        row['status']='NEW_CASEBACK_CARRIER_CURRENT_INTERFACE_HOLD' if fail else 'NEW_CASEBACK_CARRIER_CLEAR_OR_EXACT_NECKROOT';newforeign202.append(row)
        if fail:first202=dict(stage='NEW_CASEBACK_CARRIER_CURRENT_NEIGHBOR',row=row);wita202=a;witb202=b;break
        if time.monotonic()-t202>12:break
ar202=OUT/'day07-five-D-caseback-connected-capture-actual-gate.breps.zip';assert not ar202.exists();ge202=[]
exp202={'NEW_WHOLE_PERMANENT':base201,'NEW_CONNECTED_REMOVABLE_CAPTURE':up202,'USEFUL_PORTED_CAPTURE_WEB':web202,'NEW_PRIMARY_DELTA':newdelta201,'NEW_UPPER_DELTA':newup202}
if witb202 is not None:exp202['FIRST_ACTUAL_CURRENT_NEIGHBOR']=witb202
with zipfile.ZipFile(ar202,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(exp202.items()):
        raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge202.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge202),indent=2))
p202=OUT/'day07-five-D-caseback-connected-capture-current-gate.json';assert not p202.exists()
r202=dict(id=p202.stem,status='WHOLE_CASEBACK_CARRIER_FIRST_INTERFACE_HOLD' if first202 else 'CASEBACK_CARRIER_STATIC_CURSOR_RECEIVED_OR_PENDING',representation_repair_only=dict(raw=p201.name,raw_sha256=hashlib.sha256(p201.read_bytes()).hexdigest(),old_upper_solids=3,actual_disconnected_stop_gaps_mm=[.6388794991811121,.7],repair='ONEportedcasecaptureweb connectedtosameactualpressureupper, notnewcase/wire/root/stockpose',web_bounds_mm=webspec202,new_upper_solids=len(up202.Solids),no_design_counter_reset=True),upper_all4_member_coverage=cover202,upper_actual_useful_positive_connections=join202,old_primary_11_members_and9_joins_received_unchanged=True,case_and_source_nominal_newmaterial_nonpenetration=nom202,whole_stock_newmaterial_nonpenetration=stock202,foreign_rows=newforeign202,foreign_cursor=len(newforeign202),foreign_total=len(newtasks202),foreign_unreceived=[[kn,n] for _,kn,n,a,b,lo,req in newtasks202[len(newforeign202):]],fullbounds_separated=sepbounds202,first_falsifier=first202,new_material_motion_outline_and_initial_lay_NOT_qualified=True,currentbase_unchanged=True,selected=False,N01_complete=False,actualcut=None,archive=ar202.name,archive_sha256=hashlib.sha256(ar202.read_bytes()).hexdigest(),geometry=ge202,operation_seconds=time.monotonic()-t202,process_cpu_seconds=time.process_time()-c202,pid=os.getpid(),session_id=46493)
p202.write_bytes((json.dumps(r202,indent=2)+'\n').encode());print('CONNECTED_CASE_CAPTURE',r202['status'],'upper',len(up202.Solids),'joins',join202,'nom',len(nom202),'stock',len(stock202),'foreign',len(newforeign202),'of',len(newtasks202),'first',first202,'wall',r202['operation_seconds'],'CPU',r202['process_cpu_seconds'],hashlib.sha256(p202.read_bytes()).hexdigest(),flush=True)
