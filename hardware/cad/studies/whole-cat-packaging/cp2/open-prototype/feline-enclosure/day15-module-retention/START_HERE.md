# Jeden plan retencji — do przymiarki bez zasilania

Otwórz `module-retention.FCStd`. **To plan wspólnych mocowań, nie nowy zwolniony kit.** Druki P10..P18, fundament, kupne części, pozycje modułów i zakończenia są niezmienione. W drzewie znajdują się R01–R15 z rzeczywistym wskazaniem korzenia, sposobu zamknięcia, kolejności i brakującej przymiarki. Grupy nie są piętnastoma nowymi drukami.

`whole-support-access-map.png` i `whole-retention-current.png` pokazują ten sam układ. Pełna mapa wszystkich **57 pozycji oraz audio/czujników**: `selected-retention-coverage.csv`, `retention-plan.json`, `support-access-map.csv`. Obwiednie na diagramie nie są dowodem wolnej przestrzeni. STL i BOM dotychczasowej ramy wskazują piny w `source-pins.json`; nie kopiowano ponownie 9 siatek.

## Co jest podparte, a czego jeszcze nie trzymać za gotowe

- Odebrana geometria fundamentu/wspólnej ramy/pełnych śrub pozostaje bez zmian. Fizyczne 8osi/gwinty/masa/ruch nadal FIT1.
- Pi ma **4 rzeczywiste otwory Ø2,75**, osie X−74,5/−16,5 i Y−34,5/+14,5 oraz 4 istniejące słupki izolacyjne 3mm, obecnie stykające się z PCB. Wybór: pełne M2,5×12 przez PCB+słupek+tacę, z 2podkładkami i nakrętką. Nominalny stos10,6mm daje tip1,4mm; **drogi nakrętek/kolizje z szyną i bezpieczne pady są dopiero następną próbką**, nie wykonanym połączeniem.
- BUS na oddzielnym P13: 3mm podparcie do nominalnego dołu110, regulowane wspólne chwyty krawędzi. Zachowane 31mm względem chłodzenia Pi; nie założono nieznanych otworów BUS.
- PCA/E1/AMP: wspólna dolna listwa i końcowe chwytaki, PCA używa prawdziwych otworów, nie małych przelotek. E1 lutowany poza PETG; nie naciskać nieobejrzanych elementów. MAIN/AUX: jedna półka z przyszłym wspólnym carrierem; **1,48mm do płyt nie jest jeszcze podparciem**. AUX ma źródłowe otwory Ø2,18 dla M2, MAIN nie ma dowodu otworów w tym modelu.
- Speaker/BNO/mikrofon/dotyk: bezpieczne obrzeża dopiero z próbki/oględzin; nie naciskać membrany, magnesu, czujnika ani zasłaniać mikrofonów. P14 pozostaje stały, mikrofon osobny na P15. Żaden chwytak nie jest zaakceptowany przez samą nazwę.
- Banki: dwie otwarte wspólne stopki/listwy dla 12kompletnych kaset; docisk wyłącznie plastiku, nigdy końcówek TE. Cztery niezależne MTA220 dostają jeden wspólny otwarty bok podtrzymywany przez P10 i carrier baterii. WAGO: wspólne boczne listwy/endstopy, dźwignie i porty otwarte; zachowane **4DATA/5plus/7G**.
- F0 i POST_F0 wymagają **jednego rzeczywistego frontowego carriera do P10**: POST_F0 poza obrysem decku nie może być uznany za podparty samym pudełkiem. Pięć FHAC na wspólnej tylnej listwie; wszystkie fabryczne końce i odciążenia pozostają.
- Bateria: istniejąca makieta tacy/crossarmów wymaga własnej realizacji druków/połączeń do decku. **Dwa wybrane całe paski4982**, stacje X15/90, podłużne stopery. Ich szerokość/długość/zamknięcie i pozostałe końce są UNKNOWN; 138mm geometrycznego obwodu jest tylko odniesieniem, nie dowodem dostępnego paska. Nie ukryto niegotowej tacy w odbiorze 9STL ramy.
- S0 zachowuje odebrany tylny interfejs; S1/monitor potrzebują wspólnej listwy po rzeczywistym pasowaniu rodziny panelowej. Kamera/ToF/E2/inline zachowane, ale ich mocowanie do wybranego pitch-frame pozostaje jawnym osobnym interfejsem; kosmetyczna głowa nie zastępuje korzenia nośnego.

## F0 — zakończony krótki odczyt, bez kolejnej krzywej

Źródłowy prostokąt 10×12×14 przecinał tylko górny materiał P10 od Z132,5. W istniejącym obszarze **pełny pojedynczy Ø6 +margines0,4**, prosto X−106..−96, mieści się przy Y52/Z126,125: gap **2,975mm**, common0. Dopuszczalny środek Z124,4..127,85 wynika z faktycznej belki i progu1,25. To lokalny prosty odcinek R=∞, **nie dowód prawdziwego wylotu, zakrętu lub długości do F0**.

Całe wejście F0 pozostaje **FIT2/UNQUALIFIED**, W075≤50mm celu ochrony odcinka przed bezpiecznikiem zachowane. Producentowe nominal89,5/strip6,35 nie jest nowym budżetem50 ani dodatkową długością. Stare30/25/545 nie są wykonanymi cięciami, nie ma przedłużenia lub pożyczania długości. Surowe180mm³ i stareHOLDy zachowane. Model pozwala planować niezależną suchą przymiarkę mocowań, nie gotowy zasilony układ.

## Dwie osoby — jedna kolejność

1. A trzyma wspólną ramę, B ładuje pełne nakrętki i skręca fundament/zaciski. Niezasilony bench: E1/AMP/lapy+sleeves z pełnymi fabrycznymi końcami poza PETG.
2. Dolne WAGO/banki/FHAC i oba końce każdej jednostki220 układać w otwartej ramie, zanim taca baterii i górne chwytaki zamkną dojście. Krótki F0 zmierzyć przed jego finalnym dociskiem.
3. Taca z dwoma całymi paskami; Pi, PCA/E1, MAIN/AUX, BNO i audio na swoich próbkach podparć. Końcowe wspólne keepers zamykać dopiero po obejrzeniu bezpiecznych krawędzi i podłączeniu rzeczywistych portów. Nie traktować ilustracyjnych przewodów jak sztywnych przeszkód.
4. BUS/P13 z rzeczywistymi końcami; P14 dotyk pozostaje stały z E1. Oddzielny P15/mikrofon ma prawdziwy USB_AUDIO. Dla baterii: USB mikrofonu/P15 → rzeczywiste końce BUS/P13 → XT60 i istniejący balancer → bateria. Sporadyczna naprawa może wymagać częściowego demontażu.

**Najmniejszy następny materiał:** jeden coupon czterech Pi-hole/słupek/tray/nutfeed oraz wspólna otwarta taca/protection-rail/paski, z rzeczywistym korzeniem. Potem wspólne listwy/keepery z bezpiecznych krawędzi, nie kaseta na każdy moduł/przewód. Dodatkowe standardowe śruby/nakrętki/podkładki są needed/unconfirmed w CSV, nie potwierdzonym zapasem ani zakupem.

FIT1 fizyczny fundament/gwint/masa/ruch; FIT2 rzeczywiste wyjścia/długości/porty/izolacja/USB500+Delock/4×220/oba MTA/FHAC/balancer i F0; FIT3 bezpieczne krawędzie/otwory/audio/całe paski i obrys. actualfit/cut/slack=NULL. Brak nowych druków retencji, zasilania, zakupu, slicera i fizycznego PASS. Zeno: później krótki neckblend/policzki/dół boków; nie wydłużać trafionego ogona.
