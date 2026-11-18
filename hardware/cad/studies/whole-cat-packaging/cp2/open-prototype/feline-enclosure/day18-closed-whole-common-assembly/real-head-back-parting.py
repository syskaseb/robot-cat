import FreeCAD as A,Part,json,math
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def cy(x,y,z,r,h,dx=1):return Part.makeCylinder(r,h,V(x,y,z),V(dx,0,0))
def ell(c,r):
 s=Part.makeSphere(1);m=A.Matrix();m.A11,m.A22,m.A33=r;s=s.transformGeometry(m);s.translate(V(*c));return s
def add(n,s):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.65,.66,.69);return o
front=D.getObject('F3_HEAD_FRONT');back=D.getObject('F3_HEAD_BACK');fo=front.Shape.copy();bo=back.Shape.copy();f=fo.copy();b=bo.copy();outer=ell((-134,0,150),(64,77,64));rows=[]
for side in [-1,1]:
 y=side*73;z=145
 boss=box(-145,y-3,z-7,8,6,14).common(outer)
 f=f.fuse(boss)
 pocket=box(-140,y-3.25,z-7.25,3.25,6.5,14.5)
 b=b.cut(pocket).fuse(box(-136.75,y-3,z-7,3.5,6,14).common(outer))
 bore=cy(-150,y,z,1.1,22);f=f.cut(bore);b=b.cut(bore)
 # Full washer and driver enter through actual outer-wall service port, not a fictitious detached rear shell.
 b=b.cut(cy(-132.7,y,z,2.75,34))
 shaft=cy(-132.75,y,z,1,16,-1).fuse(cy(-132.75,y,z,1.9,2,1))
 hw=cy(-133.25,y,z,2.5,.5).cut(cy(-133.25,y,z,1.1,.5))
 nw=cy(-145.5,y,z,2.5,.5).cut(cy(-145.5,y,z,1.1,.5))
 pp=[V(-147.1,y+4/math.sqrt(3)*math.cos(i*math.pi/3),z+4/math.sqrt(3)*math.sin(i*math.pi/3)) for i in range(6)]
 nu=Part.Face(Part.Wire(Part.makePolygon(pp+[pp[0]]).Edges)).extrude(V(1.6,0,0)).cut(cy(-147.1,y,z,1,1.6))
 for tag,q in [('FULL_M2x16',shaft),('HEAD_WASHER',hw),('NUT_WASHER',nw),('FULL_NUT',nu)]:add('F3_HEAD_BACK_'+str(side).replace('-','m')+'_'+tag,q)
 rows.append({'side':side,'front_boss_volume':boss.Volume,'full_tip_mm':1.65,'gap_pocket':.25,'driver_port_diameter':5.5})
front.Shape=f.removeSplitter();back.Shape=b.removeSplitter()
r={'parts':{'front':{'valid':front.Shape.isValid(),'solids':len(front.Shape.Solids)},'back':{'valid':back.Shape.isValid(),'solids':len(back.Shape.Solids)}},'parting_common':front.Shape.common(back.Shape).Volume,'retained_front_missing_planned_bores_only':fo.cut(front.Shape).Volume,'retained_back_planned_pockets_and_toolports':bo.cut(back.Shape).Volume,'joints':rows,'demand':{'M2x16':2,'M2_nut':2,'M2_washer':4,'inventory':'NEEDED_UNCONFIRMED'},'assembly':'Front shell is first bolted to TRUE PITCH outer lands. Load rear shell onto two keyed lap bosses; hold full front nuts/washers through still-open lower neck, then feed complete rear washers/screws through actual D5.5 service ports. Close neck guard only after whole cable lay. No virtual factory disconnection.','remaining':'Actual new head/source/FFC local hazard and moving shell/body clearance needed; no whole motion PASS','physical_PASS':False}
(P/'head-back-real-parting.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());D.recompute();D.save();print('HEAD_BACK_REAL_TWO_KEYED_JOINTS',r)
