"""Reopen the delivered FCStd and verify the persisted new objects and view."""
import json,zipfile,hashlib,xml.etree.ElementTree as ET
import FreeCAD as App
from brep_inventory import OUT

def main():
    path=OUT/'Kot_v18_SKORUPA_DZIELONA.FCStd'
    report=json.loads((OUT/'shell-validation.json').read_text(encoding='utf-8'))
    tray=json.loads((OUT/'tray-validation.json').read_text(encoding='utf-8'))['parts'][0]
    doc=App.openDocument(str(path))
    checked=[]
    for p in report['parts']+[tray]:
        obj=doc.getObject(p['name'])
        assert obj is not None and not obj.Shape.isNull(),p['name']
        assert obj.Shape.isValid() and len(obj.Shape.Solids)==1,p['name']
        assert abs(obj.Shape.Volume-p['volume_mm3'])<0.001,p['name']
        checked.append(p['name'])
    assert all(doc.getObject(p['name']) is not None for p in report['hardware'])
    with zipfile.ZipFile(path) as z:
        root=ET.fromstring(z.read('GuiDocument.xml'))
    visibility={}
    for vp in root.findall('.//ViewProvider'):
        prop=vp.find(".//Property[@name='Visibility']/Bool")
        if prop is not None: visibility[vp.get('name')]=prop.get('value')=='true'
    for n in ('ShellFront18','ShellRear18','ShellJoinL','ShellJoinR','PiTray18'):
        assert visibility[n],(n,'not visible')
    for n in ('BackCover','BackCover18','ComputerDeck'):
        assert not visibility[n],(n,'legacy part visible')
    result=dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                reopened=True,valid_single_solids=checked,hardware_objects=8,
                saved_view='whole cat, both shell halves visible, legacy shell hidden')
    (OUT/'saved-document-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result),flush=True)

if __name__=='__main__':
    main()
