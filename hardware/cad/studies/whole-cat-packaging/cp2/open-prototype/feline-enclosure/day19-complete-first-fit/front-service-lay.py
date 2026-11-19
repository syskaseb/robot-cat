from common import *
s=(P/'smooth-lower-lay.py').read_text().split('tr={};led={}')[0].replace('N=9;','N=13;').replace('max_nfev=240','max_nfev=190').replace('[-108,-98,43]','[-99,-97,45]')
exec(s)
from scipy.ndimage import distance_transform_edt
field=field-distance_transform_edt(field==0,sampling=step)
# Choose the opened perimeter above the bank for the long-radius HELU return.
# Both conductors remain continuous to their separate ends of the same holder.
b=rd(P/'changed-branch-lays.json');ep.update(b['endpoints']);out={}
for w,seed in [('W041/custom',[[28,-34,87],[49,-20,94],[54,12,106],[35,38,104],[-5,42,97],[-49,18,82],[-64,-10,63],[-58,-39,57],[-42,-46,57]]),('W041/factory',[[-17,-90,139],[-11,-73,145],[-20,-55,143],[-33,-43,135],[-40,-40,124],[-48,-39,116],[-53,-37,103],[-53,-34,90],[-43,-34,84]])]:
 a,bk=rows[w]['ends'];p=np.array(ep[a]['point']);e=np.array(ep[bk]['point']);u=ep[a].get('outward_axis',[1,0,0]);v=ep[bk]['outward_axis'];od=4.2 if w.endswith('custom') else 4.8;r=28.8 if w.endswith('custom') else 16
 path,_,q=fit(p,u,e,v,r,od,seed);m=rows[w]['material'][0];q.update(points=path.round(4).tolist(),diameter=od,stock_mm=None,ends_outside_lay_mm=m['termination_project_allowance_mm'],lap_counted_in_lay=0,project_dress=20 if w.endswith('custom') else 0,material=m['sku'],planned_blank_mm=math.ceil((q['developed']+m['termination_project_allowance_mm']+(20 if w.endswith('custom') else 0))/5)*5,actual_cut_fit_slack=None)
 out[w]=[q];wr('front-service-lay.json',out);print(w,q['developed'],q['minimum_centre_radius']-od/2,flush=True)
