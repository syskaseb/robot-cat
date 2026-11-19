"""Design the yaw shroud inside surface and stationary chin roof from the final moving members."""
from pathlib import Path
import runpy,json,math,numpy as np
P=Path(__file__).parent
s=(P/"diaphragm-profiles.py").read_text();exec(s[:s.index("lay=json.loads")])
lay=json.loads((P/"whole-lay.json").read_bytes())
theta=np.linspace(0,2*math.pi,48,endpoint=False);uv=np.column_stack([np.cos(theta),np.sin(theta)]);centre=np.array([0.,151.])
xs=[-139.6,-136,-132,-128,-123,-118,-111,-104,-97]
source=D.shape("D19D_PitchBack");es={n:edges(n) for n in ["D19D_PitchBack","D19D_Face","D19D_YawHood"]}
sections=[]
for x in xs:
    pts=[];base=[]
    for n in ["D19D_PitchBack","D19D_Face"]:
        for p in range(-10,11,2):
            R,T=transforms(0,p)["pitch"];crossing(es[n],R,T,x,pts)
    # Maintain the original aft guide envelope as it enters the fixed shoulder.
    crossing(es["D19D_YawHood"],np.eye(3),np.zeros(3),max(x,-137),base)
    if not base:crossing(es["D19D_YawHood"],np.eye(3),np.zeros(3),-98,base)
    bh=(np.concatenate(base)-centre)@uv.T;h=np.max(bh,axis=0)-1.45
    if pts:
        ph=(np.concatenate(pts)-centre)@uv.T;h=np.maximum(h,np.max(ph,axis=0)+3.4)
    def rays(support):
        den=uv@uv.T;dist=np.min(np.where(den>1e-7,support[None,:]/np.maximum(den,1e-9),1e6),axis=1)
        return (centre+dist[:,None]*uv).round(3).tolist()
    sections.append(dict(x=x,outer=rays(h+1.45),inner=rays(h)))
# Roof over the fixed forward nose stays under the moving pitch back and mask.
# Z is invariant under yaw; the use of whole triangle edges and an angular
# padding of 3.5 mm conservatively covers the intervening pose and mesh chord.
probes=[-166.8,-155,-145,-135,-123,-113,-101]
lows=np.ones(len(probes))*1e6
for n in ["D19D_PitchBack","D19D_Face"]:
    ee=es[n];# convex cover of the lower half, restricted to each longitudinal interval
    pts=np.unique(ee.reshape(-1,3).round(5),axis=0);pts=pts[pts[:,2]<117]
    for y in range(-20,21,2):
        for p in range(-10,11,2):
            R,T=transforms(y,p)["pitch"];q=pts@R.T+T
            for i,x in enumerate(probes):
                k=abs(q[:,0]-x)<15
                if k.any():lows[i]=min(lows[i],q[k,2].min()-3.5)
roof=np.round(np.minimum(lows,94),2).tolist()
(P/"articulated-sections.json").write_bytes((json.dumps(dict(yaw=sections,chin_x=probes,chin_roof=roof),separators=(",",":"))+"\n").encode())
print(roof)

