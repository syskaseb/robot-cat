import json,time,hashlib,os,zipfile
t197=time.monotonic();c197=time.process_time()
pn197=OUT/'day07-Clamp3-opposite-face-whole-stack-proposal.json';pr197=json.loads(pn197.read_bytes())
assert pr197['one_transform']['pivot_mm']==[72,-24.5,38.37]
met197={k:Current35['Station:Anchor:Rear:RailClamp3'+k] for k in ['Screw','Nut','TopWasher','BottomWasher']}
rev197={};quality197=[]
for n,s in met197.items():
    q=s.copy();q.rotate(A.Vector(72,-24.5,38.37),A.Vector(1,0,0),180)
    row=dict(part=n,source_valid=s.isValid(),reversed_valid=q.isValid(),source_volume_mm3=s.Volume,reversed_volume_mm3=q.Volume,volume_delta_mm3=abs(q.Volume-s.Volume),original_bounds_mm=saved_bounds(s),reversed_bounds_mm=saved_bounds(q),transform='properTopLoc rigid180X SAMEaxis actualbearingmidplane38.37, nottransformGeometry')
    assert row['source_valid'] and row['reversed_valid'] and row['volume_delta_mm3']<1e-6,(n,row)
    rev197[n]=q;quality197.append(row)
assert abs(rev197['Screw'].BoundBox.ZMax-47.52)<1e-6
assert abs(rev197['Nut'].BoundBox.ZMin-43.22)<1e-6 and abs(rev197['Nut'].BoundBox.ZMax-45.62)<1e-6
shaft197=[f for f in rev197['Screw'].Faces if type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Radius-1.5)<1e-5][0]
shaftbounds197=saved_bounds(shaft197);nutbounds197=saved_bounds(rev197['Nut'])
eng197=min(shaftbounds197[1][2],nutbounds197[1][2])-max(shaftbounds197[0][2],nutbounds197[0][2])
assert abs(eng197-2.4)<1e-6
rows197=[];first197=None
# FrozenW004 fullcapacity is the namedcausal firstgate, not an oldpair replay.
for n in ['Screw','Nut','TopWasher','BottomWasher']:
    b=rev197[n];ga,ww,_=lastfield194.distToShape(b)
    row=dict(wire='W004',operand='FROZEN_C1_FULL_ALLOCATED_EXIT_r1.95',new_metal='REVERSED_FULL_CLAMP3_'+n,gap_mm=ga,required_foreign_mm=1.25,witnesses=[[list(x),list(y)] for x,y in ww[:1]],status='NEW_REVERSED_FULLMETAL_SEPARATED125' if ga>=1.25-1e-7 else 'NEW_REVERSED_FULLMETAL_ALLOCATED_PROFILE_HOLD_NOT_DELIVERED_CONTACT')
    if ga<1e-7:
        co=lastfield194.common(b);row.update(common_valid=co.isValid(),allocated_common_mm3=co.Volume if co.isValid() else None)
    rows197.append(row)
    if ga<1.25-1e-7:first197=row;break
ar197=OUT/'day07-Clamp3-opposite-face-fullstack-first-gate.breps.zip';assert not ar197.exists();ge197=[]
all197={**{'ORIGINAL_'+n:s for n,s in met197.items()},**{'REVERSED_'+n:s for n,s in rev197.items()},'FROZEN_W004_FULL_CAPACITY':lastfield194,'CURRENT_SOURCE_LOWER_JAW':Current35['Station:Anchor:Rear:LowerClampJaw3'],'CURRENT_SOURCE_TOP_PAD':Current35['Station:Anchor:Rear:TopClampPad3'],'CURRENT_CLAMP_SEAT':Current35['CurrentFoundation:ClampSeat:3']}
with zipfile.ZipFile(ar197,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate(all197.items()):
        data=s.exportBrepToString().encode('utf-8');en=f'{i:02d}.brep';z.writestr(en,data);ge197.append(dict(name=n,entry=en,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),bounds_mm=saved_bounds(s)))
    z.writestr('manifest.json',json.dumps(dict(geometry=ge197,coordinateframe='CURRENT_BAKED_WORLD_NO_XML',selected=False),indent=2))
p197=OUT/'day07-Clamp3-opposite-face-fullstack-first-gate.json';assert not p197.exists()
r197=dict(id=p197.stem,status='WHOLE_REVERSE_FASTENING_HYPOTHESIS_REJECTED_BEFORE_PRINT' if first197 else 'FULLMETAL_FIRSTGATE_PARTIAL_OTHER5FIELDS_ACCESS_LOAD_OPEN',proposal=pn197.name,proposal_sha256=hashlib.sha256(pn197.read_bytes()).hexdigest(),all4_complete_rigid_copies=quality197,measured_same_full_shaft_nut_engagement_mm=eng197,opposite_bearing_planes_unchanged_mm=[33.52,43.22],selected_same_parts_counts=True,archive=ar197.name,archive_sha256=hashlib.sha256(ar197.read_bytes()).hexdigest(),geometry=ge197,rows=rows197,first_falsifier=first197,new_cursor=len(rows197),new_pair_total=20,new_unreceived=20-len(rows197),old12of48_36unreceived_not_resumed=True,C1_mouth_all5sourceports_fixed9_stock_no_changes=True,actual_source_jaw_seat_neck_frame_unchanged=True,no_new_print_or_support=True,no_samefixture_wiremetal_exception=True,driver_below_nut_upper_capture_and_wholecontext='NOT_QUALIFIED after firstmetalstop' if first197 else 'OPEN',selected=False,N01_complete=False,actualcut=None,operation_seconds=time.monotonic()-t197,process_cpu_seconds=time.process_time()-c197,pid=os.getpid(),session_id=46493)
p197.write_bytes((json.dumps(r197,indent=2)+'\n').encode());print('CL3_FULL_REVERSE',r197['status'],first197,'new',len(rows197),'of20','eng',eng197,'wall',r197['operation_seconds'],'CPU',r197['process_cpu_seconds'],'SHA',hashlib.sha256(p197.read_bytes()).hexdigest(),flush=True)
