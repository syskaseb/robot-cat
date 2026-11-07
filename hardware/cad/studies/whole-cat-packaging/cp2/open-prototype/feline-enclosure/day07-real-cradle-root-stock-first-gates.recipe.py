import time,json,hashlib,zipfile,os,math
st153=time.monotonic();cp153=time.process_time();pp153=OUT/'day07-FPI-cradle-preserved-V-root-functional-joint-proposal.json';pr153=json.loads(pp153.read_bytes());oldroot153=ctx121['V:new_root_material']
def box153(bb):
 lo,hi=bb;return Part.makeBox(*[hi[i]-lo[i] for i in range(3)],A.Vector(*lo))
probe153=box153(pr153['first_actual_root_probe']);pc153=oldroot153.common(probe153);assert pc153.isValid();assert pc153.Volume>1e-6, 'ACTUAL_PLANNED_USEFUL_SOURCE_ROOT_EMPTY'
# Full T30L3.5x1.2 nominal band in YZ, same-source190/198, no manufacturer head/length-tolerance guarantee invented.
x,y0,y1,z0,z1,R=-60.3,-11,19,35.275,59.225,3;V=lambda y,z:A.Vector(x,y,z);edges153=[Part.makeLine(V(y0+R,z0),V(y1-R,z0))]
for cy,cz,a0,a1,en in [(y1-R,z0+R,-90,0,(y1,z1-R)),(y1-R,z1-R,0,90,(y0+R,z1)),(y0+R,z1-R,90,180,(y0,z0+R)),(y0+R,z0+R,180,270,None)]:
 pt=lambda a:V(cy+R*math.cos(math.radians(a)),cz+R*math.sin(math.radians(a)))
 edges153.append(Part.Arc(pt(a0),pt((a0+a1)/2),pt(a1)).toShape())
 if en is not None:edges153.append(Part.makeLine(pt(a1),V(*en)))
wire153=Part.Wire(edges153);prof153=Part.Wire(Part.makePolygon([A.Vector(xx,y0+R,zz) for xx,zz in [(x-1.75,z0-.6),(x+1.75,z0-.6),(x+1.75,z0+.6),(x-1.75,z0+.6),(x-1.75,z0-.6)]]).Edges);band153=wire153.makePipeShell([prof153],True,False);assert band153.isValid() and abs(band153.Volume-wire153.Length*3.5*1.2)<1e-5
members153=[]
for n,bb in pr153['planned_members'].items():
 s=box153(bb)
 if n=='floor':s=s.cut(band153) # only NEW ownfloor groove; never oldVroot/case.
 assert s.isValid() and len(s.Solids)==1;members153.append((n,s))
allmembers153=[('PRESERVED_CURRENT_V_ROOT',oldroot153)]+members153;union153=oldroot153.multiFuse([s for _,s in members153]);assert union153.isValid();coverage153=[dict(name=n,missing_mm3=s.cut(union153).Volume,bounds_mm=saved_bounds(s)) for n,s in allmembers153];assert max(q['missing_mm3'] for q in coverage153)<1e-7;delta153=union153.cut(oldroot153);assert delta153.isValid();joints153=[]
for i,(n,a) in enumerate(allmembers153):
 for m,b in allmembers153[i+1:]:
  if bbox_lower_bound(a.BoundBox,b.BoundBox)<1e-7:
   c=a.common(b)
   if c.Volume>1e-7:joints153.append(dict(a=n,b=m,common_mm3=c.Volume,valid=c.isValid()))
casefit153=union153.common(case148);bandcase153=band153.common(case148);bandprint153=band153.common(union153);assert all(c.isValid() for c in [casefit153,bandcase153,bandprint153]);own153=[]
# Face contact rather than empty solid/solid intersection-area as bearing proof.
for i,f in enumerate(case148.Faces):
 if type(f.Surface).__name__=='Plane' and abs(f.normalAt(0,0).z)>.99:
  targetz=f.CenterOfMass.z
  if abs(targetz-38.375)<1e-6:
   for j,k in enumerate(dict(members153)['floor'].Faces):
    if type(k.Surface).__name__=='Plane' and abs(k.CenterOfMass.z-targetz)<1e-6:
     c=f.common(k)
     if c.Area>1e-7:own153.append(dict(role='CASE_BOTTOM_TO_NEW_FLOOR',a=i,b=j,area_mm2=c.Area))
  if abs(targetz-58.625)<1e-6:
   for j,k in enumerate(band153.Faces):
    if type(k.Surface).__name__=='Plane' and abs(k.CenterOfMass.z-targetz)<1e-6:
     c=f.common(k)
     if c.Area>1e-7:own153.append(dict(role='WHOLE_T30L_TO_CASE_TOP',a=i,b=j,area_mm2=c.Area))
head153=head148;neck153=box153(pr153['T30L']['connected_head_neck_field']);portalrows153=[]
for n,s in [('FIVE_TAIL_PORTAL',ribbon148),('LARGE_T30L_HEAD_PROJECT',head153),('LARGE_T30L_CONNECTED_NECK_PROJECT',neck153)]:
 gap,ww,_=delta153.distToShape(s);portalrows153.append(dict(new_material_to=n,gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]],scope='samemountstockgeometry; keepnominalnonpenetration plusdeclaredworkingclearance; unrelatedregionsforeign1.25',common_mm3=delta153.common(s).Volume))
parts153=[('NEW_CASE_CRADLE_ADDED_MATERIAL',delta153),('WHOLE_T30L_CLOSED_BAND_FIELD',band153),('CASE_T30L_FULL_HEAD_PROJECT',head153),('CASE_T30L_HEAD_TO_RIBBON_NECK',neck153)];tasks153=[]
for n,s in parts153:
 for k,v in ctx121.items():
  if k in ['V:new_root_material','V:functional_pressure_support','F_PI:registered_casing_reservation']:continue
  if bbox_lower_bound(s.BoundBox,bounds126[k])<1.25:tasks153.append((n,k))
idx153={n:i for i,(n,_) in enumerate(parts153)};tasks153.sort(key=lambda t:(idx153[t[0]],0 if t[1].startswith('Ref_Material_') else 1,t[1]));rows153=[];first153=None;common153=None
# No OWN classification of old case/.75 yet: independentwirestrains/feed/fullassembly remain open.
if casefit153.Volume>1e-7 or bandcase153.Volume>1e-7 or bandprint153.Volume>1e-7:first153=dict(kind='NEW_MOUNT_OR_STOCK_MATERIAL_PENETRATION',case_common_mm3=casefit153.Volume,band_case_common_mm3=bandcase153.Volume,band_print_common_mm3=bandprint153.Volume)
if first153 is None:
 for n,k in tasks153:
  s=dict(parts153)[n];v=ctx121[k];row=dict(part=n,other=k,source_valid=v.isValid(),field_valid=s.isValid(),required_mm=1.25)
  if not v.isValid():row['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
  else:
   gap,ww,_=s.distToShape(v);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='NEW_DELTA_SEPARATED125' if gap>=1.25-1e-7 else 'NEW_DELTA_INTERFACE_HOLD')
   if gap<1e-7:
    c=s.common(v);common153=c;row.update(common_valid=c.isValid(),allocated_common_mm3=c.Volume if c.isValid() else None)
  rows153.append(row)
  if row['status']!='NEW_DELTA_SEPARATED125':first153=row;break
  if time.monotonic()-st153>18:break
items153=[('PRESERVED_ACTUAL_V_ROOT',oldroot153),('ACTUAL_ROOT_INTERFACE_PROBE',probe153),('ACTUAL_ROOT_INTERFACE_MATERIAL',pc153)]+members153+[('WHOLE_V_ROOT_PLUS_CASE_CRADLE',union153),('ONLY_NEW_ADDED_MATERIAL',delta153),('WHOLE_NOMINAL_T30L_BAND',band153),('CURRENT_CASE_RESERVED_BODY',case148),('FULL_T30L_PROJECT_HEAD',head153),('LARGE_HEAD_RIBBON_NECK',neck153)]
if first153 and first153.get('other'):items153.append(('FIRST_ACTUAL_CURRENT_NEIGHBOR',ctx121[first153['other']]))
if common153 is not None and not common153.isNull():items153.append(('ACTUAL_FIRST_NEW_COMMON',common153))
ar153=OUT/'day07-FPI-real-cradle-preserved-V-root-first-gates.breps.zip';assert not ar153.exists();ge153=[]
with zipfile.ZipFile(ar153,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(items153):
  raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge153.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge153),indent=2)+'\n').encode())
r153=dict(id='day07-FPI-real-cradle-preserved-V-root-first-gates',status='REAL_CRADLE_ROOT_AND_STOCK_FIRST_INTERFACE_HOLD' if first153 else 'REAL_CRADLE_ROOT_LOCAL_RECEIVED_WHOLEKIT_NOT_ACCEPTED',proposal=pp153.name,proposal_sha256=hashlib.sha256(pp153.read_bytes()).hexdigest(),actual_root_probe_mm3=pc153.Volume,root_unchanged_material_missing_mm3=coverage153[0]['missing_mm3'],new_union=dict(valid=union153.isValid(),solids=len(union153.Solids),extent=saved_bounds(union153),member_coverage=coverage153,positive_joints=joints153),actual_case_capture_contacts=own153,nominal_closed_band_length_mm=wire153.Length,band_volume_mm3=band153.Volume,band_case_common_mm3=bandcase153.Volume,case_print_common_mm3=casefit153.Volume,band_print_common_mm3=bandprint153.Volume,stock_portal_and_neck_rows=portalrows153,rows=rows153,cursor=len(rows153),total=len(tasks153),unreceived=len(tasks153)-len(rows153),first_falsifier=first153,source_caps_grips_ports_BankPads_NOT_moved=True,source_old_V_allmaterial_preserved=True,aggregate_pressurehalves_nylon_NOT_permanent_fused=True,new_crown_unchanged_separate=True,independentwire4strain_roots_and_fullfeedrollassembly_OPEN=True,old_case_root_raw075_HOLD_not_reclassified=True,currentparent_not_replaced=True,selected=False,N01_complete=False,archive=ar153.name,archive_sha256=hashlib.sha256(ar153.read_bytes()).hexdigest(),geometry=ge153,operation_seconds=time.monotonic()-st153,process_cpu_seconds=time.process_time()-cp153,pid=os.getpid(),session_id=46493)
p153=OUT/(r153['id']+'.json');assert not p153.exists();p153.write_bytes((json.dumps(r153,indent=2)+'\n').encode());print('BODY153',r153['status'],'probe',pc153.Volume,'members',len(coverage153),'joins',len(joints153),'solids',len(union153.Solids),'contacts',own153,'first',first153,'rows',len(rows153),len(tasks153),'wall',r153['operation_seconds'],'CPU',r153['process_cpu_seconds'],flush=True);print('OWNER72_IDLE',os.getpid(),flush=True)
