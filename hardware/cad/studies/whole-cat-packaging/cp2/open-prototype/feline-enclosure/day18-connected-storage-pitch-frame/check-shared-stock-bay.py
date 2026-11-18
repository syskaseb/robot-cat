import json,numpy as np,pathlib
P=pathlib.Path(__file__).parent
f=json.loads((P/'occupied-FFC200-family.json').read_text());d=json.loads((P/'occupied-DATA500-transport.json').read_text());pts=np.array(d['centreline'])
def point_tri(p,a,b,c):
 ab=b-a;ac=c-a;ap=p-a
 n=np.cross(ab,ac);nn=np.einsum('ij,ij->i',n,n);proj=ap-n*np.divide(np.einsum('ij,ij->i',ap,n),nn,out=np.zeros_like(nn),where=nn>1e-16)[:,None]
 v0=ab;v1=ac;v2=proj
 aa=np.einsum('ij,ij->i',v0,v0);bb=np.einsum('ij,ij->i',v0,v1);cc=np.einsum('ij,ij->i',v1,v1);dd=np.einsum('ij,ij->i',v2,v0);ee=np.einsum('ij,ij->i',v2,v1);den=aa*cc-bb*bb
 u=np.divide(cc*dd-bb*ee,den,out=np.zeros_like(den),where=abs(den)>1e-16);v=np.divide(aa*ee-bb*dd,den,out=np.zeros_like(den),where=abs(den)>1e-16)
 face=np.divide(np.einsum('ij,ij->i',ap,n)**2,nn,out=np.full_like(nn,np.inf),where=nn>1e-16);face[(u<0)|(v<0)|(u+v>1)]=np.inf
 ds=[face]
 for x,y in [(a,b),(b,c),(c,a)]:
  q=y-x;vv=np.einsum('ij,ij->i',q,q);t=np.divide(np.einsum('ij,ij->i',p-x,q),vv,out=np.zeros_like(vv),where=vv>1e-16);cl=x+np.clip(t,0,1)[:,None]*q;ds.append(np.einsum('ij,ij->i',p-cl,p-cl))
 return np.min(np.vstack(ds),axis=0)
results=[]
for s in f:
 c=np.array(s['corners']);tri=[]
 for i in range(len(c)-1):
  for j in range(4):
   k=(j+1)%4;tri.extend([[c[i,j],c[i+1,j],c[i,k]],[c[i,k],c[i+1,j],c[i+1,k]]])
 tr=np.array(tri);best=(float('inf'),None)
 for p in pts:
  m=float(point_tri(p,tr[:,0],tr[:,1],tr[:,2]).min())
  if m<best[0]:best=(m,p.tolist())
 # Half maximum DATA sample spacing plus conservative sampled ribbon arc/roll enclosure allowance.
 error=float(np.linalg.norm(np.diff(pts,axis=0),axis=1).max()/2)+.10
 lower=best[0]**.5-3.4-error
 results.append(dict(yaw=s['yaw'],pitch=s['pitch'],sampled_surface_to_DATA_axis=best[0]**.5,DATA_capacity_radius=3.4,discretization_bound=error,conservative_gap_lower=lower,DATA_witness=best[1],scope='correlated nine pose shared-bay screen; not continuous-motion certificate'))
(P/'shared-DATA-FFC-stock-bay-result.json').write_bytes((json.dumps(results,indent=2)+'\n').encode())
print(json.dumps(results))
