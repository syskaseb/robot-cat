"""Narrow named channel contracts omitted by the old generic owner matcher.

Only the explicitly received owning jacket gets its constructor's fit gap.
Other wires, PCBs, bought cases and neighboring bank caps keep 1.25mm.
Changing a necessity certificate's contract is not a clearance receipt.
"""
from reconcile_feline_source_portal_contracts import own_channel as parent


def own_channel(e, owner):
    endpoint = e.get('endpoint', '')
    group = e.get('group', '')
    prefix = e.get('prefix_geometry_owner', '')
    if group == 'BUS' and endpoint in ('BUS.D', 'BUS.G'):
        tag = endpoint[-1]
        if prefix == 'CurrentBUS:'+endpoint and owner in ('DGGrip:'+tag+':cap', 'SharedBUS:TailCarrier'):
            return .15
    if group == 'Pi4' and prefix.startswith(('PiGPIO:', 'PiPower:')) and owner == 'SharedPi:Carrier':
        return .15
    if endpoint == 'F_HY.in' and owner == 'ForeFHAC:in:custom:saddle':
        return .15
    if endpoint == 'F_TY.out' and owner == 'CurrentInline:F_TY.out:custom:saddle':
        return .15
    return parent(e, owner)
