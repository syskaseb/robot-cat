from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,html,math
from PIL import Image,ImageDraw
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['day07-SOURCE-under-bank-side-bay-actual-input-read.json','day07-SOURCE-under-bank-side-bay-current-sections.png','day07-SOURCE-under-bank-side-bay-current-sections.svg','day07-SOURCE-under-bank-vertical-return-whole-proposal.json','day07-SOURCE-sidebay-vertical-mandatory-E55-first-gate.json','day07-SOURCE-sidebay-vertical-mandatory-E55-first-gate.breps.zip','day07-SOURCE-sidebay-adaptive-bounds-interruption-receipt.json','day07-SOURCE-sidebay-E55-E65-continuous-neutral-capacity.json','day07-SOURCE-sidebay-E55-E65-analytic-whole-cover.breps.zip','day07-SOURCE-sidebay-D-exit-U1-local-hazard.json','day07-SOURCE-sidebay-D-exit-U1-local-witness.breps.zip']
a=json.loads((out/names[0]).read_bytes());p0=json.loads((out/names[3]).read_bytes());b=json.loads((out/names[4]).read_bytes());c=json.loads((out/names[7]).read_bytes());f=json.loads((out/names[9]).read_bytes());i0=json.loads((out/names[6]).read_bytes())
assert c['cursor']==c['total']==48 and c['unreceived']==0 and c['outline']['expanded_whole_cover_outside_mm3']==0
assert f['cursor']==1 and f['unreceived']==21 and abs(f['first_falsifier']['allocated_common_mm3']-12.622951141116701)<1e-7
im=Image.new('RGB',(1400,1000),'white');dr=ImageDraw.Draw(im);sv=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1000"><rect width="1400" height="1000" fill="white"/>']
def txt(x,y,t,col='#222'):
 dr.text((x,y),t,fill=col);sv.append(f'<text x="{x}" y="{y+13}" font-family="sans-serif" font-size="14" fill="{col}">{html.escape(t)}</text>')
def line(pts,col,width=2):
 if len(pts)>1:dr.line(pts,fill=col,width=width);sv.append('<polyline fill="none" stroke="'+col+'" stroke-width="'+str(width)+'" points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+'"/>')
txt(20,15,'SOURCE SIDE BAY: static six-core capacity CLOSED SCOPED / direct D exit HOLD / NOT SELECTED / N01 0/10')
txt(20,42,'Current fixed-source section Y55 (context) + XZ projection of ALL six separate Y storage planes; no contact inference from image.')
ox=70;oy=530;scale=4.7
project=lambda x,z:(ox+(x+138)*scale,oy-(z+48)*4.5)
for q in a['sections']:
 if q['Y_mm']!=55:continue
 col='#cc273a' if 'Ref_Material_P0_' in q['name'] else '#2758c8' if any(s in q['name'] for s in ['Foundation','Support','BankPad']) else '#8b8b8b'
 for cc in q['curves_xz']:line([project(x,z) for x,z in cc],col,2)
R=p0['family']['R_mm'];xc=p0['family']['centre_X_mm'];top=p0['family']['upper_port_Z_mm']
for E,col in [(55,'#d37b10'),(65,'#8f4e08')]:
 d=(E-(math.pi-2)*R)/2;zc=top-d;pts=[(xc-R,top),(xc-R,zc)]+[(xc-R*math.cos(t*math.pi/90),zc-R*math.sin(t*math.pi/90)) for t in range(91)]+[(xc+R,top)];line([project(x,z) for x,z in pts],col,4)
 txt(1080,115+(E-55)*3,'E'+str(E)+' / L_U='+str(2*R+E)+' mm',col)
x=f['P'][0];line([project(x,top+R*math.sin(t*math.pi/180)) for t in range(91)],'#c12a3b',4);pt=f['first_falsifier']['witnesses'][0][0];px,pz=project(pt[0],pt[2]);dr.ellipse((px-6,pz-6,px+6,pz+6),fill='#c12a3b');txt(px+12,pz-4,'U1 actual common12.622951 mm3','#c12a3b')
for x0 in [-130,-100,-50,0,50,100]:xx,zz=project(x0,-48);txt(xx,zz+8,str(x0))
txt(30,570,'Static: 228 analytic cover cells / 48 current valid-source distances / min3.574228 / actual BodyOuter expanded3.25 outside0.')
txt(30,598,'Six independent Y planes: W00553 / W02258 / W02163 / W00668 / W02473 / W02378 mm; R35.1 fixed; E55..65 each.')
txt(30,626,'Direct D up-to-minusY exit: 1/22, 21 unreceived; fails actual complete U1 material. No source material cut or new support.')
txt(30,670,'WHOLE CHAIN / actual ends retained; dashed links below are OPEN, not drawn routes:')
txt(30,698,'factory14 -> moving Knee6/Hip3 + existing FL3 splice/lands -> received left9 passage -> OPEN inlet/roll')
txt(30,726,'-> STATIC six-body-capacity fields -> HOLD direct D exit / OPEN G,V fans -> actual D3/G3/V3 full9 ends')
txt(30,764,'Physical units / complete ID accounting (new whole lengths NULL):')
for j,(u,ids) in enumerate([('SOURCE/FL1 continuous / Hip10','W004 D / W020 V / W019 G'),('SOURCE/FL2 continuous / each55','W005 D / W022 V / W021 G'),('SOURCE/FL3 original Knee portions','W006 D / W024 V / W023 G'),('DONOR/FL3 body portions / each55','W006 D / W024 V / W023 G')]):txt(30,792+j*27,u+' : '+ids)
txt(30,921,'NOT accepted: usable moving slack, actual per-core deltaL, connected fans/assembly/root, all12 minimums/fitceil5(+20)/MAX3.')
txt(30,950,'No old pair replay. New21/rest108 included neutral; their old motion155 was NOT replayed and does not qualify this new bay.')
sv.append('</svg>');png=out/'day07-SOURCE-sidebay-capacity-and-exit-current-view.png';sp=png.with_suffix('.svg');im.save(png);sp.write_bytes(('\n'.join(sv)+'\n').encode());names +=[png.name,sp.name]
checks=[]
for n in names:
 if n.endswith('.zip'):
  with zipfile.ZipFile(out/n) as z:
   assert z.testzip() is None;gg=json.loads(z.read('manifest.json'))['geometry']
   for q in gg:assert hashlib.sha256(z.read(q['entry'])).hexdigest()==q['sha256']
   checks.append(dict(path=n,crc_ok=True,member_sha_verified=len(gg)))
for src in ['robot-cat74-under-bank-side-bay-current-read.py','robot-cat74-render-actual-side-bay-sections.py','robot-cat74-sidebay-six-mandatory-U-first-gate.py','robot-cat74-sidebay-adaptive-E55-E65-cover.py','robot-cat74-resume-same-adaptive-cover-cached-bounds.py','robot-cat74-sidebay-D-exit-current-U1-local-hazard.py','robot-cat74-package-sidebay-current-outcome.py']:
 n='day07-'+src.removeprefix('robot-cat74-').removesuffix('.py')+'.recipe.py';assert not(out/n).exists();(out/n).write_bytes((temp/src).read_bytes());names.append(n)
pins=[q['path'] for q in p0['source_pins'] if q['path'] not in names]+['day07-coordinator-SOURCE-splice-layout-authority-receipt.json','day07-coordinator-SOURCE-frozen-S-family-math-receipt.json']
pins=[n for n in dict.fromkeys(pins) if (out/n).exists()]
times=[dict(receipt=n,operation_seconds=q['operation_seconds'],process_cpu_seconds=q['process_cpu_seconds']) for n,q in [(names[0],a),(names[4],b),(names[7],c),(names[9],f)]]
p=out/'day07-SOURCE-sidebay-capacity-and-exit-bounded-disposition.json';assert not p.exists();r=dict(id=p.stem,status='BODY_VERTICAL_STORAGE_CAPACITY_SCOPED_CLOSED_DIRECT_U1_EXIT_HOLD_WHOLE_APPROACH_OPEN',selected=False,N01_complete=False,
 closed_problem='Actualunder-bank6independentverticalXZreservoirs E55..65/R35.1 canfitstaticfullprofiles/currentfixedparts+neutralrest108/new21. Notanemptybox: 156sourcecandidates/65actualsections, 6mandatoryE55validprofiles/5distances, 228analyticcontinuousfamilycovercells/48distances/contour3.25. Nextactualfunctionalconnectionfalsified: upwardDexit crossescurrentU1completecarrier. ThusSTATICcapacityisnotusablemovingreserve/wholephysicalfit.',
 static_storage=dict(independent_core_rows=p0['six_independent_storage_branches'],full_E55_profile_quality=b['full_six_profile_quality'],mandatory_E55_received=b['cursor'],adaptive_cells=c['cells'],adaptive_rows_received=c['cursor'],adaptive_unreceived=c['unreceived'],minimum_adaptive_current_gap_mm=c['minimum_actual_cell_gap_mm'],independent_layer_packing=c['independent_layer_packing'],actual_outline=c['outline'],same_neutral_context_count=c['whole_current_context']),
 direct_exit=dict(named_hazard=f['named_hazard'],first_falsifier=f['first_falsifier'],received=f['cursor'],total=f['total'],unreceived=f['unreceived'],U1_function_NOT_waived=True,no_U1_material_removed=True,static_capacity_NOT_claimed_usable55=True),
 all9_body_rows=p0['all9_body_rows'],all12_physical_portions=p0['all12_physical_portions'],all4_physical_units=p0['all4_physical_units'],
 current_actual_percore_accounting=[dict(wire=q['wire'],physical_unit=q['physical_unit'],piece_id=q['piece_id'],body_lane=q.get('body_lane'),new_body_region_U_length_only_mm=[125.2,135.2] if q['physical_unit'] in ['SOURCE/FL2','DONOR/FL3'] else None,actual_moving_leg_and_fan_variation_mm=None,source14_terminal11_full9_properprefix_NOT_doublecounted=True,FL2_continuous_NOlap4=q['physical_unit']=='SOURCE/FL2',lap4_only_existing_FL3_joint=q['physical_unit'] in ['SOURCE/FL3','DONOR/FL3'],whole_minimum_mm=None,whole_fit_ceil5_minplus20_mm=None,actual_cut_mm=None,accepted_stored_slack_mm=None) for q in p0['all12_physical_portions']],
 budget_scope='Source14terminal11/full9eachproperprefixonce; FL2NOlap4/FL3existingownedjointlap4once/3x8laps3x20sleeves/stagger2x9lands/factoryplug/850project+900MAX3perphysicalunit/ceil5(min+20) and20NOTslack. Planned55EACHKneephysicalcore/10Hip preserved, no pool/oldprefix/chord/181205225197534614credit/newcut/splice/purchase.',
 remaining_OPEN=['Bothstorageinlet/exit tangents andrealU1/framepassage/branchfans/currentD9G24.25V9 connectedsourcefunctions','ActualKnee6/Hip3groupapproach/caseAnkle-ground/roll/newbodydelta motion/independentpercoreL_i(p)','E_i(p)=55+maxL_i-L_i; deltaL_i<=10 ifcurrent55..65capacity reused; noold4.732/sharedphiassumption','All12portion perphysicalMAX3 minima/installed/slack/assembly/loosetransfer/noreservebehindfixedclamps','W068wholepressure/currentoldretention/fullstock/S0routine/PWM/FPI C0C1/123246/U1far/headNorth/4MTA/four220/wholeN010'],
 next='ChooseONEWHOLEstorage-port orientation +actualU1/panelframeaperture/receiverlayer order BEFOREnewmaterial: currentverticalUPports leadthroughU1, notusablejustbecauseUbayfits. ReuseunchangedstaticE55..65onlywhereidentity/spaceheld; realheading/entryandDGVfanmustdecideconnectedtopology, notscalarS/Uheight/headnudge/shorterR/55waiver. Actualpercorecurrentleg+fanlengths/variation thenMAX3beforeV3detail. Currentdirectexit1of22/21frozen; no resumefailedinput/newFPIprint.',
 computation_recovery=dict(receipt=names[6],same_geometry=True,no_designfailure_increment=True,no_distance_rows_before_interrupt=i0['new_exact_distance_rows_before_interrupt'],process_CPU_until_recovery_snapshot_seconds=i0['process_CPU_to_recovery_snapshot_seconds'],wall_until_recovery_snapshot_seconds=i0['wall_to_recovery_snapshot_seconds'],wall_scope='Includesidle/recovery time afterKeyboardInterrupt, NOTCADkernelwall. Numericcachedboundsrepair SAME228cells/1445sources took.063s; no repeatedacceptedpairs.'),
 timings=times,measured_completed_native_wall_seconds=sum(q['operation_seconds'] for q in times),measured_completed_native_process_CPU_seconds=sum(q['process_cpu_seconds'] for q in times),
 view=dict(path=png.name,sha256=sha(png),actual_fixed_sections=True,allocation_projection_distinct=True,visually_inspected=False),source_pins=[dict(path=n,sha256=sha(out/n)) for n in pins],packet_pins=[dict(path=n,sha256=sha(out/n),bytes=(out/n).stat().st_size) for n in names],archive_checks=checks,native=dict(pid=26064,session_id=46493,state='IDLE',pending_operation=None,unsaved_geometry=False),current_parent_not_replaced=True,unchanged='Currenta9f78e06/2d1d8cfa/def3e56a/base1292/effective1311/newmoving21+4temp/rest108; source4ties/MODULE2/BUS/currentW068notomitted/four220/both4MTA/R47P0E6MAIN46.52/foreign1.25/outline3.25/alloldnegativecounts. No source/V3/FPI print built/selected.',written_utc=datetime.now(timezone.utc).isoformat())
p.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(dict(receipt=p.name,sha256=sha(p),packet=len(names),sources=len(pins),archives=checks,wall=r['measured_completed_native_wall_seconds'],CPU=r['measured_completed_native_process_CPU_seconds']),indent=2))
