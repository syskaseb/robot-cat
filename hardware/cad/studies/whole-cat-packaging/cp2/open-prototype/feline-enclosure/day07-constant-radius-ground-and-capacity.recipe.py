from pathlib import Path
import json,math,hashlib
out=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');p=out/'day07-SOURCE-constant-radius-axial-return-whole-proposal.json';d=json.loads(p.read_bytes())
def arclow(q,a,b,off,r,shift):
 T,N,B,R=q['T'],q['N'],q['B'],35.1;candidates=[a,b];v=math.atan2(-T[2],N[2])
 for t in [v%(2*math.pi),(v+math.pi)%(2*math.pi)]:
  if a<=t<=b:candidates.append(t)
 th=min(candidates,key=lambda t:math.sin(t)*T[2]-math.cos(t)*N[2]);u=math.sin(th)*T[2]-math.cos(th)*N[2];z=q['circle_centre'][2]+shift*T[2]+R*u+off*B[2]-r*math.sqrt(u*u+B[2]*B[2]);return dict(kind='TRANSLATED_FIRST_SEMICIRCLE' if shift else 'UNSHIFTED_REST_ARC',Zmin_mm=z,theta=th,translation_along_T_mm=shift)
def linelow(q,P,Q,tan,off,r,name):return dict(kind=name,Zmin_mm=min(P[2],Q[2])+off*q['B'][2]-r*math.sqrt(max(0,1-tan[2]**2)))
def allparts(q,dl,off,r):
 P,T,N,B,R=q['P'],q['T'],q['N'],q['B'],35.1;Pplus=[P[i]+dl*T[i] for i in range(3)];Pi=[P[i]+2*R*N[i] for i in range(3)];Piplus=[Pi[i]+dl*T[i] for i in range(3)];return [arclow(q,0,math.pi,off,r,dl),linelow(q,P,Pplus,T,off,r,'OUTWARD_AXIAL_STRAIGHT'),linelow(q,Pi,Piplus,T,off,r,'RETURN_AXIAL_STRAIGHT'),arclow(q,math.pi,q['theta_radians'],off,r,0),linelow(q,q['tangent_point'],q['Q'],q['end_tangent'],off,r,'FINAL_OLD_TANGENT')]
rows=[];first=None
for pi in range(36):
 for gi,g in enumerate(d['groups']):
  s=g['states'][pi];q=s['route'];floor=-168.3190155029297+s['body_drop_mm']
  for core,off,r in [('D',-2.75,1.55),('V',0,1),('G',2.75,1.55)]:
   parts=allparts(q,s['extension_mm'],off,r);z=min(parts,key=lambda t:t['Zmin_mm']);row=dict(pose=pi,group_index=gi,group=g['spec']['name'],core=core,profile_radius_mm=r,offset_B_mm=off,R_mm=35.1,extension_mm=s['extension_mm'],ground_bodyrelative_Z_mm=floor,required_margin_mm=1.25,full_profile_ground_lower_mm=z['Zmin_mm']-floor,minimum_piece=z,all_piece_minima=parts);rows.append(row)
   if row['full_profile_ground_lower_mm']<1.25-1e-7:first=row;break
  if first:break
 if first:break
capacity=[]
for g in d['groups']:
 limits=[]
 for s in g['states']:
  q=s['route'];floor=-168.3190155029297+s['body_drop_mm'];Tz=q['T'][2]
  if Tz>=-1e-10:continue
  for core,off,r in [('D',-2.75,1.55),('V',0,1),('G',2.75,1.55)]:
   # Variable parts only; unshiftedR35baselinepositive is separatelypreservednotcaseacceptance.
   z0=min(x['Zmin_mm'] for x in allparts(q,0,off,r)[:3]);maxd=(z0-floor-1.25)/(-Tz);maxL=q['centreline_mm']+2*maxd;limits.append(dict(pose=s['pose'],core=core,source_Tz=Tz,max_axial_extension_ground_only_mm=maxd,max_fixed_loop_length_ground_only_mm=maxL))
 if limits:
  lim=min(limits,key=lambda q:q['max_fixed_loop_length_ground_only_mm']);maxbase=max(s['route']['centreline_mm'] for s in g['states']);maxextra=lim['max_fixed_loop_length_ground_only_mm']-maxbase;capacity.append(dict(group=g['spec']['name'],limiting=lim,max_extra_above_max_base_ground_ONLY_mm=maxextra,planned_extra_mm=g['spec']['reserve'],minimum_extra_must_move_OUT_OF_THIS_BAY_mm=max(0,g['spec']['reserve']-maxextra),scope='Conditionalfloor-onlyupperbound, notavailablecase/coallocationstorage/physicalwirestockshortage. No reduction/waiverof55/10.'))
 else:capacity.append(dict(group=g['spec']['name'],max_extra_above_max_base_ground_ONLY_mm=None,scope='No finitegroundboundfromhorizontalT, NOTunlimitedaccessiblecapacity.',planned_extra_mm=g['spec']['reserve']))
r=dict(id='day07-SOURCE-constant-radius-axial-storage-ground-gate',status='CONSTANT_R_AXIAL_STORAGE_FULL_RESERVED_PROFILE_FLOOR_HOLD' if first else 'CONSTANT_R_AXIAL_FULL_PROFILE_FLOOR_RECEIVED_ONLY',proposal=p.name,proposal_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),first_falsifier=first,received_rows=rows,cursor=len(rows),total=324,unreceived=324-len(rows),conditional_storage_capacity=capacity,first_falsifier_stops_case_Ankle_otherground_rows=True,actual_A_U_minimum_fit_slack=None,selected=False,N01_complete=False,meaning='Samefull55/10 inR35.1fixedsemicircle+twoSTRAIGHTlegs, distinctfromradiusgrowth; nominalsourceoutwardTlateposehasdownwardcomponent. FalsifiesTHISsource-forwardplanarstorageallocation only. No all3Dimpossibility/actualdeliveredwirecontact/stockshortage/minRrejection. Sourcecase/Ankle/otherhardware+branchpackingremainUNRECEIVED.')
p2=out/'day07-SOURCE-constant-radius-axial-storage-ground-gate.json';assert not p2.exists();p2.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(dict(first=first,cursor=len(rows),unreceived=324-len(rows),capacity=capacity,sha256=hashlib.sha256(p2.read_bytes()).hexdigest()),indent=2))
