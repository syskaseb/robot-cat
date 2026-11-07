import time,json,hashlib,zipfile,os
st155=time.monotonic();cp155=time.process_time();pp155=OUT/'day07-FPI-cradle-rear-tail-portal-loadpath-correction1.json';pr155=json.loads(pp155.read_bytes())
probe155=box153(pr155['root_probe']);pc155=oldroot153.common(probe155);assert pc155.isValid() and pc155.Volume>1e-7
members155=[(n,s) for n,s in members153 if n in pr155['unchanged_new_members_reused']]
for n,bb in pr155['new_members'].items():
 s=box153(bb)
 if n=='overhead_tail_portal_beam':s=s.cut(band153)
 assert s.isValid() and len(s.Solids)==1
 members155.append((n,s))
all155=[('PRESERVED_CURRENT_V_ROOT',oldroot153)]+members155;union155=oldroot153.multiFuse([s for _,s in members155]);assert union155.isValid()
cov155=[dict(name=n,missing_mm3=s.cut(union155).Volume,bounds_mm=saved_bounds(s)) for n,s in all155];assert max(q['missing_mm3'] for q in cov155)<1e-7
jo155=[]
for i,(n,s) in enumerate(all155):
 for m,v in all155[i+1:]:
  if bbox_lower_bound(s.BoundBox,v.BoundBox)<1e-7:
   c=s.common(v)
   if c.Volume>1e-7:jo155.append(dict(a=n,b=m,common_mm3=c.Volume,valid=c.isValid()))
new155=union155.cut(union153);assert new155.isValid();first155=None
own155={}
for n,s,v in [('case_vs_print',case148,union155),('band_vs_print',band153,union155),('band_vs_case',band153,case148)]:
 c=s.common(v);own155[n]=dict(valid=c.isValid(),common_mm3=c.Volume)
 if not c.isValid() or c.Volume>1e-7:first155=dict(kind='MATERIAL_PENETRATION',pair=n,**own155[n])
portal155=[]
newparts155=[(n,s) for n,s in members155 if n in pr155['new_members']]
for n,s in newparts155:
 for k,v in [('FIVE_TAIL_FIELD',ribbon148),('T30L_FULL_HEAD',head153),('T30L_FULL_CONNECTED_NECK',neck153)]:
  g,w,_=s.distToShape(v);c=s.common(v);portal155.append(dict(part=n,other=k,gap_mm=g,common_mm3=c.Volume,valid=c.isValid(),required_mm=1.25))
  if g<1.25-1e-7 and first155 is None:first155=dict(kind='STOCK_PORTAL_HOLD',**portal155[-1])
tasks155=[k for k,v in ctx121.items() if k not in ['V:new_root_material','V:functional_pressure_support','F_PI:registered_casing_reservation'] and bbox_lower_bound(new155.BoundBox,bounds126[k])<1.25]
tasks155.sort(key=lambda k:(0 if 'SideLeft22' in k else 1 if k.startswith('Ref_Material_') else 2,k));rows155=[];common155=None
if first155 is None:
 for k in tasks155:
  v=ctx121[k];q=dict(other=k,source_valid=v.isValid(),required_mm=1.25)
  if not v.isValid():q['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
  else:
   g,w,_=new155.distToShape(v);q.update(gap_mm=g,witnesses=[[list(a),list(b)] for a,b in w[:1]],status='CHANGED_MATERIAL_SEPARATED125' if g>=1.25-1e-7 else 'CHANGED_MATERIAL_HOLD')
   if g<1e-7:
    c=new155.common(v);q.update(common_valid=c.isValid(),common_mm3=c.Volume if c.isValid() else None);common155=c
  rows155.append(q)
  if q['status']!='CHANGED_MATERIAL_SEPARATED125':first155=q;break
  if time.monotonic()-st155>18:break
sect155=[]
for xx in [-66.55,-50,-40]:
 pl=Part.Face(Part.makePolygon([A.Vector(xx,10,32),A.Vector(xx,35,32),A.Vector(xx,35,65),A.Vector(xx,10,65),A.Vector(xx,10,32)]));s=union155.common(pl);sect155.append(('USEFUL_WORLD_YZ_X'+str(xx),s))
items155=[('PRESERVED_ACTUAL_V_ROOT',oldroot153),('ACTUAL_SOURCE_ROOT_PROBE',probe155),('ACTUAL_SOURCE_ROOT_CONTACT',pc155)]+members155+[('WHOLE_CORRECTED_ROOT_AND_CRADLE',union155),('ONLY_C1_NEW_ADDED_MATERIAL',new155),('FULL_CASE',case148),('FULL_T30L_BAND',band153),('FULL_HEAD',head153),('FIVE_TAIL_FIELD',ribbon148),('FULL_CONNECTED_NECK',neck153),('ACTUAL_SIDELEFT22',rail154)]+sect155
if first155 and first155.get('other') in ctx121:items155.append(('FIRST_ACTUAL_NEIGHBOR',ctx121[first155['other']]))
if common155 is not None and not common155.isNull():items155.append(('FIRST_ACTUAL_COMMON',common155))
ar155=OUT/'day07-FPI-rear-portal-correction1-current-material.breps.zip';assert not ar155.exists();ge155=[]
with zipfile.ZipFile(ar155,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(items155):
  raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge155.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,area_mm2=s.Area,bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge155),indent=2)+'\n').encode())
r155=dict(id='day07-FPI-rear-portal-correction1-current-material',status='C1_FIRST_FUNCTIONAL_INTERFACE_HOLD' if first155 else 'C1_CHANGED_MATERIAL_RECEIVED_SCOPED_WHOLEKIT_OPEN',proposal=pp155.name,proposal_sha256=hashlib.sha256(pp155.read_bytes()).hexdigest(),actual_root_mm3=pc155.Volume,coverage=cov155,positive_joints=jo155,source_old_solids=len(oldroot153.Solids),new_union_solids=len(union155.Solids),own_material_checks=own155,stock_portals=portal155,rows=rows155,cursor=len(rows155),total=len(tasks155),unreceived=len(tasks155)-len(rows155),first_falsifier=first155,old_case_V075_still_HOLD=True,independent4wirestrains_feed_roll_initialassembly_OPEN=True,old_C0_4of23_19unreceived_frozen=True,source_V_caps_ports_BankPads_crown_unchanged=True,currentparent_not_replaced=True,selected=False,N01_complete=False,archive=ar155.name,archive_sha256=hashlib.sha256(ar155.read_bytes()).hexdigest(),geometry=ge155,operation_seconds=time.monotonic()-st155,process_cpu_seconds=time.process_time()-cp155,pid=os.getpid(),session_id=46493)
p155=OUT/(r155['id']+'.json');assert not p155.exists();p155.write_bytes((json.dumps(r155,indent=2)+'\n').encode());print('BODY155',r155['status'],'ROOT',pc155.Volume,'members',len(cov155),'joins',len(jo155),'first',first155,'foreign',len(rows155),len(tasks155),'wall',r155['operation_seconds'],'CPU',r155['process_cpu_seconds'],flush=True);print('OWNER72_IDLE',os.getpid(),flush=True)
