"""Reorganise the servo service loops and the data storage level around the entire box."""
from pathlib import Path
import json,math,numpy as np
P=Path(__file__).parent
src=(P/'unit-layout.py').read_text()
exec(src[:src.index('for role,S,E,fn')])
baseline=json.loads((P/'unit-layout.json').read_bytes())
# Fixed yaw case exits immediately into the aft upward window, before either FHAC.
s=vec([-119.5,0,53.2]);e=vec([-49,-46,115]);r=24
a=arc(s,X,Z,r,math.pi/2);b=line(a[-1],a[-1]+13.8*Z);c=arc(b[-1],Z,X,r,math.pi/2);v=end=e-c[-1];v=v-X*(v@X);rr=np.linalg.norm(v)/2
rest=223.55-r*math.pi-13.8;path,debits,rr=turn(c[-1],e,X,rest)
row('MG250_yaw',chain([a,b,c,path]),250,[11.45,223.55,15],[r*math.pi/2,13.8,r*math.pi/2]+debits,min(r,rr),'fixed upward case exit to companion keyed pair')
s=vec([129.5,-63.8,130]);e=vec([145,-89,66.2]);p,l,r=double(s,e,-X,223.55,24,-1)
row('MG250_tail',p,250,[11.45,223.55,15],l,r,'first bight inboard of the lever bank, second bight descends to underbank tray',inner_R=r-math.hypot(1.75,.9))
rows.append(next(q for q in baseline['rows'] if q['unit']=='JR300_tail'))
# Joint handedness: the pitch case and its free exit turn with yaw. A common
# upper body receiver replaces the former pair below the whole fuse row.
s=vec([-159,-43.8,131.5]);C=vec([-130,0,127]);E=vec([-60,-24,160])
for y in [-20,-10,0,10,20]:
    aa=math.radians(y);R=np.array([[math.cos(aa),-math.sin(aa),0],[math.sin(aa),math.cos(aa),0],[0,0,1]])
    first=(arc(s,-Y,X,25,math.pi/2)-C)@R.T+C;dir=R@X
    theta=abs(aa)
    g=arc(first[-1],dir,unit(X-dir*(dir@X)),30,theta) if theta>1e-6 else first[-1:]
    remainder=223.55-25*math.pi/2-30*theta
    p,l,r=turn(g[-1],E,X,remainder)
    row('MG250_pitch',chain([first,g,p]),250,[11.45,223.55,15],[25*math.pi/2,30*theta]+l,min(25,r),'upper return to body pair, all reserve accessible before the pair',yaw=y,inner_R=min(25,r)-math.hypot(1.75,.9))
for role,s,n,net in [('yaw',vec([-79,-46,115]),Z,['F_HY.out','G_AUX.4','R1.2']),('pitch',vec([-90,-24,160]),-Z,['F_HP.out','G_AUX.3','R2.2'])]:
    # Initial straight exits the full rectangular plug prior to curving.
    r=24;start=line(s,s-5*X);a=arc(start[-1],-X,n,r,math.pi);l=246-5-math.pi*r
    p=chain([start,a,line(a[-1],a[-1]+l*X)])
    row('JR300_'+role,p,300,[12,246,25,9,8],[5,math.pi*r,l],r,'body receiving bay; no slack credit across clamp',inner_R=22.25,fan_direction=[1,0,0],nets=net)
# The DATA first bight goes into the LOWER longitudinal equipment bay rather than
# through the PCB layer. The approach from each end is along its full boot axis.
s=vec([6,-.66,104.1]);end=vec([92.804,78.11,133.77]);v1=vec([0,-34,-58]);v2=vec([0,65,18]);d=end-s;d[0]=0
turns=[v1,v2,d-v1-v2];rr=[np.linalg.norm(v)/2 for v in turns]
free=448-math.pi*sum(rr);pos=(free+end[0]-s[0])/2;neg=free-pos
spans=[pos*.78,neg*.5,pos*.22,neg*.5];assert min(spans)>0 and min(rr)>33.4
p=s.copy();seq=[];ds=[]
for i,v in enumerate(turns):
    t=X*(-1)**i;a=line(p,p+t*spans[i]);b=arc(a[-1],t,unit(v),rr[i],math.pi);seq.extend([a,b]);p=b[-1];ds.extend([spans[i],math.pi*rr[i]])
seq.append(line(p,end));ds.append(spans[3])
row('DATA500',chain(seq),500,[26,448,26],ds,min(rr),'lower open return, project 26 mm boots, 6.8 jacket',OD=6.8,inner_R=min(rr)-3.4)
out=dict(baseline,rows=rows)
for q in rows:assert abs(sum(q['segments'])-q['stock'])<1e-6
out['E2']=[]
# End stations refer to the actual graph. Regional exit assignment is a proposal;
# residual includes both seated contact and the permanent regulator solder land.
for net,sku,ends,pts in [
 ('XP02.source','2147612113',['F_PWM.out','JPWM_SOURCE.1'],[[-27,-42,65],[-4,-42,65],[12,-38,95],[12,-30,124],[35,-29,126]]),
 ('XP03.source','2147611113',['G_TAIL.3','JPWM_SOURCE.2'],[[101,-69,122],[95,-55,127],[68,-54,127],[25,-45,128],[25,-25,126],[35,-25,126]]),
 ('XP02.module','2147632113',['JPWM_MODULE.1','U_PWM.3'],[[61,-29,126],[77,-25,126],[100,-23,146],[140,-16,149],[159,25,147],[159,34,136]]),
 ('XP03.module','2147631113',['JPWM_MODULE.2','U_PWM.2'],[[61,-25,126],[77,-21,126],[97,-19,146],[136,-12,149],[155,26,147],[155,34,136]])]:
    v=np.array(pts);l=float(np.linalg.norm(np.diff(v,axis=0),axis=1).sum())
    out['E2'].append(dict(wire=net,sku=sku,ends=ends,region_spine=pts,regional_transport_mm=l,remaining_220_including_ends_and_lay=220-l,stock=220,actual_cut=None,qualification='not cut; both ends retained, end engagement/axial solder/accessible bight to be fitted'))
out['side_groups']=[
 dict(name='POWER',ends=['K1474','Delock60047','Pi power'],spine=[[-60,-59,58],[-57,-40,72],[-80,-38,87],[-92,-42,101]],stock='separate from DATA and USB_AUDIO, Pi branch and input lengths retain source budget'),
 dict(name='USB_AUDIO',ends=['Pi.USB2_B upper','ReSpeaker USB-C'],spine=[[6,-19.39,104.1],[15,-19.39,104.1],[16,-12,142],[6,2,153],[-18,16,161]],stock=None,qualification='full simultaneous A boots overlap 429.26 mm3 in project fields; delivered USB stock/boot unknown'),
 dict(name='four leg returns',ends=['four separate leg looms','motor banks / inline / BUS'],spine=[[-93,-80,56],[-65,-92,66],[18,-92,67],[102,-89,68],[108,-51,88],[67,39,131]],stock='per-leg bought leads + individual MTA units, distinct from E2'),
 dict(name='axial fuse',ends=['P_REAR.4','F_PWM.in'],spine=[[-45,-42,63],[-39,-42,65],[-35,-42,65]],stock='XP01 protected takeoff max50 mm, full sleeved unit lands immediately adjacent')
]
(P/'installed-looms.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
print([(q['unit'],q.get('yaw'),round(q['path_mm'],2),q.get('inner_R')) for q in rows])
