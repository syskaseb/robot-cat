"""Native common interior/low-head candidate and actual interface checks.

Retained source parts stay unchanged. New mounts/wiring/shell are OPEN.
No old protruding mount is silently accepted by this layout study.
"""
import json
import time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, SavedShapes, sha
from plan_feline_layout import BASE, OUT, MODEL, STAGES
from check_feline_leg_body import placement


def bb(shape):
    b=shape.BoundBox
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]


def center(shape):
    solids=shape.Solids
    total=sum(s.Volume for s in solids)
    assert total>0
    return sum((s.CenterOfMass*s.Volume for s in solids),A.Vector())/total


def transform(row):
    m=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(m,f'A{i+1}{j+1}',row['rotation_rows'][i][j])
    return A.Placement(A.Vector(*row['translation_mm']),A.Rotation(m))


def main():
    tick=time.monotonic()
    plan_path=OUT/'module-layout.json';plan=json.loads(plan_path.read_text())
    motion=json.loads((OUT/'motion-layout.json').read_text())
    envelope=json.loads((OUT/'layout-checkpoint.json').read_text())
    assert envelope['native'].get('cross_section_exponent')==plan['proposed_cross_section_exponent']
    assert all(sha(ROOT/n)==h for n,h in plan['geometry_source_sha256'].items())
    reader=SavedShapes();owned=[]
    source_docs={}
    doc=A.newDocument('FelineInteriorCandidate');owned.append(doc.Name)
    path=OUT/'FelineInteriorCandidate.FCStd'
    assert path.resolve().parent==OUT.resolve()
    source_pins={**plan['geometry_source_sha256'],**{n:h for n,h in plan['source_sha256'].items() if n.endswith('.FCStd')}}
    assert all(sha(ROOT/n)==h for n,h in source_pins.items())
    # FreeCAD requires the owner path before creating external native links.
    doc.saveAs(str(path))
    report=dict(status='BUILDING_COMMON_INTERIOR',selected=False,physical_pass=False,
        scope='Actual relocated modules, retained P0/legs/tail and lower73part head. Mounts, complete wires and shell panels not yet built.',
        groups=[],contacts=[],errors=[],pairs=0,source_sha256={},
        new_mounts_complete=False,complete_wiring=False,shell_panels_complete=False)
    destination=OUT/'interior-native-checks.json'
    def save_progress():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def snapshot(name,shape,container):
        ob=doc.addObject('Part::Feature',name);container.addObject(ob);ob.Shape=shape
        return ob
    try:
        parameters=doc.addObject('Spreadsheet::Sheet','Parameters')
        drop=plan['head_drop_mm']
        parameters.set('A1','HeadDrop');parameters.set('B1',f'{drop} mm');parameters.setAlias('B1','HeadDrop')
        all_objects={};shapes={};group_shapes={};group_parts={};head_names=[]
        for row in plan['groups']:
            group=doc.addObject('App::Part','Group_'+row['role'].replace(':','_'))
            group.Label=row['role'];t=transform(row);parts=[]
            for n in row['objects']:
                replacement=plan.get('reference_substitutions',{}).get(n)
                if replacement:
                    source_path=ROOT/replacement['source']
                    if source_path not in source_docs:
                        src=A.openDocument(str(source_path));owned.append(src.Name);source_docs[source_path]=src
                    src=source_docs[source_path];original=src.getObject(replacement['object'])
                    shift=A.Placement(A.Vector(*replacement['world_shift_before_head_drop_mm']),A.Rotation())
                    ob=doc.addObject('App::Link',n);group.addObject(ob)
                    ob.setLink(original);ob.LinkTransform=True;ob.LinkPlacement=t*shift
                    s=reader.shape(source_path,replacement['object']);s.Placement=t*shift*s.Placement
                    if row['role']=='HeadMechanism':
                        ob.setExpression('LinkPlacement.Base.z','25 mm - Parameters.HeadDrop')
                    assert max(abs(a-b) for a,b in zip(bb(ob.Shape),bb(s)))<1e-5
                else:
                    s=reader.shape(MODEL,n)
                    # Identity assignment needlessly re-locates complex
                    # supplier solids and invalidates BUS25 tolerance flags.
                    # Keep unchanged source BRep exactly unchanged.
                    override=plan.get('part_pose_overrides',{}).get(n)
                    if override:s.Placement=transform(override)*s.Placement
                    if not t.isIdentity():
                        if t.Rotation.isIdentity():s.translate(t.Base)
                        else:s.Placement=t*s.Placement
                    ob=snapshot(n,s,group)
                    if row['role']=='HeadMechanism':
                        initial=ob.Placement.Base.z+plan['head_drop_mm']
                        ob.setExpression('Placement.Base.z',f'{initial:.15g} mm - Parameters.HeadDrop')
                if not s.isValid() or not s.Solids:
                    report['errors'].append(dict(object=n,error='Invalid or non-solid source/reference'))
                all_objects[n]=ob;shapes[n]=s;parts.append(s)
                if row['role']=='HeadMechanism':head_names.append(n)
            group_shapes[row['role']]=Part.makeCompound(parts)
            group_parts[row['role']]={n:shapes[n] for n in row['objects']}
            report['groups'].append(dict(role=row['role'],objects=row['objects'],region=row['region']))
            print('Native group',row['role'],len(parts),flush=True)
            save_progress()
        retained=doc.addObject('App::Part','RetainedP0TailBattery')
        retained_shapes={}
        for r in motion['inventory']:
            n=r['object'];label=r['label']
            if n in shapes or r['kind']!='surface':continue
            if not (label.startswith(('P0_','tail/')) or n.startswith(('Print_P0_','Print_CP2_TailRiser','Battery'))):continue
            s=reader.shape(MODEL,n)
            snapshot(n,s,retained);retained_shapes[n]=s
        ep=ROOT/envelope['native']['native'];src=A.openDocument(str(ep));owned.append(src.Name)
        body_link=doc.addObject('App::Link','TorsoEnvelopeReference');body_link.setLink(src.TorsoEnvelope);body_link.LinkTransform=True
        body_link.addProperty('App::PropertyString','Status');body_link.Status='Shared reservation, no printable skin yet'
        for i in range(1,5):
            n=f'BellyPadReservation{i}'
            s=reader.shape(ep,n);snapshot(n,s,retained);retained_shapes[n]=s
        doc.recompute()
        before={n:center(all_objects[n].Shape).z for n in head_names}
        parameters.set('B1',f'{drop+1} mm');doc.recompute()
        assert all(abs(center(all_objects[n].Shape).z-before[n]+1)<1e-5 for n in head_names)
        parameters.set('B1',f'{drop} mm');doc.recompute()
        assert all(abs(center(all_objects[n].Shape).z-before[n])<1e-5 for n in head_names)
        doc.saveAs(str(path))
        report.update(status='NATIVE_COMMON_CANDIDATE_SAVED_CHECKS_RUNNING',native=path.relative_to(ROOT).as_posix(),native_sha256=sha(path),
            native_head_drop_parameter_test_mm=[drop,drop+1,drop],head_reference_count=len(head_names),
            retained_reference_count=len(retained_shapes),native_supplier_parts=len(shapes))
        save_progress()
        bounds={}
        def check(a_name,a,b_name,b,pose=None):
            ka,kb=(a_name,pose),(b_name,pose)
            if ka not in bounds:bounds[ka]=a.BoundBox
            if kb not in bounds:bounds[kb]=b.BoundBox
            if not bounds[ka].intersect(bounds[kb]):return
            report['pairs']+=1
            try:
                overlap=a.common(b)
                if not overlap.isNull() and not overlap.isValid():raise ValueError('Invalid intersection result')
                if overlap.Volume>1e-5:
                    report['contacts'].append(dict(a=a_name,b=b_name,pose=pose,volume_mm3=overlap.Volume,
                        witness_bounds_mm=bb(overlap)))
            except Exception as exc:report['errors'].append(dict(a=a_name,b=b_name,pose=pose,error=str(exc)))
        for a,b in plan['potential_group_pairs_NOT_collisions']:
            for an,as_ in group_parts[a].items():
                for bn,bs in group_parts[b].items():check(an,as_,bn,bs)
            print('Exact common groups',a,b,'contacts',len(report['contacts']),'errors',len(report['errors']),flush=True)
            save_progress()
        stage_of={n:(code,stage) for code,g in motion['membership'].items() for stage,ns in g.items() for n in ns}
        axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
        for index in (0,envelope['planning_pose_index']):
            pose=motion['poses'][index];current={n:s for n,s in retained_shapes.items() if n not in stage_of}
            for code,g in motion['membership'].items():
                aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
                transforms=placement(aa,pose['legs'][code]['angles_delta_degrees'])
                for stage,names in g.items():
                    for n in names:
                        s=retained_shapes[n].copy();s.Placement=transforms[stage]*s.Placement;current[n]=s
            for role,parts in group_parts.items():
                for an,as_ in parts.items():
                    for n,s in current.items():check(an,as_,n,s,index)
                print('Group vs retained',index,role,'contacts',len(report['contacts']),'errors',len(report['errors']),flush=True)
                save_progress()
        # Only external group interfaces are tested; manufactured module
        # internal overlaps and unchanged leg self-motion are not rechecked.
        expected={n:(s.Volume,list(center(s))) for n,s in shapes.items()}
        doc_name=doc.Name
        A.closeDocument(doc_name);owned.remove(doc_name)
        reopened=A.openDocument(str(path));owned.append(reopened.Name)
        for n,(volume,point) in expected.items():
            s=reopened.getObject(n).Shape
            assert s.isValid() and abs(s.Volume-volume)<max(1e-5,volume*1e-8),n
            assert (center(s)-A.Vector(*point)).Length<1e-5,n
        report.update(status='COMMON_INTERIOR_INTERFACES_REJECTED' if report['contacts'] or report['errors'] else 'COMMON_INTERIOR_ENDPOINTS_CLEAR_MOUNTS_WIRES_SKIN_OPEN',
            fresh_native_reopen_verified=True,source_sha256={**reader.hashes,
                plan_path.relative_to(ROOT).as_posix():sha(plan_path),
                Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
            continuous_new_module_motion_checked=False,skin_containment_exact_checked=False)
        save_progress()
        print(json.dumps({k:report[k] for k in ('status','pairs','worker_seconds')}),'contacts',len(report['contacts']),'errors',len(report['errors']),flush=True)
    finally:
        for name in reversed(owned):
            if name in A.listDocuments():A.closeDocument(name)
        assert all(sha(ROOT/n)==h for n,h in source_pins.items()),'Historical source changed during build'


if __name__=='__main__':main()
