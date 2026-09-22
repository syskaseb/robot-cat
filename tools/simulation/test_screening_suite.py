from run_v32_screening import configurations

def test_baseline_is_three_comparable_cases():
    rows=configurations('baseline')
    assert len(rows)==3
    assert {(r['mode'],r['mass']) for r in rows}=={('stand','nominal'),('crawl','nominal'),('crawl','upper')}
    assert all(r['step_seconds']==1 and r['friction']==.4 and r['torque_cap']==1 for r in rows)

def test_sweep_is_bounded_and_keeps_mass_sensitivity():
    rows=configurations('sweep')
    assert len(rows)==14 and len({r['tag'] for r in rows})==14
    assert {r['mass'] for r in rows}=={'nominal','upper'}
    assert all(r['mode']=='crawl' and r['seconds']==15 for r in rows)
    assert all(.15<=r['step_seconds']<=1 and .25<=r['friction']<=.6 and .65<=r['torque_cap']<=1 for r in rows)
    assert len(configurations('all'))==17
