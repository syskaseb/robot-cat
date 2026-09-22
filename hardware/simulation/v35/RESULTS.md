# Wyniki Gazebo — aktualny CAD

All per-joint statistics after t=2 s; displacement after t=3 s. Early failures retained with null / — for unavailable statistics, never zero. Commanded effort, not measured hardware torque. No thermal or full collision approval.

| Próba / wynik | Masa kg | dx/dz mm | Cykl s | μ | Limit Nm | Droga x mm | RMS max Nm | Pik Nm | Nasycenie max | Sztuczny limit prędkości |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| [stand 20260922-170012](trials/20260922-170012-stand-summary.json) / duration_completed | 2.503 | -30/-5 | — | 0.40 | 1.00 | 0.0 | 0.565 | 0.568 | 0.0% | nie |
| [crawl 20260922-170034](trials/20260922-170034-crawl-summary.json) / duration_completed | 2.503 | -30/-5 | 4.00 | 0.40 | 1.00 | 84.1 | 0.605 | 1.000 | 4.6% | nie |
| [crawl 20260922-170102](trials/20260922-170102-crawl-summary.json) / duration_completed | 2.968 | -30/-5 | 4.00 | 0.40 | 1.00 | 89.9 | 0.681 | 1.000 | 21.6% | nie |

`duration_completed` oznacza koniec próby bez upadku, nie zatwierdzenie napędów.
Nasycenie liczone względem limitu testowego; model dodatkowo ogranicza moment przy wzroście prędkości.
Podłoga i stopy są uproszczone. Wszystkie wyniki wymagają oceny wraz z README i audytem kolizji.
