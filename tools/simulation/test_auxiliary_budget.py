import numpy as np
import pytest
from auxiliary_budget import budget


def part(x):
    return dict(name='test',mass_kg=1,com_m=[x,0,0],inertia_kg_m2=(np.eye(3)*.001).tolist())


def test_balanced_head_gravity_zero():
    result=budget([part(.1)],[.1,0,0],[0,1,0],range(-30,31),2)
    assert result['peak_gravity_nm']==pytest.approx(0)
    assert result['gravity_plus_inertia_nm']==pytest.approx(.002)


def test_cantilever_gravity_and_inertia():
    result=budget([part(.1)],[0,0,0],[0,1,0],[0],2)
    assert result['peak_gravity_nm']==pytest.approx(.980665)
    assert result['inertia_about_axis_kg_m2']==pytest.approx(.011)


def test_vertical_yaw_not_affected_by_gravity():
    result=budget([part(.1)],[0,0,0],[0,0,1],range(-30,31),2)
    assert result['peak_gravity_nm']==pytest.approx(0)
