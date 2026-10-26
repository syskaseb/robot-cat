"""Separate illustrative flexible leads from rigid prototype space constraints.

This classification is for shared harness-space planning only. It does not
waive connector, bare-conductor, fixed-grip or moving-joint checks. Families
below are pipe/reference constructors, not their separately named guides/ties.
"""
from feline_common_space_context import is_jacket


FLEXIBLE_REFERENCE_PREFIXES = (
    'USB500:', 'AuxEscape:', 'SelectedYaw:', 'SelectedYawFactory:',
    'SelectedTail:', 'EndFactory:', 'EndCustom:', 'VerticalCuff:',
    'CuffPrefix:', 'FLArcCuff:', 'RLArc:', 'RRFlat:', 'RRFlatResource:',
    'RepackedMiddle:', 'FactoryFour:',
)


def installed_stock_envelope(name, metadata, retired=()):
    """On-robot tie/head allowance stays occupied even when not rendered.

    These are constructor-declared planning envelopes, not exact supplier
    material. A band and its head are components of ONE physical tie. Retired
    station envelopes must be removed by the current assembly manifest first.
    """
    if name in retired or metadata.get('installed') is False or metadata.get('off_robot'):
        return False
    return (metadata.get('kind') == 'project_stock_reservation'
            and any(token in name.lower() for token in ('band', 'head', 'tie')))


def flexible_reference(name, metadata):
    if installed_stock_envelope(name, metadata):
        return False
    if ':bare' in name.lower() or 'BodyBare' in name or 'PadBare' in name:
        return False
    if metadata.get('kind') == 'bare':
        return False
    return (is_jacket(name, metadata)
            or metadata.get('kind') in ('received_nominal_wire',
                                        'received_nominal_wire_axis')
            or metadata.get('flexible_reference_not_rigid_obstacle') is True
            or name.startswith(FLEXIBLE_REFERENCE_PREFIXES)
            or name.endswith(':wire'))
