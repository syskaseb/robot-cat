from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
import hashlib,json,shutil
P=Path(__file__).parent
C=P.parent/"day19-closed-head-neck-and-module-interfaces"
source=C/"whole-cat19C.FCStd";backup=P/"preserved-unsaved-19C.FCStd";dst=P/"whole-cat19D.FCStd"
def hashes(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def state(p):
    with ZipFile(p) as z:
        assert z.testzip() is None
        x=E.fromstring(z.read("Document.xml"));g=E.fromstring(z.read("GuiDocument.xml"))
        obs=x.findall("./ObjectData/Object");geo={};props={}
        for o in obs:
            part=o.find("./Properties/Property[@name='Shape']/Part");name=o.get("name")
            if part is not None:geo[name]=hashlib.sha256(z.read(part.get("file"))).hexdigest()
            props[name]=E.tostring(o.find("Properties"))
        return geo,props,hashlib.sha256(z.read("GuiDocument.xml")).hexdigest(),len(obs)
src,pr,v,k=state(source);bak,br,w,n=state(backup);assert n==k==443 and src.keys()==bak.keys()
changed=[i for i in src if bak[i]!=src[i]]
r=dict(source_sha=hashes(source),preserved_sha=hashes(backup),object_count=n,changed_brep_streams=changed,changed_object_properties=[i for i in pr if pr[i]!=br[i]],gui_xml_identical=v==w)
assert r["source_sha"]=="e82c2658ddf204fe2c120e8951af51981846d9d9c5925876a71d649b6b13f403"
assert not dst.exists();shutil.copyfile(source,dst);assert hashes(dst)==r["source_sha"]
(P/"reconciliation.json").write_bytes((json.dumps(r,indent=1)+"\n").encode())
print({**r,"changed_brep_streams":len(changed),"changed_object_properties":len(r["changed_object_properties"])})

