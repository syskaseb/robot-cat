"""Shared check of four source wires plus reopened short XA01, no waiver."""
from pathlib import Path
import json
from servo_fuse_inputs_r1 import save,sha
ROOT=Path(__file__).resolve().parents[2]
receiver=ROOT/'tools/electronics/w5_s1_source_check_r4.py'
source=receiver.read_text(encoding='utf-8')
source=source.replace("w5-s1-source-check-r4'","w5-s1-source-check-r6'")
source=source.replace("w5-s1-source-layout-r4/intent.json'","w5-s1-source-layout-r6/intent.json'")
start=source.index("        centre=intent['S1_ring_seat_centres'][row['b']]")
end=source.index('        pieces=[];edges=[]',start)
block=source[start:end]
source=source[:start]+"        if row['b'].startswith('S1'):\n"+''.join('    '+line+'\n' for line in block.rstrip().splitlines())+source[end:]
source=source.replace("    begin=datetime.now(timezone.utc)","    begin=datetime.now(timezone.utc)")
namespace=dict(__file__=str(Path(__file__).resolve()),__name__='r6_receiver')
exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)

def main():
    namespace['main']()
    out=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r6'
    path=out/'checks.json';record=json.loads(path.read_text(encoding='utf-8'))
    record['source_sha256'][receiver.relative_to(ROOT).as_posix()]=sha(receiver)
    record['five_routes_include_reopened_XA01']=True
    record['new_cover_required']=True
    save(path,record)

if __name__=='__main__':main()
