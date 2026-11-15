import FreeCAD as A,FreeCADGui as G,Part,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
S=A.getDocument('DAY15_HEAD_OLA_WHOLE');P=Path(S.FileName).parent.parent/'day15-strapped-carrier-first-fit';P.mkdir(exist_ok=True)
D=A.newDocument('DAY15_STRAPPED_CARRIER');groups={}
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape.copy();q.Label=o.Label
 q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for prop in ['ProposalStatus','AssemblyNote','Status','OriginalSource']:
  if prop in o.PropertiesList:q.addProperty('App::PropertyString',prop);setattr(q,prop,str(getattr(o,prop)))
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
# Exactly one cosmeticdelta: uppercheekedge derived below the complete existingeye rims.
mask=D.getObject('Ola_shared_cheek_mask_PROPOSED');before=mask.Shape.copy()
rimZ=min(D.getObject(n).Shape.BoundBox.ZMin for n in ['Ola_eye_gold__1','Ola_eye_gold_1']);z=rimZ-1.25
cut=Part.makeBox(80,140,80,A.Vector(-265,-70,z));mask.Shape=mask.Shape.cut(cut)
assert mask.Shape.isValid();noadded=mask.Shape.cut(before).Volume;assert noadded<1e-6
cosmetic=dict(status='ONE_UPPER_CHEEK_EDGE_RETRACTED_ONLY',source_commit='a28265d0d06037f842510c5897c377d1b0302186',source_native_sha256=hashlib.sha256(Path(S.FileName).read_bytes()).hexdigest(),actual_gold_rim_Zmin=rimZ,upper_edge_Z=z,eye_margin=1.25,addedmaterial=noadded,removed_cosmetic_volume=before.cut(mask.Shape).Volume,profile_windows_preserved_by_subset=True,bought_poses_unchanged=True,tail_back_legs_unchanged=True,no_STL=True)
(P/'cosmetic-upper-edge-delta.json').write_bytes((json.dumps(cosmetic,indent=2)+'\n').encode())
plan=dict(utc=datetime.now(timezone.utc).isoformat(),status='ONE_WHOLE_STRAPPED_RETENTION_HYPOTHESIS_BEFORE_MATERIAL',hypothesis='Existingtwofull200closedloops passingP12guides jointlyretainbattery ANDP19 TOactualP12 sofailedrearM3couldretire. Test actualenclosedloadsections beforeanyprintchange.',existing_constraints=dict(P19_four_feet='compressiononly not upliftroot',battery_endstops='existingXcapture but notframeconnection',front_M3='kept entireactualjoint initially; no assumptionitcanreplacefullrearfunction',fullstraps2=True,selected_width=15,selected_textile_each=200,total210includesbuckle_notextra=True,declared_thickness_capacity=2.2,stationX=[29.5,52.5],P12_guide_Z=[86.1,91.3],P12_surviving_roof=4.7,old_rear_actualS0common=60.30986073465577,actual_P11_receivingROI_material=0),load_path_needed=['battery ->declaredclosedband','band ->positiveP19bearing/capture, notfreefriction','sameband ->ACTUALenclosedfixedP12member/seat','P12 ->existingfourdeckclamps/frame','P19 fourfeet ->compressiondeck and realantiX/Y/rotation interface'],first_causal_gate='For each fullclosedannulus readactualinside cavity and materialsections: is ANYP12fixedmaterial enclosed? Is P19floor captured belowband ratherthan sittingoutsideclosedloop? Ifnot, firsthypothesisFAIL no rearretirement/newprint/secondloopfamily.',actual_stock_FIT=['thickness/buckle/lap/takeup/cellpadding/strength physicalFIT','No invented25pull, no unitcut or210asextra'],all_parts_and_57_extras_retained=True,physical_pass=False,actual_fit_cut_slack=None)
(P/'whole-retention-hypothesis.json').write_bytes((json.dumps(plan,indent=2)+'\n').encode())
D.Label='DAY15 STRAPPED CARRIER / ONE HYPOTHESIS / UNPOWERED FIT ONLY';D.recompute();D.saveAs(str(P/'strapped-carrier.FCStd'))
print(json.dumps(dict(saved=D.FileName,objects=len(D.Objects),cosmetic=cosmetic)))
