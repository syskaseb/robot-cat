import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def obj(n,s,col=(.12,.125,.135)):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=True;return o
def nut_at(x,y,z):
 r=4/math.sqrt(3);pts=[V(x,y+r*math.cos(k*math.pi/3),z+r*math.sin(k*math.pi/3)) for k in range(6)]
 return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(1.6,0,0)).cut(Part.makeCylinder(1.025,1.62,V(x-.01,y,z),V(1,0,0)))
def run():
 t=time.perf_counter();D.save();old=D.getObject('HC_BACK_HOLLOW_EARS_SOCKET').Shape.copy();old.exportBrep(str(P/'raw-head-back-before-real-assembly-parting.brep'))
 # A real horizontal parting around the pitch mechanism; do not heal/delete faces.
 parts=[]
 for n,z,h in [('HC_BACK_LOWER',50,84),('HC_BACK_UPPER',134,120)]:
  q=old.common(box(-280,-110,z,170,220,h)).removeSplitter();obj(n,q);parts.append({'n':n,'valid':q.isValid(),'solids':len(q.Solids),'v':q.Volume})
 D.getObject('HC_BACK_HOLLOW_EARS_SOCKET').ViewObject.Visibility=False
 # Correct full nut/washer bearing against the REAL printed end plane.
 for y in [-49,49]:
  for z in [110,146]:
   pre='HC_BACK_'+str(y).replace('-','_')+'_'+str(z)
   o=D.getObject(pre+'_nutwasher');o.Shape=Part.makeCylinder(2.5,.5,V(-134,y,z),V(1,0,0)).cut(Part.makeCylinder(1.1,.52,V(-134.01,y,z),V(1,0,0)))
   D.getObject(pre+'_fullnut').Shape=nut_at(-133.5,y,z)
 for y in [-52,52]:
  pre='HC_FRONT_'+str(y).replace('-','_');z=181
  D.getObject(pre+'_nutwasher').Shape=Part.makeCylinder(2.5,.5,V(-200,y,z),V(1,0,0)).cut(Part.makeCylinder(1.1,.52,V(-200.01,y,z),V(1,0,0)))
  D.getObject(pre+'_fullnut').Shape=nut_at(-199.5,y,z)
 # Source end is exact: original(233,0,214) circleR3 normal(1,0,1),
 # retained curved tube rigid(-45,+10,-24) -> (188,10,190).
 root=D.getObject('TAIL_ROTATING_HOLLOW_REAL_ROOT');before=root.Shape.copy();before.exportBrep(str(P/'source-tail-root-before-hollow-continuation.brep'))
 rings=[(187.65,189.65,3.1,(1,0,1)),(199,209,4.5,(8,0,42)),(203,232,4.2,(-2,0,43)),(197,252,3.2,(-18,0,34)),(185,266,2.0,(-12,0,14))]
 outer=[];inner=[]
 for i,(x,z,r,n) in enumerate(rings):
  a=V(*n);a.normalize();c=V(x,10,z);outer.append(Part.Wire(Part.makeCircle(r,c,a)))
  if i==len(rings)-1:c-=a*1.5
  inner.append(Part.Wire(Part.makeCircle(max(.8,r-1.2),c,a)))
 ext=Part.makeLoft(outer,True,False);cavity=Part.makeLoft(inner,True,False)
 sourceinner=Part.makeLoft([Part.Wire(Part.makeCircle(r-1.2,V(x,10,z),V(1,0,1))) for x,z,r in [(140,118,8),(165,141,7),(184,175,5),(188,190,3)]],True,False).common(box(125,-10,142,90,40,80))
 q=before.fuse(ext).cut(cavity).cut(sourceinner).removeSplitter();root.Shape=q
 # One moving print, actual journal/horn/crosspin and caps remain distinct bought/separateparts.
 D.getObject('Ola_tail_ENVELOPE').ViewObject.Visibility=False
 pose=[];pivot=V(140,0,130);tip=V(185,10,266)
 for a in [-15,0,15]:
  p=pivot+A.Rotation(V(0,1,0),a).multVec(tip-pivot);pose.append({'pitchY':a,'tip':list(p)})
 low=before.common(box(120,-20,110,90,70,32))
 put('head-parting-and-hollow-tail.json',{'head_rear_parts':parts,'raw_back_v':old.Volume,'back_split_sum':sum(x['v'] for x in parts),'real_rear_parting_Z134':True,'reason':'Open assembly around pitch mechanism/bearings and factory centre screw; no virtual integral cover detach.','full_hardware_bearing_corrected':{'back25':{'underhead':-152.5,'boss_end':-134,'washer':[-134,-133.5],'fullnut':[-133.5,-131.9],'tip':-127.5},'front30':{'underhead':-225.5,'boss_end':-200,'washer':[-200,-199.5],'fullnut':[-199.5,-197.9],'tip':-195.5}},'tail_rings':rings,'tail_outer_continuation_positive_join':before.common(ext).Volume,'tail_critical_below142_missing':low.cut(q).Volume,'tail_valid':q.isValid(),'tail_solids':len(q.Solids),'tail_volume':q.Volume,'tail_poses':pose,'tail_vertical_tip_range':max(p['tip'][2] for p in pose)-min(p['tip'][2] for p in pose),'tail_axis':[0,1,0],'tail_factory_servo_lead':'FIXED to body because servo case fixed; no extra moving tail wire invented','source_solid_visual_tail_retired':'Unbuilt visual ENVELOPE, not bought material credit','physicalPASS':False,'wholekit':False,'seconds':time.perf_counter()-t})
 D.recompute();D.save();print(json.dumps({'headparts':parts,'tail':[q.isValid(),len(q.Solids),q.Volume],'seconds':time.perf_counter()-t}))
run()
