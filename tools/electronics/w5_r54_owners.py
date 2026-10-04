"""Current selected R54 census, exactly one Deck and one XA05 path.

R53 BUS/bank unchanged. The replaced R20 interlinked XA05 tie roles had no
cached shapes; don't insert imaginary historical restraints into the scene.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]


def installed(A,Part):
    from w5_r53_owners import installed as previous
    from servo_fuse_inputs_r1 import sha
    owners,pins,omitted=previous(A,Part)
    selection_path=ROOT/'hardware/manufacturing/one-batch-prototype-r54/selection.json'
    selected=json.loads(selection_path.read_text(encoding='utf-8'))
    assert selected['XA05_local_complete'] and not selected['W5_complete']
    native=ROOT/selected['XA05_native_proof']
    proof=json.loads(native.read_text(encoding='utf-8'))
    assert proof['status']=='XA05_NATIVE_STATIC_COMPLETE_UNSELECTED' and not proof['hits'] and not proof['errors']
    for k,v in {**proof['source_sha256'],**proof['files']}.items():assert sha(ROOT/k)==v,k
    old='hardware/electronics/full-cat/xa05-main-aux-return-r2/XA05_DESIGN.brep'
    assert old in owners and 'CandidateDeck' in owners
    del owners[old]
    deck=ROOT/selected['current_deck_world'];owners['CandidateDeck']=Part.read(str(deck))
    bracket=deck.with_name('Outrigger_WORLD.brep');owners['R54XA05/Outrigger']=Part.read(str(bracket))
    raw=ROOT/'hardware/electronics/full-cat/w5-xa05-outer-support-r5'
    wire=raw/'XA05_WORLD.brep';owners['R54XA05/Wire']=Part.read(str(wire))
    additions=raw/'ADDITIONS_WORLD.brep';children=Part.read(str(additions)).childShapes();assert len(children)==10
    for label,s in zip(('InnerTie','OuterTie','Bolt0','Washers0','Nut0','Bolt1','Washers1','Nut1'),children[2:]):owners['R54XA05/'+label]=s
    pins += [Path(__file__),selection_path,native,ROOT/selected['XA05_access_proof'],deck,bracket,wire,additions]
    return owners,pins,omitted
