import FreeCAD as A,FreeCADGui as G,Part,math,json,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent;t0=time.perf_counter();R=12.5
def wr(n,d): (P/n).write_bytes((json.dumps(d,indent=2)+'\n').encode())
def unit(v):q=V(v);q.normalize();return q
def rotate(p,o,axis,deg):return o+A.Rotation(axis,deg).multVec(p-o)
def pose(p,yaw,pitch):return rotate(rotate(p,V(-135,0,121),V(0,1,0),pitch),V(-106,0,127),V(0,0,1),yaw)
def path(yaw,pitch):
 # Initial quarter belongs to the moving head; open receiver is not a clamp.
 c0=pose(V(-206.85,0,134.6),yaw,pitch);p1=pose(V(-194.35,0,122.1),yaw,pitch)
 ps=[p1,pose(V(-174.35,0,122.1),yaw,pitch),rotate(V(-150,-22,92),V(-106,0,127),V(0,0,1),yaw),V(-123,-24,94),V(-84.5,-27.5,80),V(-84.5,-27.5,60.62)]
 # Exact circular primitives plus true straight spans; not a chord-as-route.
 firstc=pose(V(-194.35,0,134.6),yaw,pitch);firstaxis=A.Rotation(V(0,0,1),yaw).multVec(A.Rotation(V(0,1,0),pitch).multVec(V(0,-1,0)))
 firstt=A.Rotation(V(0,0,1),yaw).multVec(A.Rotation(V(0,1,0),pitch).multVec(V(0,0,-1)))
 arcs=[(c0,p1,firstc,firstaxis,math.pi/2,firstt)];cuts=[]
 for i in range(1,len(ps)-1):
  u=unit(ps[i]-ps[i-1]);v=unit(ps[i+1]-ps[i]);theta=math.acos(max(-1,min(1,u.dot(v))));dist=R*math.tan(theta/2);b=unit(u.cross(v));en=ps[i]-u*dist;ex=ps[i]+v*dist;cen=en+b.cross(u)*R
  arcs.append((en,ex,cen,b,theta,u));cuts.append(dist)
 lens=[(b-a).Length for a,b in zip(ps,ps[1:])]
 fit=all(lens[i]>(cuts[i-1] if i else 0)+(cuts[i] if i<len(cuts) else 0) for i in range(len(lens)))
 # Exact arcwidth normals, continuous finite twist only along straights.
 wprev=pose(V(0,1,0),yaw,pitch)-pose(V(),yaw,pitch);sections=[];L=0;edge0=0;edge1=0
 def sec(c,t,w):
  w=unit(w-t*w.dot(t));sections.append((V(c),unit(t),w))
 for k,arc in enumerate(arcs):
  en,ex,cen,b,theta,u=arc;w=b
  if w.dot(wprev)<0:w=-w
  if sections:
   st,tt,sw=sections[-1];line=en-st;ll=line.Length;tt=unit(line);angle=math.atan2(tt.dot(sw.cross(w)),max(-1,min(1,sw.dot(w))));count=max(2,math.ceil(ll/3),math.ceil(abs(angle)/(math.pi/60)))
   for j in range(1,count+1):sec(st+line*(j/count),tt,A.Rotation(tt,math.degrees(angle*j/count)).multVec(sw))
   L+=ll
  count=max(2,math.ceil(theta/(math.pi/90)))
  for j in range(0 if not sections else 1,count+1):
   rot=A.Rotation(b,math.degrees(theta*j/count));sec(cen+rot.multVec(en-cen),rot.multVec(u),w)
  L+=R*theta;wprev=w
 st,tt,sw=sections[-1];line=ps[-1]-st;tt=unit(line);count=max(2,math.ceil(line.Length/3))
 # Pi-end width is PCB CSI row alongY. Contact-facing unknown is NOT resolved.
 ew=V(0,1,0);ew=unit(ew-tt*ew.dot(tt))
 if ew.dot(sw)<0:ew=-ew
 angle=math.atan2(tt.dot(sw.cross(ew)),sw.dot(ew))
 for j in range(1,count+1):sec(st+line*(j/count),tt,A.Rotation(tt,math.degrees(angle*j/count)).multVec(sw))
 L+=line.Length
 for i in range(1,len(sections)):
  a,_,aw=sections[i-1];b,_,bw=sections[i];edge0+=(b+bw*8.4-a-aw*8.4).Length;edge1+=(b-bw*8.4-a+aw*8.4).Length
 return {'yaw':yaw,'pitch':pitch,'exact_center_mm':L,'sampled_edge_lengths_mm':[edge0,edge1],'ends_project_once':10,'center_plus_ends':L+10,'whole200_remainder_center':190-L,'corners_fit_on_straights':fit,'sections':[{'c':list(c),'t':list(t),'w':list(w)} for c,t,w in sections]}
rows=[path(y,p) for y,p in [(0,0),(-20,-10),(-20,0),(-20,10),(0,-10),(0,10),(20,-10),(20,0),(20,10)]]
wr('FFC200-nine-correlated-analytic-premises.json',{'profile_mm':[16.8,1.8],'sagitta_twist_cover_each':.04,'center_R_project':R,'arc_min_allocated_radius':R-.94,'normal_basis':'arc binormalwidth; continuous finite straighttwist; source contactside physicalFIT','rows':rows,'whole200_notshortened':True,'centrelen_notstockdebit':'fullwidth edges/twist/nonlocal overlap/actual mouth stillmustqualify','whole_remainder_range':[min(q['whole200_remainder_center'] for q in rows),max(q['whole200_remainder_center'] for q in rows)],'surplus_storage':'UNRECEIVED; no hidden cut/extension. Needs physicalconnected head/neck bight for fullsameunit, not slackbehindPi grip','no_motionPASS':True})
# Full occupied neutral profile, conservative ruled strips. Named actual hazard
# is the former backing-plate pinch and adjacent gimbal; group boxes cannot
# decide ribbon width/normal at this compound bend. No individual conductors.
ss=[]
for r in rows[0]['sections']:
 c=V(*r['c']);t=V(*r['t']);w=V(*r['w']);n=unit(t.cross(w));a=w*8.44;b=n*.94
 ss.append(Part.Wire(Part.makePolygon([c-a-b,c+a-b,c+a+b,c-a+b,c-a-b]).Edges))
flat=Part.makeLoft(ss,True,True);o=D.getObject('HN_FFC_NEUTRAL_ALLOCATED_FULL_PROFILE') or D.addObject('PartDesign::Feature','HN_FFC_NEUTRAL_ALLOCATED_FULL_PROFILE');o.Shape=flat;o.ViewObject.ShapeColor=(.8,.4,.2);o.ViewObject.Transparency=20
D.recompute();D.save()
wr('FFC-neutral-field-construction.json',{'valid':flat.isValid(),'solids':len(flat.Solids),'volume':flat.Volume,'sections':len(ss),'path_role':'hypothesis fullprofile notpurchasedjacket','coverage_margin':.04,'source_R':'project12.5 notcatalog','named_hazard':'sensorcarrier/fullFFC then actualpitchMG/horn/neck; no oldneutralprefix replay','FIRST_falsifier_cursor':0})
checks=[]
for n in ['HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','MG92B_Head_pitch','PITCH_HORN_ROOF_JOURNAL','HEAD_YAW_FORK_FIXED_PITCH_HOUSING','MG92B_Head_yaw','YAW_HORN_ROOF_JOURNAL','NIGHT_HEAD_FIXED_SADDLE_ROOT','Pi_GPIO1992_factory_female']:
 q=D.getObject(n);distance=flat.distToShape(q.Shape)[0];valid=flat.isValid() and q.Shape.isValid();row={'field':o.Name,'neighbor':n,'gap':distance,'valid':valid,'threshold':1.25,'pass_scoped':valid and distance>=1.25-1e-7}
 checks.append(row);wr('FFC-first-named-occupied-gate.json',{'checks':checks,'cursor':len(checks),'remaining':8-len(checks),'wholePASS':False})
 if not row['pass_scoped']:break
print(json.dumps({'neutral':rows[0]['exact_center_mm'],'minmax_center_plus10':[min(q['center_plus_ends'] for q in rows),max(q['center_plus_ends'] for q in rows)],'checks':checks,'seconds':time.perf_counter()-t0}))
