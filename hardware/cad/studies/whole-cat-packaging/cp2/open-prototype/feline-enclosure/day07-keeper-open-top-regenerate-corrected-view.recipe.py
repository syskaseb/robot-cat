from pathlib import Path
import json,hashlib,html
from PIL import Image,ImageDraw
out=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');temp=Path('C:/Users/Sysq/AppData/Local/Temp')
s=json.loads((out/'day07-D5-real-keeper-open-top-actual-sections-and-source-witness.json').read_bytes());v=json.loads((out/'day07-D5-open-top-XZ-actual-section-plane-range-correction.json').read_bytes());s['sections']=[q for q in s['sections'] if q['view']!='XZ_Yminus23p375']+v['sections'];names=[]
src=(temp/'robot-cat89-package-real-keeper-entry.py').read_text(encoding='utf-8-sig');code=src[src.index('im=Image.new'):src.index('for src in [')].replace('assert not png.exists();','');exec(code)
print(str(png),hashlib.sha256(png.read_bytes()).hexdigest())
