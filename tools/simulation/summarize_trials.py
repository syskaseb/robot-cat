"""Generate a compact, evidence-linked table; completion is NOT a pass verdict."""
import json, math
from cad_model import OUT


def comparison_row(s, filename, records=()):
        # Early falls can precede the t>2 s statistics window. Keep them in
        # the comparison; absence of statistics is NOT zero effort or success.
        j=list(s.get('joints',{}).values())
        displacement=s.get('displacement_after_settle_m')
        last=records[-1] if records else {}
        last_rpy=s.get('last_rpy',last.get('rpy'))
        return dict(file=filename,mode=s['mode'],mass_kg=s['mass_kg'],hard_joint_velocity_limit=s.get('hard_joint_velocity_limit',True),
                         step_seconds=s['configuration']['step_seconds'],
                         crawl_cycle_seconds=4*s['configuration']['step_seconds'] if s['mode']=='crawl' else None,
                         kinematic_speed_mm_s=24/(3.5*s['configuration']['step_seconds']) if s['mode']=='crawl' else None,
                         offset_mm=[v*1000 for v in s['stance_offset_m']],
                         mu=s['configuration']['friction'],cap_nm=s['configuration']['torque_cap'],
                         simulation_seconds=s['configuration']['seconds'],result=s['result'],
                         observed_end_seconds=last.get('t'),last_position_m=last.get('position'),
                         screening_completed=s.get('screening_completed',False),
                         settled_statistics_available=bool(j),
                         travelled_x_mm=displacement[0]*1000 if displacement else None,
                         mean_x_mm_s=s['mean_x_speed_m_s']*1000 if 'mean_x_speed_m_s' in s else None,
                         max_joint_peak_nm=max((v['peak_nm'] for v in j),default=None),
                         max_joint_rms_nm=max((v['rms_nm'] for v in j),default=None),
                         max_joint_saturation_fraction=max((v['saturation_fraction'] for v in j),default=None),
                         max_joint_error_deg=max(v['max_error_rad'] for v in j)*180/math.pi if j else None,
                         max_joint_peak_speed_rad_s=max((v['peak_speed_rad_s'] for v in j),default=None),
                         peak_abs_roll_pitch_deg=[v*180/math.pi for v in s['peak_abs_roll_pitch_rad']] if 'peak_abs_roll_pitch_rad' in s else None,
                         final_yaw_deg=last_rpy[2]*180/math.pi if last_rpy else None,
                         envelope_violations=sum(v['torque_speed_violations'] for v in j) if j else None,
                         stale_motor_samples=s['stale_motor_samples'],cad_sha256=s['source_sha256'])


def format_stat(value, digits=3, scale=1, suffix=''):
    return '—' if value is None else f'{value*scale:.{digits}f}{suffix}'


def main():
    rows=[]
    for p in sorted((OUT/'trials').glob('*-summary.json')):
        s=json.loads(p.read_text())
        raw=p.with_name(p.name.replace('-summary.json','.json'))
        records=json.loads(raw.read_text()).get('records',[]) if raw.exists() else []
        rows.append(comparison_row(s,p.name,records))
    report=dict(scope='All per-joint statistics after t=2 s; displacement after t=3 s. Early failures retained with null / — for unavailable statistics, never zero. Commanded effort, not measured hardware torque. No thermal or full collision approval.',trials=rows)
    (OUT/'trial-comparison.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    lines=['# Wyniki Gazebo — aktualny CAD','',report['scope'],'',
           '| Próba / wynik | Masa kg | dx/dz mm | Cykl s | μ | Limit Nm | Droga x mm | RMS max Nm | Pik Nm | Nasycenie max | Sztuczny limit prędkości |',
           '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for r in rows:
        cycle='—' if r['crawl_cycle_seconds'] is None else f"{r['crawl_cycle_seconds']:.2f}"
        lines.append(f"| [{r['mode']} {r['file'][:15]}](trials/{r['file']}) / {r['result']} | {r['mass_kg']:.3f} | {r['offset_mm'][0]:.0f}/{r['offset_mm'][2]:.0f} | {cycle} | {r['mu']:.2f} | {r['cap_nm']:.2f} | {format_stat(r['travelled_x_mm'],1)} | {format_stat(r['max_joint_rms_nm'])} | {format_stat(r['max_joint_peak_nm'])} | {format_stat(r['max_joint_saturation_fraction'],1,100,'%')} | {'TAK — starsza próba' if r['hard_joint_velocity_limit'] else 'nie'} |")
    lines+=['','`duration_completed` oznacza koniec próby bez upadku, nie zatwierdzenie napędów.','Nasycenie liczone względem limitu testowego; model dodatkowo ogranicza moment przy wzroście prędkości.','Podłoga i stopy są uproszczone. Wszystkie wyniki wymagają oceny wraz z README i audytem kolizji.']
    (OUT/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print('\n'.join(lines))


if __name__=='__main__':main()
