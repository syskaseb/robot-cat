"""Receive ONE shared outboard/underside layout after the complete R1 map.

The electronics layer is occupied, not a place for four more feet. Put the
feet beneath integral outboard ledges and the posts/rails outside S1, source
feeds, G_AUX and bank walls. Keep all twelve cable split axes unchanged.
"""
from pathlib import Path
import json
from servo_fuse_inputs_r1 import sha
from w5_loom_common_layout import ROOT,OUT as PRIOR


def main():
    proof=PRIOR/'checks.json';r=json.loads(proof.read_text(encoding='utf-8'))
    assert len(r['hits'])==30 and not r['errors'] and r['pairs']==77
    source_file=Path(__file__).with_name('w5_loom_common_layout.py')
    assert sha(source_file)==r['source_sha256'][source_file.relative_to(ROOT).as_posix()]
    source=source_file.read_text(encoding='utf-8')
    changes={
        "OUT=BASE/'w5-loom-common-layout-r1'":"OUT=BASE/'w5-loom-common-layout-r2'",
        "rx=-85 if leg.startswith('F') else 123;ry=side*85":"rx=-85 if leg.startswith('F') else 123;ry=side*107",
        "landing=[rx-13,ry-9,105,rx+13,ry+9,113]":"landing=[rx-13,94.5 if side>0 else -116,101,rx+13,116 if side>0 else -94.5,109]",
        "raw={'Foot':[rx-13,ry-9,113,rx+13,ry+9,119]}":"raw={'Foot':[rx-13,ry-9,95,rx+13,ry+9,101]}",
        "raw['Post']=[post_x-4,ry-4,77,post_x+4,ry+4,119]":"raw['Post']=[post_x-4,ry-4,77,post_x+4,ry+4,101]",
        "Part.makeCylinder(1.7,16,A.Vector(x,ry,104))":"Part.makeCylinder(1.7,16,A.Vector(x,ry,94))",
        "deck_landing_z_mm=[105,113],foot_z_mm=[113,119]":"deck_landing_z_mm=[101,109],foot_z_mm=[95,101]",
        "pins.extend([Path(__file__),CORRIDORS,BEARING,SIDE,N.CENTRAL])":"pins.extend([Path(__file__),_base_source,_prior_proof,CORRIDORS,BEARING,SIDE,N.CENTRAL])",
        "Mount four fixed frames from above with accessible captive nuts below; exact hardware and tool envelopes remain to receive.":"Before installing the Deck in the body, mount the four frames from below to the integral outboard ledges; top captive nuts, exact screws and tool access remain to receive.",
        "status='FOUR_FRAME_INTEGRAL_LANDING_CONTACT_RECEIPT'":"status='ONE_OUTBOARD_UNDERSIDE_FOUR_FRAME_CONTACT_RECEIPT'",
    }
    for old,new in changes.items():
        assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new)
    ctx=dict(__file__=str(Path(__file__).resolve()),__name__='loom_outboard_receive',
             _base_source=source_file,_prior_proof=proof)
    exec(compile(source,str(source_file),'exec'),ctx);ctx['main']()


if __name__=='__main__':main()
