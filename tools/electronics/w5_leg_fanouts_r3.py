"""Raise D/G before the existing inner data bridges, without smaller bends.

Six mm of straight D entry precedes the first R10 turn. An endpoint
has one corner, not two; use exact adjacent-offset checks rather than moving
the turn past already occupied inner bridge lanes. G lifts on a separate
inner lane. The triangle points V outward so its first turn cannot cross D/G
risers. Keep the OD5.5 moving corridors, not the changed V body continuations.
"""
from pathlib import Path
import runpy
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))

definition=runpy.run_path(str(Path(__file__).with_name('w5_leg_fanouts_r2.py')),
                         run_name='r2_definitions_only')
M=definition['M']
source=definition['source']


def replace_once(old,new):
    global source
    assert source.count(old)==1,old
    source=source.replace(old,new)


replace_once("w5-leg-fanouts-r2'","w5-leg-fanouts-r3'")
replace_once('lane=side*5.5',"lane=side*(14.5 if role=='D' else 18.5)")
replace_once("tail=[breakout[0]+dx,breakout[1]+dy,breakout[2]]", """# 1.45mm centre radius leaves0.11mm nominal core-to-core space;
            # complete cross-section OD5.3 remains inside the OD5.5 corridor.
            dx,dy={'D':[-math.sqrt(3)*1.45/2,-side*.725],
                   'G':[math.sqrt(3)*1.45/2,-side*.725],
                   'V':[0,side*1.45]}[role]
            tail=[breakout[0]+dx,breakout[1]+dy,breakout[2]]""")
start=source.index("        if row['role']=='V':\n            previous,shape,path=inherited[row['wire']]")
end=source.index('        try:\n            path=fillet_path',start)
source=source[:start]+source[end:]
replace_once("            if built[i]['role']=='V' and built[j]['role']=='V':continue\n",'')
replace_once("if info['role']!='V' and info['loom']!=row['loom']:","if info['loom']!=row['loom']:")
replace_once("inherited_unchanged='Twelve V body paths, OD5.5 bundle owner checks and bundle-to-bundle checks from R1'",
             "inherited_unchanged='Only OD5.5 moving corridor owner and mutual checks from R1; all36 body core branches changed'")
replace_once('from w5_leg_corridors_r1 import fillet_path',
             'from w5_rounded_path import rounded as fillet_path')
replace_once('    started=datetime.now(timezone.utc)', '''    started=datetime.now(timezone.utc)
    rejected_path=ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r2/checks.json'
    rejected=json.loads(rejected_path.read_text(encoding='utf-8'))
    assert rejected['status']=='COUPLED_LEG_FANOUT_REJECTED'
    assert rejected['hits'] and not rejected['errors'] and len(rejected['routes'])==36
    assert all(sha(ROOT/k)==v for k,v in {**rejected['source_sha256'],**rejected['files']}.items())''')
replace_once('    owners,cache=cached()', '''    owners,cache=cached()
    chosen_carrier=next(p for p in selected['prints'] if p['identity']=='electronics:Carrier service ports')
    assert chosen_carrier['stl']=='hardware/cad/studies/pi-complete-native-r2/Carrier_x1.stl'
    assert sha(ROOT/chosen_carrier['stl'])==chosen_carrier['sha256']
    # These are older recipes for the SAME cassette carrier, not four extra
    # printed/installed parts. Keep its sole chosen Pi-native world geometry.
    omitted_carrier_aliases=[
        'hardware/electronics/full-cat/tail-ground-direct-r1/CarrierTailPWMEntry_DESIGN.brep',
        'hardware/electronics/full-cat/tail-central-routes-r3/CarrierTailPWMEntry_DESIGN.brep',
        'hardware/electronics/full-cat/head-connected-feeds-r8/CarrierPWMEntry_DESIGN.brep',
        'hardware/electronics/full-cat/aux-converter-routes-r5/Carrier_TWO_PORTS_DIAGNOSTIC.brep']
    for key in omitted_carrier_aliases:del owners[key]
    assert 'hardware/cad/studies/pi-complete-native-r2/Carrier_WORLD.brep' in owners''')
replace_once('    pins += [Path(M.__file__),prior_folder/\'checks.json\',',
             "    pins += [rejected_path,ROOT/'tools/electronics/w5_leg_fanouts_r2.py',ROOT/'tools/electronics/w5_rounded_path.py']\n    pins += [Path(M.__file__),prior_folder/'checks.json',")
replace_once("    save(OUT/'checks.json',dict(inherited_unchanged=",
             "    pins += [ROOT/chosen_carrier['stl']]\n    save(OUT/'checks.json',dict(omitted_retired_carrier_aliases=omitted_carrier_aliases,inherited_unchanged=")
exec(compile(source,str(Path(__file__).resolve()),'exec'))
