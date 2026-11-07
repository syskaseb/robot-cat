import time,json,hashlib,math,zipfile,os
t126=time.monotonic();c126=time.process_time();p126=OUT/'day07-SOURCE-receiver-layer-independent-U-reserve-whole-proposal.json';prop126=json.loads(p126.read_bytes());R126=35.1;xb126=84.6;dl126,dh126=prop126['family']['d_each_independent_mm'];fields126=[];parts126=[];members126=[]
def half126(r,h,x,z):
 sh=Part.makeCylinder(r,h,A.Vector(x,0,z),A.Vector(0,0,1),180);sh.rotate(A.Vector(x,0,z),A.Vector(0,0,1),-90);return sh
for br in prop126['branches']:
 name=br['DGV'];hw=br['capacity_cross_mm'][0]/2;z=br['Z_mm']-hw;h=2*hw;ca=xb126+dl126;cb=xb126+dh126
 # Exact union over ALL d: outer right-semidisk at maxcentre plus translated-centre strip, minus inner right-semidisk at mincentre.
 disk=half126(R126+hw,h,cb,z);strip=Part.makeBox(cb-ca,2*(R126+hw),h,A.Vector(ca,-R126-hw,z));outer=disk.fuse(strip);inner=half126(R126-hw,h+.2,ca,z-.1);arc=outer.cut(inner)
 a=Part.makeBox(dh126+2*hw,2*hw,h,A.Vector(xb126-hw,-R126-hw,z));b=Part.makeBox(dh126+2*hw,2*hw,h,A.Vector(xb126-hw,R126-hw,z));whole=arc.fuse(a).fuse(b);assert whole.isValid() and len(whole.Solids)==1
 for label,sh in [('FULL_VARIABLE_U_ARC',arc),('FULL_INLET_STRAIGHT',a),('FULL_RETURN_STRAIGHT',b)]:
  loss=sh.cut(whole);assert loss.isValid() and loss.Volume<1e-6;members126.append(dict(branch=name,member=label,missing_mm3=loss.Volume));parts126.append((name+':'+label,sh))
 fields126.append((name,whole))
tasks126=[];bounds126={k:v.BoundBox for k,v in ctx121.items()}
for name,sh in fields126:
 bb=sh.optimalBoundingBox(False,False)
 for k,v in ctx121.items():
  if bbox_lower_bound(bb,bounds126[k])<1.25:tasks126.append((name,k))
tasks126.sort(key=lambda q:(0 if q[1]=='Underdeck:RestoredBank' else 1 if q[1].endswith(':case') or 'Housing' in q[1] else 2,q));look126=dict(fields126);rows126=[];first126=None
for name,k in tasks126:
 sh=look126[name];v=ctx121[k];row=dict(branch=name,other=k,field_valid=sh.isValid(),source_valid=v.isValid())
 if row['source_valid']:
  gap,ww,_=sh.distToShape(v);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='FULL_CAPACITY_SEPARATED125' if gap>=1.25-1e-7 else 'ALLOCATED_REGION_HOLD_FUNCTION_PENDING_NOT_WIRECONTACT')
 else:row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
 rows126.append(row)
 if row['status']!='FULL_CAPACITY_SEPARATED125':first126=row;break
 if time.monotonic()-t126>18:break
ar126=OUT/'day07-SOURCE-receiver-U-body-capacity-first.breps.zip';assert not ar126.exists();geo126=[]
items126=fields126+parts126
if first126:items126.append(('FIRST_CURRENT_NEIGHBOR',ctx121[first126['other']]))
with zipfile.ZipFile(ar126,'w',zipfile.ZIP_DEFLATED) as zz:
 for i,(n,sh) in enumerate(items126):
  raw=sh.exportBrepToString().encode();e=str(i)+'.brep';zz.writestr(e,raw);geo126.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),valid=sh.isValid(),volume_mm3=sh.Volume,bounds_mm=saved_bounds(sh)))
 zz.writestr('manifest.json',(json.dumps(dict(geometry=geo126),indent=2)+'\n').encode())
r126=dict(id='day07-SOURCE-receiver-U-body-capacity-first',status='RECEIVER_U_ALLOCATION_FIRST_HOLD_FUNCTION_PENDING' if first126 else 'RECEIVER_U_STATIC_PENDING' if len(rows126)<len(tasks126) else 'RECEIVER_U_STATIC_SCOPE_RECEIVED',proposal=p126.name,proposal_sha256=hashlib.sha256(p126.read_bytes()).hexdigest(),rows=rows126,cursor=len(rows126),total=len(tasks126),unreceived=len(tasks126)-len(rows126),first_falsifier=first126,whole3fields_member_coverage=members126,exact_continuous_family='ForrightannularhalfUtranslatedalongX[dlo,dhi], OUTER=maxcentrehalfdisc+centrestrip; subtractINNER=mincentrehalfdisc. ExactunionALLd forfixedR/fullrectangularprofile, not sampledfillfactor/bbox. Straightlegsfullintervalcovered. Independentd foreachcore.',archive=ar126.name,archive_sha256=hashlib.sha256(ar126.read_bytes()).hexdigest(),geometry=geo126,new_material=False,new_leg_geometry=False,all_current_A_U_minfit_slack=None,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t126,process_cpu_seconds=time.process_time()-c126,pid=os.getpid(),session_id=46493)
q126=OUT/'day07-SOURCE-receiver-U-body-capacity-first.json';assert not q126.exists();q126.write_bytes((json.dumps(r126,indent=2)+'\n').encode());print('BODY126',r126['status'],len(rows126),len(tasks126),first126,'wall',r126['operation_seconds'],'CPU',r126['process_cpu_seconds'],flush=True);print('OWNER63_IDLE',os.getpid(),flush=True)
