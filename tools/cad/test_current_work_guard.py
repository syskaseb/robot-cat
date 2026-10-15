import copy,unittest
from datetime import datetime,timezone,timedelta
from current_work_guard import validate


class CurrentGuardTest(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,15,12,tzinfo=timezone.utc)
        self.state={'enabled':False,'stop_reason':None,'usage_max_age_seconds':600,
            'manual_phase1_resume_20261015':{'target_count':20,'fixed_total':20,'deadline_utc':None},
            'last_account_usage':{'ordinary_usage_allowed':True,'weekly_remaining_percent':98,'checked_utc':'2026-10-15T11:59:00Z'}}
    def test_manual_authorization_does_not_reenable_old_hook(self):self.assertTrue(validate(self.state,self.now))
    def test_old_read_stops(self):
        with self.assertRaises(TimeoutError):validate(self.state,self.now+timedelta(minutes=11))
    def test_zero_usage_stops_without_reset(self):
        self.state['last_account_usage']['weekly_remaining_percent']=0
        with self.assertRaises(TimeoutError):validate(self.state,self.now)
    def test_stop_or_completed_authorization_stops(self):
        self.state['stop_reason']='human_stop'
        with self.assertRaises(TimeoutError):validate(self.state,self.now)
        self.state['stop_reason']=None;self.state['manual_phase1_resume_20261015']['completed']=True
        with self.assertRaises(TimeoutError):validate(self.state,self.now)


if __name__=='__main__':unittest.main()
