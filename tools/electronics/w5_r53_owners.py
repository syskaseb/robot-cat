"""Installed R53 census, with one selected carrier and the completed BUS."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]


def installed(A,Part):
    from w5_selected_owners_r52 import cached
    import w5_bus_restraints_r3 as bus
    from servo_fuse_inputs_r1 import sha
    owners,_=cached()
    omitted=[
        'hardware/electronics/full-cat/tail-ground-direct-r1/CarrierTailPWMEntry_DESIGN.brep',
        'hardware/electronics/full-cat/tail-central-routes-r3/CarrierTailPWMEntry_DESIGN.brep',
        'hardware/electronics/full-cat/head-connected-feeds-r8/CarrierPWMEntry_DESIGN.brep',
        'hardware/electronics/full-cat/aux-converter-routes-r5/Carrier_TWO_PORTS_DIAGNOSTIC.brep']
    for key in omitted:del owners[key]
    for key in bus.removed_owners():del owners[key]
    selection=ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json'
    selected=json.loads(selection.read_text(encoding='utf-8'))
    carrier=next(p for p in selected['prints'] if p['identity']=='electronics:Carrier service ports')
    assert sha(ROOT/carrier['stl'])==carrier['sha256']
    deck=ROOT/selected['current_deck_world'];owners['CandidateDeck']=Part.read(str(deck))
    bus_file=ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
    bi=json.loads(bus_file.read_text(encoding='utf-8'))
    sx=sum(bi['source_lead_datums'][k][0] for k in ('W002','W003'))/2
    owners.update({'R53BUS/'+k:s for k,s in bus.restraints(A,Part,sx).items()})
    for wire in ('W002','W003'):owners['R53BUS/'+wire]=Part.read(str(bus_file.parent/(wire+'_DESIGN.brep')))
    pins=[selection,deck,bus_file,ROOT/carrier['stl'],Path(__file__),
          ROOT/'tools/electronics/w5_selected_owners_r52.py',ROOT/'tools/electronics/w5_bus_restraints_r3.py',
          ROOT/'hardware/electronics/full-cat/w5-installed-r52/owners.json',
          ROOT/'hardware/electronics/full-cat/w5-installed-r52/installed.brep']
    return owners,pins,omitted
