import time,json,hashlib,math,zipfile,os
t125=time.monotonic();c125=time.process_time();case125=ctx121['Station:P_SYS:case'];assert case125.isValid() and Current35['Station:P_SYS:case'].isSame(case125)
f125=first124;assert f125['other']=='Station:P_SYS:case' and len(rows121)==8
its125=[('RECEIVED_INTERVAL_FAMILY_COVER',lookup121[f125['region']]),('ACTUAL_CURRENT_P_SYS_PURCHASED_CASE_ENVELOPE',case125)]
checks125=[]
for label,phi in [('E55_FAMILY_MIN',pl121),('E65_FAMILY_MAX',ph121)]:
 cc=P121+[4*R121*math.sin(phi),-R121];n,sh=sector121(label,cc,R121-w121,R121+w121,math.pi/2,math.pi/2+phi);gap,ww,_=sh.distToShape(case125);com=sh.common(case125);assert com.isValid()
 checks125.append(dict(name=label,phi_radians=phi,E_each_core_mm=4*R121*(phi-math.sin(phi)),gap_mm=gap,allocated_common_mm3=com.Volume,common_valid=True,full_field_valid=sh.isValid(),bounds_mm=saved_bounds(sh),status='ALLOCATED_BODY_REGION_HOLD_NOT_WIRECONTACT' if gap<1.25-1e-7 else 'LOCAL_FAMILY_ENDPOINT_SEPARATED125',witnesses=[[list(a),list(b)] for a,b in ww[:1]]));its125.extend([(label,sh),(label+'_ALLOCATED_COMMON_NOT_PHYSICAL_WIRECONTACT',com)])
co125=lookup121[f125['region']].common(case125);assert co125.isValid();its125.append(('RECEIVED_INTERVAL_COMMON_NOT_WIRECONTACT',co125))
sections125=[]
for label,phi in [('E55_FAMILY_MIN',pl121),('E65_FAMILY_MAX',ph121)]:
 source=dict(its125)[label]
 for name,sh in [(label,source),('CURRENT_P_SYS_CASE',case125)]:
  plane=Part.makePlane(350,220,A.Vector(-170,-120,44),A.Vector(0,0,1));sec=sh.section(plane);curves=[]
  for e in sec.Edges:
   ps=e.discretize(Deflection=.12)
   if len(ps)>1:curves.append([[v.x,v.y] for v in ps])
  sections125.append(dict(plane='XY',Z_mm=44,family=label,name=name,curves_xy=curves))
ar125=OUT/'day07-SOURCE-FL2-body-reserve-Psys-local-proof.breps.zip';assert not ar125.exists();geo125=[]
with zipfile.ZipFile(ar125,'w',zipfile.ZIP_DEFLATED) as zz:
 for i,(name,sh) in enumerate(its125):
  raw=sh.exportBrepToString().encode();entry=str(i)+'.brep';zz.writestr(entry,raw);geo125.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),valid=sh.isValid(),volume_mm3=sh.Volume,bounds_mm=saved_bounds(sh)))
 zz.writestr('manifest.json',(json.dumps(dict(geometry=geo125,scope='Currentcase+receivedconservativefield+exactSfamilytwoendpointlocalfields; no wire reroute/newdesignvariant'),indent=2)+'\n').encode())
r125=dict(id='day07-SOURCE-FL2-body-reserve-Psys-local-proof',status='CURRENT_BODY_S_FAMILY_ALLOCATED_SPACE_REJECTED_BY_P_SYS_CASE' if any(q['gap_mm']<1.25-1e-7 for q in checks125) else 'INTERVAL_COVER_OVERLAP_ENDPOINTS_ONLY_SEPARATE_INTERIOR_OPEN',current_actor='Station:P_SYS:case',current_actor_is_same_source1292=True,current_case_valid=True,current_case_volume_mm3=case125.Volume,current_case_bounds_mm=saved_bounds(case125),function='SelectedretainedWAGO-P_SYSboughtcaseplanningbody, notflexwire/notprojectguide/ownmount. Nominalcaseenvelope is not manufacturer-deliveredexactsurfaceguarantee.',named_hazard='ReceivedadaptiveintervalfieldoverlapwithP_SYS may be conservativephi-coverpadding. OnlyexacttwoREQUIREDfamilyendlocalregions aretested toseparatecoverartefactfromactualproposedcapacityallocationfailure; no individual freewire/globalwiretest/newpose/offset.',received_interval_allocated_common_mm3=co125.Volume,received_interval_common_valid=True,local_family_endpoint_rows=checks125,sections=sections125,archive=ar125.name,archive_sha256=hashlib.sha256(ar125.read_bytes()).hexdigest(),geometry=geo125,source_constraints='full9.4x3.9/D-G3.1,V2/.2gaps/.4margin unchanged; groupR37.85/coreR35.1;E55..65eachcore; no waiver/reduction/physicalcontactclaim',counter=dict(cursor=8,total=127,unreceived=119,first_falsifier_stop=True),new_material=False,new_leg_geometry=False,actual_A_U_minfit_slack=None,selected=False,N01_complete=False,operation_seconds=time.monotonic()-t125,process_cpu_seconds=time.process_time()-c125,pid=os.getpid(),session_id=46493)
p125=OUT/'day07-SOURCE-FL2-body-reserve-Psys-local-proof.json';assert not p125.exists();p125.write_bytes((json.dumps(r125,indent=2)+'\n').encode());print('BODY125',r125['status'],checks125,'intervalcommon',co125.Volume,'wall',r125['operation_seconds'],'CPU',r125['process_cpu_seconds'],flush=True);print('OWNER62_IDLE',os.getpid(),flush=True)
