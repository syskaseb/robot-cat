# Wyniki Gazebo — aktualny CAD

All per-joint statistics after t=2 s; displacement after t=3 s. Commanded effort, not measured hardware torque. No thermal or full collision approval.

| Próba | Masa kg | dx/dz mm | μ | Limit Nm | Droga x mm | RMS max Nm | Pik Nm | Nasycenie max | Sztuczny limit prędkości |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| [stand 20260921-235426](trials/20260921-235426-stand-summary.json) | 2.449 | -30/-5 | 0.4 | 1.00 | 0.0 | 0.539 | 0.541 | 0.0% | TAK — starsza próba |
| [crawl 20260921-235515](trials/20260921-235515-crawl-summary.json) | 2.449 | -30/-5 | 0.4 | 1.00 | 81.7 | 0.581 | 1.000 | 4.1% | TAK — starsza próba |
| [crawl 20260921-235524](trials/20260921-235524-crawl-summary.json) | 2.449 | -30/-5 | 0.2 | 1.00 | 86.9 | 0.538 | 1.000 | 2.6% | TAK — starsza próba |
| [crawl 20260921-235534](trials/20260921-235534-crawl-summary.json) | 2.912 | -30/-5 | 0.4 | 1.00 | 86.9 | 0.658 | 1.000 | 16.0% | TAK — starsza próba |
| [crawl 20260921-235642](trials/20260921-235642-crawl-summary.json) | 2.449 | -40/-5 | 0.4 | 1.00 | 82.8 | 0.568 | 1.000 | 4.1% | TAK — starsza próba |
| [crawl 20260921-235654](trials/20260921-235654-crawl-summary.json) | 2.912 | -40/-5 | 0.4 | 1.00 | 85.7 | 0.643 | 1.000 | 15.0% | TAK — starsza próba |
| [stand 20260921-235658](trials/20260921-235658-stand-summary.json) | 2.449 | 0/0 | 0.4 | 1.00 | 0.0 | 0.720 | 0.721 | 0.0% | TAK — starsza próba |
| [crawl 20260921-235704](trials/20260921-235704-crawl-summary.json) | 2.449 | -30/-5 | 0.4 | 0.65 | 87.1 | 0.504 | 0.650 | 38.3% | TAK — starsza próba |

`duration_completed` oznacza koniec próby bez upadku, nie zatwierdzenie napędów.
Nasycenie liczone względem limitu testowego; model dodatkowo ogranicza moment przy wzroście prędkości.
Podłoga i stopy są uproszczone. Wszystkie wyniki wymagają oceny wraz z README i audytem kolizji.
