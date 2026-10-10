"""Only current interface C1 qualification; no repeated spatial work."""
import plan_current_head_access as C
def run():
 rows=[]
 for yaw in (-15,0,15):
  for name in C.K.PACK:
   w=C.Part.read(str(C.OUT/f'{name}_yaw{yaw:+}_Loop.brep'))
   approach=C.Part.read(str(C.OUT/(name+'_ReceivingApproach.brep')))
   e=w.Edges[-1];end=e.valueAt(e.LastParameter);fixed=end-C.A.Vector(0,9,0)
   a=approach.Edges[-1];gap=(a.valueAt(a.LastParameter)-fixed).Length
   dot=-e.tangentAt(e.LastParameter).dot(C.A.Vector(0,1,0))
   approach_dot=a.tangentAt(a.LastParameter).dot(C.A.Vector(0,1,0))
   assert gap<1e-5 and dot>1-1e-6 and approach_dot>1-1e-6,(yaw,name,gap,dot,approach_dot)
   rows.append(dict(yaw=yaw,wire=name,gap_mm=gap,tangent_dot=dot,fixed_tail_end_mm=list(fixed),approach_tangent_dot=approach_dot))
 C.save('boundary-checks.json',dict(status='CURRENT_ACCESS_BOUNDARIES_CLEAR',boundaries=rows,physical_pass=False))
 print('Current access boundaries:',len(rows))
if __name__=='__main__':run()
