from pathlib import Path
from datetime import datetime,timezone
import json,math,hashlib,os
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ports=json.loads((out/'day07-SOURCE-new-moving-module-region-first-gate.json').read_bytes())['new_port_frame_rows36'];dot=lambda a,b:sum(x*y for x,y in zip(a,b));add=lambda a,b:[x+y for x,y in zip(a,b)];sub=lambda a,b:[x-y for x,y in zip(a,b)];mul=lambda a,t:[x*t for x in a];norm=lambda a:math.sqrt(dot(a,a));unit=lambda a:mul(a,1/norm(a));cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def route(P,T,Q,R):
 T=unit(T);d=sub(Q,P);perp=sub(d,mul(T,dot(d,T)));N=mul(unit(perp),-1);B=unit(cross(T,N));a=dot(d,T);b=dot(d,N);ll=math.hypot(a,R-b);alpha=math.atan2(a,R-b);ang=math.acos(max(-1,min(1,R/ll)));valid=[]
 for th in [(alpha-ang)%(2*math.pi),(alpha+ang)%(2*math.pi)]:
  W=add(P,add(mul(T,R*math.sin(th)),mul(N,R*(1-math.cos(th)))));endT=add(mul(T,math.cos(th)),mul(N,math.sin(th)));tail=dot(sub(Q,W),endT);res=norm(sub(sub(Q,W),mul(endT,tail)))
  if tail>=-1e-7 and res<1e-6:valid.append((th,tail,W,endT))
 assert len(valid)==1,(valid,P,T,Q,R);th,tail,W,endT=valid[0];assert th>math.pi
 return dict(P=P,T=T,Q=Q,N=N,B=B,R_mm=R,theta_radians=th,theta_degrees=math.degrees(th),tangent_point=W,end_tangent=endT,straight_mm=tail,centreline_mm=R*th+tail,circle_centre=add(P,mul(N,R)))
def lowest(q,width=9.4,depth=3.9):
 P,T,N,B,R,th=q['P'],q['T'],q['N'],q['B'],q['R_mm'],q['theta_radians'];cands=[0,th];base=math.atan2(-T[2],N[2])
 for z in [base%(2*math.pi),(base+math.pi)%(2*math.pi)]:
  if 0<=z<=th:cands.append(z)
 best=None
 for z in cands:
  rd=add(mul(T,math.sin(z)),mul(N,-math.cos(z)));C=add(P,add(mul(T,R*math.sin(z)),mul(N,R*(1-math.cos(z)))));point=add(C,add(mul(rd,-depth/2*(1 if rd[2]>=0 else -1)),mul(B,-width/2*(1 if B[2]>=0 else -1))))
  if best is None or point[2]<best['point'][2]:best=dict(kind='ARC_FULL_RECT_PROFILE',theta=z,point=point)
 rd=add(mul(T,math.sin(th)),mul(N,-math.cos(th)))
 for C in [q['tangent_point'],q['Q']]:
  point=add(C,add(mul(rd,-depth/2*(1 if rd[2]>=0 else -1)),mul(B,-width/2*(1 if B[2]>=0 else -1))))
  if point[2]<best['point'][2]:best=dict(kind='STRAIGHT_FULL_RECT_PROFILE',point=point)
 return best
specs=[dict(name='HIP3_SOURCE_FL1',ids=['W004','W020','W019'],Q=[-132.75,39.25,40.7],reserve=10,source_index=0),dict(name='KNEE3_CONTINUOUS_FL2',ids=['W005','W022','W021'],Q=[-132.75,77,44],reserve=55,source_index=1),dict(name='KNEE3_DONOR_FL3',ids=['W006','W024','W023'],Q=[-132.75,77,47.3],reserve=55,source_index=None)]
allgroups=[]
for sp in specs:
 base=[]
 for p in ports:
  if sp['source_index'] is None:P=p['Knee_exit_world_mm'];T=p['Knee_exit_tangent']
  else:q=p['source_origins'][sp['source_index']];P=q['nominal_source14_outer_world_mm'];T=q['nominal_departure_world']
  base.append(route(P,T,sp['Q'],35.1))
 fixedL=max(q['centreline_mm'] for q in base)+sp['reserve'];states=[]
 for p,q in zip(ports,base):
  lo=35.1;hi=35.1+max(1,(fixedL-q['centreline_mm'])/math.pi)
  assert route(q['P'],q['T'],q['Q'],hi)['centreline_mm']>=fixedL-1e-6
  # Invert ONEdefinedlong-loop length forconstant material/space planning, NOTclearance/pose/Rsearch.
  for _ in range(38):
   mid=(lo+hi)/2
   if route(q['P'],q['T'],q['Q'],mid)['centreline_mm']<fixedL:lo=mid
   else:hi=mid
  x=route(q['P'],q['T'],q['Q'],hi);assert abs(x['centreline_mm']-fixedL)<1e-6;z=lowest(x);z.update(conservative_profile_ground_lower_mm=z['point'][2]-p['body_drop_mm']+168.3190155029297,body_drop_mm=p['body_drop_mm']);states.append(dict(pose=p['pose'],minimum_R_path_centreline_mm=q['centreline_mm'],allocated_fixed_loop_centreline_mm=fixedL,radius_from_fixed_length_ONLY=x['R_mm'],route=x,lowest_full_profile=z))
 allgroups.append(dict(spec=sp,full_triplet_cross_mm=[9.4,3.9],group_min_R_mm=35.1,loop_axial_allocation_mm=fixedL,source14_prefix_and_bodyfans_NOT_included=True,states=states))
p=out/'day07-SOURCE-left-entry-adaptive-long-loop-whole-proposal.json';assert not p.exists();r=dict(id=p.stem,status='ONE_ADAPTIVE_EXTERNAL_LONG_RETURN_GROUP_FAMILY_GROUND_FIRST',selected=False,N01_complete=False,cause='Actualleftbodypassageclosed. Preserveexistingall3source14nominalframes+FL3holderexit, chooseexternalAWAYturn(longarc>180)+straighttotrueleftpassage. No forcedYterminal/no quarter/noshorterR. ThreeFULLtripletregions with6KneecorescoallocatedONLYifunionpackingproved; no123wireaxes.',family='PerposeoneC/Sgroup-region plane definedbyactualstartT andbodytarget, curvature>=35.1. IncreaseRONLYascontinuousshapechange tostorefixedaxialloopallocation maxrequiredR35p1length +planned55/10reserve. Scalarinversionislengthidentitynotclearancetuning/designvariant. Exactphysicalpercoretotalfit/slack remainsNULL untilspace/roll/fans/currentends qualify.',groups=allgroups,first_hazard='FULLactualreservedtripletprofilegroundvsfrozenbodydrop/ground; thencriticalactualcase/Ankle/head/P0/fullcurrentneighbors. Firstfalsifierstopsbranch; no unsupportedlegexposure/bodyoutlinewaiver. LongloopsareMOVINGexternalfieldsnotfixedBodyOuterpassage, separateexposure/actualmechanicalscope remainsOPEN.',required_frozen_ground_z_mm=-168.3190155029297,group_binormal_width_mm=9.4,radial_depth_mm=3.9,fullreserved_profiles='D/G3.1,V2/.2gaps/.4margin ineachflat3; perpwidth9.4/depth3.9, allcoresminR12.4 preserved. No OD shrink/boughtstockchange.',assembly='ConnectedSOURCEKneekit+full4movingtiespreserved; handlaythreegroupregionsbeforebodyclosures, fullfactoryplugscasesunchanged, mergeaccountingnotterminal. Bodypassage9fieldretained; prospectiveguideloadroot/materialNOTbuilt. No virtualunsolder/physicalcut/newsplice.',all9_12portions4MAX3_A_U_minimum_fit_slack=None,known_stock_guards='Source14terminal11full9lap4once/3x8/3x20/stagger2x9/850project/900ceil5(min+20)MAX3 perphysicalunit/actualcutNULL; four220/both4MTA unchanged. Computedgroup-loopLNOTwholewirefit oroldprefixcredit.',source_pins=[dict(path=n,sha256=sha(out/n)) for n in ['day07-SOURCE-left-end-body-passage-bounded-disposition.json','day07-SOURCE-new-moving-module-region-first-gate.json','day07-SOURCE-new-motion-frozen-input-projection.json','day07-whole-physical-SOURCE-approach-Knee-link-proposal.json','day07-coordinator-SOURCE-splice-layout-authority-receipt.json']],written_utc=datetime.now(timezone.utc).isoformat());p.write_bytes((json.dumps(r,indent=2)+'\n').encode());print('PROPOSAL116',sha(p));print([(g['spec']['name'],g['loop_axial_allocation_mm'],min(s['lowest_full_profile']['conservative_profile_ground_lower_mm'] for s in g['states'])) for g in allgroups])
card=root/'hardware/HOBBY_COMPLETION_PLAN.md';raw=card.read_bytes();i=raw.index(b'## Historia poprzednich okien');s=raw[:i].decode();j=s.index('\n',s.index('## Bieżąca'))+1;s=s[:j]+'\nSOURCE_ADAPTIVE_LOOP_PROPOSAL: '+p.name+' SHA'+sha(p)+'. ONEexternalAWAYlongarc+straightperactual36sourceframes→closedleftbodypassage; FULL3tripletfields9.4x3.9/R>=35.1 varyingbyfixedaxiallength(maxR35length+55/10reserve), notclearancetuning/123axes/fixedwireforallposes. FIRSTexactfullprofileground/frozenbodydrop thenactualcase/Ankle. Wholefree-space/exposure/roll/prefix/bodyfan/stockfitunqualified; no newmaterial/oldmotionreplay.\n'+s[j:];assert card.read_bytes()==raw;q=card.with_suffix('.owner59proposal.tmp');q.write_bytes(s.encode()+raw[i:]);os.replace(q,card)
