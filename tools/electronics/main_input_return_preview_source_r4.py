"""Refresh only the changed Deck preview from the final saved native source."""
import json
from pathlib import Path
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/main-input-return-finish-r3'
CAD=ROOT/'hardware/cad/studies/main-input-return-finish-r3'

def main():
    source=CAD/'DeckMainInput.FCStd'
    data=json.loads((OUT/'preview-geometry.json').read_text(encoding='utf-8'))
    doc=A.openDocument(str(source));name=doc.Name
    try:
        assert abs(doc.MainInputParameters.GrooveRadius.Value-1.8)<1e-6
        shapes={n:doc.getObject(n).Shape.copy() for n in ('G1InputSeat','InputPortalSeat')}
        deck=Part.Shape();deck.read(str(CAD/'Deck_WORLD.brep'));shapes['Deck']=deck
    finally:
        A.closeDocument(name)
    for row in data:
        if row['name'] in shapes:
            vs,ts=shapes[row['name']].tessellate(.4)
            row.update(vertices=[list(v) for v in vs],triangles=ts)
    assert all(any(r['name']==n for r in data) for n in shapes)
    (OUT/'preview-geometry.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Final native Deck and two changed seats included in preview.')

if __name__=='__main__':main()
