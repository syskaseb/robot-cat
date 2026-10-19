"""Keep one immutable world loaded across bounded requested-only receipts.

Does not alter the receiver's geometry/query kernel or cache semantics.
All source pins are checked fresh before reusing the in-memory world.
"""
import json
import sys
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


class PinnedWorld:
    def __init__(self,factory):
        self.factory=factory
        self.loaded=None

    def __call__(self):
        if self.loaded is None:self.loaded=self.factory()
        else:
            world,_=self.loaded
            for name,digest in world.pins.items():
                assert sha(ROOT/name)==digest,'Changed fixed-world source requires a new receiver context: '+name
        return self.loaded


_receiver=None


def receive_requested():
    global _receiver
    if _receiver is None:
        import feline_beside_bank_receive as module
        module.current_world=PinnedWorld(module.current_world)
        _receiver=module
    previous=sys.argv
    try:
        sys.argv=[_receiver.__file__,'--straight','--requested']
        _receiver.main()
    finally:sys.argv=previous
    result=json.loads((OUT/'n01-straight-combs-received.json').read_text())
    assert not result['errors'],result['errors']
    return result['status']
