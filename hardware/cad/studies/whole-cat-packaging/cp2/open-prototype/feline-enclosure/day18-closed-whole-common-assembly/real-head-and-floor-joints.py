import FreeCAD as A, Part, math, json
from pathlib import Path
D=A.ActiveDocument; P=Path(__file__).parent; V=A.Vector
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def cyl(x,y,z,r,h,axis):return Part.makeCylinder(r,h,V(x,y,z),V(*axis))
def obj(n,s,col=(.65,.66,.69)):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;return o
def nut(x,y,z,sgn):
 pp=[V(x+4/math.sqrt(3)*math.cos(i*math.pi/3),y,z+4/math.sqrt(3)*math.sin(i*math.pi/3)) for i in range(6)]
 return Part.Face(Part.Wire(Part.makePolygon(pp+[pp[0]]).Edges)).extrude(V(0,sgn*1.6,0)).cut(cyl(x,y,z,1,1.6,(0,sgn,0)))
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
r=D.getObject('D18C_TRUE_PITCH_OPTICAL_RECEIVER'); f=D.getObject('F3_HEAD_FRONT')
old=r.Shape.copy(); s=old.copy(); h=f.Shape.copy(); cuts=[]; metal=[]
# Replace only inner upper bridge by the real roof arch bolted to BOTH surviving outer lands.
cuts=[box(-159.601,10,152.5,6.002,5.8,5.501),box(-159.601,-15.8,152.5,6.002,5.8,5.501),box(-157,-11,152.5,3.4,22,5.501)]
for q in cuts:s=s.cut(q)
for side in [-1,1]:
 x=-156.6;z=155;d=-side;y=side*25.5
 bore=cyl(x,side*28,z,1.1,16,(0,-side,0));s=s.cut(bore);h=h.cut(bore)
 for tag,q in [('FULL_M2x12',cyl(x,y,z,1,12,(0,d,0)).fuse(cyl(x,y,z,1.9,2,(0,side,0)))),('HEAD_WASHER',cyl(x,side*25,z,2.5,.5,(0,side,0)).cut(cyl(x,side*25,z,1.1,.5,(0,side,0)))),('NUT_WASHER',cyl(x,side*15.3,z,2.5,.5,(0,side,0)).cut(cyl(x,side*15.3,z,1.1,.5,(0,side,0)))),('FULL_NUT',nut(x,side*13.7,z,side))]:
  o=obj('F3_HEAD_ROOT_'+str(side).replace('-','m')+'_'+tag,q);metal.append(o)
r.Shape=s.removeSplitter();f.Shape=h.removeSplitter()
wr('head-two-root-joints.json',{'root':'actual TRUE_PITCH receiver outer two upper lands to integral hollow front skull masts; no attachment to yaw-only fork or bearing','replaced_own_function':'inner top crossbar stiffness replaced by two bolted outer lands plus real rounded roof arch; lower camera plate, both camera sets, ToF plate, journal and lower loadarm retained','valid':[s.isValid(),h.isValid()],'solids':[len(s.Solids),len(h.Solids)],'removed_mm3':old.cut(s).Volume,'steel_count':len(metal),'demand':{'M2x12':2,'washer_M2':4,'nut_M2':2,'stock':'NEEDED_UNCONFIRMED'},'stack_positive_Y':{'head_under':25.5,'headwasher':[25,25.5],'skull_land':[22,25],'receiver_land':[15.8,22],'nutwasher':[15.3,15.8],'fullnut':[13.7,15.3],'full_tip':13.5},'order':'Put complete M2 sets through front skull; hold full nut/washer from open interior BEFORE FFC/ToF handlay and before rear skull; no factory horn centre-stack change','remaining':['rear skull actual closure joints','new head root steel to full FFC/moving part local gate'],'physical_PASS':False})
D.recompute();D.save()
print('HEAD_TRUE_PITCH_TWO_REAL_JOINTS_SAVED')
