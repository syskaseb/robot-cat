import FreeCAD as A,Part,json,math
from pathlib import Path
from datetime import datetime,timezone
D=A.getDocument('DAY15_STRAPPED_CARRIER');P=Path(D.FileName).parent;V=A.Vector
def rounded(station,w,h,rr):
 y=-w/2;z=75.75-h/2;s=Part.makeBox(15,w-2*rr,h,V(station-7.5,y+rr,z)).fuse(Part.makeBox(15,w,h-2*rr,V(station-7.5,y,z+rr)))
 for yy in [y+rr,y+w-rr]:
  for zz in [z+rr,z+h-rr]:s=s.fuse(Part.makeCylinder(rr,15,V(station-7.5,yy,zz),V(1,0,0)))
 return s
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
old=json.loads((P.parent/'day15-p12-integrated-retention/whole-kit-first-gate.json').read_bytes())
r=dict(utc=datetime.now(timezone.utc).isoformat(),status='NEW_ENCLOSED_LOAD_SECTION_GATE_NOT_OLD_CLEARANCE_REPLAY',physical_question='Can unchangedtwofull200closedloops transfer P19uplift and antiX/Y/rotation TOacceptedfixedP12, sofullrearjointcanretire? Existingguidegap0/common0 didnotanswerthis topology.',rows=[],received_scope_reuse=[x for x in old['checks'] if x['a'].startswith('STRAP') and x['b'] in ['P12_common_deck_speaker','P19_shared_lower_carrier']],sections=[],first_falsifier=None)
# ONE currentloopfamily: the same cavity is read at both distinct actualP12stations, no offsetvariants.
for i,x in enumerate([29.5,52.5]):
 cavity=rounded(x,42,21.5,1.9);loop=D.getObject('STRAP'+str(i)+'_bodyloop_full2p2').Shape
 cavity.exportBrep(str(P/('strap'+str(i)+'-actual-enclosed-cavity.brep')))
 r['rows'].append(dict(station=x,closed_band_bounds=bb(loop),enclosed_cavity_bounds=bb(cavity),cavity_volume=cavity.Volume,method='Exact source annulus inner roundedrectangle42x21.5R1.9 extruded full15width; currentloops unchanged.'))
 for n in ['P12_common_deck_speaker','P19_shared_lower_carrier']:
  s=D.getObject(n).Shape;c=s.common(cavity);row=dict(station=x,part=n,enclosed_actual_material=c.Volume,valid=c.isValid());r['rows'][-1].setdefault('enclosed_material',[]).append(row)
  if n.startswith('P12') and c.Volume<1e-6 and r['first_falsifier'] is None:r['first_falsifier']=row
 sec=dict(stationX=x,curves=[])
 for name in ['P12_common_deck_speaker','P19_shared_lower_carrier','Battery_GEA223S30X6GT','STRAP'+str(i)+'_bodyloop_full2p2','STRAP'+str(i)+'_whole_tail','STRAP'+str(i)+'_closure_fullunit_projectfield']:
  s=D.getObject(name).Shape
  for wire in s.slice(V(1,0,0),x):
   for e in wire.Edges:
    pts=e.discretize(Deflection=.05);sec['curves'].append(dict(name=name,yz=[[p.y,p.z] for p in pts]))
 r['sections'].append(sec)
 r['rows'][-1]['carrier_lower_remaining_floor']=[60.8,62.8];r['rows'][-1]['band_bottom']=[62.8,65.0];r['rows'][-1]['P12guide_roof']=[91.3,96.0];r['rows'][-1]['band_top']=[86.5,88.7]
r['status']='HOLD_NO_FIXED_P12_OR_P19_MATERIAL_ENCLOSED_BOTH_CURRENT_LOOPS'
r['consequence']='Bothclosedloops retainbatteryonly, nottrayTOframe. P19remainingfloor lies BELOWbottomstrap outsideclosedloop; P12roof lies ABOVEtopstrap outsideclosedloop. Openguides do not constitute a hook/root. Fourfeetcompression cannotreplaceupliftroot or guaranteeantiX/Y/rotation. KeeprearM3unbuiltHOLD, DO NOTretireonthishypothesis; no printchange or secondloopfamily.'
r['initial_lay_disposition']='Prethreadandlaypossibleasbatterybandprototype but NOT a completecarrierretainingassembly. No validmountorder canreplace missingloadinterface. ExistingMIC/P15->BUS/P13->XT60+balance->cell removal remainsconditional. FourMTA220fullends/plasticpressure/cellpadding notwaived.'
r['actual_fit_cut_slack']=None;r['no_new_print']=True;r['no_bought_pose_or_profile_change']=True
(P/'closed-load-path-first-gate.json').write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(dict(status=r['status'],rows=r['rows'],first=r['first_falsifier'],sections=[len(s['curves']) for s in r['sections']])))
