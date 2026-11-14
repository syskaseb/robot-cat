import FreeCAD as A,FreeCADGui as G,Part,Mesh,json,math,hashlib,csv,time
from pathlib import Path
from datetime import datetime,timezone
T=time.perf_counter();V=A.Vector
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit/foundation-fit-kit')
P.mkdir(exist_ok=True);(P/'stl').mkdir(exist_ok=True)
B=P.parent;baseline=json.loads((B/'layout.json').read_bytes());old=next(d for d in A.listDocuments().values() if d.FileName and Path(d.FileName).resolve()==(B/'first-fit.FCStd').resolve())
D=A.newDocument('DAY14_FOUNDATION_FIT_KIT');D.Label='WAVEGO foundation fit kit — conditional prototype'
refs=D.addObject('App::DocumentObjectGroup','Retained_whole_layout_REFERENCE')
prints=D.addObject('App::DocumentObjectGroup','PRINT_PARTS_world_assembly')
hardware=D.addObject('App::DocumentObjectGroup','USED_FASTENERS_nominal_fit')
trial=D.addObject('App::DocumentObjectGroup','FIT_REFERENCES_not_print')
removed=['Load_rail_','Deck_front_blank','Deck_rear_blank','Rear_crossbeam','Rear_S0_shared_panel_BLANK','S0_panel_sharedpost_','Tail_shared_root','Lower_data_open']
copied=[];objects={};report={};partdata=[];assemblyparts={};intended={};fast=[]
def bounds(s):
 b=s.BoundBox;return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
def feature(n,s,g,color=(.72,.7,.61),notes=''):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=color;o.addProperty('App::PropertyString','Status').Status='CONDITIONAL_FOUNDATION_MOCKUP_NOT_WHOLE_ROBOT_PASS';o.addProperty('App::PropertyString','AssemblyNote').AssemblyNote=notes;g.addObject(o);objects[n]=o;return o
for r in baseline['rows']:
 if any(r['id'].startswith(k) for k in removed):continue
 a=old.getObject(r['object']);o=feature(r['id'],a.Shape.copy(),refs,a.ViewObject.ShapeColor,r['notes']);o.ViewObject.Transparency=a.ViewObject.Transparency
 o.addProperty('App::PropertyString','OriginalSource').OriginalSource=r.get('source','');copied.append(r['id'])
# The 16 cases are physically movable trial locations, NOT16frozen dedicated holders.
electrical=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/electronics/kicad-current/design.json')
graph=json.loads(electrical.read_bytes());mods={m['ref']:m for m in graph['modules'] if '221-415' in m.get('value','')}
roles=[('D_FL','DATA'),('D_FR','DATA'),('D_RL','DATA'),('D_RR','DATA'),('FL_P','POSITIVE'),('FR_P','POSITIVE'),('RL_P','POSITIVE'),('RR_P','POSITIVE'),('P_AUX','POSITIVE'),('FL_G','GROUND'),('FR_G','GROUND'),('RL_G','GROUND'),('RR_G','GROUND'),('G2','GROUND'),('G_AUX','GROUND'),('G_TAIL','GROUND')]
ids=['WAGO415_data_%s_%s'%(side,i) for side in [-1,1] for i in range(8)];mapping=[]
for n,(ref,role) in zip(ids,roles):
 o=objects[n];o.Label='WAGO415 '+ref+' / '+role+' — adjustable trial'
 o.AssemblyNote='Physical station 221-415 / exact sourcegraph pins unchanged; provisional movable case location. No port/bend-room acceptance from3mmgap.'
 nets=sorted({p['net'] for p in mods[ref]['pins']});mapping.append(dict(object=o.Name,old_geometry_id=n,station=ref,role=role,nets=nets,pins=mods[ref]['pins'],bounds_mm=bounds(o.Shape),mount='shared open deck / slots; no dedicated holder frozen'))
for n,x in [('WAGO415_data_1_7',133),('WAGO415_data_-1_7',155)]:
 o=objects[n];s=o.Shape.copy();b=s.BoundBox;s.translate(V(x-b.XMin,20-b.YMin,0));o.Shape=s
 next(r for r in mapping if r['old_geometry_id']==n)['bounds_mm']=bounds(s)
feature('Mixed_DATA_POWER_GROUND_open_lay_region',Part.makeBox(177,16,11,V(-48,-8,50.52)),trial,(.9,.6,.18),'Mixed electrical branches share space, not electrical commoning; conductor assignment remains sourcegraph. Ports/stock openbench first.').ViewObject.Transparency=88
def cub(p,d):return Part.makeBox(*d,V(*p))
def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,V(x,y,z))
def holes(shape,rows,z,h,r):
 for x,y in rows:shape=shape.cut(cyl(x,y,z,r,h))
 return shape
source_axes=[(x,y) for x in [-80,-70,112,122] for y in [-22.5,22.5]]
join_axes=[(x,y) for x in [24,36] for y in [-44,44]]
post_xy=[(107,-76),(107,12),(169,-76),(161,12)]
post_axes=[(x+3,y+3) for x,y in post_xy]
tail_axes=[(x,y) for x in [185,191] for y in [-9,9]]
def slot(x,y,z,L,W,H):
 return cub((x-L/2+W/2,y-W/2,z),(L-W,W,H)).fuse(cyl(x-L/2+W/2,y,z,W/2,H)).fuse(cyl(x+L/2-W/2,y,z,W/2,H))
slottools=[slot(x,y,40,20,4.5,15) for x in [-55,-5,45,95] for y in [-70,70]]
def finishpart(n,members,tools,qty=1,print_rotation=None,note=''):
 s=members[0]
 for m in members[1:]:s=s.fuse(m)
 for t in tools:s=s.cut(t)
 assert s.isValid() and len(s.Solids)==1,(n,'invalid or disconnected',len(s.Solids))
 losses=[]
 for j,m in enumerate(members):
  q=m
  for t in tools:q=q.cut(t)
  losses.append(q.cut(s).Volume)
 assert max(losses or [0])<1e-5,(n,losses)
 o=feature(n,s,prints,notes=note);assemblyparts[n]=s;intended[n]=dict(member_count=len(members),missing_mm3=losses)
 local=s.copy()
 if print_rotation:local.rotate(V(),*print_rotation)
 b=local.BoundBox;local.translate(V(-b.XMin,-b.YMin,-b.ZMin));mesh=Mesh.Mesh(local.tessellate(.08));mesh.write(str(P/'stl'/str(n+'.stl')))
 assert mesh.isSolid(),(n,'mesh not closed')
 partdata.append(dict(name=n,quantity=qty,assembly_object=o.Name,bounds_mm=bounds(s),volume_mm3=s.Volume,print_bounds_mm=bounds(local),stl='stl/'+n+'.stl',triangles=mesh.CountFacets,mesh_closed=mesh.isSolid(),print_orientation='flat bottom Z0' if not print_rotation else 'long column on its side; Zheight6',member_coverage=intended[n],notes=note))
 return s
# Two equal rails: rear step meets the integrated rear yoke without overlapping separate prints.
rail=cub((-86,-27.5,38.52),(214,10,7));rearstep=cub((104,-28,41.52),(25,11,5));rail=rail.cut(rearstep)
railtools=[cyl(x,-22.5,38,1.4,9) for x in [-80,-70,112,122]]
rail=finishpart('P01_load_rail',[rail],railtools,qty=2,note='214x10;7high, rear24mm steps down to3high. One geometry printed2x; eight source-axis clearanceholes2.8mm. Frame thread not asserted.')
# Replace the displayed first rail by same local geometry for opposite side; only one STL.
rail2=rail.copy();rail2.translate(V(0,45,0));feature('P01_load_rail_instance2',rail2,prints);assemblyparts['P01_load_rail_instance2']=rail2
front_members=[cub((-105,-82,45.52),(135,164,3)),cub((-105,-79,42.52),(135,3,3)),cub((-105,76,42.52),(135,3,3))]
front_tools=[cyl(x,y,41,1.4,10) for x,y in source_axes if x<30]+[Part.makeCone(1.4,2.5,1.1,V(x,y,47.42)) for x,y in source_axes if x<30]+[cyl(x,y,41,1.65,10) for x,y in join_axes if x<30]+slottools
front=finishpart('P02_front_deck',front_members,front_tools,note='135x164,3mm deck plus3mm edge ribs. Open adjustable slots, not16dedicated WAGO holders.')
rear_members=[cub((30,-82,45.52),(147,164,3)),cub((104,-82,41.52),(73,164,4)),cub((169,-18,41.52),(29,36,7)),cub((171,-15,48.52),(27,30,4)),cub((30,-79,42.52),(147,3,3)),cub((30,76,42.52),(147,3,3))]
rear_tools=[cyl(x,y,40,1.4,12) for x,y in source_axes if x>30]+[Part.makeCone(1.4,2.5,1.1,V(x,y,47.42)) for x,y in source_axes if x>30]+[cyl(x,y,40,1.65,20) for x,y in join_axes if x>30]+[cyl(x,y,40,1.65,18) for x,y in post_axes+tail_axes]+slottools
rear=finishpart('P03_rear_deck_integrated_load_yoke',rear_members,rear_tools,note='Rear fullwidth endsX177, narrow tail tongueX198; no floating outside-deck posts. 4mm yoke under deck to stepped rail shoulders; tailseat top52.52. Fits168x164 print footprint.')
strappart=cub((20,-50,42.52),(20,12,3));strappart=finishpart('P04_deck_splice', [strappart],[cyl(x,-44,42,1.65,5) for x in [24,36]],qty=2,note='Two underside straps bridge actual deck seam; two M3x10 per strap, nuts/washers below.')
strap2=strappart.copy();strap2.translate(V(0,88,0));feature('P04_deck_splice_instance2',strap2,prints);assemblyparts['P04_deck_splice_instance2']=strap2
# Four explicit separate40mm spacers; full seating planes contact deck48.52 and panel88.52.
post=cub((107,-76,48.52),(6,6,40))
post=finishpart('P05_S0_panel_spacer40',[post],[cyl(110,-73,48,1.65,42)],qty=4,print_rotation=(V(0,1,0),90),note='6x6x40, bore3.3; top/bottom matched seating, separate disjoint print. Side-print to avoid tiny40mm tower.')
for i,(x,y) in enumerate(post_xy[1:],2):
 s=post.copy();s.translate(V(x-107,y+76,0));feature('P05_spacer_instance'+str(i),s,prints);assemblyparts['P05_spacer_instance'+str(i)]=s
panelmembers=[cub((107,-76,88.52),(70,94,3))]+[cub((x,y,91.52),(6,6,2)) for x,y in post_xy]
paneltools=[cyl(135.5,-29.3289166382,88,12.2,7)]+[cyl(x,y,88,1.65,8) for x,y in post_axes]+[cyl(x,-29.3289166382,88,3.3,7) for x in [116.5,154.5]]
panel=finishpart('P06_S0_shared_panel',panelmembers,paneltools,note='Actual body seatingZ88.52, neck22 within24.4aperture.2M6clearance at38pitch are PROJECTfamily nominal, not actual delivered thread proof; dryfit only before S0 fastening. Four2mm bosses yield completeM3x55 stack.')
tailmembers=[cub((171,-15,52.52),(27,30,4)),cub((178.5,-15,55.52),(3,30,51.48)),cub((195,-15,55.52),(3,30,51.48))]
tail=finishpart('P07_open_tail_root_U',tailmembers,[cyl(x,y,52,1.65,6) for x,y in tail_axes],note='Open sides and top for four base screws/driver; useful two cheeks to sourcefuture MG interface. No production tailshaft/servo tabs released.')
template=holes(cub((-86,-27.5,0),(214,55,1.2)),source_axes,-.5,3,1.4)
template_mesh=Mesh.Mesh(template.tessellate(.08));st=template.copy();st.translate(V(86,27.5,0));Mesh.Mesh(st.tessellate(.08)).write(str(P/'stl'/'P00_eight_hole_template.stl'))
feature('P00_eight_hole_template_REFERENCE',template,trial).ViewObject.Visibility=False
partdata.append(dict(name='P00_eight_hole_template',quantity=1,stl='stl/P00_eight_hole_template.stl',print_bounds_mm=[[0,0,0],[214,55,1.2]],mesh_closed=template_mesh.isSolid(),notes='First small cheaptemplate. No screws forced if physical8axes/thread do not match. NOT assembled structuralpart.'))
# Only fasteners actually used for this kit. Nominal standard envelopes, stock availability UNKNOWN.
def screw(n,x,y,under,length,diam=3,head_d=5.5,head_h=3,washer=False,nut_bottom=None):
 s=cyl(x,y,under-length,diam/2,length).fuse(cyl(x,y,under,head_d/2,head_h));o=feature(n,s,hardware,(.55,.56,.59));fast.append(dict(name=n,kind='screw',diameter_mm=diam,length_mm=length,underhead_z=under,bounds_mm=bounds(s),shaft_end_z=under-length,availability='NEEDED_UNCONFIRMED_NOT_PURCHASED'))
 if nut_bottom is not None:
  pts=[V(x+3.175*math.cos(math.pi*j/3),y+3.175*math.sin(math.pi*j/3),nut_bottom) for j in range(7)]
  nut=Part.Face(Part.Wire(Part.makePolygon(pts).Edges)).extrude(V(0,0,2.4)).cut(cyl(x,y,nut_bottom-.1,1.5,2.6));feature(n+'_nut',nut,hardware,(.55,.56,.59))
 if washer:
  z=nut_bottom+2.4;w=cyl(x,y,z,3.5,.5).cut(cyl(x,y,z-.1,1.6,.7));feature(n+'_washer',w,hardware,(.6,.6,.62))
for i,(x,y) in enumerate(source_axes):
 s=cyl(x,y,32.52,1.25,14.9).fuse(Part.makeCone(1.25,2.35,1.1,V(x,y,47.42)))
 feature('H01_source_M2p5x16_flat_'+str(i),s,hardware,(.55,.56,.59));fast.append(dict(name='H01_'+str(i),kind='M2.5x16 countersunk overalllength',diameter_mm=2.5,length_mm=16,top_z=48.52,shaft_end_z=32.52,availability='NEEDED_UNCONFIRMED_NOT_PURCHASED'))
for i,(x,y) in enumerate(join_axes):screw('H02_splice_M3x10_'+str(i),x,y,48.52,10,washer=True,nut_bottom=39.62)
for i,(x,y) in enumerate(post_axes):screw('H03_panel_M3x55_'+str(i),x,y,93.52,55,washer=True,nut_bottom=38.62)
for i,(x,y) in enumerate(tail_axes):screw('H04_tailbase_M3x20_'+str(i),x,y,56.52,20,washer=True,nut_bottom=38.62)
report['fasteners']=[dict(role='8source anchors',count=8,nominal='M2.5x16 countersunk overalllength, sourcehole2.6/frame2.05; deck90deg5.0countersink leaves1.9mmfloor',source='Nominal size inferred from actual hole axes ONLY; factorythread/actualgrip/stockUNKNOWN, firsttemplate and handfit before load. NO frame drill/tap'),dict(role='2decksplices',count=4,nominal='M3x10 +M3nut2.4 +onebottomwasher0.5',stack_mm=8.9,source='New standard fit-kit hardware demand; availability UNKNOWN'),dict(role='4S0panel spacers',count=4,nominal='M3x55 +M3nut2.4 +onebottomwasher0.5',stack_mm=54.9,source='New nominal hardware demand UNKNOWN; integrated2mmheadboss. Fullnut engagement~0.1tip projection by nominal stack'),dict(role='tailroot base',count=4,nominal='M3x20 +M3nut2.4 +onebottomwasher0.5',stack_mm=17.9,source='New nominal hardware demand UNKNOWN'),dict(role='S0case family mount',count=2,nominal='M6x12 PROJECTpattern38mm, delivered engagementUNKNOWN',source='NOT installed/claimed hardware in kit; two panel test holes only; physicalcase attachment fit prerequisite before loading S0')]

# Recoverability checkpoint BEFORE any validation against retained source.
D.Label='WAVEGO foundation fit kit — same geometry recovered';D.recompute();D.saveAs(str(P/'foundation-assembly.FCStd'))
checkpoint=dict(status='GEOMETRY_SAVED_VALIDATION_PENDING',document=D.Name,object_count=len(D.Objects),parts=partdata,station_mapping=mapping,fasteners=report['fasteners'],saved_utc=datetime.now(timezone.utc).isoformat())
(P/'foundation-recovery-checkpoint.json').write_bytes((json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n').encode())
expected=json.loads((P/'same-geometry-before-recovery.json').read_bytes())
actual={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in (P/'stl').glob('*.stl')}
assert expected==actual,'Printed geometry changed during service recovery'
report['same_print_geometry_all8_SHA_identical']=True

# Useful actual load connections are separate-part seating with bolts, not fused boughtframe.
contacts=[]
for a,b in [('P01_load_rail','P02_front_deck'),('P01_load_rail','P03_rear_deck_integrated_load_yoke'),('P01_load_rail_instance2','P03_rear_deck_integrated_load_yoke'),('P05_S0_panel_spacer40','P03_rear_deck_integrated_load_yoke'),('P05_S0_panel_spacer40','P06_S0_shared_panel'),('P07_open_tail_root_U','P03_rear_deck_integrated_load_yoke')]:
 s=assemblyparts[a];t=assemblyparts[b];gap=s.distToShape(t)[0];contact_shape=s.common(t);common=contact_shape.Volume;assert gap<1e-6 and common<1e-5,(a,b,gap,common)
 contacts.append(dict(a=a,b=b,gap_mm=gap,positive_overlap_mm3=common,contact_area_mm2=contact_shape.Area,connection='matched seat + explicitly modeled complete fastener stack, no boughtfusion'))
report['contacts']=contacts
separate=[]
names=list(assemblyparts)
for i,a in enumerate(names):
 for b in names[i+1:]:
  sa=assemblyparts[a];sb=assemblyparts[b]
  if not sa.BoundBox.intersect(sb.BoundBox):continue
  c=sa.common(sb).Volume
  assert c<1e-5,('separate prints overlap',a,b,c)
  separate.append(dict(a=a,b=b,common_mm3=c))
report['separate_print_material']=separate

base=objects['WAVEGO_complete_126_source_solids'].Shape
solids=base.Solids;assert len(solids)==126
source_bounds=[q.BoundBox for q in solids]
def lowergap(a,b):
 return math.sqrt(sum(max(lo1-hi2,lo2-hi1,0)**2 for lo1,hi1,lo2,hi2 in [(a.XMin,a.XMax,b.XMin,b.XMax),(a.YMin,a.YMax,b.YMin,b.YMax),(a.ZMin,a.ZMax,b.ZMin,b.ZMax)]))
hazards=[];exact_failed=False
targets=[(n,assemblyparts[n]) for n in ['P03_rear_deck_integrated_load_yoke','P06_S0_shared_panel','P07_open_tail_root_U']]+[(o.Name,o.Shape) for o in hardware.Group if not o.Name.startswith('H01')]
for n,shape in targets:
 b=shape.BoundBox;lower=[lowergap(b,q) for q in source_bounds];candidates=[i for i,x in enumerate(lower) if x<1.25-1e-7]
 row=dict(name=n,vs='retainedbase source Solids by actualworldBBox',full_neighbor_criterion='All126source solids included in numeric distance bound; exact ONLYbboxlower<1.25 and simpleplane/cylinder<=100faces; stop exactafterfirstHOLD',source_solids_total=126,candidate_indices=candidates,gap_mm=min(lower),distance_type='CERTIFIED_AABB_LOWER_BOUND',status='CLEAR_LOWER_BOUND' if not candidates else 'UNKNOWN_LOCAL_CANDIDATE',exact=[])
 if candidates and not exact_failed:
  for i in candidates:
   q=solids[i]
   simple=len(q.Faces)<=100 and all(isinstance(f.Surface,(Part.Plane,Part.Cylinder,Part.Cone)) for f in q.Faces)
   if not simple:
    row['exact'].append(dict(source_solid=i,status='OPEN_nontrivialsource_notruninGUI',faces=len(q.Faces)));continue
   gap=shape.distToShape(q)[0];common=shape.common(q).Volume
   row['exact'].append(dict(source_solid=i,gap_mm=gap,common_mm3=common,faces=len(q.Faces),source_bounds_mm=bounds(q),valid=q.isValid()))
   if gap<1.25-1e-7 or common>1e-5:
    row.update(status='HOLD_NOMINAL_HARDWARE_OR_MATERIAL_CLEARANCE',gap_mm=gap,distance_type='ACTUAL_LOCAL_FULL_OPERANDS');exact_failed=True;break
  if not exact_failed and row['exact'] and all('gap_mm' in x and x['gap_mm']>=1.25-1e-7 for x in row['exact']):row['status']='CLEAR_BOUNDED_LOCAL_OPERANDS'
 elif candidates:row['status']='UNRECEIVED_EXACT_AFTER_FIRST_HOLD'
 hazards.append(row)
 (P/'foundation-local-check-cursor.json').write_bytes((json.dumps(hazards,indent=2)+'\n').encode())
report['changed_named_hazards']=hazards
report['scope_of_cull']='Only NEW parts/steel vs realnearby retainedbase, numericalworld126index. No exact compound126, oldmatrix or implicit waiver. Complex source candidates remain OPEN, no GUI blocking worker.'
report['retained_reference_interface_notes']=[dict(new_part='P06_S0_shared_panel',old_unbuilt='Upper_frame_end_105 / rear logic rails',status='OPEN_NOT_MOUNT_RELEASE',reason='Raised actual S0 seatingpanel88.52..91.52 versus old unbuiltlogicbrace90..93 has overlapping necessarybounds; retain as dependency, no automaticown or hiddenretirement. Printed8STLs unchanged by recovery.')]
report['source_root_hardware_caveat']='H01 nominalM2.5 shaft intentionally passes source2.05 unspecificthread feature; no digitalOWN/threadfit claim, physicaltemplate/handthread first. No boughtmaterial modified.'
# S0 full11 remain unchanged, guard skin and projectcasehole fit explicit.
s0=Part.makeCompound([o.Shape for n,o in objects.items() if n.startswith('S0_') and n in copied])
report['S0_panel_actual_source']=dict(body_panel_common_mm3=objects['S0_body'].Shape.common(panel).Volume,neck_panel_common_mm3=objects['S0_neck'].Shape.common(panel).Volume,seat_z=88.52,neck_clearance_nominal_mm=1.2,source11preserved=True,M6='PROJECTpattern not delivered supplierdatums; two holes are test only')
assert report['S0_panel_actual_source']['body_panel_common_mm3']<1e-5
assert report['S0_panel_actual_source']['neck_panel_common_mm3']<1e-5
# Adjustable BUS fit shelf, not fixed production spacers: keep originalnominal PCB room flags.
objects['BUS_upper_simple_shelf'].AssemblyNote='ADJUSTABLE_TRIAL only: original123..126 shelf overlaps Pi coolingreserve3.12mm; no actualcollisionclaim. Do not fabricate fixed spacers until real Pi/BUS/connectors placed.'
report['review_dispositions']=[dict(id=1,status='REAR_PRINT_LOAD_PATH_REALIZED',evidence='Integratedrear yoke seats steppedrails at41.52; posts seatdeck48.52, panel88.52; tailpad52.52. Actual complete nominalM3stacks, separateprints zero overlap; sourceframe thread physicalunknown'),dict(id=2,status='CORRECTED_16_STATIONS_4DATA_5POSITIVE_7GROUND',evidence='One-to-one exactnet/pin sourcegraph mapping. All casepositions adjustable trial; no 3mmgap portproof'),dict(id=3,status='OPEN_BENCH_ENDS_FIT_BEFORE_DEDICATED_HOLDERS',evidence='4independent220/factoryendpairs, 5FHAC>=84.5leads, fullUSB500+Delock retained; template/foundation does not freeze terminals'),dict(id=4,status='BUS_ADJUSTABLE_TRIAL_ONLY',evidence='3.12nominalreserveoverlap retained; shelfnotfixedproductionfixture'),dict(id=5,status='CARDBOARD_WHOLE_OUTLINE_NEXT',evidence='Rearfullwidth177 vsoldcosmetic170; narrowtailtongue198. Currentfullparts/ports shown, no finalskinrelease')]
D.recompute();A.setActiveDocument(D.Name);G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll()
D.Label='WAVEGO foundation fit kit — conditional prototype';D.saveAs(str(P/'foundation-assembly.FCStd'))
report.update(status='FOUNDATION_FIT_GEOMETRY_EXPORTED_HOLD_IF_LOCAL_HARDWARE_UNRESOLVED',started_utc='2026-11-14T21:50:58.0999965Z',saved_utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.perf_counter()-T,document=D.Name,object_count=len(D.Objects),parts=partdata,station_mapping=mapping,retained_reference_ids=copied,source_baseline_manifest_sha256=hashlib.sha256((B/'manifest.json').read_bytes()).hexdigest(),source_electrical_sha256=hashlib.sha256(electrical.read_bytes()).hexdigest(),print_plan='PETG0.2layer/4walls/5top-bottom/35percentinfill proposal; no slicing/physicalprint; source8holetemplate FIRST, no force/no realframecut. Parts normalised topositiveXYZ;2rails/2splices/4posts quantitiesexplicit.',assembly_order=['First print1.2mm8holetemplate and handcheck actualframeaxes/thread/8screwgrip; stopif mismatch','Fit2steppedrails sourceframe ontopcover, slide front/rear deck halves overrails, insert8source bolts finger-tight only after correctthread confirmed','Fit2underside M3splices, rearrootuses4rear sourcebolts throughactualyoke shoulders; nuts/tools before electronics/battery','Seat4panelspacers oncontinuousreardeck; alignpaneloveractualS0neck/bodyseat, install4M3x55+bottomnuts/washers throughbosses','S0 twoM6 nominaltestholes needactualcasefit before fastening/load; do not drill boughtcase. Terminalshield remains necessary','InstallopentailU with4M3x20 intointegrated52.52pad; top/side access remainsopen beforefutureMG tabs','Openbenchstation/end trials before clamps: electricalgraphrolesnotgeometryIDs; batterytray, upperboards and skin late'],unknowns=['ActualWAVEGOthread/revision/8screwgrip and prototypepayload/legmotion','Fullselectedends/ports/shortleads, S0familycasefasteners/terminalguard and openbenchstockfit','ActualPiBUSstack and fullcardboardOlaoutline/headtail interfaces; no fixedBUSspacers or productionmechanism'])
(P/'foundation-kit.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'saved':str(P/'foundation-assembly.FCStd'),'parts':len(partdata),'totalprintquantity':sum(r['quantity'] for r in partdata),'contacts':contacts,'minimum_received_gap_or_lower_bound':min(r['gap_mm'] for r in hazards if r['name'].startswith('H')),'objects':len(D.Objects),'elapsed':time.perf_counter()-T}))
