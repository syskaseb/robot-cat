"""Read-only guard for the newly authorized manual phase1 continuation.

Legacy builders retain their historical deadline. New native work must use
current authorization and a fresh actual account reading, never reset credit.
"""
import json,os
from datetime import datetime,timezone
from pathlib import Path


def validate(state,now=None):
    now=now or datetime.now(timezone.utc)
    manual=state.get('manual_phase1_resume_20261015',{})
    if manual.get('target_count')!=20 or manual.get('fixed_total')!=20 or manual.get('completed'):
        raise TimeoutError('No active manual100percent authorization')
    if state.get('stop_reason') is not None:raise TimeoutError('Current work explicitly stopped')
    deadline=manual.get('deadline_utc')
    if deadline and now>=datetime.fromisoformat(deadline.replace('Z','+00:00')):raise TimeoutError('Current authorized deadline')
    u=state.get('last_account_usage',{})
    if not u.get('ordinary_usage_allowed') or not isinstance(u.get('weekly_remaining_percent'),(int,float)) or u['weekly_remaining_percent']<=0:
        raise TimeoutError('Ordinary account usage unavailable/exhausted')
    checked=datetime.fromisoformat(u['checked_utc'].replace('Z','+00:00'));age=(now-checked).total_seconds()
    if not -120<=age<=state.get('usage_max_age_seconds',600):raise TimeoutError('Actual account reading is stale')
    return True


def check():
    path=os.environ.get('ROBOT_CAT_WORK_STATE')
    if not path:raise RuntimeError('Set explicit ROBOT_CAT_WORK_STATE for current native worker')
    return validate(json.loads(Path(path).read_text(encoding='utf-8-sig')))
