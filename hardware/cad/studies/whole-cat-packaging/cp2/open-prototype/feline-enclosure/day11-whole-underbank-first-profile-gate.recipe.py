import FreeCAD as A,Part,json,hashlib,math,time,zipfile,os
from pathlib import Path
t=time.monotonic();c=time.process_time();O=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');D=A.ActiveDocument
assert os.getpid()==26044 and D.getObject('N01Status').RetainedCount==1311
p=O/'day11-WHOLE-end-to-end-underbank-load-layer-proposal.json';P=json.loads(p.read_bytes());F=json.loads((O/P['frozen_numeric_input']['path']).read_bytes());idx=json.loads((O/'day11-GUI-working-snapshot-source-index.json').read_bytes());target=D.getObject(idx['actor_names_to_objects'][P['first_falsifier']['target']]);assert target.Shape.isValid()
caps=[];noms=[];rows=[]
for q in F['nine_ID_twelve_portions']:
 if q['physical_unit']=='SOURCE/FL3':continue
 k=q['core'];unit=q['physical_unit'];y=P['required_trunk']['columns_Y_mm'][k];z={'SOURCE/FL1':28.7,'SOURCE/FL2':32,'DONOR/FL3':35.3}[unit];end=q['receiver_held9_frame']['end'][0];length=end+126;r=1 if k=='V' else 1.55
 cap=Part.makeCylinder(r+.4,length,A.Vector(-126,y,z),A.Vector(1,0,0));nom=Part.makeCylinder(r,length,A.Vector(-126,y,z),A.Vector(1,0,0));assert cap.isValid() and nom.isValid();caps.append(cap);noms.append(nom);rows.append(dict(wire=q['wire'],unit=unit,core=k,start=[-126,y,z],end=[end,y,z],component_length_mm=length,nominal_r_mm=r,margin_mm=.4,nominal_volume_mm3=nom.Volume,allocated_volume_mm3=cap.Volume))
field=Part.makeCompound(caps);nominal=Part.makeCompound(noms);assert field.isValid() and nominal.isValid() and len(field.Solids)==9
gap,w,_=field.distToShape(target.Shape);co=field.common(target.Shape);ng=nominal.distToShape(target.Shape)[0];nc=nominal.common(target.Shape);assert co.isValid() and nc.isValid()
if co.Volume>1e-8: x=(co.BoundBox.XMin+co.BoundBox.XMax)/2
else: x=w[0][0].x
section=[];plane=Part.makePlane(220,180,A.Vector(x,-110,-55),A.Vector(1,0,0),A.Vector(0,1,0))
for name,s in [('CURRENT_P0_SIDELEFT22',target.Shape),('ACTUAL_ALLOCATED_BRANCH_FIELD',field),('NOMINAL_BRANCH_FIELD',nominal)]:
 a=s.section(plane);curves=[]
 for e in a.Edges:curves.append([[v.y,v.z] for v in e.discretize(Deflection=.08)])
 section.append(dict(name=name,curves_YZ=curves))
g=D.addObject('App::DocumentObjectGroup','WholeEndToEndPremise');g.Label='PROPOSED wholebank-layer diagnostic / firstP0gate ONLY / N01_0of10'
for name,s,col,vis in [('UnderbankActualAllocated',field,(.9,.2,.1),True),('UnderbankNominal',nominal,(.1,.6,.8),False)]:
 o=D.addObject('Part::Feature',name);o.Label=name+' / no wholefeasibilityclaim';o.Shape=s;o.ViewObject.ShapeColor=col;g.addObject(o);o.Visibility=vis
ar=O/'day11-WHOLE-end-to-end-underbank-first-gate.breps.zip';gm=[]
with zipfile.ZipFile(ar,'w',zipfile.ZIP_DEFLATED) as zf:
 for i,(name,s) in enumerate([('DECLINING9_ALLOCATED_FIELD',field),('DECLINING9_NOMINAL_FIELD',nominal),('CURRENT_P0_SIDELEFT22',target.Shape),('VALID_ALLOCATED_COMMON',co),('VALID_NOMINAL_COMMON',nc)]):
  raw=s.exportBrepToString().encode();entry=str(i)+'.brep';zf.writestr(entry,raw);gm.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),valid=s.isValid(),volume_mm3=s.Volume))
 zf.writestr('manifest.json',(json.dumps(dict(geometry=gm),indent=2)+'\n').encode())
r=dict(id='day11-WHOLE-end-to-end-underbank-first-gate',status='WHOLE_UNDERBANK_TRUNK_P0_HOLD_STOP_FAMILY' if gap<1.25-1e-7 else 'LOCAL_MANDATORY_TRUNK_P0_CLEAR_OTHER_LINKS_UNKNOWN',proposal=p.name,proposal_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),frozen_math_input=P['frozen_numeric_input'],allocated_gap_mm=gap,allocated_common_valid=True,allocated_common_mm3=co.Volume,nominal_gap_mm=ng,nominal_common_valid=True,nominal_common_mm3=nc.Volume,required_foreign_mm=1.25,received_new_pairs=1,no_other_family_run=True,target_actor=target.SourceActor,target_gui_object=target.Name,rows=rows,section_plane_x_mm=x,section=section,witnesses=[[list(a),list(b)] for a,b in w[:2]],fullnormalfield='Straight+X normalYZ, unchanged full3.1/2/3.1,.2gaps,.4outermargin, components stop atactualbranchcolumns; no9atoneport. R/roll at branch/source transitions NOTqualified.',allocated_interpretation='This exact mandatoryoccupied component HOLD is not deliveredwirecontact, all3Dspace impossibility, actualroute/minfit or physicalstockshortage. CurrentP0frame not erased/cut/own. No nextheight/roll/localtrim.',all_actual_Li_A_U_fit_slack_cut=None,N01='0/10',archive=ar.name,archive_sha256=hashlib.sha256(ar.read_bytes()).hexdigest(),geometry=gm,operation_seconds=time.monotonic()-t,process_cpu_seconds=time.process_time()-c,gui_pid=os.getpid(),source_cache_not_used=True)
pp=O/(r['id']+'.json');pp.write_bytes((json.dumps(r,indent=2)+'\n').encode());D.recompute();print(json.dumps({k:r[k] for k in ['status','allocated_gap_mm','allocated_common_mm3','nominal_gap_mm','nominal_common_mm3','section_plane_x_mm','operation_seconds','process_cpu_seconds']}))
