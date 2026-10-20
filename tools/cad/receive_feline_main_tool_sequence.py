"""Release the one consumable grip band BEFORE MAIN fastener tooling.

No geometry/margin changes. Reuse all passing tool paths; the four rejected
rows were only this absent nylon band, never another material or fastener.
"""
import gzip,json,time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();f=OUT/'n01-MAIN-fastener-access.json';p=json.loads(f.read_text())
    assert p['status']=='MAIN_FASTENER_TOOL_HOLDS' and len(p['failures'])==4
    assert all(k.endswith('|MainSupported:band') for k in p['failures'])
    for n,h in p['source_sha256'].items():assert sha(ROOT/n)==h,n
    pf=ROOT/p['pair_rows'];assert sha(pf)==p['pair_rows_sha256'];old=json.loads(gzip.decompress(pf.read_bytes()))
    checks={k:v for k,v in old.items() if not k.endswith(('|MainSupported:band','|MainSupported:head'))}
    assert all(v['ok'] for v in checks.values())
    dest=OUT/'n01-MAIN-fastener-sequence-received.json';rows=dest.with_suffix('.pairs.json.gz')
    rows.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
    r=dict(p,status='MAIN_TWO_AXIS_FASTENER_ACCESS_RECEIVED_HARNESS_RELEASE_OPEN',
        temporarily_removed_actual_parts=p['temporarily_removed_actual_parts']+['MainSupported:band','MainSupported:head'],
        released_band_is_consumable_replaced_after_service=True,band_absent_for_initial_fastener_assembly=True,
        live_copper_metal_and_foreign_tool_margins_NOT_reduced=True,checks=len(checks),failures=[],
        superseded_absent_material_rows=p['failures'],unchanged_passing_queries_reused=len(checks),
        sequence=['Top service panel absent; unpowered assembly only','Withdraw only F_R2 ATO using unchanged received path',
            'Cut/remove MAIN grip nylon band+head BEFORE accessing screws; no tool-induced harness load',
            'Enter socket sideways above bed, rise3mm; use upper driver and park two complete M2 stacks',
            'Full F_PI/splice/harness release remains common-plan dependency','After MAIN fixed and tools withdrawn replace grip band and reinstall F_R2 ATO'],
        source_sha256={n.relative_to(ROOT).as_posix():sha(n) for n in (f,pf,Path(__file__))},
        pair_rows=rows.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(rows),adopted_worker_seconds=p['worker_seconds'],worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,r);print(r['status'],r['checks'],r['worker_seconds'],flush=True)


if __name__=='__main__':main()
