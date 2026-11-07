import json,time,hashlib,zipfile,os
t173=time.monotonic();c173=time.process_time()
az173=OUT/'day07-SOURCE-lateral-mouth-C1-current-portal-first-gate.breps.zip'
with zipfile.ZipFile(az173) as z:
    raw173=z.read('0.brep')
assert hashlib.sha256(raw173).hexdigest()=='075fe6b0a24337a6021604dedd81c495ef9d3c31d1d1e4fb7327a9bf22b30426'
f173=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat78-pinned-Dportal.brep');f173.write_bytes(raw173)
portal173=Part.Shape();portal173.read(str(f173));assert portal173.isValid()
parts173=[('NEW_PRIMARY_POSITIVE_MATERIAL_DELTA',delta170),('NEW_REMOVABLE_UPPER',up170),('NEW_PRESSURE_FULL_LOOP',pb170),('NEW_PRESSURE_FULL_HEAD',head170)]+tail171
rows173=[];first173=None
p173=OUT/'day07-SOURCE-G4-C1-shared-leading-new-pairs.json';assert not p173.exists()
def save173():
    global r173
    r173=dict(id=p173.stem,status='FIRST_NEW_G4_ALLOCATED_PORTAL_HOLD' if first173 else ('ALL_NEW_G4_SHARED_LEADING_PAIRS_CLOSED_SCOPED' if len(rows173)==len(parts173) else 'PENDING_NEW_PAIRS'),source_portal_archive=az173.name,source_portal_archive_sha256=hashlib.sha256(az173.read_bytes()).hexdigest(),source_portal_entry='0.brep',source_portal_sha256=hashlib.sha256(raw173).hexdigest(),source_portal_valid=True,new_G4_static_receipt='day07-SOURCE-G4-common-closure-C1-bounded-disposition.json',source_G4_receipt_sha256=hashlib.sha256((OUT/'day07-SOURCE-G4-common-closure-C1-bounded-disposition.json').read_bytes()).hexdigest(),operand_order=[n for n,s in parts173],rows=rows173,cursor=len(rows173),unreceived=[n for n,s in parts173[len(rows173):]],first_falsifier=first173,required_foreign_mm=1.25,scope='ONLY new G4 material/upper/pressure stock/full tails versus FROZEN complete allocated D portal. No old Gcomb pair replay; no portal or print change; allocated HOLD is NOT delivered wire contact.',operation_seconds=time.monotonic()-t173,process_cpu_seconds=time.process_time()-c173,selected=False,N01_complete=False,current_parent_unchanged=True,pid=os.getpid(),session_id=46493)
    tmp=p173.with_suffix('.tmp');tmp.write_bytes((json.dumps(r173,indent=2)+'\n').encode());os.replace(tmp,p173)
save173()
for n,s in parts173:
    row=dict(key='FROZEN_W005_PORTAL075fe6b0::'+n,actor=n,operand_valid=s.isValid(),bounds=saved_bounds(s))
    assert row['operand_valid']
    lower=bbox_lower_bound(portal173.BoundBox,s.BoundBox);row['bbox_lower_mm']=lower
    if lower>=1.25-1e-7:row.update(status='FULL_BOUNDS_SEPARATED125',lower_mm=lower)
    else:
        gap,ww,_=portal173.distToShape(s);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='VALID_NEW_PAIR_SEPARATED125' if gap>=1.25-1e-7 else 'ALLOCATED_D_PORTAL_VS_NEW_G4_HOLD_NOT_DELIVERED_WIRECONTACT')
        if gap<1e-7:
            cc=portal173.common(s);row.update(common_valid=cc.isValid(),allocated_common_mm3=cc.Volume if cc.isValid() else None)
    rows173.append(row)
    if row['status'].endswith('WIRECONTACT'):first173=row
    save173()
    if first173:break
print('G4_NEW_SHARED_LEADING',r173['status'],len(rows173),'of',len(parts173),first173,r173['operation_seconds'],r173['process_cpu_seconds'],hashlib.sha256(p173.read_bytes()).hexdigest(),flush=True)
