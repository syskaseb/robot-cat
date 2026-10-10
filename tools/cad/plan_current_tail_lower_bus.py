"""Lower three-feed bus passes the case BEFORE joining the tail triangle.

Shared power/signal layering, exact ring/frame corridor and outside-arc grip.
No native detail until this whole plan is feasible.
"""
from pathlib import Path
import plan_current_tail_inboard as C
A,P,B,box,line,arc,shift=C.A,C.P,C.B,C.box,C.line,C.arc,C.shift
parent=C.build

def build():
 p=parent();n=1.05/C.math.sqrt(3);zr=92-2*n;zg=92+n;y=-41.875
 red=[line([-16,y,151.49],[-65,y,151.49]),arc([-65,y,138.89],[-65,y,151.49],[-77.6,y,138.89]),
  line([-77.6,y,138.89],[-77.6,y,99.1]),arc([-65,y,99.1],[-77.6,y,99.1],[-65,y,86.5])]
 red+=shift(red[-1]['end'],[1,0,0],[0,-1,0],3.125)
 red+=[line(red[-1]['end'],[20,-45,86.5])]
 red+=shift(red[-1]['end'],[1,0,0],[0,0,1],zr-86.5)
 red+=[line(red[-1]['end'],[68,-45,zr])]
 signal=[line([86.51,14.97,79.2],[86.51,37.4,79.2]),arc([73.91,37.4,79.2],[86.51,37.4,79.2],[73.91,50,79.2]),
  line([73.91,50,79.2],[-16.4,50,79.2]),arc([-16.4,37.4,79.2],[-16.4,50,79.2],[-29,37.4,79.2]),
  line([-29,37.4,79.2],[-29,-36.9,79.2]),arc([-16.4,-36.9,79.2],[-29,-36.9,79.2],[-16.4,-49.5,79.2])]
 signal+=shift(signal[-1]['end'],[1,0,0],[0,0,1],95-79.2)
 signal+=shift(signal[-1]['end'],[1,0,0],[0,1,0],3.45)
 signal+=[line(signal[-1]['end'],[40,-46.05,95])]
 signal+=shift(signal[-1]['end'],[1,0,0],[0,0,-1],95-zg)
 signal+=[line(signal[-1]['end'],[68,-46.05,zg])]
 p['routes']['XB32']['parts']=red;p['routes']['XS33']['parts']=signal
 p['carrier_reliefs_mm']=[[83.51,36,77.9,89.51,45,81.5],[-32,-45,77.9,-26,-36,81.5]]
 p['support_plan']+=['Signal column X-29 between frame X-24 and PCA postX-35.825, east of S0 ringmaxX-38.3289.',
  'Red86.5 below casing bands; signal uses Y-49.5 when crossing red level, rises to95 BEFORE both paths enter packed tail. Return joins after its vertical drop.',
  'Ground grip bears on OUTSIDE of elbowX56.15, root tabY-39..-34, not across elbow footprint.']
 p['source_sha256'][Path(__file__).relative_to(C.ROOT).as_posix()]=P.sha(Path(__file__))
 return p

def supports(q):
 q['GroundGripBack']=box([56.15,-48,119,59.5,-36,129.5])
 q['GroundGripTab']=box([49,-39,129.5,62,-34,132.3])
 return q

if __name__=='__main__':
 C.build=build;C.run('lower-bus',supports)
