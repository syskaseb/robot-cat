"""Preserve a standalone concept checkpoint and its inherited source dependencies."""
import json
from pathlib import Path
import pilot
from release_check import sha256,verify


def main():
    out=pilot.CAD/'studies/tail-cartridge-service'
    parent_path=pilot.ROOT/'hardware/releases/tail-cartridge-study.json'
    parent=json.loads(parent_path.read_text())
    assert verify(pilot.ROOT,parent)['integrity_ok']
    paths=[pilot.ROOT/item['path'] for item in parent['files']]+[parent_path]
    paths += [out/f for f in ['TailCartridgeService.FCStd','README.md','service-channel.png',
                             'service-audit.json','joint-audit.json','installation-audit.json']]
    paths += [pilot.ROOT/'tools/cad'/f for f in ['tail_cartridge_service.py','tail_cartridge_joints.py',
               'tail_cartridge_installation.py','test_tail_cartridge_service.py','package_tail_cartridge_service.py']]
    audit=json.loads((out/'service-audit.json').read_text())
    assert audit['study_sha256']==sha256(out/'TailCartridgeService.FCStd')
    for name,digest in audit['unchanged_robot_files'].items():assert sha256(pilot.ROOT/name)==digest
    manifest={'schema_version':1,'name':'tail-cartridge-service-r2','readiness':'concept',
        'installed_in_robot':False,'freecad':'1.1.3','occt':'7.8.1',
        'files':[{'path':p.relative_to(pilot.ROOT).as_posix(),'sha256':sha256(p)} for p in paths],
        'gates':{}}
    reasons={
        'geometry':'Study PETG only: 21 fully constrained sketches, strict BOP, explicit cuts, relocation and parameter restoration; not robot shell.',
        'assembly':'Bench native Fixed solver passed; whole tail drive and remaining assembly trajectories unresolved.',
        'fit':'Approximate horn, nominal M2/M3 and tool envelope; actual spline, screw and PETG fit unknown.',
        'petg':'Inherited 0.8/0.9 mm local walls, 1.65 mm roof and print profile unresolved.',
        'loads':'New nut slot and insertion flat reduce sections; strength, layers and creep not validated.',
        'electrical':'Factory horn screw, servo cable and complete electrical integration unresolved.',
        'service':'Conditional blade/nut access and sampled preassembly path only; actual screw seating, hands and remaining installation stages unknown.'}
    for name,reason in reasons.items():manifest['gates'][name]={'status':'pass' if name=='geometry' else 'open','reason':reason}
    manifest['gates']['geometry']['evidence']=[(out/'service-audit.json').relative_to(pilot.ROOT).as_posix()]
    assert verify(pilot.ROOT,manifest)['integrity_ok']
    assert not verify(pilot.ROOT,manifest,True)['integrity_ok']
    (pilot.ROOT/'hardware/releases/tail-cartridge-service.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8',newline='\n')
    print(verify(pilot.ROOT,manifest))


if __name__=='__main__':main()
