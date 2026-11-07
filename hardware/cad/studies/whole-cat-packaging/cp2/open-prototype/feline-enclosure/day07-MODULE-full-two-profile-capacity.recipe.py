import time,json,hashlib,zipfile,math,os
t52=time.monotonic();c52=time.process_time();rows52=CurrentCanon31['current_foreign_flat_crossing_proposal']['module_rows'];pr52=CurrentCanon31['current_foreign_flat_front_candidate']['proofs'];a52=np.array(rows52[5]['start']);b52=np.array(rows52[5]['end']);L52=float(np.linalg.norm(b52-a52));tangent52=(b52-a52)/L52
u052=np.array(pr52['continuous_pair_transport'][-1]['end_pair_offset_mm'])
last52=rows52[6];edge52=Part.Arc(A.Vector(*last52['start']),A.Vector(*last52['mid']),A.Vector(*last52['end'])).toShape();curve52=edge52.Curve;axis52=np.array(list(curve52.Axis));centre52=np.array(list(curve52.Center));rr52=(np.array(last52['start'])-centre52)/last52['radius_mm'];ang52=last52['length_mm']/last52['radius_mm']
def rot52(v,n,a):return v*math.cos(a)+np.cross(n,v)*math.sin(a)+n*(n@v)*(1-math.cos(a))
u152=rot52(np.array([0.,0.,-1.5]),axis52,-ang52)
assert abs(last52['radius_mm']+u152@rr52-pr52['module_each_core']['XP03.module']['arc_radii_mm'][-1])<1e-7
e052=u052/2;e152=u152/1.5;theta52=math.atan2(tangent52@np.cross(e052,e152),e052@e152);D52=1.5*(.5+2*abs(theta52));dq52=1.05*D52/(L52*L52)
def off52(q):
 h=3*q*q-2*q*q*q;return (2-.5*h)*rot52(e052,tangent52,theta52*h)
normal52=np.cross(tangent52,[0,0,1.]);normal52/=np.linalg.norm(normal52);vertical52=np.cross(tangent52,normal52)
prisms52=[];intervals52=[]
for i in range(8):
 q0=i/8;q1=(i+1)/8;qm=(q0+q1)/2;u=off52(qm);E=D52*((q1-q0)/2+dq52);N=abs(u@normal52)+E+1.05;V=abs(u@vertical52)+E+1.05;p=a52+q0*(b52-a52)
 verts=[A.Vector(*(p+normal52*x+vertical52*z)) for x,z in [(-N,-V),(N,-V),(N,V),(-N,V),(-N,-V)]];s=Part.Face(Part.Wire(Part.makePolygon(verts).Edges)).extrude(A.Vector(*((b52-a52)*(q1-q0))));prisms52.append(s);intervals52.append(dict(q=[q0,q1],offset_Lipschitz=D52,profile_axial_parameter_error_upper=dq52,offset_error_upper=E,half_dimensions=[N,V]))
enclosure52=prisms52[0].multiFuse(prisms52[1:]);source52=Current35['Flat:MODULE:5'];tight52=source52.common(enclosure52);assert tight52.isValid() and len(tight52.Solids)==1
missing52=tight52.cut(source52);g52,w52,_=tight52.distToShape(W37parts['west_bank_gap_column'])
# Critical column interval and conservative horizontal offset bound; no sampling proof.
col52=W37parts['west_bank_gap_column'].BoundBox;lo=np.array([col52.XMin,col52.YMin]);hi=np.array([col52.XMax,col52.YMax]);dxy=(b52-a52)[:2];breaks=[0.,1.]
for k in range(2):
 for v in [lo[k],hi[k]]:
  q=(v-a52[k])/dxy[k]
  if 0<q<1:breaks.append(float(q))
breaks=sorted(breaks);test=list(breaks)
for q0,q1 in zip(breaks[:-1],breaks[1:]):
 qm=(q0+q1)/2;p=a52[:2]+qm*dxy;target=np.minimum(np.maximum(p,lo),hi);mask=(p<lo)|(p>hi)
 if np.dot(dxy[mask],dxy[mask])>0:
  q=float(-np.dot((a52[:2]-target)[mask],dxy[mask])/np.dot(dxy[mask],dxy[mask]));test.append(min(q1,max(q0,q)))
axisgap52=min(float(np.linalg.norm((a52[:2]+q*dxy)-np.minimum(np.maximum(a52[:2]+q*dxy,lo),hi))) for q in test)
qlo=0.;qhi=1.
for k in range(2):
 qx=sorted([(lo[k]-4.3-a52[k])/dxy[k],(hi[k]+4.3-a52[k])/dxy[k]]);qlo=max(qlo,qx[0]);qhi=min(qhi,qx[1])
hmin=3*qlo*qlo-2*qlo*qlo*qlo;rmax=2-.5*hmin;offxyupper=rmax*(float(np.linalg.norm(e152[:2]))+2*math.sin(abs(theta52)*(1-hmin)/2));analyticgap=axisgap52-offxyupper-1.05
assert missing52.Volume<1e-7 and g52>=1.25-1e-7 and analyticgap>=1.25-1e-7
joins52=[dict(other=n,gap_mm=tight52.distToShape(Current35[n])[0]) for n in ['Flat:MODULE:4','Flat:MODULE:6']]
ar52=OUT/'day07-MODULE-two-profile-twist-capacity.breps.zip';assert not ar52.exists();raw=tight52.exportBrepToString().encode();ge52=dict(name='MODULE5:connected_full_two_profile_twist_region',entry='0.brep',sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(tight52))
with zipfile.ZipFile(ar52,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('0.brep',raw);z.writestr('manifest.json',(json.dumps(dict(geometry=[ge52],scope='Connected occupied two-full2.1 profile region, not two new exactwire models; subset of existing round3.05 field'),indent=2)+'\n').encode())
r52=dict(id='day07-MODULE-two-profile-twist-capacity-receipt',status='ORIGINAL_MODULE_CAPACITY_HOLD_CLOSED_SCOPED',selected=False,N01_complete=False,
 original_hold=dict(region='Flat:MODULE:5',old_round_capacity_radius_mm=3.05,old_gap_mm=1.0257060169020848,not_physical_wirecontact=True),
 current_region=dict(whole_connected=True,valid=True,solids=1,subset_old_field_missing_volume_mm3=missing52.Volume,column_gap_mm=g52,required_foreign_mm=1.25,witnesses=[[list(a),list(b)] for a,b in w52[:1]],portal_joins=joins52,full_profile_diameter_each_mm=2.1,nominal_OD_each_mm=1.85),
 constructive_definition=dict(axis_row=rows52[5],start_pair_offset_mm=u052.tolist(),end_pair_offset_mm=u152.tolist(),offset_law='r=2-.5h, e=rotate(e0,t,theta*h), h=3q^2-2q^3; symmetric +- centreoffsets, full radius1.05 each',theta_rad=theta52,profile_containment='Prism coordinates include full radius1.05 plus Lipschitz offset variation AND axial error from actual tilted per-core tangent; intersecting oldradius3.05 doesnot remove either tube: r<=2 and fullradius1.05, endpoints havehprime0; axialspill bound1.05*6*(.5+2abs(theta))/L²<1. Each interval centre may differ by at most dq. No sampledwire collision pass.',axial_no_end_spill_coefficient=1.05*6*(.5+2*abs(theta52))/(L52*L52),intervals=intervals52),
 analytic_clearance=dict(column_axis_xy_gap_mm=axisgap52,critical_axis_q_interval=[qlo,qhi],horizontal_pair_offset_upper_mm=offxyupper,all_interval_surface_gap_lower_mm=analyticgap,method='Outside expandedcolumnXY4.3, oldradius3.05 has>=1.25. Inside interval use exact axis-to-rectangle quadratic minimum and angular endpoint deviation bound for full2.1 profiles; no freewire pose assumption.'),
 whole_factory=dict(XP03_module_required_upper_mm=199.17616758692503,XP02_module_required_upper_mm=213.55265253548615,min_each_mm=220,individual_residual_lower_mm=[20.823832413074967,6.447347464513854],source_analytic_proof_reused=pr52['module_each_core'],all_axes_bends_ends_prefixes_and_factory_debits_UNCHANGED=True,min_arc_core_R_mm=13.5,twist_R_lower_mm=59.38067018007507,no_pool_trim_extra9=True,other_SOURCE_units='211.811106/160.659660 of independent220 unchanged; not borrowed.'),
 assembly='Hand-lay both full leads through existing open shared Cguide before FHYcase/dock tying. Same received source ports/full9 and paired ends, same smoothstep witness and group lengths. New analytical occupiedregion replaces only the old oversized roundtwist field; all unchanged source foreign evidence reusable by actualsubset proof.',
 archive=ar52.name,archive_sha256=hashlib.sha256(ar52.read_bytes()).hexdigest(),geometry=[ge52],operation_seconds=time.monotonic()-t52,process_cpu_seconds=time.process_time()-c52)
p52=OUT/'day07-MODULE-two-profile-twist-capacity-receipt.json';assert not p52.exists();p52.write_bytes((json.dumps(r52,ensure_ascii=False,indent=2)+'\n').encode());print('MODULE52_CAPACITY',g52,analyticgap,joins52,r52['operation_seconds'],r52['process_cpu_seconds'],hashlib.sha256(p52.read_bytes()).hexdigest(),flush=True)
