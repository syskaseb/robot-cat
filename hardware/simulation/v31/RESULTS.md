# Wyniki Gazebo — aktualny CAD

All per-joint statistics after t=2 s; displacement after t=3 s. Commanded effort, not measured hardware torque. No thermal or full collision approval.

| Próba | Masa kg | dx/dz mm | μ | Limit Nm | Droga x mm | RMS max Nm | Pik Nm | Nasycenie max | Sztuczny limit prędkości |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| [stand 20260922-031610](trials/20260922-031610-stand-summary.json) | 2.421 | -30/-5 | 0.4 | 1.00 | 0.0 | 0.535 | 0.537 | 0.0% | nie |
| [crawl 20260922-031630](trials/20260922-031630-crawl-summary.json) | 2.421 | -30/-5 | 0.4 | 1.00 | 78.8 | 0.576 | 1.000 | 3.7% | nie |
| [crawl 20260922-031657](trials/20260922-031657-crawl-summary.json) | 2.879 | -30/-5 | 0.4 | 1.00 | 82.1 | 0.649 | 1.000 | 15.4% | nie |

`duration_completed` oznacza koniec próby bez upadku, nie zatwierdzenie napędów.
Nasycenie liczone względem limitu testowego; model dodatkowo ogranicza moment przy wzroście prędkości.
Podłoga i stopy są uproszczone. Wszystkie wyniki wymagają oceny wraz z README i audytem kolizji.
