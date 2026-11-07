import time,json,math,hashlib,zipfile,os
tr121=time.monotonic();tc121=time.process_time();pp121=OUT/'day07-SOURCE-FL2-body-reserve-and-DGV-whole-proposal.json';prop121=json.loads(pp121.read_bytes());bs121=prop121['connected_route']['body_storage'];R121=37.85;z121=42.05;h121=3.9;w121=4.7;P121=np.array([-94.9,16.15]);pl121,ph121=bs121['phi_range_radians']
def sector121(name,c,inner,outer,a,b):
 p=A.Vector(float(c[0]),float(c[1]),z121);s=Part.makeCylinder(outer,h121,p,A.Vector(0,0,1),math.degrees(b-a));s.rotate(p,A.Vector(0,0,1),math.degrees(a));s=s.cut(Part.makeCylinder(inner,h121+.2,A.Vector(p.x,p.y,z121-.1)));assert s.isValid() and len(s.Solids)==1;return(name,s)
fields121=[sector121('INPUT_CONNECTED_QUARTER',[-94.9,54],R121-w121,R121+w121,math.pi,1.5*math.pi)];allfields121=[]
# Wholeadaptivefamilycover, notfilledbaybbox. Firstarc centreconstant/nestedsectors exact.
allfields121.append(sector121('BODY_FIRST_ARC_ALLPHI',P121+[0,-R121],R121-w121,R121+w121,math.pi/2-ph121,math.pi/2))
for j in range(8):
 a=pl121+(ph121-pl121)*j/8;b=pl121+(ph121-pl121)*(j+1)/8;m=(a+b)/2
 c=P121+[2*R121*math.sin(m),-R121+2*R121*math.cos(m)];delta=4*R121*math.sin((b-a)/4);pad=math.asin(delta/(R121-w121));allfields121.append(sector121('BODY_MIDDLE_INTERVAL_'+str(j),c,R121-w121-delta,R121+w121+delta,-math.pi/2-b-pad,-math.pi/2+b+pad))
 c=P121+[4*R121*math.sin(m),-R121];delta=max(abs(4*R121*(math.sin(x)-math.sin(m))) for x in [a,b]);pad=math.asin(delta/(R121-w121));allfields121.append(sector121('BODY_FINAL_INTERVAL_'+str(j),c,R121-w121-delta,R121+w121+delta,math.pi/2-pad,math.pi/2+b+pad))
startX=P121[0]+4*R121*math.sin(pl121);allfields121.append(('BODY_VARIABLE_FINAL_STRAIGHT_COVER',Part.makeBox(55.1-startX,9.4,3.9,A.Vector(startX,16.15-4.7,42.05))));fields121+=allfields121
ctx121=dict(ctx114);tasks121=[]
for n,s in fields121:
 for k,v in ctx121.items():
  if bbox_lower_bound(s.BoundBox,v.BoundBox)<1.25:tasks121.append((n,k))
lookup121=dict(fields121);tasks121.sort(key=lambda x:(0 if x[0]=='INPUT_CONNECTED_QUARTER' else 1,0 if x[1]=='Ref_Material_S0_body_CP2_0_0' else 1,x));rows121=[];first121=None;co121=None
for n,k in tasks121:
 s=lookup121[n];v=ctx121[k];row=dict(region=n,other=k,source_valid=v.isValid(),field_valid=s.isValid())
 if row['source_valid']:
  gap,ww,_=s.distToShape(v);row.update(gap_mm=gap,witnesses=[[list(aa),list(bb)] for aa,bb in ww[:1]],status='BODY_RESERVE_REGION_SEPARATED125' if gap>=1.25-1e-7 else 'ALLOCATED_BODY_REGION_HOLD_NOT_DELIVEREDWIRECONTACT')
  if gap<1e-7:
   co121=s.common(v);row.update(common_valid=co121.isValid(),allocated_common_mm3=co121.Volume if co121.isValid() else None)
 else:row['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
 rows121.append(row)
 if row['status']!='BODY_RESERVE_REGION_SEPARATED125':first121=row;break
 if time.monotonic()-tr121>15:break
whole121=Part.makeCompound([s for n,s in fields121]);assert len(whole121.Solids)==len(fields121);bodybbox121=whole121.BoundBox;cover121=Part.makeBox(bodybbox121.XLength+6.5,bodybbox121.YLength+6.5,bodybbox121.ZLength+6.5,A.Vector(bodybbox121.XMin-3.25,bodybbox121.YMin-3.25,bodybbox121.ZMin-3.25));outside121=None
if first121 is None:outside121=cover121.cut(BodyOuter31);assert outside121.isValid()
sections121=[]
yvalues121=[16.15,-30.0]
if first121 and first121.get('witnesses'):yvalues121=[first121['witnesses'][0][0][1],-30.0]
for y in yvalues121:
 plane=Part.makePlane(350,160,A.Vector(-180,y,-20),A.Vector(0,1,0))
 for n,s in [('proposed_full_body_reserve_region',whole121),('actual_S0_body',ctx121['Ref_Material_S0_body_CP2_0_0'])]+([(first121['other'],ctx121[first121['other']])] if first121 else []):
  sec=s.section(plane);curves=[]
  for e in sec.Edges:
   ps=e.discretize(Deflection=.2)
   if len(ps)>1:curves.append([[v.x,v.z] for v in ps])
  sections121.append(dict(Y_mm=y,name=n,curves_xz=curves))
ar121=OUT/'day07-SOURCE-FL2-body-reserve-first-gate.breps.zip';assert not ar121.exists();ge121=[]
with zipfile.ZipFile(ar121,'w',zipfile.ZIP_DEFLATED) as zz:
 its=[('WHOLE_ADAPTIVE_BODY_REGION_COVERS_NOT_PRINT',whole121)];
 if first121:its.extend([('FIRST_FIELD',lookup121[first121['region']]),('FIRST_ACTUAL_CURRENT_NEIGHBOR',ctx121[first121['other']])])
 if co121 is not None:its.append(('ALLOCATED_COMMON_NOT_WIRECONTACT',co121))
 for i,(n,s) in enumerate(its):
  raw=s.exportBrepToString().encode();e=str(i)+'.brep';zz.writestr(e,raw);bb=s.optimalBoundingBox(False,False);ge121.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=[[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]],volume_mm3=s.Volume,valid=s.isValid()))
 zz.writestr('manifest.json',(json.dumps(dict(geometry=ge121,scope='Newbodyallocatedregion/fulladaptive55..65coverageONLY/no newprintedmaterial/leggeometry/oldsourcechecks'),indent=2)+'\n').encode())
r121=dict(id='day07-SOURCE-FL2-body-reserve-first-gate',status='BODY_RESERVE_CONNECTED_REGION_FIRST_FALSIFIER_HOLD' if first121 else 'BODY_RESERVE_REGION_PENDING' if len(rows121)<len(tasks121) else 'BODY_RESERVE_STATIC_SCOPE_RECEIVED_OTHERPROOFS_OPEN',proposal=pp121.name,proposal_sha256=hashlib.sha256(pp121.read_bytes()).hexdigest(),region_parts_count=len(fields121),compound_solids=len(whole121.Solids),all_group_capacity_members_retained=True,adaptive_family=dict(E_each_core_mm=[55,65],R_group_mm=37.85,R_min_percore_mm=35.1,intervals=8,method='Analyticcentreshiftbounds+angle/radialpaddingcoversALLphi, notemptybboxorclearanceparametersearch. FixedP/Q+variablefinalstraightmaintainswirelengthtransfer.',original_input_straight_is_subset_received_leftpassage=True),rows=rows121,cursor=len(rows121),total=len(tasks121),unreceived=len(tasks121)-len(rows121),first_falsifier=first121,BodyOuter3p25='UNRECEIVED_AFTER_FIRST_HOLD' if outside121 is None else dict(outside_mm3=outside121.Volume,valid=outside121.isValid()),current_context_count=len(ctx121),mechanical_transfer='Plannedcontinuousloosespanbeforeall3truebodyendclamps; no fixedclampbeforeSloopadded/no oldunselected9guide. Physicalcase/stock/coallocation/slidingretention/root/motion/accessremainOPEN ifHOLD.',new_leg_geometry_built=False,new_material_built=False,all_current_A_U_minimum_fit_slack=None,sections=sections121,archive=ar121.name,archive_sha256=hashlib.sha256(ar121.read_bytes()).hexdigest(),geometry=ge121,operation_seconds=time.monotonic()-tr121,process_cpu_seconds=time.process_time()-tc121,selected=False,N01_complete=False,pid=os.getpid(),session_id=46493)
p121=OUT/'day07-SOURCE-FL2-body-reserve-first-gate.json';assert not p121.exists();p121.write_bytes((json.dumps(r121,indent=2)+'\n').encode());print('BODY_RESERVE121',r121['status'],len(rows121),len(tasks121),first121,r121['operation_seconds'],r121['process_cpu_seconds'],hashlib.sha256(p121.read_bytes()).hexdigest(),flush=True);print('OWNER61_IDLE',os.getpid(),'1292/1311/108 pendingnull unsavedfalse',flush=True)
