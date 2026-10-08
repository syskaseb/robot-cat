"""Cheap changed-route/beam/ATO check BEFORE another native fixture build."""
import json
import time
from pathlib import Path
from open_prototype_fhac_supports import ROOT, BASE, OUT, SOURCE, PLAN, read, sha, bounds, targets, tie_shapes


def main():
    import FreeCAD as A
    import Part
    from open_prototype_source_service import pi_service_route
    tick=time.monotonic();plan=read(PLAN)
    d=A.openDocument(str(SOURCE));ctx=A.openDocument(str(BASE/'OpenPrototypePlan.FCStd'))
    material={};reserved={}
    for doc in (d,ctx):
        for ob in doc.Objects:
            if 'Shape' not in ob.PropertiesList or ob.Shape.isNull():continue
            if doc is d and ob.Name=='PiSpliceInsulationSaddle':continue
            if doc is d and (ob.TypeId in ('PartDesign::Body','App::Link') or ob.Name.endswith('NominalPCB') or ob.Name.startswith('BUSsupplier')):
                material[doc.Name+'/'+ob.Name]=ob.Shape
            elif doc is ctx and (ob.Name.startswith(('P0_','S1_ring_','S1_screw_')) or ob.Name in ('LeftRiserWithMain','RightRiser','MainSupplierFamily')):
                material[doc.Name+'/'+ob.Name]=ob.Shape
            elif ob.Name.endswith('_CP2') and ob.Name!='MAIN4853_CP2' and not ob.Name.startswith(('W0','F_PI_','F_AUX_','F_HP_','F_HY_','F_TY_','Access_','Corridor_')):
                if doc is ctx and d.getObject(ob.Name) is not None:continue
                s=ob.Shape.copy()
                if doc is ctx and ob.Name in ('Pi4_CP2','BUS_CP2','PWM9685_CP2','AUX4092_CP2','PWM1608_CP2'):
                    s.translate(A.Vector(0,0,5.72 if ob.Name in ('Pi4_CP2','BUS_CP2') else 4.72))
                reserved[doc.Name+'/'+ob.Name]=s
    for group in (d.NominalMountHardware,d.SideMountHardware,d.U1NominalMountHardware):
        for ob in group.Group:material['hardware/'+ob.Name]=ob.Shape
    neighbour=targets(A,Part,plan)
    wires,route=pi_service_route(A,Part)
    # Exact proposed beam including mating strap notches, not a bbox claim.
    beam=Part.makeBox(100,4,2,A.Vector(-67,69,111.99))
    for x in (-32.68,-61.68):
        beam=beam.cut(Part.makeBox(3.5,1.7,2.7,A.Vector(x-1.75,69.3,111.99)))
    assert beam.isValid()
    altered=dict(wires,CurrentPiBeam=beam)
    ties=tie_shapes(A,Part,plan)
    contacts=[];errors=[];pairs=0
    def check(n,s,objects):
        nonlocal pairs
        for m,t in objects.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            pairs+=1
            try:
                assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:contacts.append(dict(a=n,b=m,volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
            except Exception as e:errors.append(dict(a=n,b=m,error=str(e)))
    for n,s in altered.items():check(n,s,dict(material,**reserved,**neighbour,**ties))
    # No tool motion claim: current vertical ATO budget must not meet output.
    pi=next(r for r in plan['source_plan'] if r['holder']=='F_PI');b=pi['proposed_body_bounds_mm']
    access=Part.makeBox(22,10,35,A.Vector((b[0]+b[3])/2-11,(b[1]+b[4])/2-5,b[5]))
    check('PI_ATO_tool_budget',access,altered)
    record=dict(status='CHANGED_PI_SERVICE_CORRIDOR_PREFLIGHT_CHECKED' if not(contacts or errors) else 'SERVICE_PREFLIGHT_REQUIRES_LAYOUT_CHANGE',
        contacts=contacts,errors=errors,tested_pairs=pairs,route=route,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (PLAN,SOURCE,
            ROOT/'tools/cad/open_prototype_source_service.py',Path(__file__))},
        scope='Only changed Pi route/beam/nominal ATO opening before native build; all fixture check still required',
        physical_pass=False,selected=False,stage_completed=False,wall_seconds=time.monotonic()-tick)
    (OUT/'fhac-space-preflight.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:record[k] for k in ('status','contacts','errors','wall_seconds')}),flush=True)
    A.closeDocument(ctx.Name);A.closeDocument(d.Name)


if __name__=='__main__':main()
