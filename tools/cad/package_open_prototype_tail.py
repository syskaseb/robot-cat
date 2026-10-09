"""Fail-closed M3 nominal prototype selection; fixed20-result score overlay."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,time,struct,re
from release_check import verify, REQUIRED_GATES

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'tail-mount-checkpoint'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def stl_size(path):
    data=path.read_bytes();n=struct.unpack_from('<I',data,80)[0]
    low=[float('inf')]*3;high=[float('-inf')]*3
    if len(data)==84+50*n and n>0:
        vertices=(struct.unpack_from('<3f',data,84+50*i+12+12*j) for i in range(n) for j in range(3))
    else:
        vertices=[tuple(map(float,m)) for m in re.findall(r'(?m)^\s*vertex\s+([\deE+.-]+)\s+([\deE+.-]+)\s+([\deE+.-]+)\s*$',data.decode('ascii'))]
        assert vertices,'No retained STL vertices'
    for xyz in vertices:
        for axis,v in enumerate(xyz):low[axis]=min(low[axis],v);high[axis]=max(high[axis],v)
    return [b-a for a,b in zip(low,high)]


def run():
    start=time.monotonic();mount=read(OUT/'native-mount-checks.json');tail=read(OUT/'tail-assembly-checks.json')
    reopen=read(OUT/'tail-reopen-checks.json')
    assert mount['status']=='NATIVE_PLATE_ROOTED_TAIL_MOUNT_PREPARED'
    assert tail['status']=='CURRENT_TAIL_MECHANICS_NOMINAL_GEOMETRY_PREPARED'
    assert reopen['status']=='FRESH_RELOCATED_NATIVE_REOPEN_CHECKED'
    assert reopen['all_61_rise_restored'] and reopen['localized_moving_parts_checked']==33
    assert not mount['contacts'] and not mount['errors'] and not tail['contacts'] and not tail['errors']
    assert [s['angle_deg'] for s in tail['motion_samples']]==list(range(-30,31,5))
    assert all(s['new_contacts']==0 for s in tail['motion_samples'])
    assert len(tail['tail_identities'])==len(set(tail['tail_identities']))==61
    assert tail['internal_hardware']['unique_parts']==44
    assert tail['native_yaw_parameter_checked'] and tail['whole_tail_parameter_restore']
    for proof in (mount,tail,reopen):
        for n,h in proof['source_sha256'].items():assert sha(ROOT/n)==h,n
    assert sha(OUT/'TailAssemblyCurrent.FCStd')==tail['model_sha256']
    selection=read(ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json')
    prints=[]
    for row in selection['prints']:
        if row['module'] not in ('tail support','tail segments') and row['identity']!='drive:MG92BPrintedHorn20T-R2':continue
        q=dict(row);q['quantity']=1
        if row['identity']=='tail support:MG92BMount29':
            q.update(stl=(BASE/'wiring-checkpoint/TailLocalCurrent.stl').relative_to(ROOT).as_posix(),
                     source=(OUT/'TailAssemblyCurrent.FCStd').relative_to(ROOT).as_posix(),source_object='RaisedTailSupport',
                     print_size_mm=[126,97.6130837436,54],status='nominal_prototype_selected_physical_fit_open')
        if row['identity']=='tail support:TailRoot29':
            q.update(source='hardware/cad/studies/tail-horn-provisional-r5/TailCartridgeProvisionalR5.FCStd',source_object='SupportedRoot34')
        if row['identity']=='drive:MG92BPrintedHorn20T-R2':
            q.update(source='hardware/cad/studies/mg92b-printed-horn-r2/MG92BPrintedHornTopReliefR2.FCStd',source_object='PrintedHorn20T',
                     allocation='ONE of the existing three horn prints; two head horns are not added again')
        assert (ROOT/q['stl']).is_file();q['sha256']=sha(ROOT/q['stl'])
        q['print_size_mm']=stl_size(ROOT/q['stl']);prints.append(q)
    assert len(prints)==16
    for file,row in mount['exports'].items():
        assert sha(OUT/file)==row['sha256']
        prints.append(dict(identity='CP2:'+file.split('_x')[0],quantity=row['quantity'],stl=(OUT/file).relative_to(ROOT).as_posix(),
            source=(OUT/'TailAssemblyCurrent.FCStd').relative_to(ROOT).as_posix(),source_object=file.split('_x')[0],
            sha256=row['sha256'],print_size_mm=row['dimensions_mm'],material='PETG',brim_mm=5,
            orientation='Flat base at Z0; carrier floor down, annular risers axis vertical',supports='Phase2 slicer/printed fit verification required'))
    assert all(max(row.get('print_size_mm',[0]))+10<256 for row in prints)
    package=dict(status='M3_NOMINAL_PROTOTYPE_MECHANICS_SELECTED',selected=True,mechanical_M3_complete=True,
        physical_pass=False,print_ready=False,wiring_complete=False,full_phase1_complete=False,
        current_assembly='TailAssemblyCurrent.FCStd',result_id='M3',prints=prints,
        tail_internal_hardware=tail['internal_hardware'],
        shared_rear_frame_hardware=dict(M2x30=4,M2_nut_reused=4,M2_washer_reused=8,
             replaces='Four rear P0 M2x10 / historical M2x14; no second TailFrame bolt set',
             selected_supplier='Rosentaler 0200912020030 DIN912 A2-70 M2x30 full thread30mm',
             supplier_url='https://www.rosentaler-schrauben.de/Befestigungstechnik/Schrauben/Innensechskant-Schrauben/DIN-912-Zylinderkopf-mit-Innensechskant/Zylinderkopfschraube-mit-Innensechskant-DIN-912-A2-Edelstahl-Rostfrei-M2-x-30.html/',
             procurement_contribution_only=dict(unit='piece',installed=4,spare=1,planned_total=5,purchased=0)),
        monitor=dict(case_bounds_mm=[108,-12.5,42.92,149,12.5,54.92],floor_thickness_mm=1.8,band_channel_minimum_floor_mm=1.6,
             tie_count=2,ties_retained_not_extra=True,sku='111-02370',nominal_length_mm=145,
             supplier_url='https://www.hellermanntyton.com/products/cable-ties-inside-serrated/t18i/111-02370',
             unknown_delivered_pads_and_connectors_are_fit_gate=True),
        assembly_recipe='README.md',range_deg=[-30,30],discrete_samples=13,
        work_timing=dict(started_utc='2026-10-09T13:55:24Z',native_checks_finished_utc='2026-10-09T15:08:27Z',
                         wall_seconds_to_native_checks=4383,not_cpu_seconds=True),
        phase2_gates=['Actual MG92B spline, shaft height and axial retention screw/retainer fit',
             'PETG bearing, creep/torque and support/web coupon',
             'Delivered monitor underside/lead exit, insulation and non-crushing tie fit',
             'Real fastener lengths, thread runout, tools and light tightening; frame holes hand-finished per retained P0 recipe',
             'Slicer/printing; loaded tail movement and passive segment posture'],
        explicitly_open=['W4 tail-to-body wiring','W5 whole harness','M2 head','M4 protective covers','M5 complete board mount result','E3 data','Global K1/K2/K3 and A2/A3'],
        fixed_total=20,confirmed_result_ids=['M1','M3','E4','A1'],result_count=4,result_percent=20,
        preserved=['P0','E6','15 drives','bank R47','MAIN worldZ46.52','torso325x200x160','replaceable provisional MG92B adapters'])
    save(OUT/'selection.json',package)
    pins={OUT/'README.md',OUT/'selection.json',OUT/'native-mount-checks.json',OUT/'tail-assembly-checks.json',OUT/'tail-reopen-checks.json',
          OUT/'TailAssemblyCurrent.FCStd',OUT/'TailMechanicalCurrent.FCStd',Path(__file__),ROOT/'tests/test_open_prototype_tail_package.py'}
    for proof in (mount,tail,reopen):pins.update(ROOT/n for n in proof['source_sha256'])
    pins.update({BASE/'wiring-checkpoint/source-group-allocation.json',BASE/'wiring-checkpoint/obstacle-map-current.json',
                 ROOT/'tools/cad/open_prototype_side_source_routes.py',ROOT/'tools/cad/open_prototype_tail_clearance.py'})
    for row in prints:
        pins.add(ROOT/row['stl'])
        if row.get('source'):pins.add(ROOT/row['source'])
    manifest=dict(schema_version=1,readiness='prototype',result_id='M3',mechanical_preparation_complete=True,physical_pass=False,
         gates={g:dict(status='open',reason='Phase2 delivered fit/loads/material/electrical/tool trials remain open; nominal M3 preparation only') for g in REQUIRED_GATES},
         files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(pins)])
    manifest['gates']['geometry']=dict(status='pass',reason='Changed nominal material, coupled native rise/yaw and13 discrete motion samples; no continuous or whole-robot claim',
        evidence=[(OUT/f).relative_to(ROOT).as_posix() for f in ('native-mount-checks.json','tail-assembly-checks.json','tail-reopen-checks.json')])
    assert verify(ROOT,manifest)['integrity_ok'] and not verify(ROOT,manifest,True)['integrity_ok']
    save(OUT/'manifest.json',manifest)
    score=dict(status='CURRENT_CP2_NOMINAL_PREPARATION_SCORE',fixed_total=20,confirmed_result_ids=package['confirmed_result_ids'],
       result_count=4,result_percent=20,change_pp=5,new_result='M3',physical_pass=False,
       baseline='execution-plan.json remains immutable historical stage1 minimum3/20',
       evidence=(OUT/'manifest.json').relative_to(ROOT).as_posix(),evidence_sha256=sha(OUT/'manifest.json'),
       checked_utc=datetime.now(timezone.utc).isoformat(),verification_seconds=round(time.monotonic()-start,3))
    save(BASE/'current-phase1-score.json',score)
    print(json.dumps(dict(result_count=4,result_percent=20,pins=len(pins),verification_seconds=score['verification_seconds'])))


if __name__=='__main__':run()
