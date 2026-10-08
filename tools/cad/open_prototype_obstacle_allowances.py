"""Add only omitted component-height/reference volumes to received sections.

No repeat of the402-part map, no new route variant. Nominal complete-board
allowances are deliberately not described as actual component collision proof.
"""
from datetime import datetime, timezone
from pathlib import Path
import html, json, time
from open_prototype_obstacle_sections import OUT, CONTEXT, COLORS
from open_prototype_wiring_endpoints import ROOT, read, sha, bounds

SOURCE=OUT/'obstacle-sections.json'
DEST=OUT/'obstacle-map-current.json'
VIEW=OUT/'obstacle-map-current.html'
NAMES=['Pi4_CP2','PWM9685_CP2','AUX4092_CP2','PWM1608_CP2',
       'BUS_CP2','Monitor_CP2','F0_CP2','Splice_L1_CP2','PostF0Splice_CP2']


def main():
    import FreeCAD as A
    assert not DEST.exists() and not VIEW.exists(),'Receive current map; no unchanged rerun'
    tick=time.monotonic();r=read(SOURCE)
    assert not r['errors'] and r['bank_reference_count']==48
    for n,h in r['source_sha256'].items():assert sha(ROOT/n)==h,n
    r['source_sha256'].update({p.relative_to(ROOT).as_posix():sha(p) for p in (SOURCE,Path(__file__))})
    d=A.openDocument(str(CONTEXT));panels=[];added_contours=0
    try:
        for name in NAMES:
            s=d.getObject(name).Shape
            assert s.isValid() and s.Solids,name
            r['objects'].append(dict(name=name,kind='delivery_reservation',
                basis='Canonical whole-component/reference envelope, includes height beyond bare PCB; no supplier pinout or actual component collision claim',
                bounds_mm=[round(x,4) for x in bounds(s)]))
        for section in r['sections']:
            z=section['z_mm']
            for name in NAMES:
                s=d.getObject(name).Shape
                if not s.BoundBox.ZMin<z<s.BoundBox.ZMax:continue
                for w in s.slice(A.Vector(0,0,1),z):
                    xy=[[round(p.x,3),round(p.y,3)] for p in w.discretize(Deflection=.25)]
                    if len(xy)>1:
                        section['contours'].append(dict(part=name,kind='delivery_reservation',xy_mm=xy));added_contours+=1
            svg=[]
            for c in section['contours']:
                pts=' '.join(f'{x},{-y}' for x,y in c['xy_mm'])
                color='#111827' if c['part']=='TorsoEnvelope' else COLORS[c['kind']]
                svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width=".8"><title>{html.escape(c["part"])}</title></polyline>')
            panels.append(f'<section><h2>Z {z:g} mm</h2><svg viewBox="-120 -106 325 212">'+''.join(svg)+'</svg></section>')
        r['status']='CURRENT_OBSTACLE_AND_COMPONENT_ALLOWANCE_MAP_NOT_ROUTE_ACCEPTANCE'
        r['scope_additions']+=['9whole component/source reference envelopes; no bare-PCB-only clearance claim']
        r['scope_limitations']+=['R47 design retained but mounting/placement qualification in CP2 remains OPEN',
            '12 old Access_F_L/F_R reservations are obsolete service concepts, not a qualified current bank service sequence',
            'Bank printed replacement/mount and all moving/connected service envelopes still require current qualification',
            'Overlaps with purple reference budgets are planning constraints, not proof of delivered-part contact']
        r['incremental_allowances']=dict(objects=len(NAMES),added_contours=added_contours,
            reused_objects=len(r['objects'])-len(NAMES),no_repeated_prior_geometry_sections=True)
        VIEW.write_text('<!doctype html><meta charset="utf-8"><title>Robot-cat: wspólny model przestrzeni</title><style>body{font:15px system-ui;background:#f8fafc;color:#172033;margin:22px}main{display:grid;grid-template-columns:repeat(2,minmax(320px,1fr));gap:16px}section{background:white;border:1px solid #ddd;padding:10px}svg{width:100%;height:auto}h2{margin:4px}</style><h1>Wspólny model przeszkód i rezerwacji, etap3</h1><p>Szare: zachowane bryły. Pomarańczowe: podpory do uzgodnienia. Czerwone: ODRZUCONY układ stanowisk. Niebieskie: narzędzia. Fioletowe: rezerwacje całych płytek/modułów, nie tylko PCB; nie dowodzą kontaktu dostarczonych części. Jednostki mm, X poziomo, +Y do góry. Tułów325×200×160 bez poszerzania. Przekroje NIE kwalifikują ciągłej trasy, odciążeń, ruchu ani fizycznego PASS.</p><main>'+''.join(panels)+'</main>',encoding='utf-8')
    finally:A.closeDocument(d.Name)
    r.update(incremental_worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
    DEST.write_text(json.dumps(r,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    assert all(sha(ROOT/n)==h for n,h in r['source_sha256'].items())
    print(json.dumps(dict(objects=len(r['objects']),added_contours=added_contours,seconds=r['incremental_worker_seconds'])),flush=True)


if __name__=='__main__':main()
