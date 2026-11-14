from pathlib import Path
import zipfile,xml.etree.ElementTree as E,json,hashlib
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit/fit-kit-ready');source=P.parent/'foundation-fit-kit/foundation-assembly.FCStd';b=source.read_bytes();assert hashlib.sha256(b).hexdigest()=='c8366ff726740d8220fd5ecbc94685c43154dcb969ab3571a7f2fa8eb2294c59'
z=zipfile.ZipFile(source);root=E.fromstring(z.read('Document.xml'));r=[]
for o in root.findall('.//ObjectData/Object'):
 if o.get('name') not in ['Upper_frame_rail_44','Upper_frame_rail__49']:continue
 prop=o.find("./Properties/Property[@name='Shape']");member=prop.find('Part').get('file');data=z.read(member);dest=P/(o.get('name')+'-frozen-source.brep');dest.write_bytes(data);r.append(dict(object=o.get('name'),source=str(source),source_sha256=hashlib.sha256(b).hexdigest(),member=member,member_sha256=hashlib.sha256(data).hexdigest(),local=str(dest)))
(P/'frozen-rail-binding.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(r))
