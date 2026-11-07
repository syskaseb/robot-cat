import time,json,hashlib
t131=time.monotonic();c131=time.process_time();assert first130['other']=='W068/single/end:0:head_budget';yy=first130['witnesses'][0][1][1]-.01;plane=Part.makePlane(100,120,A.Vector(-160,yy,0),A.Vector(0,1,0));views=[]
for name,sh in [('ASSIGNED_D_FULL39_CAPACITY',assigned130),('CURRENT_W068_FULL_HEAD_BUDGET',ctx121[first130['other']])]:
 sec=sh.section(plane);curves=[]
 for e in sec.Edges:
  vs=e.discretize(Deflection=.06)
  if len(vs)>1:curves.append([[p.x,p.z] for p in vs])
 views.append(dict(name=name,Y_mm=yy,curves_xz=curves))
r131=dict(id='day07-SOURCE-assigned-entry-W068-actual-section-read',scope='ActualsectionONLYofunchangednewfield/currentheadbudget,no dist/common/replay/newgeometryvariant',section_Y_mm=yy,sections=views,actual_received_3D_gap_mm=first130['gap_mm'],gap_witnesses=first130['witnesses'],section_not_whole_clearance_proof=True,operation_seconds=time.monotonic()-t131,process_cpu_seconds=time.process_time()-c131)
p131=OUT/'day07-SOURCE-assigned-entry-W068-actual-section-read.json';assert not p131.exists();p131.write_bytes((json.dumps(r131,indent=2)+'\n').encode());print('BODY131',yy,[len(q['curves_xz']) for q in views],'wall',r131['operation_seconds'],'CPU',r131['process_cpu_seconds'],flush=True);print('OWNER65_IDLE',os.getpid(),flush=True)
