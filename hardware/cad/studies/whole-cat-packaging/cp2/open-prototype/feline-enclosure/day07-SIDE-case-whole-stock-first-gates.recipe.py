import time,json,hashlib,zipfile,os,math
st148=time.monotonic();cp148=time.process_time();pp148=OUT/'day07-FPI-minusY-whole-case-stock-root-kit-proposal.json';pr148=json.loads(pp148.read_bytes())
def box148(bb):
 a,b=bb;return Part.makeBox(*[b[i]-a[i] for i in range(3)],A.Vector(*a))
def roundpipe148(edges,r):
 path=Part.Wire(edges);p=edges[0].Vertexes[0].Point;t=edges[0].tangentAt(edges[0].FirstParameter);s=path.makePipeShell([Part.Wire([Part.makeCircle(r,p,t)])],True,False);assert s.isValid();return s,path.Length
old148=ctx121['F_PI:registered_casing_reservation'];rot148=A.Rotation(A.Vector(1,0,0),180);tf148=A.Placement(A.Vector(*pr148['case_pose']['centre_mm'])-rot148.multVec(A.Vector(-52.95,0,41.1)),rot148);case148=old148.copy();case148.Placement=tf148*case148.Placement;assert case148.isValid() and abs(case148.Volume-old148.Volume)<1e-7;lid148=box148(pr148['case_pose']['side_operation_box'])
w43148,l43148=roundpipe148([Part.makeLine(A.Vector(-17.3,4,48.5),A.Vector(4.55,4,48.5))],2)
a=pr148['W077'];ed148=[Part.makeLine(A.Vector(*a['start']),A.Vector(*a['arc_start'])),Part.Arc(A.Vector(*a['arc_start']),A.Vector(*a['arc_mid']),A.Vector(*a['arc_end'])).toShape(),Part.makeLine(A.Vector(*a['arc_end']),A.Vector(*a['tip16']))];w77148,l77148=roundpipe148(ed148,2);assert abs(l77148-a['L_nominal'])<1e-6
splice148=Part.makeCylinder(3,20,A.Vector(-81.95,-19.4,48.5),A.Vector(0,-1,0));head148=box148(pr148['case_tie']['head_bounds_mm']);inputhead148=Part.makeBox(5,4.3,5.3,A.Vector(-14.05,9.35,45.85))
# Full five-tail capacity, 15.1 alongZ and 2 radially inXY; notfive pooled lengthdebits.
w,e,lo,hi,R=-55,-7,17.5,23.5,3;V=lambda x,y:A.Vector(x,y,47.175);edges148=[Part.makeLine(V(w+R,lo),V(e-R,lo))]
for cx,cy,t0,t1,endpoint in [(e-R,lo+R,-90,0,(e,hi-R)),(e-R,hi-R,0,90,(w+R,hi)),(w+R,hi-R,90,180,(w,lo+R)),(w+R,lo+R,180,270,None)]:
 pt=lambda t:V(cx+R*math.cos(math.radians(t)),cy+R*math.sin(math.radians(t)))
 edges148.append(Part.Arc(pt(t0),pt((t0+t1)/2),pt(t1)).toShape())
 if endpoint is not None and (pt(t1)-V(*endpoint)).Length>1e-8:edges148.append(Part.makeLine(pt(t1),V(*endpoint)))
path148=Part.Wire(edges148);prof148=Part.Wire(Part.makePolygon([A.Vector(w+R,y,z) for y,z in [(lo-1,39.625),(lo+1,39.625),(lo+1,54.725),(lo-1,54.725),(lo-1,39.625)]]).Edges);ribbon148=path148.makePipeShell([prof148],True,False);assert ribbon148.isValid() and abs(ribbon148.Volume-path148.Length*15.1*2)<1e-5
parts148=[('SIDE_WHOLE_FHAC_CASE',case148),('SIDE_ROUTINE_OPENING',lid148),('W043_FULL_FACTORY_ALLOCATED_PROFILE',w43148),('W077_FULL_FACTORY_ALLOCATED_PROFILE',w77148),('OWNED_SPLICE20_FULL_PROFILE',splice148),('T30L_WHOLE6x6x4_HEAD',head148),('W043_T18I_SELECTED_FULL_HEAD',inputhead148),('FIVE_FULL_TAIL_SHARED15_1x2_REGION',ribbon148),('UNCHANGED_W068_FULL6_PRESSUREHEAD',phead137)]
tasks148=[]
for n,s in parts148:
 for k,v in ctx121.items():
  if k=='F_PI:registered_casing_reservation':continue
  if bbox_lower_bound(s.BoundBox,bounds126[k])<1.25:tasks148.append((n,k))
index148={n:i for i,(n,_) in enumerate(parts148)}
def pri148(k):return 0 if k.startswith('Ref_Material_') or k.startswith('CurrentFoundation:') or k=='Underdeck:RestoredBank' or (k.startswith('Station:') and k.endswith(':case')) else 1
tasks148.sort(key=lambda t:(index148[t[0]],pri148(t[1]),t[1]));rows148=[];first148=None;co148=None;lookup148=dict(parts148)
for n,k in tasks148:
 s=lookup148[n];v=ctx121[k];minimum=0 if n.startswith('W043_FULL') and k=='Station:P_SYS:case' else .15 if n.startswith('W043_FULL') and k=='Station:P_SYS:common_channelled_cap_exterior' else 1.25;row=dict(part=n,other=k,field_valid=s.isValid(),source_valid=v.isValid(),required_mm=minimum,kind='typednominalfactoryallocation' if n.startswith(('W043_FULL','W077_FULL')) else 'functionalprojectallocation')
 if not v.isValid():row['status']='INVALID_CURRENT_SOURCE_OPEN_NOT_CONTACT'
 else:
  gap,ww,_=s.distToShape(v);row.update(gap_mm=gap,witnesses=[[list(a),list(b)] for a,b in ww[:1]])
  if gap<1e-7:
   c=s.common(v);co148=c;row.update(common_valid=c.isValid(),allocated_common_mm3=c.Volume if c.isValid() else None)
  ok=gap>=minimum-1e-6 and (minimum>0 or row.get('allocated_common_mm3',0)<1e-7)
  row['status']='NEW_KIT_INTERFACE_SCOPED_SEPARATED_OR_OWNFIT' if ok else 'NEW_KIT_INTERFACE_ALLOCATION_HOLD'
  if minimum<1.25:row['named_own_function']='sameW043 P_SYS5 actualprojectport/full9channel, no other ownership waiver'
 rows148.append(row)
 if row['status']!='NEW_KIT_INTERFACE_SCOPED_SEPARATED_OR_OWNFIT':first148=row;break
 if time.monotonic()-st148>18:break
casekeys148=[t for t in tasks148 if t[0] in ['SIDE_WHOLE_FHAC_CASE','SIDE_ROUTINE_OPENING']];receivedcase148=[r for r in rows148 if r['part'] in ['SIDE_WHOLE_FHAC_CASE','SIDE_ROUTINE_OPENING']];caseclosed148=len(receivedcase148)==len(casekeys148) and all(r['status']=='NEW_KIT_INTERFACE_SCOPED_SEPARATED_OR_OWNFIT' for r in receivedcase148)
items148=[('OLD_FPI_UNQUALIFIED_RESERVATION',old148)]+parts148
if first148:items148.append(('FIRST_CURRENT_OBSTACLE',ctx121[first148['other']]))
if co148 is not None and co148.isValid() and not co148.isNull():items148.append(('VALID_FIRST_ALLOCATED_COMMON',co148))
ar148=OUT/'day07-FPI-minusY-case-whole-stock-first-gates.breps.zip';assert not ar148.exists();ge148=[]
with zipfile.ZipFile(ar148,'w',zipfile.ZIP_DEFLATED) as z:
 for i,(n,s) in enumerate(items148):
  raw=s.exportBrepToString().encode();en=str(i)+'.brep';z.writestr(en,raw);ge148.append(dict(name=n,entry=en,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',(json.dumps(dict(geometry=ge148),indent=2)+'\n').encode())
r148=dict(id='day07-FPI-minusY-case-whole-stock-first-gates',status='SIDE_CASE_BAY_CLOSED_SCOPED_LATER_KIT_HOLD' if caseclosed148 and first148 else 'SIDE_KIT_FIRST_ALLOCATION_HOLD' if first148 else 'BOUNDED_SIDE_KIT_GATE_NOT_WHOLE_ACCEPTANCE',proposal=pp148.name,proposal_sha256=hashlib.sha256(pp148.read_bytes()).hexdigest(),case_bay_closed_scoped=caseclosed148,case_operation_counter=dict(received=len(receivedcase148),total=len(casekeys148)),case_world_transform_once=True,new_case_valid_same_volume=True,rows=rows148,cursor=len(rows148),total=len(tasks148),unreceived=len(tasks148)-len(rows148),tasks=tasks148,first_falsifier=first148,nominal_W043_L_mm=l43148,nominal_W077_L_mm=l77148,five_tail_region=dict(path_capacity_each_mm=path148.Length,profile15_1x2=True,volume_mm3=ribbon148.Volume,individual_feeds_and_total_tail_coverage_OPEN=True),T30L_name_corrected_SKUunchanged=True,cradle_or_pressure_print_built=False,old_current_parent_or_splicebudgets_not_deleted=True,current_S0cowl_PWMwasher_dependencies_OPEN=True,wholekit_stockfeed_and_assembly_NOT_accepted=True,selected=False,N01_complete=False,archive=ar148.name,archive_sha256=hashlib.sha256(ar148.read_bytes()).hexdigest(),geometry=ge148,operation_seconds=time.monotonic()-st148,process_cpu_seconds=time.process_time()-cp148,pid=os.getpid(),session_id=46493)
p148=OUT/(r148['id']+'.json');assert not p148.exists();p148.write_bytes((json.dumps(r148,indent=2)+'\n').encode());print('BODY148',r148['status'],'case',r148['case_operation_counter'],'first',first148,'rows',len(rows148),len(tasks148),'wall',r148['operation_seconds'],'CPU',r148['process_cpu_seconds'],flush=True);print('OWNER71_IDLE',os.getpid(),flush=True)
