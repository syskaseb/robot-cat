"""Restore the named current receipt only; never search historical archives."""
import hashlib
import json
import zipfile
from pathlib import Path
import Part


def load(packet_path):
    packet_path=Path(packet_path);packet=json.loads(packet_path.read_text(encoding='utf-8'))
    archive=Path(packet['geometry_archive']['path'])
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==packet['geometry_archive']['sha256']
    member=packet['day18_current_scoped_receipt']['member']
    with zipfile.ZipFile(archive) as z:
        receipt=json.loads(z.read(member));shapes={}
        records=dict(receipt['shapes'])
        extras={}
        if packet.get('day18_BUS25_space_receipt'):
            bus=json.loads(z.read(packet['day18_BUS25_space_receipt']))
            records['ConservativeSourceCover:Ref_Material_BUSsupplier25_0_0']=bus['cover']
            extras['BUS25']=bus
        if packet.get('day18_MTA_simple_retention_receipt'):
            mta=json.loads(z.read(packet['day18_MTA_simple_retention_receipt']))
            records.update(mta['shapes']);extras['MTA']=mta
        for n,row in records.items():
            raw=z.read(row['member']);assert hashlib.sha256(raw).hexdigest()==row['sha256'],n
            s=Part.Shape();s.importBrepFromString(raw.decode());s.check(True);shapes[n]=s
        receipt['restored_supplement_receipts']=extras
        receipt['retired_duplicate_reference']=packet.get('day18_retired_duplicate_reference',{})
    return shapes,receipt


def apply_to_received_world(world,metadata,shapes,receipt):
    """Caller first receives its AV5/BL/BP/MAIN9 layers; no silent base replay."""
    result=dict(world);meta=dict(metadata)
    retired=[*receipt['retained_printed_parent_owners'],'RRFlatGuide',
             'DAY18:XP02:pad','DAY18:XP02:root','DAY18:W011',
             'Station:D_RL:one_common_cap','Station:D_RL:split_common_comb',
             'Station:D_RL:one_common_band','Station:D_RL:band_budget',
             'Station:D_FR:wire:D_FR.5']
    # W011 now begins at its true front surface and includes the full9 itself.
    # The old front prefix is therefore duplicate material, not another wire.
    retired.extend(receipt.get('retired_duplicate_reference',{}))
    retired.extend(receipt.get('restored_supplement_receipts',{}).get('MTA',{}).get('source_retired',[]))
    for n in retired:result.pop(n,None)
    result.update({'CurrentFoundation:BankBedCurrent:-1':shapes['Frame'],
                   'Carrier:D_RR':shapes['SourceCarrier'],
                   'Station:D_RL:wire:D_RL.5':shapes['W012ReceiverPrefix'],
                   'Body:W011':shapes['W011Axis'],'Body:W012':shapes['W012Axis']})
    for n,s in shapes.items():
        if n.startswith(('MID:','D_RL:common_band','DAY18:XP02:band','DAY18:XP02:head')):result[n]=s
        if n.startswith('ConservativeSourceCover:'):
            result[n]=s;meta[n]=dict(kind='complete_supplier_space_cover',not_approved_native_BRep=True)
        if n in receipt.get('restored_supplement_receipts',{}).get('MTA',{}).get('shapes',{}):
            result[n]=s;meta[n]=dict(kind='received_constructive_MTA_retention_NOT_production_N03')
    for n in ['Body:W011','Body:W012']:meta[n]=dict(kind='received_nominal_wire_axis',nominal_profile_radius_mm=1.55)
    meta['Station:D_RL:wire:D_RL.5']=dict(kind='received_nominal_wire',logical_endpoint='D_RL.5',physical_slot=1,same_common_potential=True)
    return result,meta
