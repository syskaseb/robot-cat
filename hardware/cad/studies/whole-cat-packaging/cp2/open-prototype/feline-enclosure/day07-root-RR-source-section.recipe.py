import time,json
t134=time.monotonic();c134=time.process_time();yy134=first133['witnesses'][0][0][1];plane134=Part.makePlane(100,100,A.Vector(-140,yy134,0),A.Vector(0,1,0));sections134=[]
for name,sh in [('ROOT_BACKPAD_FUNCTIONAL_ENVELOPE',back132),('ACTUAL_RR_STAGE0_RETAINED_PART',ctx121[first133['other']]),('ACTUAL_NEW_COMMON',co133)]:
 sec=sh.section(plane134);curves=[]
 for e in sec.Edges:
  ps=e.discretize(Deflection=.08)
  if len(ps)>1:curves.append([[v.x,v.z] for v in ps])
 sections134.append(dict(name=name,Y_mm=yy134,curves_xz=curves))
r134=dict(id='day07-W068-root-RR-source-section',source_neighbor=first133['other'],current_motion_owner=list(owners106[first133['other']]),no_motion_tests_performed=True,actual_section_Y_mm=yy134,sections=sections134,operation_seconds=time.monotonic()-t134,process_cpu_seconds=time.process_time()-c134)
p134=OUT/'day07-W068-root-RR-source-section.json';assert not p134.exists();p134.write_bytes((json.dumps(r134,indent=2)+'\n').encode());print('BODY134',r134['current_motion_owner'],[len(q['curves_xz']) for q in sections134],'wall',r134['operation_seconds'],'CPU',r134['process_cpu_seconds'],flush=True);print('OWNER66_IDLE',os.getpid(),flush=True)
