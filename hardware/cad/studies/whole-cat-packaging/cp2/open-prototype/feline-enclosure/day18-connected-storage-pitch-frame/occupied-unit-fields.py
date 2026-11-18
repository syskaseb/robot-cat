"""Chosen analytic construction only; no optimization, solver or free-span solid loft."""
import json,math,pathlib,numpy as np
P=pathlib.Path(__file__).parent
def unit(v):return v/np.linalg.norm(v)
def rot(v,ax,a):return v*math.cos(a)+np.cross(ax,v)*math.sin(a)+ax*np.dot(ax,v)*(1-math.cos(a))
def arc(c,r,t,w,axis,angle,steps):
 return [(c+rot(r,axis,a),rot(t,axis,a),rot(w,axis,a)) for a in np.linspace(0,angle,steps+1)]
ffc=[];Z=np.array([0.,0.,1.]);Pe=np.array([-62.5,-16.5,105.1]);R=22.
for row in json.loads((P/'separate-FFC200-storage-plan.json').read_text())['rows']:
 c=np.array(row['C0']);v=np.array(row['source_tangent']);yaw=math.radians(row['yaw']);w=np.array([math.sin(yaw),-math.cos(yaw),0.]);points=[]
 def add(p,t,ww):points.append((p.copy(),unit(t),unit(ww)))
 add(c,v,w)
 theta=math.acos(np.clip(v@Z,-1,1))
 if theta>1e-8:
  ax=unit(np.cross(v,Z));e=unit(Z-v*math.cos(theta));centre=c+R*e
  for p,t,ww in arc(centre,c-centre,v,w,ax,theta,4)[1:]:add(p,t,ww)
 c=np.array(row['after_connector_approach']);w=points[-1][2];H=np.array(row['H']);N=unit(np.cross(Z,H))
 # Variable straight source leg, then the first exact quarter.
 a=c+Z*row['variable_source_leg'];add(a,Z,w)
 centre=a+R*H
 for p,t,ww in arc(centre,a-centre,Z,w,N,math.pi/2,24)[1:]:add(p,t,ww)
 # Roll occurs in the long horizontal transport, not inside a radius-critical compound bridge.
 b=points[-1][0];w0=points[-1][2];target=N if w0@N>=0 else -N
 roll=math.atan2(np.cross(w0,target)@H,w0@target)
 for f in np.linspace(0,1,25)[1:]:add(b+H*row['straight_between_quarters']*f,H,rot(w0,H,roll*f))
 a=points[-1][0];w=points[-1][2];centre=a-Z*R
 for p,t,ww in arc(centre,a-centre,H,w,N,math.pi/2,24)[1:]:add(p,t,ww)
 a=points[-1][0];w0=points[-1][2];target=np.array([0.,-1.,0.]);ax=-Z
 roll=math.atan2(np.cross(w0,target)@ax,w0@target)
 for f in np.linspace(0,1,25)[1:]:add(a-Z*row['return_leg']*f,-Z,rot(w0,ax,roll*f))
 corners=[]
 for p,t,ww in points:
  n=unit(np.cross(t,ww));corners.append([(p+sy*8.4*ww+sz*.9*n).tolist() for sy,sz in [(-1,-1),(1,-1),(1,1),(-1,1)]])
 ffc.append(dict(yaw=row['yaw'],pitch=row['pitch'],centreline=[p.tolist() for p,t,w in points],widths=[w.tolist() for p,t,w in points],corners=corners,source_approach_profiles=corners[:5] if theta>1e-8 else corners[:2],roll_horizontal_deg=math.degrees(math.atan2(np.cross(w0,target)@ax,w0@target)),analytic_total_mm=row['total'],analytic_inner_lower_mm=row['profile_inner_lower'],sample_only=True))
data=json.loads((P/'connected-DATA500-plan.json').read_text())
# The previously calculated tangent angles and vertical-leg take-up are retained exactly.
H=178.004547905688;A=np.array([6.,-.66,104.1]);B=np.array([40.11,-6.804,109.77]);C=np.array([-62.5,-16.5,H]);R=30.;paths=[]
def ln(a,b):
 for f in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/1)+1)):paths.append((a+(b-a)*f).tolist())
def ar(c,rad,axis,ang):
 for a in np.linspace(0,ang,max(2,int(abs(ang)*30)+1)):paths.append((c+rot(rad,axis,a)).tolist())
Y=np.array([0.,1.,0.]);X=np.array([1.,0.,0.]);
ar(A+30*Z,-30*Z,-Y,math.pi/2);ln(np.array(paths[-1]),np.array([36.,-.66,H-30]));ar(np.array([6.,-.66,H-30]),30*X,-Y,math.pi/2)
hin=-3.3671702756284;hout=.0955414339;Cs=np.array([6.,29.34,H]);ar(Cs,np.array([0.,-30.,0.]),-Z,math.pi-((hin+2*math.pi)%(2*math.pi)))
# At heading hin the right-side source circle and left-side coil meet through the saved common tangent.
tin=np.array([math.cos(hin),math.sin(hin),0.]);leftin=np.cross(Z,tin);Ein=C-30*leftin
ln(np.array(paths[-1]),Ein)
tout=np.array([math.cos(hout),math.sin(hout),0.]);Eout=C-30*np.cross(Z,tout)
a0=math.atan2((Ein-C)[1],(Ein-C)[0]);a1=math.atan2((Eout-C)[1],(Eout-C)[0]);sweep=(a1-a0)%(2*math.pi)
ar(C,Ein-C,Z,sweep)
Q=np.array([40.11,-36.804,H-30]);start=Q-30*tout+30*Z;ln(np.array(paths[-1]),start)
ar(Q-30*tout,30*Z,np.cross(tout,-Z),math.pi/2)
ln(np.array(paths[-1]),np.array([40.11,-36.804,139.77]));ar(np.array([40.11,-6.804,139.77]),np.array([0.,-30.,0.]),X,math.pi/2)
ds=np.array(paths);report=dict(centreline=paths,nominal_source_jacket_OD_mm=5.,old_occupied_project_OD_mm=5.8,active_capacity_OD_mm=6.8,minimum_centre_R_mm=30.,analytic_free_mm=448.,same_unit_boot_debit_mm=52.,whole_unit_mm=500.,sample_polyline_mm=float(np.linalg.norm(np.diff(ds,axis=0),axis=1).sum()),end_error=float(np.linalg.norm(ds[-1]-B)),coil_sweep_deg=math.degrees(sweep),no_factory_dimension_claim=True)
(P/'occupied-FFC200-family.json').write_bytes((json.dumps(ffc,indent=2)+'\n').encode())
(P/'occupied-DATA500-transport.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
print('ANALYTIC_OCCUPIED_FAMILIES',len(ffc),'DATA endpoint error',report['end_error'],'sample length',report['sample_polyline_mm'])
