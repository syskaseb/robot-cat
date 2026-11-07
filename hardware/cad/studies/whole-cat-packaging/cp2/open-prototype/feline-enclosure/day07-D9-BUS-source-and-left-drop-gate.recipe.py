import time,json,hashlib,zipfile,math,os
t128=time.monotonic();c128=time.process_time();prp128=OUT/'day07-SOURCE-D9-anchored-south-return-and-BUS-D-coallocation-proposal.json';pr128=json.loads(prp128.read_bytes());source128={}
for tag in ['D','G']:
 cap=ctx121['DGGrip:'+tag+':cap'];face=next(f for f in cap.Faces if isinstance(f.Surface,Part.Cylinder));surf=face.Surface;axis=np.array(list(surf.Axis));axis=axis/np.linalg.norm(axis);base=np.array(list(surf.Center));values=[float(np.dot(np.array(list(v.Point))-base,axis)) for v in cap.Vertexes];p0=base+min(values)*axis;p9=base+max(values)*axis
 band=ctx121['DGGrip:'+tag+':band'];source128[tag]=dict(current_cap_valid=cap.isValid(),groove_axis=axis.tolist(),groove_radius_mm=surf.Radius,actual9_start_mm=p0.tolist(),actual9_end_mm=p9.tolist(),actual9_span_mm=float(np.linalg.norm(p9-p0)),band_valid=band.isValid(),band_volume_mm3=band.Volume,loop_geometry_debit_mm=band.Volume/(2.5*1.2),band_bounds_mm=saved_bounds(band),head_bounds_mm=saved_bounds(ctx121['DGGrip:'+tag+':head']),source_family_current_nominal_H5_jacket_origin_R10=(p0-10*(np.array([0.,0,-1])+axis)).tolist(),origin_not_manufacturer_pinout=True,whole_tail_145_upper_bound_mm=145-band.Volume/3,head_pull25_portion_inside_remaining_tail=True,exact_current_SKU_binding='OPEN, no physical inventory claim')
src128=pr128['route_OUTWARD_from_receiver'][4];P128=np.array(src128['P']);T128=np.array([0.,1,0]);N128=np.array([0.,0,-1]);R128=35.1;ang128=src128['opposed_arc_angle_each']
def edge128(p,t,n,ang):
 pts=[p+R128*math.sin(a)*t+R128*(1-math.cos(a))*n for a in [0,ang/2,ang]];e=Part.Arc(*[A.Vector(*p) for p in pts]).toShape();return e,pts[-1],math.cos(ang)*t+math.sin(ang)*n,-math.sin(ang)*t+math.cos(ang)*n
e1,p1,t1,n1=edge128(P128,T128,N128,ang128);e2,p2,t2,n2=edge128(p1,t1,-n1,ang128);profile=Part.Wire(Part.makeCircle(1.95,A.Vector(*P128),A.Vector(*T128)));drop128=Part.Wire([e1,e2]).makePipeShell([profile],True,False);assert drop128.isValid() and len(drop128.Solids)==1;assert np.linalg.norm(p2-np.array(src128['Q']))<1e-6
bb=drop128.optimalBoundingBox(False,False);candidates128=[k for k,v in ctx121.items() if bbox_lower_bound(bb,bounds126[k])<1.25];candidates128.sort(key=lambda k:(0 if k=='Ref_Material_S0_body_CP2_0_0' else 1 if 'ring' in k.lower() else 2,k));checks128=[];first128=None;common128=None
for k in candidates128:
 v=ctx121[k];row=dict(other=k,field_valid=True,source_valid=v.isValid())
 if row['source_valid']:
  gap,ww,_=drop128.distToShape(v);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='CAPACITY_SEPARATED125' if gap>=1.25-1e-7 else 'ALLOCATED_ENTRY_REGION_HOLD_FUNCTION_PENDING_NOT_WIRECONTACT')
  if gap<1e-7:
   common128=drop128.common(v);row.update(common_valid=common128.isValid(),allocated_common_mm3=common128.Volume if common128.isValid() else None)
 else:row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
 checks128.append(row)
 if row['status']!='CAPACITY_SEPARATED125':first128=row;break
 if time.monotonic()-t128>15:break
items128=[('FULL_D_LEFT_ENTRY_DROP_CAPACITY',drop128)]
if first128:items128.append(('FIRST_ACTUAL_CURRENT_NEIGHBOR',ctx121[first128['other']]))
if common128 is not None:items128.append(('ALLOCATED_COMMON_NOT_DELIVERED_WIRECONTACT',common128))
items128 += [('CURRENT_BUS_D_CAP',ctx121['DGGrip:D:cap']),('CURRENT_BUS_D_BAND',ctx121['DGGrip:D:band']),('CURRENT_BUS_D_HEAD',ctx121['DGGrip:D:head'])]
sections128=[]
ys128=[float(first128['witnesses'][0][0][1])] if first128 and first128.get('witnesses') else [-25.0]
for y in ys128:
 plane=Part.makePlane(100,140,A.Vector(-160,y,0),A.Vector(0,1,0))
 for name,sh in items128[:3 if common128 is not None else 2]:
  sec=sh.section(plane);curves=[]
  for e in sec.Edges:
   ps=e.discretize(Deflection=.08)
   if len(ps)>1:curves.append([[v.x,v.z] for v in ps])
  sections128.append(dict(Y_mm=y,name=name,curves_xz=curves))
ar128=OUT/'day07-SOURCE-D9-BUS-source-and-left-entry-gate.breps.zip';assert not ar128.exists();ge128=[]
with zipfile.ZipFile(ar128,'w',zipfile.ZIP_DEFLATED) as zz:
 for i,(name,sh) in enumerate(items128):
  raw=sh.exportBrepToString().encode();en=str(i)+'.brep';zz.writestr(en,raw);ge128.append(dict(name=name,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=sh.isValid(),volume_mm3=sh.Volume,bounds_mm=saved_bounds(sh)))
 zz.writestr('manifest.json',(json.dumps(dict(geometry=ge128),indent=2)+'\n').encode())
r128=dict(id='day07-SOURCE-D9-BUS-source-and-left-entry-gate',status='D9_ANCHORED_WHOLE_APPROACH_FIRST_LOCAL_ENTRY_HOLD' if first128 else 'D9_ENTRY_SCOPE_RECEIVED_WHOLE_APPROACH_OPEN',proposal=prp128.name,proposal_sha256=hashlib.sha256(prp128.read_bytes()).hexdigest(),BUS_native_source_function=source128,BUS_H5_nominal_bounds_mm=saved_bounds(ctx121['CurrentBUS:H5MatingReserve']),BUS_root_valid=ctx121['SharedBUS:TailCarrier'].isValid(),BUS_root_unchanged=True,logical_W002_W003_only_no_oldworld_transform=True,checked_rows=checks128,cursor=len(checks128),total=len(candidates128),unreceived=len(candidates128)-len(checks128),first_falsifier=first128,new_region_role='SingleDreceiver-sidecapacitylocalcasehazard, full3.9profile/.4margin/R35.1/opposedarcs; not exactphysicalfreewire/global123sweep/immutablelegcurve',actual_region_endpoint=p2.tolist(),new_D_body_plan_length_mm=pr128['known_D_body_plan_centreline_min_mm'],new_D_body_length_NOT_wholephysical_fit=True,sections=sections128,archive=ar128.name,archive_sha256=hashlib.sha256(ar128.read_bytes()).hexdigest(),geometry=ge128,new_material=False,new_leg_geometry=False,all9_A_U_minfit_slack=None,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t128,process_cpu_seconds=time.process_time()-c128,pid=os.getpid(),session_id=46493)
rp128=OUT/'day07-SOURCE-D9-BUS-source-and-left-entry-gate.json';assert not rp128.exists();rp128.write_bytes((json.dumps(r128,indent=2)+'\n').encode());print('BODY128',r128['status'],len(checks128),len(candidates128),first128,'BUS_D',source128['D'],'wall',r128['operation_seconds'],'CPU',r128['process_cpu_seconds'],flush=True);print('OWNER64_IDLE',os.getpid(),flush=True)
