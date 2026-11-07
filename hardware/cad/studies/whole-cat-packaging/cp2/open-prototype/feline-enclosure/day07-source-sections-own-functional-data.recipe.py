# Save actual current sections plus new crown's own functional contacts only; stopped foreign key remains unreceived.
st138=time.monotonic();cp138=time.process_time();sec138=[]
for yy in [0,-23]:
 plane=Part.makePlane(120,90,A.Vector(-145,yy,0),A.Vector(0,1,0))
 for n,s in [('CURRENT_FRAME',ff137),('NEW_CROWN_COMPLETE',union137),('FULL145_BAND_NOMINAL',bandphys137),('FULL6_ROOT_HEAD',headroot137),('F_PI_CASING_ALLOCATION',ctx121['F_PI:registered_casing_reservation'])]:
  sh=s.section(plane);curves=[]
  for e in sh.Edges:curves.append([[v.x,v.z] for v in e.discretize(Deflection=.025)])
  sec138.append(dict(Y_mm=yy,name=n,curves_xz=curves))
newown138=[]
for i,x in [(16,-85.4575664610479),(99,-83.9575664610479)]:
 f=Part.Face(Part.Wire(Part.makePolygon([A.Vector(x,y,z) for y,z in [(-4.5,33.5),(4.5,33.5),(4.5,35.51),(-4.5,35.51),(-4.5,33.5)]]).Edges));c=ff137.Faces[i].common(f);newown138.append(dict(role='NEW_SPLIT_CAPTURE_ANTIROTATION_SIDE',face=i,valid=c.isValid(),contact_area_mm2=c.Area))
cc138=bandphys137.common(union137);cf138=bandphys137.common(ff137)
r138=dict(id='day07-W068-top-bearing-functional-sections-and-own-contacts',status='NEW_ROOT_FUNCTION_DATA_ONLY_FOREIGN_FIRST_STOP_RETAINED',sections=sec138,side_contacts=newown138,band_to_crown=dict(valid=cc138.isValid(),common_mm3=cc138.Volume,contact_area_mm2=cc138.Area),band_to_frame=dict(valid=cf138.isValid(),common_mm3=cf138.Volume,contact_area_mm2=cf138.Area),foreign_new_tests=0,foreign_first_HOLD_preserved=r137['first_falsifier'],foreign_received=r137['foreign_received'],foreign_total=r137['foreign_total'],remaining_foreign_keys=r137['foreign_tasks'][r137['foreign_received']:],actual_nominal_band_volume_mm3=bandphys137.Volume,expected_L_width_thickness_mm3=L137*2.5*1.2,delivered_band_shape_NOT_claimed=True,new_union_material_coverage_received=coverage137,member_extent_received=True,fullpressure_and_tail_kit_OPEN=True,operation_seconds=time.monotonic()-st138,process_cpu_seconds=time.process_time()-cp138,pid=os.getpid(),session_id=46493)
p138=OUT/'day07-W068-top-bearing-functional-sections-and-own-contacts.json';assert not p138.exists();p138.write_bytes((json.dumps(r138,indent=2)+'\n').encode());print('BODY138',newown138,'band-crown',r138['band_to_crown'],'band-frame',r138['band_to_frame'],'wall',r138['operation_seconds'],'CPU',r138['process_cpu_seconds'],flush=True);print('OWNER68_IDLE',os.getpid(),flush=True)
