import json,time,hashlib,zipfile,os
t174=time.monotonic();c174=time.process_time()
assert first173 and len(rows173)==1
ge174=[];ar174=OUT/'day07-SOURCE-G4-C1-shared-leading-witness.breps.zip';assert not ar174.exists()
with zipfile.ZipFile(ar174,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate([('FROZEN_W005_FULL_ALLOCATED_PORTAL',portal173),('ONLY_NEW_PRIMARY_POSITIVE_MATERIAL_DELTA',delta170),('NEW_UPPER_CONTEXT',up170),('RETAINED_BOUGHT_G4_CASE_CONTEXT',case170)]):
        p=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat78-witness-'+str(i)+'.brep');s.exportBrep(str(p));b=p.read_bytes();entry=str(i)+'.brep';z.writestr(entry,b)
        ge174.append(dict(name=n,entry=entry,sha256=hashlib.sha256(b).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume,bounds_mm=saved_bounds(s),role='allocated_flexible_capacity_not_delivered_wire' if i==0 else ('new_actual_print_material' if i<3 else 'unchanged_bought_context_only')))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge174,selected=False,no_new_geometry_built=True),indent=2)+'\n').encode())
plane174=Part.makePlane(100,100,A.Vector(-15,0,45.52),A.Vector(0,0,1));sec174=[]
for n,s in [('allocated_D_portal',portal173),('new_primary_delta',delta170),('new_upper',up170),('bought_G4case',case170)]:
    cut=s.section(plane174);lines=[]
    for e in cut.Edges:
        lines.append([[v.x,v.y] for v in e.discretize(Deflection=.08)])
    sec174.append(dict(name=n,curves_xy=lines))
q174=OUT/'day07-SOURCE-G4-C1-shared-leading-actual-section.json';assert not q174.exists()
rr174=dict(id=q174.stem,Z_mm=45.52,sections=sec174,closest_valid_pair=first173,archive=ar174.name,archive_sha256=hashlib.sha256(ar174.read_bytes()).hexdigest(),geometry=ge174,no_contact_inference_from_section=True,operation_seconds=time.monotonic()-t174,process_cpu_seconds=time.process_time()-c174)
q174.write_bytes((json.dumps(rr174,indent=2)+'\n').encode())
print('G4_SHARED_WITNESS_SAVED',ar174.name,hashlib.sha256(ar174.read_bytes()).hexdigest(),len(ge174),rr174['operation_seconds'],rr174['process_cpu_seconds'],'NO_NEW_DESIGN_NATIVE_IDLE',os.getpid(),flush=True)
