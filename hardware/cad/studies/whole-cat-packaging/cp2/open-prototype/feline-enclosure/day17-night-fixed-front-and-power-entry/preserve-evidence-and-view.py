import FreeCAD as A,FreeCADGui as G,Part,json,datetime
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
q=D.getObject('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE').Shape.copy();q.rotate(V(-135,0,121),V(0,1,0),-10);q.rotate(V(-106,0,127),V(0,0,1),-20)
for n,s,col in [('FP_WITNESS_HEAD_YAWm20_PITCHm10_NOT_BOM',q,(.78,.66,.45)),('FP_WITNESS_GPIO_INTERSECTION_NOT_MATERIAL',q.common(D.getObject('Pi_GPIO1992_factory_female').Shape),(.9,.08,.12))]:
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=False
 if 'HEAD_' in n:o.ViewObject.Transparency=35
 s.exportBrep(str(P/(n+'.brep')))
a=D.getObject('F0_FHAC0002_30A').Shape;b=D.getObject('NIGHT_YTAIL_FIXED_RECEIVER_ROOT').Shape;dist,pts,infos=a.distToShape(b)
(P/'actual-rear-root-nearest-points.json').write_text(json.dumps({'distance':dist,'points':[[list(x),list(y)] for x,y in pts],'interpretation':'allocation clearance1.0 below1.25; F0 conservativefullunitinstallation envelope, NOTsupplierexactplastic; common0 notclearancePASS'},indent=2)+'\n',encoding='utf-8')
for o in D.Objects:
 if o.Name.startswith('CF_') or o.Name.startswith('FP_WITNESS') or o.Name in ['HN_FFC_NEUTRAL_ALLOCATED_FULL_PROFILE']:o.ViewObject.Visibility=False
for n in ['NIGHT_BODY_PROPORTION_ENVELOPE_NOT_PRINT','NIGHT_HEAD_PROPORTION_ENVELOPE_NOT_PRINT']:
 o=D.getObject(n);o.ViewObject.Visibility=True;o.ViewObject.Transparency=0;o.ViewObject.ShapeColor=(.28,.29,.31)
(P/'whole-visibility-before-local.json').write_text(json.dumps({o.Name:o.ViewObject.Visibility for o in D.Objects},indent=2)+'\n',encoding='utf-8')
d=V(-1.5,-1,.65);d.normalize();r=V(0,0,1).cross(d);r.normalize();v=G.activeDocument().activeView();v.setCameraOrientation(A.Rotation(r,d.cross(r),d,'ZXY').Q);v.fitAll();v.getCameraNode().height.setValue(v.getCameraNode().height.getValue()*1.12)
D.Label='NIGHT FIXED FRONT AND REAR ENTRY - REJECTED WHOLE ALLOCATION';D.save()
print(json.dumps({'objects':len(D.Objects),'rear_gap':dist,'GPIO_witness':D.getObject('FP_WITNESS_GPIO_INTERSECTION_NOT_MATERIAL').Shape.Volume,'source_bought_volumes_unchanged':True,'no_support_STL':True}))
