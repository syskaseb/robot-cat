"""Do not mistake a changed CAD part for harmless BRep serialization."""
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location(
    'inheritance30', Path(__file__).parents[1]/'freecad/skorupa/inheritance30.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_identical_brep_text():
    assert module.compare_text('Locations 1\n0 1 2', 'Locations 1\n0 1 2')['byte_identical']


def test_roundoff_and_alignment():
    result = module.compare_text('Locations 1\n-0 1.00000000000001 -2e-16',
                                 'Locations 1\n  0                 1  3e-16')
    assert result['changed_numbers'] == 3
    assert result['max_absolute_delta'] < 1e-12


@pytest.mark.parametrize('changed', [
    'Locations 1\n0 1 2.001',  # geometric change
    'Surfaces 1\n0 1 2',      # topology/text change
    'Locations 1\n0 1',       # missing numeric token
    'Locations 2\n0 1 2',     # changed count
])
def test_reject_changed_representation(changed):
    with pytest.raises(AssertionError):
        module.compare_text('Locations 1\n0 1 2', changed)
