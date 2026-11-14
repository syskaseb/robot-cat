import FreeCAD as A,Part,json
from pathlib import Path
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit/foundation-fit-kit')
D=A.getDocument('DAY14_FOUNDATION_FIT_KIT');r=json.loads((P/'foundation-kit.json').read_bytes())
def seat(a,b,z):
 sa=D.getObject(a).Shape if isinstance(a,str) else a;sb=D.getObject(b).Shape if isinstance(b,str) else b
 def faces(s):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.BoundBox.ZLength<1e-6 and abs(f.BoundBox.ZMin-z)<1e-6]
 area=0;normalisation=[]
 for f in faces(sa):
  fa=f.copy();dz=z-fa.BoundBox.ZMin;normalisation.append(dz);fa.translate(A.Vector(0,0,dz))
  for g in faces(sb):
   fb=g.copy();dz2=z-fb.BoundBox.ZMin;normalisation.append(dz2);fb.translate(A.Vector(0,0,dz2));area+=fa.common(fb).Area
 assert area>1e-4,(a,b,'No useful bearingface',area)
 return dict(a=a if isinstance(a,str) else 'sourceTopCoverSolid38',b=b,seat_z_mm=z,actual_coplanar_face_intersection_mm2=area,max_numerical_plane_normalisation_mm=max(map(abs,normalisation)),model_geometry_changed=False)
pairs=[('P01_load_rail','P02_front_deck',45.52),('P01_load_rail_instance2','P02_front_deck',45.52),('P01_load_rail','P03_rear_deck_integrated_load_yoke',41.52),('P01_load_rail_instance2','P03_rear_deck_integrated_load_yoke',41.52),('P04_deck_splice','P02_front_deck',45.52),('P04_deck_splice','P03_rear_deck_integrated_load_yoke',45.52),('P04_deck_splice_instance2','P02_front_deck',45.52),('P04_deck_splice_instance2','P03_rear_deck_integrated_load_yoke',45.52),('P07_open_tail_root_U','P03_rear_deck_integrated_load_yoke',52.52)]
for n in ['P05_S0_panel_spacer40','P05_spacer_instance2','P05_spacer_instance3','P05_spacer_instance4']:
 pairs += [(n,'P03_rear_deck_integrated_load_yoke',48.52),(n,'P06_S0_shared_panel',88.52)]
out=[seat(a,b,z) for a,b,z in pairs]
cover=D.getObject('WAVEGO_complete_126_source_solids').Shape.Solids[38]
out += [seat(cover,'P01_load_rail',38.52),seat(cover,'P01_load_rail_instance2',38.52)]
r['actual_bearing_faces']=out
r['contact_method_note']='Solid.common returned zero area for disjointtangent solids, which is NOTmissing bearingproof. Actual planar face-face intersections measured separately at equalZ (normalisation<1e-10mm only on analysis copies); positive areas not strengthcertification.'
panel=D.getObject('P06_S0_shared_panel').Shape;brace=D.getObject('Upper_frame_end_105').Shape
c=panel.common(brace)
r['unbuilt_logic_reference_interface']=dict(new='P06_S0_shared_panel',reference='Upper_frame_end_105',common_mm3=c.Volume,common_valid=c.isValid(),classification='UNBUILT_PROJECT_REFERENCE_MATERIAL_INTERFACE_HOLD_NOT_BOUGHT_COLLISION',required='Integrate or replace this unbuilt logicframe branch by actual functional load connection before fabricating upper electronics mount. No reference deletion/ownwaiver done by recovery.')
holds=[x for x in r['changed_named_hazards'] if x['status']=='HOLD_NOMINAL_HARDWARE_OR_MATERIAL_CLEARANCE']
r['decision']='SAME_PRINT_GEOMETRY_RECOVERED_TEMPLATE_AND_PRIMARY_FOUNDATION_FIT_ONLY_REAR_S0_FIXING_HOLD'
r['first_falsifier']=holds[0] if holds else None
r['release_scope']=dict(P00='READY_FOR_UNPOWERED_8AXIS_TEMPLATE_TRIAL',P01_P04='FOUNDATION_FIT_EXPORTS_CONDITIONAL_SOURCETHREAD_8HOLE_MOTION_PAYLOAD',P05_P07='FIT_GEOMETRY_ONLY_NOT_LOADED_ASSEMBLY_RELEASE_untilS0boltstack_and_logic_reference_resolved',whole_cat='NOT_RELEASED')
r['review_dispositions'][0].update(status='PRINT_LOAD_SEATS_POSITIVE_BUT_REAR_FIXING_HOLD',evidence='All19real bearingfaces positive, zero separate-print overlap; samegeometry8STLSHA preserved. ActualH03M3x55 tip touches retainedTopCover, gap~0<1.25; no waiver. Oldunbuiltlogicbrace also intersects newS0panel, sourceparts retained.')
r['native_pid']=8920
(P/'foundation-kit.json').write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'received_bearing_faces':len(out),'minimum_face_area_mm2':min(x['actual_coplanar_face_intersection_mm2'] for x in out),'max_normalisation_mm':max(x['max_numerical_plane_normalisation_mm'] for x in out),'first_falsifier':r['first_falsifier'],'unbuilt_logic_interface':r['unbuilt_logic_reference_interface'],'same_geometry':True}))
