import time,json,hashlib,zipfile,os
tr112=time.monotonic();tc112=time.process_time();badname112=r111['Knee6_full_region']['first_falsifier']['other'];bad112=ctx111[badname112];common112=co;assert abs(common112.Volume-r111['Knee6_full_region']['first_falsifier']['allocated_common_mm3'])<1e-5
same112=badname112 in Current35 and bad112.isSame(Current35[badname112]);assert same112
sec112=[]
for y in [37.394595088058644,55,60]:
    plane=Part.makePlane(260,180,A.Vector(-160,y,-35),A.Vector(0,1,0))
    for n,s in [('actual_retained_P0_MountFrontL',bad112),('actual_current_U1carrier',ctx111['Underdeck:PositiveFoundation']),('allocated_Knee6_south_region',south111),('actual_BankBedguide',whole105)]:
        q=s.section(plane);curves=[]
        for e in q.Edges:
            pp=e.discretize(Deflection=.12)
            if len(pp)>1:curves.append([[v.x,v.z] for v in pp])
        sec112.append(dict(axis='Y',value_mm=y,name=n,curves_xz=curves))
ar112=OUT/'day07-SOURCE-split-portals-actual-blocker-source.breps.zip';assert not ar112.exists();ge112=[]
with zipfile.ZipFile(ar112,'w',zipfile.ZIP_DEFLATED) as z:
    for i,(n,s) in enumerate([('ACTUAL_RETAINED_P0_MountFrontL_SAME_CURRENT1292',bad112),('ALLOCATED_KNEE6_CURRENT_P0_COMMON_NOT_WIRE',common112)]):
        raw=s.exportBrepToString().encode();e=str(i)+'.brep';z.writestr(e,raw);ge112.append(dict(name=n,entry=e,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s),volume_mm3=s.Volume))
    z.writestr('manifest.json',(json.dumps(dict(geometry=ge112,scope='Alreadyreceivedvalidfirstfalsifier operand/worldexport and cachedcommon; NOTnewcollision/sourceproofreplay.'),indent=2)+'\n').encode())
r112=dict(id='day07-SOURCE-split-portals-actual-blocker-source-read',status='ACTUAL_RETAINED_P0_BODY_PORTAL_MATERIAL_IDENTIFIED_NO_NEW_VARIANT',source_actor=badname112,isSame_Current1292=same112,current_source_count=len(Current35),effective_source_count=len(effective62),actual_source_world_bounds_mm=saved_bounds(bad112),actual_source_volume_mm3=bad112.Volume,source_validity='ALREADYreceivedtrueinr111, notrerun',manufacturing_material_or_ownership_NOT_inferred_from_name=True,function='RetainedP0mount/frameactualoccupiedmaterial, no sharedmountfunctionwithSOURCEfieldproved. PreserveP0; no cutting/waiverfromname.',cached_common_mm3=common112.Volume,first_falsifier_receipt=p111.name,first_falsifier_receipt_sha256=hashlib.sha256(p111.read_bytes()).hexdigest(),sections=sec112,archive=ar112.name,archive_sha256=hashlib.sha256(ar112.read_bytes()).hexdigest(),geometry=ge112,BodyOuter_actual_world_bounds_mm=bodybounds111,operation_seconds=time.monotonic()-tr112,process_cpu_seconds=time.process_time()-tc112,new_geometry_variant=False,N01_complete=False)
p112=OUT/'day07-SOURCE-split-portals-actual-blocker-source-read.json';assert not p112.exists();p112.write_bytes((json.dumps(r112,indent=2)+'\n').encode());print('SOURCE112_SAVED',same112,r112['actual_source_world_bounds_mm'],r112['operation_seconds'],r112['process_cpu_seconds'],hashlib.sha256(p112.read_bytes()).hexdigest(),flush=True);print('OWNER57_IDLE',os.getpid(),len(Current35),len(effective62),len(restMotion),'pendingnull unsavedfalse',flush=True)
