# Wyniki Gazebo — aktualny CAD

All per-joint statistics after t=2 s; displacement after t=3 s. Commanded effort, not measured hardware torque. No thermal or full collision approval.

| Próba | Masa kg | dx/dz mm | μ | Limit Nm | Droga x mm | RMS max Nm | Pik Nm | Nasycenie max | Sztuczny limit prędkości |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| [stand 20260922-001715](trials/20260922-001715-stand-summary.json) | 2.448 | -30/-5 | 0.4 | 1.00 | 0.0 | 0.539 | 0.540 | 0.0% | TAK — starsza próba |
| [crawl 20260922-001731](trials/20260922-001731-crawl-summary.json) | 2.448 | -30/-5 | 0.4 | 1.00 | 82.0 | 0.583 | 1.000 | 3.8% | TAK — starsza próba |
| [crawl 20260922-001741](trials/20260922-001741-crawl-summary.json) | 2.911 | -30/-5 | 0.4 | 1.00 | 86.9 | 0.658 | 1.000 | 16.0% | TAK — starsza próba |
| [stand 20260922-002635](trials/20260922-002635-stand-summary.json) | 2.448 | -30/-5 | 0.4 | 1.00 | 0.0 | 0.539 | 0.541 | 0.0% | nie |
| [crawl 20260922-002653](trials/20260922-002653-crawl-summary.json) | 2.448 | -30/-5 | 0.4 | 1.00 | 78.3 | 0.580 | 1.000 | 4.2% | nie |
| [crawl 20260922-002703](trials/20260922-002703-crawl-summary.json) | 2.911 | -30/-5 | 0.4 | 1.00 | 82.0 | 0.654 | 1.000 | 16.1% | nie |

`duration_completed` oznacza koniec próby bez upadku, nie zatwierdzenie napędów.
Nasycenie liczone względem limitu testowego; model dodatkowo ogranicza moment przy wzroście prędkości.
Podłoga i stopy są uproszczone. Wszystkie wyniki wymagają oceny wraz z README i audytem kolizji.
