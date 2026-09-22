"""Numerical IK for measured, non-ideal CAD axes. No ROS or CAD dependency."""
import numpy as np


def rotation(axis,angle):
    a=np.asarray(axis,dtype=float);a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+np.sin(angle)*K+(1-np.cos(angle))*(K@K)


def forward(joints,foot,q):
    R=np.eye(3);t=np.zeros(3);axes=[];pivots=[]
    for j,angle in zip(joints,q):
        p=np.asarray(j['origin_m']);a=np.asarray(j['axis'])
        pivots.append(R@p+t);axes.append(R@a)
        Q=rotation(a,angle)
        t+=R@(p-Q@p);R=R@Q
    end=R@np.asarray(foot)+t
    jacobian=np.column_stack([np.cross(a,end-p) for a,p in zip(axes,pivots)])
    return end,jacobian


def stage_transforms(joints,q):
    """Global displacement transform of each moving CAD stage."""
    R=np.eye(3);t=np.zeros(3);result=[]
    for j,angle in zip(joints,q):
        p=np.asarray(j['origin_m']);a=np.asarray(j['axis'])
        pivot=R@p+t;axis=R@a;Q=rotation(a,angle)
        t=t+R@(p-Q@p);R=R@Q
        result.append((R.copy(),t.copy(),pivot,axis))
    return result


def inverse(joints,foot,target,initial=None,limit=.48):
    q=np.zeros(3) if initial is None else np.array(initial,dtype=float)
    for _ in range(80):
        end,J=forward(joints,foot,q);error=np.asarray(target)-end
        if np.linalg.norm(error)<1e-7:return q
        step=J.T@np.linalg.solve(J@J.T+np.eye(3)*1e-8,error)
        q=np.clip(q+np.clip(step,-.12,.12),-limit,limit)
    raise ValueError(f'Unreachable CAD target: residual {np.linalg.norm(error):.6f} m')


def smooth(t):
    t=np.clip(t,0,1)
    return t*t*t*(10+t*(-15+6*t))


def support_shift(feet,code,com,margin=.15):
    """Move COM into triangle by mixing nearest feasible point with centroid.

    Input/return expressed in base XY. This is a planned body displacement,
    not an external force stabilising the simulation.
    """
    points=np.array([p[:2] for c,p in feet.items() if c!=code])
    A=np.vstack([points.T,np.ones(3)]);b=np.r_[com[:2],1.]
    weights=np.linalg.solve(A,b)
    weights=np.maximum(weights,0);weights/=weights.sum()
    weights=(1-margin)*weights+margin/3
    return np.r_[weights@points-np.asarray(com[:2]),0]


def stepping_targets(model,feet,time,step_seconds=3.,lift=.006,offset=(0,0,0),support_com=None):
    """One foot at a time, body shift then lift. NO forward travel claim.

    Starts/ends neutral. Deliberately distinct from the legacy trot until
    contact and actuator limits have been checked in the CAD model.
    """
    codes=['FR','RL','FL','RR']
    code=codes[int(time//step_seconds)%4];u=(time%step_seconds)/step_seconds
    neutral={c:(np.array(p)+offset).tolist() for c,p in feet.items()}
    shift=support_shift(neutral,code,model['total']['com_m'] if support_com is None else support_com)
    weight=smooth(u/.25) if u<.25 else (smooth((1-u)/.25) if u>.75 else 1.)
    height=lift*np.sin(np.pi*np.clip((u-.25)/.5,0,1))**2
    result={}
    for c,p in feet.items():
        target=np.array(p)+offset-shift*weight
        if c==code:target[2]+=height
        chain=[j for j in model['joints'] if j['cad_code']==c]
        result.update({j['name']:float(q) for j,q in zip(chain,inverse(chain,p,target))})
    return result


def crawl_targets(model,feet,time,step_seconds=3.,lift=.006,stride=.024,
                  offset=(0,0,0),support_com=None):
    """Slow 87.5% duty crawl; stance feet track backwards at constant speed.

    This is an experimental trajectory, not hardware control. One full
    cycle takes 4*step_seconds. Nominal speed=stride/(3.5*step_seconds).
    """
    codes=['FR','RL','FL','RR'];targets={};speed=stride/(3.5*step_seconds)
    current=codes[int(time//step_seconds)%4];u=(time%step_seconds)/step_seconds
    for i,c in enumerate(codes):
        phase=(time/step_seconds-i)%4
        height=0.
        if .25<=phase<=.75:
            s=(phase-.25)/.5;v=-speed*.5*step_seconds
            x=-stride/2+v*s+(10*stride-10*v)*s**3+(-15*stride+15*v)*s**4+(6*stride-6*v)*s**5
            height=lift*np.sin(np.pi*s)**2
        elif phase<.25:x=-stride/2+speed*(.25-phase)*step_seconds
        else:x=stride/2-speed*(phase-.75)*step_seconds
        targets[c]=np.asarray(feet[c])+offset+[x,0,height]
    shift=support_shift(targets,current,model['total']['com_m'] if support_com is None else support_com)
    weight=smooth(u/.25) if u<.25 else (smooth((1-u)/.25) if u>.75 else 1.)
    result={}
    for c,p in targets.items():
        chain=[j for j in model['joints'] if j['cad_code']==c]
        result.update({j['name']:float(q) for j,q in zip(chain,inverse(chain,feet[c],p-shift*weight))})
    return result
