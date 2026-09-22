# Wyniki Gazebo — aktualny CAD

All per-joint statistics after t=2 s; displacement after t=3 s. Early failures retained with null / — for unavailable statistics, never zero. Commanded effort, not measured hardware torque. No thermal or full collision approval.

| Próba / wynik | Masa kg | dx/dz mm | Cykl s | μ | Limit Nm | Droga x mm | RMS max Nm | Pik Nm | Nasycenie max | Sztuczny limit prędkości |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| [stand 20260922-041646](trials/20260922-041646-stand-summary.json) / duration_completed | 2.420 | -30/-5 | — | 0.40 | 1.00 | 0.0 | 0.535 | 0.538 | 0.0% | nie |
| [crawl 20260922-041721](trials/20260922-041721-crawl-summary.json) / duration_completed | 2.420 | -30/-5 | 4.00 | 0.40 | 1.00 | 78.5 | 0.575 | 1.000 | 3.8% | nie |
| [crawl 20260922-041749](trials/20260922-041749-crawl-summary.json) / duration_completed | 2.878 | -30/-5 | 4.00 | 0.40 | 1.00 | 82.7 | 0.651 | 1.000 | 15.4% | nie |
| [crawl 20260922-042018](trials/20260922-042018-crawl-summary.json) / duration_completed | 2.420 | -30/-5 | 3.00 | 0.40 | 1.00 | 130.7 | 0.600 | 1.000 | 4.5% | nie |
| [crawl 20260922-042101](trials/20260922-042101-crawl-summary.json) / duration_completed | 2.878 | -30/-5 | 3.00 | 0.40 | 1.00 | 131.4 | 0.686 | 1.000 | 22.0% | nie |
| [crawl 20260922-042132](trials/20260922-042132-crawl-summary.json) / duration_completed | 2.420 | -30/-5 | 2.00 | 0.40 | 1.00 | 171.7 | 0.626 | 1.000 | 12.4% | nie |
| [crawl 20260922-042159](trials/20260922-042159-crawl-summary.json) / duration_completed | 2.878 | -30/-5 | 2.00 | 0.40 | 1.00 | 154.6 | 0.710 | 1.000 | 26.1% | nie |
| [crawl 20260922-042226](trials/20260922-042226-crawl-summary.json) / duration_completed | 2.420 | -30/-5 | 1.00 | 0.40 | 1.00 | 382.7 | 0.603 | 1.000 | 11.6% | nie |
| [crawl 20260922-042253](trials/20260922-042253-crawl-summary.json) / duration_completed | 2.878 | -30/-5 | 1.00 | 0.40 | 1.00 | 375.2 | 0.698 | 1.000 | 27.8% | nie |
| [crawl 20260922-042333](trials/20260922-042333-crawl-summary.json) / duration_completed | 2.420 | -30/-5 | 0.60 | 0.40 | 1.00 | 911.4 | 0.685 | 1.000 | 26.9% | nie |
| [crawl 20260922-042420](trials/20260922-042420-crawl-summary.json) / duration_completed | 2.878 | -30/-5 | 0.60 | 0.40 | 1.00 | 597.3 | 0.741 | 1.000 | 41.4% | nie |
| [crawl 20260922-042451](trials/20260922-042451-crawl-summary.json) / duration_completed | 2.420 | -30/-5 | 2.00 | 0.25 | 1.00 | 132.2 | 0.570 | 1.000 | 4.0% | nie |
| [crawl 20260922-042527](trials/20260922-042527-crawl-summary.json) / duration_completed | 2.878 | -30/-5 | 2.00 | 0.25 | 1.00 | 148.5 | 0.661 | 1.000 | 11.5% | nie |
| [crawl 20260922-042557](trials/20260922-042557-crawl-summary.json) / duration_completed | 2.420 | -30/-5 | 2.00 | 0.60 | 1.00 | 87.2 | 0.597 | 1.000 | 12.9% | nie |
| [crawl 20260922-042624](trials/20260922-042624-crawl-summary.json) / duration_completed | 2.878 | -30/-5 | 2.00 | 0.60 | 1.00 | 52.5 | 0.716 | 1.000 | 29.7% | nie |
| [crawl 20260922-042651](trials/20260922-042651-crawl-summary.json) / duration_completed | 2.420 | -30/-5 | 4.00 | 0.40 | 0.65 | 83.0 | 0.503 | 0.650 | 36.0% | nie |
| [crawl 20260922-042718](trials/20260922-042718-crawl-summary.json) / fell_or_tilted | 2.878 | -30/-5 | 4.00 | 0.40 | 0.65 | — | — | — | — | nie |

`duration_completed` oznacza koniec próby bez upadku, nie zatwierdzenie napędów.
Nasycenie liczone względem limitu testowego; model dodatkowo ogranicza moment przy wzroście prędkości.
Podłoga i stopy są uproszczone. Wszystkie wyniki wymagają oceny wraz z README i audytem kolizji.
