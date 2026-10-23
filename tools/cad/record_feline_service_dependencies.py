"""Record the authority of an existing S0 reservation and service cutset.

No selected geometry changes; no reservation overlap becomes a material verdict.
"""
import json
import math
from graphlib import TopologicalSorter
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_source_restraint_plan import box


def record(scene):
    f=OUT/'n01-FPI-top-service-dependencies.json'
    prior=json.loads(f.read_text()); key=scene['Ref_Material_S0_key_CP2_0_0']
    assert len(key.Solids)==1 and len(key.Faces)==3 and key.isValid()
    assert abs(key.Volume-math.pi*15**2*63.5)<1e-5
    access=box(*prior['bounds_mm'])
    axis=Part.makeLine(key.Placement.multVec(A.Vector()),
                       key.Placement.multVec(A.Vector(0,0,63.5)))
    distance=axis.distToShape(access)[0]
    common=key.common(access); assert common.isValid()
    local=common.copy();local.Placement=key.Placement.inverse()*local.Placement
    sources=[f,ROOT/'tools/cad/whole_cat_interior.py',
        ROOT/'hardware/reference/hella-s0-primary-2026-10-16/HELLA-page259.png',
        OUT/'n01-USB-BUS-first-service-negative.json',
        OUT/'n01-BUS-module-service-retreat-sample.json',
        OUT/'n01-Pi-mated-USB-lift-service-sample.json']
    result=dict(status='SERVICE_DEPENDENCIES_RECORDED_NOT_ASSEMBLY_APPROVAL',
        S0=dict(actor='Ref_Material_S0_key_CP2_0_0',
            geometric_type='FULL_FAMILY_RESERVATION_NOT_EXACT_KEY_OR_OFF_POSE',
            radius_mm=15,height_mm=63.5,
            source_definition='whole_cat_interior.py: S0 family model includes stud space, NOT exact HELLA SKU casing',
            supplier_drawing_selected_part='002843002 on HELLA page259',
            confirmed_dimensions_mm={'panel_to_front_tip':66.5,'neck_diameter':22},
            exact_neck_axial_extent_and_key_shape_unknown=True,
            extraction25_is_project_assumption_not_measured_stroke=True,
            reservation_overlap_mm3=common.Volume,
            overlap_axial_interval_from_reservation_base_mm=[local.BoundBox.ZMin,local.BoundBox.ZMax],
            axis_to_FPI_access_mm=distance,
            sufficient_uniform_radius_with_half_mm_margin=distance-.5,
            radius_bound_is_NOT_supplier_dimension=True,
            actual_collision_proved=False,
            removing_key_does_not_remove_fixed_neck=True),
        routine_FPI=dict(prerequisites=['Isolate and physically disconnect source',
            'Release and park complete W027/W020/W031/W033/W035 groups with terminals unloaded',
            'Qualify actual fixed neck and key OFF position against F_PI access',
            'Only if key removal is necessary, qualify its actual withdrawal',
            'Open delivered cap, replace fuse, restore all restraints'],
            five_groups_are_NOT_five_WAGO_disconnects=True,
            fixed_boundaries_are_NOT_connectors=True,
            W027_known_terminal='FL_P.2',
            other_body_boundaries=['W020:FL1/fixed_boundary','W031:FR1/fixed_boundary',
                                   'W033:FR2/fixed_boundary','W035:FR3/fixed_boundary'],
            sequence_approved=False),
        rare_Pi_BUS=dict(separate_from_routine_fuse_service=True,
            Pi_first='USB gap0.430475 below project0.5; no material intersection claimed',
            BUS_plug_first='Fixed pad intersects plug withdrawal70.2mm3',
            BUS_module_retreat='Current TailCarrier witness68.382751mm3 suffices; secondary tail-mount witness ownership not requalified',
            Pi_lift_mated='Constant452mm jacket and R>=30 end pose; W009 clearance fails, continuous motion unqualified',
            sequence_approved=False),
        decision='Do not redesign Pi again solely to clear an inaccurately classified S0 key. Resolve fixed neck/key OFF geometry first; retain real cable/printed-support blockers.',
        required_measurements=['Panel to fixed neck tip',
            'Key handle thickness/width and installed OFF orientation',
            'Actual axial withdrawal needed to release the key'],
        exact_manufacturer_key_geometry_received=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sources},
        selected_geometry_changed=False,N01_complete=False,physical_pass=False)
    save_json(OUT/'n01-service-dependency-decision-20261023.json',result)
    return result


def complete_sequence(rows, source_files, withdrawal):
    """Compose one conditional sequence from current terminals, not fake plugs.

    This receives an already computed changed-interface check. It does not
    rerun rejected geometry or promote an acyclic plan into assembly approval.
    """
    dest = OUT/'n01-service-dependency-decision-20261023.json'
    result = json.loads(dest.read_text())
    by_id = {r['id']: r for r in rows}
    assert len(by_id) == len(rows) == 246
    portions = ['W009/body', 'W027/single', 'W020/body', 'W031/body',
                'W033/body', 'W035/body', 'W002/retained0', 'W003/retained0',
                'W079/retained0', 'W080/retained0', 'XL01/extra', 'XL05/extra',
                'XL06/extra', 'XL07/extra', 'XL10/extra']
    terminals = {}
    for portion in portions:
        terminals[portion] = [{k: by_id[portion+'/'+side].get(k) for k in
            ('id', 'endpoint', 'group', 'support_owner', 'prefix_geometry_owner')}
            for side in ('start', 'end')]
    expected = {'W009/body': ('FR2/fixed_boundary', 'D_FR.3'),
                'W027/single': ('FL_P.2', 'F_FL1.in'),
                'W002/retained0': ('BUS.D', 'D_FL.1'),
                'W003/retained0': ('BUS.G', 'G2.4')}
    for p, ends in expected.items():
        assert tuple(r['endpoint'] for r in terminals[p]) == ends
    # Each operation begins at a named prior state of the assembled robot.
    # No "disconnect" operation may be performed at a routing seam or solder pad.
    steps = [
        ('isolate', [], 'Physically disconnect source; support robot; do not energize.',
         'conditional', 'Physical procedure, not an executed test.'),
        ('open', ['isolate'], 'Remove service panels and expose installed grips.',
         'missing', 'Final enclosure opening/fastener access is not qualified.'),
        ('release_W009', ['open'],
         'Label W009; support adjacent D_FR wires; release its restraint and D_FR.3; park the COMPLETE connected wire without cutting the FR2 seam.',
         'missing', 'D_FR.3 identity checked; lever/tool access, adjacent-wire support and full-length parking missing.'),
        ('release_Pi_signals', ['open'],
         'Support leads; release GPIO4/H1 restraints and unplug the occupied GPIO housing from Pi, preserving H1/H3/H5/H11/H6 mapping; park it with remote ends attached.',
         'missing', 'Five pins are not five independently removable housings. Full housing extraction/parking and tool access missing.'),
        ('release_Pi_power', ['open'],
         'Release Power2 restraint; unplug the SINGLE K-1474 USB-C power connector from Pi; keep W079/W080 joined to that plug and MAIN solder joints intact.',
         'missing', 'Plug axis/stroke, access and two-lead parking not yet received; no desoldering or invented MAIN connector.'),
        ('release_cradle', ['release_W009', 'release_Pi_signals', 'release_Pi_power'],
         'Support Pi; release USB-A jacket tie and the two cradle ties; remove cradle lid normal8 then up80.',
         'conditional', 'Existing lid/tool geometry received for its stated subset; parked leads must be included.'),
        ('lift_mated10', ['release_cradle'],
         'Lift Pi and its upper carrier10mm with data USB A-C still mated; BUS remains fixed.',
         'conditional', 'Saved cable end pose preserves nominal452mm/R30; W009 must be parked. Continuous deformation and moving full carrier not yet received.'),
        ('unplug_USB_A', ['lift_mated10'],
         'Hold Pi; release its USB grip arm before the reserved15mm +X withdrawal; keep BUS USB-C mated; park the freed A end.',
         'missing', 'Only first12mm clears the carrier. The remaining3mm intersects its arm; an actually releasable arm and cable parking are required. Neither12 nor15mm is a measured supplier stroke.'),
        ('remove_Pi', ['unplug_USB_A'],
         'Lift Pi/upper carrier to the previously checked40mm height, then transfer to bench with leads unloaded.',
         'conditional', 'Existing necessary lift-space proof is not a full cable/parking proof.'),
        ('release_BUS_DG', ['remove_Pi'],
         'For BUS replacement only: release D/G split clamps; unplug the complete H5 mating housing OR release remote D_FL.1/G2.4 after qualifying access. Do not pull individual contacts from a mated housing.',
         'missing', 'Choice is not geometrically selected; actual housing withdrawal/remote parking and retention access missing.'),
        ('remove_BUS', ['release_BUS_DG'],
         'Support BUS and release its real mounting stack before removal; carry the USB cable rather than pulling BUS+X12 into TailCarrier.',
         'missing', 'BUS removal path and mounting-tool access require qualification; rejected +X12 path is prohibited.'),
    ]
    operations = [dict(id=i, requires=deps, action=action, status=status, basis=basis)
                  for i, deps, action, status, basis in steps]
    order = list(TopologicalSorter({x['id']: set(x['requires']) for x in operations}).static_order())
    plan = dict(status='ONE_CONDITIONAL_SEQUENCE_NOT_EXECUTION_READY',
        operations=operations, dependency_order=order, dependency_graph_acyclic=True,
        acyclic_does_not_prove_geometric_feasibility=True,
        current_terminal_pairs=terminals,
        USB_data=dict(part='LanbergCA-USBO-10CU-0005-BK',
                      additional_to_123_portions=True, end_count=2,
                      same_bought_cable=True, detach_at='Pi USB-A after lift, not BUS USB-C in place'),
        initial_assembly_order=[
            'Prepare fixed carriers, BUS mounting and all inaccessible fastener stacks before crossing wires.',
            'Mount BUS with USB-C already mated and its jacket independently restrained; do not assume later axial access through its fixed pad.',
            'Keep W009 and Pi GPIO/power disconnected/unrestrained locally; complete Pi and upper carrier on bench.',
            'Present supported Pi with USB grip arm released, mate USB-A, restore arm and lower Pi while preserving full cable length and bend radius; releasable arm is not yet implemented.',
            'Seat/retain cradle, then mate Pi power/GPIO and restore their individual jacket restraints.',
            'Install W009 at D_FR.3 and restore both its restraints last; verify every wire identity and retained neighbour.',
            'Close panels only after shared tool access and reversible cable parking are qualified.'],
        assembly_order_is_conditional_not_received=True,
        routine_FPI=dict(independent_of_rare_Pi_sequence=True,
            groups=['W027/single','W020/body','W031/body','W033/body','W035/body'],
            must_move_complete_grips_not_just_wires=True,
            only_explicit_WAGO_in_these_groups='FL_P.2 on W027',
            bank_ends_are_not_assumed_detachable=True,
            leg_fixed_boundaries_are_not_connectors=True,
            missing=['Actual S0 fixed neck/OFF key/withdrawal geometry',
                     'Reversible parking of all five groups including their bank grip bodies',
                     'Actual F_PI cap/tool manipulation'],
            remove_Pi_not_automatically_required=True, approved=False),
        W009_connected_parking_alternative=dict(
            status='NOT_SELECTED_WITHOUT_FULL_PATH',
            existing_body_length_mm=636.4129719628785,
            length_is_NOT_available_service_slack=True,
            reason='Length belongs to a routed path around real obstacles, not a free coil. Both endpoint tangents, R>=12.4 and the entire path must remain valid.',
            benefit_if_qualified='Would eliminate the D_FR.3 disconnect prerequisite, without a new connector.',
            no_new_offset_family_started=True),
        D_FR_release_constraints=dict(
            other_occupied_wires=['W007','W008','W010','W011'],
            common_comb_actor='Station:D_FR:split_common_comb',
            current_comb_is_one_solid_reservation_for_split_construction=True,
            removing_tie_alone_does_not_prove_radial_wire_release=True,
            case_only_model_does_not_prove_lever_clearance=True,
            manufacturer_strip_mm=11,
            strip_length_is_NOT_complete_service_stroke=True,
            supplier_lever_pivot_length_and_open_sweep_not_dimensioned=True,
            independent_neighbour_support_required=True),
        checked=['Current terminal identities for15 affected portions from hash-checked246-end provider',
                 'Cradle and stationary/upper support evidence retained within original scope',
                 'USB-A lifted rigid withdrawal substep in stated partial scene'],
        missing_not_hidden=['W009 full connected parking and D_FR lever access',
                           'Pi GPIO and single power-plug withdrawal/parking',
                           'Release of USB grip arm for reserved15mm stroke, then continuous USB flex during lift and unplug',
                           'BUS hardware access and complete extraction',
                           'Final panel access and missing scene actors'],
        next='Qualify D_FR.3 lever/comb release and whole W009 parking before any new USB shape. S0 only gates routine F_PI branch.',
        no_new_connectors_or_selected_parts=True,
        selected_geometry_changed=False, assembly_approved=False,
        N01_complete=False, physical_pass=False)
    assert all(x['status'] in {'checked','conditional','missing'} for x in operations)
    result['shared_sequence'] = plan
    result['lifted_USB_A_withdrawal'] = withdrawal
    resolved = [Path(p) if Path(p).is_file() else OUT/Path(p).name for p in source_files]
    result['sequence_source_sha256'] = {
        str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in
        [*resolved, Path(__file__),
         OUT/'n01-Pi-open-cradle-joint.json', OUT/'n01-Pi-split-service-space.json',
         OUT/'n01-USB-release-grip-topology-repaired.json', OUT/'n01-physical-cable-contract.json',
         OUT/'W009-W069-harness-corridor/recovered-context.json',
         OUT/'n01-shared-Pi-carrier-r3-core-received.json',
         OUT/'n01-current-W009-complete-body-plan.json',
         OUT/'n01-current-W069-complete-body-plan.json',
         ROOT/'hardware/reference/wago-221415-access-2026-10-02/source.json',
         ROOT/'hardware/reference/wago-221415-access-2026-10-02/page6.png']}
    save_json(dest, result)
    return plan


def receive_comb_opening(lift, slide):
    """Receive the changed two-piece planning geometry, not production CAD."""
    assert not lift['failures'] and not lift['errors']
    assert not slide['failures'] and not slide['errors']
    dest = OUT/'n01-service-dependency-decision-20261023.json'
    result = json.loads(dest.read_text())
    result['D_FR_comb_opening'] = dict(
        status='CONSTRUCTIVE_SPLIT_CAP_SUBSTEP_IN_PARTIAL_SCENE',
        source_actor='Station:D_FR:split_common_comb', split_world_Z_mm=45.26,
        upper_piece='Existing comb intersect X[2.575,28.675], Y[-44.25,-35.25], Z[45.26,55.26]',
        motion_mm=[[0,0,1.8],[0,9,0]],
        continuous_lift_proof='Upper half has open semicircular grooves and constant top48.81. Exact swept union is upper half plus its full top slab Z48.81..50.61.',
        continuous_slide_proof='After lift, extrude the full planar +Y end face9mm and fuse with the lifted half; geometry is invariant along Y.',
        lift=lift, slide=slide, own_wire_nominal_fit_mm=.15,
        external_clearance_required_mm=.5,
        requires=['Hold/support all five wires before cutting common tie',
                  'Keep lower saddle fixed; do not unload neighbouring terminals',
                  'Provide access for holding/removing cap and cutting/replacing tie'],
        tie_cutting_tool_and_hand_access_qualified=False,
        final_cap_parking_and_W009_extraction_qualified=False,
        current_selected_comb_still_one_piece=True,
        future_native_split_required=True, native_or_selected_geometry_changed=False,
        full_D_FR_service_approved=False, N01_complete=False, physical_pass=False)
    result['sequence_source_sha256'][str(Path(__file__).relative_to(ROOT)).replace('\\','/')] = sha(Path(__file__))
    save_json(dest,result)
    return result['D_FR_comb_opening']


def removable_usb_sleeve(kits):
    """N01 separable restraint on the existing beam, not a new Pi position.

    Keep constituents independent: a fused child's distance may disagree with
    both its source constituents and its empty Boolean intersection. Such a
    fused artifact is NOT automatically a qualified export.
    """
    from receive_feline_pi_split_service_space import independent
    y = 28.85810963471377
    sleeve = Part.makeBox(12,8,4.5,A.Vector(108.5,y-4,107.1)).cut(
        Part.makeCylinder(1.7,12,A.Vector(108.4,y,107.1),A.Vector(1,0,0)))
    parts = {k:independent(kits[k]) for k in ('arm','pad')}
    # The old spherical nose hooks the arm during upward release. A flat
    # beam end and explicit .2mm axial assembly gap remove that interlock.
    # Both are subsets; unchanged external clearance evidence is reusable.
    parts['arm']=parts['arm'].common(Part.makeBox(100,200,200,A.Vector(118.7,-80,0)))
    parts['sleeve'] = sleeve
    assert all(s.isValid() and len(s.Solids)==1 for s in parts.values())
    return parts


def usb_flat_beam(kits):
    from receive_feline_pi_split_service_space import independent
    result=independent(kits['retained']).cut(
        Part.makeBox(100,200,200,A.Vector(118.5,-80,0)))
    assert result.isValid() and len(result.Solids)==1
    return result


def sampled_translation_bound(scene, metadata, parts, excluded, delta,
                              intervals=3, minimum=.5):
    """Continuous clearance bound, not endpoints masquerading as a sweep.

    Distance to fixed material is 1-Lipschitz under translation. Every point
    of the path is within half a sample interval of a sample. Subtract this
    displacement from each sampled gap; reject errors or insufficient bounds.
    Union clearance is the minimum of constituent clearances, without Boolean
    fusion of the curved pad. Intended mating contacts need separate proof.
    """
    import time
    from check_feline_service_translation import check
    from receive_feline_pi_split_service_space import independent
    tick=time.monotonic(); vector=A.Vector(*delta)
    penalty=vector.Length/(2*intervals)
    samples=[]
    for i in range(intervals+1):
        moved={k:independent(v) for k,v in parts.items()}
        for shape in moved.values():shape.translate(vector*(i/intervals))
        receipt=check(scene,metadata,moved,excluded,None,None,minimum+penalty)
        for row in receipt['checks'].values():
            row['continuous_gap_lower_bound_mm']=row['gap_mm']-penalty
        samples.append(dict(fraction=i/intervals,**receipt))
    return dict(delta_mm=delta,intervals=intervals,
        nearest_sample_displacement_mm=penalty,minimum_mm=minimum,
        method='1-Lipschitz distance lower bound for translating constituent union',
        samples=samples,
        passed=all(not s['failures'] and not s['errors'] for s in samples),
        intended_contacts_not_covered=True,partial_scene_only=True,
        worker_seconds=round(time.monotonic()-tick,3),N01_complete=False)


def usb_sleeve_tie_reservations():
    """Two replaceable 2.5x1.2 ties; shape budgets, not rated retention.

    A conformal band crosses under the existing beam and over the sleeve.
    Reserve its FULL outer box: a hollow rectangular ring would omit the
    diagonal nylon runs under the narrower round beam. This is occupied-space
    reservation, not actual nylon material; own beam/sleeve overlap is intended.
    No terminal or lever carries its load. Hand/jaw access is separate.
    """
    y=28.85810963471377; result={}
    for index,x in enumerate((110.,115.)):
        # The top of the actual sleeve is111.6: retain its full roof inside
        # the band rather than intersecting it with a falsely tight loop.
        outer=Part.makeBox(2.5,10.4,8.4,A.Vector(x,y-5.2,104.4))
        result[f'root_tie{index}:band_budget']=outer
        result[f'root_tie{index}:head']=Part.makeBox(5.,5.3,4.3,
            A.Vector(x-1.25,y-2.65,112.8))
    return result


def receive_usb_removal(parts, fixed, ties, evidence):
    """Save one constructive service witness without selecting production CAD."""
    import hashlib,zipfile
    from receive_feline_pi_split_service_space import independent
    dest=OUT/'n01-service-dependency-decision-20261023.json'
    result=json.loads(dest.read_text())
    archive=OUT/'n01-service-removable-usb-20261023.brep.zip'
    geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for index,(name,shape) in enumerate({**parts,'fixed_beam':fixed,**ties}.items()):
            shape=independent(shape);shape.check(True)
            raw=shape.exportBrepToString().encode();entry=f'{index:02}.brep'
            z.writestr(entry,raw)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result['removable_USB_planning_witness']=dict(
        status='CONSTRUCTIVE_SUBSTEPS_NOT_WHOLE_SERVICE_APPROVAL',
        geometry=geometry,bundle=str(archive.relative_to(ROOT)).replace('\\','/'),
        bundle_sha256=sha(archive),evidence=evidence,
        beam_end_X_mm=118.5,arm_begin_X_mm=118.7,assembly_gap_mm=.2,
        sleeve_mm=[12,8,4.5],groove_radius_mm=1.7,
        additional_root_ties=2,existing_USB_jacket_tie_retained=True,
        head_budget_mm=[5,5.3,4.3],
        restraint_load_path='USB jacket -> existing pad/arm -> removable sleeve and two ties -> existing upper beam -> Pi carrier/root',
        axial_retention_relies_on_clamped_fit_not_tested_load_rating=True,
        fused_artifact_not_qualified=True,
        changed_parts_are_printed_only=True,selected_bought_parts_changed=False,
        source_subset_external_evidence_reused=True,
        assembly_sequence=['Disconnect source and open service access.',
            'Qualify and park W009 first; its full parking is still OPEN.',
            'Support cable and cap by hand; cut jacket tie and two sleeve ties.',
            'Lift the open sleeve/arm/pad off the flat-ended beam; keep cable supported.',
            'Park removed cap; then perform the separately conditional Pi lift and USB withdrawal.',
            'Reverse on assembly, replacing all cut ties; verify unloaded connectors.'],
        not_covered=['Full W009 parking and neighbouring-wire support',
            'Continuous mated USB flex and unplugged-end parking',
            'Final enclosure opening and human hand access',
            'Physical tie tension/retention, print fit and strength',
            'Production native split and reliable fused export'],
        whole_service_approved=False,selected_native_changed=False,
        N01_complete=False,physical_pass=False)
    operations=result['shared_sequence']['operations']
    if not any(op['id']=='release_USB_restraint' for op in operations):
        operations.insert(5,dict(id='release_USB_restraint',requires=['release_W009'],
            action='Support USB; cut jacket tie and two root ties; lift removable sleeve/arm/pad30mm before lifting Pi.',
            status='conditional',basis='Constructive partial-scene space proof; W009 parking, hands, fit and native artifact remain OPEN.'))
    cradle_step=next(op for op in operations if op['id']=='release_cradle')
    if 'release_USB_restraint' not in cradle_step['requires']:
        cradle_step['requires'].append('release_USB_restraint')
    step=next(op for op in operations if op['id']=='unplug_USB_A')
    step['basis']='Fixed-arm15mm rejection preserved. New removable restraint has conditional space evidence; continuous cable deformation and parking remain OPEN.'
    result['shared_sequence']['dependency_order']=list(TopologicalSorter(
        {op['id']:set(op['requires']) for op in operations}).static_order())
    result['sequence_source_sha256'][str(Path(__file__).relative_to(ROOT)).replace('\\','/')]=sha(Path(__file__))
    save_json(dest,result)
    return result['removable_USB_planning_witness']
