"""One coupled correction driven by completed, rejected R4 saved geometry."""
from pathlib import Path
import runpy

definition=runpy.run_path(str(Path(__file__).with_name('w5_leg_fanouts_r4.py')),run_name='r4_definitions')
M=definition['M'];source=definition['source']


def replace(old,new):
    global source
    assert source.count(old)==1,old
    source=source.replace(old,new)


replace("w5-leg-fanouts-r4'","w5-leg-fanouts-r5'")
replace('from w5_leg_fanout_layout import changed_plan, GROUND_DX, GROUND_DY',
        'from w5_leg_fanout_layout_r5 import changed_plan, GROUND_DX, GROUND_DY')
replace("tie_shifts={'DATA_tie/W007/1/':-2.5,'DATA_tie/W012/0/':1.5}","tie_shifts={}  # retain all six selected DATA ties exactly on their wires")
replace("ROOT/'tools/electronics/w5_leg_fanout_layout.py'","ROOT/'tools/electronics/w5_leg_fanout_layout_r5.py'")
replace('    started=datetime.now(timezone.utc)', '''    started=datetime.now(timezone.utc)
    rejected_file=ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r4/checks.json'
    rejected=json.loads(rejected_file.read_text(encoding='utf-8'))
    assert rejected['status']=='COUPLED_LEG_FANOUT_REJECTED' and len(rejected['routes'])==36
    assert all(sha(ROOT/k)==v for k,v in {**rejected['source_sha256'],**rejected['files']}.items())''')
replace("            print('FANOUT',row['wire'],round(path.Length,1),'blank',blank,'hits',len(hits),flush=True)",
        """            save(OUT/'progress.json',dict(completed_routes=len(built),hits=hits,errors=errors,pairs=pairs,started_utc=started.isoformat()))
            print('FANOUT',row['wire'],round(path.Length,1),'blank',blank,'hits',len(hits),flush=True)""")
replace("    mounts=OUT/'RELOCATED_OWNERS_WORLD.brep'", """    save(OUT/'progress.json',dict(completed_routes=len(built),hits=hits,errors=errors,pairs=pairs,started_utc=started.isoformat(),all_contact_checks_completed=True))
    pins += [rejected_file,ROOT/'tools/electronics/w5_leg_fanouts_r4.py',ROOT/'tools/electronics/w5_leg_fanouts_r4_saved.py']
    mounts=OUT/'RELOCATED_OWNERS_WORLD.brep'""")
exec(compile(source,str(Path(__file__).resolve()),'exec'))
