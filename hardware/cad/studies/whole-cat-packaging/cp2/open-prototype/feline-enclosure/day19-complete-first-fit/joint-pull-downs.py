from common import *
from scipy.integrate import cumulative_trapezoid
s=(F/'service-lay.py').read_text();exec(s[:s.index('for deg in [-20')])
for deg in [-20,-10,0,10,20]:
 a=math.radians(deg);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
 start=(s-yc)@R.T+yc;t=R@X;r=24.2
 lead=line(start,start+4*t);b=arc(lead[-1],t,Z,r,math.pi/2);h=K[2]-2*r-start[2];c=line(b[-1],b[-1]+h*Z)
 static=4+r*math.pi/2+h;theta0=(50-static)/r
 th=np.r_[np.linspace(0,theta0,30)[:-1],np.linspace(theta0,math.pi/2,181)]
 width=.42;w=np.clip((th-theta0)/width,0,1);phi=a*(1-(3*w*w-2*w**3));dphi=-a*(6*w-6*w*w)/width
 # Return to the original upper lane with zero net lateral displacement.
 # The unrestrained section can change its clock after the last insulated grip.
 from scipy.optimize import brentq
 v=np.clip((th-theta0-width)/(math.pi/2-theta0-width),0,1);bump=np.sin(math.pi*v)**2
 deriv=math.pi*np.sin(2*math.pi*v)/(math.pi/2-theta0-width)
 def steer(k):
    az=phi-k*bump;da=dphi-k*deriv;ds=r*np.sqrt(1+(np.sin(th)*da)**2)
    return np.c_[np.sin(th)*np.cos(az),np.sin(th)*np.sin(az),np.cos(th)],ds
 def residual(k):
    t0,ds=steer(k);return np.trapezoid(t0[:,1]*ds,th)
 tangent,ds=steer(brentq(residual,-1.,1.));d=c[-1]+cumulative_trapezoid(tangent*ds[:,None],x=th,axis=0,initial=0)
 run=float(np.trapezoid(ds,th));offset=K-d[-1];axial=offset@X;cross=offset-axial*X;side=unit(cross);span=np.linalg.norm(cross)
 ru=min(span/2,(246-static-run-span-abs(axial)-4)/(math.pi-2));middle=max(0,span-2*ru);first=(246-static-run-math.pi*ru-middle+axial)/2;back=first-axial
 assert min(first,back)>=0,(deg,first,back)
 aa=line(d[-1],d[-1]+first*X);bb=arc(aa[-1],X,side,ru,math.pi/2);cc=line(bb[-1],bb[-1]+middle*side);ee=arc(cc[-1],side,-X,ru,math.pi/2)
 p=chain([aa,bb,cc,ee,line(ee[-1],K)]);dd=[first,math.pi*ru,middle,back]
 record('JR_pitch',[lead,b,c,d,p],[4,r*math.pi/2,h,run]+dd,min(r,ru),'first 50 on yaw, remaining 196 flexible to the fixed body fan',yaw=deg,fan=out(K),fan_axis=out(-X),inner_R=min(r,ru)-1.75)
 assert min(r,ru)-1.75>=22.25
def station(q):
 p=np.asarray(q['points']);d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
 return {str(k):[float(np.interp(k,d,col)) for col in p.T] for k in [0,5,15,25,35,45,50]}
wr('remote-pulldown-lay.json',dict(fixed={n:station(fixed['JR_'+n]) for n in ['yaw','tail']},pitch=moving,stations={str(q['yaw']):station(q) for q in moving},budgets=[12,50,196,25,9,8],static_housing_mm=50,window_centres=[15,35],grips=[5,45],actual_cut_fit_slack=None))
print([(q['yaw'],round(q['inner_R'],3),q['free']) for q in moving])
