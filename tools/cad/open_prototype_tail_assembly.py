"""Current selected tail parts, retained internal kit and CP2 motion samples."""
from datetime import datetime, timezone
from pathlib import Path
import json,time
import FreeCAD as A
import Part
from check_main_p0_placement import SavedShapes, sha
from open_prototype_tail_mount import ROOT, BASE, OUT
from open_prototype_side_source_routes import load_scene
from open_prototype_tail_clearance import near

MODEL=OUT/'TailAssemblyCurrent.FCStd'

def solid_centre(shape):
    solids=shape.Solids
    assert solids and sum(s.Volume for s in solids)>0
    total=sum(s.Volume for s in solids)
    centre=A.Vector()
    for s in solids:centre+=s.CenterOfMass*(s.Volume/total)
    return centre


def make_rotor(doc):
    rotor=doc.addObject('App::Part','TailRotor')
    rotor.Placement=A.Placement(A.Vector(),A.Rotation(A.Vector(0,0,1),0))
    rotor.setExpression('Placement.Rotation.Angle','TailParameters.TailYaw')
    rotor.setExpression('Placement.Base.x','171 mm * (1 - cos(TailParameters.TailYaw)) - 6 mm * sin(TailParameters.TailYaw)')
    rotor.setExpression('Placement.Base.y','-6 mm * (1 - cos(TailParameters.TailYaw)) - 171 mm * sin(TailParameters.TailYaw)')
    return rotor


def run():
    assert not MODEL.exists(),'Do not overwrite a current assembly'
    tick=time.monotonic();docs=[];doc=None
    r=dict(status='PENDING',mechanical_M3_complete=False,physical_pass=False,wiring_complete=False,
           selected=False,contacts=[],errors=[],tested_pairs=0,motion_samples=[])
    def progress(s):print(json.dumps(dict(phase=s,seconds=round(time.monotonic()-tick,2))),flush=True)
    def test(n,s,m,t,angle=None):
        if not near(s,t,0):return
        assert s.isValid() and t.isValid(),(n,m,'Invalid BRep')
        r['tested_pairs']+=1;c=s.common(t);assert c.isValid()
        if c.Volume>1e-5:r['contacts'].append(dict(a=n,b=m,angle_deg=angle,volume_mm3=c.Volume))
    try:
        # Cheap expression smoke test BEFORE opening the costly context.
        smoke=A.newDocument('TailYawSmoke')
        v=smoke.addObject('App::VarSet','TailParameters');v.addProperty('App::PropertyAngle','TailYaw')
        rotor=make_rotor(smoke)
        for a in (-30,0,30):
            v.TailYaw=a;smoke.recompute()
            assert rotor.Placement.Rotation.isSame(A.Rotation(A.Vector(0,0,1),a),1e-7)
            assert (rotor.Placement.multVec(A.Vector(171,-6,0))-A.Vector(171,-6,0)).Length<1e-6
        A.closeDocument(smoke.Name)
        p=json.loads((BASE/'wiring-checkpoint/source-group-allocation.json').read_text())['family']
        progress('load current mount and retained CP2 context')
        docs,fixed,rings,torso,paths=load_scene(p)
        mountpath=OUT/'TailMechanicalCurrent.FCStd';doc=A.openDocument(str(mountpath))
        oldentry=ROOT/'hardware/cad/assembly/RobotCatTailCartridge.FCStd'
        hornpath=ROOT/'hardware/cad/studies/tail-printed-horn-r2/TailR5PrintedHornR2_CANDIDATE.FCStd'
        src=A.openDocument(str(hornpath));docs.append(src)
        native_group=doc.copyObject(src.TailPrintedCartridge,True);doc.recompute()
        reader=SavedShapes();xml=reader.doc(oldentry)
        kitpath=ROOT/'hardware/manufacturing/tail-fixed-build-r1/interfaces.json'
        kit=json.loads(kitpath.read_text())['tail_internal']
        hardware=[n for g in kit['groups'] for n in g['identities']]
        assert len(hardware)==len(set(hardware))==44
        baseline=json.loads((ROOT/'hardware/cad/validation/tail-cartridge-integration/geometry.json').read_text())
        rotating=set(baseline['co_rotated_parts']);rotating.remove('MG92BOutput29');rotating.add('PrintedHornR2')
        shapes={};objects={};replacements={'TailRoot29':'SupportedRoot34','TailLowerRetainer':'LowerRetainerPETG'}
        replacements.update({f'TailCartridge{kind}{i}':f'Cartridge{kind}{i}' for kind in ('Bolt','Nut') for i in range(4)})
        copied={o.Name:o for o in native_group.Group}
        # Native group copy owns its editable children; all eleven instances
        # receive the SAME current15mm transform, including the printed horn.
        for name,target in list(replacements.items())+[('PrintedHornR2','PrintedHornR2')]:
            ob=copied[target];z=ob.LinkPlacement.Base.z
            ob.getLinkedObject().Visibility=False;ob.Visibility=True
            ob.setExpression('Placement.Base.z',f'{z} mm + TailParameters.TailRise')
            objects[name]=ob
        doc.recompute()
        for name,ob in objects.items():shapes[name]=ob.Shape.copy()
        names=set(hardware)|{'UpperHousing34','BearingCap34','OuterSpacer34','InnerSpacer34','SpindleCap34','MG92BCase29'}
        names |= {f'TailModule29_{i:02}' for i in range(6)}
        for name in sorted(names-set(replacements)):
            s=reader.shape(oldentry,name)
            if 'Rigid_'+name in xml:s.Placement=reader.placement(xml['Rigid_'+name])*s.Placement
            # Explicit immutable geometry receipt, backed by the retained
            # editable source document, not a fabricated native redesign.
            ob=doc.addObject('Part::Feature','Current_'+name);ob.Shape=s
            ob.addProperty('App::PropertyString','RetainedSource')
            ob.RetainedSource=oldentry.relative_to(ROOT).as_posix()+'#'+name
            z=ob.Placement.Base.z;ob.setExpression('Placement.Base.z',f'{z} mm + TailParameters.TailRise')
            objects[name]=ob
        doc.recompute()
        for name,ob in objects.items():shapes[name]=ob.Shape.copy()
        shapes['MG92BMount29']=doc.RaisedTailSupport.Shape.copy()
        shapes['TailBridge29']=doc.RaisedTailBridge.Shape.copy()
        assert len(shapes)==61,('Tail physical identity count',len(shapes))
        doc.TailParameters.addProperty('App::PropertyAngle','TailYaw');doc.TailParameters.TailYaw=0
        rotor=make_rotor(doc)
        for n,o in objects.items():
            if n in rotating:rotor.addObject(o)
        doc.recompute()
        aliases={'P0_'+n for n in shapes}|{'CurrentTailSupport','TailBridge'}
        fixed=[q for q in fixed if q[0] not in aliases|{'P0_MG92BOutput29','LowerCarrier','Monitor_CP2'}]
        fixed += [(o.Name,o.Shape,'current tail external material') for o in doc.Objects
                  if o.Name=='LowerCarrier' or o.Name.startswith(('TailRiser1','TailRiser2','TailRiser3','TailRiser4','RearShared','MonitorTie','MonitorCase'))]
        # Newly selected R5 root/horn/retainer and new local support vs retained
        # tail material. Other unchanged relative R4 pairs reuse the pinned
        # whole-tail baseline, not another full historical audit.
        changed=set(replacements)|{'PrintedHornR2','MG92BMount29'}
        for n in changed:
            for m,t in shapes.items():
                if m==n or (m in changed and m<n):continue
                test(n,shapes[n],m,t,0)
        progress('current R5 cartridge and61 physical tail identities reconciled')
        moving={n:s for n,s in shapes.items() if n in rotating}
        stationary={n:s for n,s in shapes.items() if n not in rotating}
        for angle in range(-30,31,5):
            doc.TailParameters.TailYaw=angle;doc.recompute()
            assert rotor.Placement.Rotation.isSame(A.Rotation(A.Vector(0,0,1),angle),1e-7)
            pivot=rotor.Placement.multVec(A.Vector(171,-6,0))
            assert (pivot-A.Vector(171,-6,0)).Length<1e-6
            start=len(r['contacts'])
            for n,source in moving.items():
                s=objects[n].Shape.copy();s.Placement=rotor.Placement*s.Placement
                expected=source.copy();expected.rotate(A.Vector(171,-6,0),A.Vector(0,0,1),angle)
                assert (solid_centre(s)-solid_centre(expected)).Length<1e-5,(n,'Native motion differs')
                for m,t,_ in fixed:test(n,s,m,t,angle)
                # R5 changes and the new local support invalidate only these
                # relative pairs; all other co-rotated relative fits unchanged.
                for m,t in stationary.items():
                    if n in changed or m in changed:test(n,s,m,t,angle)
            r['motion_samples'].append(dict(angle_deg=angle,new_contacts=len(r['contacts'])-start))
            progress('tail sample '+str(angle))
        doc.TailParameters.TailYaw=0;doc.recompute()
        # Installed61 includes44 internal hardware, one servo,16PETG; risers
        # and shared P0 bolts are separate, never double-counted tail-frame kits.
        r['tail_identities']=sorted(shapes);r['internal_hardware']=kit
        r['moving_identities']=sorted(moving)
        r['range_deg']=[-30,30];r['step_deg']=5
        r['motion_scope']='13 discrete nominal samples, not continuous/loaded physical sweep; passive segment posture retained'
        r['legacy_unchanged_pair_evidence']='hardware/cad/validation/tail-cartridge-integration/geometry.json'
        # Coupled transform trial across all tail instances and new risers.
        initial={n:(o.Shape.BoundBox.ZMin,o.Shape.Volume) for n,o in objects.items()}
        doc.TailParameters.TailRise=16;doc.recompute()
        assert all(abs(o.Shape.BoundBox.ZMin-initial[n][0]-1)<1e-5 for n,o in objects.items())
        doc.TailParameters.TailRise=15;doc.recompute()
        assert all(abs(o.Shape.BoundBox.ZMin-initial[n][0])<1e-5 and abs(o.Shape.Volume-initial[n][1])<1e-5 for n,o in objects.items())
        r['whole_tail_parameter_restore']=True
        if r['contacts']:
            r['status']='REJECTED_CURRENT_TAIL_CHANGED_INTERFACES';return
        names_to_reopen=[o.Name for o in objects.values()]
        doc.saveAs(str(MODEL));r['model_sha256']=sha(MODEL)
        A.closeDocument(doc.Name);doc=None
        import tempfile,shutil
        with tempfile.TemporaryDirectory(prefix='robot-cat-tail-relocated-') as td:
            relocated=Path(td)/MODEL.name;shutil.copy2(MODEL,relocated)
            reopen=A.openDocument(str(relocated));reopen.recompute()
            assert reopen.RaisedTailBridge.Shape.isValid()
            assert all(reopen.getObject(n).Shape.isValid() for n in names_to_reopen)
            for ob in reopen.Objects:
                if ob.TypeId=='App::Link':assert ob.getLinkedObject().Document==reopen,'External dependency remained'
            reopen.TailParameters.TailYaw=30;reopen.recompute()
            pivot=reopen.TailRotor.Placement.multVec(A.Vector(171,-6,0))
            assert (pivot-A.Vector(171,-6,0)).Length<1e-6
            reopen.TailParameters.TailYaw=0;reopen.recompute()
            A.closeDocument(reopen.Name)
        r.update(status='CURRENT_TAIL_MECHANICS_NOMINAL_GEOMETRY_PREPARED',reopen_verified=True,
                 relocated_reopen_verified=True,native_yaw_parameter_checked=True,
                 mechanical_M3_complete=False,selection_stock_and_assembly_manifest_open=True)
    except Exception as exc:
        r['errors'].append(str(exc));r['status']='ERROR_NO_ACCEPTANCE';raise
    finally:
        if doc and doc.Name in A.listDocuments():A.closeDocument(doc.Name)
        for d in docs:
            if d.Name in A.listDocuments():A.closeDocument(d.Name)
        if 'reader' in locals():r['source_sha256']=reader.hashes
        if 'paths' in locals():r.setdefault('source_sha256',{}).update({f.relative_to(ROOT).as_posix():sha(f) for f in paths+[mountpath,hornpath,kitpath,Path(__file__),ROOT/'hardware/cad/validation/tail-cartridge-integration/geometry.json'] if f.exists()})
        r.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        (OUT/'tail-assembly-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:r.get(k) for k in ('status','contacts','errors','tested_pairs','worker_seconds')}),flush=True)


if __name__=='__main__':run()
