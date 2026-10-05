"""Joint north-side central distribution instead of trapped central returns.

G1 is near the battery datum, G2 faces it across49.5mm. This reopens BOTH
factory source leads and the bridge; the 150/300mm budgets are mandatory.
All prior native central mounts become pending replacement interfaces.
"""
from pathlib import Path
import json
import w5_coupled_corridors_r3 as prior
from w5_central_ground_routes_r2 import recipes as received_central

ROOT=prior.base.ROOT
def contract():
    bodies,rows,preserved,pins=prior.contract()
    delta={'G1':[-16,89.5,0],'G2':[9,89.5,0]}
    for row in rows:
        for side in ('a','b'):
            name=row[side+'_end'].split('.')[0]
            if name in delta and side+'_datum' in row:
                d=delta[name];p=row[side+'_datum']['point_mm']
                row[side+'_datum']=dict(row[side+'_datum'],point_mm=[v+x for v,x in zip(p,d)])
    bodies['G1']=[39,76.5,109,61,113.5,120]
    bodies['G2']=[110.5,80,109,129.5,110,118]
    datums=prior.base.ground_ports()
    central=received_central()
    bus_path=ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
    bus=json.loads(bus_path.read_text(encoding='utf-8'))['source_lead_datums']
    leads=[]
    for wire,end,target in [('W001','G1.1',next(r for r in central if r['wire']=='W001')['middle'][0]),
                            ('W003','G2.4',bus['W003'])]:
        d=delta[end.split('.')[0]];p=datums[end]['point_mm']
        datum=dict(datums[end],point_mm=[v+x for v,x in zip(p,d)])
        leads.append(dict(wire=wire,a_end=end,b_end='BAT.minus' if wire=='W001' else 'BUS.G',a_datum=datum,
            target=target,lead_in=True,radius_mm=prior.base.spec(wire)['radius_mm']))
    rows=leads+rows
    preserved=[w for w in preserved if w not in ('W001','W003','W061')]
    assert len(rows)==36 and len(preserved)==12  # plus separately checked NEW W061
    pins += [Path(__file__),Path(prior.__file__),ROOT/'tools/electronics/w5_central_ground_routes_r2.py',
             ROOT/'tools/electronics/w5_central_ground_routes.py']
    return bodies,rows,preserved,pins


source=prior.source
needle='    fixed,source_pins=owners(A,Part,json.loads(RECEIVED.read_text(encoding=\'utf-8\'))); pins+=source_pins'
assert needle in source
source=source.replace(needle,'''    reuse_folder=ROOT/'hardware/electronics/full-cat/w5-coupled-corridors-r3'
    reuse_receipt=json.loads((reuse_folder/'checks.json').read_text(encoding='utf-8'))
    assert not reuse_receipt['errors'] and not reuse_receipt['body_hits']
    core={'W001','W003','W025','W036','W062','W063','XA05','W060'}
    reusable={r['wire']:r for r in reuse_receipt['accepted'] if r['wire'] not in core}
    deferred=[r for r in rows if r['wire'] not in core and r['wire'] not in reusable]
    rows=[r for r in rows if r['wire'] in core]
    pins.append(reuse_folder/'checks.json')
'''+needle)
start=source.index("    central=ROOT/'hardware/electronics/full-cat/w5-central-ground-routes-r2'")
end=source.index('    printed=',start)
source=source[:start]+'''    # This new bridge belongs to the new pair, not the preserved old24.5mm span.
    edge=Part.makeLine(A.Vector(61,95,113.5),A.Vector(110.5,95,113.5))
    section=Part.Wire([Part.makeCircle(2.1,A.Vector(61,95,113.5),A.Vector(1,0,0))])
    fixed['W061']=Part.Wire([edge]).makePipeShell([section],True,False)
    bridge_path=OUT/'W061_WORLD.brep';fixed['W061'].exportBrep(str(bridge_path))
    pins.append(bridge_path)
    for wire in reusable:
        p=reuse_folder/(wire+'_WORLD.brep');fixed[wire]=Part.read(str(p));pins.append(p)
'''+source[end:]
needle="    save(OUT/'intent.json',dict(bodies=bodies,routes=rows,preserved=preserved,scope_count=49,"
assert needle in source
source=source.replace(needle,"    bridge_hit=contact(fixed['W061'],skip=('W061',))\n    if bridge_hit:body_hits.append(dict(body='NEW_W061_BRIDGE',owner=bridge_hit))\n"+needle)
source=source.replace("body_hits=body_hits,printed_rework_owners", "body_hits=body_hits,new_bridge_mm=49.5,new_bridge_contact=bridge_hit,printed_rework_owners")
source=source.replace("preserved=preserved,errors=errors", "preserved=preserved,new_bridge_mm=49.5,new_bridge_contact=bridge_hit,errors=errors")
source=source.replace("preserved=preserved,scope_count=49", "preserved=preserved,reused=list(reusable),deferred_unchanged=deferred,scope_count=49")
source=source.replace("preserved=preserved,new_bridge_mm", "preserved=preserved,reused=list(reusable),deferred_unchanged=deferred,new_bridge_mm")
source=source.replace("            if row['wire']=='W002' and path.Length+11+30>300:",
    "            if row['wire']=='W001' and path.Length+19>150:\n                rejected['source150mm_budget']+=1;continue\n            if row['wire'] in ('W002','W003') and path.Length+11+30>300:")
# Include the lowest bend-feasible plane, not only arbitrary tall flights.
source=source.replace("            for h in (202,214,226,238,250):", "            for h in sorted(set([max(p[2],q[2])+r+1.1,170,190,202,214,226,238,250])):")
ctx=dict(__name__='coupled_r4_definition',__file__=prior.base.__file__)
exec(compile(source,prior.base.__file__,'exec'),ctx)
ctx['contract']=contract
ctx['OUT']=ROOT/'hardware/electronics/full-cat/w5-coupled-corridors-r4'
if __name__=='__main__':ctx['main']()
