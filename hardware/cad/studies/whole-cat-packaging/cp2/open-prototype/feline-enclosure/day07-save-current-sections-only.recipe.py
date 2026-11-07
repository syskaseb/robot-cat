st156=time.monotonic();cp156=time.process_time();sections156=[]
for xx in [-66.55,-40]:
 plane=Part.Face(Part.makePolygon([A.Vector(xx,-35,28),A.Vector(xx,52,28),A.Vector(xx,52,70),A.Vector(xx,-35,70),A.Vector(xx,-35,28)]))
 for n,s in [('NEW_CRADLE',union155.cut(oldroot153)),('OLD_V_ROOT',oldroot153),('FRAME_FRONT20',ctx121['Ref_Material_P0_FrameFront20_0_0']),('SIDE_LEFT22',rail154),('FULL_CASE',case148),('FIVE_TAIL_FIELD',ribbon148),('T30L_BAND',band153),('T30L_HEAD_NECK',neck153)]:
  sec=s.section(plane);sections156.append(dict(X_mm=xx,name=n,curves_yz=[[[v.y,v.z] for v in e.discretize(Deflection=.03)] for e in sec.Edges]))
r156=dict(id='day07-FPI-cradle-C0-C1-actual-received-sections',purpose='Existing saved actual operands sectioned for witness presentation only; NO pair replay/new variant/current selection',sections=sections156,operation_seconds=time.monotonic()-st156,process_cpu_seconds=time.process_time()-cp156)
p156=OUT/(r156['id']+'.json');assert not p156.exists();p156.write_bytes((json.dumps(r156,indent=2)+'\n').encode());print('BODY156_SAVED',r156['operation_seconds'],r156['process_cpu_seconds'],flush=True);print('OWNER72_IDLE',os.getpid(),flush=True)
