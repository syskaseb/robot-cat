"""One static positive-side storage bay, separated functionally from moving FFC return."""
import math,json,pathlib,numpy as np
P=pathlib.Path(__file__).parent;Z=np.array([0.,0.,1.]);X=np.array([1.,0.,0.]);Y=np.array([0.,1.,0.]);R=30.
A=np.array([6.,-.66,104.1]);B=np.array([40.11,-6.804,109.77]);Cs=np.array([6.,29.34,0.]);C=np.array([-30.,60.,0.]);Qxy=np.array([40.11,-36.804,0.])
delta=C-Cs;hin=math.atan2(delta[1],delta[0]);tin=np.array([math.cos(hin),math.sin(hin),0.]);source_sweep=(hin-math.pi/2)%(2*math.pi)
d=Qxy-C;dist=np.linalg.norm(d);hout=math.atan2(d[1],d[0])+math.asin(R/dist);tout=np.array([math.cos(hout),math.sin(hout),0.]);exit_tangent=math.sqrt(dist**2-R**2)-R;coil_sweep=(hout-hin)%(2*math.pi)
H0=B[2]+60;analytic0=4*math.pi*R/2+R*source_sweep+np.linalg.norm(delta)+R*coil_sweep+exit_tangent+(H0-30-(A[2]+30))+(H0-30-(B[2]+30))+52
H=H0+(500-analytic0)/2;C[2]=Cs[2]=H;paths=[]
def rot(v,ax,a):return v*math.cos(a)+np.cross(ax,v)*math.sin(a)+ax*np.dot(ax,v)*(1-math.cos(a))
def arc(c,r,axis,a):
 for f in np.linspace(0,a,max(3,int(abs(a)*30)+1)):paths.append((c+rot(r,axis,f)).tolist())
def line(a,b):
 for f in np.linspace(0,1,max(3,int(np.linalg.norm(b-a))+1)):paths.append((a+(b-a)*f).tolist())
arc(A+30*Z,-30*Z,-Y,math.pi/2);line(np.array(paths[-1]),np.array([36.,-.66,H-30]));arc(np.array([36.,29.34,H-30]),-30*Y,-X,math.pi/2)
arc(Cs,30*X,Z,source_sweep)
Ein=C-30*np.cross(Z,tin);line(np.array(paths[-1]),Ein);arc(C,Ein-C,Z,coil_sweep)
Q=Qxy+np.array([0,0,H-30]);start=Q-30*tout+30*Z;line(np.array(paths[-1]),start);arc(Q-30*tout,30*Z,np.cross(tout,-Z),math.pi/2)
line(np.array(paths[-1]),np.array([40.11,-36.804,B[2]+30]));arc(np.array([40.11,B[1],B[2]+30]),-30*Y,X,math.pi/2)
pts=np.array(paths);out=dict(centreline=paths,source_jacket_nominal_PROJECT_OD=5.,old_occupied_PROJECT_OD=5.8,active_capacity_OD_mm=6.8,minimum_centre_R_mm=30,physical_unit_mm=500,free_analytic_mm=448,full_two_boots_once_mm=52,coil_centre=C.tolist(),coil_sweep_deg=math.degrees(coil_sweep),source_sweep_deg=math.degrees(source_sweep),source_straight_mm=H-60-A[2],return_straight_mm=H-60-B[2],sample_polyline_mm=float(np.linalg.norm(np.diff(pts,axis=0),axis=1).sum()),end_error=float(np.linalg.norm(pts[-1]-B)),status='ONE_STATIC_POSITIVE_SIDE_BAY_REMOVES_SHARED_MOVING_RETURN_CROSSING; actual occupied neighbors pending',same500_full_stock=True,physical_PASS=False)
(P/'occupied-DATA500-separated-static-bay.json').write_bytes((json.dumps(out,indent=2)+'\n').encode())
print(json.dumps({k:v for k,v in out.items() if k!='centreline'}))
