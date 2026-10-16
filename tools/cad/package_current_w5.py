"""Select nominal W5 only after identity, native, stock and assembly gates.

No score mutation, no printing/electrical approval. Historical scope receipts
are retained; two exact historical macro hashes have an explicit ancestry proof.
"""
import hashlib,json,subprocess,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA
from current_rest_pose import is_rest,is_physical_reference
from compose_current_body_restraint_coverage import unchanged_routes
from release_check import verify


def validate_counts(coverage,materials,assembly):
    fixed=coverage['fixed_physical_guide_ends'];body=coverage['body_fixed_boundary_ends']
    assert len(fixed)==106 and len(body)==72
    assert len({r['id'] for r in fixed+body})==178
    assert len({r['wire'] for r in fixed+body})==80
    assert all(r['restraint'].get('owner') and r['restraint'].get('native_proof') for r in fixed+body)
    assert materials['conductor_portions']==101 and materials['physical_cut_ends']==202
    assert len(materials['portions'])==101 and all(r['actual_cut_mm'] is None for r in materials['portions'])
    assert {r['wire'] for r in materials['portions']}=={r['wire'] for r in fixed+body}
    assert materials['historical_920mm_extra_wire_count']==0
    assert materials['selected_for_nominal_W5'] and not materials['purchase_authorized']
    assert assembly['relocated_reopen'] and assembly['all_linked_native_sources_within_relocated_package'] and not assembly['errors']
    assert len(assembly['printed_body_support_links'])==14
    assert all(is_rest(r['name']) and is_physical_reference(r['name']) for r in assembly['reference_objects'])


def run():
    tick=time.monotonic();loaded={};files={};cache={};ancestry=[]
    def read(name):
        f=OUT/(name+'.json');p=json.loads(f.read_text());loaded[name]=p;files[f.relative_to(ROOT).as_posix()]=SHA(f);return p
    coverage=read('w5-current-end-coverage');materials=read('w5-nominal-material-selection')
    assembly=read('current-w5-assembly/neutral-manifest');choice=read('current-operating-native-composition');sources=read('current-source-supports')
    validate_counts(coverage,materials,assembly)
    for name in ['operating-supports-native/manifest','operating-supports-native/upper-junction-native',
        'local-source-retention-roots','local-source-retention-native/manifest','remaining25-saddle-roots','remaining25-restraint-space',
        'current-upper-operating-roots','individual-bank-roots','individual-bank-seat-relief-space','remaining-frame-saddles-native/manifest',
        'receiver-supports/manifest','remaining-supports/manifest','remaining-support-shared-material',
        'g1-rooted-carrier-plan','remaining-fixed-feed-checks','body36-fixed-restraint-coverage','body36-shared-macro-layout',
        'body36-recovery-layout','retained-feed-restraints-checks','u1-power-grips-native','BUS-native-checks',
        'fixed-body-cut-contribution','body36-fit-material-contribution','case-bond-material-contribution']:
        read(name)
    macro=loaded['body36-shared-macro-layout'];key=(OUT/'body36-shared-macro-layout.json').relative_to(ROOT).as_posix()
    commit=macro['inherited_qualified_receipt']['git_commit'];raw=subprocess.check_output(['git','show',commit+':'+key],cwd=ROOT)
    variants={hashlib.sha256(v).hexdigest() for v in (raw,raw.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))}
    unchanged_routes(json.loads(raw),macro,loaded['body36-recovery-layout'])
    for name,p in loaded.items():
        for n,h in p.get('source_sha256',{}).items():
            if n not in cache:cache[n]=SHA(ROOT/n)
            if cache[n]==h:continue
            assert name in ('g1-rooted-carrier-plan','remaining-fixed-feed-checks') and n==key and h in variants,('Changed proof input',name,n)
            ancestry.append(dict(receipt=name,input=n,historical_sha256=h,git_commit=commit,unchanged33_new3_verified=True))
    assert len(ancestry)==2
    assert loaded['current-upper-operating-roots']['accepted']==38 and not loaded['current-upper-operating-roots']['errors']
    assert loaded['individual-bank-roots']['accepted']==12 and not loaded['individual-bank-roots']['errors']
    seats=loaded['individual-bank-seat-relief-space']
    assert seats['status']=='TWELVE_INDIVIDUAL_BANK_SEATS_MATERIAL_CLEAR_ROOTS_SERVICE_OPEN' and not seats['errors']
    assert len(seats['seats'])==12 and all(not r['contacts'] for r in seats['seats'])
    seat_recipes={r['id']:r['recipe'] for r in seats['seats']}
    assert all(r['seat_recipe']==seat_recipes[r['id']] for r in loaded['individual-bank-roots']['groups'])
    assert not loaded['remaining-support-shared-material']['errors'] and not loaded['remaining-support-shared-material']['contacts']
    assert choice['physical_print_quantity']==14
    prints={r['part']:dict(r,scope='body') for r in choice['prints']};superseded=[]
    for r in sources['parts']:
        if r['part'] in prints:
            assert r['part'].endswith('FixedCarrier');superseded.append(r['part']);continue
        assert r['received_native_validation_reused']
        e=r['export'];assert e['printing']['fits_with_5mm_brim']
        prints[r['part']]=dict(part=r['part'],path=e['path'],sha256=e['sha256'],native=r['native'],native_object=r['native_object'],quantity=1,printing=e['printing'],scope='moving_source')
    assert len(prints)==22 and len(superseded)==4
    for r in prints.values():
        assert SHA(ROOT/r['path'])==r['sha256']
        files[r['path']]=r['sha256'];files[r['native']]=SHA(ROOT/r['native'])
    files[assembly['native']]=assembly['native_sha256'];assert SHA(ROOT/assembly['native'])==assembly['native_sha256']
    for name in coverage['source_sha256']:files[name]=SHA(ROOT/name)
    for name in materials['source_sha256']:files[name]=SHA(ROOT/name)
    # Runtime CAD embeds unchanged reference BReps and needs only its explicit
    # native links. Derived planning caches are provenance, not a runtime file.
    for r in assembly['printed_body_support_links']:files[r['native']]=SHA(ROOT/r['native'])
    for f in [OUT/'W5_ASSEMBLY.md',Path(__file__),Path(__file__).with_name('current_rest_pose.py'),
              Path(__file__).with_name('compose_w5_end_coverage.py'),Path(__file__).with_name('compose_w5_materials.py'),
              Path(__file__).with_name('build_current_w5_assembly.py'),Path(__file__).with_name('correct_w5_snapshot_selection.py')]:
        files[f.relative_to(ROOT).as_posix()]=SHA(f)
    # Required referenced runtime and source files, excluding the reproducible
    # planning archive (not needed to open or use the selected assembly).
    transient={n:h for n,h in assembly['source_sha256'].items() if n.endswith('remaining25-space-context.zip')}
    assert len(transient)==1
    for n,h in assembly['source_sha256'].items():
        if n in transient:continue
        files[n]=h
    assert all(SHA(ROOT/n)==h for n,h in files.items())
    selection=dict(status='W5_CURRENT_NOMINAL_PROTOTYPE_COMPLETE',result_id='W5',selected=True,W5_complete=True,
        physical_pass=False,E3_complete=False,A2_complete=False,K1_complete=False,K2_complete=False,K3_complete=False,A3_complete=False,
        native=assembly['native'],native_sha256=assembly['native_sha256'],prints=list(prints.values()),
        print_subset_quantity=22,print_subset_NOT_whole_cat=True,superseded_source_FixedCarrier_exports=superseded,
        nets=80,logical_ends=160,conductor_portions=101,physical_cut_ends=202,
        end_coverage='w5-current-end-coverage.json',materials='w5-nominal-material-selection.json',assembly_instructions='W5_ASSEMBLY.md',
        verified_historical_receipt_ancestry=ancestry,transient_planning_cache_NOT_runtime_dependency=transient,
        readiness='prototype',nominal_preparation_NOT_cutting_or_power_authorization=True,
        limits=['Delivered pin cavities, Cu/OD/termination/usable lengths and retention must be checked before use',
                'PETG/adhesive/sleeve/case trials, loads and continuous motion acceptance are phase2 gates',
                'Whole-robot M4/K1/K2/K3/A2/A3 and electrical E3 remain separate open results'],
        source_sha256=files,worker_seconds=round(time.monotonic()-tick,3))
    sf=OUT/'w5-selection.json';sf.write_text(json.dumps(selection,indent=2)+'\n');files[sf.relative_to(ROOT).as_posix()]=SHA(sf)
    gate_names=('geometry','assembly','fit','petg','loads','electrical','service')
    reasons=dict(geometry='Nominal current geometry/material and affected-interface receipts composed; not physical validation.',
        assembly='Local W5 order and relocated native links prepared; whole-robot A2 remains open.',
        fit='Delivered Cu/OD/cavity/termination/PETG/case/sleeve fit trials required.',petg='Geometry and exports prepared; print/profile/coupons not approved.',
        loads='No physical retention/creep/bond load acceptance.',electrical='E3 source/fault/lead data gaps remain open; no power authorization.',
        service='Local prototype reverse assembly documented; whole-robot service/M4/A2 remain open.')
    manifest=dict(schema_version=1,readiness='prototype',scope='Complete nominal W5 preparation only. Not whole phase1, printing, cutting or power approval.',
        selected=True,W5_complete=True,physical_pass=False,files=[dict(path=n,sha256=h) for n,h in sorted(files.items())],
        gates={n:dict(status='open',reason=reasons[n]) for n in gate_names})
    report=verify(ROOT,manifest);assert report['integrity_ok'],report
    mf=OUT/'w5-manifest.json';mf.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(status=selection['status'],files=report['files_checked'],print_subset=22,seconds=selection['worker_seconds'])))


if __name__=='__main__':run()
