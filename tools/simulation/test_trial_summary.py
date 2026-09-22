"""Failed physics runs must remain visible even before settled statistics."""
from summarize_trials import comparison_row,format_stat


def early_failure():
    return dict(mode='crawl',mass_kg=2.8,hard_joint_velocity_limit=False,
                configuration=dict(step_seconds=1,friction=.4,torque_cap=.65,seconds=15),
                stance_offset_m=[-.03,0,-.005],result='fell_or_tilted',
                screening_completed=False,stale_motor_samples=0,source_sha256='cad')


def test_early_fall_is_retained_without_invented_zero_statistics():
    row=comparison_row(early_failure(),'failed-summary.json',[
        dict(t=1.001,position=[0,0,.09],rpy=[.1,.2,.3])])
    assert row['result']=='fell_or_tilted' and not row['screening_completed']
    assert not row['settled_statistics_available']
    for key in ('max_joint_rms_nm','travelled_x_mm','mean_x_mm_s','envelope_violations'):
        assert row[key] is None
    assert row['observed_end_seconds']==1.001
    assert row['last_position_m']==[0,0,.09]
    assert row['final_yaw_deg']>0


def test_missing_raw_data_is_not_reported_as_zero_time_or_yaw():
    row=comparison_row(early_failure(),'failed-summary.json')
    assert row['observed_end_seconds'] is None and row['final_yaw_deg'] is None
    assert format_stat(None)=='—'
    assert format_stat(0)=='0.000'
    assert format_stat(.36,1,100,'%')=='36.0%'
