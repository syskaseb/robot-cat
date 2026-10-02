"""Move the descent0.5mm west of W012's nominal insulated envelope.

R3 identified W012 X135 at crossing height; OD allowances need >2.1mm
centre spacing. X132.5 gives2.5mm while retaining the rear support gap.
This is not a remap/re-route of the already selected DATA wire.
"""
from pathlib import Path
import json
import main_input_return_r3 as M

M.OUT=M.ROOT/'hardware/electronics/full-cat/main-input-return-r4'
M.POLES=[[132.5,0,95],[132.5,0,95-30.4252/3],M.POLES[2],M.POLES[3]]
M.POINTS=[p if p[0]!=133 else [132.5,p[1],p[2]] for p in M.POINTS]

def main():
    M.main()
    import body_ground_routes_r1 as B
    p=M.OUT/'checks.json';c=json.loads(p.read_text(encoding='utf-8'))
    c['datum_builder_sha256']=B.sha(Path(__file__))
    c['corridor_change']='X132.5 preserves DATA/W012; nominal centre spacing2.5mm versus radii1.5+.6'
    B.save(p,c)

if __name__=='__main__':main()
