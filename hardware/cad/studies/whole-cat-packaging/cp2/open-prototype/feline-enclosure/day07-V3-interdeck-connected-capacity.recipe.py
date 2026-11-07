import time,json,hashlib,zipfile,math,os
t53=time.monotonic();c53=time.process_time();oldV53=CurrentCanon31['current_foreign_common_bank_V_functional_space']['recipes']
def line53(a,b):
 a=np.array(a,float);b=np.array(b,float);return dict(kind='line',start=a.tolist(),end=b.tolist(),length_mm=float(np.linalg.norm(b-a)))
def arc53(a,t,u,R,angle):
 a=np.array(a,float);t=np.array(t,float);u=np.array(u,float);p=a+R*(math.sin(angle)*t+(1-math.cos(angle))*u);m=a+R*(math.sin(angle/2)*t+(1-math.cos(angle/2))*u)
 return dict(kind='arc',start=a.tolist(),mid=m.tolist(),end=p.tolist(),radius_mm=R,length_mm=R*angle),p,math.cos(angle)*t+math.sin(angle)*u
def S53(a,b,t):
 a=np.array(a,float);b=np.array(b,float);t=np.array(t,float);v=b-a;run=v@t;h=v-run*t;H=np.linalg.norm(h);u=h/H;theta=2*math.atan2(H,run);R=(run*run+H*H)/(4*H);one,p,nt=arc53(a,t,u,R,theta);two,p,nt=arc53(p,nt,math.sin(theta)*t-math.cos(theta)*u,R,theta);assert np.linalg.norm(p-b)<1e-6;return [one,two],R
def path53(rows):return Part.Wire([Part.makeLine(A.Vector(*r['start']),A.Vector(*r['end'])) if r['kind']=='line' else Part.Arc(A.Vector(*r['start']),A.Vector(*r['mid']),A.Vector(*r['end'])).toShape() for r in rows])
def pipe53(rows,r):
 w=path53(rows);t=w.Edges[0].tangentAt(w.Edges[0].FirstParameter);return w.makePipeShell([Part.Wire([Part.makeCircle(r,A.Vector(*rows[0]['start']),t)])],True,False)
Rprofile53=math.hypot(1.4,3.6)
commonS53,Rs53=S53([-74.55,95.1,66.75],[-33.6,90.2,45.26],[1,0,0]);a,p,t=arc53(commonS53[-1]['end'],[1,0,0],[0,-1,0],14.6,math.pi/2);common53=commonS53+[a,line53(p,[-19,36.5,45.26])]
p0=np.array(commonS53[0]['start']);vs=[A.Vector(*(p0+np.array([0,y,z]))) for y,z in [(-1.4,-3.6),(1.4,-3.6),(1.4,3.6),(-1.4,3.6),(-1.4,-3.6)]]
leading53=path53(commonS53).makePipeShell([Part.Wire(Part.makePolygon(vs).Edges)],True,False);round53=pipe53(common53[2:],Rprofile53);commonshape53=leading53.fuse(round53);assert commonshape53.isValid() and len(commonshape53.Solids)==1
branches53={};recipes53={}
for n in ['W020','W024']:
 old=oldV53[n]['parts'];rows=[dict(r) for r in old[:3]];p=np.array(rows[-1]['end']);t=np.array([1.,0,0]) if n=='W020' else np.array([-1.,0,0]);a,p,t=arc53(p,t,[0,1,0],12.4,math.pi/2);rows.append(a);p2=p.copy();p2[1]=13.65;rows.append(line53(p,p2));end=[-19,36.5,47.46 if n=='W020' else 43.06];ss,RR=S53(p2,end,[0,1,0]);assert RR>=12.4;rows+=ss;recipes53[n]=dict(parts=rows,join=end,old_local_branch_mm=oldV53[n]['length_mm'],new_local_branch_mm=sum(r['length_mm'] for r in rows),minimum_R_mm=min(r['radius_mm'] for r in rows if r['kind']=='arc'),full_source9_unchanged=True);branches53[n+':occupied_branch_region']=pipe53(rows[1:],1.4)
old=oldV53['W022']['parts'];rows=[dict(r) for r in old[:4]];p=rows[-1]['end'];a,p,t=arc53(p,[0,1,0],[-1,0,0],12.4,math.pi/2);rows.append(a);p2=np.array([-7.1,p[1],p[2]]);rows.append(line53(p,p2));ss,RR=S53(p2,[-29.6,p[1],45.26],[-1,0,0]);assert RR>=12.4;rows+=ss;p=np.array(rows[-1]['end']);a,p,t=arc53(p,[-1,0,0],[0,1,0],12.4,math.pi/2);rows.append(a);ss,RR=S53(p,[-19,61,45.26],[0,1,0]);assert RR>=12.4;rows+=ss;recipes53['W022']=dict(parts=rows,join=[-19,61,45.26],old_local_branch_mm=oldV53['W022']['length_mm'],new_local_branch_mm=sum(r['length_mm'] for r in rows),minimum_R_mm=min(r['radius_mm'] for r in rows if r['kind']=='arc'),full_source9_unchanged=True);branches53['W022:occupied_branch_region']=pipe53(rows[1:],1.4)
new53={'V3:common_connected_lower_region':commonshape53,**branches53}
for s in new53.values():assert s.isValid() and len(s.Solids)==1
proposal53=dict(id='day07-V3-interdeck-connected-capacity-proposal',status='ONE_CAUSAL_UNDERBANK_COMMON_REGION_PRECHECK',selected=False,N01_complete=False,
 unchanged_column_bounds=saved_bounds(W37parts['west_bank_gap_column']),source_9mm_and_original3_grip_roots_stock_unchanged=True,
 region_strategy='Keep original3full2.0cores/.2spacing/.4outer margins. Incoming rectangle2.8x7.2 descends on north open side; below bank use full rotation-enclosing radius hypot(1.4,3.6), not a shrunken cable. WestunderbankX-19/Z45.26 passes column; no new terminal/9 at computational joins. MODULE5 upperregion separately remains source2.1profiles/stock unchanged; no shared volume credited twice.',
 old_narrow_slot=dict(housing_left_Xmax=-15.5,housing_right_Xmin=-6.5,column_X=[-13.5,-9.5],remaining_left_mm=2.,remaining_right_mm=3.,required_for_old2p8_plus_foreign_mm=5.3),
 common=dict(parts=common53,incoming_rect_mm=[2.8,7.2],lower_rotation_enclosing_R_mm=Rprofile53,lower_z_mm=45.26,lower_X_mm=-19,leading_S_R_mm=Rs53,worst_core_centre_R_lower_mm=min(Rs53,14.6)-2.2,local_core_count='3 from incoming toY61; W022 peels atY61, W020/W024 continue toY36.5. Region may retain generous full3profile beyond peel, not a second stockdebit.',computed_centre_length_mm=sum(r['length_mm'] for r in common53)),branches=recipes53,
 stock_scope='W020/W022/W024 selected SOURCE/FL1/FL2/FL3 and donorFL3 roles from900/MAX3contract retained. New localbranch/common contributions explicit; complete other-end/whole900 blank fits not invented. No source900 credit to independent MODULE225. FourMODULE/SOURCE220 unchanged. This region proposal is not whole-length acceptance.',
 retention='Original3bank full9/clamps/printed roots and actual bankpads retained. Old middle looseguide is only an intermediate guide; its sourcefunction/stock must be reallocated to a root-connected open pass if this region passes. No new9/case/terminal at the changed seams; no retirement of actual ends by name.',
 assembly='Lay fullconnected U1/wirekit through accessible lower common passage from openwest before closing source looseguides and before removablePi carrier; purchased ends not dragged through narrow closed holes. Finalguide/root/access proof required before acceptance.',
 first_falsifier='Full occupiedregional profiles vs all realcurrentcase/stock/roots around F_PI/P_SYS/TE and unchanged westcolumn. Old3printed V receiver root arms remainactualoperands, not silently deleted. Stop first unmet1.25; region overlap is allocationHOLD, not actualwirecontact.')
pp53=OUT/'day07-V3-interdeck-connected-capacity-proposal.json';assert not pp53.exists();pp53.write_bytes((json.dumps(proposal53,ensure_ascii=False,indent=2)+'\n').encode())
fixed53={n:s for n,s in Current35.items() if n!='V:common_region' and not any(n.startswith(w+':') for w in ['W020','W022','W024'])};fixed53.update({'C1:'+n:s for n,s in W37parts.items()})
tasks53=[]
for n,s in new53.items():
 for k,q in fixed53.items():
  if bbox_lower_bound(s.BoundBox,q.BoundBox)<=1.25:tasks53.append((n,k))
tasks53.sort(key=lambda p:(0 if p[0].startswith('W020') and ('support' in p[1] or 'root' in p[1]) else 1 if p[1].startswith('F_PI:') else 2 if p[1].startswith('Station:P_SYS:') else 3,p))
rr53=[];stop53=None
for n,k in tasks53:
 s,q=new53[n],fixed53[k];r=dict(a=n,b=k,a_valid=s.isValid(),b_valid=q.isValid())
 if k.startswith(('Flat:MODULE:','Underdeck:SOURCE:')):r['status']='OTHER_FLEXIBLE_REGION_CAPACITY_DEPENDENCY_NOT_RIGIDCONTACT'
 elif r['a_valid'] and r['b_valid']:
  g,w,_=s.distToShape(q);r.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in w[:1]])
  if g<1e-7:
   co=s.common(q);r.update(common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None)
  r['status']='FULL_ALLOCATED_REGION_SEPARATED125' if g>=1.25-1e-7 else 'V3_ALLOCATED_REGION_HOLD_NOT_PHYSICAL_WIRECONTACT'
 else:r['status']='INVALID_SOURCE_UNRESOLVED_NOT_CONTACT'
 rr53.append(r)
 if r['status']=='V3_ALLOCATED_REGION_HOLD_NOT_PHYSICAL_WIRECONTACT':stop53=r;break
 if time.monotonic()-t53>45:break
ar53=OUT/'day07-V3-interdeck-connected-capacity-first-gate.breps.zip';assert not ar53.exists();ge53=[]
with zipfile.ZipFile(ar53,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(list(new53.items())+[(n,fixed53[n]) for n in sorted({r['b'] for r in rr53})]):
  raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge53.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge53,scope='One connected V3 regional hypothesis; not fixed-wire CAD or selectedwholelayout'),indent=2)+'\n').encode())
r53=dict(id='day07-V3-interdeck-connected-capacity-first-gate',status='V3_REGION_FIRST_FIXED_HOLD' if stop53 else 'V3_REGIONAL_PREFLIGHT_RECEIVED_SCOPED' if len(rr53)==len(tasks53) else 'V3_BOUNDED_PREFLIGHT_PENDING',rows=rr53,cursor=len(rr53),total=len(tasks53),unreceived=len(tasks53)-len(rr53),stop=stop53,proposal=pp53.name,proposal_sha256=hashlib.sha256(pp53.read_bytes()).hexdigest(),archive=ar53.name,archive_sha256=hashlib.sha256(ar53.read_bytes()).hexdigest(),geometry=ge53,operation_seconds=time.monotonic()-t53,process_cpu_seconds=time.process_time()-c53,selected=False,N01_complete=False,original_V_hold_NOT_closed_yet=True)
p53=OUT/'day07-V3-interdeck-connected-capacity-first-gate.json';assert not p53.exists();p53.write_bytes((json.dumps(r53,ensure_ascii=False,indent=2)+'\n').encode());print('V53_FIRST',r53['status'],len(rr53),len(tasks53),stop53,r53['operation_seconds'],r53['process_cpu_seconds'],hashlib.sha256(p53.read_bytes()).hexdigest(),flush=True)
