import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def obj(n,s):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.14,.145,.155);return o
def m2(n,x,y,under,L,bearing,lowerwasher=True):
 p=V(x,y,under);a=V(0,0,-1);np=p+a*(bearing+(.5 if lowerwasher else 0));R=4/math.sqrt(3)
 def cy(r,h,t):return Part.makeCylinder(r,h,p+a*t,a)
 pts=[np+V(R*math.cos(k*math.pi/3),R*math.sin(k*math.pi/3),0) for k in range(6)]
 sets=[('screw',cy(1,L,0).fuse(cy(1.9,2,-2))),('headwasher',cy(2.5,.5,0).cut(cy(1.1,.52,-.01))),('fullnut',Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(a*1.6).cut(cy(1.025,1.62,bearing+(.49 if lowerwasher else -.01))))]
 if lowerwasher:sets.append(('nutwasher',cy(2.5,.5,bearing).cut(cy(1.1,.52,bearing-.01))))
 for tag,s in sets:o=obj(n+'_'+tag,s);o.ViewObject.ShapeColor=(.66,.67,.69)
def run():
 t=time.perf_counter();D.save();out={}
 # Fifth active sourcebasekey: purposeful up-over arch aroundactualN5beam+1.48.
 o=D.getObject('FC_R_NEG');old=o.Shape.copy();arch=box(139,-95,52,9.5,19,3).fuse(box(139,-95,43.62,9.5,4,11.38)).fuse(box(139,-78,43.62,9.5,3,11.38));o.Shape=old.fuse(arch).removeSplitter()
 out['rear_key_arch']={'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'source_key_preserved':True,'N5top50p52_to_bridge52':1.48,'N5postX150_to_arch148p5':1.5,'real_positive_attach':old.common(arch).Volume}
 # Fixed touchsupport physicallyroots onN1; removabletray installedafterMICcap.
 n1=D.getObject('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER');root=box(-65,20,130,4,8.75,2.75).fuse(box(-65,24.75,130,4,4,15)).fuse(box(-67,20.5,141.5,19,8.25,3.5));contact=n1.Shape.common(root).Volume
 out['TTP_root_material_common']=contact
 if contact>1e-6:
  n1.Shape=n1.Shape.fuse(root).removeSplitter();tray=box(-70,-8,145,29,24,2).cut(box(-66,-4,144,21,16,4)).fuse(box(-70,14,145,29,11,2))
  for i,x in enumerate([-65,-50]):
   hole=Part.makeCylinder(1.15,12,V(x,23,138));tray=tray.cut(hole);n1.Shape=n1.Shape.cut(hole).removeSplitter();m2('TOUCH_M2x8_'+str(i),x,23,147.5,8,6,False)
  obj('TOUCH_REMOVABLE_SAFE_EDGE_TRAY',tray.removeSplitter());out['TTP']='Realring+2fullM2x8/directfullnutbearing. Safeedge/revisionFIT3; removewiredtray beforeMIC; no inventedTTPmountpattern.'
 # Sharedspeaker rimreceiver onactualfixedlowerMTArail; no pressureonmembrane/magnet.
 mt=D.getObject('FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER');feet=box(-104,77,77,5,13,4).fuse(box(-1,77,77,5,13,4));contact=mt.Shape.common(feet).Volume
 out['speaker_actual_fixed_rail_contact']=contact
 if contact>1e-6:
  upright=box(-104,86,77,3.75,8,70.25).fuse(box(.25,86,77,3.75,8,70.25));rim=box(-104,82.25,97.75,108,2,49.5).cut(box(-100.25,81,99.75,100.5,5,45.5));base=feet.fuse(upright).fuse(rim)
  mt.Shape=mt.Shape.fuse(base).removeSplitter();top=box(-104,84.25,145.25,108,23.5,2).cut(box(-99,84,144,98,20.75,4))
  # Realremovabletopwith2throughsets; gap.25toboughtnominalcase is adjustabletrial, not suppliercontact.
  for i,x in enumerate([-102,2]):
   hole=Part.makeCylinder(1.15,15,V(x,90,136));mt.Shape=mt.Shape.cut(hole).cut(box(x-3,85.5,138.15,6,9,1.8)).removeSplitter();top=top.cut(hole);m2('SPKR_M2x10_'+str(i),x,90,147.75,10,7.5,True)
  obj('SPEAKER_REMOVABLE_BASKET_RIM_TRIAL_KEEPER',top.removeSplitter());out['speaker']='Realrootedopenreceiver+removabletop2fullM2x10. Whole100x21x45casekept. Actualbasket/flange safeland/suspension/magnet sampleFIT3 BEFOREtightening, no certifiedcontactpressure.'
 D.recompute();D.save();out['parts']=[{'n':n,'valid':D.getObject(n).Shape.isValid(),'solids':len(D.getObject(n).Shape.Solids),'v':D.getObject(n).Shape.Volume} for n in ['FC_R_NEG','RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER','TOUCH_REMOVABLE_SAFE_EDGE_TRAY','SPEAKER_REMOVABLE_BASKET_RIM_TRIAL_KEEPER'] if D.getObject(n)]
 out.update({'wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t})
 (P/'remaining-common-audio-receivers.json').write_bytes((json.dumps(out,indent=2)+'\n').encode());print(json.dumps(out))
run()
