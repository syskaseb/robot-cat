import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day16-closed-whole-layout')
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def cyl(x,y,z,r,h,axis=None):return Part.makeCylinder(r,h,V(x,y,z),axis or V(0,0,1))
def fuse(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def rr(x,ry,top,bottom=41.5,t=0):
 ry-=t;top-=t;bottom+=t;rb=12-t;rt=35-t;k=math.sqrt(.5);es=[]
 def v(y,z):return V(x,y,z)
 pts=[v(-ry+rb,bottom),v(ry-rb,bottom),v(ry,bottom+rb),v(ry,top-rt),v(ry-rt,top),v(-ry+rt,top),v(-ry,top-rt),v(-ry,bottom+rb)]
 mids={1:v(ry-rb+rb*k,bottom+rb-rb*k),3:v(ry-rt+rt*k,top-rt+rt*k),5:v(-ry+rt-rt*k,top-rt+rt*k),7:v(-ry+rb-rb*k,bottom+rb-rb*k)}
 for i in range(8):es.append(Part.Arc(pts[i],mids[i],pts[(i+1)%8]).toShape() if i in mids else Part.makeLine(pts[i],pts[(i+1)%8]))
 return Part.Wire(es)
def ellipsoid(cx,cy,cz,rx,ry,rz):
 # Analytic ellipsoid via primitive sphere scaling; proposal representation only.
 m=A.Matrix();m.A11=rx;m.A22=ry;m.A33=rz;s=Part.makeSphere(1).transformGeometry(m);s.translate(V(cx,cy,cz));return s
def run():
 S=A.getDocument('DAY15_WHOLE_REAR_LAYER');D=A.newDocument('DAY16_CLOSED_WHOLE_PROPOSAL');groups={};T=time.perf_counter()
 for o in S.Objects:
  if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
 for o in S.Objects:
  if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor') or o.Name.startswith(('VIEW_','COUPON_')):continue
  q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape.copy();q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
  for g in S.Objects:
   if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
 gr=D.addObject('App::DocumentObjectGroup','DAY16_REAL_PARTING_AND_WHOLE_STRUCTURAL_PROPOSAL')
 skins=D.addObject('App::DocumentObjectGroup','DAY16_CLOSED_COVERS_PROPOSED_NO_STL_RELEASE')
 def add(n,s,col=(.22,.55,.65),group=gr,show=True):
  assert s.isValid(),n
  o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=show;group.addObject(o);return o
 # Real new P11 split, not hiding an unchanged integral beam. Same whole material except two printed bores.
 old=D.getObject('P11_rear_gate').Shape.copy();lower=old.common(box(70,-100,0,80,200,128));keys=[]
 for y in [-85,81]:keys.append(old.common(box(98,y,127,6,4,6)))
 lower=fuse([lower]+keys);upper=old.cut(lower);steel=[];bore=fuse([cyl(90,y,130,1.7,23,V(1,0,0)) for y in [-83,83]])
 lower=lower.cut(bore);upper=upper.cut(bore);expected=old.cut(bore);combined=lower.fuse(upper)
 material=dict(source_expected_missing=expected.cut(combined).Volume,unexpected_added=combined.cut(expected).Volume,part_common=lower.common(upper).Volume,lower_solids=len(lower.Solids),upper_solids=len(upper.Solids),key_roots=[q.common(old.common(box(70,-100,0,80,200,128))).Volume for q in keys])
 D.getObject('P11_rear_gate').Shape=lower;D.getObject('P11_rear_gate').Label='NEW P11 LOWER: actual separate print, upperbeam transferred'
 add('P11_REMOVABLE_UPPER_CROSSMEMBER',upper)
 for i,y in enumerate([-83,83]):
  shaft=cyl(94.5,y,130,1.5,16,V(1,0,0)).fuse(cyl(91.5,y,130,2.75,3,V(1,0,0)))
  for tag,s in [('fullM3x16',shaft),('headwasher',cyl(94.5,y,130,3.5,.5,V(1,0,0)).cut(cyl(94.5,y,130,1.6,.5,V(1,0,0)))),('nutwasher',cyl(107,y,130,3.5,.5,V(1,0,0)).cut(cyl(107,y,130,1.6,.5,V(1,0,0))))]:steel.append((f'CAP{i}_{tag}',s));add(f'CAP{i}_{tag}',s,(.7,.71,.75))
  r=5.5/math.sqrt(3);vs=[V(107.5,y+r*math.cos(k*math.pi/3),130+r*math.sin(k*math.pi/3)) for k in range(6)];nut=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(2.4,0,0)).cut(cyl(107.48,y,130,1.525,2.45,V(1,0,0)));steel.append((f'CAP{i}_fullnut',nut));add(f'CAP{i}_fullnut',nut,(.7,.71,.75))
 # A real integral front load bridge at known P10 uppercrossmember, bearing-supported rather than cosmetic-shell root.
 source10=D.getObject('P10_front_gate').Shape.copy();arms=[box(-141,y,132.5,43,6,5.5) for y in [-76,70]];posts=[box(-134,y,137,18,6,4) for y in [-76,70]]
 bridge=box(-134,-76,137,18,152,4).cut(cyl(-126,0,118,11.1,28));cup=cyl(-126,0,119,15.5,22).cut(cyl(-126,0,119,11.1,23));lip=cyl(-126,0,119,15.5,1).cut(cyl(-126,0,119,5,1))
 root=fuse(arms+posts+[bridge,cup,lip]);p10=source10.fuse(root);D.getObject('P10_front_gate').Shape=p10
 add('HEAD_BEARING_UPPER_RETAINER_NOT_SKIN',cyl(-126,0,141,15.5,2).cut(cyl(-126,0,141,5,2)))
 headroot=dict(actual_root_arm_common=[a.common(source10).Volume for a in arms],source_P10_missing=source10.cut(p10).Volume,source_bearing_axis=[-126,0],bearing608OD22_ID8=True,seat_bore22p2_physicalFIT3=True,shaft8_IS_INDEPENDENT_BEARING_PIN_NOT_MG_OUTPUT=True,factoryhorn_holes_seatedheight_coupling_UNKNOWN=True,retainer_bolting_contract_not_detailed=True)
 # Moving fork/plate occupied structure: material interfaces retained in map, no fictitious supplier spline.
 add('HEAD_MOVING_SENSOR_PLATE_PROPOSED',box(-219,-40,106,3,61,55))
 add('HEAD_MOVING_PITCH_ARM_PROPOSED',box(-219,22,138,66,6,6))
 # Whole closed body shell, not a solid envelope called printed mass.
 stations=[(-145,90,158),(-112,102,179),(60,102,183),(150,102,175),(205,60,149)]
 outer=Part.makeLoft([rr(x,y,z) for x,y,z in stations],True,False)
 inner=Part.makeLoft([rr(x+(2.4 if i==0 else -2.4 if i==len(stations)-1 else 0),y,z,t=2.4) for i,(x,y,z) in enumerate(stations)],True,False)
 body=outer.cut(inner)
 # S0 key remains in an accessible isolated well; S1 has a separate operator well.
 body=body.cut(cyl(135.5,-29.278,145,34,60));well=cyl(135.5,-29.278,147,36.4,43).cut(cyl(135.5,-29.278,147,34,44));well=well.fuse(cyl(135.5,-29.278,147,34,2.4).cut(cyl(135.5,-29.278,147,23,2.4)));body=body.fuse(well.common(outer))
 body=body.cut(box(60.4,36.4,156.5,43.2,43.2,40));s1well=box(58,34,156.5,48,48,40).cut(box(60.4,36.4,156.5,43.2,43.2,41));s1well=s1well.fuse(box(60.4,36.4,156.5,43.2,43.2,2.4).cut(box(69,45,156.5,26,26,2.4)));body=body.fuse(s1well.common(outer))
 # Functional cooling and sound perforations; positions remain fit/thermal/acoustic validation, no sealed mic port.
 for x in [-90,-72,-54,-36,-18]:
  for y in [-110,90]:body=body.cut(box(x,y,98,11,20,5))
 for x in range(0,80,10):body=body.cut(box(x,-16,165,4,32,35))
 # Neutral moving head seam, not continuous-motion acceptance.
 houter=ellipsoid(-198,0,144,62,72,63).common(box(-236.5,-100,70,150,200,160));hinner=ellipsoid(-198,0,144,59.6,69.6,60.6).common(box(-234.1,-100,70,150,200,160));head=houter.cut(hinner)
 cam=box(-250,-42,127,34,34,32);tof=box(-252,-18,106,32,36,34)
 head=head.cut(cam).cut(tof).cut(box(-146,-24,113,50,48,40))
 muzzle=ellipsoid(-237,0,124,10,24,23).cut(ellipsoid(-237,0,124,7.6,21.6,20.6));muzzle=muzzle.cut(tof).cut(box(-234.1,-50,80,30,100,100));head=head.fuse(muzzle)
 body=body.cut(ellipsoid(-198,0,144,63.5,73.5,64.5))
 for n in ['Ola_body_ENVELOPE','Ola_head_ENVELOPE','Ola_muzzle','Ola_shared_cheek_mask_PROPOSED','Ola_short_shoulder_blend_PROPOSED']:
  o=D.getObject(n)
  if o:o.ViewObject.Visibility=False;o.Label='RETIRED VISUAL ENVELOPE / '+n
 skinparts=[]
 for tag,x0,x1,split in [('front',-150,25,0),('rear',25,210,10)]:
  for side,y0,y1 in [('negative',-120,split),('positive',split,120)]:
   s=body.common(box(x0,y0,30,x1-x0,y1-y0,170));n='CLOSED_BODY_'+tag+'_'+side;add(n,s,(.105,.11,.12),skins);skinparts.append((n,s,'Yseam down',6))
 for n,z0,z1 in [('CLOSED_HEAD_LOWER',70,140),('CLOSED_HEAD_UPPER',140,230)]:
  s=head.common(box(-270,-100,z0,180,200,z1-z0));add(n,s,(.105,.11,.12),skins);skinparts.append((n,s,'Zseam down',6))
 # Cosmetic eyes are project parts, moved onto the new face. Full sensor openings preserved.
 for n in ['Ola_eye_gold__1','Ola_eye_gold_1','Ola_nose']:
  o=D.getObject(n)
  if o:
   s=o.Shape.copy();s.translate(V(-4.7,0,0));o.Shape=s.cut(cam).cut(tof);o.ViewObject.Visibility=True;o.ViewObject.Transparency=0
 for o in D.Objects:
  if o.Name.startswith(('Ola_ear','Ola_tail')):o.ViewObject.Visibility=True;o.ViewObject.Transparency=0
 printplan=[]
 for n,s,orientation,brim in skinparts:
  b=s.BoundBox;dims=[b.XLength,b.YLength,b.ZLength];xy=[dims[0],dims[2]] if orientation.startswith('Y') else dims[:2];height=dims[1] if orientation.startswith('Y') else dims[2];printplan.append(dict(part=n,geometry= dims,orientation=orientation,brim_per_side=brim,supports='Vertical removable supports within fullpart projection; open seam permits removal. Explicit occupiedregion projection+6mm brim, not slicerPASS.',occupiedXYZ=[xy[0]+2*brim,xy[1]+2*brim,height],under256=max(xy[0]+2*brim,xy[1]+2*brim,height)<256,manufacturing_release=False))
 # Save WHOLE model before first actual falsifier.
 D.Label='DAY16 WHOLE CLOSED CAT / STRUCTURAL ASSEMBLY PROPOSAL';D.recompute();D.saveAs(str(P/'closed-whole-layout.FCStd'))
 r=dict(utc=datetime.now(timezone.utc).isoformat(),status='WHOLE_PROPOSAL_SAVED_FIRST_GATE_PENDING',P11_material=material,headroot=headroot,print_plan=printplan,gate=[],first_falsifier=None)
 # Named risk: prior selected axialdriver fields hit INTEGRAL roof. Now actual lower and cap are physically separate.
 tooldefs=[('root0',cyl(103,35,115,4.25,35)),('root1',cyl(103,49,115,4.25,35)),('M2_MAIN',cyl(89.321,24.159,122.8748,2.2,25)),('M2_AUX',cyl(101.159,70.241,122.87,2.2,25))]
 for n,s in tooldefs:
  c=s.common(lower);row=dict(name=n,target='ACTUAL_NEW_LOWER_P11_CAP_ABSENT',common=c.Volume,valid=c.isValid());r['gate'].append(row)
  if c.Volume>1e-5 or not c.isValid():r['first_falsifier']=row;break
 if not r['first_falsifier']:
  for n in ['AUX_FULL9p5_POPULATED_SCOPE','MAIN_UNSHRUNK_FAMILY_SCOPE','AUX_all_terminal_field_FIT2','MAIN_all_terminal_field_FIT2']:
   o=D.getObject(n);b=o.Shape.BoundBox;c=upper.common(box(b.XMin,b.YMin,0,b.XLength,b.YLength,200));empty=c.isNull() or c.Volume<1e-5;gap=None if empty else c.BoundBox.ZMin-b.ZMax;row=dict(name='CAP_CONTINUOUS_PLUS_Z_CLOSING',other=n,emptyXYcolumn=empty,min_gap=gap,valid=c.isValid(),clear=empty or gap>=1.25-1e-6);r['gate'].append(row)
   if not row['clear']:r['first_falsifier']=row;break
 if not r['first_falsifier'] and (not all(x>1e-5 for x in headroot['actual_root_arm_common'])):r['first_falsifier']=dict(name='HEAD_NEW_LOAD_BRIDGE_NO_ACTUAL_P10_ROOT',values=headroot['actual_root_arm_common'])
 # One bounded cover witness: source fullkey/body/F0. Coarse allocations are labelled, not deliveredcontact.
 if not r['first_falsifier']:
  for n in ['S0_key','S1_NKK_S821_installed','F0_FHAC0002_30A']:
   q=D.getObject(n).Shape;c=body.common(q);gap=body.distToShape(q)[0];row=dict(name='NEW_CLOSED_BODY',other=n,gap=gap,common=c.Volume,valid=c.isValid(),allocated_body_if_box=(n!='S0_key'));r['gate'].append(row)
   if not c.isValid() or gap<1.25-1e-6:r['first_falsifier']=row;break
 r['status']='WHOLE_PROPOSAL_FIRST_FALSIFIER_HOLD_NO_SECOND_FAMILY' if r['first_falsifier'] else 'NEW_PARTING_ASSEMBLY_AND_FIRST_BODY_WITNESSES_CLEAR_SCOPED_NOT_WHOLE_ACCEPTANCE'
 r['seconds']=time.perf_counter()-T;r['whole_feasible']=False;r['physical_pass']=False;r['actual_fit_cut_slack']=None
 (P/'first-whole-falsifier-and-source-proof.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 # Data references sufficient for review, not giant copied motion matrices.
 rows=[]
 for z in [130,150]:
  for n in ['P11_rear_gate','P11_REMOVABLE_UPPER_CROSSMEMBER']+[x[0] for x in skinparts]+['AUX_FULL9p5_POPULATED_SCOPE','MAIN_Pololu4853']:
   s=D.getObject(n).Shape
   if s.BoundBox.ZMin>z or s.BoundBox.ZMax<z:continue
   sec=s.section(Part.makePlane(500,250,V(-270,-120,z)));rows.append(dict(z=z,name=n,lines=[[[v.x,v.y] for v in e.discretize(Deflection=.2)] for e in sec.Edges]))
 (P/'whole-assembly-sections.json').write_text(json.dumps(rows)+'\n',encoding='utf-8')
 for o in D.Objects:
  if hasattr(o.ViewObject,'ShapeColor') and (o.Name.startswith(('FEED_','KEY_','CAPTURE_','DIRECT_','VIEW_','AL_','CF_','P12_FULL_OD6','P12_UNCHANGED_R24')) or 'section' in o.Name.lower()):o.ViewObject.Visibility=False
 D.Label='DAY16 CLOSED WHOLE / '+r['status'];D.recompute();D.save();A.setActiveDocument(D.Name)
 print(json.dumps(dict(status=r['status'],objects=len(D.Objects),parting=material,headroot=headroot,first=r['first_falsifier'],printplan=printplan,seconds=r['seconds'])))
run()
