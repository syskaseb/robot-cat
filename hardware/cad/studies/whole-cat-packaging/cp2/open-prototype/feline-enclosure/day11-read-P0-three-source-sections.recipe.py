import time,json,math,zipfile,hashlib,os
from pathlib import Path
t15=time.monotonic();c15=time.process_time();layers15={'BASE_CURRENT1292':dict(Current35),'NEUTRAL_MOVING108':dict(restMotion),'ORIGINAL_SOURCE_FRONTL_METAL':{n:s for n,s in source_parts14.items() if n in ['FrameScrewFrontL','FrameNutFrontL','ShellScrewFrontL','ShellNutFrontL']}}
binding15={}
for label,actor in [('MountFrontL','Ref_Material_P0_MountFrontL_0_0'),('NutShoeFrontL','Ref_Material_P0_NutShoeFrontL_0_0')]:
 a=Current35[actor];b=source_parts14[label];ab=a.cut(b);ba=b.cut(a);assert ab.isValid() and ba.isValid();binding15[label]=dict(current_actor=actor,source_world_part=label,current_missing_vs_source_mm3=ba.Volume,source_missing_vs_current_mm3=ab.Volume,both_valid=True,matched_material=ab.Volume<1e-7 and ba.Volume<1e-7)
assert binding15['MountFrontL']['matched_material']
shellheadseat15=source_parts14['ShellScrewFrontL'].BoundBox.YMax-3.;tools15={'LATERAL_M3_SOURCE_TOOL_R2p5x35':Part.makeCylinder(2.5,35,A.Vector(-63.5,shellheadseat15+3.1,56),A.Vector(0,1,0)),'FRAME_M2p5_SOURCE_CHANNEL_R1p5x25':Part.makeCylinder(1.5,25,A.Vector(-70,31.5,45.3),A.Vector(0,0,1))};layers15['SOURCE_TOOL_RESERVATION_NOT_PHYSICAL_MATERIAL']=tools15
# Recover ONLY the missing savedneutralSOURCE21+4temp assembly frompinnedlocalBReps.
slot15=json.loads((OUT/'day07-SOURCE-slot-bearing-retention-whole-proposal.json').read_bytes());leg15=json.loads((OUT/'day07-whole-physical-SOURCE-approach-Knee-link-proposal.json').read_bytes());fr15=leg15['actual_contact_frame'] if 'actual_contact_frame' in leg15 else leg15.get('actual_frame')
fr15=json.loads((OUT/'day07-WHOLE9-north-entry-vertical-before-foreturn-whole-plan.json').read_bytes())['current_moving_holder']['source_actual_frame'];u15=fr15['long_axis_from_actual_face_edge_world'];v15=fr15['transverse_axis_world'];n15=fr15['outward_normal_world'];o15=fr15['contact_face_centre_world_mm'];mat15=A.Matrix()
for i in range(3):
 for j,col in enumerate([u15,v15,n15]):setattr(mat15,'A'+str(i+1)+str(j+1),col[i])
setattr(mat15,'A14',o15[0]);setattr(mat15,'A24',o15[1]);setattr(mat15,'A34',o15[2]);pl15=A.Placement(mat15);op15={};temp15={};op_pins15=[]
for filename,select in [('day07-SOURCE-slot-crosshead-functional-grooves.breps.zip',lambda n:n in ['LOCAL:corrected_whole_lower','LOCAL:unchanged_whole_upper']),('day07-SOURCE-slot-whole-tail-bearing-gate.breps.zip',lambda n:n.startswith(('LOCAL:LOOP:','LOCAL:HEAD:','LOCAL:PULL:','LOCAL:TAIL_PARK:'))),('day07-SOURCE-slot-full-stock-completion.breps.zip',lambda n:n.startswith('LOCAL:TAIL_TRANSPORT:')),('day07-SOURCE-slot-retention-functional-first-gate.breps.zip',lambda n:n.startswith('LOCAL:FULL_PROFILE:'))]:
 with zipfile.ZipFile(OUT/filename) as z:
  gm=json.loads(z.read('manifest.json'))['geometry']
  for q in gm:
   name=q['name']
   if not select(name):continue
   raw=z.read(q['entry']);assert hashlib.sha256(raw).hexdigest()==q['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());vol=s.Volume;s.Placement=pl15*s.Placement;assert s.isValid() and abs(s.Volume-vol)<1e-5
   (temp15 if name.startswith('LOCAL:PULL:') else op15)[name]=s;op_pins15.append(dict(path=filename,entry=q['entry'],sha256=q['sha256'],name=name,world_once=True))
assert len(op15)==21 and len(temp15)==4,(len(op15),len(temp15),list(op15))
knownport15=json.loads((OUT/'day07-SOURCE-new-moving-module-region-first-gate.json').read_bytes())['new_port_frame_rows36'][0];entry15=pl15.multVec(A.Vector(-43,8.5,4));assert (entry15-A.Vector(*knownport15['Knee_entry_world_mm'])).Length<1e-8
layers15['PROPOSED_SOURCE21_NEUTRAL_OPERATING']=op15;layers15['SOURCE4_TEMP_PULL_ONLY']=temp15
g4e15=json.loads((OUT/'day07-SOURCE-G4-common-closure-C1-proposed-actor-effectivity.json').read_bytes());g4dict15={}
for q in g4e15['new_actors']:
 with zipfile.ZipFile(OUT/q['archive']) as z:raw=z.read(q['source_geometry']['entry'])
 assert hashlib.sha256(raw).hexdigest()==q['source_geometry']['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());g4dict15[q['name']]=s
layers15['G4_PROPOSED_ALTERNATIVE_PRINT_LAYER_NOT_ADDITIVE_TO_BASE']=g4dict15
dd15=json.loads((OUT/'day07-D5-disjoint-construction-repair-closure-boundary-bounded-disposition.json').read_bytes())['proposed_effectivity'];d5dict15={}
for key in ['lower','upper']:
 with zipfile.ZipFile(OUT/dd15[key+'_archive']) as z:raw=z.read(dd15[key+'_entry'])
 s=Part.Shape();s.importBrepFromString(raw.decode());d5dict15['D5_DISJOINT_'+key]=s
layers15['D5_PROPOSED_ALTERNATIVE_FRAME_LAYER_NOT_BASE_UNION']=d5dict15;layers15['ACTUAL_BODYOUTER_BOUNDARY']={'BodyOuter31':BodyOuter31}
sections15=[];planes15=[dict(id='A_U1_WEST_MATERIAL_EDGE',x=-126.,reason='ActualretainedU1westmaterialedge, pairedBodyOuterleftwall andmoving/sourceentry; notoldY77portal.'),dict(id='B_SHELL_M3_AND_P0_LOAD_INTERFACE',x=-63.5,reason='ActualMountFrontL lateralM3/shellbearingaxis, selectedmetal+nut/feed/driver andframeM2.5/dowel functions.'),dict(id='C_G4_TRUE9_RECEIVER_DISTRIBUTION',x=28.125,reason='ActualnewG4held9freeend; middlebankseparator betweenP_SYS/V3west andD5east. G4fourleadscountincludesW025; not9atoneport.')]
for sec in planes15:
 x=sec['x'];plane=Part.makePlane(210,180,A.Vector(x,-105,-55),A.Vector(1,0,0),A.Vector(0,1,0));rows=[]
 for layer,dd in layers15.items():
  for name,s in dd.items():
   bb=s.BoundBox
   if not(bb.XMin-1e-7<=x<=bb.XMax+1e-7) or bb.ZMax< -50 or bb.ZMin>112 or bb.YMax< -100 or bb.YMin>100:continue
   if not s.isValid():rows.append(dict(layer=layer,actor=name,status='SOURCE_INVALID_UNRESOLVED_NOT_CONTACT'));continue
   cut=s.section(plane);curves=[]
   for edge in cut.Edges:
    ps=edge.discretize(Deflection=.15)
    if ps:curves.append([[p.y,p.z] for p in ps])
   if curves:rows.append(dict(layer=layer,actor=name,status='ACTUAL_SOURCE_SECTION',curves_YZ=curves,classification='REFERENCE_FLEX_OR_CAPACITY_NOT_RIGIDOBSTACLE' if any(t in name.lower() for t in ['wire','factory','custom','tail','pull','band','loop','profile','capacity']) else 'FUNCTIONAL_MATERIAL_OR_DECLARED_SOURCE_BOUNDARY'))
 sections15.append(dict(**sec,rows=rows,entire_route_or_occupied_free_layer_accepted=False))
source_floor15=json.loads((OUT/'day07-SOURCE-new-moving-module-region-first-gate.json').read_bytes())
p15=OUT/'day11-P0-connected-space-and-load-interface-read.json';r15=dict(id=p15.stem,status='THREE_REAL_SOURCE_INTERFACE_SECTIONS_CONTINUITY_STILL_UNKNOWN_NO_NEW_ROUTE',source_base1292_unchanged=True,effective1311_and_G4_D5_SOURCE_not_newselected=True,current_mount_binding=binding15,mount_role='SeparatePETGshellmount; realframeholes/metal/dowel/shellbearing/tool preserved. Notboughtimmutable/notwirebudget.',source_metal_binding='Originalnative4selectednominalsourcehardware loadedandlabelled; current1292actor-by-actorsteelregistration stillnotproven. Do NOTduplicateintoactivebase/claimsourceexactsteelids.',source_parts_metadata='day11-P0-shell-mount-current-metal-source-binding.json',source21_neutral_data_binding=dict(operating=len(op15),temporary=len(temp15),owner='Motion_RL_Knee',frame_once=True,entry_matches_received_neutral_sourceframe=True,pins=op_pins15,old36motion155_not_replayed=True),layer_policy='Sections showseparateBASE/proposedreplacement/reference layers. NEVERunionbase+proposedparents; wholeactorselectionnotaccepted. Referenceflexcurves andtailfields notrigidobstacles. Whitearea isunqualifiednotfree-space.',sections=sections15,BodyOuter_actual_bounds_mm=saved_bounds(BodyOuter31),source_motion_ports36=source_floor15['new_port_frame_rows36'],moving108_neutral_sections=True,required_new_wire_ground_R_motion_NOT_proven=True,actual9port_frame_source='day11-WHOLE_N01-layout-architecture-and-closure-plan.json',selected_FPI_S0_dependencies='runtime.coordinator_whole_layout_source_dependencies_received; projectpointsnotmanufacturerverified, no immutable210blank/newextension/cut.',prior_first_common_scope='day11oldallocatedcommon17.140621 atPETGupperwallZ59.958..61, NOTmetal/contactproof orallpaths. Current4sourcehardwaredimensionspreserved; allwholefieldmetalclearanceNOTtested.',no_new_curves_prints_grids_or_oldscans=True,all_actual_Li_A_U_fit_slack_cut=None,N01='0/10',operation_seconds=time.monotonic()-t15,process_cpu_seconds=time.process_time()-c15,pid=os.getpid(),session_id=70789);p15.write_bytes((json.dumps(r15,indent=2)+'\n').encode());print('P0_SPACE_READ_SAVED',[(v['id'],len(v['rows'])) for v in sections15],'SOURCE',len(op15),len(temp15),'binding',binding15,'wallCPU',r15['operation_seconds'],r15['process_cpu_seconds'],'OWNER11476_NATIVE_IDLE',flush=True)
