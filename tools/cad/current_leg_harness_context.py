"""Pinned leg-candidate overlay on the retained body-source scene."""
import json
from pathlib import Path
from current_body_harness_context import context as body_context,W,Part,ROOT,OUT,BASE

def context():
    pfile=OUT/'leg-stations-plan.json';gfile=OUT/'leg-stations-checks.json'
    p=json.loads(pfile.read_text());g=json.loads(gfile.read_text())
    assert g['status']=='LEG_STATIONS_AND_MAIN_OUTPUT_SPACE_ONLY_FANS_NATIVE_OPEN'
    assert not g['contacts'] and not g['errors']
    for n,h in {**p['source_sha256'],**g['source_sha256']}.items():assert W.sha(ROOT/n)==h,n
    reader,pins,targets,retained=body_context();pins.update((Path(__file__),pfile,gfile))
    spfile=OUT/'source-receiving-plan.json';sp=json.loads(spfile.read_text());pins.add(spfile)
    targets.update({'P_SYS_new':W.box(sp['P_SYS']['casing_mm']),
      'F_PI_new':W.box(sp['F_PI']['casing_mm']),'F_PI_sleeve':W.box(sp['F_PI']['output_sleeve_mm'])})
    targets.update({n:W.box(s['casing_mm']) for n,s in p['stations'].items()})
    for n,v in {**sp['routes'],**sp['factory_routes'],**p['routes']}.items():retained[n]=(W.makewire(v['parts']),v['radius_mm'])
    o=p.get('factory_override')
    if o:
        j=o['joint'];s=W.box(j['local_casing_mm'])
        s.Placement=W.A.Placement(W.A.Vector(*j['factory_entry_mm']),W.A.Rotation(W.A.Vector(1,0,0),j['rotation_x_degrees']))
        assert s.isValid() and len(s.Solids)==1
        targets['W026_Joint']=s;retained['W026_FACTORY']=(W.makewire(o['parts']),o['radius_mm'])
    return reader,pins,targets,retained
