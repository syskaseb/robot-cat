import time,json,hashlib,zipfile,os,math
st137=time.monotonic();cp137=time.process_time();pp137=OUT/'day07-W068-top-bearing-split-crown-whole-proposal.json';pr137=json.loads(pp137.read_bytes());ff137=ctx121[pr137['root']['actor']]
def box137(bb):
 a,b=bb;return Part.makeBox(*[b[j]-a[j] for j in range(3)],A.Vector(*a))
def rect137(xa,xb,ya,yb,z):
 return Part.Face(Part.Wire(Part.makePolygon([A.Vector(x,y,z) for x,y in [(xa,ya),(xb,ya),(xb,yb),(xa,yb),(xa,ya)]]).Edges))
def band137(width,thick):
 w,e,lo,hi,R=-89,-80.2,31.31,40.11,3
 V=lambda x,z:A.Vector(x,0,z)
 edges=[]
 edges.append(Part.makeLine(V(w+R,lo),V(e-R,lo)))
 for cx,cz,a0,a1,end in [(e-R,lo+R,-90,0,(e,hi-R)),(e-R,hi-R,0,90,(w+R,hi)),(w+R,hi-R,90,180,(w,lo+R)),(w+R,lo+R,180,270,None)]:
  def pt(a):return V(cx+R*math.cos(math.radians(a)),cz+R*math.sin(math.radians(a)))
  edges.append(Part.Arc(pt(a0),pt((a0+a1)/2),pt(a1)).toShape())
  if end is not None:edges.append(Part.makeLine(pt(a1),V(*end)))
 wire=Part.Wire(edges);x=w+R;z=lo;prof=Part.Wire(Part.makePolygon([A.Vector(x,y,zz) for y,zz in [(-width/2,z-thick/2),(width/2,z-thick/2),(width/2,z+thick/2),(-width/2,z+thick/2),(-width/2,z-thick/2)]]).Edges)
 sh=wire.makePipeShell([prof],True,False);assert sh.isValid() and len(sh.Solids)==1;return sh,wire.Length
bandphys137,L137=band137(2.5,1.2);bandfield137,_=band137(3.3,2)
cap137=box137(pr137['root']['crown_block']);west137=box137(pr137['root']['west_capture_cheek']);east137=box137(pr137['root']['east_capture_cheek']);bar0_137=box137(pr137['loadpath']['transverse_crown_bar']);bar137=bar0_137.cut(bandphys137);beam137=box137(pr137['loadpath']['whole_overframe_beam']);members137=[('CENTRAL_TOP_CROWN',cap137),('WEST_CAPTURE',west137),('EAST_CAPTURE',east137),('TRANSVERSE_BAR_WITH_PURPOSEFUL_BAND_CHANNEL',bar137),('WHOLE_TOP_BEARING_BEAM',beam137)];assert all(s.isValid() for _,s in members137)
union137=cap137.multiFuse([s for _,s in members137[1:]]);assert union137.isValid();coverage137=[dict(member=n,missing_mm3=s.cut(union137).Volume,bounds_mm=saved_bounds(s)) for n,s in members137];assert all(q['missing_mm3']<1e-7 for q in coverage137);joints137=[]
for i,(n,a) in enumerate(members137):
 for m,b in members137[i+1:]:
  if bbox_lower_bound(a.BoundBox,b.BoundBox)<1e-7:
   c=a.common(b)
   if c.Volume>1e-7:joints137.append(dict(a=n,b=m,positive_mm3=c.Volume))
headroot137=box137([[-87.6,-3,25.91],[-81.6,3,31.91]]);feed137=box137([[-90,-1.65,27.91],[-79.2,1.65,29.91]])
# New pressure head uses a proper full6 cube, not a smaller axis-aligned approximation.
sad137=ctx121['W068/single/end:0:saddle'];cyl137=[f for f in sad137.Faces if type(f.Surface).__name__=='Cylinder'][0].Surface;axis137=np.array([.25,-.918558653543692,.306186217847898]);origin137=np.array([-129.68807991231608,-26.687023334631895,35.861762918243244]);ss137=[np.dot(np.array(list(v.Point))-origin137,axis137) for v in sad137.Vertexes];mid137=origin137+axis137*(min(ss137)+max(ss137))/2;normal137=np.array([1.,0.,1.]);normal137-=axis137*np.dot(normal137,axis137);normal137/=np.linalg.norm(normal137);u137=np.cross(normal137,axis137);rot137=np.column_stack([u137,normal137,axis137]);assert abs(np.linalg.det(rot137)-1)<1e-8;hc137=mid137+normal137*8.3;mat137=A.Matrix()
for i in range(3):
 for j in range(3):setattr(mat137,'A'+str(i+1)+str(j+1),float(rot137[i,j]))
for i in range(3):setattr(mat137,'A'+str(i+1)+'4',float(hc137[i]))
phead137=Part.makeBox(6,6,6,A.Vector(-3,-3,-3));phead137.Placement=A.Placement(mat137);assert phead137.isValid()
contacts137=[dict(face=22,area_mm2=ff137.Faces[22].common(rect137(-85.6,-83.4,-4.5,4.5,35.51)).Area),dict(face=0,area_mm2=ff137.Faces[0].common(rect137(-127,-80.8,-25,-21,37.02)).Area)]
parts137=[('WHOLE_CROWN_CAPTURE_LOADPATH',union137),('WHOLE_INSTALLED145_BAND_MATERIAL',bandphys137),('ROOT_FULL6_HEAD_IN_APERTURE',headroot137),('FULL_INITIAL_ROOT_FEED_FIELD',feed137),('NEW_FULL6_PRESSURE_HEAD_PROPER_FRAME',phead137)];rows137=[];first137=None;cofirst137=None
for n,s in parts137[:4]:
 co=s.common(ff137);gap,ww,_=s.distToShape(ff137);row=dict(part=n,other=pr137['root']['actor'],field_valid=s.isValid(),source_valid=ff137.isValid(),gap_mm=gap,common_valid=co.isValid(),common_mm3=co.Volume if co.isValid() else None,classification='NAMED_OWN_FRAME_BEARING_CLOSED_BAND_OR_INSTALL_APERTURE',status='OWN_MATERIAL_NONPENETRATION' if co.isValid() and co.Volume<1e-6 else 'ACTUAL_RETAINED_FRAME_MATERIAL_HOLD');rows137.append(row)
 if row['status'].endswith('HOLD'):first137=row;cofirst137=co;break
exclude137={'W068/single/end:0:saddle','W068/single/end:0:band_budget','W068/single/end:0:head_budget'};tasks137=[]
for n,s in parts137:
 for k in ctx121:
  if k==pr137['root']['actor'] or k in exclude137:continue
  if bbox_lower_bound(s.BoundBox,bounds126[k])<1.25:tasks137.append((n,k))
if first137 is None:
 for n,k in tasks137:
  s=dict(parts137)[n];v=ctx121[k];row=dict(part=n,other=k,field_valid=s.isValid(),source_valid=v.isValid())
  if not v.isValid():row['status']='INVALID_SOURCE_OPEN_NOT_CONTACT'
  else:
   gap,ww,_=s.distToShape(v);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]],status='FOREIGN_SEPARATED125' if gap>=1.25-1e-7 else 'FOREIGN_FUNCTION_INTERFACE_HOLD')
   if gap<1e-7:
    c=s.common(v);row.update(common_valid=c.isValid(),allocated_common_mm3=c.Volume if c.isValid() else None);cofirst137=c
  rows137.append(row)
  if row['status']!='FOREIGN_SEPARATED125':first137=row;break
  if time.monotonic()-st137>20:break
items137=[('ACTUAL_CURRENT_FRAME',ff137)]+members137+[('WHOLE_CROWN_UNION',union137),('WHOLE_ROOT145_PHYSICAL_BAND',bandphys137),('ROOT_BAND_FULL_CAPACITY_PROFILE',bandfield137),('FULL6_ROOT_HEAD',headroot137),('INITIAL_FULL_FEED',feed137),('FULL6_PRESSURE_HEAD',phead137)]
if first137 and first137['other']!=pr137['root']['actor']:items137.append(('FIRST_ACTUAL_CURRENT_NEIGHBOR',ctx121[first137['other']]))
if cofirst137 is not None and not cofirst137.isNull():items137.append(('FIRST_ACTUAL_COMMON',cofirst137))
ar137=OUT/'day07-W068-top-bearing-whole-functional-first-gate.breps.zip';assert not ar137.exists();ge137=[]
with zipfile.ZipFile(ar137,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(items137):
  raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge137.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge137),indent=2)+'\n').encode())
r137=dict(id='day07-W068-top-bearing-whole-functional-first-gate',status='NEW_TOP_BEARING_FUNCTIONAL_FIRST_GATE_HOLD' if first137 else 'NEW_TOP_BEARING_INITIAL_ENVELOPE_LOCAL_RECEIVED_FULL_STOCK_OPEN',proposal=pp137.name,proposal_sha256=hashlib.sha256(pp137.read_bytes()).hexdigest(),contacts=contacts137,union=dict(valid=union137.isValid(),solids=len(union137.Solids),member_coverage=coverage137,positive_connections=joints137,extent_mm=saved_bounds(union137),band_channel_removed_mm3=bar0_137.Volume-bar137.Volume),actual_root_loop_length_mm=L137,nominal_loop_length_mm=pr137['root_stock']['nominal_closed_loop_mm'],root_uncut145_minus_loop_mm=145-L137,root_head_pull25_counted_once=True,pressure_axis=axis137.tolist(),pressure_mid=mid137.tolist(),pressure_head_centre=hc137.tolist(),pressure_head_basis=rot137.tolist(),pressure_full6_cube_valid=phead137.isValid(),rows=rows137,first_falsifier=first137,foreign_tasks=tasks137,foreign_received=sum('classification' not in q for q in rows137),foreign_total=len(tasks137),tail_capacity_and_complete_feed_installation_OPEN=True,pressure_full9_material_and_attachment_OPEN=True,selected=False,current_parent_changed=False,N01_complete=False,archive=ar137.name,archive_sha256=hashlib.sha256(ar137.read_bytes()).hexdigest(),geometry=ge137,operation_seconds=time.monotonic()-st137,process_cpu_seconds=time.process_time()-cp137,pid=os.getpid(),session_id=46493)
p137=OUT/'day07-W068-top-bearing-whole-functional-first-gate.json';assert not p137.exists();p137.write_bytes((json.dumps(r137,indent=2)+'\n').encode());print('BODY137',r137['status'],'contacts',contacts137,'members',len(coverage137),'joints',len(joints137),'solids',len(union137.Solids),'Lroot',L137,'first',first137,'rows',r137['foreign_received'],len(tasks137),'wall',r137['operation_seconds'],'CPU',r137['process_cpu_seconds'],flush=True);print('OWNER68_IDLE',os.getpid(),flush=True)
