"""Receive one shared five-route check against all unchanged installed owners."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
receiver=ROOT/'tools/electronics/w5_s1_source_check_r4.py'
source=receiver.read_text(encoding='utf-8').replace('check-r4','check-r7').replace('layout-r4','layout-r7')
start=source.index("        centre=intent['S1_ring_seat_centres'][row['b']]")
end=source.index('        pieces=[];edges=[]',start)
block=source[start:end]
source=source[:start]+"        if row['b'].startswith('S1'):\n"+''.join('    '+line+'\n' for line in block.rstrip().splitlines())+source[end:]
source=source.replace('    # Drawing-bounded reserved casing', '''    carrier_receipt=ROOT/'hardware/electronics/full-cat/w5-source-carrier-native-r1/checks.json'
    carrier=json.loads(carrier_receipt.read_text(encoding='utf-8'))
    assert carrier['status']=='FOUR_SOURCE_CARRIER_PASSAGES_LOCAL_COMPLETE_UNSELECTED' and not carrier['hits']
    assert all(sha(ROOT/k)==v for k,v in {**carrier['source_sha256'],**carrier['files']}.items())
    old_carrier='hardware/cad/studies/pi-complete-native-r2/Carrier_WORLD.brep'
    assert old_carrier in owners
    owners.pop(old_carrier)
    carrier_path=ROOT/'hardware/cad/studies/w5-source-carrier-native-r1/Carrier_WORLD.brep'
    owners['SourceCarrier_native']=Part.read(str(carrier_path));pins += [carrier_path,carrier_receipt]
    # Drawing-bounded reserved casing''')
namespace=dict(__file__=str(Path(__file__).resolve()),__name__='r7_receiver')
exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)
if __name__=='__main__':
    namespace['main']()
    from servo_fuse_inputs_r1 import save,sha
    import json
    p=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r7/checks.json'
    r=json.loads(p.read_text(encoding='utf-8'));r['source_sha256'][receiver.relative_to(ROOT).as_posix()]=sha(receiver)
    r.update(five_routes_include_reopened_XA01=True,received_native_carrier_passages=True,new_cover_required=True)
    save(p,r)
