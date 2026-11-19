from common import *
s=(H19/'layout.py').read_text().split('tracks={}')[0];exec(s)
b=rd(P/'changed-branch-lays.json');d['endpoints'].update(b['endpoints'])
rows={v['wire']:v for v in d['wires']};result={}
for name in ['W026/factory','W041/factory','W026/custom','W041/custom']:
 a,e=[d['endpoints'][k] for k in rows[name]['ends']];p,q=arr(a['point']),arr(e['point'])
 u=arr(a.get('outward_axis',[1,0,0]));v=arr(e.get('outward_axis',[1,0,0]))
 def ray(p,v):
    return np.round(clear([p+j*v for j in np.arange(0,20,2)]),1).tolist()
 a0=p+9*u;e0=q+9*v;z=travel(a0,e0,3.5)
 ps=np.array([p,*z,q]);result[name]=dict(ends=rows[name]['ends'],region_stations=ps.tolist(),corridor_polyline_mm=length(ps),lower_bound_mm=float(np.linalg.norm(q-p)),ray_clearance=[ray(p,u),ray(q,v)],physical=None)
 print(name,ps.round(1).tolist(),result[name]['ray_clearance'])
wr('fl-region.json',result)
