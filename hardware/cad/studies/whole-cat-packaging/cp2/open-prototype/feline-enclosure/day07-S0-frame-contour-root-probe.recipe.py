import time,json,hashlib,zipfile,os,math
t56=time.monotonic();c56=time.process_time();s0names56=[n for n in Current35 if n.startswith('Ref_Material_S0')];assert len(s0names56)==11
neck56=Current35['Ref_Material_S0_neck_CP2_0_0'];body56=Current35['Ref_Material_S0_body_CP2_0_0'];cyl56=next(f for f in neck56.Faces if type(f.Surface).__name__=='Cylinder')
axis56=np.array(list(cyl56.Surface.Axis));axis56/=np.linalg.norm(axis56)
if axis56@(np.array(list(body56.CenterOfMass))-np.array(list(neck56.CenterOfMass)))<0:axis56=-axis56
planes56=[f for f in neck56.Faces if type(f.Surface).__name__=='Plane'];seatface56=min(planes56,key=lambda f:(f.CenterOfMass-body56.CenterOfMass).Length);C56=np.array(list(seatface56.CenterOfMass));out56=-axis56
def nearStud56(n):return np.array(list(min([f for f in Current35[n].Faces if type(f.Surface).__name__=='Plane'],key=lambda f:(f.CenterOfMass-A.Vector(*C56)).Length).CenterOfMass))
in56=nearStud56('Ref_Material_S0_stud_IN_0_0');outStud56=nearStud56('Ref_Material_S0_stud_OUT_0_0');stud56=outStud56-in56;stud56-=axis56*(stud56@axis56);stud56/=np.linalg.norm(stud56);fix56=-np.cross(axis56,stud56)
dsrc56=np.array([0.,-1,0]);ssrc56=np.array([-math.sqrt(.5),0,math.sqrt(.5)]);fsrc56=-np.cross(dsrc56,ssrc56);Rot56=np.column_stack((axis56,stud56,fix56))@np.column_stack((dsrc56,ssrc56,fsrc56)).T
srcC56=np.array([-61.5,95.,43.]);T56=C56-Rot56@srcC56;assert np.linalg.norm(Rot56.T@Rot56-np.eye(3))<1e-10 and abs(np.linalg.det(Rot56)-1)<1e-10
srcStud56=[[-53.01471862576143,70,34.51471862576143],[-69.98528137423857,70,51.48528137423857]]
res56=[float(np.linalg.norm(Rot56@np.array(p)+T56-q)) for p,q in zip(srcStud56,[in56,outStud56])];assert max(res56)<1e-7
key56=Current35['Ref_Material_S0_key_CP2_0_0'];keyplane56=min([f for f in key56.Faces if type(f.Surface).__name__=='Plane'],key=lambda f:(f.CenterOfMass-A.Vector(*C56)).Length);keyres56=float(np.linalg.norm(C56+3*out56-np.array(list(keyplane56.CenterOfMass))));assert keyres56<1e-7
fixcentres56=[C56+fix56*d for d in [-19,19]]
contour56=[]
boundary56=Part.makeCompound(BodyOuter31.Faces)
for n in s0names56:
 s=Current35[n];cut=s.cut(BodyOuter31);gap=s.distToShape(boundary56)[0];contour56.append(dict(name=n,source_valid=s.isValid(),outside_valid=cut.isValid(),outside_mm3=cut.Volume,boundary_gap_mm=gap,required_mm=3.25,ok=s.isValid() and cut.isValid() and cut.Volume<1e-7 and gap>=3.25-1e-7))
# One actual source-rail footprint; top horizontal faces are real source faces because ROI ceiling50 > railmax48.1.
railname56='CurrentFoundation:FoundationRail:-1';rail56=Current35[railname56];roi56=box49([-86,-28,34],[-80,-20,50]);coupon56=rail56.common(roi56);rootfaces56=[]
if not coupon56.isNull() and coupon56.Volume>1e-7:
 for f in coupon56.Faces:
  if type(f.Surface).__name__=='Plane' and abs(f.normalAt(0,0).z)>.999 and abs(f.CenterOfMass.z-coupon56.BoundBox.ZMax)<1e-7:
   p=f.CenterOfMass-A.Vector(0,0,.1);rootfaces56.append(dict(area_mm2=f.Area,centre_mm=list(f.CenterOfMass),source_material_inside_below=rail56.isInside(p,1e-7,False)))
rootface56=max([f for f in coupon56.Faces if type(f.Surface).__name__=='Plane' and abs(f.normalAt(0,0).z)>.999 and abs(f.CenterOfMass.z-coupon56.BoundBox.ZMax)<1e-7],key=lambda f:f.Area) if rootfaces56 else None
ar56=OUT/'day07-S0-frame-contour-actual-root-inputs.breps.zip';assert not ar56.exists();ge56=[]
with zipfile.ZipFile(ar56,'w',zipfile.ZIP_DEFLATED) as z:
 items=[(n,Current35[n]) for n in s0names56]+[(railname56,rail56)]+([('SOURCE:actual_rail_footprint_coupon',coupon56)] if not coupon56.isNull() else [])
 for i,(n,s) in enumerate(items):
  raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge56.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge56,scope='Actual currentworld BReps, no XML reapplied; one currentrail footprint'),indent=2)+'\n').encode())
r56=dict(id='day07-S0-current-frame-contour-root-probe',status='SOURCE_FRAME_MATCHED_CURRENT11_CONTOUR_RECEIVED_ROOTFACE_AVAILABLE' if all(r['ok'] for r in contour56) and any(r['source_material_inside_below'] and r['area_mm2']>=12 for r in rootfaces56) else 'FRAME_OR_CONTOUR_OR_ROOT_HOLD',
 source_interface=dict(nominal_R6_origin_mm=srcC56.tolist(),current_neck_seating_plane_centre_mm=C56.tolist(),current_axis_into_body=axis56.tolist(),labelled_IN_OUT_direction=stud56.tolist(),current_casefix_pair_direction=fix56.tolist(),source_to_current_rotation=Rot56.tolist(),source_to_current_translation_mm=T56.tolist(),proper_rotation_det=float(np.linalg.det(Rot56)),labelled_stud_plane_match_residuals_mm=res56,neck_to_key_face_match_residual_mm=keyres56,mapped_two_M6_centres_mm=[p.tolist() for p in fixcentres56],fix_pitch_mm=38,panel_neck_hole_mm=24,panel_fix_holes_mm=6.5,old_XML_placement_applied=False,source_flangethickness4_and_seat70_are_project_not_supplier=True),
 complete11_contour=contour56,root=dict(actual_parent=railname56,requested_footprint_mm=[[-86,-28,34],[-80,-20,50]],actual_coupon_valid=not coupon56.isNull() and coupon56.isValid(),actual_coupon_mm3=coupon56.Volume if not coupon56.isNull() else 0,actual_top_faces=rootfaces56,not_bbox_root=True),
 source_current1292_unchanged=True,archive=ar56.name,archive_sha256=hashlib.sha256(ar56.read_bytes()).hexdigest(),geometry=ge56,operation_seconds=time.monotonic()-t56,process_cpu_seconds=time.process_time()-c56,pid=os.getpid(),session_id=46493,selected=False,N01_complete=False)
p56=OUT/'day07-S0-current-frame-contour-root-probe.json';assert not p56.exists();p56.write_bytes((json.dumps(r56,ensure_ascii=False,indent=2)+'\n').encode());print('S0_FRAME56',r56['status'],[p.tolist() for p in fixcentres56],min(r['boundary_gap_mm'] for r in contour56),r56['root'],r56['operation_seconds'],r56['process_cpu_seconds'],hashlib.sha256(p56.read_bytes()).hexdigest(),flush=True)
