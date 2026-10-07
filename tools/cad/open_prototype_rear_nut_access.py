"""Change the rejected axial rear socket approach to lateral open-end access.

Only two changed tool paths and the final lower print are checked. The prior
four socket collisions are preserved, never waived as false contacts.
"""
from pathlib import Path
from datetime import datetime, timezone
import json,time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/mounting-checkpoint'

def sha(p):
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    import FreeCAD as A, Part, Mesh, MeshPart
    tick=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    target=OUT/'board-rear-tool-checks.json';assert not target.exists()
    prior=json.loads((OUT/'board-hardware-checks.json').read_text(encoding='utf-8'))
    native=OUT/'BoardMountAssembly.FCStd';assert sha(native)==prior['native_sha256']
    assert not prior['errors'] and len(prior['contacts'])==4
    assert {r['a'] for r in prior['contacts']}=={'UpperFrame7NutToolStage','UpperFrame8NutToolStage'}
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in
        [native,OUT/'board-hardware-checks.json',OUT.parent/'OpenPrototypePlan.FCStd',Path(__file__)]}
    d=A.openDocument(str(native));context=A.openDocument(str(OUT.parent/'OpenPrototypePlan.FCStd'))
    try:
        obstacles={o.Name:o.Shape for o in context.Objects if 'Shape' in o.PropertiesList and not o.Shape.isNull()
            and (o.Name.startswith('P0_') or o.Name in ('LeftRiserWithMain','RightRiser','MainSupplierFamily'))}
        obstacles.update({n:d.getObject(n).Shape for n in ('LowerCarrier','UpperCarrier')})
        obstacles.update({o.Name:o.Shape for o in d.Objects if o.TypeId=='App::Link'})
        contacts=[];errors=[];tested=0;paths=[]
        for identifier,y in [('UpperFrame7NutToolStage',-30),('UpperFrame8NutToolStage',30)]:
            # AF5.5 open-end spanner: jaw outer width9, slot5.5,
            # thickness1.5 at nut mid-plane. Continuous +X approach40mm;
            # each jaw and back/handle prism describes its complete swept path.
            z=37.27
            jaws=[Part.makeBox(53.4,1.75,1.5,A.Vector(134,y-4.5,z)),
                  Part.makeBox(53.4,1.75,1.5,A.Vector(134,y+2.75,z))]
            handle=Part.makeBox(83.6,9,1.5,A.Vector(141.4,y-4.5,z))
            sweep=jaws[0].fuse(jaws[1]).fuse(handle).removeSplitter()
            assert sweep.isValid() and len(sweep.Solids)==1 and not sweep.check(True)
            for name,s in obstacles.items():
                if not sweep.BoundBox.intersect(s.BoundBox):continue
                tested+=1
                try:
                    assert s.isValid();hit=sweep.common(s);assert hit.isValid()
                    if hit.Volume>1e-5:contacts.append(dict(a=identifier,b=name,volume_mm3=hit.Volume))
                except Exception as e:errors.append(dict(a=identifier,b=name,error=str(e)))
            paths.append(dict(id=identifier,replaces='D7 axial socket from below',
                new_approach='AF5.5 flat open-end spanner from rear +X',
                continuous_entry_distance_mm=40,nominal_tool_thickness_mm=1.5,outer_width_mm=9,
                z_mm=[37.27,38.77],nut_z_mm=[36.82,39.22],
                prerequisite='Source isolated; fit upper plate nuts before connectors/harness; rear approach unoccupied',
                real_tool_and_clearance_coupon_in_phase2=True))
        exports=[]
        if not contacts and not errors:
            s=d.LowerCarrier.Shape.copy();b=s.BoundBox;s.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
            export=OUT/'LowerCarrierAssembly.stl'
            MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.2,Relative=False).write(str(export))
            mesh=Mesh.Mesh(str(export));assert mesh.isSolid() and mesh.countComponents()==1
            size=[mesh.BoundBox.XLength+10,mesh.BoundBox.YLength+10,mesh.BoundBox.ZLength]
            assert max(size)<256
            exports=[dict(part='LowerCarrier',quantity=1,replaces='LowerCarrier.stl',
                path=export.relative_to(ROOT).as_posix(),sha256=sha(export),bounds_with_5mm_brim_mm=size)]
        assert all(sha(ROOT/k)==v for k,v in pins.items())
        result=dict(status='LATERAL_REAR_NUT_ACCESS_CLEAR' if not(contacts or errors) else 'LATERAL_REAR_NUT_ACCESS_REJECTED',
            source_sha256=pins,started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=round(time.monotonic()-tick,3),exact_changed_pairs=tested,
            contacts=contacts,errors=errors,tool_paths=paths,exports=exports,
            retains_all_other_hardware_checks=True,old_socket_contacts_retained=True,
            unchanged_geometry_checks_not_repeated=True,physical_pass=False,stage_completed=False,
            open=['PCB populated fit','Distribution supports and joint integration','Delivered tools/PETG fit and load in phase2'])
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('status','worker_wall_seconds','exact_changed_pairs','contacts','errors')}),flush=True)
    finally:
        A.closeDocument(context.Name);A.closeDocument(d.Name)

if __name__=='__main__':main()
