# Resolve zero-area solid/solid common at coincident nominal bearing with actual face/face contact, not new material or a variant.
st139=time.monotonic();cp139=time.process_time();bc139=[];hc139=[]
for i,f in enumerate(bandphys137.Faces):
 if type(f.Surface).__name__=='Plane' and abs(f.normalAt(0,0).z)>.99:
  if abs(f.CenterOfMass.z-31.91)<1e-6:
   c=f.common(ff137.Faces[96]);bc139.append(dict(band_face=i,frame_face=96,valid=c.isValid(),area_mm2=c.Area))
  if abs(f.CenterOfMass.z-39.51)<1e-6:
   for j,v in enumerate(cap137.Faces):
    if abs(v.CenterOfMass.z-39.51)<1e-6:
     c=f.common(v);hc139.append(dict(band_face=i,crown_face=j,valid=c.isValid(),area_mm2=c.Area))
r139=dict(id='day07-W068-top-bearing-new-closed-band-bearing-face-contact',status='ACTUAL_NEW_NOMINAL_OWN_BEARING_CONTACT_SOURCE_FACES',band_to_frame=bc139,band_to_crown=hc139,solid_solid_zero_area_is_not_face_contact_proof=True,solid_solid_zero_volume_already_received=True,source_frame_unchanged=True,foreign_tests=0,stock_foreign_FPI_HOLD_preserved=True,delivered_fit_strength_not_claimed=True,operation_seconds=time.monotonic()-st139,process_cpu_seconds=time.process_time()-cp139,pid=os.getpid(),session_id=46493)
p139=OUT/'day07-W068-top-bearing-new-closed-band-bearing-face-contact.json';assert not p139.exists();p139.write_bytes((json.dumps(r139,indent=2)+'\n').encode());print('BODY139',bc139,hc139,'wall',r139['operation_seconds'],'CPU',r139['process_cpu_seconds'],flush=True);print('OWNER68_IDLE',os.getpid(),flush=True)
