"""Fresh relocated reopen, staged-driver check and unselected carrier exports.

Original203pair result INCLUDING3superseded-source contacts stays unchanged.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,shutil,tempfile,time
import FreeCAD as A
import Part,Mesh,MeshPart
from open_prototype_shared_distribution_carriers import MODEL,PROOF,OUT,ROOT,MOUNTS,CONTEXT,validate
from open_prototype_wiring_endpoints import read,sha


def main():
    output=OUT/'shared-distribution-carrier-package.json'
    assert not output.exists(),'Receive existing finish result'
    tick=time.monotonic();prior=read(PROOF)
    expected={'retained/SourceLeftCarrier','retained/F_AUX_OutputGuide','retained/F_TY_OutputGuide'}
    assert {r['b'] for r in prior['contacts']}==expected and not prior['errors'] and not prior['outside_torso']
    assert sha(MODEL)==prior['model_sha256']
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (MODEL,PROOF,MOUNTS,CONTEXT,OUT/'TailLocalCurrent.FCStd',Path(__file__))}
    r=dict(schema_version=1,readiness='prototype',selected=False,stage_completed=False,physical_pass=False,
        original_contacts_retained=prior['contacts'],contacts_with_replacements_are_NOT_waived=True,
        replacement_scope='All5source placements/restraints invalidated by shared-allocation-plan;3old interfaces must be replaced before integration',
        contacts=[],errors=[],tested_pairs=0,source_sha256=pins,
        quantities={'LeftDistributionCarrier':1,'RightDistributionCarrier':1,'DistributionSpacer':4},
        hardware_added={'M3x30':0,'M3_washer':0,'M3_nut':0},assembly=prior['assembly'],
        nominal_stack=dict(spacer_bottom_z_mm=47.72,spacer_height_mm=8.28,boss_bottom_z_mm=56,
            well_floor_z_mm=58,washer_z_mm=[58,58.5],underhead_z_mm=58.5,head_top_z_mm=61.5,
            screw_tip_z_mm=28.5,nut_z_mm=[36.82,39.22],thread_protrusion_mm=8.32,bearing_floor_mm=2),
        manufacturing=dict(material='PETG',orientation='WorldZ up after bed translation; upper bridge undersides need removable supports review in phase2',
            printer_cube_mm=[256,256,256],total_reserved_margin_mm=10,nozzle_layer_profile='UNSET',
            physical_gates=['Bearing/creep/upper bridge stiffness','Delivered fastener/adhesive fit coupons','Support removal/electrical isolation']))
    with tempfile.TemporaryDirectory(prefix='robot-cat-carrier-reopen-') as temp:
        copy=Path(temp)/MODEL.name;shutil.copy2(MODEL,copy)
        doc=A.openDocument(str(copy));mount=A.openDocument(str(MOUNTS));ctx=A.openDocument(str(CONTEXT));tail=A.openDocument(str(OUT/'TailLocalCurrent.FCStd'))
        try:
            bodies=[doc.getObject(n) for n in ('LeftDistributionCarrier','RightDistributionCarrier','DistributionSpacer')]
            vol=validate(doc,bodies);assert all(abs(v-prior['native_geometry']['volumes_mm3'][n])<1e-6 for n,v in vol.items())
            r['fresh_relocated_reopen']=True
            def check(n,s,m,t):
                if not s.BoundBox.intersect(t.BoundBox):return
                r['tested_pairs']+=1
                try:
                    assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                    if hit.Volume>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume))
                except Exception as e:r['errors'].append(dict(a=n,b=m,error=str(e)))
            for body in bodies[:2]:check(body.Name,body.Shape,'CurrentTailSupport',tail.CurrentTailSupport.Shape)
            targets={b.Name:b.Shape for b in bodies[:2]}
            for o in mount.Objects:
                if 'Shape' in o.PropertiesList and not o.Shape.isNull() and (o.Name.endswith('NominalPCB') or o.Name.startswith('BUSsupplier') or o.Name in ('LowerCarrier','UpperCarrier')):targets[o.Name]=o.Shape
            for o in ctx.Objects:
                if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','S0_','S1_')) and o.Name!='P0_MG92BMount29':targets[o.Name]=o.Shape
            for i,(x,y) in enumerate([(x,y) for x in (-13,71) for y in (-84.75,84.75)]):
                tool=Part.makeCylinder(1.5,40,A.Vector(x,y,61.5))
                for n,t in targets.items():check('InstallDriver'+str(i+1),tool,n,t)
            r['driver_scope']='Four nominalOD3/40mm install budgets BEFORE WAGO/source wiring; not routine access through installed blocks'
            r['status']='CONDITIONAL_CARRIER_EXPORTS_SOURCE_REPLACEMENT_OPEN' if not r['contacts'] and not r['errors'] else 'CARRIER_FINISH_HAS_OPEN_CONTACTS'
            exports={}
            if not r['contacts'] and not r['errors']:
                for body in bodies:
                    s=body.Shape.copy();b=s.BoundBox;s.translate(-A.Vector(b.XMin,b.YMin,b.ZMin))
                    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.15,AngularDeflection=.2,Relative=False)
                    assert mesh.isSolid();path=OUT/(body.Name+'.stl');assert not path.exists(),'Preserve existing export'
                    mesh.write(str(path));assert Mesh.Mesh(str(path)).isSolid();exports[path.name]=sha(path)
            r['exports']=exports;r['print_dimensions_mm']=prior['print_dimensions_mm']
        finally:
            for d in (doc,mount,ctx,tail):A.closeDocument(d.Name)
    assert all(sha(ROOT/n)==v for n,v in pins.items())
    paths=[MODEL,PROOF,Path(__file__),ROOT/'tools/cad/open_prototype_shared_distribution_carriers.py']+[OUT/n for n in r['exports']]
    r['files']=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in paths]
    r['gates']={k:dict(status='open',reason=reason) for k,reason in dict(
        geometry='3old source interfaces require coherent replacement integration',assembly='Full wired assembly/removal open',
        fit='Delivered hardware/adhesive/connector coupons phase2',petg='Support/bearing/creep/profile not physically qualified',
        loads='Prototype stiffness/creep gate remains',electrical='Wiring/insulation/protection remain open',service='Full source access remains').items()}
    r.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    output.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r[k] for k in ('status','contacts','errors','tested_pairs','exports','worker_seconds')}),flush=True)


if __name__=='__main__':main()
