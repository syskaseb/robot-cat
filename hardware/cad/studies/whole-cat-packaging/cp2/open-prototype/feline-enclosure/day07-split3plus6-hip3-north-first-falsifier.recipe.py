import time,json,os,math,hashlib,zipfile
t237=time.monotonic();c237=time.process_time();pp237=OUT/'day07-SPLIT_HIP3_DIRECT10_KNEE6_LOWER55-whole-proposal.json';pr237=json.loads(pp237.read_bytes());fields237={};quality237=[];rows237=[];first237=None;bb237={};tasks237=[]
for q in pr237['rows']:
 if q['row']!=0:continue
 n=q['wire'];P=A.Vector(*q['upper_passage_P']);R=q['north_turn_R_mm'];Q=A.Vector(*q['north_turn_end']);E=A.Vector(*q['leading_end']);C=A.Vector(-94.9,77,47.3);arc=Part.Arc(P,A.Vector(C.x-R/math.sqrt(2),C.y-R/math.sqrt(2),47.3),Q).toShape();path=Part.Wire([arc,Part.makeLine(Q,E)]);r=1.4 if q['core']=='V' else 1.95;s=path.makePipeShell([Part.Wire([Part.makeCircle(r,P,A.Vector(0,-1,0))])],True,False);assert s.isValid() and abs(s.Volume-math.pi*r*r*path.Length)<1e-4
 lo=[P.x-r,Q.y-r,47.3-r];hi=[E.x+r,77+r,47.3+r];bb237[n]=box153([lo,hi]).BoundBox;fields237[n]=s;quality237.append(dict(wire=n,valid=True,nominal_radius_mm=r-.4,allocated_radius_mm=r,R_mm=R,local_guide_mm=path.Length,actual_volume_mm3=s.Volume,expected_volume_mm3=math.pi*r*r*path.Length,bounds_mm=[lo,hi]))
tasks237=[(n,k) for n in fields237 for k,v in context230.items() if bbox_lower_bound(bb237[n],v.BoundBox)<1.25]
tasks237.sort(key=lambda p:(0 if p[1].startswith('Ref_Material_P0_') else 1 if p[1].startswith('Ref_Material_') else 2,p[1],p[0]))
for n,k in tasks237:
 s=fields237[n];v=context230[k];q=dict(field=n,other=k,source_valid=v.isValid(),required_mm=1.25)
 if not q['source_valid']:q.update(status='SOURCE_INVALID_UNRESOLVED_NOT_CONTACT');rows237.append(q);first237=q;break
 g,ws,_=s.distToShape(v);q.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in ws[:1]],status='NEW_HIP_NORTH_CAPACITY_CLEAR' if g>=1.25-1e-7 else 'NEW_HIP_NORTH_ALLOCATED_HOLD')
 if g<1.25-1e-7:
  co=s.common(v);assert co.isValid();q.update(common_valid=True,allocated_common_mm3=co.Volume,meaning='Capacity/actualrequiredpart functionalclearanceHOLD, notdeliveredwirecontact/all3Dlayouts/physicalshortage. No secondfamily or remainingfailedscan.')
 rows237.append(q)
 # Immediately persist every received key, no unsaved broad scan.
 cursor=OUT/'day07-SPLIT3plus6-Hip-upper-north-first-gate-cursor.json';cursor.write_bytes((json.dumps(dict(rows=rows237,received=len(rows237),total=len(tasks237),first=first237,pending=None if first237 else (tasks237[len(rows237)] if len(rows237)<len(tasks237) else None)),indent=2)+'\n').encode())
 if first237:break
 # Small interruptible scope; never extend into a whole model scan.
 if time.monotonic()-t237>65 or len(rows237)>=36:break
ar237=OUT/'day07-SPLIT3plus6-Hip-north-first-gate.breps.zip';gg=[]
with zipfile.ZipFile(ar237,'w',zipfile.ZIP_DEFLATED) as z:
 ss=[('NEW_HIP_NORTH:'+n,s) for n,s in fields237.items()]
 if first237:ss.append(('FIRST_CURRENT_ACTUAL:'+first237['other'],context230[first237['other']]))
 for i,(n,s) in enumerate(ss):
  f=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat94-'+str(i)+'.brep');s.exportBrep(str(f));raw=f.read_bytes();e=str(i)+'.brep';z.writestr(e,raw);gg.append(dict(actor=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=gg),indent=2)+'\n').encode())
p237=OUT/'day07-SPLIT3plus6-Hip-upper-north-first-gate.json';r237=dict(id=p237.stem,status='WHOLE3PLUS6_FIRST_HIP_NORTH_FALSIFIER_STOP' if first237 else 'HIP_LOCAL_NORTH_BOUNDED_CURSOR_NOT_WHOLE_TRANSPORT',proposal=pp237.name,proposal_sha256=hashlib.sha256(pp237.read_bytes()).hexdigest(),quality=quality237,rows=rows237,received=len(rows237),total=len(tasks237),unreceived=len(tasks237)-len(rows237),first_falsifier=first237,source_whole_context=len(context230),all9_12portion4MAX3_preserved=True,selected=False,N01_complete=False,actual_allphysical_fit_slack_cut=None,bodyouter_and_moving_free_legs_NOT_qualified=True,no_new_material_or_secondfamily=True,archive=ar237.name,archive_sha256=hashlib.sha256(ar237.read_bytes()).hexdigest(),geometry=gg,operation_seconds=time.monotonic()-t237,process_cpu_seconds=time.process_time()-c237,pid=os.getpid(),session_id=46493);p237.write_bytes((json.dumps(r237,indent=2)+'\n').encode());print('SPLIT237_SAVED',first237,'received',len(rows237),'total',len(tasks237),'wallCPU',r237['operation_seconds'],r237['process_cpu_seconds'],'OWNER94_NATIVE_IDLE26064',flush=True)
