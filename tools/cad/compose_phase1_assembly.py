"""One complete nominal assembly dependency graph, not a powered trial."""
import json,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,BASE,SHA
from release_check import verify,REQUIRED_GATES
from current_work_guard import check


def order(stages):
    seen=set()
    for s in stages:
        assert s['id'] not in seen and set(s['requires'])<=seen,(s['id'],s['requires'],seen)
        seen.add(s['id'])
    return seen


def stage_for(r):
    n=r['identity']
    if n.startswith('P0-BASE-COVER'):return 'close'
    if n.startswith('P0-BATTERY'):return 'battery'
    if n.startswith('P0-BASE-FRAME'):return 'base'
    if n.startswith('P0-BASE-') or 'HipExtension' in n or 'KneeCarrier' in n:return 'legs'
    if n.startswith('head:') or n.startswith('tail ') or n=='drive:MG92BPrintedHorn20T-R2':return 'headtail_bench'
    if n.startswith(('ReceiverCap','SourceGripRail')):return 'route_finish'
    if n in ('Foundation','LowerCarrier001','LeftRiser','RightRiser') or n.endswith('FixedCarrier') or n in ('LowerClampJaw','TopClampPad') or 'TailRiser' in n:return 'mounts'
    return 'upper_bench'


def run():
    check();tick=time.monotonic();pins={}
    def read(rel):
        f=BASE/rel;pins[f.relative_to(ROOT).as_posix()]=SHA(f);return json.loads(f.read_text())
    k1=read('phase1-current-print-selection.json');k2=read('phase1-current-purchased-selection-r2.json');w5=read('body-harness-checkpoint/w5-selection.json')
    for p in ['head-mount-checkpoint/selection.json','tail-mount-checkpoint/selection.json','mounting-checkpoint/current-M5-selection.json',
        'body-harness-checkpoint/e1-selection.json','aux-wiring-checkpoint/selection.json','tail-wiring-checkpoint/selection.json',
        'head-wiring-checkpoint/fixed-head-current-selection.json','pwm-branch-checkpoint/selection.json']:
        read(p)
    stages=[dict(id=n,requires=req) for n,req in [
        ('delivery',[]),('base',['delivery']),('mounts',['base']),('legs',['mounts']),
        ('headtail_bench',['delivery']),('headtail_install',['mounts','headtail_bench']),
        ('battery',['legs','mounts','headtail_install']),('electronics_bench',['delivery']),('lower_boards',['mounts','electronics_bench']),
        ('looms_bench',['delivery']),('bank_inputs_before_TE',['looms_bench','mounts']),
        ('upper_bench',['electronics_bench','bank_inputs_before_TE']),('upper_install',['upper_bench','lower_boards']),
        ('route_finish',['upper_install','looms_bench','legs','headtail_install']),
        ('close',['route_finish']),('unpowered_checks',['close','battery']),('E3_power_gate',['unpowered_checks'])]]
    seen=order(stages)
    prints=[dict(identity=r['identity'],quantity=r['quantity'],stage=stage_for(r)) for r in k1['prints']]
    assert all(r['stage'] in seen for r in prints)
    assert sum(r['quantity'] for r in prints)==k1['installed_print_quantity']==122
    docs=[BASE/'PHASE1_ASSEMBLY.md',BASE/'body-harness-checkpoint/W5_ASSEMBLY.md',
        BASE/'head-mount-checkpoint/README.md',BASE/'tail-mount-checkpoint/README.md',
        BASE/'mounting-checkpoint/current-M5-README.md',BASE/'pwm-branch-checkpoint/README.md',
        ROOT/'hardware/electronics/power-platform/MONTAZ-P0.md',Path(__file__)]
    for f in docs:assert f.is_file(),f;pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    selected=dict(status='A2_ONE_CURRENT_WHOLE_NOMINAL_ASSEMBLY_SEQUENCE',result_id='A2',A2_complete=True,selected=True,
        physical_pass=False,readiness='prototype',stages=stages,print_allocations=prints,
        hardware_role_count=len(k2['roles']),component_rows=len(k2['components']),
        current_net_count=w5['nets'],current_physical_cut_ends=w5['physical_cut_ends'],
        instruction=(BASE/'PHASE1_ASSEMBLY.md').relative_to(ROOT).as_posix(),
        scope='Whole nominal open prototype assembly/reverse sequence: P0/battery,neck,head,tail,boards,bank,all current wiring. Staged tool/fastener access, explicit pretermination threading and ordinary deep disconnection. No hot-swap/zero-disconnection requirement or physical/energizing PASS.',
        physical_phase2_gates=['Delivered geometry/access/tool/fasteners/PETG/adhesives/cable limits before actual assembly',
            'Unpowered electrical continuity/polarity/retention and continuous movement must be performed',
            'E3 independent power gate must close before any source is connected'],
        source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3))
    f=BASE/'phase1-assembly-selection.json';f.write_text(json.dumps(selected,indent=2)+'\n',newline='\n');pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    manifest=dict(schema_version=1,result_id='A2',readiness='prototype',scope=selected['scope'],selected=True,A2_complete=True,physical_pass=False,
        selection=f.relative_to(ROOT).as_posix(),files=[dict(path=n,sha256=h) for n,h in sorted(pins.items())],
        gates={n:dict(status='open',reason='Nominal sequence only; physical/print/electrical readiness not demonstrated.') for n in REQUIRED_GATES})
    assert verify(ROOT,manifest)['integrity_ok']
    f=BASE/'phase1-assembly-manifest.json';f.write_text(json.dumps(manifest,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(stages=len(stages),prints=len(prints),installed=122,seconds=selected['worker_seconds'])))


if __name__=='__main__':run()
