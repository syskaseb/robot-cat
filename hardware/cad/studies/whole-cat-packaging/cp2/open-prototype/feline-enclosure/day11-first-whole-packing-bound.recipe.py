from pathlib import Path
from datetime import datetime,timezone
import json,math,hashlib
out=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');p=out/'day11-WHOLE_N01-layout-architecture-and-closure-plan.json';a=json.loads(p.read_bytes());results=[];pitch=80/(2*math.pi);dz=3.3
for core,R,diam in [('D',40.6,3.1),('V',37.85,2.0),('G',35.1,3.1)]:
 lo=0;hi=.2
 for i in range(70):
  delta=(lo+hi)/2;der=R*R*math.sin(delta)+pitch*pitch*delta-pitch*dz
  if der<0:lo=delta
  else:hi=delta
 delta=(lo+hi)/2;theta=.6;theta2=theta+delta
 # Two actually selected finitehelix centreline points, NOT asserted globalminimaldistance.
 def pt(th,z):return [-94.9-R*math.cos(th),77-R*math.sin(th),z+pitch*th]
 P=pt(theta+delta,40.7);Q=pt(theta,44);dist=math.dist(P,Q);results.append(dict(core=core,Rxy=R,source_nominal_profile_diameter_mm=diam,required_gap_mm=.2,world_Z_row_pitch_mm=dz,theta0=theta,theta_delta=delta,P=P,Q=Q,actual_chosen_point_distance_mm=dist,necessary_allowed_distance_mm=diam+.2,chosen_distance_is_upper_bound_on_global_curve_gap=True,packing_necessary_failure=dist<diam+.2-1e-8,not_global_routed_length_or_contact_proof=True))
g=next(q for q in results if q['core']=='G');assert g['packing_necessary_failure'];r=dict(id='day11-whole-nine-dorsal-entry-first-packing-falsifier',status='FIRST_NECESSARY_WHOLE_OCCUPANCY_PACKING_HOLD_NO_SECOND_FAMILY',proposal=p.name,proposal_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),rows=results,meaning='SamecoreFL1/FL2 worldZseparation3.3 doesNOTpreserve3.1diameter+.2gap in pitched3Dentry. Explicitpoints onchosenGfinitehelices are closerthan3.3; sufficientnecessarypackingfalsifier, no need wholepathsolver or boughtpartscan. NominalwirecontactNOTclaimed; allphysicalparts/budgets unchanged. StopthisONEwholechosenentry-layer hypothesis beforeprintdetails.',actual_selected_stock_unchanged=True,all_actual_A_U_fit_slack_cut=None,no_new_material_or_second_geometry_family=True,N01_complete=False,written_utc=datetime.now(timezone.utc).isoformat());rp=out/(r['id']+'.json');assert not rp.exists();rp.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(rp.name,hashlib.sha256(rp.read_bytes()).hexdigest(),results)
