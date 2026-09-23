"""Pin this concept checkpoint; does not create a release tag or publish."""
import json
from pathlib import Path
import pilot
from release_check import sha256, verify


def main():
    folder=pilot.CAD/'studies/tail-cartridge'
    audit=json.loads((folder/'cartridge-audit.json').read_text())
    paths=[folder/name for name in ['.gitattributes','TailHornCartridge.FCStd','README.md','cartridge-audit.json',
           'cartridge-details.json','cartridge-assembled.png','cartridge-exploded.png']]
    paths.extend(folder/'rejected-r0'/name for name in ['TailHornCartridge.FCStd','cartridge-audit.json','cartridge-assembled.png','tail_cartridge_study.py'])
    paths.extend(pilot.ROOT/name for name in audit['unchanged_robot_files'])
    ref=pilot.ROOT/'hardware/reference/mg92b-horn-2026-09-23'
    paths.extend(ref/name for name in ['MG92BCommunityReference.FCStd','README.md','measurements.json','LICENSE-Dtto.txt'])
    paths.extend(pilot.ROOT/'tools/cad'/name for name in ['tail_cartridge_study.py','tail_cartridge_details.py',
                 'test_tail_cartridge.py','package_tail_cartridge.py','pilot.py','tail_module.py','release_check.py'])
    manifest={'schema_version':1,'name':'tail-horn-cartridge-r1','readiness':'concept',
              'installed_in_robot':False,'freecad':'1.1.3','occt':'7.8.1',
              'files':[{'path':p.relative_to(pilot.ROOT).as_posix(),'sha256':sha256(p)} for p in paths],
              'gates':{}}
    for gate,reason in {
        'geometry':'Three study PETG solids only: strict BOP, exact intended operations, fully constrained sketches and standalone relocation; not legacy shell.',
        'assembly':'Not installed; new native joints and solver validation remain open.',
        'fit':'Approximate community horn and nominal fasteners only; actual part/tolerance not proven.',
        'petg':'Local 0.8/0.9 mm walls and 1.65 mm roof need redesign or justification; printer/profile and coupons missing.',
        'loads':'Layer direction, altered root section, torque transfer and creep unverified.',
        'electrical':'Servo cable and true supplied horn/central screw envelope unresolved.',
        'service':'Pre-root OD6 tool access only; assembled root blocks it. Counterholding M2 heads, M3 nut and assembly order unresolved.'
    }.items():
        manifest['gates'][gate]={'status':'pass' if gate=='geometry' else 'open','reason':reason}
    manifest['gates']['geometry']['evidence']=[(folder/f).relative_to(pilot.ROOT).as_posix() for f in ['cartridge-audit.json','cartridge-details.json']]
    assert verify(pilot.ROOT,manifest)['integrity_ok']
    assert not verify(pilot.ROOT,manifest,True)['integrity_ok']
    (pilot.ROOT/'hardware/releases/tail-cartridge-study.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8',newline='\n')
    print(verify(pilot.ROOT,manifest))


if __name__=='__main__':main()
