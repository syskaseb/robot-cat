from common import *
import zipfile,re,io,csv,posixpath
from urllib.parse import unquote
import trimesh
zpath=P/'19I-WAVEGO-first-fit.zip';manifest=rd(P/'verified-19I.json')
with zipfile.ZipFile(zpath) as z:
 names=set(z.namelist());assert len(names)==len(z.namelist())==manifest['archive_CRC_checked_entries'] and z.testzip() is None
 for document in ['START_HERE.md','MONTAZ.md','ELECTRICAL_ASSEMBLY.md']:
    for link in re.findall(r'\]\(([^)]+)\)',z.read(document).decode()):
        if link.startswith(('http:','https:','#')):continue
        key=posixpath.normpath(unquote(link.split('#')[0]));assert key in names,(document,key)
 ix=json.loads(z.read('material-index.json'));listing=list(csv.DictReader(io.StringIO(z.read('PRINT.csv').decode('utf-8-sig'))))
 assert len(listing)==len(ix['parts']);assert sum(int(v['szt.']) for v in listing)==sum(q['qty'] for q in ix['parts'])
 for q in ix['parts']+[ix['off_robot']]:
    b=z.read(q['stl']);assert hashlib.sha256(b).hexdigest()==q['sha256'];m=trimesh.load_mesh(io.BytesIO(b),file_type='stl');assert m.is_watertight and m.is_volume,q['part']
    assert max(q['envelope_with_allowance'])<=256,q['part']
 assert hashlib.sha256(z.read(native.name)).hexdigest()==manifest['native']['final_sha256']
print('transfer OK',len(names),sum(int(v['szt.']) for v in listing),sha(zpath))
