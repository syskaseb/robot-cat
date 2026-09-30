"""Fixed power-ground return from selected P0 G2 to G_AUX, not Pi signal GND."""
import json,sys
from pathlib import Path
import xb11_upstream_route as R
sys.path.insert(0,str(R.ROOT/'tools/cad'))
from check_main_p0_placement import SavedShapes,prop
A,Part,ROOT=R.A,R.Part,R.ROOT
OUT=ROOT/'hardware/electronics/full-cat/xa05-main-aux-return-r1'
REPAIR='--r2' in sys.argv
if REPAIR:OUT=ROOT/'hardware/electronics/full-cat/xa05-main-aux-return-r2'
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
    assert not (OUT/'checks.json').exists();OUT.mkdir(exist_ok=True)
    layout=ROOT/'hardware/electronics/power-platform/open-deck-p0/layout.json'
    g=next(c for c in json.loads(layout.read_text())['components'] if c['id']=='G2')
    assert g['center_xy_mm']==[90,0] and g['footprint_xyxy_mm']==[75,-9.5,105,9.5]
    plan=dict(endpoints=['P0G2.5','G_AUX.1'],rail='power ground shared AUX/PWM return; NOT Pi or signal-only ground',
      wire='HELU23501 black1mm2 OD2.5 fixedR15',waypoints_mm=[[123,9.5,113.5],[123,40,113.5],[90,40,113.5],[90,-81,113.5],[110.5,-81,113.5]],
      G2_registration='Selected Deck center+21,0 world, top109. Retain WAGO221415 footprintX96..126/Y-9.5..9.5; choose+Y entry and cage5 atX123. Dry-fit delivered body orientation.',
      G_AUX_cage_assignment='Logical labels on unnumbered WAGO mouths, negative-to-positiveY: cage1 -81, cage2 -75, cage5 -69, cage3 -63, cage4 -57. XA06 cage5 center preserved; not manufacturer numbered cavities.',
      planning_cage_pitch_mm=6,actual_cage_pitch_verified=False,
      restraints='Two releasable T18I interlinked to existing G2 and G_AUX mounting ties; middle route lies above Deck, never trapped under Carrier spacers. Additional midspan anchor remains to be fitted if sag approaches other wires.',
      cut='Dry-fit then cut with30mm allowance per detachable end plus11mm strip per WAGO end;25percent procurement reserve. No energized fit check.',
      new_stls=0,new_fasteners=0,additional_ties=2,physical_pass=False,phase1_complete=False)
    dump('plan.json',plan)
    if REPAIR:
        plan['waypoints_mm']=[[123,9.5,113.5],[123,40,113.5],[90,40,113.5],[90,-57,113.5],[110.5,-57,113.5]]
        plan['G_AUX_cage_assignment']='Logical labels on unnumbered mouths, negative-to-positiveY: cage4 -81, cage2 -75, cage5 -69, cage3 -63, cage1 -57. XA04/XA06 remain unchanged; head return cage4 is not yet routed.'
        plan['excluded_legacy_owner']='Speaker is an old E6 audio electronics reference, not a selected print/purchased part. Approved hobby scope explicitly has no audio; not an installed obstacle waiver.'
        dump('plan.json',plan)
    p=[A.Vector(*v) for v in plan['waypoints_mm']];path=R.rounded(p,15)
    w=path.makePipeShell([Part.Wire([Part.makeCircle(1.25,p[0],p[1]-p[0])])],True,False)
    assert w.isValid() and len(w.Solids)==1;w.exportBrep(str(OUT/'XA05_DESIGN.brep'))
    reader=SavedShapes();rows=[]
    def test(name,s):
        for i,t in enumerate(s.Solids):
            if R.overlap(t.BoundBox,w.BoundBox):rows.append(dict(owner=name,solid=i,positive_mm3=R.volume(t.common(w)),distance_mm=t.distToShape(w)[0]))
    e6=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';objs=reader.doc(e6)
    for link in prop(objs['RobotCatAssembly24'],'Group').findall('.//Link'):
        wrapper=link.get('value')
        if not wrapper.startswith('Rigid_'):continue
        name=prop(objs[wrapper],'Group').findall('.//Link')[0].get('value')
        if name in ('ShellMounted20','Part__Feature038'):continue
        if REPAIR and name=='Speaker':continue
        s=reader.shape(e6,name);s.Placement=reader.placement(objs[wrapper])*s.Placement;test(name,s)
    for f,o in [('hardware/cad/studies/xb11-hangers-r2/DeckXB11Hangers.FCStd','Deck'),
      ('hardware/cad/studies/aux-splice-shelf-r2/AuxSpliceShelfR2.FCStd','Shelf'),
      ('hardware/cad/studies/upper-cover-mount-r1/RaisedUpperCoverMount.FCStd','CoverMountHole4')]:test(f+'#'+o,reader.shape(ROOT/f,o))
    s=reader.shape(ROOT/'hardware/cad/studies/aux-carrier-wire-ports-r1/CarrierAuxWirePorts.FCStd','Carrier');s.translate(A.Vector(21,0,144));test('selected_new_Carrier',s)
    for n,b in {'P0G2_design':[96,-9.5,109,126,9.5,118], 'G_AUX_design':[110.5,-84,109,129.5,-54,118]}.items():test(n,R.box(b))
    fs=['hardware/electronics/full-cat/xb11-upstream-route-r3/XB11_DESIGN.brep','hardware/electronics/full-cat/xa06-ground-bridge-r1/XA06_DESIGN.brep']
    fs+=['hardware/electronics/full-cat/aux-converter-routes-'+('r2' if n=='XA03' else 'r5')+'/'+n+'_DESIGN.brep' for n in ('XA02','XA03','XA04')]
    for f in fs:
        s=Part.Shape();s.read(str(ROOT/f));test(f,s);reader.hashes[f]=R.sha(ROOT/f)
    hits=[r for r in rows if r['positive_mm3']>1e-5]
    dump('checks.json',dict(status='REJECTED' if hits else 'NOMINAL_POWER_RETURN_CANDIDATE',hits=hits,exact_pairs=rows,
      source_sha256=reader.hashes,layout_sha256=R.sha(layout),plan_sha256=R.sha(OUT/'plan.json'),script_sha256=R.sha(Path(__file__)),
      length_mm=path.Length,samples=[[v.x,v.y,v.z] for e in path.Edges for v in e.discretize(Deflection=.15)],
      new_stls=0,physical_pass=False,phase1_complete=False))
    print(json.dumps(dict(hits=hits,pairs=len(rows),length_mm=path.Length)),flush=True)
if __name__=='__main__':main()
