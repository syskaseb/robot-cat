import time,json,hashlib,zipfile,math,os
st161=time.monotonic();cp161=time.process_time();cells161=[];bounds161=[]
for b in pr160['six_independent_storage_branches']:
 n=b['wire'];y=b['plane_Y_mm'];r=b['profile_radius_mm']+.4;shift=5.;zc=zc160
 for i in range(36):
  a=i*math.pi/36;bb=(i+1)*math.pi/36;sn=[math.sin(a),math.sin(bb)]+([1.] if a<=math.pi/2<=bb else []);xs=[xc160-R160*math.cos(a),xc160-R160*math.cos(bb)];lo=[min(xs)-r,y-r,zc-R160*max(sn)-shift-r];hi=[max(xs)+r,y+r,zc-R160*min(sn)+r];s=box153([lo,hi]);cells161.append((n+':ARC_INTERVAL:'+str(i),s));bounds161.append(dict(name=cells161[-1][0],wire=n,angle_radians=[a,bb],bounds_mm=[lo,hi],source_relation='EveryE55..65arc centre is sameR35.1 semicircle translateddown0..5; growanalyticXYZintervalr containsALLfullcircularprofiles, no fillfactor/samplingassumption.'))
 for side in [-1,1]:
  x=xc160+side*R160;lo=[x-r,y-r,zc-shift-r];hi=[x+r,y+r,top160+r];s=box153([lo,hi]);cells161.append((n+':VARIABLE_STRAIGHT:'+str(side),s));bounds161.append(dict(name=cells161[-1][0],wire=n,bounds_mm=[lo,hi],source_relation='Continuous straight endleg fromvariablecentreZ tofixedtop port, allE55..65.'))
rows161=[];first161=None;checked161=0;minbbox161=1e9;mindetail161=1e9;tasks161=[]
for n,s in cells161:
 for k,v in context160.items():
  low=bbox_lower_bound(s.BoundBox,v.BoundBox)
  if low<1.25:tasks161.append((n,k))
  else:minbbox161=min(minbbox161,low)
lookup161=dict(cells161);tasks161.sort()
for n,k in tasks161:
 s=lookup161[n];v=context160[k];q=dict(cell=n,other=k,valid_source=v.isValid(),required_mm=1.25)
 if not v.isValid():q['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
 else:
  g,ww,_=s.distToShape(v);mindetail161=min(mindetail161,g);q.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='CONTINUOUS_STORAGE_COVER_SEPARATED125' if g>=1.25-1e-7 else 'CONSERVATIVE_STORAGE_COVER_HOLD_NOT_WIRE_CONTACT')
 rows161.append(q)
 if q['status']!='CONTINUOUS_STORAGE_COVER_SEPARATED125':first161=q;break
 if time.monotonic()-st161>17:break
# Single exterior bounding box expanded3.25 is deliberately conservative contour proof, not wire shape.
lo161=[min(b['bounds_mm'][0][i] for b in bounds161) for i in range(3)];hi161=[max(b['bounds_mm'][1][i] for b in bounds161) for i in range(3)];outercover161=box153([[x-3.25 for x in lo161],[x+3.25 for x in hi161]]);outside161=outercover161.cut(BodyOuter31);assert outside161.isValid()
co161=[]
for a,b in zip(pr160['six_independent_storage_branches'],pr160['six_independent_storage_branches'][1:]):co161.append(dict(a=a['wire'],b=b['wire'],full_capacity_layer_gap_mm=b['plane_Y_mm']-a['plane_Y_mm']-(a['profile_radius_mm']+.4)-(b['profile_radius_mm']+.4)))
ar161=OUT/'day07-SOURCE-sidebay-E55-E65-analytic-whole-cover.breps.zip';assert not ar161.exists();ge161=[]
with zipfile.ZipFile(ar161,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(cells161+[('BODY_OUTER_MARGIN_FULL_COVER',outercover161)]):
  raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge161.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge161),indent=2)+'\n').encode())
complete161=len(rows161)==len(tasks161) and first161 is None and outside161.Volume<1e-7
r161=dict(id='day07-SOURCE-sidebay-E55-E65-continuous-neutral-capacity',status='SIX_INDEPENDENT_CONTINUOUS_E55_E65_STATIC_CAPACITY_CLOSED_SCOPED' if complete161 else 'CONTINUOUS_STORAGE_COVER_OR_OUTLINE_OPEN',selected=False,N01_complete=False,analytic_family_relation=bounds161,full_profile_role='Allocated fullprofiles .4capacitymargin, not deliveredphysicalwire collision model',cells=len(cells161),whole_current_context=len(context160),bbox_separated_pairs=len(cells161)*len(context160)-len(tasks161),bbox_separated_lower_mm=minbbox161,rows=rows161,cursor=len(rows161),total=len(tasks161),unreceived=len(tasks161)-len(rows161),minimum_actual_cell_gap_mm=mindetail161 if rows161 else None,first_falsifier=first161,independent_layer_packing=co161,overall_bounds_mm=[lo161,hi161],outline=dict(required_mm=3.25,actual_BodyOuter_used=True,expanded_whole_cover_outside_mm3=outside161.Volume,proof='Validwholeboundingcoverexpanded3.25.cut(actualBodyOuter31)=0 implies ALLallocatedcells3.25insideactualcontour; NOTbboxBodyOuteralone.'),source_lengths=dict(E_each_independently_mm=[55,65],actual_leg_deltaL_each=None,actual_moving_accessible_feed_and_portal=None,body_capacity_NOT_received_storedslack=True,percore_Uonly_mm=[125.2,135.2],whole_A_U_minfit_slack=None,whole_850_900_MAX3_not_accepted=True),no_new_material=True,no_old_passing_pair_or_motion_replay=True,archive=ar161.name,archive_sha256=hashlib.sha256(ar161.read_bytes()).hexdigest(),geometry=ge161,operation_seconds=time.monotonic()-st161,process_cpu_seconds=time.process_time()-cp161,pid=os.getpid(),session_id=46493)
p161=OUT/(r161['id']+'.json');assert not p161.exists();p161.write_bytes((json.dumps(r161,indent=2)+'\n').encode());print('BODY161',r161['status'],'rows',len(rows161),len(tasks161),'first',first161,'outside',outside161.Volume,'min',mindetail161,'wall',r161['operation_seconds'],'CPU',r161['process_cpu_seconds'],flush=True);print('OWNER74_IDLE',os.getpid(),flush=True)
