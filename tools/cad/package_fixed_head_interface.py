"""One current head replacement overlay; old releases remain immutable.

The overlay replaces identities and wire roles, not another head assembly.
It contributes no new phase point and is not a whole-cat release.
"""
import json,math,time
from pathlib import Path
from datetime import datetime,timezone
from release_check import verify,sha256,REQUIRED_GATES
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'head-wiring-checkpoint'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def blank(guide,source):return 5*math.ceil((guide+source+60)/5)

def run():
    tick=time.monotonic();nativefile=OUT/'fixed-head-jr-terminations-native.json';native=read(nativefile)
    assert native['status']=='FIXED_HEAD_JOINED_NATIVE_PREPARED_SELECTION_STOCK_OPEN'
    assert native['relocated_reopen'] and native['external_links']==0
    assert native['parameter_restore_mm']==[3,3.2,3] and len(native['exports'])==2
    model=ROOT/native['model'];assert sha256(model)==native['model_sha256']
    material=read(OUT/'fixed-head-jr-terminations-material.json')
    assert material['head_poses']==9 and material['leg_poses']==108
    assert not material['contacts'] and not material['errors']
    plan=read(OUT/'fixed-head-jr-terminations-plan.json')
    master=read(OUT/'fixed-head-native-master.json')
    assert master['identities']==52 and len(master['pose_samples'])==9
    assert master['MAIN_worldZ_4_5_4']==[46.52,47.52,46.52]
    pins={}
    def pin(p,digest=None):
        actual=sha256(p);assert digest is None or actual==digest,p
        name=p.relative_to(ROOT).as_posix();assert name not in pins or pins[name]==actual
        pins[name]=actual
    for name,h in native['source_sha256'].items():pin(ROOT/name,h)
    for p in [nativefile,model,Path(__file__),OUT/'fixed-head-current-README.md',Path(__file__).with_name('test_fixed_head_package.py')]:pin(p)
    retained={}
    for folder in ('head-mount-checkpoint','head-wiring-access-checkpoint','head-supply-checkpoint'):
        mf=BASE/folder/'manifest.json';m=read(mf)
        result=verify(ROOT,m);assert result['integrity_ok'],result
        for row in m['files']:pin(ROOT/row['path'],row['sha256'])
        pin(mf);retained[folder]=read(BASE/folder/'selection.json')
    m2,w2,w3=[retained[n] for n in ('head-mount-checkpoint','head-wiring-access-checkpoint','head-supply-checkpoint')]
    print_rows={r['identity']:dict(r) for r in m2['prints']}
    retired=[]
    for identity,part in [('head:UpperFork','MovingFork'),('head:YawCarrier','FixedYawCarrier')]:
        old=print_rows[identity];retired.append(old['stl'])
        row=next(r for r in native['exports'] if r['part']==part)
        pin(ROOT/row['path'],row['sha256']);assert max(row['size_mm'])+2*row['brim_each_mm']<256
        print_rows[identity]=dict(identity=identity,stl=row['path'],sha256=row['sha256'],quantity=1,
            print_size_mm=row['size_mm'],brim_each_mm=5,material='PETG',print_ready=False)
    # W3 owns the physical Foundation and carrier: not a second M2 plate.
    foundation=next(r for r in w3['prints'] if Path(r['path']).name=='Foundation_current_x1.stl')
    retired.append(print_rows['head:Foundation']['stl'])
    print_rows['head:Foundation']=dict(identity='head:Foundation',stl=foundation['path'],sha256=foundation['sha256'],
        quantity=1,print_size_mm=foundation['size_mm'],material='PETG',print_ready=False)
    retired.extend(r['path'] for r in w2['prints'] if 'HeadFixedAnchor' in r['path'])
    wire_rows=[dict(r) for r in w3['length_stock_rows'] if r['wire'] in ('XB12','XB13','XS13')]
    for row in plan['stock_rows']:
        n=row['wire'];strip=11 if n=='XB23' else 8
        cut=blank(row['HELU_guide_to_lap_end_mm'],strip)
        assert row['JR_nominal_trim_after_fit_mm']<280,'Keep connector/body reserve within JR300'
        wire_rows.append(dict(wire=n,sku='HELU'+{'XB22':'23302 red','XB23':'23301 black','XS23':'23308 yellow'}[n]+'0.5mm2',
            HELU_guide_mm=row['HELU_guide_to_lap_end_mm'],JR_guide_mm=row['JR_guide_to_lap_end_mm'],
            lap_overlap_mm=8,source_strip_or_lap_allowance_mm=strip,trim_allowance_mm=60,
            conservative_continuous_fit_blank_mm=cut,procurement_contribution_mm=5*math.ceil(cut*1.25/5),
            JR_nominal_trim_after_fit_mm=row['JR_nominal_trim_after_fit_mm'],JR_stock_product_mm=300,
            accounting='Replaces ALL prior pitch W2 local and W3 HELU contributions; JR guides consume one existing three-core JR300, not three purchased cables. No new boundary joint.'))
    assert {r['wire'] for r in wire_rows}=={'XB12','XB13','XS13','XB22','XB23','XS23'} and len(wire_rows)==6
    selection=dict(status='CURRENT_FIXED_HEAD_NOMINAL_REPLACEMENT_OVERLAY_SELECTED',selected=True,physical_pass=False,
        scope='One head/neck replacement overlay before whole-cat W5/stock selection, not a whole-cat assembly or print-ready release.',
        phase1_score_change_pp=0,preserves_result_ids=['M2','W2','W3'],
        native=native['model'],model_sha256=native['model_sha256'],prints=list(print_rows.values()),retired_print_paths=retired,
        body_foundation_role='Use current W3 Foundation replacement (or explicitly qualified whole-body successor), never instance the inherited M2 Foundation as a second plate.',
        replaces_mechanical_targets={'Fork':'MovingFork fixed interface','YawCarrier':'FixedYawCarrier fixed joins'},
        retired_wire_roles=['Old moving pitch JR/local solder joins','Old three pitch HELU transport loops/fixed tail boundary','Old outboard Fork receiver','Old HeadFixedAnchor and its two M3x10/nut/washer stacks'],
        retains=['All other50 head identities and existing M2 fasteners/adapters/current E6 ears','Whole three yaw source/local paths and their three individual joins','W3 source cases/both FHAC exits/grips/known PCB ends/individual source splice insulation','P0/bankR47/15drives/torso325x200x160'],
        length_stock_rows=wire_rows,
        quantities=dict(MG92B_factory250_reused_uncut=2,JR_Kamami586761_300mm22AWG=2,
            replacement_fixed_pitch_interface_T18I=16,retained_W3_case_source_T18I=12,
            yaw_local_ties='Retain existing yaw local roles only; no old pitch local tie or retired fixed anchor added again.',
            RNF100_1_8_raw_mm=[11.5]*3,RNF100_3_16_9_raw_mm=[20]*5,
            sleeve_accounting='Three retained yaw11.5 + three replacement fixed pitch20 + two retained FHAC20; do not also add old three pitch11.5.',
            new_M3=0,retired_anchor_M3x10=2,retired_anchor_nuts=2,retired_anchor_washers=2),
        assembly=plan['assembly'],service=plan['service'],
        routine_ATO='Retain selected W3 supported holder/case-band service; additions are below fixed receiving region. No new full connected head lift or74routineWAGO-disconnect criterion.',
        print_rule='One current replacement per identity. New parts each have5mmbrim allowance within256cube; orientation/PETG/slicer/delivery fit remain phase2 gates.',
        factory_motion='Retained S-prefix43.814903mm + constant206.185097mm free family = uncut250. Nominal CAD curve is not a continuous animation/sweep.',
        phase2_gates=plan['uncertainty']+w3['phase2_gates'],
        open=['Whole leg/body/source W5 and all independent restraints','M4 local/underside protection after current wiring','Global K1/K2/K3/A2/A3 and actual electrical E3'],
        checked_utc=datetime.now(timezone.utc).isoformat(),worker_seconds=round(time.monotonic()-tick,3))
    sf=OUT/'fixed-head-current-selection.json';save(sf,selection);pin(sf)
    gates={g:dict(status='open',reason='Nominal prototype preparation; delivered fit/PETG/load/electrical and whole build qualification not physical approval') for g in REQUIRED_GATES}
    gates['geometry']=dict(status='pass',reason='Changed wholehead factory/feed/support material plus added fixed joins;52rest identities/two changed targets9poses/108leg samples, native parameter/reopen and closed printable-size exports. Sampled scope only.',evidence=[nativefile.relative_to(ROOT).as_posix(),(OUT/'fixed-head-native-master.json').relative_to(ROOT).as_posix()])
    manifest=dict(schema_version=1,readiness='prototype',physical_pass=False,result_ids=['M2','W2','W3'],score_change_pp=0,
        tool_versions=dict(native='FreeCAD1.1.3 bundled py311; no external native links or addons'),gates=gates,
        files=[dict(path=n,sha256=h) for n,h in sorted(pins.items())])
    result=verify(ROOT,manifest);assert result['integrity_ok'],result
    assert not verify(ROOT,manifest,True)['integrity_ok']
    mf=OUT/'fixed-head-current-manifest.json';save(mf,manifest)
    score=read(BASE/'current-phase1-score.json');assert score['result_count']==12 and score['fixed_total']==20
    overrides=score.setdefault('current_result_overrides',{})
    for n in ('M2','W2','W3'):overrides[n]=dict(evidence=mf.relative_to(ROOT).as_posix(),sha256=sha256(mf),new_points=0)
    score['checked_utc']=selection['checked_utc'];score['current_head_change_pp']=0
    save(BASE/'current-phase1-score.json',score)
    print(json.dumps(dict(status=selection['status'],pins=len(pins),score=60,new_points=0,worker_seconds=time.monotonic()-tick)),flush=True)

if __name__=='__main__':run()
