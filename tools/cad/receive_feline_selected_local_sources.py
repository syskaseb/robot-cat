"""Receive whole selected local head/tail sources before further allocation.

Validate accounting boundaries against saved selected geometry, not a guessed
connector face. W3 yaw boundaries already include CP2SHIFT; W2 saved local
curves also include it. Apply only the current head placement to both.
"""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, SavedShapes, prop, sha
from plan_feline_layout import OUT, BASE


def ends(shape):
    vertices = {}
    for edge in shape.Edges:
        for v in edge.Vertexes:
            key = tuple(round(x, 6) for x in v.Point)
            vertices.setdefault(key, [v.Point, 0])[1] += 1
    return [p for p, degree in vertices.values() if degree == 1]


def main():
    tick = time.monotonic()
    dest = OUT/'n01-selected-local-head-tail-sources.json'
    bundle = dest.with_suffix('.zip')
    assert not dest.exists() and not bundle.exists(), 'Receive saved result first'
    files = dict(head=BASE/'head-wiring-checkpoint/selection.json',
        yaw_boundary=BASE/'head-supply-checkpoint/boundary-checks.json',
        tail=BASE/'tail-wiring-checkpoint/selection.json',
        tail_release=BASE/'tail-wiring-checkpoint/release-checks.json',
        yaw_factory=ROOT/'hardware/cad/studies/head-fixed-yaw-feed-r3/plan.json',
        modules=OUT/'n01-module-plan-r5.json',
        extra=OUT/'n01-all-extra-interface-contract.json')
    data = {k:json.loads(p.read_text()) for k,p in files.items()}
    reader = SavedShapes(); rows = []; boundaries = []; shapes = {}
    head = ROOT/data['head']['native']; tail = BASE/'tail-wiring-checkpoint'/data['tail']['current_native']
    assert sha(head) == data['head']['model_sha256']
    assert sha(tail) == data['tail_release']['model_sha256']
    group = next(g for g in data['modules']['groups'] if g['role'] == 'HeadMechanism')
    matrix = A.Matrix()
    for i in range(3):
        for j in range(3):setattr(matrix,f'A{i+1}{j+1}',group['rotation_rows'][i][j])
    transform = A.Placement(A.Vector(*group['translation_mm']), A.Rotation(matrix))
    def put(name, shape, source, obj, role, kind, radius=None, original_frame=None):
        assert shape.isValid() and (shape.Edges or shape.Solids), name
        b = shape.BoundBox; raw = shape.exportBrepToString().encode('utf-8')
        shapes[name] = raw
        rows.append(dict(name=name, role=role, kind=kind, entry=f'{len(rows):04}.brep',
            sha256=hashlib.sha256(raw).hexdigest(), source=source.relative_to(ROOT).as_posix(),
            source_object=obj, placed_current=True, bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],
            nominal_profile_radius_mm=radius, source_frame=original_frame,
            curve_length_mm=shape.Length if not shape.Solids else None,
            current_curve_ends_mm=[list(v) for v in ends(shape)] if not shape.Solids else None,
            supplier_datum_guaranteed=False, current_shared_clearance_accepted=False))
    # Source W3 boundary proof is in the same CP2 world frame as saved W2
    # local curves. The old draft contract incorrectly added CP2SHIFT again.
    old_ends={e['endpoint']:e for r in data['extra']['sections'] for e in r['ends']}
    for wire, ref in (('XB12','C_HY.V+'),('XB13','C_HY.GND'),('XS13','C_HY.PWM')):
        source = next(r for r in data['yaw_boundary']['boundaries'] if r['wire'] == wire)
        name = 'W2_'+source['receiving'].replace('/','_')
        curve = reader.shape(head,name); q = A.Vector(*source['end_mm'])
        ee = ends(curve); gap = min((q-e).Length for e in ee)
        assert gap < 1e-5, (wire, gap, 'Selected W3/W2 frame mismatch')
        current = transform.multVec(q); old = A.Vector(*old_ends[ref]['point_mm'])
        boundaries.append(dict(wire=wire, endpoint=ref, source_CP2_point_mm=list(q),
            current_point_mm=list(current), selected_local_object=name, native_gap_mm=gap,
            previous_unselected_contract_point_mm=list(old), correction_delta_mm=list(current-old),
            CP2SHIFT_already_in_both_selected_sources=True,
            extra_splice_or_connector_added=False, accounting_boundary_not_connector_pin=True))
        for i in range(3):
            n=f'W2_local_{wire}_{i}'; s=reader.shape(head,n);s.Placement=transform*s.Placement
            radius=1.7 if i==2 else 1.05
            put('SelectedYaw:'+n,s,head,n,'HeadElectricalYaw','curve_profile_reservation',radius,
                'Saved CP2 world shape -> current R5 head transform only')
    yawdir = files['yaw_factory'].parent
    for path in sorted(yawdir.glob('factory_*.brep')):
        s=Part.read(str(path));s.translate(A.Vector(-42,0,25));s.Placement=transform*s.Placement
        reader.hashes[path.relative_to(ROOT).as_posix()]=sha(path)
        put('SelectedYawFactory:'+path.stem,s,path,path.stem,'HeadElectricalYaw','provisional_factory_envelope',
            original_frame='Historical original head -> CP2SHIFT once -> current R5')
    b=data['yaw_factory']['JR_bbox_mm'];s=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    s.translate(A.Vector(-42,0,25));s.Placement=transform*s.Placement
    put('SelectedYawJRPairReservation',s,files['yaw_factory'],'JR_bbox_mm','HeadElectricalYaw',
        'project_mating_reservation', original_frame='Historical original head -> CP2SHIFT once -> current R5')
    # Read the final selected tail geometry, not its earlier coil candidate.
    # Both case faces, all local JR/HELU/insulation and complete250 factory
    # curve remain in current tail world frame, without an extra translation.
    for name, obj in reader.doc(tail).items():
        if not name.startswith('W4Reference_') or prop(obj,'Shape') is None:continue
        s=reader.shape(tail,name)
        if s.Solids:
            kind='project_mating_reservation' if 'JR_paired' in name else 'retained_insulation'
            radius=None
        else:
            kind='curve_profile_reservation';p=prop(obj,'ProfileRadius')
            if p is None:
                assert name in ('W4Reference_JR_XB32','W4Reference_JR_XB33','W4Reference_JR_XS33'),name
                radius=1.05 # final selected builder's three explicit8mm JR approaches
            else:radius=float(p[0].get('value'))
        put('SelectedTail:'+name,s,tail,name,'TailElectricalFixed',kind,radius,
            'Final selected W4 world source, already local translation12,-3,35')
    for wire in ('XB32','XB33','XS33'):
        r=data['tail_release']['local_lengths']['local/'+wire+'/2_CENTERLINE']
        expected=data['tail']['routes'][wire]['parts'][-1]['end']
        assert (A.Vector(*r['end_mm'])-A.Vector(*expected)).Length<1e-5
        boundaries.append(dict(wire=wire, endpoint={'XB32':'C_TY.V+','XB33':'C_TY.GND','XS33':'C_TY.PWM'}[wire],
            current_point_mm=expected, native_gap_mm=0, accounting_boundary_not_connector_pin=True,
            extra_splice_or_connector_added=False, full_JR_approach_included_mm=8))
    fac=next(r for r in rows if 'factory_flat_circumscribed' in r['name'])
    assert abs(fac['curve_length_mm']-247)<1e-4,fac['curve_length_mm']
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as archive:
        for r in rows:archive.writestr(r['entry'],shapes[r['name']])
    # The superseded draft is recorded separately, not a live dependency of
    # the corrected source packet that will supersede it in turn.
    pins={**reader.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),Path(__file__)) if p != files['extra']}}
    report=dict(status='SELECTED_LOCAL_SOURCES_RECEIVED_YAW_DRAFT_DOUBLE_SHIFT_CORRECTED',
        selected=False,N01_complete=False,physical_pass=False,parts=rows,boundaries=boundaries,
        bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),source_sha256=pins,
        wrong_prior_contract_not_geometry_accepted=True,previous_extra_contract_sha256=sha(files['extra']),
        yaw_accounting_boundary_does_not_require_a_new_mould_face=True,
        tail_factory_total_uncut_mm=250, tail_factory_curve_length_mm=247,
        yaw_factory_modeled_mm=220,yaw_factory_delivery_fit_budget_mm=30,
        full_layout_clearance_or_all_wiring_complete=False,
        worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],parts=len(rows),boundaries=len(boundaries),
        yaw_points=[b['current_point_mm'] for b in boundaries[:3]],seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()
