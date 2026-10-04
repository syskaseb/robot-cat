"""Receive R5 as one shared family without repeating R4 geometry."""
from pathlib import Path
import json
import w5_s1_source_check_r4 as receiver
from servo_fuse_inputs_r1 import save,sha
ROOT=receiver.ROOT
OUT=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r5'

def main():
    receiver.OUT=OUT
    receiver.INTENT=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r5/intent.json'
    receiver.main()
    p=OUT/'checks.json';r=json.loads(p.read_text(encoding='utf-8'))
    r['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    r['new_cover_required']=True
    save(p,r)

if __name__=='__main__':main()
