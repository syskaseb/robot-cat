from common import *
s=(H19/'layout.py').read_text().split('# Common nine-lead drop')[0].replace("rd(G/'whole-termination-plan.json')","rd(H19/'whole-termination-plan.json')").replace("rd(G/'named-approaches.json')","rd(H19/'named-approaches.json')")
exec(s[:s.index("for key,v in d['endpoints']")]+s[s.index('def route('):])
for i in range(1,6):
 ep=d['endpoints']['G1.'+str(i)]
 ep.update(point=[-7-6.5*(i-1),-81.5,57.5],outward_axis=[0,-1,0])
def entry(net):
 q=d['endpoints'][net];p=arr(q['point']);a=arr(q.get('outward_axis',[0,0,1]));L=10.5 if net!='MAIN.GND' else 7
 return [p,p+L*a]
for w,diameter in [('W001',4.8),('W025',4.8),('W036',4.8),('W060',3.),('W061',4.8)]:
 a,b=rows[w]['ends'];a=entry(a) if a!='BAT.minus' else [arr([24,-30,102]),arr([24,-30,94])];b=entry(b)[::-1]
 route(w,a,[],b,diameter,17)
 m=rows[w]['material'][0];q=ledger[w];q.update(physical_unit=m['physical_unit'],material=m['sku'],end_allowance_mm=m['termination_project_allowance_mm'],dress_margin_mm=15,stock_limit_mm=m['retained_limit_mm']);q['project_blank_mm']=5*math.ceil((q['transport_mm']+q['end_allowance_mm']+q['dress_margin_mm'])/5)
 print(w,q['project_blank_mm'],q['stock_limit_mm'])
# The battery is seated in the RR door bay. Park the loose lower pair on its short end
# before lifting the battery side of the mate. Run the lower transfer outside the plug's hand space.
q=Saved(native);bb=q.bounds('Battery_GEA223S30X6GT');print('pack',bb)
# Terminate the capacity run on the top face, by the +X end. Delivered pigtail position unmeasured.
p=arr([bb[3]-8,bb[1]+10,bb[5]]);end=arr([61,-30,145])
for i in [-1,1]:
    shift=arr([0,i*2.65,0]);route('pack'+str(i),[p+shift,p+shift+[0,0,8]],[],[end+shift-[0,0,9],end+shift],4.8,17)
wr('lower-approaches.json',tracks);wr('lower-unit-lengths.json',dict(rows=ledger,endpoints={n:q for n,q in d['endpoints'].items() if n.startswith('G1.')}))
