"""Use the open deck split as the vertical transfer; approach each WAGO from its labelled face."""
from pathlib import Path
import json,numpy as np
P=Path(__file__).parent
def rd(n):return json.loads((P/n).read_bytes())
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=1,ensure_ascii=False)+'\n').encode())
m=rd('mic-port.json');p=np.array(m['pivot_xy']);original=np.array(m['source_19F_mouth']);rot=np.array([[0,1],[-1,0]]);m.update(mouth=[*(p+rot@(original[:2]-p)),original[2]],outward_axis=[1,0,0],final_rotation_from_F_deg=-90);wr('mic-port.json',m)
s=(P/'connections.py').read_text(encoding='utf8').replace('(-84 if idx<2 else 114),(-85 if idx%2==0 else 85)','(114 if idx<2 else -84),(85 if idx%2==0 else -85)').replace("-84 if k[0]=='F' else 114,-90 if k[1]=='L' else 90","114 if k[0]=='F' else -84,90 if k[1]=='L' else -90")
exec(compile(s,'connections.py','exec'))
s=(P/'finish-plan.py').read_text(encoding='utf8')
# finish-plan executes the source port definitions again on startup.
s=s.replace("exec((P/'connections.py').read_text()", "exec((P/'connections.py').read_text()")
s=s.replace("[-23,-46,178],[-22,-47,154]","[15,-41,185],[15,-41,157]")
s=s.replace("[133,-31,150],[143,18,149]","[148,-39,155],[174,-30,157],[180,18,153]")
s=s.replace("[23,-45,139],[end[0],-44,137]","[23,-58,152],[end[0],-57,152]")
s=s.replace("[162,-45,139]","[162,-57,152]").replace("[e[0],-45,139],e+v([0,17,0])","[e[0],-54,152],e+v([0,9,0])")
s=s.replace("sp+v([0,-11,0]),[106,-29,79]","sp+v([0,-4,8]),[99,-30,83]")
s=s.replace("[63,a[1],a[2]],[87,a[1],115]","[-36,a[1],112],[32,a[1]+6,116],[85,a[1]+6,115]")
s=s.replace("[20,5,145],[5,9,151],b+20*ax","[26,7,143],[34,41,153],b+20*ax")
exec(compile(s,'finish-plan.py','exec'))
d=rd(P/'whole-termination-plan.json');d['units']['K1474']['gross_parent_debits_per_core_mm']=[d['units']['K1474']['power_pair_kept'][0]+210,d['units']['K1474']['power_pair_kept'][1]];wr('whole-termination-plan.json',d)
