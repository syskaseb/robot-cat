import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
from datetime import datetime,timezone
D=A.getDocument('DAY15_PI_BATTERY_CARRIER');P=Path(D.FileName).parent
q=D.getObject('Pi4B_actual_PCB').Shape.common(Part.makeBox(12,12,1.6,A.Vector(-80.5,-40.5,98.52)));o=D.addObject('PartDesign::Feature','VIEW_ACTUAL_PI_HOLE_PAD_NOT_PRINT');o.Shape=q;o.ViewObject.ShapeColor=(.12,.6,.2);o.ViewObject.Transparency=55
old=A.getDocument('DAY15_MODULE_RETENTION')
if old:A.closeDocument(old.Name)
for o in D.Objects:
 if hasattr(o,'Shape') and hasattr(o.ViewObject,'Visibility'):o.ViewObject.Visibility=(o.Name in ['COUPON_ONE_CORNER_PI_NUT_WASHER','VIEW_ACTUAL_PI_HOLE_PAD_NOT_PRINT'] or o.Name.startswith('PI0_'))
D.Label='DAY15 Pi coupon / carrier capacity HOLD — NOT installed release';D.recompute();D.save();G.getDocument(D.Name).Modified=False
r=json.loads((P/'Pi-coupon-result.json').read_bytes());r['anti_rotation']=dict(actualnutAF=5,cavityAF=5.2,full_corner_diameter=5/math.cos(math.pi/6),approx_play_each_direction_deg=30-math.degrees(math.acos(5.2/(5/math.cos(math.pi/6)))),lower_flat_engagement_mm=1.9,full_rotation_blocked=True,physical_fit_still_REQUIRED=True);r['post_to_tray_functional_connection']=dict(single_print_shared_annular_section=math.pi*(2.5**2-1.375**2),facecontact_normal_to_Z=True,positive_postvolume_in_tray=0,intended_coverage0missing=True,strength_PASS=False);r['standard_nominal']='DIN912/ISO4762M2.5 socket; washersBN715 ~ISO7089; nutM2.5 DIN934/BN109 nominalAF5/h2, not latestISO4032M5+claim';(P/'Pi-coupon-result.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print(dict(doc=D.Name,objects=len(D.Objects),coupon='fullstock/feed/driver ownfit received; actualinstalled4setOPEN'))
