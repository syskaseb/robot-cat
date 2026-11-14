import FreeCAD as A,FreeCADGui as G,Part,Mesh,json,math,time,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;T=time.perf_counter()
B=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit');OLD=B/'foundation-fit-kit';P=B/'fit-kit-final';P.mkdir(exist_ok=True);(P/'stl').mkdir(exist_ok=True)
source=A.getDocument('DAY14_FOUNDATION_FIT_KIT');d=json.loads((OLD/'foundation-kit.json').read_bytes())
D=A.newDocument('DAY14_FIT_KIT_FINAL');groups={};objs={};identity=[]
for o in source.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in source.Objects:
 if o.TypeId=='App::DocumentObjectGroup' or not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor') or o.Name=='Upper_frame_end_105':continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Label=o.Label;q.Shape=o.Shape
 q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for prop in ['Status','AssemblyNote','OriginalSource']:
  if hasattr(o,prop):q.addProperty('App::PropertyString',prop);setattr(q,prop,str(getattr(o,prop)))
 for g in source.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
 objs[o.Name]=q;identity.append(dict(name=o.Name,same_shape_after_assignment=q.Shape.isSame(o.Shape)))
def box(p,s):return Part.makeBox(*s,V(*p))
def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,V(x,y,z))
def bbox(s):
 b=s.BoundBox;return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
def hexsolid(x,y,z,AF,h,angle):
 R=AF/math.sqrt(3);pts=[V(x+R*math.cos(angle+j*math.pi/3),y+R*math.sin(angle+j*math.pi/3),z) for j in range(7)]
 return Part.Face(Part.Wire(Part.makePolygon(pts).Edges)).extrude(V(0,0,h))
centres=[(110,-73),(110,15),(172,-73),(164,15)]
pockettools=[];pocketrows=[]
for i,(x,y) in enumerate(centres):
 axis='X' if i==1 else 'Y';angle=0 if axis=='X' else math.pi/6
 tools=[hexsolid(x,y,43.42,5.8,2.6,angle),cyl(x,y,45.82,3.7,.7)]
 if axis=='X':
  tools += [box((99,y-2.9,43.42),(x-99,5.8,2.6)),box((99,y-3.7,45.82),(x-99,7.4,.7))];entry=[99,y]
 elif i in [0,2]:
  tools += [box((x-2.9,-83,43.42),(5.8,y+83,2.6)),box((x-3.7,-83,45.82),(7.4,y+83,.7))];entry=[x,-83]
 else:
  tools += [box((x-2.9,y,43.42),(5.8,27-y,2.6)),box((x-3.7,y,45.82),(7.4,27-y,.7)),cyl(x,27,41.42,4.5,5.1)];entry=[x,27]
 pockettools+=tools;pocketrows.append(dict(centre=[x,y],feed_axis=axis,entry=entry,feed_length_mm=abs(x-entry[0])+abs(y-entry[1]),nut_AF_nominal=5.5,nut_pocket_AF=5.8,washer_OD=7,washer_channel_width=7.4,entry_height=3.1,nut_z=[43.62,46.02],washer_z=[46.02,46.52],lower_loading_clearance_mm=.2,roof_web_mm=2,floor_mm=1.9,antirotation_basis='5.8slot width <nut acrosscorners6.35085; enclosedsidewalls2.2mm high, no assumedreleasabletie'))
oldrear=objs['P03_rear_deck_integrated_load_yoke'].Shape;rear=oldrear.copy()
for tool in pockettools:rear=rear.cut(tool)
assert rear.isValid() and len(rear.Solids)==1
expectedrear=oldrear.copy()
for tool in pockettools:expectedrear=expectedrear.cut(tool)
assert expectedrear.cut(rear).Volume<1e-5 and rear.cut(oldrear).Volume<1e-5
objs['P03_rear_deck_integrated_load_yoke'].Shape=rear
# Integrated realbrace + two enclosed rail sockets; purchased board/case positions unchanged.
postxy=[(107,-76),(107,12),(169,-76),(161,12)]
panelmembers=[box((107,-76,88.52),(70,94,3))]+[box((x,y,91.52),(6,6,1)) for x,y in postxy]
panelmembers += [box((107,-52.65,90),(6,103.3,2.5))]
for cy in [-47.5,45.5]:panelmembers += [box((101,cy-5.15,88.52),(12,10.3,3.98))]
paneltools=[cyl(135.5,-29.3289166382,88,12.2,7)]+[cyl(x,y,88,1.65,8) for x,y in centres]+[cyl(x,-29.3289166382,88,3.3,7) for x in [116.5,154.5]]
paneltools += [box((100.5,cy-3.15,90),(9.5,6.3,1.7)) for cy in [-47.5,45.5]]
panel=panelmembers[0]
for m in panelmembers[1:]:panel=panel.fuse(m)
for tool in paneltools:panel=panel.cut(tool)
assert panel.isValid() and len(panel.Solids)==1
coverage=[]
for i,m in enumerate(panelmembers):
 q=m
 for tool in paneltools:q=q.cut(tool)
 missing=q.cut(panel).Volume;assert missing<1e-5,(i,missing);coverage.append(dict(member=i,missing_mm3=missing,extent_mm=bbox(q)))
objs['P06_S0_shared_panel'].Shape=panel
railchanges=[]
for n,cy,postn in [('Upper_frame_rail__49',-47.5,'Upper_frame_post_101__49'),('Upper_frame_rail_44',45.5,'Upper_frame_post_101_44')]:
 o=objs[n];old=o.Shape;body=old.common(box((-105,cy-2,89),(205.5,4,5)));tongue=box((100,cy-3,90),(9.8,6,1.5));q=body.fuse(tongue)
 assert q.isValid() and len(q.Solids)==1;assert q.common(panel).Volume<1e-5
 o.Shape=q;o.AssemblyNote='Onlyunbuilt local railend replaced by6x1.5tongue, netsection9mm2 sameold3x3. Ends109.8 withinclosedP06socket; bottommatched90, sides.15/roof.2/end.2 nominalclearance. Slidebeforefrontframefastening/boards.'
 p=objs[postn];oldp=p.Shape;p.Shape=oldp.common(box((99,cy-3,48),(7,6,40.52)));assert p.Shape.isValid()
 railchanges.append(dict(rail=n,old_bounds_mm=bbox(old),new_bounds_mm=bbox(q),male_tongue_mm=[9.8,6,1.5],male_crosssection_mm2=9,old_crosssection_mm2=9,rear_post=postn,new_rear_post_top=88.52,role='Rail floorbearing andlift/sidecapture via integratedP06socket; rearpost retainedandseatsP06bottom, no missingloadrole'))
# Four fullstandardM3x50 stacks; no shafttrim/partialengagement.
steel=[]
for i,(x,y) in enumerate(centres):
 n='H03_panel_M3x55_'+str(i);o=objs[n];o.Shape=cyl(x,y,42.52,1.5,50).fuse(cyl(x,y,92.52,2.75,3));o.Label='H03 M3x50 complete stack '+str(i);o.Status='NOMINAL_STANDARD_FASTENER_DEMAND_UNCONFIRMED_STOCK'
 nut=objs[n+'_nut'];nu=nut.Shape.copy();nu.translate(V(0,0,5))
 if i!=1:nu.rotate(V(x,y,0),V(0,0,1),90)
 nut.Shape=nu;w=objs[n+'_washer'];wa=w.Shape.copy();wa.translate(V(0,0,5));w.Shape=wa
 assert o.Shape.isValid() and nut.Shape.isValid() and w.Shape.isValid()
 steel.append(dict(screw=o.Name,nominal='M3x50 sockethead',quantity=1,underhead_z=92.52,shaft_tip_z=42.52,nut_z=[43.62,46.02],washer_z=[46.02,46.52],compressed_stack_mm=48.9,tip_beyond_fullnut_mm=1.1,headboss_mm=1,seat_roof_mm=2,stock='NEEDED_UNCONFIRMED_no purchase/cut'))
# Metadata and recoverability checkpoint before allchecks.
for n in ['P03_rear_deck_integrated_load_yoke','P06_S0_shared_panel','P05_S0_panel_spacer40','P07_open_tail_root_U']:
 objs[n].Status='CONDITIONAL_UNPOWERED_FIRST_FIT_PENDING_LOCAL_CHECK'
objs['P06_S0_shared_panel'].AssemblyNote='Oneintegral panel/brace/twoclosed sockets replaces oldUpper_frame_end_105 role, preservingactualS0seat88.52/source11andallboughtposes. Not owningpenetration.'
for o in objs.values():
 if o.Name.startswith('H03'):o.ViewObject.ShapeColor=(.55,.56,.59)
D.Label='WAVEGO fit kit final — conditional unpowered first fit';D.recompute();A.setActiveDocument(D.Name);D.saveAs(str(P/'fit-assembly.FCStd'))
checkpoint=dict(status='GEOMETRY_SAVED_BEFORE_TESTS',created_utc=datetime.now(timezone.utc).isoformat(),source_manifest_sha256=hashlib.sha256((OLD/'manifest.json').read_bytes()).hexdigest(),document=D.Name,objects=len(D.Objects),pocket_plan=pocketrows,steel=steel,logic_support=railchanges,retired_reference='Upper_frame_end_105 replacedbyintegralP06, notpresentinnewdoc',source_case_board_poses='unchanged directshapeassignment',panel_member_coverage=coverage)
(P/'checkpoint.json').write_bytes((json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'saved_before_tests':str(P/'fit-assembly.FCStd'),'objects':len(D.Objects),'source_bought_shapes_changed':False,'new_part_changes':['P03','P06'],'newjoint':steel[0],'elapsed':time.perf_counter()-T}))
# Export onlytwo changedprintparts; unchanged6STLs copiedbyteforbyte.
parts=[]
for row in d['parts']:
 r=dict(row);name=r['name'];out=P/r['stl']
 if name in ['P03_rear_deck_integrated_load_yoke','P06_S0_shared_panel']:
  s=objs[name].Shape;local=s.copy();b=local.BoundBox;local.translate(V(-b.XMin,-b.YMin,-b.ZMin));mesh=Mesh.Mesh(local.tessellate(.08));assert mesh.isSolid();mesh.write(str(out));r.update(bounds_mm=bbox(s),volume_mm3=s.Volume,print_bounds_mm=bbox(local),triangles=mesh.CountFacets,mesh_closed=True,changed=True)
 else:shutil.copyfile(OLD/r['stl'],out);r['changed']=False
 parts.append(r)
(P/'parts.json').write_bytes((json.dumps(parts,ensure_ascii=False,indent=2)+'\n').encode())
print('PRINT EXPORTS SAVED;8unique/13quantity;6unchangedSHA reused')
