"""Load received whole central routes, not their superseded end fragments."""
from pathlib import Path
import json
import w5_central_shared_routes as scope
from servo_fuse_inputs_r1 import sha

RECEIVED=scope.ROOT/'hardware/electronics/full-cat/w5-central-received-joint-r1/received.json'


def load(A,Part):
    fixed,printed,ends,family,rows,pins,reused,replaced=scope.load_scope(A,Part)
    receipt=json.loads(RECEIVED.read_text(encoding='utf-8'))
    for rel,digest in receipt['source_sha256'].items():
        assert sha(scope.ROOT/rel)==digest,rel
        pins.append(scope.ROOT/rel)
    for wire,row in receipt['routes'].items():
        fixed[wire]=Part.read(str(scope.ROOT/row['geometry']))
        for key in list(ends):
            if key==wire or key.startswith(wire+'_'):del ends[key]
    pins.extend([RECEIVED,Path(__file__)])
    return fixed,printed,ends,family,rows,pins,reused,replaced
