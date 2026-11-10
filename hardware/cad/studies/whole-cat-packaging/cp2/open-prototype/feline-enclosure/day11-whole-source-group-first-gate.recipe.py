import time,json,math,hashlib,zipfile,os
T12=time.monotonic();C12=time.process_time();pp12=OUT/'day11-WHOLE_N01-layout-architecture-and-closure-plan.json';pa12=json.loads(pp12.read_bytes());gd12=pa12['group_capacity_definition'];R12=37.85;a12=80/(2*math.pi);rho12=gd12['outer_circular_capacity_radius_mm'];alpha12=math.atan(a12/R12);rc12=gd12['crest_unpitch_R_mm'];assert gd12['R_basis']['rotation_minimizing_offset_centre_R_lower_mm']>35.1
h12=Part.makeHelix(80,20,R12);h12.rotate(A.Vector(0,0,0),A.Vector(0,0,1),180);h12.translate(A.Vector(-94.9,77,44));E12=h12.Vertexes[-1].Point;P12=h12.Vertexes[0].Point;Tangent12=h12.Edges[0].tangentAt(h12.Edges[0].FirstParameter);M12=E12+A.Vector(rc12*(math.sin(alpha12)-math.sin(alpha12/2)),0,rc12*(math.cos(alpha12/2)-math.cos(alpha12)));Q12=E12+A.Vector(rc12*math.sin(alpha12),0,rc12*(1-math.cos(alpha12)));End12=A.Vector(65.98036180850077,Q12.y,Q12.z);arc12=Part.Arc(E12,M12,Q12).toShape();path12=Part.Wire(list(h12.Edges)+[arc12,Part.makeLine(Q12,End12)]);field12=path12.makePipeShell([Part.Wire([Part.makeCircle(rho12,P12,Tangent12)])],True,False);assert field12.isValid() and len(field12.Solids)==1
volume_expected12=math.pi*rho12*rho12*path12.Length;assert abs(field12.Volume-volume_expected12)<.1
lo12=[-94.9-R12-rho12,77-R12-rho12,44-rho12];hi12=[End12.x+rho12,77+rho12,End12.z+rho12];BB12=A.BoundBox(*lo12,*hi12)
fixed12={n:s for n,s in Current35.items() if n.startswith('Ref_Material_') or ':bought:' in n or n.endswith(':case') or (':kit:' in n and any(v in n for v in ['Screw','Nut','Washer']))}
tasks12=[]
for n,s in fixed12.items():
 bb=bounds11.get(n)
 b=A.BoundBox(*bb[0],*bb[1]) if bb else s.BoundBox
 if bbox_lower_bound(BB12,b)<1.25:tasks12.append(n)
tasks12.sort(key=lambda n:(0 if n.startswith('Ref_Material_P0_') else 1 if n.startswith('Ref_Material_S0_') else 2 if n.startswith('Ref_Material_U1_') else 3,n));rows12=[];first12=None
for n in tasks12:
 v=fixed12[n];q=dict(other=n,source_valid=v.isValid(),required_mm=1.25,classification='RETAINED_SOURCE_COMPONENT_FRAME_OR_WHOLE_CASE_NOT_PRINTED_ROOT_WAIVER')
 if not q['source_valid']:q['status']='ACTUAL_SOURCE_INVALID_NO_GEOMETRY_CONTACT_CLAIM';rows12.append(q);first12=q;break
 g,w,_=field12.distToShape(v);q.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='NEW_SOURCE_GROUP_FIELD_CLEAR' if g>=1.25-1e-7 else 'NEW_SOURCE_GROUP_ALLOCATION_HOLD')
 if g<1.25-1e-7:
  common12=field12.common(v);assert common12.isValid();q.update(common_valid=True,allocated_common_mm3=common12.Volume,meaning='ChosenwholelooseSOURCE9capacityallocation fails; notactualwirecontact/all3Dspace/physicalshortage. Stoponearchitecturecandidate/no nextfamily.');first12=q
 rows12.append(q);(OUT/'day11-whole-source-group-first-gate-cursor.json').write_bytes((json.dumps(dict(rows=rows12,received=len(rows12),total=len(tasks12),first=first12),indent=2)+'\n').encode())
 if first12 or len(rows12)>=40 or time.monotonic()-T12>70:break
ar12=OUT/'day11-whole-source-group-first-gate.breps.zip';gg12=[]
with zipfile.ZipFile(ar12,'w',zipfile.ZIP_DEFLATED) as z:
 ss=[('NEW_WHOLE_SOURCE9_LOOSE_CIRCULAR_CAPACITY',field12)]
 if first12:ss.append(('ACTUAL_FIRST_CURRENT_SOURCE:'+first12['other'],fixed12[first12['other']]))
 for i,(n,s) in enumerate(ss):
  f=Path('C:/Users/Sysq/AppData/Local/Temp/day11-source-first-'+str(i)+'.brep');s.exportBrep(str(f));raw=f.read_bytes();en=str(i)+'.brep';z.writestr(en,raw);gg12.append(dict(actor=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume))
 z.writestr('manifest.json',(json.dumps(dict(geometry=gg12),indent=2)+'\n').encode())
p12=OUT/'day11-whole-source-group-first-gate.json';r12=dict(id=p12.stem,status='WHOLE_ARCHITECTURE_GROUP_FIRST_FIXED_SOURCE_HOLD' if first12 else 'NECESSARY_GROUP_FIELD_BOUNDED_NO_WHOLE_N01_ACCEPTANCE',proposal=pp12.name,proposal_sha256=hashlib.sha256(pp12.read_bytes()).hexdigest(),allocated_group_not_purchased_jacket=True,profile=dict(radius_mm=rho12,all9normalplane_profiles_preserved=True,valid=field12.isValid(),solids=len(field12.Solids),guide_mm=path12.Length,volume_mm3=field12.Volume,expected_volume_mm3=volume_expected12,analytic_bounds_mm=[lo12,hi12],start=list(P12),end=list(End12),start_T=list(Tangent12),crest_R_mm=rc12),first_falsifier=first12,received=len(rows12),total=len(tasks12),unreceived=len(tasks12)-len(rows12),rows=rows12,immutable_source_context_count=len(fixed12),printed_load_replacement_and_proposed_effective1311_delta_NOT_accepted=True,new_moving_source21_rest108_and_whole_ground_contour_NOT_accepted=True,allactual_A_U_fit_slack_cut=None,oldpairs_replayed=0,no_new_prints_or_secondfamily=True,archive=ar12.name,archive_sha256=hashlib.sha256(ar12.read_bytes()).hexdigest(),geometry=gg12,operation_seconds=time.monotonic()-T12,process_cpu_seconds=time.process_time()-C12,pid=os.getpid(),session_id=70789,N01_complete=False);p12.write_bytes((json.dumps(r12,indent=2)+'\n').encode());print('DAY11_GROUP_GATE_SAVED',first12,'rows',len(rows12),'of',len(tasks12),'wallCPU',r12['operation_seconds'],r12['process_cpu_seconds'],'OWNER11476_NATIVE_IDLE',flush=True)
