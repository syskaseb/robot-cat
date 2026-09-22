import json
import numpy as np
import pytest
from cad_model import OUT
from cad_kinematics import forward,inverse,stepping_targets,support_shift,crawl_targets

MODEL=json.loads((OUT/'model.json').read_text(encoding='utf8'))
FEET=json.loads((OUT/'feet.json').read_text())


@pytest.mark.parametrize('code',list(FEET))
def test_forward_inverse_and_jacobian(code):
    js=[j for j in MODEL['joints'] if j['cad_code']==code];p=FEET[code]
    assert forward(js,p,[0,0,0])[0]==pytest.approx(p)
    q=np.array([.12,-.07,.05]);target,J=forward(js,p,q)
    assert inverse(js,p,target)==pytest.approx(q,abs=2e-5)
    for i in range(3):
        d=np.eye(3)[i]*1e-6
        numeric=(forward(js,p,q+d)[0]-forward(js,p,q-d)[0])/2e-6
        assert J[:,i]==pytest.approx(numeric,abs=1e-7)


def test_slow_stepping_is_continuous_and_limited():
    samples=np.array([list(stepping_targets(MODEL,FEET,t).values()) for t in np.arange(0,12.001,.02)])
    assert abs(samples).max()<.48
    assert abs(np.diff(samples,axis=0)/.02).max()<1.0
    assert samples[0]==pytest.approx(np.zeros(12),abs=1e-5)
    assert samples[-1]==pytest.approx(samples[0],abs=1e-5)


@pytest.mark.parametrize('code',list(FEET))
def test_shift_places_com_inside_support(code):
    com=np.array(MODEL['total']['com_m'])+support_shift(FEET,code,MODEL['total']['com_m'])
    points=np.array([p[:2] for c,p in FEET.items() if c!=code])
    bary=np.linalg.solve(np.vstack([points.T,np.ones(3)]),np.r_[com[:2],1.])
    assert bary.min()>.04


def test_crawl_is_periodic_continuous_and_within_joint_limits():
    trajectory=np.array([list(crawl_targets(MODEL,FEET,t,offset=[-.03,0,-.005]).values()) for t in np.arange(0,12.001,.02)])
    assert abs(trajectory).max()<.48
    assert abs(np.diff(trajectory,axis=0)/.02).max()<1
    assert trajectory[0]==pytest.approx(trajectory[-1],abs=1e-6)
