"""Three complete fixed converter leads, registered to supplier pad drawing.

Save sources before CAD. Supplier bottom DXF maps to component-side XY by
reflection x_top=y_dxf,y_top=x_dxf; never register a bottom photograph as top.
Installed revision, soldering and terminal cages remain dry-fit conditions.
"""
import json,sys
from pathlib import Path
import xb11_upstream_route as R
from full_cat_board_interfaces import dxf_polylines,DXF
sys.path.insert(0,str(R.ROOT/'tools/cad'))
from check_main_p0_placement import SavedShapes,prop
A,Part,ROOT=R.A,R.Part,R.ROOT
OUT=ROOT/'hardware/electronics/full-cat/aux-converter-routes-r2'
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
    assert not (OUT/'checks.json').exists(),'Preserve saved result; changed paths need new revision'
    OUT.mkdir(exist_ok=True)
    cross=[]
    for q in dxf_polylines():
        if len(q)==2 and abs((q[1][0]-q[0][0])-.04)<1e-6 and abs(q[1][1]-q[0][1])<1e-9:
            cross.append([round((q[0][0]+q[1][0])/2,6),round(q[0][1],6)])
    assert sorted(cross)==[[x,y] for x in (.25,.35,.45,.55,.65,.75) for y in (.05,.15)]
    pads={net:[16+.05*25.4,-12.7+x*25.4,155.6002]
          for net,x in [('VIN',.45),('GND',.55),('VOUT',.75)]}
    z=155.6002
    routes={
      'XA02':dict(endpoints=['F_AUX.out','4092.VIN'],color='red',
        points=[[96,17.6,132],[115,17.6,132],[115,50,132],[115,50,176],[-15,50,176],[-15,-1.27,176],[17.27,-1.27,176],pads['VIN']]),
      'XA03':dict(endpoints=['4092.VOUT','P_AUX.1'],color='red',
        points=[pads['VOUT'],[17.27,6.35,176],[-25,6.35,176],[-25,66,176],[-25,66,113.5],[.5,66,113.5]]),
      'XA04':dict(endpoints=['4092.GND','G_AUX.2'],color='black',
        points=[pads['GND'],[17.27,1.27,181],[-35,1.27,181],[-35,-44,181],[-35,-44,151],[80,-44,151],[80,-75,151],[80,-75,113.5],[110.5,-75,113.5]])}
    plan=dict(status='SOURCE_SAVED_BEFORE_THREE_NEW_ROUTES',routes=routes,pads_world_mm=pads,
      pad_basis=dict(dxf=str(DXF.relative_to(ROOT)),sha256=R.sha(DXF),
        supplier='https://www.pololu.com/product/4092',top_labels='https://a.pololu-files.com/picture/0J10742.1200.png?72ba56c9b0ea605456cc74a75e63010e',
        bottom_dimension_image='https://a.pololu-files.com/picture/0J10740.1200.jpg?b5e894b2ac43935199c4281dd6fc0aa9',
        registration='DXF bottom-view x,y reflected to component top y,x. Three-hole pattern preserved; electrical labels distinguish mirror. Origin world(16,-12.7), PCB bottom154, planning thickness1.6002.',
        image_remote_not_locally_hash_pinned=True,delivered_revision_verified=False),
      wire='HELU23502 red /23501 black 1mm2 OD2.5; fixed R15',
      pad_termination='Component-side direct solder, wire normal to pad then R15 away from parts. Bare tinned end restricted to pad, no threading whole strand bundle through Ø1.02 drill. Sleeve up to pad; no VIN/GND/VOUT bridges. VRP/EN/PG unused.',
      solder_clearance='Adjacent VIN/GND holes2.54mm apart versus OD2.5 gives only0.04mm insulation gap. Route is candidate, not solder/thermal PASS; actual pad land, sleeve and workmanship must fit. Do not enlarge bare joints.',
      restraints='Board-end three insulated legs secured via releasable T18I interlinked to existing Carrier x11 tie pair; tie clear of components/pads. Existing cassette restraint x82 at input; WAGO mounting-tie end restraints at P_AUX and G_AUX. Intermediate raised routes need fixed restraint locations after interference check.',
      terminal_cages='P_AUX.1 Y66 and G_AUX.2 Y-75 are provisional cage centers, not delivered pin pitch qualification.',
      component_reservations='Conservative PCB/parts boxes excluding photographed pad strip; not manufacturer full3D CAD.',
      new_stls=0,physical_pass=False,phase1_complete=False)
    dump('plan.json',plan)
    tubes={};paths={}
    for name,r in routes.items():
        p=[A.Vector(*v) for v in r['points']];path=R.rounded(p,15)
        t=path.makePipeShell([Part.Wire([Part.makeCircle(1.25,p[0],p[1]-p[0])])],True,False)
        assert t.isValid() and len(t.Solids)==1
        t.exportBrep(str(OUT/(name+'_DESIGN.brep')));tubes[name]=t;paths[name]=path
    reader=SavedShapes();obstacles=[]
    def add(name,s):
        for i,t in enumerate(s.Solids):
            if any(R.overlap(t.BoundBox,w.BoundBox) for w in tubes.values()):
                assert t.isValid();obstacles.append((name,i,t))
    e6=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';objs=reader.doc(e6)
    for link in prop(objs['RobotCatAssembly24'],'Group').findall('.//Link'):
        wrapper=link.get('value')
        if not wrapper.startswith('Rigid_'):continue
        name=prop(objs[wrapper],'Group').findall('.//Link')[0].get('value')
        if name in ('ShellMounted20','Part__Feature038'):continue
        s=reader.shape(e6,name);s.Placement=reader.placement(objs[wrapper])*s.Placement;add(name,s)
    for f,o in [('hardware/cad/studies/xb11-hangers-r2/DeckXB11Hangers.FCStd','Deck'),
      ('hardware/cad/studies/aux-splice-shelf-r2/AuxSpliceShelfR2.FCStd','Shelf'),
      ('hardware/cad/studies/upper-cover-mount-r1/RaisedUpperCoverMount.FCStd','CoverMountHole4')]:add(f+'#'+o,reader.shape(ROOT/f,o))
    s=reader.shape(ROOT/'hardware/cad/studies/full-cat-board-carrier/service-access-r1/CarrierServicePorts.FCStd','Carrier');s.translate(A.Vector(21,0,144));add('Carrier_world21_0_144',s)
    for n,b in {'P_AUX_design':[.5,57,109,19.5,87,118], 'G_AUX_design':[110.5,-84,109,129.5,-54,118],
      'Pololu_PCB':[16,-12.7,154,41.4,12.7,z], 'Pololu_components_except_pad_strip':[20.5,-12.7,z,41.4,12.7,163.5],
      'Adafruit_populated_design':[-59,-12.7,154,3.23,12.7,164],
      'F_AUX_design':[51,11.6,122,72.2,23.6,142], 'P_REAR_design':[10,-18.5,124,32,18.5,135]}.items():add(n,R.box(b))
    for f in ('hardware/electronics/full-cat/xb11-upstream-route-r3/XB11_DESIGN.brep','hardware/electronics/full-cat/xa06-ground-bridge-r1/XA06_DESIGN.brep'):
        s=Part.Shape();s.read(str(ROOT/f));add(f,s);reader.hashes[f]=R.sha(ROOT/f)
    rows=[]
    for name,w in tubes.items():
        for owner,i,s in obstacles:
            if R.overlap(s.BoundBox,w.BoundBox):
                v=R.volume(s.common(w));rows.append(dict(wire=name,owner=owner,solid=i,positive_mm3=v,distance_mm=s.distToShape(w)[0] if v<1e-5 else 0))
    for n,w in tubes.items():
        for m,v in tubes.items():
            if n<m:rows.append(dict(wire=n,owner=m,solid=0,positive_mm3=R.volume(w.common(v)),distance_mm=w.distToShape(v)[0]))
    hits=[r for r in rows if r['positive_mm3']>1e-5]
    for i,(n,k,s) in enumerate(obstacles):s.exportBrep(str(OUT/f'obstacle_{i:03}.brep'))
    dump('checks.json',dict(status='REJECTED_ROUTES' if hits else 'NOMINAL_ROUTES_CANDIDATE',source_sha256=reader.hashes,
      script_sha256=R.sha(Path(__file__)),plan_sha256=R.sha(OUT/'plan.json'),exact_pairs=rows,hits=hits,
      obstacle_cache=[dict(owner=n,solid=k,file=f'obstacle_{i:03}.brep') for i,(n,k,s) in enumerate(obstacles)],
      lengths_mm={n:p.Length for n,p in paths.items()},samples={n:[[v.x,v.y,v.z] for e in p.Edges for v in e.discretize(Deflection=.15)] for n,p in paths.items()},
      anchors_complete=False,new_stls=0,physical_pass=False,phase1_complete=False))
    print(json.dumps(dict(hits=hits,pairs=len(rows),lengths={n:p.Length for n,p in paths.items()})),flush=True)
if __name__=='__main__':main()
