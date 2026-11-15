import FreeCAD as A,FreeCADGui as G,Part,json,hashlib,math,time
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;ROOT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';OLD=OUT/'day15-frame-fastening';P=OUT/'day15-connected-power-fit';P.mkdir(exist_ok=True);S=A.getDocument('DAY15_FRAME_FASTENING');D=A.newDocument('DAY15_CONNECTED_POWER_FIT');groups={};T=time.perf_counter();CPU=time.process_time()
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape;q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for prop in ['AssemblyNote','Status','OriginalSource']:
  if hasattr(o,prop):q.addProperty('App::PropertyString',prop);setattr(q,prop,str(getattr(o,prop)))
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
def box(p,size):return Part.makeBox(*size,V(*p))
def wire_rect(c,u,v,hu,hv):
 pts=[c+u*x+v*y for x,y in [(-hu,-hv),(hu,-hv),(hu,hv),(-hu,hv),(-hu,-hv)]];return Part.Wire(Part.makePolygon(pts).Edges)
def arc(a,m,b):return Part.Arc(a,m,b).toShape()
fieldgrp=D.addObject('App::DocumentObjectGroup','CONNECTED_POWER_CAPACITY_NOT_RIGID_WIRES');fields=[]
def field(n,s,role):
 assert s.isValid(),n;o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.9,.55,.15);o.ViewObject.Transparency=70;fieldgrp.addObject(o);o.addProperty('App::PropertyString','AssemblyNote').AssemblyNote=role;fields.append(dict(name=n,role=role,volume=s.Volume,valid=True));return s
# Full original capacity, no smaller part/protection. This is project flexible allowance, not a boughtport.
xt=D.getObject('XT60H_mated_with_boots');oldvol=xt.Shape.Volume;xt.Shape=box((-96,40,125),(50,24,18));assert abs(xt.Shape.Volume-oldvol)<1e-6;xt.Label='XT60 selectedpair+boots+wire CAPACITY — loose servicebay';xt.AssemblyNote='Same50x24x18fullcapacity, realcase/ports unknown. Loosebattery-side pair, notfixedoriginalworldport. No fabricatedleadlength.'
# Two-core group region, conservative provisionalOD6/1gap/.4outer; true jackets/exit FIT2.
a=V(-2,0,88);b=V(-2,0,106);c=V(-2,24,130);m=V(-2,24-24/math.sqrt(2),106+24/math.sqrt(2))
one=Part.Wire([Part.makeLine(a,b),arc(b,m,c)]).makePipeShell([wire_rect(a,V(1,0,0),V(0,1,0),6.9,3.4)],True,False)
field('POWER_BAT2_VERTICAL_AND_NORTH_TURN',one,'BATfactory+/minus approach, not true deliveredmouth. R24/coreR24; U=X, two6mmcapacityprofiles+1gap+.4outer. OpenbeforeMIC/BUS closure. Ports/length/RactualFIT2.')
a=c;b=V(-30,52,130);m=V(-30+28/math.sqrt(2),24+28/math.sqrt(2),130);two=Part.Wire([arc(a,m,b)]).makePipeShell([wire_rect(a,V(1,0,0),V(0,0,-1),6.9,3.4)],True,False)
field('POWER_BAT2_FORE_TURN',two,'R28centre, individualcoreR>=24.5 under provisional6mm/4ODprojectbasis; whole packet not immutablecircle or individualproductionaxes.')
field('POWER_THREE_CORE_LOOSE_TOP_RETURN',box((-96,41.6,126.6),(146,20.8,6.8)),'BAT2 plus robotnegativeW001 shareaccessibletraylessspace. Three6mmcapacityprofiles+1gaps/.4outside; no new3terminal/9mmseam. Relativefreefan remainsphysicaldrylay, not actualinstalledslack.')
field('POWER_GROUP_BRANCH_AND_LAY_NODE',box((-46,40,125.5),(32,24,18)),'Accessible3corehandlay/fan aboveE1max124, genuinefullpacking volume. Not fixedgrip, no cut or extra termination.')
# Robotnegative one-core branch, passage outside commonlogicstripX26 and MAINledgeX55.
a=V(50,42.4,74);b=V(50,42.4,106);c=V(26,42.4,130);m=V(26+24/math.sqrt(2),42.4,106+24/math.sqrt(2));neg=Part.Wire([Part.makeLine(a,b),arc(b,m,c)]).makePipeShell([wire_rect(a,V(1,0,0),V(0,1,0),3.4,3.4)],True,False)
field('POWER_ROBOT_G1_RISER',neg,'W001 one6mmcapacity profile/R24 project assumption. Riserwindow between stripend26 and ledgestart55; no actualG1mfgmouth claim.')
field('POWER_G1_OPEN_LOWER_AISLE',box((-85,39,70.6),(135,6.8,6.8)),'One robotnegativeG1approach aboveWAGO, outboardofspeakerhangerY35 and inboardofmotorbankY50. FinalG1caseport/mapping/entry notmanufacturerdatum; fixedreceiverstrain afterdrylay.')
field('POWER_F0_SHORT_INPUT_APPROACH',box((-106,46,121),(10,12,14)),'RobotpositiveW075 to adjacentF0. TrueF0exitnormal/lengthUNKNOWN; nominalproject30/retainedlimit50 staysNOTactualcut. No credit/extension ifdeliverydoesnotfacebay.')
field('POWER_DISCONNECT_TOP_ACCESS',box((-96,40,143),(50,24,24)),'Directopen+Z access, actualselectedpairseparationtravel UNKNOWN; fullpairallowance preserved. Removeplannedskin/P15mic and actualBUSends/bridge beforebattery; TTPfixedP14 andE1soldernevervirtualunplug.')
# Conservative connected volumes intersect at branches, do not assume two clear sections mean route.
shapes=[D.getObject(x['name']).Shape for x in fields];edges=[]
for i,s in enumerate(shapes):
 for j,q in enumerate(shapes[i+1:],i+1):
  gap=s.distToShape(q)[0]
  if gap<1e-6:edges.append([fields[i]['name'],fields[j]['name'],s.common(q).Volume])
graph={x['name']:set() for x in fields}
for a,b,v in edges:graph[a].add(b);graph[b].add(a)
seen=set();stack=[fields[0]['name']]
while stack:
 a=stack.pop()
 if a in seen:continue
 seen.add(a);stack.extend(graph[a]-seen)
assert len(seen)==len(fields),('disconnectedregion',set(graph)-seen)
design=ROOT/'hardware/electronics/kicad-current/design.json';src=json.loads(design.read_bytes());wirefacts=[w for w in src['wires'] if w['id'] in ['W001','W075','W076/factory','W076/custom']];materialfacts=[w for w in src['body_material_portions'] if str(w.get('wire','')).startswith(('W001','W075','W076'))]
plan=dict(status='SAVED_ONE_CONNECTED_POWER_ALLOCATION_BEFORE_TESTS',created_utc=datetime.now(timezone.utc).isoformat(),source_manifest=hashlib.sha256((OLD/'manifest.json').read_bytes()).hexdigest(),source_builder=dict(path='C:/Users/Sysq/AppData/Local/Temp/day14-firstfit-build.py',sha256=hashlib.sha256(Path('C:/Users/Sysq/AppData/Local/Temp/day14-firstfit-build.py').read_bytes()).hexdigest(),line86='50x24x18 is selectedpair mating/WIRE allowance; batteryplug/lead flexible'),capacity_full_same_volume_mm3=oldvol,case_capacity_bounds=[[-96,40,125],[-46,64,143]],fields=fields,connected_graph_edges=edges,all_regions_connected=True,nominal_cable_OD_upper_capacity=6,packing_gap=1,outermargin=.4,core_R_project_basis='4xOD6=24; firstYZ24outofplanepacking/XY28gives24.5; notmanufacturerR or old35.1',source_electrical=dict(path=str(design),sha256=hashlib.sha256(design.read_bytes()).hexdigest(),unchanged_graph=wirefacts,proper_portions=materialfacts),interface_assumptions=['Factorybatteryexitapproach(-2,0,88) is explicitphase2frontupperexitassumption, not mfgdatum/freeclock; batterybodyposekept. Actualexit/leadlength/BALANCEtapconnector remainFIT2.', 'SelectedXT60wholepair/mate+boots retained. No modeldecomposition or smallcaseclaim. W075shortF0leg≤50PROJECT hasnotbeenprovedwithrealmouth; directadjacentlinkactualdeliveryFIT2, no extension/cut.', 'RobotG1currentselectedelectricalrole andlever/terminalentrymustbedrylaid; no newwire/connector/graphchange. W076factoryfulllead/POST_F0 andcustomS0 path retained, not newdebit.', 'Movingbattery/unplugstock +fixedrobotrelief nearF0/G1 notuniversalclamp. Allnewregionsareloose transfer/handlay, not fixedgrip; no actualoperatingslack/lengthPASS.', 'Threecores inupperreturn are battery+/batteryminus and existingrobotminusW001, not3newterminals. Pairbaytwoelectricalpoles notnewsplice.'],assembly='Benchframe+fullsourceends ->openlowervoltage/powerlay andnominalshortF0match ->PCB/audio/keeperslast. Battery:skin/P15mic actualUSB->BUSexistingpower/USB/P13->disconnectXT60+existingbalanceinterface inopentopbay ->battery. TTPP14/E1lead stayfixed. Physicaltrialmaypartialdemount, notquickservice.',physical_pass=False,actual_installed_cut_slack=None,print_material_changed=False,new_bought_pose_changed=False)
(P/'power-space-plan.json').write_bytes((json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode());D.Label='DAY15 connectedpower — nominalspace checks pending';D.recompute();A.setActiveDocument(D.Name);D.saveAs(str(P/'connected-power-fit.FCStd'));print(json.dumps({'saved_beforetests':D.FileName,'objects':len(D.Objects),'capacity_preserved':oldvol,'graph_nodes':len(fields),'graph_edges':len(edges)}))
