import time,json,hashlib,zipfile,os,math
st160=time.monotonic();cp160=time.process_time();pp160=OUT/'day07-SOURCE-under-bank-vertical-return-whole-proposal.json';pr160=json.loads(pp160.read_bytes());fam160=pr160['family'];R160=fam160['R_mm'];xc160=fam160['centre_X_mm'];top160=fam160['upper_port_Z_mm'];E160=55;d160=(E160-(math.pi-2)*R160)/2;zc160=top160-d160;fields160={};quality160=[];ab160={}
for b in pr160['six_independent_storage_branches']:
 n=b['wire'];y=b['plane_Y_mm'];r=b['profile_radius_mm']+b['capacity_margin_mm'];P=A.Vector(xc160-R160,y,top160);L=A.Vector(xc160-R160,y,zc160);M=A.Vector(xc160,y,zc160-R160);H=A.Vector(xc160+R160,y,zc160);Q=A.Vector(xc160+R160,y,top160)
 w=Part.Wire([Part.makeLine(P,L),Part.Arc(L,M,H).toShape(),Part.makeLine(H,Q)]);prof=Part.Wire([Part.makeCircle(r,P,A.Vector(0,0,-1))]);s=w.makePipeShell([prof],True,False);expected=math.pi*r*r*(2*R160+E160);assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-expected)<1e-5
 lo=[xc160-R160-r,y-r,zc160-R160-r];hi=[xc160+R160+r,y+r,top160+r];bb=A.BoundBox(*(lo+hi));points=[A.Vector(xc160-R160-r,y,zc160),A.Vector(xc160+R160+r,y,zc160),A.Vector(xc160,y,zc160-R160-r),A.Vector(xc160,y+r,zc160-R160),A.Vector(xc160,y-r,zc160-R160)];on=[s.distToShape(Part.Vertex(p))[0] for p in points];assert max(on)<1e-6
 fields160[n]=s;ab160[n]=bb;quality160.append(dict(wire=n,valid=True,solids=1,centreline_mm=w.Length,analytic_centreline_mm=2*R160+E160,volume_mm3=s.Volume,analytic_volume_mm3=expected,analytic_full_bounds_mm=[lo,hi],default_bounds_mm=saved_bounds(s),new_extrema_point_onshape_distances_mm=on,margin_capacity_radius_mm=r,centreline_R_mm=R160))
context160=dict(ctx121);assert all(n in context160 and s.isSame(context160[n]) for n,s in restMotion.items());assert all(n in context160 and s.isSame(context160[n]) for n,s in op106.items())
context160.update({'PROPOSED_W068_CROWN_UNACCEPTED_KIT':union137,'PROPOSED_W068_FULL6_PRESSURE_HEAD':phead137})
tasks160=[]
for n,s in fields160.items():
 for k,v in context160.items():
  if bbox_lower_bound(ab160[n],v.BoundBox)<1.25:tasks160.append((n,k))
# Actual rigid current body source first. Flexible drawings remain typed, not an automatic rigid blocker.
tasks160.sort(key=lambda q:(0 if q[1].startswith('Ref_Material_P0_') else 1 if 'case' in q[1].lower() else 2,q[1],q[0]));rows160=[];first160=None;common160=None
for n,k in tasks160:
 s=fields160[n];v=context160[k];q=dict(wire=n,other=k,field_valid=True,source_valid=v.isValid(),required_mm=1.25,operand_classification='ACTUAL_RIGID_P0_SOURCE' if k.startswith('Ref_Material_P0_') else 'ACTUAL_CASE_OR_FUNCTIONAL_SOURCE_CLASSIFICATION_IF_HOLD')
 if not v.isValid():q['status']='CURRENT_INVALID_SOURCE_UNRESOLVED_NOT_CONTACT'
 else:
  g,ww,_=s.distToShape(v);q.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='SIDE_BAY_E55_FIELD_SEPARATED125' if g>=1.25-1e-7 else 'SIDE_BAY_E55_ALLOCATED_FIELD_HOLD')
  if g<1e-7:
   common160=s.common(v);q.update(common_valid=common160.isValid(),allocated_common_mm3=common160.Volume if common160.isValid() else None)
 rows160.append(q)
 if q['status']!='SIDE_BAY_E55_FIELD_SEPARATED125':first160=q;break
 if time.monotonic()-st160>18:break
items160=[('MANDATORY_E55_FULL_PROFILE:'+n,s) for n,s in fields160.items()]
if first160:items160.append(('FIRST_ACTUAL_SOURCE_NEIGHBOR',context160[first160['other']]))
if common160 is not None and not common160.isNull():items160.append(('FIRST_VALID_ALLOCATED_COMMON',common160))
ar160=OUT/'day07-SOURCE-sidebay-vertical-mandatory-E55-first-gate.breps.zip';assert not ar160.exists();ge160=[]
with zipfile.ZipFile(ar160,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(items160):
  raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge160.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge160),indent=2)+'\n').encode())
r160=dict(id='day07-SOURCE-sidebay-vertical-mandatory-E55-first-gate',status='VERTICAL_SIDE_BAY_FIRST_ALLOCATED_SOURCE_HOLD' if first160 else 'E55_SIDE_BAY_ENDPOINT_RECEIVED_ONLY_ADAPTIVE_AND_FANS_OPEN',selected=False,N01_complete=False,proposal=pp160.name,proposal_sha256=hashlib.sha256(pp160.read_bytes()).hexdigest(),full_six_profile_quality=quality160,rows=rows160,cursor=len(rows160),total=len(tasks160),unreceived=len(tasks160)-len(rows160),first_falsifier=first160,currentfullcontext=len(context160),rest108_source_same_all=True,new21_source_same_all=True,new21motion155_not_replayed=True,newW068crown_pressure_allocations_included_NOT_accepted=True,newprofiles_mean_allocated_space_NOT_deliveredwire_contact=True,E65_family_actual_percore_deltaL_R35p1_fans_A_Ufit_slack_OPEN=True,all9ID12portion4MAX3_sourceparts_andstockunchanged=True,no_material_built=True,archive=ar160.name,archive_sha256=hashlib.sha256(ar160.read_bytes()).hexdigest(),geometry=ge160,operation_seconds=time.monotonic()-st160,process_cpu_seconds=time.process_time()-cp160,pid=os.getpid(),session_id=46493)
p160=OUT/(r160['id']+'.json');assert not p160.exists();p160.write_bytes((json.dumps(r160,indent=2)+'\n').encode());print('BODY160',r160['status'],'first',first160,'rows',len(rows160),len(tasks160),'wall',r160['operation_seconds'],'CPU',r160['process_cpu_seconds'],flush=True);print('OWNER74_IDLE',os.getpid(),flush=True)
