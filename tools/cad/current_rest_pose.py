"""Select a neutral snapshot from explicit sampled-motion names only.

No geometry, collision or quantities are inferred from this name filter.
Never discard a numeric physical part identity as though it were a pose.
"""
import re


def is_rest(name):
    parts=name.split('/')
    if parts[0]=='head':return float(parts[1])==float(parts[2])==0
    if parts[0] in ('headref','headwire','factory'):
        return float(parts[1])==0
    # Branch and splice indices are identities, not extra motion angles.
    if parts[0] in ('Root','Source') and len(parts)==4:return float(parts[-1])==0
    if parts[0]=='chosen' and len(parts)==3:return float(parts[-1])==0
    if parts[0].startswith('Band_'):
        return float(parts[-2])==float(parts[-1])==0
    m=re.search(r'/(-?\d+(?:\.\d+)?)/(-?\d+(?:\.\d+)?)(?:/(-?\d+(?:\.\d+)?))?$',name)
    if m:
        values=[float(v) for v in m.groups() if v is not None]
        if all(v in (-15,0,15) for v in values):return not any(values)
    return True
def is_physical_reference(name):
    """Access/tool reservations belong to proofs, not installed material."""
    return not name.startswith(('ServiceATO/','ServiceJaw/','RailHoleKeepout','RailNutTrapKeepout','RailDriverKeepout'))

