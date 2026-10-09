"""Relocated reopen/export and explicit remaining-dependency gate for S1."""
from pathlib import Path
from datetime import datetime, timezone
import json, math, tempfile, time
import FreeCAD as A
import Part, Mesh, MeshPart
from open_prototype_source_retention import OUT, ROOT, BASE, MODEL, sha
from open_prototype_source_receipt import verified_family
from open_prototype_shared_distribution_carriers import validate
from open_prototype_tail_clearance import box, near


def run():
    tick=time.monotonic();proof=json.loads((OUT/'source-retention-checks.json').read_text())
    assert not proof['contacts'] and not proof['errors']
    assert sha(MODEL)==proof['model_sha256']
    assert all(sha(ROOT/n)==h for n,h in proof['source_sha256'].items())
    family=verified_family();exports=[];additional_contacts=[];pairs=0
    report=dict(selected=False,physical_pass=False,stage_completed=False,full_source_retention_complete=False)
    with tempfile.TemporaryDirectory(prefix='robot-cat-source-reopen-') as tmp:
        relocated=Path(tmp)/MODEL.name;relocated.write_bytes(MODEL.read_bytes())
        doc=A.openDocument(str(relocated))
        old=A.openDocument(str(OUT/'CommonMtaMounts.FCStd'))
        rails=A.openDocument(str(OUT/'SharedDistributionCarriers.FCStd'))
        mount=A.openDocument(str(BASE/'mounting-checkpoint/RetentionMountsAssembly.FCStd'))
        ctx=A.openDocument(str(BASE/'OpenPrototypePlan.FCStd'))
        try:
            bodies=[doc.UpperCarrier,doc.S1Bracket,doc.LeftDistributionCarrier,doc.RightDistributionCarrier];baseline=validate(doc,bodies)
            assert not any(o.TypeId=='App::Link' for o in doc.Objects),'Self-contained source module required'
            doc.RetentionParameters.PanelThickness=3.5;trial=validate(doc,bodies)
            assert trial['S1Bracket']>baseline['S1Bracket']
            doc.RetentionParameters.PanelThickness=3;restored=validate(doc,bodies)
            assert all(abs(v-restored[n])<1e-7 for n,v in baseline.items())
            # Every retained board mounting post still has its actual surrounding
            # material after the new source windows. This catches clipped posts.
            profile=old.UpperPcbPosts.Profile
            postsketch=profile[0] if isinstance(profile,tuple) else profile
            post_checks=[]
            for g in postsketch.Geometry:
                if not isinstance(g,Part.Circle):continue
                x,y=g.Center.x,g.Center.y
                region=Part.makeCylinder(g.Radius+.001,5,A.Vector(x,y,77.72))
                before=old.UpperCarrier.Shape.common(region);after=doc.UpperCarrier.Shape.common(region)
                lost=before.cut(after).Volume
                post_checks.append(dict(xy_mm=[x,y],lost_volume_mm3=lost))
                assert lost<1e-6,('PCB post changed',x,y,lost)
            # New bracket versus actual saved parts, not just generic boxes.
            targets={}
            for d in (old,mount):
                for o in d.Objects:
                    if o.TypeId not in ('PartDesign::Body','App::Link') or not hasattr(o,'Shape') or o.Shape.isNull():continue
                    if o.Name=='UpperCarrier':continue
                    targets[d.Name+'/'+o.Name]=o.Shape
            for o in ctx.Objects:
                if not o.Name.startswith(('P0_','Head_','TailBridge','S0_')) or not hasattr(o,'Shape') or o.Shape.isNull():continue
                targets[o.Name]=o.Shape
            for name,s in targets.items():
                if not near(doc.S1Bracket.Shape,s,0):continue
                assert s.isValid(),name
                v=doc.S1Bracket.Shape.common(s).Volume;pairs+=1
                if v>1e-6:additional_contacts.append(dict(a='S1Bracket',b=name,volume_mm3=v))
            # MTA bodies have since moved; their old added rear roots/posts are
            # explicitly invalidated, NOT quietly treated as retained geometry.
            base_rail_contacts=[]
            for ob in (doc.LeftDistributionCarrier,doc.RightDistributionCarrier):
                assert ob.Shape.isValid(),ob.Name
                v=doc.S1Bracket.Shape.common(ob.Shape).Volume
                if v>1e-6:base_rail_contacts.append(dict(native=ob.Name,volume_mm3=v))
            assert not base_rail_contacts,base_rail_contacts
            assert all(c['b'].startswith(old.Name+'/') and c['b'].endswith('DistributionCarrier') for c in additional_contacts),additional_contacts
            # The prior D_RL nominal casing also occupies the rear load column;
            # do not silently delete a structural boss or call this whole-assembly clear.
            dcase=next(r for r in family['stations'] if r['role']=='D_RL')
            dshape=box(dcase['centre_mm'],dcase['size_mm']);dependencies=[]
            for o in mount.Objects:
                if o.TypeId not in ('PartDesign::Body','App::Link') or not hasattr(o,'Shape') or o.Shape.isNull():continue
                if not near(dshape,o.Shape,0):continue
                assert o.Shape.isValid(),o.Name
                v=dshape.common(o.Shape).Volume
                if v>1e-6:dependencies.append(dict(case='D_RL',native=o.Name,volume_mm3=v))
            for body in bodies:
                s=body.Shape.copy()
                if body.Name=='S1Bracket':s.rotate(A.Vector(),A.Vector(1,0,0),180)
                b=s.BoundBox;s.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
                mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
                assert mesh.isSolid() and mesh.countComponents()==1,body.Name
                path=OUT/(body.Name+'SourceCurrent.stl');mesh.write(str(path))
                loaded=Mesh.Mesh(str(path));assert loaded.isSolid() and loaded.countComponents()==1
                bb=loaded.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength]
                assert max(size)<=246,'10mm total print margin inside256cubed'
                exports.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),dimensions_mm=size,
                                    closed=True,selected=False,print_ready=False))
            report.update(status='S1_LOCAL_NATIVE_AND_EXPORT_VERIFIED_ASSEMBLY_DEPENDENCIES_OPEN',
                fresh_relocated_reopen=True,parameter_test_mm=[3,3.5,3],parameter_restored=True,
                native_bodies=4,fully_constrained_sketches=sum(o.TypeId=='Sketcher::SketchObject' for o in doc.Objects),
                native_volumes_mm3=baseline,additional_saved_material_pairs=pairs,additional_contacts=additional_contacts,
                base_rail_contacts=base_rail_contacts,
                obsolete_MTA_root_replacement_required=bool(additional_contacts),
                pcb_post_preservation=post_checks,unresolved_D_RL_column_contacts=dependencies,exports=exports)
        finally:
            for d in (doc,old,rails,mount,ctx):A.closeDocument(d.Name)
    report.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    dest=OUT/'source-retention-reopen.json';dest.write_text(json.dumps(report,indent=2)+'\n')
    files=[MODEL,OUT/'SharedDistributionCarriers.FCStd',OUT/'source-retention-checks.json',OUT/'source-retention-capacity.json',dest,
           Path(__file__),ROOT/'tools/cad/open_prototype_source_retention.py']
    files.extend(ROOT/e['path'] for e in exports)
    pins=dict(proof['source_sha256']);pins.update({f.relative_to(ROOT).as_posix():sha(f) for f in files})
    package=dict(schema_version=1,readiness='prototype',status=report['status'],selected=False,physical_pass=False,
        stage_completed=False,source_retention_checkpoint_complete=False,
        gates={n:dict(status='open',reason=reason) for n,reason in {
            'geometry':'S1 current wires/cases and base rails checked; obsolete MTAroot contacts require replacement; D_RL/rear native column contact unresolved',
            'assembly':'Local S1 bench mounting only; complete wire/ATO installation/removal OPEN',
            'fit':'Delivered S821bushing,lockingring,lead,no-crush/no-slip and tool fit OPEN',
            'petg':'Profile,layer strength,creep and print support/removal OPEN',
            'loads':'Bracket acts on upper receiving plate; prototype load/retention test OPEN',
            'electrical':'All14independent wire restraints/full body wiring/U1/stock OPEN',
            'service':'Actual wired bank access and whole module service OPEN'}.items()},
        files=[dict(path=n,sha256=h) for n,h in sorted(pins.items())],exports=exports,
        new_candidate_hardware=proof['candidate_hardware'],supplier_hardware_reused=proof['supplier_hardware_reused'],
        assembly=['Fit upper plate with source passages and north anchor ear before boards',
                  'Bench fit S821backupnut/lockingring/panel/lockwasher/facenut; preserve stated panel stack',
                  'Fit2M3nuts in bracket underside; install bracket using2M3x8/2washers from below before monitor',
                  'Attach four source ring terminations with power disconnected; independent wire grips still OPEN'],
        dependency_note='Use matched paired carriers without obsolete G2/D_RR station pads/4MTA roots; whole4MTA mounting remains OPEN. Do not select the plate while D_RL occupies the rear load column. No frame boss deleted to hide that conflict.',
        next='Resolve D_RL and all source support ownership jointly; then14native wire seats, P_REAR, MTA/ATO/service and stock',
        worker_seconds=report['worker_seconds'],minimum_confirmed_results='3/20=15%,unchanged')
    (OUT/'source-retention-package.json').write_text(json.dumps(package,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__':run()
