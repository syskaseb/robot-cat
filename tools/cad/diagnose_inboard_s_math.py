"""Bounded math witness: distinguish infeasible runs from self crossing."""
import json,math
from plan_current_moving_looms import sub,dot
from plan_inboard_s_hip_sources import OUT,DOWN,add,mul,exact_turn_to,line,build,endpoints,self_screen

if __name__=='__main__':
    rows=json.loads((OUT/'body-inboard-s-hip-plan.json').read_text())['hips']
    for row in rows:
        if row['physical_leg'].startswith('Front'):continue
        a=add(row['fixed_anchor_world_mm'],mul(DOWN,9));side=1 if a[1]>0 else -1;u=[0,-side,0]
        for span in (72,90):
            first=exact_turn_to(a,DOWN,u,31.5);p=add(first['end'],mul(u,span-63));last=exact_turn_to(p,u,DOWN,31.5)
            prefix=[first,line(first['end'],p),last]
            for h in (-15,0,15):
                _,b,v,m=endpoints(row,h);parts=build(last['end'],b,v,190)
                print(json.dumps(dict(loom=row['loom'],span=span,h=h,built=parts is not None,
                    witness=self_screen([line(row['fixed_anchor_world_mm'],a),*prefix,*parts,line(b,m)]) if parts else None)),flush=True)
                if row['loom']=='RL1' and span==90 and h==-15:
                    dx,dy,dz=sub(b,last['end']);print('actual ends',last['end'],b,'exit',v,flush=True)
                    for phi in (70,75,80,85):
                        u=[math.cos(math.radians(phi)),math.sin(math.radians(phi)),0]
                        angle=math.acos(dot(u,v));k=31.5*math.tan(angle/2)
                        shift=add(mul(add(DOWN,u),31.5),mul(add(u,v),k))
                        bb=(dx-shift[0])/u[0];cc=(dy-shift[1]-bb*u[1])/v[1];aa=shift[2]+cc*v[2]-dz
                        print(phi,'runs',aa,bb,cc,'length',aa+bb+cc+31.5*(math.pi/2+angle),flush=True)
