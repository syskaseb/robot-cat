import FreeCAD as A, FreeCADGui as G, Part, json, math
from pathlib import Path
V=A.Vector
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit')
D=A.getDocument('DAY14_WAVEGO_FIRST_FIT_UNRELEASED');A.setActiveDocument(D.Name)
d=json.loads((P/'layout.json').read_text())
by={r['id']:r for r in d['rows']}
def bounds(s):
 b=s.BoundBox;return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
def change(n,p,dim=None):
 r=by[n];o=D.getObject(r['object'])
 if dim:o.Shape=Part.makeBox(*dim,V(*p))
 else:
  s=o.Shape.copy();b=s.BoundBox;s.translate(V(p[0]-b.XMin,p[1]-b.YMin,p[2]-b.ZMin));o.Shape=s
 r['bounds_mm']=bounds(o.Shape);r['volume_mm3']=o.Shape.Volume
def remove(n):
 r=by.pop(n);D.removeObject(r['object']);d['rows'].remove(r)
def support(n,p,dim,note):
 o=D.addObject('PartDesign::Feature',n);o.Shape=Part.makeBox(*dim,V(*p));o.ViewObject.ShapeColor=(.74,.73,.67)
 o.addProperty('App::PropertyString','FitStatus').FitStatus='PROPOSED_SHARED_LOAD_STRUCTURE_NOT_PRINT_READY'
 o.addProperty('App::PropertyString','AssemblyNote').AssemblyNote=note
 D.getObject('Shared_structure_PROPOSED').addObject(o)
 r=dict(id=n,object=o.Name,evidence='PROPOSED_shared_support_blank_not_print_ready',source='',bounds_mm=bounds(o.Shape),volume_mm3=o.Shape.Volume,notes=note);d['rows'].append(r);by[n]=r
# Complete first arrangement's shared-support layer before freeze; no old architecture inherited.
change('WAGO415_data_-1_7',[129,20,50.52])
change('WAGO415_data_1_7',[107,20,50.52])
by['WAGO415_data_-1_7']['notes']+=' Rear positive-side pair keeps whole S0 body/metal bay clear.'
for i,x in enumerate([-96,-51,-6,39]):change('Leg_protected_MTA0100335_'+str(i),[x,-48.5,67])
change('F0_FHAC0002_30A',[-132,32,49],[26,35,70])
change('POST_F0_WAGO412',[-130,-59,50],[13,20,10])
change('BNO085',[-100,-48,80])
for n in list(by):
 if n.startswith('Pi_standoff') or n.startswith('Logic_shelf_post') or n=='Logic_common_side_shelf' or n.startswith('Tray_standoff'):remove(n)
for i,x in enumerate([5,95]):
 for y in [-45,41]:support('Battery_edgepost_%s_%s'%(i,y),[x,y,48.52],[5,4,13.48],'Outside lower WAGO rows; whole tray/crossarm removable after unplugging battery.')
 support('Battery_crossarm_'+str(i),[x,-45,62],[5,90,3],'Two simple crossarms carry central removable tray; leg-fuse bodies start67 above arm65.')
for x,y in [(-104,-49),(-104,44),(101,-49),(101,44)]:support('Upper_frame_post_%s_%s'%(x,y),[x,y,48.52],[3,3,41.48],'Source deck-rooted perimeter frame; avoids lower WAGO fields; complete fastening/stiffness to fit coupon.')
for y in [-49,44]:support('Upper_frame_rail_'+str(y),[-104,y,90],[212,3,3],'Two shared side beams, not one local grip per module.')
for x in [-104,105]:support('Upper_frame_end_'+str(x),[x,-49,90],[3,96,3],'Ties shared sideframes. S0 body ends88.52 below rail90; actual local fit is a named check.')
for x in [-102,-31]:support('Pi_bridge_'+str(x),[x,-49,93],[5,96,3],'Bridges between common side rails before boards/fuses. X-31 fits between PCA and E1, nominal interfaces to verify.')
support('Pi_removable_common_tray',[-101,-41,95.52],[91,62,3],'Common Pi plate on two bridges; board mounts insulated; USB front and GPIO negativeY kept accessible.')
support('BUS_upper_simple_shelf',[-83,-7,123],[48,39,3],'Above populated Pi nominal envelope; actual connector/cooling fit in FIT2. Four standoffs/support interfaces to detail, not print ready.')
change('Rear_crossbeam',[112,-79,43.52],[65,161,2])
for n in ['S0_panel_endstand_-76','S0_panel_endstand_-7']:remove(n)
panel=D.getObjectsByLabel('Rear_S0_shared_panel_BLANK')[0]
panel.Shape=Part.makeBox(70,94,3,V(107,-76,85.52)).cut(Part.makeCylinder(12.2,5,V(135.5,-29.3289166382,84.52)))
by['Rear_S0_shared_panel_BLANK']['bounds_mm']=bounds(panel.Shape)
by['Rear_S0_shared_panel_BLANK']['volume_mm3']=panel.Shape.Volume
for x in [107,169]:
 for y in [-76,12]:support('S0_panel_sharedpost_%s_%s'%(x,y),[x,y,48.52],[6,6,37],'Four simple posts outside actual S0 body and ring bounds, from rear deck extension to shared neck panel; no wire load.')
# Named first-fit hazards on actual new arrangement only. No blanket scan or historical tests.
pairs=[('S0_body','WAGO415_data_1_7'),('S0_body','WAGO415_data_-1_7'),('S0_body','Upper_frame_end_105'),('Battery_GEA223S30X6GT','Speaker'),('Battery_GEA223S30X6GT','MAIN_Pololu4853'),('Pi_removable_common_tray','PCA9685_Adafruit815_PCB')]
for a,b in pairs:
 s=D.getObject(by[a]['object']).Shape;t=D.getObject(by[b]['object']).Shape
 d['checks'].append(dict(hazard=a+' VS '+b,gap_mm=s.distToShape(t)[0],status='NAMED_NEUTRAL_GEOMETRY_PAIR_ONLY_NOT_WHOLE_MOTION_OR_PHYSICAL_PASS'))
d['first_fit_layer_completion']='Before first freeze, lower rear WAGO pair on positive side; battery crossarms above open WAGO; upper common perimeter frame outside lower cases; front mainfuse upright beside neck. No old local detail/variant series.'
d['decision']='WHOLE_FIRST_FIT_CANDIDATE_READY_FOR_ONE_REVIEW; no physical/print/wholeassembly acceptance. Shared support blanks still need root fasteners, electrical shielding and three named fitting checks.'
d['support_scope']='Concept has actual source-hole roots, shared rails/deck/crossarms/perimeter frame and individual board/support blanks; mating/hole details unbuilt. UpperBUS shelf support, terminal guards, batterystrap slots, S0 M6 and MGshaft coupling remain in the three prototype fit groups.'
# Explicit installed tiny-part/stock accounting: retain every CSV selection without fictitious loose geometry.
d['grouped_selected_functions']={'E1':['Adafruit1608/1208','SN74LVC8T245','L78L05','all selected resistors/caps/Harwin headers','0.1A0242logic'],'MG_harness':['three selected JR300','three remoteR7R8R9','three1Afuses','selectedE2Molex pair/fourcontacts'],'battery_and_power':['two selectedstraps','XT60Hpair','selectedM10/M3rings','WAGO2212411 x8 distributed inline','main30A+4leg10A+12motor4A+AUX4A+Pi3A+3MG1A+logic0.1A'],'factory_lengths':['4separate MTA0100335 units: full220 each and bothends','5FHAC0001 twofactory leads>=84.5 each','K1474one1m2colourunit proper210MAINinput/350Piallocations from source, no pooling','LanbergUSB500 + currentlyselectedDelock60047','MAX3/850project/900physicalceil5(M+20) preserved as source accounting until actualchosenroute; no fabricated fit/shortage']}
(P/'layout.json').write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
D.Label='DAY14 WAVEGO FIRST FIT — UNRELEASED / one arrangement'
D.recompute();G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();D.save()
print(json.dumps({'document':D.Name,'objects':len(D.Objects),'checks':d['checks'],'saved':D.FileName}))
