"""Native source-outline PCB and clearly labelled purchased/reference population.

This is not an E1 selection. Custom carrier and retention have separate native
owners. Board thickness is a project parameter; chip and local decouplers follow
its top face. Header seating and fixed base-board passives do not move with it.
"""
import json,time,tempfile,shutil,sys
from pathlib import Path
import FreeCAD as A
import Part,Sketcher
from plan_current_main_sources import ROOT,OUT,SHA
from open_deck_p0_supports import sketch,feature
from open_deck_p0_plate import circle
import plan_u1_socket_passives as F
import plan_u1_socket_links as L
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'electronics'))
import plan_u1_socket_carrier as U

MODEL=OUT/'U1SocketPopulation.FCStd'


def tube(w,r):
    e=w.Edges[0]
    s=w.makePipeShell([Part.Wire([Part.makeCircle(r,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
    assert s.isValid() and len(s.Solids)==1
    return s


def world(x,y):
    return A.Vector(90.32-(y-17.78),-3.81+(17.78-x-8.89),95.3602)


def run():
    tick=time.monotonic();assert not MODEL.exists(),'Receive existing result first'
    pf=OUT/'u1-socket-carrier-plan.json';mf=OUT/'u1-documented-adapter.json'
    lf=OUT/'u1-socket-links-plan.json';ff=OUT/'u1-socket-passive-leads.json'
    gatef=OUT/'u1-socket-passives-resolved.json';carrierf=OUT/'u1-socket-carrier-native.json'
    p=json.loads(pf.read_text());m=json.loads(mf.read_text());fp=json.loads(ff.read_text());lp=json.loads(lf.read_text())
    gate=json.loads(gatef.read_text());carrier=json.loads(carrierf.read_text())
    assert not gate['errors'] and not gate['passive_material_resolutions']
    assert carrier['exact_match_qualified_subtractions']
    for receipt in (gate,carrier):
        for n,h in receipt['source_sha256'].items():assert SHA(ROOT/n)==h,n
    U.check(p);d=A.newDocument('U1SocketPopulation')
    par=d.addObject('App::VarSet','Parameters');par.addProperty('App::PropertyLength','AdapterThickness');par.AdapterThickness=1.6
    pcb=d.addObject('PartDesign::Body','Adapter1208PCB');s=sketch(pcb,'SourceOutline',95.3602)
    for x,y,X,Y in m['board_outline_segments_mm']:
        a,b=world(x,y),world(X,Y);i=s.addGeometry(Part.LineSegment(A.Vector(a.x,a.y,0),A.Vector(b.x,b.y,0)),False)
        s.addConstraint(Sketcher.Constraint('Block',i))
    pcb.Tip=feature(pcb,'Pad','SourceBoard',s,'Parameters.AdapterThickness');s.Visibility=False
    old=pcb.Tip;s=sketch(pcb,'Actual28HeaderHoles','95.3602 mm+Parameters.AdapterThickness')
    coords=[]
    for row in m['rows']:
        x,y=row['TSSOP_face_up_xy_mm'];coords.append(A.Vector(90.32-(y-17.78),-3.81+x-8.89,0))
    for x in (1.27,16.51):
        for y in (3.81,1.27):coords.append(A.Vector(90.32-(y-17.78),-3.81+x-8.89,0))
    assert len({(round(v.x,5),round(v.y,5)) for v in coords})==28
    for v in coords:circle(s,v.x,v.y,1.016)
    cut=pcb.newObject('PartDesign::Pocket','SupplierDrills');cut.Profile=s;cut.BaseFeature=old;cut.setExpression('Length','Parameters.AdapterThickness');pcb.Tip=cut;s.Visibility=False
    fixed=d.addObject('App::Part','FixedPurchasedReferences');upper=d.addObject('App::Part','TopFaceReferences')
    upper.setExpression('Placement.Base.z','Parameters.AdapterThickness-1.6 mm')
    def reference(name,shape,group,qualification):
        o=d.addObject('Part::Feature',name);o.Shape=shape;group.addObject(o)
        o.addProperty('App::PropertyString','Qualification');o.Qualification=qualification
        return o
    def body(name,centre,size,group):
        x,y,z=centre;dx,dy,dz=size
        return reference(name,Part.makeBox(dx,dy,dz,A.Vector(91.59+x-dx/2,y-dy/2,84.3202+z-dz/2)),group,
                         'Supplier maximum body envelope / source-referenced fixed datum, NOT a custom printable part')
    for y in (-11.43,3.81):
        body('Female'+str(y).replace('-','n').replace('.','p'),[-3.81,y,4.325],[31.23,2.65,8.65],fixed)
        body('Male'+str(y).replace('-','n').replace('.','p'),[-3.81,y,9.77],[30.48,2.54,2.54],fixed)
    body('TI_PW_MaxBody',[-1.92,-3.81,13.24],[7.9,4.5,1.2],upper)
    for q in p['parts']+p['adapter_local_parts']:
        body(q['ref'],q['body_center_local_mm'],q['body_size_mm'],upper if q['ref'] in ('C1','C2') else fixed)
    curves=F.curves(fp)
    for n,(w,r,net) in curves.items():
        reference(n.replace('/','_'),tube(w,r),upper if n.startswith(('C1.','C2.')) else fixed,
                  'Fixed formed lead/envelope; net='+net+'; phase2 solder/insulation inspection required')
    for q in lp['links']:
        w=L.path(q['start_mm'],q['end_mm'],q['underside_plane_world_mm'],q['via_xy_mm'])
        reference(q['ref'],tube(w,.4),fixed,'Fixed30AWG project envelope, not motor wiring; net='+q['net'])
    reference('JG_COMB',tube(Part.Wire([Part.makeLine(*[A.Vector(*v) for v in lp['ground_bus']['centreline_mm']])]),.25),fixed,
              'One17mm tinned MRS16 lead offcut, seven same-net annuli; no motor current')
    def validate():
        d.recompute();assert pcb.Shape.isValid() and len(pcb.Shape.Solids)==1 and not pcb.Shape.check(True)
        for o in pcb.Group:
            assert not any(t in ('Invalid','Error') for t in o.State),(o.Name,list(o.State))
            if o.TypeId=='Sketcher::SketchObject':assert o.FullyConstrained and o.solve()==0,o.Name
        assert all(o.Shape.isValid() for g in (fixed,upper) for o in g.Group)
        assert abs(pcb.Shape.BoundBox.ZLength-par.AdapterThickness.Value)<1e-6
    validate();volume=pcb.Shape.Volume;z=d.TI_PW_MaxBody.getGlobalPlacement().Base.z
    par.AdapterThickness=1.8;validate();assert pcb.Shape.Volume>volume
    assert abs(d.TI_PW_MaxBody.getGlobalPlacement().Base.z-z-.2)<1e-6
    par.AdapterThickness=1.6;validate();assert abs(pcb.Shape.Volume-volume)<1e-5
    d.saveAs(str(MODEL));A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-U1-population-') as td:
        f=Path(td)/MODEL.name;shutil.copy2(MODEL,f);d=A.openDocument(str(f));pcb=d.Adapter1208PCB;par=d.Parameters
        fixed=d.FixedPurchasedReferences;upper=d.TopFaceReferences;validate();assert abs(pcb.Shape.Volume-volume)<1e-5
    result=dict(status='NATIVE_POPULATION_REFERENCE_ENDS_SERVICE_SELECTION_OPEN',selected=False,E1_complete=False,physical_pass=False,
                native=MODEL.relative_to(ROOT).as_posix(),native_sha256=SHA(MODEL),
                editable_PCB_outline_edges=8,actual_header_holes=28,parameter_restore_mm=[1.6,1.8,1.6],fresh_relocated_reopen=True,
                custom_print_parts=0,purchased_reference_objects=len(fixed.Group)+len(upper.Group),
                source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (pf,mf,lf,ff,gatef,carrierf,Path(__file__))},
                open=['Complete external wire interfaces/grips and E2 insulation','Retainer-first and12mm socket withdrawal from assembled state',
                      'One selected assembly/netlist/BOM/stock; source solder fillets and delivery dimensions remain phase2 gates'],
                worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'u1-socket-population-native.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    A.closeDocument(d.Name);print(json.dumps(result),flush=True)


if __name__=='__main__':run()
