import time,json,hashlib,zipfile,math,os
st162=time.monotonic();cp162=time.process_time();b=pr160['six_independent_storage_branches'][0];x=xc160+R160;y=b['plane_Y_mm'];z=top160;r=b['profile_radius_mm']+.4
P=A.Vector(x,y,z);M=A.Vector(x,y-R160+R160/math.sqrt(2),z+R160/math.sqrt(2));Q=A.Vector(x,y-R160,z+R160);w=Part.Wire([Part.Arc(P,M,Q).toShape()]);s= w.makePipeShell([Part.Wire([Part.makeCircle(r,P,A.Vector(0,0,1))])],True,False);assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-math.pi*r*r*w.Length)<1e-5
names162=[k for k,v in context160.items() if bbox_lower_bound(s.BoundBox,bounds126[k] if k in bounds126 else v.BoundBox)<1.25];names162.sort(key=lambda k:(0 if k=='Underdeck:PositiveFoundation' else 1,k));rows162=[];first162=None;c162=None
for k in names162:
 v=context160[k];q=dict(wire='W005',other=k,required_mm=1.25,source_valid=v.isValid(),field_valid=True)
 if not v.isValid():q['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
 else:
  g,ww,_=s.distToShape(v);q.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='LOCAL_EXIT_FIELD_SEPARATED125' if g>=1.25 else 'LOCAL_EXIT_FIELD_HOLD')
  if g<1e-7:c162=s.common(v);q.update(common_valid=c162.isValid(),allocated_common_mm3=c162.Volume if c162.isValid() else None)
 rows162.append(q)
 if q['status']!='LOCAL_EXIT_FIELD_SEPARATED125':first162=q;break
items162=[('D_FL2_ALLOCATED_UP_TO_MINUS_Y_EXIT',s),('ACTUAL_CURRENT_U1_COMPLETE_CARRIER',context160['Underdeck:PositiveFoundation'])]
if c162 is not None and not c162.isNull():items162.append(('ACTUAL_ALLOCATED_COMMON',c162))
ar162=OUT/'day07-SOURCE-sidebay-D-exit-U1-local-witness.breps.zip';assert not ar162.exists();ge162=[]
with zipfile.ZipFile(ar162,'w',zipfile.ZIP_DEFLATED) as zz:
 for i,(n,v) in enumerate(items162):
  raw=v.exportBrepToString().encode();en=str(i)+'.brep';zz.writestr(en,raw);ge162.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=v.isValid(),volume_mm3=v.Volume,bounds_mm=saved_bounds(v)))
 zz.writestr('manifest.json',(json.dumps(dict(geometry=ge162),indent=2)+'\n').encode())
r162=dict(id='day07-SOURCE-sidebay-D-exit-U1-local-hazard',status='DIRECT_VERTICAL_BAY_EXIT_BLOCKED_BY_CURRENT_U1_MATERIAL' if first162 else 'LOCAL_EXIT_RECEIVED_ONLY',selected=False,N01_complete=False,named_hazard='StorageUupperDportpoints+ZundercompleteU1lowercarrier. OneR35.1quarterto-YtowardcurrentDreceiver maycrossactualsteppedcarrier; boundingoverlapcannotidentifyactualholes. Fullreservedlocalprofile answersTHISexitlayerdecision only, notwholewire/123axes.',source_wire='W005',source_physical_unit='SOURCE/FL2',P=list(P),Q=list(Q),initial_T=[0,0,1],final_T=[0,-1,0],R_mm=R160,capacity_radius_mm=r,centreline_mm=w.Length,actual_profile_valid=True,rows=rows162,cursor=len(rows162),total=len(names162),unreceived=len(names162)-len(rows162),first_falsifier=first162,storage_E55_E65_static_capacity_NOT_revoked=True,meaning='Thisdirectexitallocationnotusable; NOTactualdeliveredwirecontact/allmanualapproachesimpossible/stockshortage. No printedcarrier cut/port move/newmaterial. Resolvewholebelow-floorfan/layorder oraccessibleU1aperture beforeclaimedusablemoving55.',A_U_percore_actualdeltaL_fit_slack=None,actual_cut=None,archive=ar162.name,archive_sha256=hashlib.sha256(ar162.read_bytes()).hexdigest(),geometry=ge162,operation_seconds=time.monotonic()-st162,process_cpu_seconds=time.process_time()-cp162,pid=os.getpid(),session_id=46493)
p162=OUT/(r162['id']+'.json');assert not p162.exists();p162.write_bytes((json.dumps(r162,indent=2)+'\n').encode());print('BODY162',r162['status'],first162,'rows',len(rows162),len(names162),'wall',r162['operation_seconds'],'CPU',r162['process_cpu_seconds'],flush=True);print('OWNER74_IDLE',os.getpid(),flush=True)
