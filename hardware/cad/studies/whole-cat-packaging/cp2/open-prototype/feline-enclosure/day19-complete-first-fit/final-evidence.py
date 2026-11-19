from common import *
import zipfile,shutil
from xml.etree import ElementTree as ET
def streams(z):
 root=ET.fromstring(z.read('Document.xml'))
 return {o.get('name'):hashlib.sha256(z.read(a.get('file'))).hexdigest() for o in root.findall('./ObjectData/Object') if (a:=o.find('./Properties/Property[@name="Shape"]/Part')) is not None and a.get('file')}
with zipfile.ZipFile(native) as z,zipfile.ZipFile(P/'printed-tested.FCBak') as t:
 assert z.testzip() is None;now=streams(z);old=streams(t);assert set(now)==set(old);delta=[k for k in now if now[k]!=old[k]]
 assert delta==['H19_Wires_battery'],delta
 idx=rd(P/'material-index.json');assert idx['native_sha256']==sha(P/'printed-tested.FCBak')
 wr('export-identity.json',dict(print_geometry_source=idx['native_sha256'],final_native=sha(native),same_BRep=len(now)-1,changed=delta,reason='display four current pack and fixed supply approaches; changed actor is illustrative, not print material',final_print_parts=len(idx['parts']),fixed_W075_evidence='battery-lower-fit.json'))
shutil.copyfile(native,P/'geometry-tested.FCBak')
