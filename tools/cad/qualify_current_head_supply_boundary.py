"""Six current source-feed boundaries, no duplicate spatial qualification."""
import time
from pathlib import Path
import plan_current_head_supply_coupled as C

def run():
 tick=time.monotonic();p=C.build();rows=[];local=C.H.local(0)
 for name in ('XB12','XB13','XS13'):
  wire=C.S.Q.makewire(p['routes'][name]['parts']);edge=wire.Edges[-1];end=edge.valueAt(edge.LastParameter);candidates=[]
  for label,(other,rr,path) in local.items():
   if '/'+name+'/' not in label:continue
   for e in other.Edges:
    for u in (e.FirstParameter,e.LastParameter):
     gap=(end-e.valueAt(u)).Length;dot=abs(edge.tangentAt(edge.LastParameter).dot(e.tangentAt(u)))
     candidates.append((gap,label,dot,path))
  gap,label,dot,path=min(candidates);assert gap<1e-5 and dot>1-1e-5,(name,gap,dot)
  rows.append(dict(wire=name,receiving=label,gap_mm=gap,absolute_tangent_dot=dot,end_mm=list(end),source_path=path.relative_to(C.ROOT).as_posix(),source_sha256=C.P.sha(path),continuous=True))
 for yaw in (-15,0,15):
  for name in ('XB22','XB23','XS23'):
   wire=C.S.Q.makewire(p['routes'][name]['parts']);edge=wire.Edges[-1];end=edge.valueAt(edge.LastParameter)
   path=C.S.C.OUT/f'{name}_yaw{yaw:+}_Loop.brep';loop=C.Part.read(str(path));last=loop.Edges[-1]
   fixed=last.valueAt(last.LastParameter)-C.A.Vector(0,9,0);gap=(fixed-end).Length
   dot=edge.tangentAt(edge.LastParameter).dot(C.A.Vector(0,1,0))
   reverse_loop=-last.tangentAt(last.LastParameter).dot(C.A.Vector(0,1,0))
   assert gap<1e-5 and min(dot,reverse_loop)>1-1e-5,(name,yaw,gap,dot,reverse_loop)
   rows.append(dict(wire=name,yaw=yaw,receiving='CURRENT_W2_Y85_FIXED_TAIL',gap_mm=gap,tangent_dot=dot,reverse_loop_tangent_dot=reverse_loop,end_mm=list(end),source_path=path.relative_to(C.ROOT).as_posix(),source_sha256=C.P.sha(path),continuous=True))
 C.S.save('boundary-checks.json',dict(status='CURRENT_W3_BOUNDARIES_CLEAR',boundaries=rows,physical_pass=False,worker_seconds=time.monotonic()-tick,
  source_sha256={**{v['source_path']:v['source_sha256'] for v in rows},Path(__file__).relative_to(C.ROOT).as_posix():C.P.sha(Path(__file__)),(C.OUT/'coupled-plan.json').relative_to(C.ROOT).as_posix():C.P.sha(C.OUT/'coupled-plan.json')}))
 print('Current six-feed boundaries',len(rows),flush=True)
if __name__=='__main__':run()
