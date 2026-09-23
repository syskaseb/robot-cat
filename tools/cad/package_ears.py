"""Hash the E1 development checkpoint; never promote printing readiness."""
import json
from pathlib import Path
import pilot,author_ears as task
from release_check import verify,sha256

def main():
    g=json.loads((task.OUT/'module.json').read_text());a=json.loads((task.OUT/'assembly.json').read_text())
    m=json.loads((task.OUT/'migration.json').read_text())
    assert m['assembly_sha256']==sha256(task.TARGET) and m['module_sha256']==sha256(task.MODULE)
    paths=[]
    old=pilot.ROOT/'hardware/releases/tail-cartridge-installation.json'
    prior=json.loads(old.read_text());assert verify(pilot.ROOT,prior)['integrity_ok']
    paths.extend([old]+[pilot.ROOT/r['path'] for r in prior['files']])
    for report,tool in [(g,'validate_ears.py'),(a,'validate_ear_assembly.py')]:
        assert report['tool_sha256']==sha256(pilot.ROOT/'tools/cad'/tool)
        for p,h in report['file_sha256'].items():assert sha256(pilot.ROOT/p)==h;paths.append(pilot.ROOT/p)
    assert not g['intersections'] and not a['new_intersections']
    assert len(a['native']['frames'])==22 and a['native']['temporary']==25 and a['native']['restored']
    assert all(r['strict_bop'] is True for n,r in g['new_geometry'].items() if n!='RearHead')
    assert all(max(p['restored_sample_distance_mm'].values())<1e-4 for p in g['parameters'])
    paths += [task.OUT/n for n in ['.gitattributes','README.md','module.json','assembly.json','migration.json','assembly-plan.json','checkpoint-entry.json','head-ears.png','robot-ears.png']]
    paths += [pilot.CAD/'validation/tail-cartridge-integration/checkpoint/.gitattributes']
    paths += [pilot.ROOT/'tools/cad'/n for n in ['author_ears.py','validate_ears.py','validate_ear_assembly.py','package_ears.py','test_ears.py','test_tail_installation.py']]
    paths += [pilot.ROOT/'hardware/bom/ears-e1.json']
    reasons={
      'geometry':'FAIL inherited head BOP errors. New ears strict BOP pass; parameter restoration uses documented sampled surface comparison, not exact Boolean proof.',
      'assembly':'Native 22 frames / 335 parts tested; 25 inherited TEMP locks remain, including head-to-neck; no new Gazebo validation.',
      'fit':'Nominal M2x12/nuts only. Exact supplier, thread/recess, tolerances and physical fit not verified.',
      'petg':'Fits 256 cubed nominally. Wall/rim audit, slicer, supports, nozzle/layer settings and coupons remain unapproved.',
      'loads':'PETG layer strength, ear impact, clamp torque and creep not tested.',
      'electrical':'Earlier electronics and harness/thermal integration gates remain open.',
      'service':'Sampled nut insertion / nominal driver paths clear. Physical tool, cable and assembled-head servicing not approved.'}
    result=dict(schema_version=1,name='robot-cat-rounded-ears-e1',readiness='prototype',installed_in_robot=True,
                entry=task.TARGET.relative_to(pilot.ROOT).as_posix(),freecad='1.1.3',occt='7.8.1',freecad_ai='0.23.1-alpha',
                checks=dict(components=335,fixed=321,revolute=13,temporary=25,linked_parts=65,documents=11,native_frames=22),
                files=[dict(path=p.relative_to(pilot.ROOT).as_posix(),sha256=sha256(p)) for p in dict.fromkeys(paths)],
                gates={n:dict(status='fail' if n=='geometry' else 'open',reason=r) for n,r in reasons.items()})
    assert verify(pilot.ROOT,result)['integrity_ok'] and not verify(pilot.ROOT,result,True)['integrity_ok']
    (pilot.ROOT/'hardware/releases/ears-e1.json').write_text(json.dumps(result,indent=2),encoding='utf-8',newline='\n')
    print(verify(pilot.ROOT,result))

if __name__=='__main__':main()
