"""Reuse unchanged tested pad geometry after changing only the torso envelope."""
import hashlib
import io
import json
import subprocess
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, SavedShapes, prop, sha
from plan_feline_layout import OUT


def main():
    tick=time.monotonic();report_path=OUT/'leg-body-path.json'
    report=json.loads(report_path.read_text());native=OUT/'FelineLayoutEnvelope.FCStd'
    rel=native.relative_to(ROOT).as_posix()
    assert report['status']=='SAMPLED_EXTERNAL_LEG_PAD_PATH_CLEAR_SUPPLIER_JOINTS_WIRING_SHELL_OPEN'
    assert len(report['poses'])==36 and not report['new_contacts'] and not report['errors']
    old_bytes=subprocess.check_output(['git','show',f'a458642:{rel}'],cwd=ROOT)
    assert hashlib.sha256(old_bytes).hexdigest()==report['source_sha256'][rel]
    assert all(sha(ROOT/n)==h for n,h in report['source_sha256'].items() if n!=rel)
    reader=SavedShapes();rows=[]
    with zipfile.ZipFile(io.BytesIO(old_bytes)) as z:
        xml=ET.fromstring(z.read('Document.xml'))
        objects={o.get('name'):o for o in xml.findall('./ObjectData/Object')}
        for i in range(1,5):
            n=f'BellyPadReservation{i}'
            old=Part.Shape();old.importBrepFromString(z.read(prop(objects[n],'Shape')[0].get('file')).decode('utf-8'))
            new=reader.shape(native,n)
            old_text=old.exportBrepToString().encode();new_text=new.exportBrepToString().encode()
            assert old_text==new_text,n
            assert old.isValid() and new.isValid() and len(new.Solids)==1,n
            rows.append(dict(object=n,old_and_new_BRep_sha256=hashlib.sha256(old_text).hexdigest(),
                volume_mm3=new.Volume,center_mm=list(new.Solids[0].CenterOfMass)))
    result=dict(status='UNCHANGED_FOUR_PAD_BREPS_PROVE_REUSE_OF_SAMPLED_LEG_P0_PAD_RESULT',
        physical_pass=False,continuous_sweep_verified=False,new_torso_skin_covered=False,
        original_native_git_commit='a458642',original_native_sha256=hashlib.sha256(old_bytes).hexdigest(),
        updated_native_sha256=sha(native),motion_report=report_path.relative_to(ROOT).as_posix(),
        motion_report_sha256=sha(report_path),unchanged_tested_parts=rows,
        poses_reused=36,exact_pairs_reused=report['pairs'],all_other_original_inputs_unchanged=True,
        source_sha256={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'motion-pad-reuse.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(result['status'],result['worker_seconds'])


if __name__=='__main__':main()
