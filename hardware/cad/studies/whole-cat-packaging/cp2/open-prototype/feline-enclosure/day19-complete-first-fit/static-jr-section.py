from common import *
src=(F/'service-lay.py').read_text()
s=src[:src.index("for q in list(fixed.values())+moving:")]
s=s[s.index('X,Y,Z='):] if s.startswith('X,Y,Z=') else s
s=s.replace("P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'","P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'")
s=s.replace('start+4*t','start+12*t').replace('242-h-math.pi*r','234-h-math.pi*r').replace('[4,r*math.pi/2,h,r*math.pi/2]','[12,r*math.pi/2,h,r*math.pi/2]')
exec(s)
def station(q):
 p=np.asarray(q['points']);d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
 return {str(k):[float(np.interp(k,d,col)) for col in p.T] for k in [0,5,15,25,35,45,50]}
wr('remote-pulldown-lay.json',dict(fixed={n:station(fixed['JR_'+n]) for n in ['yaw','tail']},pitch=moving,stations={str(q['yaw']):station(q) for q in moving},component=['MRS16000C1002FCT00',3],budget_each=[12,50,196,25,9,8],windows_mm=[15,35],isolated_support=[5,45],actual_cut_fit_slack=None));print([(q['yaw'],q['inner_R']) for q in moving])
