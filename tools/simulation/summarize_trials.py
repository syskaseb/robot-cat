"""Generate a compact, evidence-linked table; completion is NOT a pass verdict."""
import json, math
from cad_model import OUT


def main():
    rows=[]
    for p in sorted((OUT/'trials').glob('*-summary.json')):
        s=json.loads(p.read_text());j=list(s.get('joints',{}).values())
        if not j:continue
        rows.append(dict(file=p.name,mode=s['mode'],mass_kg=s['mass_kg'],hard_joint_velocity_limit=s.get('hard_joint_velocity_limit',True),
                         offset_mm=[v*1000 for v in s['stance_offset_m']],
                         mu=s['configuration']['friction'],cap_nm=s['configuration']['torque_cap'],
                         simulation_seconds=s['configuration']['seconds'],result=s['result'],
                         travelled_x_mm=s.get('displacement_after_settle_m',[0])[0]*1000,
                         mean_x_mm_s=s.get('mean_x_speed_m_s',0)*1000,
                         max_joint_peak_nm=max(v['peak_nm'] for v in j),
                         max_joint_rms_nm=max(v['rms_nm'] for v in j),
                         max_joint_saturation_fraction=max(v['saturation_fraction'] for v in j),
                         max_joint_error_deg=max(v['max_error_rad'] for v in j)*180/math.pi,
                         envelope_violations=sum(v['torque_speed_violations'] for v in j),
                         stale_motor_samples=s['stale_motor_samples'],cad_sha256=s['source_sha256']))
    report=dict(scope='All per-joint statistics after t=2 s; displacement after t=3 s. Commanded effort, not measured hardware torque. No thermal or full collision approval.',trials=rows)
    (OUT/'trial-comparison.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    lines=['# Wyniki Gazebo — aktualny CAD','',report['scope'],'',
           '| Próba | Masa kg | dx/dz mm | μ | Limit Nm | Droga x mm | RMS max Nm | Pik Nm | Nasycenie max | Sztuczny limit prędkości |',
           '|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for r in rows:
        lines.append(f"| [{r['mode']} {r['file'][:15]}](trials/{r['file']}) | {r['mass_kg']:.3f} | {r['offset_mm'][0]:.0f}/{r['offset_mm'][2]:.0f} | {r['mu']:.1f} | {r['cap_nm']:.2f} | {r['travelled_x_mm']:.1f} | {r['max_joint_rms_nm']:.3f} | {r['max_joint_peak_nm']:.3f} | {r['max_joint_saturation_fraction']*100:.1f}% | {'TAK — starsza próba' if r['hard_joint_velocity_limit'] else 'nie'} |")
    lines+=['','`duration_completed` oznacza koniec próby bez upadku, nie zatwierdzenie napędów.','Nasycenie liczone względem limitu testowego; model dodatkowo ogranicza moment przy wzroście prędkości.','Podłoga i stopy są uproszczone. Wszystkie wyniki wymagają oceny wraz z README i audytem kolizji.']
    (OUT/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print('\n'.join(lines))


if __name__=='__main__':main()
