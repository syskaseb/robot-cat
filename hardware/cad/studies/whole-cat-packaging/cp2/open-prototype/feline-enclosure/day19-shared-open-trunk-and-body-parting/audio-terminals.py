"""Read only the output and mounting features from Adafruit's selected 3006 mono Eagle design."""
from common import *
import xml.etree.ElementTree as X,urllib.request,urllib.parse
base='https://api.github.com/repos/adafruit/Adafruit-MAX98357-I2S-Amp-Breakout/contents/'
name='Adafruit MAX98357 Breakout.brd';meta=json.load(urllib.request.urlopen(base+urllib.parse.quote(name),timeout=10));raw=urllib.request.urlopen(meta['download_url'],timeout=10).read();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==meta['sha']
q=X.fromstring(raw);board=q.find('./drawing/board');elems={a.get('name'):dict(a.attrib) for a in board.findall('./elements/element')}
out=dict(url=meta['html_url'],blob=meta['sha'],sha256=hashlib.sha256(raw).hexdigest(),source_name=name,holes=[h.attrib for h in board.findall('./plain/hole')],dimensions=[w.attrib for w in board.findall('./plain/wire') if w.get('layer')=='20'],terminals={})
for sig in board.findall('./signals/signal'):
 for pad in sig.findall('./contactref'):
    el=elems[pad.get('element')];pkg=el['package']
    if not any(k in pkg.upper() for k in ['TERM','1X02','3.5','MOUNT','3.50']):continue
    pkgref=board.find("./libraries/library[@name='%s']/packages/package[@name='%s']"%(el['library'],pkg))
    out['terminals'][pad.get('element')+'.'+pad.get('pad')]=dict(net=sig.get('name'),element=el,pads=[q.attrib for q in pkgref.findall('pad')],outline=[q.attrib for q in pkgref.findall('wire') if q.get('layer')=='21'])
out['mechanical_elements']=[v for v in elems.values() if any(k in (v['package']+' '+v['name']).upper() for k in ['MOUNT','HOLE','FID','SCREW'])]
wr('audio-source.json',out);print(out['holes'],out['mechanical_elements']);print([(k,v['net'],v['element']['package']) for k,v in out['terminals'].items()])
