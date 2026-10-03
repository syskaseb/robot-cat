"""One bounded bank checkpoint pipeline, retaining existing construction.

Expand saved material/assembly/selection builders without running obsolete
variants. Only actual clear R18 permits one R52. --recover saves the native
Cover and failed R17 before the expensive shared check. Never closes wholeW5.
"""
from pathlib import Path
from datetime import datetime, timezone
import ast, json, runpy, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha, save
START=datetime(2026,10,3,21,25,28,tzinfo=timezone.utc)

def expanded(name):
    return runpy.run_path(str(ROOT/'tools/electronics'/name),run_name='checkpoint_definition')['code']

def replace(code, changes):
    for old,new in changes:
        assert old in code,old
        code=code.replace(old,new)
    ast.parse(code)
    return code

def execute(code):
    ns=dict(__file__=str(Path(__file__).resolve()),__name__='checkpoint_definition')
    exec(compile(code,str(Path(__file__).resolve()),'exec'),ns)
    ns['main']()

def recover():
    prev=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r37/manifest.json'
    m=json.loads(prev.read_text(encoding='utf-8')); files={r['path']:r['sha256'] for r in m['files']}
    def add(p):
        rel=p.relative_to(ROOT).as_posix();h=sha(p)
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    add(prev)
    nativepath='hardware/electronics/full-cat/servo-fuse-cover-source-joint-service-r2/checks.json'
    native=json.loads((ROOT/nativepath).read_text(encoding='utf-8'))
    assert native['exports'][0]['relocated_reopen'] and len(native['mounts'])==4
    for folder in ('servo-fuse-bank-fixed-rr-lift-r17','servo-fuse-cover-source-joint-service-r1','servo-fuse-cover-source-joint-service-r2'):
        for base in ('hardware/electronics/full-cat','hardware/cad/studies'):
            directory=ROOT/base/folder
            if directory.exists():
                for p in directory.iterdir():
                    if p.suffix in ('.json','.brep','.FCStd','.stl'):add(p)
    for rel,h in native['source_sha256'].items():assert sha(ROOT/rel)==h,rel;add(ROOT/rel)
    for name in ('servo_fuse_cover_source_joint_service_r1.py','servo_fuse_cover_source_joint_service_r2.py','servo_fuse_bank_fixed_rr_lift_r18.py','servo_fuse_bank_close_r1.py'):add(ROOT/'tools/electronics'/name)
    now=datetime.now(timezone.utc)
    m.update(status='NATIVE_COVER_FULL_JOINT_PASSAGES_WITH_PRESERVED_MOUNTS_R18_PENDING',recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-START).total_seconds(),completion_turn_started_utc=START.isoformat(),selected=False,local_bank_complete=False,
        completed='Whole insulated W042/W044/W052 source passages and a native short bridge preserving all four original Cover mount regions. R1 split mount rejected; R17 contact30mm retained.',
        remaining=['R18 installed Cover and all six withdrawal samples; only clear result permits one material/assembly/R52/commit pipeline.','WholeW5/E3/K3/A2/A3 OPEN;15/20=75%.'])
    m['current_cover']=dict(source=nativepath,exports=native['exports'],additive_mount_bridge=True)
    m['whole_bank_release']=dict(source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r17/checks.json',status='R17_REJECTED_AT30MM_R18_PENDING',continuous_withdrawal_qualified=False)
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r40'
    out.mkdir(parents=True,exist_ok=True); assert not (out/'manifest.json').exists()
    save(out/'manifest.json',m);print('RECOVERABLE_R40',len(files),flush=True)

def close():
    lift='servo-fuse-bank-fixed-rr-lift-r18'
    stock=replace(expanded('servo_fuse_bank_stock_budget_r12.py'),[
        ('servo-fuse-bank-stock-budget-r12','servo-fuse-bank-stock-budget-r13'),
        ('servo-fuse-bank-fixed-rr-lift-r17',lift)])
    execute(stock)
    assembly=replace(expanded('servo_fuse_bank_assembly_r11.py'),[
        ('servo-fuse-bank-assembly-r11','servo-fuse-bank-assembly-r12'),
        ('servo-fuse-bank-stock-budget-r12','servo-fuse-bank-stock-budget-r13'),
        ('servo-fuse-bank-fixed-rr-lift-r17',lift),
        ('servo-fuse-cover-deck-edge-service-r2','servo-fuse-cover-source-joint-service-r2')])
    execute(assembly)
    selection=replace(expanded('servo_fuse_bank_select_r7.py'),[
        ('servo-fuse-bank-stock-budget-r12','servo-fuse-bank-stock-budget-r13'),
        ('servo-fuse-bank-assembly-r11','servo-fuse-bank-assembly-r12'),
        ('servo-fuse-bank-fixed-rr-lift-r17',lift),
        ('servo-fuse-cover-deck-edge-service-r2','servo-fuse-cover-source-joint-service-r2'),
        ('CoverDeckEdgeServiceFinished','CoverSourceJointServiceFinished')])
    execute(selection)
    code=(ROOT/'tools/electronics/servo_fuse_construction_checkpoint_r36.py').read_text(encoding='utf-8')
    code=replace(code,[
        ('servo-fuse-construction-checkpoint-r35','servo-fuse-construction-checkpoint-r40'),
        ('servo-fuse-construction-checkpoint-r36','servo-fuse-construction-checkpoint-r41'),
        ('servo-fuse-bank-fixed-rr-lift-r15',lift),
        ('servo-fuse-bank-stock-budget-r11','servo-fuse-bank-stock-budget-r13'),
        ('servo-fuse-bank-assembly-r10','servo-fuse-bank-assembly-r12'),
        ('servo_fuse_bank_stock_budget_r11.py','servo_fuse_bank_stock_budget_r12.py'),
        ('servo_fuse_bank_assembly_r10.py','servo_fuse_bank_assembly_r11.py'),
        ('servo_fuse_bank_select_r6.py','servo_fuse_bank_select_r7.py'),
        ('servo_fuse_bank_fixed_rr_lift_r15.py','servo_fuse_bank_fixed_rr_lift_r18.py')])
    marker="    m.update(recorded_utc=now.isoformat(),status='LOCAL_12_FUSE_BANK_COMPLETE_PHASE1_INCOMPLETE',"
    assert marker in code
    code=code.replace(marker,"    m.update(elapsed_turn_seconds=(now-datetime(2026,10,3,21,25,28,tzinfo=timezone.utc)).total_seconds(),completion_turn_started_utc='2026-10-03T21:25:28Z',recorded_utc=now.isoformat(),status='LOCAL_12_FUSE_BANK_COMPLETE_PHASE1_INCOMPLETE',")
    execute(code)

if __name__=='__main__':
    if sys.argv[1:]==['--recover']:recover()
    elif not sys.argv[1:]:close()
    else:raise SystemExit('Use no arguments for guarded close, or --recover')
