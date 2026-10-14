"""Configured complete oblique source-space gate, without duplicate engine."""
import json
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_low_hip_shared_space import P,run
from oblique_source_fans import fan


def candidate():
    pf=P.OUT/'body-oblique-source-ports.json';mf=P.OUT/'body-oblique-port-motion-chosen-plan.json'
    ports,motion=[json.loads(f.read_text()) for f in (pf,mf)]
    for data in (ports,motion):
        for n,h in data['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    archive=P.ROOT/ports['archive'];assert P.SHA(archive)==ports['archive_sha256'];shapes={}
    with zipfile.ZipFile(archive) as z:
        for row in json.loads(z.read('index.json')):
            s=Part.Shape();s.importBrepFromString(z.read(row['file']).decode());assert s.isValid() and len(s.Solids)==1
            shapes[row['name']]=s
    return ports,motion,shapes,(pf,mf,archive,Path(__file__),Path(__file__).with_name('oblique_source_fans.py'))


if __name__=='__main__':
    run(candidate_loader=candidate,report_name='body-oblique-source-space.json',cache_name='oblique-source-pairs.json',source_fan_function=fan)
