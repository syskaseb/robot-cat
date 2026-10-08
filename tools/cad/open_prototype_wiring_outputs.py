"""One current output allocation, retaining the existing protected Pi solder joint.

No unspecified extra connector or invented U1/AUX pad. Read-only CAD check and
exact tangent paths; support/attachment and full wiring selection remain open.
"""
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from open_prototype_wiring_endpoints import ROOT, BASE, CURRENT, OUT, read, sha, bounds
from open_prototype_wiring_source_fit import input_path


def main():
    import FreeCAD as A
    import Part
    tick = time.monotonic()
    source_path = BASE/'wiring-checkpoint/source-layout-plan.json'
    interface_path = ROOT/'hardware/electronics/full-cat/main-positive-wiring-card-r1/interface.json'
    helper = ROOT/'tools/cad/open_prototype_wiring_source_fit.py'
    context_path = BASE/'OpenPrototypePlan.FCStd'
    endpoints = read(OUT)
    allocation = read(source_path)
    interface = read(interface_path)
    pi = next(r for r in allocation['source_plan'] if r['holder']=='F_PI')
    pad = next(e['point_mm'] for r in endpoints['body_conductors'] for e in r['ends'] if e['role']=='MAIN.VIN')
    ctx, mounts = A.openDocument(str(context_path)), A.openDocument(str(CURRENT))
    X,Y,Z = A.Vector(1,0,0),A.Vector(0,1,0),A.Vector(0,0,1)
    def line(a,b):
        assert (b-a).Length>1e-7
        return Part.makeLine(a,b)
    def quarter(a,u,v,r=6):
        c=a+v*r; end=a+(u+v)*r
        return Part.Arc(a,c+(u-v)*(r/math.sqrt(2)),end).toShape(),end
    def sweep(edges,diameter,departure):
        wire=Part.Wire(edges)
        start=edges[0].Vertexes[0].Point
        s=wire.makePipeShell([Part.Wire(Part.makeCircle(diameter/2,start,departure))],True,False)
        assert s.isValid() and len(s.Solids)==1
        return s,wire.Length
    start=A.Vector(*pi['output_exit_mm'])
    a=start+X*9; c1,b=quarter(a,X,Z)
    c=b+Z*15; c2,d=quarter(c,Z,-X)
    j=A.Vector(pad[0]-5, start.y, d.z)
    factory_edges=[line(start,a),c1,line(b,c),c2,line(d,j)]
    factory,factory_length=sweep(factory_edges,4,X)
    assert factory_length+8<=84.5, 'Keep delivered minimum and actual strip in same accounting'
    # Two bare8mm ends overlap: .16 starts at j, .18 at j-X*8.
    #20mm sleeve covers the joint and6mm intact insulation each side.
    small_start=j-X*8
    # Two rejected assumptions: clear the holder alone; then clear only its
    # left wall. Both missed the whole package/inlet lane. The retained rail
    # and input are now included BEFORE generating the downward path.
    input_shape=input_path(A,Part,pi,allocation['input_wire_diameter_design_allowance_mm']/2)[0]
    clearance=2.; extension_radius=1.3
    package_left={
        'holder_budget':pi['proposed_body_bounds_mm'][0],
        'input_insulation':input_shape.BoundBox.XMin,
        'retained_left_rail':mounts.SideRail1.Shape.BoundBox.XMin}
    descent_x=min(package_left.values())-clearance-extension_radius
    first_straight=small_start.x-descent_x-6
    a=small_start-X*first_straight; c1,b=quarter(a,-X,-Z)
    cross_z=pad[2]+20
    c=A.Vector(b.x,b.y,cross_z+6); c2,d=quarter(c,-Z,X)
    e=A.Vector(pad[0]-6,d.y,d.z); c3,f=quarter(e,X,-Y)
    g=A.Vector(f.x,pad[1]+6,f.z); c4,h=quarter(g,-Y,-Z)
    neck=A.Vector(*pad)+Z*5
    assert abs((h-neck).Length-9)<1e-6, 'Nine intact mm before5mm exposed MAIN neck'
    extension_edges=[line(small_start,a),c1,line(b,c),c2,line(d,e),c3,line(f,g),c4,line(h,neck)]
    extension,extension_length=sweep(extension_edges,2.6,-X)
    sleeve=Part.makeCylinder(interface['splice']['finished_OD_project_mm']/2,20,j+X*6,-X)
    targets={'W077_factory':factory,'W078_K1474_red':extension,'PiSolderSleeveAllowance':sleeve}
    neighbours={}
    for r in allocation['source_plan']:
        b=r['proposed_body_bounds_mm']
        neighbours[r['holder']+'_budget']=Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
        neighbours[r['holder']+'_input']=input_path(A,Part,r,allocation['input_wire_diameter_design_allowance_mm']/2)[0]
    material,reservations={},{}
    for o in ctx.Objects:
        if 'Shape' not in o.PropertiesList or o.Shape.isNull():continue
        if o.Name.startswith(('P0_','S1_ring_','S1_screw_')) or o.Name in ('LeftRiserWithMain','RightRiser','MainSupplierFamily'):
            material['context/'+o.Name]=o.Shape
        elif o.Name.endswith('_CP2') and o.Name!='MAIN4853_CP2' and mounts.getObject(o.Name) is None and not o.Name.startswith(('W0','F_PI_','F_AUX_','F_HP_','F_HY_','F_TY_')):
            s=o.Shape.copy()
            if o.Name in ('Pi4_CP2','BUS_CP2','PWM9685_CP2','AUX4092_CP2','PWM1608_CP2'):
                # Current board planes differ from the old displayed budget.
                s.translate(Z*(5.72 if o.Name in ('Pi4_CP2','BUS_CP2') else 4.72))
            reservations['context/'+o.Name]=s
    for o in mounts.Objects:
        if 'Shape' not in o.PropertiesList or o.Shape.isNull():continue
        if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.startswith('BUSsupplier') or o.Name.endswith('NominalPCB'):
            material['mount/'+o.Name]=o.Shape
        elif o.Name.endswith('_CP2'):reservations['mount/'+o.Name]=o.Shape
    for group in (mounts.NominalMountHardware,mounts.SideMountHardware):
        for o in group.Group:material['hardware/'+o.Name]=o.Shape
    contacts,reserve_hits,errors=[],[],[]
    pairs=0
    for n,s in targets.items():
        for category,objects,dest in [('material',material,contacts),('reservation',reservations,reserve_hits),('changed_neighbour',neighbours,contacts)]:
            for m,t in objects.items():
                if not s.BoundBox.intersect(t.BoundBox):continue
                pairs+=1
                try:
                    assert s.isValid() and t.isValid()
                    hit=s.common(t);assert hit.isValid()
                    if hit.Volume>1e-5:dest.append(dict(a=n,b=m,volume_mm3=hit.Volume,bounds_mm=bounds(hit),category=category))
                except Exception as exc:errors.append(dict(a=n,b=m,error=str(exc)))
    # Sleeve/insulation overlap is intentional only on the two6mm intact
    # intervals; no blanket exemption for contacts in this neighbourhood.
    self_errors=[]; joint_overlaps=[]
    names=list(targets)
    for i,n in enumerate(names):
        for m in names[i+1:]:
            hit=targets[n].common(targets[m]); assert hit.isValid()
            expected=0.
            if 'PiSolderSleeveAllowance' in (n,m):
                expected=math.pi*(2 if 'W077_factory' in (n,m) else 1.3)**2*6
            if abs(hit.Volume-expected)>1e-5:
                self_errors.append(dict(a=n,b=m,volume_mm3=hit.Volume,expected_mm3=expected))
            joint_overlaps.append(dict(a=n,b=m,volume_mm3=hit.Volume,expected_mm3=expected))
    paths=[source_path,OUT,CURRENT,context_path,interface_path,helper,Path(__file__)]
    result=dict(status='PI_OUTPUT_PATH_CHECKED_SUPPORTS_OPEN' if not(contacts or reserve_hits or errors or self_errors) else 'PI_OUTPUT_LAYOUT_REQUIRES_CHANGE',
        selected=False,stage_completed=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths},
        planned_output_connections=[dict(holder=h,destination=g,status='PLANNED_PI_PAIR_SUPPORTS_OPEN' if h=='F_PI' else 'LOAD_DATUM_OPEN_NO_CENTRE_AS_PIN')
            for h,g in [('F_PI','MAIN.VIN'),('F_AUX','AUX.VIN'),('F_HY','C_HY.V+'),('F_HP','C_HP.V+'),('F_TY','C_TY.V+')]],
        W077=dict(insulated_route_mm=factory_length,bare_overlap_mm=8,required_blank_mm=factory_length+8,
            nominal_fit_blank_mm=82,factory_minimum_mm=84.5,OD4_R6_project_gates=True),
        W078=dict(insulated_route_mm=extension_length,splice_strip_mm=8,MAIN_strip_mm=8,
            required_blank_mm=extension_length+16,nominal_fit_blank_mm=math.ceil((extension_length+16+10)/10)*10,
            material='Red18AWG from SAME K1474; not a new stock cable',OD2p6_R6_project_gates=True),
        splice=dict(factory_insulation_boundary_mm=list(j),extension_insulation_boundary_mm=list(small_start),
            axis=[-1,0,0],bare_overlap_mm=8,sleeve_blank_mm=20,intact_overlap_each_side_mm=6,
            SKU=interface['splice']['outer_sleeve'],new_connector_or_splice_count=0,
            required_independent_grips=[dict(wire='W077',centre_mm=list(j+X*10.5),axis=[1,0,0],length_mm=9),
                dict(wire='W078',centre_mm=list(small_start-X*10.5),axis=[1,0,0],length_mm=9)],
            heat_and_trim_off_PETG=True,actual_joint_OD_and_shrink_profile_phase2=True),
        MAIN=dict(pad_mm=pad,exposed_neck_mm=5,insulated_grip_straight_mm=9,insertion_allowance_mm=3),
        old_MAIN4853_CP2_budget_superseded_by_valid_world_MainSupplierFamily=True,
        planned_insulated_descent_x_mm=descent_x,
        shared_descent_plan=dict(package_left_limits_mm=package_left,
            insulation_radius_mm=extension_radius,clearance_design_mm=clearance,
            reason='External left corridor beyond WHOLE holder/input/rail package; none of their datums moved',
            envelope_is_allocation_not_contact_proof=True),
        rejected_hypotheses=['Descent within holder left wall crossed F_PI material budget',
            'Clearing holder alone by4mm crossed its input; do not repeat that layout'],
        centreline_edges={n:[dict(start_mm=list(e.Vertexes[0].Point),end_mm=list(e.Vertexes[-1].Point),length_mm=e.Length,
            curve=e.Curve.__class__.__name__,centre_mm=list(e.Curve.Center) if hasattr(e.Curve,'Center') else None)
            for e in edges] for n,edges in {'W077':factory_edges,'W078':extension_edges}.items()},
        exact_joint_self_checks=joint_overlaps,self_errors=self_errors,
        tested_candidate_pairs=pairs,material_or_changed_contacts=contacts,reservation_contacts=reserve_hits,errors=errors,
        native_load_paths_whole_stock_and_other_outputs_open=True,
        finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=time.monotonic()-tick)
    dest=BASE/'wiring-checkpoint/source-output-plan.json'
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','W077','W078','material_or_changed_contacts','reservation_contacts','errors','worker_wall_seconds')}),flush=True)
    A.closeDocument(mounts.Name);A.closeDocument(ctx.Name)


if __name__=='__main__':main()
