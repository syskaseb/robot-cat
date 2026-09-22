# Wyniki Gazebo — aktualny CAD

All per-joint statistics after t=2 s; displacement after t=3 s. Commanded effort, not measured hardware torque. No thermal or full collision approval.

| Próba | Masa kg | dx/dz mm | μ | Limit Nm | Droga x mm | RMS max Nm | Pik Nm | Nasycenie max | Sztuczny limit prędkości |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| [stand 20260922-014049](trials/20260922-014049-stand-summary.json) | 2.416 | -30/-5 | 0.4 | 1.00 | 0.0 | 0.534 | 0.536 | 0.0% | nie |
| [crawl 20260922-014109](trials/20260922-014109-crawl-summary.json) | 2.416 | -30/-5 | 0.4 | 1.00 | 79.0 | 0.573 | 1.000 | 3.8% | nie |
| [crawl 20260922-014135](trials/20260922-014135-crawl-summary.json) | 2.875 | -30/-5 | 0.4 | 1.00 | 82.2 | 0.650 | 1.000 | 15.3% | nie |

`duration_completed` oznacza koniec próby bez upadku, nie zatwierdzenie napędów.
Nasycenie liczone względem limitu testowego; model dodatkowo ogranicza moment przy wzroście prędkości.
Podłoga i stopy są uproszczone. Wszystkie wyniki wymagają oceny wraz z README i audytem kolizji.
