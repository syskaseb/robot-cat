from common import *
src=(E/'print-components.py').read_text()
pre=src[:src.index('ret=[')].replace("D=P.parent/'day19-whole-appearance-and-moving-neck-correction'","D=P.parent/'day19-real-terminations-and-assembly'").replace("P/'whole-cat19E.FCStd'; src=D/'whole-cat19D.FCStd'","P/'whole-cat19H.FCStd'; src=D/'whole-cat19G.FCStd'")
exec(pre);names=list(rd(P/'new-members.json'));ret=['E19_FrontShroud','E19_ForeBase',*names]
code=(E/'print-components.py').read_text();exec(code[code.index('rows=[];steps=[]'):code.index("new=['E19_KeyedTail")])
for n in names:
 old=next((r for r in base['parts'] if r['part']==n),{});rows.append(dict(part=n,qty=1,hardware_use=old.get('hardware_use','integral fixed shroud/base with four existing front anchor stacks, yaw bearing bridge and full crosspin, fit before head')))
coupon=dict(base['off_robot']);ff=(G/coupon['stl']).resolve();assert h(ff)==coupon['sha256'];coupon['stl']=rel(ff)
for q in base['steps']:
 if q['part'] in ret:continue
 ff=(G/q['step']).resolve();assert h(ff)==q['sha256'];steps.append(dict(q,step=rel(ff)))
tail=code[code.index("folder=P/'components'"):].replace('source_19D_sha256','source_19G_sha256').replace(']+[coupon]:',']:').replace("if n in ['E19_ForeBase','E19_RearBase','E19_KeyedTail']:","if n in ['H19_FrontFrame','E19_RearBase']:");exec(tail)
