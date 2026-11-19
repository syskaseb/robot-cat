from common import *
from importlib.machinery import SourceFileLoader
sv=SourceFileLoader('survey',str(P/'station-survey.py')).load_module()
D=sv.D
out={}
for role in ['F_HY','F_HP','F_TY','F_PI','F_AUX']:
 n='PBAY_'+role;out[role]=sv.screen(D.bounds(n),[n],D.shape(n))
n='WAGO615_power_0_0';out['G1']=sv.screen(D.bounds(n),[n],D.shape(n))
out['G1_open_face']=sv.screen(np.array([-22.4,53,148.6,8.4,69.999,153.4]),[n])
wr('seated-units.json',dict(source=sha(native),rows=out));print({k:[(n,sum(v['volume'] for v in h)) for n,h in t.items()] for k,t in out.items()})
