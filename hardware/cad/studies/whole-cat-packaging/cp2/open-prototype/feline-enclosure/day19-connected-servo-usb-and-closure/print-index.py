"""Reopen only changed meshes. All other manufactured pieces use verified original bytes."""
from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
code=(E/'print-components.py').read_text()
pre=code[:code.index('ret=[')].replace("D=P.parent/'day19-whole-appearance-and-moving-neck-correction'","D=P.parent/'day19-simple-box-common-core'").replace("P/'whole-cat19E.FCStd'; src=D/'whole-cat19D.FCStd'","P/'whole-cat19F.FCStd'; src=D/'whole-cat19E.FCStd'")
exec(pre)
ret=list(json.loads((P/'new-members.json').read_bytes()))
exec(code[code.index('rows=[];steps=[]'):code.index("new=['E19_KeyedTail")])
for n in ret:
    old=next((q for q in base['parts'] if q['part']==n),{})
    purpose=old.get('hardware_use','removable gallery cap with four snap tongues, fitted after hand lay')
    rows.append(dict(part=n,qty=1,hardware_use=purpose))
coupon=dict(base['off_robot']);f=(E/coupon['stl']).resolve();assert h(f)==coupon['sha256'];coupon['stl']=rel(f)
for q in base['steps']:
    if q['part'] in ret:continue
    f=(E/q['step']).resolve();assert h(f)==q['sha256'];steps.append(dict(q,step=rel(f)))
tail=code[code.index("folder=P/'components'"):].replace('source_19D_sha256','source_19E_sha256').replace("]+[coupon]:","]:").replace("n.endswith('Lid')","n.endswith(('Lid','Cap'))").replace("if n in ['E19_ForeBase','E19_RearBase','E19_KeyedTail']:","if n in ['F19_ForeCap','F19_RearCap','E19_ForeBase']:")
exec(tail)
