import FreeCAD as A,FreeCADGui as G,json,math,time
from pathlib import Path
from PySide import QtCore
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector;t=time.perf_counter()
eff=json.loads((P/'whole-organization-effectivity.json').read_text())
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def unions(ns):
 rows=[{'name':n,'bounds':bb(D.getObject(n).Shape)} for n in ns if D.getObject(n)]
 b=[min(r['bounds'][i] for r in rows) for i in range(3)]+[max(r['bounds'][i] for r in rows) for i in range(3,6)];return {'members':rows,'bounds':b,'size':[b[i+3]-b[i] for i in range(3)]}
# Save candidate prior to ANYlocalcheck, currentoldsource unchanged.
D.save();checks=[]
for a,b,why in [('PBAY_P_SYS','PCA9685_Adafruit815_PCB','fivechamber orientation gives37mm rather than22mm inY; wholePCA/E1layer, notcurve'),('S0_body','S1_NKK_S821_installed','wholecontrols operatingbay'),('S0_key','Monitor_MOD05015','actual keytravel/readout bay'),('Speaker','Pi_GPIO1992_factory_female','wholefront audio/realGPIO'),('AUX_FULL9p5_POPULATED_SCOPE','MAIN_UNSHRUNK_FAMILY_SCOPE','fullPCBfamily/undersides'),('PBAY_F_PI','S0_body','entirefactoryfuse body notwireillustration')]:
 x=D.getObject(a).Shape;y=D.getObject(b).Shape;bx=x.BoundBox;by=y.BoundBox
 low=math.sqrt(sum(max(getattr(bx,k+'Min')-getattr(by,k+'Max'),getattr(by,k+'Min')-getattr(bx,k+'Max'),0)**2 for k in ['X','Y','Z']))
 r={'a':a,'b':b,'named_risk':why,'bbox_lower_mm':low,'threshold':1.25}
 if low>=1.25:r.update({'scoped_status':'SEPARATE_BY_LOWER_BOUND','actualdistance_not_needed':True})
 else:
  r['gap_mm']=x.distToShape(y)[0];r['scoped_status']='NOMINAL_OCCUPANCY_HOLD' if r['gap_mm']<1.25 else 'LOCAL_CLEAR'
 checks.append(r);(P/'first-finite-whole-falsifier.json').write_bytes((json.dumps({'checks':checks,'whole_acceptance':False,'physical_collision_claim':False,'cursor':len(checks)},indent=2)+'\n').encode())
# FULL camera to Pi, not neckonly. KnownworldPiCSIprimary sourcepoint shifts withwholePi, camera unchanged.
C=(-226.85,0,134.6);E=(-50.5,-28.5,60.62);L=math.dist(C,E)
ffc={'whole_unit_nominal_mm':200,'camera_exit_project_datum':C,'Pi_CSI_project_datum':E,'direct_Euclidean_necessary_bound_mm':L,'end_consumption_project_total':10,'bound_plus_end_mm':L+10,'scope':'ONLYnecessarylowerbound at currentprovisionalsourcecontactdatums; NOTactualroute/minfit/physicaldeliveryshortage','result':'CHOSEN_DATUM_AND_10MM_END_BUDGET_HOLD' if L+10>200 else 'NO_LENGTH_ACCEPTANCE_FROM_CHORD','still_unknown':['actualCAMFFC connector datum/contactside and1.6mmPiheightbound','fullinsidehead/neck/roll/fold/radii/motionreserve/wholeuncutlength','no newlongercable orborrowUSB/Grove']}
(P/'CSI200-full-unit-necessary-bound.json').write_bytes((json.dumps(ffc,indent=2)+'\n').encode())
# Major sourcegroup intervals exactly current, notarithmeticpackminimum.
g={'MTA12_complete':unions(['Motor_ATO4A_1_'+str(i) for i in range(6)]+['Motor_ATO4A__1_'+str(i) for i in range(6)]),'WAGO16':unions(['WAGO415_data__1_'+str(i) for i in range(8)]+['WAGO415_data_1_'+str(i) for i in range(1,8)]+['PBAY_P_AUX']),'FHAC5_cases':unions(['PBAY_F_PI','PBAY_F_AUX','PBAY_F_HY','PBAY_F_HP','PBAY_F_TY']),'Pi_battery':unions(['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','Pi_GPIO1992_factory_female','Battery_GEA223S30X6GT']),'S0_full11':unions(['S0_body','S0_key','S0_neck','S0_nut_IN_0_0','S0_nut_OUT_0_0','S0_ring_IN_0_0','S0_ring_OUT_0_0','S0_stud_IN_0_0','S0_stud_OUT_0_0','S0_washer_IN_0_0','S0_washer_OUT_0_0']),'body_provisional_only':unions(['NIGHT_BODY_PROPORTION_ENVELOPE_NOT_PRINT'])}
(P/'current-whole-group-datums.json').write_bytes((json.dumps(g,indent=2)+'\n').encode())
# SamePETGmaterial scope honest: provisionalfilledhulls NEVERmass; retain fulloldcovermaterialasexplicitallowance not hiddenweight credit.
old=json.loads((P.parent/'day16-low-light-whole-correction/same-density-complete-correction-mass.json').read_text());oldby={r['name']:r for r in old['rows']};ret=eff['retained_mechanism_print_names'];known=[]
for n in ret+eff['new_structural_concepts']:
 o=D.getObject(n)
 if o:known.append({'name':n,'volume_mm3':o.Shape.Volume,'PETGsolid_g':o.Shape.Volume*.00127})
cover=[r for r in old['rows'] if r['name'].startswith('LC_CURVED_BODY_') or r['name'] in ['LC_ORBIT_CHEEK_FRONT_MASK','OLA_REAL_BACK_COVER']]
m={'PETG_density':1.27,'current_known_retained_and_new_core_members':known,'known_print_material_g':sum(r['PETGsolid_g'] for r in known),'held_prior6a_covermaterial_g':sum(r['PETG_full_g'] for r in cover),'held_prior6a_covermembers':[r['name'] for r in cover],'envelope_filled_volume_IS_NOT_PRINTMASS':True,'all_other_replaced_functions':'completeboard/tier/WAGOretention/batteryplatform/wholeclamps/steel/skin hardware stillunmodeledfuturematerial; not counted as guaranteed saving','total_whole_mass':None,'baseline70_fullPETG_g':1778.501,'prior6a_same_scope_fullPETG_g':1283.4361041211068,'no_new_total_mass_saving_claim':True}
(P/'same-density-material-accounting.json').write_bytes((json.dumps(m,indent=2)+'\n').encode())
v=G.activeDocument().activeView();d=V(-1.5,-1,.65);d.normalize();r=V(0,0,1).cross(d);r.normalize();v.setCameraOrientation(A.Rotation(r,d.cross(r),d,'ZXY').Q);v.fitAll();v.redraw()
def finish():
 D.Label='NIGHT COMPACT WHOLE CORE - PROPOSAL HOLD';D.save();G.activeDocument().Modified=False
 (P/'actual-native-final-save.json').write_bytes((json.dumps({'UTC':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'path':D.FileName,'objects':len(D.Objects),'saved':True,'modified':False,'pending':None,'GUI_PID':17796,'wholekit':False},indent=2)+'\n').encode())
QtCore.QTimer.singleShot(1500,finish)
print(json.dumps({'checks':checks,'FFCnecessary_bound':ffc,'groups':{n:q['size'] for n,q in g.items()},'seconds':time.perf_counter()-t}))
