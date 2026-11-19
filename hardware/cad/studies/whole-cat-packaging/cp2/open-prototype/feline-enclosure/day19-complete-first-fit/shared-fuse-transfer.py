from common import *
s=(P/'fuse-lead-layout.py').read_text();exec(s[:s.index('proposals=')])
# Across the open lower slot first, turn in plan between the cradles, THEN rise.
# Changing clock only at the vertical return left the long straight against the AUX clip.
n=np.array([0,1.,0]);a=math.radians(40);rr=18
def arc(p,u,n,a,r):return p+r*(np.sin(np.linspace(0,a,60))[:,None]*u+(1-np.cos(np.linspace(0,a,60)))[:,None]*n)
routes=[]
for L in [84.5,89.5,94.5]:
 first=33.;p=origin+first*u;b=arc(p,u,n,a,rr);v=math.cos(a)*u+math.sin(a)*n
 # Keep the lower handoff in its own bay; the supplied length variation uncurls
 # above the terminal row underneath the Pi, before fitting the Pi assembly.
 extra=0;k=b[-1];up=np.array([math.sin(a)*.65,math.cos(a)*.65,math.sqrt(1-.65**2)])
 h=arc(k,v,up,math.pi/2,rr)
 rem=L-first-rr*a-rr*math.pi/2;t=np.linspace(h[-1],h[-1]+rem*up,42)
 end=t[-1];pts=np.vstack([np.linspace(origin,p,35)[:-1],b[:-1],h[:-1],t])
 pts=pts[np.r_[True,np.linalg.norm(np.diff(pts,axis=0),axis=1)>.00001]]
 dist=np.linalg.norm(pts-end,axis=1);screen('HP prefuse '+str(L),0,0,circle(pts[dist>=4.35][1:],2.1));screen('exposed factory land '+str(L),0,0,circle(pts[dist<4.35],.75))
 routes.append(dict(stock=L,points=pts.round(4).tolist(),end_or_overlap=end.tolist(),bare_tip_included=True,free_segments=[first,rr*a,extra,rr*math.pi/2,rem]))
wr('shared-fuse-transfer.json',dict(routes=routes,results=rows,clock='two consecutive orthogonal bends on opposite sides of the upper cradle; open top during lay',centre_R=rr,physical=None))
print([(r['field'],r['hits']) for r in rows if r['hits']])
