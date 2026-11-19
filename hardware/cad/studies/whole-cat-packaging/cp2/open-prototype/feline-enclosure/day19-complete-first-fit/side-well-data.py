from common import *
d=rd(P/'side-bay-envelope.json');x=np.array(d['x']);y=np.array(d['y']);z=np.array(d['upper_z'])
xx=[-111.95,-100,-84,-68,-52,-36,-20,-4,8,13];yy=[-103.1,-100,-96,-92,-88,-84,-80,-76,-72,-68,-65.]
rows=[]
for i,v in enumerate(xx):
 sel=(x[:-1]<xx[min(i+1,len(xx)-1)]+.001)&(x[1:]>xx[max(0,i-1)]-.001)
 line=[]
 for k,t in enumerate(yy):
    use=(y[:-1]<yy[min(k+1,len(yy)-1)]+.001)&(y[1:]>yy[max(0,k-1)]-.001)
    line.append(round(max(40.45,float(z[np.ix_(sel,use)].max())+1.25),3))
 rows.append(line)
wr('well-sections.json',dict(x=xx,y=yy,underside=rows,vertical_thickness=2.4,sampled_allowance=1.25))
