from pathlib import Path
import json,math,hashlib,datetime
out=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');p=out/'day07-SOURCE-left-entry-adaptive-long-loop-whole-proposal.json';d=json.loads(p.read_bytes())
def plus(a,b):return [x+y for x,y in zip(a,b)]
def mult(a,s):return [x*s for x in a]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def profile_low(q,offset,r):
 T,N,B,R,th=q['T'],q['N'],q['B'],q['R_mm'],q['theta_radians'];angles=[0,th];v=math.atan2(-T[2],N[2]);angles += [a for a in [v%(2*math.pi),(v+math.pi)%(2*math.pi)] if 0<=a<=th]
 z=min(angles,key=lambda a:math.sin(a)*T[2]-math.cos(a)*N[2]);rd=plus(mult(T,math.sin(z)),mult(N,-math.cos(z)));C=plus(q['circle_centre'],mult(rd,R));extent=r*math.sqrt(rd[2]**2+B[2]**2);arc=C[2]+offset*B[2]-extent
 rdEnd=plus(mult(T,math.sin(th)),mult(N,-math.cos(th)));straight=min(q['tangent_point'][2],q['Q'][2])+offset*B[2]-r*math.sqrt(rdEnd[2]**2+B[2]**2)
 return dict(kind='ARC' if arc<=straight else 'STRAIGHT',centreline_theta=z,full_profile_Zmin_mm=min(arc,straight),offset_B_mm=offset,profile_radius_mm=r)
rows=[];first=None
for pi in range(36):
 for gi,g in enumerate(d['groups']):
  s=g['states'][pi];q=s['route'];floor=-168.3190155029297+s['lowest_full_profile']['body_drop_mm']
  for core,off,rr in [('D',-2.75,1.55),('V',0,1),('G',2.75,1.55)]:
   z=profile_low(q,off,rr);z.update(pose=pi,group=g['spec']['name'],group_index=gi,core=core,ground_bodyrelative_Z_mm=floor,full_reserved_profile_ground_lower_mm=z['full_profile_Zmin_mm']-floor,route_radius_mm=q['R_mm'],group_min_R_mm=35.1,axial_loop_mm=q['centreline_mm'],required_margin_mm=1.25);rows.append(z)
   if z['full_reserved_profile_ground_lower_mm']<1.25-1e-7:first=z;break
  if first:break
 if first:break
# Baseline minR is SAMEfamily/sourceposes, diagnostic ONLY notacceptedcase/space/slack route.
src=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat59-save-adaptive-loop-whole-proposal.py').read_text(encoding='utf-8-sig');ns={};exec(compile(src[:src.index('specs=[')],'metadata_route_definition','exec'),ns);base=[]
for g in d['groups']:
 lows=[]
 for s in g['states']:
  q=s['route'];b=ns['route'](q['P'],q['T'],q['Q'],35.1);floor=-168.3190155029297+s['lowest_full_profile']['body_drop_mm'];lows.extend(profile_low(b,off,rr)['full_profile_Zmin_mm']-floor for off,rr in [(-2.75,1.55),(0,1),(2.75,1.55)])
 base.append(dict(group=g['spec']['name'],minimum_full_profile_ground_lower_mm=min(lows),scope='MinR35.1groundONLY/no otherclearance/storage/fitacceptance',moving_centreline_demand_range_mm=[min(s['minimum_R_path_centreline_mm'] for s in g['states']),max(s['minimum_R_path_centreline_mm'] for s in g['states'])]))
r=dict(id='day07-SOURCE-adaptive-loop-ground-first-falsifier',status='RADIUS_STORAGE_TOPOLOGY_FULL_RESERVED_PROFILE_GROUND_HOLD' if first else 'GROUP_FULL_PROFILE_GROUND_RECEIVED_ONLY_CASES_STORAGE_OPEN',proposal=p.name,proposal_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),criterion='FULLreservedroundD/G3.1,V2 vs SAMEfrozenactualfloor+bodydrop, minimum1.25. RectanglecornerboundNOTtreatedwirecontact; roundprofilesdiagnoseactualallocatedfullprofile margin.',received_rows=rows,cursor=len(rows),total=324,unreceived=324-len(rows),first_falsifier=first,baseline_minR_ground_diagnostic=base,meaning='OnlychosenadaptiveC/Sfamilyconcentratingentire55/10plannedallowanceinradiusgrowth. NOTallR35.1loops, actualdeliveredwirefloorcontact, requiredphysicalslack55orstockshortage. Firstfalsifierstopsbeforecase/Ankle/otherposes/entryfanchecks.',all_current_A_U_minfit_slack=None,physical_cut=None,N01_complete=False,selected=False)
p2=out/'day07-SOURCE-adaptive-loop-ground-first-falsifier.json';assert not p2.exists();p2.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(dict(first=first,cursor=len(rows),unreceived=324-len(rows),baseline=base,sha256=hashlib.sha256(p2.read_bytes()).hexdigest()),indent=2))
